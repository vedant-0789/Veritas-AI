
/**
 * API Client
 * Handles communication with the local Python backend
 */

const API_BASE_URL = 'http://127.0.0.1:8000/api';

export interface AnalysisRequest {
    frames: Array<{ data: string; timestamp: number }>;
    video_url?: string;
    consent_given: boolean;
    enable_gemini?: boolean;
    fps?: number;
}

export interface AnalysisResult {
    task_id: string;
    status: 'processing' | 'completed' | 'error';
    verdict?: 'LIKELY_REAL' | 'LIKELY_FAKE' | 'UNCERTAIN';
    confidence?: number;
    evidence?: string[];
    summary?: string;
    assessment?: string; // Legacy field
    bio_guard?: {
        pulse_detected: boolean;
        bpm?: number;
        confidence: number;
        pulse_signal?: number[]; // Array of values for graph
        [key: string]: any;
    };
    physics_guard?: any;
}

export class ApiClient {
    /**
     * Check if backend is available
     */
    async healthCheck(): Promise<boolean> {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 2000);

            const response = await fetch(`${API_BASE_URL}/health`, {
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            return response.ok;
        } catch (e) {
            return false;
        }
    }

    /**
     * Submit video frames for analysis (Async - Recommended)
     * Returns a task_id immediately.
     */
    async analyzeVideo(request: AnalysisRequest): Promise<AnalysisResult> {
        try {
            // Fast fail if health check fails
            const isHealthy = await this.healthCheck();
            if (!isHealthy) {
                throw new Error("Backend connection failed. Is the server running on port 8000?");
            }

            const response = await fetch(`${API_BASE_URL}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(request),
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Analysis request failed: ${response.status} - ${errorText}`);
            }

            return await response.json();
        } catch (e: any) {
            console.error("API Error (analyzeVideo):", e);
            throw e;
        }
    }

    /**
     * Poll for analysis status until completion or timeout
     */
    async waitForAnalysis(taskId: string, timeoutMs: number = 60000): Promise<AnalysisResult> {
        const startTime = Date.now();

        while (Date.now() - startTime < timeoutMs) {
            try {
                const response = await fetch(`${API_BASE_URL}/status/${taskId}`);

                if (!response.ok) {
                    // If 404, maybe task expired or wrong ID
                    if (response.status === 404) throw new Error("Task not found (expired?)");
                    // Otherwise retry
                    await new Promise(r => setTimeout(r, 1000));
                    continue;
                }

                const result: AnalysisResult = await response.json();

                if (result.status === 'completed') {
                    return result;
                } else if (result.status === 'error') {
                    throw new Error(result.evidence?.[0] || "Unknown analysis error");
                }

                // Still processing, wait 1s
                await new Promise(r => setTimeout(r, 1000));

            } catch (e: any) {
                // Network error or other fatal error -> retry a few times then fail?
                // For now, if we get a specific error like "Task not found", we throw.
                // Network errors we might want to retry a bit more gracefully.
                console.warn("Polling error:", e);
                if (e.message.includes("Task not found")) throw e;
                await new Promise(r => setTimeout(r, 2000));
            }
        }

        throw new Error("Analysis timed out");
    }

    /**
     * Sync analysis (Deprecated/Legacy)
     */
    async analyzeVideoSync(request: AnalysisRequest): Promise<AnalysisResult> {
        return this.analyzeVideo(request); // Redirect to async for safety
    }

    /**
     * Poll for analysis status (Single check)
     */
    async getStatus(taskId: string): Promise<AnalysisResult> {
        try {
            const response = await fetch(`${API_BASE_URL}/status/${taskId}`);

            if (!response.ok) {
                throw new Error(`Status check failed: ${response.statusText}`);
            }

            return await response.json();
        } catch (e) {
            console.error("API Error:", e);
            throw e;
        }
    }
}

export const apiClient = new ApiClient();
