
/**
 * Video Capture Utility
 * Captures frames from HTMLVideoElement for analysis
 */

export interface VideoFrame {
    data: string; // Base64 encoded frame
    timestamp: number;
}

export class VideoCapture {
    private canvas: HTMLCanvasElement;
    private ctx: CanvasRenderingContext2D | null;

    constructor() {
        this.canvas = document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d');
    }

    /**
     * Capture a single frame from a video element
     */
    /**
     * Capture a single frame (Async)
     */
    async captureFrame(video: HTMLVideoElement): Promise<VideoFrame | null> {
        // Try direct capture first (fastest)
        const frame = this.captureFrameDirect(video);
        if (frame) return frame;

        // Fallback to background capture (for CORS issues)
        // console.log("Direct capture failed, trying fallback...");
        return await this.captureFrameFallback(video);
    }

    /**
     * Direct canvas capture (Sync risk, but fast)
     */
    captureFrameDirect(video: HTMLVideoElement): VideoFrame | null {
        if (!this.ctx || video.videoWidth === 0 || video.videoHeight === 0) return null;

        const width = video.videoWidth;
        const height = video.videoHeight;

        // Resize for performance
        const MAX_DIMENSION = 640;
        let finalWidth = width;
        let finalHeight = height;
        if (width > MAX_DIMENSION || height > MAX_DIMENSION) {
            const ratio = Math.min(MAX_DIMENSION / width, MAX_DIMENSION / height);
            finalWidth = Math.round(width * ratio);
            finalHeight = Math.round(height * ratio);
        }

        this.canvas.width = finalWidth;
        this.canvas.height = finalHeight;

        try {
            this.ctx.drawImage(video, 0, 0, finalWidth, finalHeight);
            const dataUrl = this.canvas.toDataURL('image/jpeg', 0.8);
            return {
                data: dataUrl.split(',')[1],
                timestamp: video.currentTime
            };
        } catch (e) {
            // Tainted canvas - expected for CORS videos
            return null;
        }
    }

    /**
     * Fallback: Ask background script to capture tab, then crop
     */
    async captureFrameFallback(video: HTMLVideoElement): Promise<VideoFrame | null> {
        return new Promise((resolve) => {
            chrome.runtime.sendMessage({ type: 'CAPTURE_TAB' }, async (response) => {
                if (!response || !response.success) {
                    resolve(null);
                    return;
                }

                // Crop the timestamp/video area
                // We need to calculate video position relative to viewport
                const rect = video.getBoundingClientRect();

                try {
                    const blob = await fetch(response.dataUrl).then(r => r.blob());
                    const imgBitmap = await createImageBitmap(blob);

                    // We need a device pixel ratio aware crop
                    const dpr = window.devicePixelRatio || 1;

                    this.canvas.width = 640; // Fixed size for AI
                    this.canvas.height = 360;

                    if (this.ctx) {
                        this.ctx.drawImage(
                            imgBitmap,
                            rect.left * dpr, rect.top * dpr,
                            rect.width * dpr, rect.height * dpr,
                            0, 0,
                            this.canvas.width, this.canvas.height
                        );

                        const dataUrl = this.canvas.toDataURL('image/jpeg', 0.8);
                        resolve({
                            data: dataUrl.split(',')[1],
                            timestamp: video.currentTime
                        });
                    } else {
                        resolve(null);
                    }
                } catch (e) {
                    console.error("Fallback crop failed", e);
                    resolve(null);
                }
            });
        });
    }

    /**
     * Capture a sequence of frames
     */
    async captureSequence(video: HTMLVideoElement, count: number = 30, intervalMs: number = 100): Promise<VideoFrame[]> {
        const frames: VideoFrame[] = [];

        // Check if we need fallback mode immediately
        const testFrame = this.captureFrameDirect(video);
        const useFallback = !testFrame;

        // If direct works, push the first frame
        if (testFrame) frames.push(testFrame);

        // Adjust interval for fallback (it's slower)
        const finalInterval = useFallback ? Math.max(intervalMs, 300) : intervalMs;

        for (let i = 0; i < count; i++) {
            // If manual fallback needed
            if (useFallback) {
                const frame = await this.captureFrameFallback(video);
                if (frame) frames.push(frame);
            } else {
                if (i > 0) { // optimization
                    const frame = this.captureFrameDirect(video);
                    if (frame) frames.push(frame);
                }
            }

            if (i < count - 1) {
                await new Promise(resolve => setTimeout(resolve, finalInterval));
            }
        }

        return frames;
    }
}
