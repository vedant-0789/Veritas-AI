

// VERITAS DEBUG: INLINED VIDEO CAPTURE TO FIX TDZ
interface VeritasVideoFrame {
  data: string; // Base64 encoded frame
  timestamp: number;
}

class VeritasCapture {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D | null;

  constructor() {
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d');
  }

  async captureFrame(video: HTMLVideoElement): Promise<VeritasVideoFrame | null> {
    const frame = this.captureFrameDirect(video);
    if (frame) return frame;
    return await this.captureFrameFallback(video);
  }

  captureFrameDirect(video: HTMLVideoElement): VeritasVideoFrame | null {
    if (!this.ctx || video.videoWidth === 0 || video.videoHeight === 0) return null;
    const width = video.videoWidth;
    const height = video.videoHeight;
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
      return null;
    }
  }

  async captureFrameFallback(video: HTMLVideoElement): Promise<VeritasVideoFrame | null> {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage({ type: 'CAPTURE_TAB' }, async (response) => {
        if (!response || !response.success) {
          resolve(null);
          return;
        }
        const rect = video.getBoundingClientRect();
        try {
          const blob = await fetch(response.dataUrl).then(r => r.blob());
          const imgBitmap = await createImageBitmap(blob);
          const dpr = window.devicePixelRatio || 1;
          this.canvas.width = 640;
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

  async captureSequence(video: HTMLVideoElement, count: number = 30, intervalMs: number = 100): Promise<VeritasVideoFrame[]> {
    const frames: VeritasVideoFrame[] = [];
    const testFrame = this.captureFrameDirect(video);
    const useFallback = !testFrame;
    if (testFrame) frames.push(testFrame);
    const finalInterval = useFallback ? Math.max(intervalMs, 300) : intervalMs;
    for (let i = 0; i < count; i++) {
      if (useFallback) {
        const frame = await this.captureFrameFallback(video);
        if (frame) frames.push(frame);
      } else {
        if (i > 0) {
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



console.log("Veritas-AI: Content script loaded");

// Inject styles
const style = document.createElement('style');
style.textContent = `
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

  .veritas-glass {
    background: rgba(15, 23, 42, 0.85);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.5);
    font-family: 'Inter', sans-serif;
    color: white;
  }
  
  .veritas-btn-pulse {
    animation: veritas-pulse 3s infinite;
  }
  
  @keyframes veritas-pulse {
    0% { box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(56, 189, 248, 0); }
    100% { box-shadow: 0 0 0 0 rgba(56, 189, 248, 0); }
  }

  .veritas-fade-in {
    animation: veritas-fade-in 0.3s ease-out forwards;
  }

  @keyframes veritas-fade-in {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;
document.head.appendChild(style);

class VeritasCore {
  private veritasCapture: VeritasCapture;
  private analyzing: boolean = false;
  private overlay: HTMLElement | null = null;
  private consentGiven: boolean = false; // In a real app, load from storage

  constructor() {
    this.veritasCapture = new VeritasCapture();
    this.init();
  }

  init() {
    console.log("Veritas-AI: Init called");

    // Aggressive polling to find the player
    setInterval(() => {
      this.checkForVideo();
    }, 1000);

    // Also observe changes
    const observer = new MutationObserver(() => {
      this.checkForVideo();
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  checkForVideo() {
    const video = document.querySelector('video');
    const player = document.querySelector('#movie_player') || document.querySelector('#ytd-player');

    if (video && player && !document.querySelector('#veritas-btn')) {
      console.log("Veritas-AI: Player found, injecting button...");
      this.injectButton(player as HTMLElement, video as HTMLVideoElement);
    }
  }

  injectButton(container: HTMLElement, video: HTMLVideoElement) {
    if (document.querySelector('#veritas-btn')) return;

    const btn = document.createElement('button');
    btn.id = 'veritas-btn';
    btn.className = 'veritas-glass veritas-btn-pulse';
    btn.innerHTML = `
      <div style="display: flex; align-items: center; gap: 8px;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2.5">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        </svg>
        <span style="font-weight: 700; color: #fff; letter-spacing: 0.5px;">VERITAS SEAL</span>
      </div>
    `;

    // High visibility styles
    Object.assign(btn.style, {
      position: 'absolute',
      top: '20px',
      left: '20px', // Changed to left to avoid overlapping with other extension buttons
      zIndex: '2147483647', // Max z-index
      padding: '10px 20px',
      borderRadius: '30px',
      cursor: 'pointer',
      fontSize: '14px',
      display: 'flex',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      border: '1px solid #38bdf8',
      pointerEvents: 'auto' // Ensure clicks are captured
    });

    btn.onclick = async (e) => {
      e.stopPropagation();
      e.stopImmediatePropagation();
      e.preventDefault();
      console.log("Veritas-AI: Button clicked");

      if (this.analyzing) return;

      if (!this.consentGiven) {
        this.showConsentModal(video, btn);
      } else {
        await this.startAnalysis(video, btn);
      }
    };

    container.appendChild(btn);
    console.log("Veritas-AI: Button injected successfully");
  }

  public handleExternalScan(message: any, sendResponse: (response: any) => void) {
    const video = document.querySelector('video');
    const btn = document.querySelector('#veritas-btn') as HTMLButtonElement | null;
    const options = message.options || { enable_gemini: true };

    if (video && btn) {
      console.log("Veritas-AI: Scan triggered from popup", options);
      if (!this.analyzing) {
        if (!this.consentGiven) {
          // Pass options to consent modal -> startAnalysis
          this.showConsentModal(video, btn, options);
        } else {
          this.startAnalysis(video, btn, options);
        }
      }
      sendResponse({ success: true });
    } else {
      sendResponse({ success: false, error: "Video or button not found. Is the video playing?" });
    }
  }

  showConsentModal(video: HTMLVideoElement, btn: HTMLButtonElement, options = { enable_gemini: true }) {
    if (this.overlay) this.overlay.remove();

    this.overlay = document.createElement('div');
    this.overlay.className = 'veritas-glass veritas-fade-in';
    Object.assign(this.overlay.style, {
      position: 'absolute',
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
      width: '400px',
      padding: '24px',
      borderRadius: '16px',
      zIndex: '10000',
      textAlign: 'left',
      pointerEvents: 'auto'
    });

    this.overlay.innerHTML = `
      <h3 style="margin:0 0 12px 0; font-size: 18px; font-weight: 700;">Biometric Analysis Consent</h3>
      <p style="font-size: 14px; color: #cbd5e1; line-height: 1.5; margin-bottom: 20px;">
        To detect authenticity, Veritas-AI analyzes biological signals (pulse) from faces in this video. 
        This data is processed locally and via secure AI for forensic analysis only.
      </p>
      <div style="display: flex; gap: 10px; justify-content: flex-end;">
         <button id="veritas-cancel" style="padding: 8px 16px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); background: transparent; color: white; cursor: pointer;">Cancel</button>
         <button id="veritas-agree" style="padding: 8px 16px; border-radius: 8px; background: #38bdf8; color: #0f172a; font-weight: 600; border: none; cursor: pointer;">I Agree</button>
      </div>
    `;

    const player = document.querySelector('#movie_player') as HTMLElement;
    player.appendChild(this.overlay);

    document.getElementById('veritas-cancel')!.onclick = (e) => {
      e.stopPropagation();
      e.stopImmediatePropagation();
      this.overlay?.remove();
      this.overlay = null;
    };

    document.getElementById('veritas-agree')!.onclick = async (e) => {
      e.stopPropagation();
      e.stopImmediatePropagation();
      this.consentGiven = true;
      this.overlay?.remove();
      this.overlay = null;
      await this.startAnalysis(video, btn, options);
    };
  }

  async startAnalysis(video: HTMLVideoElement, btn: HTMLButtonElement, options = { enable_gemini: true }) {
    try {
      this.analyzing = true;
      btn.innerHTML = `<span style="font-weight:600">Starting...</span>`;
      btn.style.opacity = '0.8';

      // Show Analysis Overlay immediately
      this.showScanningOverlay();

      // Capture
      // Updates status in the overlay
      const statusEl = document.getElementById('veritas-scan-status');
      if (statusEl) statusEl.textContent = "Acquiring Target...";

      const frames = await this.veritasCapture.captureSequence(video, 15, 150);

      if (frames.length === 0) throw new Error("Capture failed");

      if (statusEl) statusEl.textContent = "Processing Biometrics...";
      btn.innerHTML = `<span style="font-weight:600">Processing...</span>`;

      // Analyze via Background Script
      const response = await new Promise<any>((resolve, reject) => {
        console.log("Veritas-AI: Sending ANALYZE_REQUEST");
        chrome.runtime.sendMessage({
          type: 'ANALYZE_REQUEST',
          data: {
            frames: frames,
            video_url: window.location.href,
            consent_given: true,
            enable_gemini: options.enable_gemini
          }
        }, (responseCallback) => {
          console.log("Veritas-AI: Callback received", responseCallback, chrome.runtime.lastError);
          if (chrome.runtime.lastError) {
            console.error("Veritas-AI: Runtime error", chrome.runtime.lastError);
            reject(chrome.runtime.lastError);
          } else if (responseCallback && responseCallback.success) {
            resolve(responseCallback.result);
          } else {
            console.error("Veritas-AI: Success false", responseCallback);
            // Simplify rejection to avoid potential 'Error' class shadowing issues
            reject("Analysis failed: " + (responseCallback?.error || "Unknown"));
          }
        });
      });

      this.showDetailedResult(response);

      // Reset button state
      btn.innerHTML = `
      <div style="display: flex; align-items: center; gap: 8px;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2.5">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        </svg>
        <span style="font-weight: 700; color: #fff;">VERITAS</span>
      </div>`;
      btn.style.opacity = '1';

    } catch (e: any) {
      console.error(e);
      if (this.overlay) this.overlay.remove();

      let errorMessage = e.message || "Unknown error";

      if (errorMessage.includes("Extension context invalidated")) {
        errorMessage = "Extension updated. Please refresh this page.";
      }

      // Show error overlay
      this.overlay = document.createElement('div');
      this.overlay.className = 'veritas-glass veritas-fade-in';
      Object.assign(this.overlay.style, {
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: '350px',
        padding: '24px',
        borderRadius: '16px',
        zIndex: '10000',
        textAlign: 'center',
        border: '1px solid rgba(239, 68, 68, 0.4)'
      });

      this.overlay.innerHTML = `
        <div style="color: #ef4444; font-size: 48px; margin-bottom: 16px;">⚠️</div>
        <h3 style="margin: 0 0 8px 0; color: #ef4444;">Analysis Failed</h3>
        <p style="color: #cbd5e1; font-size: 13px; margin-bottom: 20px; word-break: break-word;">
           ${errorMessage}
        </p>
        <button id="veritas-error-close" style="padding: 8px 16px; background: rgba(255,255,255,0.1); border: none; border-radius: 8px; color: white; cursor: pointer;">Close</button>
      `;

      const player = document.querySelector('#movie_player') as HTMLElement;
      player.appendChild(this.overlay);

      document.getElementById('veritas-error-close')!.onclick = (ev) => {
        ev.stopPropagation();
        this.overlay?.remove();
        this.overlay = null;
      };

      btn.innerHTML = `<span style="color:#ef4444; font-weight:700">Error</span>`;
      setTimeout(() => {
        btn.innerHTML = `
          <div style="display: flex; align-items: center; gap: 8px;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2.5">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
            <span style="font-weight: 700; color: #fff;">VERITAS</span>
          </div>
        `;
      }, 3000);
    } finally {
      this.analyzing = false;
    }
  }

  showScanningOverlay() {
    if (this.overlay) this.overlay.remove();
    this.overlay = document.createElement('div');
    this.overlay.className = 'veritas-glass veritas-fade-in';
    Object.assign(this.overlay.style, {
      position: 'absolute',
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
      width: '300px',
      padding: '24px',
      borderRadius: '20px',
      zIndex: '10000',
      textAlign: 'center',
      pointerEvents: 'none' // Let user watch video while scanning
    });

    this.overlay.innerHTML = `
        <div style="margin-bottom: 20px; position: relative;">
            <div style="width: 60px; height: 60px; border: 2px solid rgba(56, 189, 248, 0.1); border-top-color: #38bdf8; border-bottom-color: #38bdf8; border-radius: 50%; animation: veritas-spin 2s linear infinite; margin: 0 auto; box-shadow: 0 0 20px rgba(56, 189, 248, 0.2);"></div>
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 40px; height: 40px; background: rgba(56, 189, 248, 0.1); border-radius: 50%; animation: veritas-pulse-inner 1.5s ease-in-out infinite;"></div>
        </div>
        <div id="veritas-scan-status" style="font-family: 'Inter', monospace; font-size: 14px; color: #fff; font-weight: 600; letter-spacing: 2px; text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);">INITIALIZING</div>
        <div style="font-size: 10px; color: #94a3b8; margin-top: 4px; letter-spacing: 0.5px;">ESTABLISHING SECURE CONNECTION</div>
        
        <div style="margin-top: 24px; height: 60px; width: 100%; overflow: hidden; position: relative; background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.05), transparent); border-top: 1px solid rgba(56, 189, 248, 0.1); border-bottom: 1px solid rgba(56, 189, 248, 0.1);">
            <!-- High-tech waveform visualization -->
            <div style="display: flex; align-items: center; justify-content: center; gap: 4px; height: 100%; mask-image: linear-gradient(90deg, transparent, black 20%, black 80%, transparent);">
                ${Array.from({ length: 24 }).map((_, i) => `<div style="width: 3px; background: #38bdf8; border-radius: 10px; height: 10px; animation: veritas-wave 1s ease-in-out infinite; animation-delay: ${i * 0.05}s; box-shadow: 0 0 8px rgba(56, 189, 248, 0.4);"></div>`).join('')}
            </div>
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 1px; background: rgba(56, 189, 248, 0.3); box-shadow: 0 0 10px #38bdf8; animation: veritas-scanline 2s linear infinite;"></div>
        </div>
      `;

    // Add keyframes if not present
    if (!document.getElementById('veritas-keyframes')) {
      const style = document.createElement('style');
      style.id = 'veritas-keyframes';
      style.textContent = `
            @keyframes veritas-spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            @keyframes veritas-pulse-inner { 0%, 100% { transform: translate(-50%, -50%) scale(0.8); opacity: 0.5; } 50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.2; } }
            @keyframes veritas-wave { 0%, 100% { height: 10%; opacity: 0.3; } 50% { height: 70%; opacity: 1; } }
            @keyframes veritas-scanline { 0% { top: 0%; opacity: 0; } 10% { opacity: 1; } 90% { opacity: 1; } 100% { top: 100%; opacity: 0; } }
          `;
      document.head.appendChild(style);
    }

    const player = document.querySelector('#movie_player') as HTMLElement;
    player.appendChild(this.overlay);
  }

  showDetailedResult(result: any) {
    if (this.overlay) this.overlay.remove();

    const isReal = result.verdict === 'LIKELY_REAL';
    const isFake = result.verdict === 'LIKELY_FAKE';
    const color = isReal ? '#22c55e' : (isFake ? '#ef4444' : '#eab308');
    const title = isReal ? 'LIKELY REAL' : (isFake ? 'LIKELY FAKE' : 'UNCERTAIN');
    const confidence = Math.round((result.confidence || 0) * 100);

    // Enhanced evidence display with better formatting
    const evidenceList = (result.evidence || []).map((e: string) => {
      const isPositive = e.includes('✅') || e.includes('🔬') || e.includes('⏱️');
      const isNegative = e.includes('❌') || e.includes('🚨') || e.includes('⚠️');
      const color = isPositive ? '#22c55e' : (isNegative ? '#ef4444' : '#e2e8f0');
      return `<li style="margin-bottom:8px; opacity:0.95; color:${color}; font-size:13px; line-height:1.4;">${e}</li>`;
    }).join('');

    // Pulse Graph Generation
    let graphHtml = '';
    if (result.bio_guard?.pulse_signal && result.bio_guard.pulse_signal.length > 10) {
      const data = result.bio_guard.pulse_signal;
      const min = Math.min(...data);
      const max = Math.max(...data);
      const range = max - min || 1;
      const points = data.map((v: number, i: number) => {
        const x = (i / (data.length - 1)) * 100;
        const y = 100 - ((v - min) / range) * 100;
        return `${x},${y}`;
      }).join(' ');

      graphHtml = `
        <div style="margin-top: 8px; width: 100%; height: 40px; background: rgba(0,0,0,0.2); border-radius: 6px; overflow: hidden; position: relative;">
            <svg viewBox="0 0 100 100" preserveAspectRatio="none" style="width: 100%; height: 100%; opacity: 0.8;">
                <polyline points="${points}" fill="none" stroke="${result.bio_guard.pulse_detected ? '#22c55e' : '#94a3b8'}" stroke-width="2" vector-effect="non-scaling-stroke" />
            </svg>
             <div style="position:absolute; top:2px; left:4px; font-size:8px; color:rgba(255,255,255,0.4);">LIVE SIGNAL</div>
        </div>
        `;
    }

    this.overlay = document.createElement('div');
    this.overlay.className = 'veritas-glass veritas-fade-in';
    Object.assign(this.overlay.style, {
      position: 'absolute',
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
      width: '450px',
      padding: '0',
      borderRadius: '20px',
      zIndex: '10000',
      textAlign: 'left',
      overflow: 'hidden',
      pointerEvents: 'auto'
    });

    // Enhanced confidence display with color coding
    const confidenceColor = confidence >= 85 ? '#22c55e' : (confidence >= 70 ? '#3b82f6' : (confidence >= 50 ? '#eab308' : '#ef4444'));
    const confidenceLabel = confidence >= 90 ? 'VERY HIGH' : (confidence >= 80 ? 'HIGH' : (confidence >= 70 ? 'MODERATE' : (confidence >= 50 ? 'LOW' : 'VERY LOW')));

    this.overlay.innerHTML = `
      <div style="padding: 24px; border-bottom: 1px solid rgba(255,255,255,0.1); background: linear-gradient(135deg, ${color}15 0%, transparent 100%);">
         <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 12px;">
           <h2 style="margin:0; font-size: 28px; font-weight: 900; color: ${color}; letter-spacing: -0.5px; text-shadow: 0 2px 10px ${color}40;">${title}</h2>
         </div>
         <div style="display: flex; align-items: center; gap: 16px;">
           <div style="flex: 1;">
             <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.6; margin-bottom: 4px;">Confidence Level</div>
             <div style="display: flex; align-items: center; gap: 8px;">
               <div style="flex: 1; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden;">
                 <div style="height: 100%; width: ${confidence}%; background: linear-gradient(90deg, ${confidenceColor} 0%, ${confidenceColor}dd 100%); border-radius: 4px; transition: width 0.5s;"></div>
               </div>
               <div style="font-family: monospace; font-size: 18px; font-weight: 700; color: ${confidenceColor}; min-width: 50px; text-align: right;">${confidence}%</div>
             </div>
             <div style="font-size: 10px; color: ${confidenceColor}; margin-top: 4px; font-weight: 600;">${confidenceLabel} CONFIDENCE</div>
           </div>
         </div>
      </div>
      
      <div style="padding: 24px; background: rgba(0,0,0,0.2);">
        <h4 style="margin:0 0 12px 0; font-size: 12px; text-transform:uppercase; letter-spacing:1px; opacity:0.6;">Forensic Analysis</h4>
        <ul style="margin:0; padding-left: 20px; font-size: 14px; line-height: 1.5; color: #e2e8f0;">
          ${evidenceList}
        </ul>
        
        <div style="margin-top: 20px; display:grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px;">
           <div style="background: linear-gradient(135deg, rgba(56, 189, 248, 0.1) 0%, rgba(56, 189, 248, 0.05) 100%); padding: 14px; border-radius: 12px; border: 1px solid rgba(56, 189, 248, 0.2);">
             <div style="font-size:10px; text-transform: uppercase; letter-spacing: 1px; opacity:0.6; margin-bottom:6px; font-weight: 600;">BIO-GUARD</div>
             <div style="font-weight:700; font-size:16px; color:${result.bio_guard?.pulse_detected ? '#22c55e' : '#94a3b8'}; margin-bottom:4px;">
               ${result.bio_guard?.pulse_detected ? `❤️ ${Math.round(result.bio_guard.bpm)} BPM` : '❌ No Pulse'}
             </div>
             ${result.bio_guard?.snr ? `<div style="font-size:11px; opacity:0.7; color:${result.bio_guard.snr > 5 ? '#22c55e' : (result.bio_guard.snr > 2 ? '#eab308' : '#ef4444')};">SNR: ${result.bio_guard.snr.toFixed(1)}</div>` : ''}
             ${graphHtml}
           </div>
           <div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%); padding: 14px; border-radius: 12px; border: 1px solid rgba(139, 92, 246, 0.2);">
             <div style="font-size:10px; text-transform: uppercase; letter-spacing: 1px; opacity:0.6; margin-bottom:6px; font-weight: 600;">PHYSICS-GUARD</div>
             <div style="font-weight:700; font-size:16px; color:${result.physics_guard?.is_suspicious ? '#ef4444' : (result.physics_guard?.is_real ? '#22c55e' : '#94a3b8')}; margin-bottom:4px;">
               ${result.physics_guard?.is_real ? '✅ Authentic' : (result.physics_guard?.is_suspicious ? '❌ Suspicious' : '⚠️ Uncertain')}
             </div>
             ${result.physics_guard?.confidence ? `<div style="font-size:11px; opacity:0.7;">Conf: ${Math.round(result.physics_guard.confidence * 100)}%</div>` : ''}
           </div>
           ${result.temporal_guard?.available ? `
           <div style="background: linear-gradient(135deg, rgba(236, 72, 153, 0.1) 0%, rgba(236, 72, 153, 0.05) 100%); padding: 14px; border-radius: 12px; border: 1px solid rgba(236, 72, 153, 0.2);">
             <div style="font-size:10px; text-transform: uppercase; letter-spacing: 1px; opacity:0.6; margin-bottom:6px; font-weight: 600;">TEMPORAL-GUARD</div>
             <div style="font-weight:700; font-size:16px; color:${result.temporal_guard.temporal_consistency > 0.7 ? '#22c55e' : (result.temporal_guard.temporal_consistency < 0.4 ? '#ef4444' : '#eab308')}; margin-bottom:4px;">
               ${result.temporal_guard.temporal_consistency > 0.7 ? '✅ Consistent' : (result.temporal_guard.temporal_consistency < 0.4 ? '❌ Inconsistent' : '⚠️ Moderate')}
             </div>
             <div style="font-size:11px; opacity:0.7;">Score: ${(result.temporal_guard.temporal_consistency * 100).toFixed(0)}%</div>
           </div>
           ` : ''}
        </div>
        
        ${result.summary ? `
        <div style="margin-top: 16px; padding: 12px; background: rgba(56, 189, 248, 0.1); border-left: 3px solid #38bdf8; border-radius: 8px;">
          <div style="font-size:12px; font-weight:600; margin-bottom:6px; color:#38bdf8;">SUMMARY</div>
          <div style="font-size:13px; color:#e2e8f0; line-height:1.5;">${result.summary}</div>
        </div>
        ` : ''}
      </div>
      
      <div style="padding: 16px; background: rgba(0,0,0,0.4); text-align:center;">
        <button id="veritas-close" style="background: transparent; border: none; color: #94a3b8; font-size: 13px; cursor: pointer; text-decoration: underline;">Close Analysis</button>
      </div>
    `;

    const player = document.querySelector('#movie_player') as HTMLElement;
    player.appendChild(this.overlay);

    document.getElementById('veritas-close')!.onclick = (e) => {
      e.stopPropagation();
      e.stopImmediatePropagation();
      this.overlay?.remove();
      this.overlay = null;
    };
  }
}

const initVeritas = () => {
  if ((window as any).veritasInitialized) return;
  (window as any).veritasInitialized = true;
  console.log("Veritas-AI: Initializing Core...");
  const core = new VeritasCore();

  // Global listener
  chrome.runtime.onMessage.addListener((request, _sender, sendResponse) => {
    if (request.type === 'START_SCAN') {
      core.handleExternalScan(request, sendResponse);
      return true;
    }
  });
};

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initVeritas);
} else {
  initVeritas();
}
