
import { VideoCapture } from './video-capture';


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

class VeritasInjector {
  private videoCapture: VideoCapture;
  private analyzing: boolean = false;
  private overlay: HTMLElement | null = null;
  private consentGiven: boolean = false; // In a real app, load from storage

  constructor() {
    this.videoCapture = new VideoCapture();
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

  public handleExternalScan(sendResponse: (response: any) => void) {
    const video = document.querySelector('video');
    const btn = document.querySelector('#veritas-btn') as HTMLButtonElement | null;

    if (video && btn) {
      console.log("Veritas-AI: Scan triggered from popup");
      if (!this.analyzing) {
        if (!this.consentGiven) {
          this.showConsentModal(video, btn);
        } else {
          this.startAnalysis(video, btn);
        }
      }
      sendResponse({ success: true });
    } else {
      sendResponse({ success: false, error: "Video or button not found. Is the video playing?" });
    }
  }

  showConsentModal(video: HTMLVideoElement, btn: HTMLButtonElement) {
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
      await this.startAnalysis(video, btn);
    };
  }

  async startAnalysis(video: HTMLVideoElement, btn: HTMLButtonElement) {
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

      const frames = await this.videoCapture.captureSequence(video, 15, 150);

      if (frames.length === 0) throw new Error("Capture failed");

      if (statusEl) statusEl.textContent = "Processing Biometrics...";
      btn.innerHTML = `<span style="font-weight:600">Processing...</span>`;

      // Analyze via Background Script
      const response = await new Promise<any>((resolve, reject) => {
        chrome.runtime.sendMessage({
          type: 'ANALYZE_REQUEST',
          data: {
            frames: frames,
            video_url: window.location.href,
            consent_given: true
          }
        }, (res) => {
          if (chrome.runtime.lastError) {
            reject(chrome.runtime.lastError);
          } else if (res.success) {
            resolve(res.result);
          } else {
            reject(new Error(res.error || "Analysis failed"));
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
        <div style="margin-bottom: 16px;">
            <div style="width: 40px; height: 40px; border: 3px solid #38bdf8; border-top-color: transparent; border-radius: 50%; animation: veritas-spin 1s linear infinite; margin: 0 auto;"></div>
        </div>
        <div id="veritas-scan-status" style="font-family: 'Inter', monospace; font-size: 14px; color: #38bdf8; font-weight: 600; letter-spacing: 0.5px;">INITIALIZING</div>
        <div style="margin-top: 12px; height: 40px; overflow: hidden; position: relative; opacity: 0.6;">
            <!-- Fake waveform visualization -->
            <div style="display: flex; align-items: flex-end; justify-content: center; gap: 3px; height: 100%;">
                ${Array.from({ length: 15 }).map(() => `<div style="width: 4px; background: #38bdf8; border-radius: 2px; animation: veritas-wave ${0.5 + Math.random()}s ease-in-out infinite;"></div>`).join('')}
            </div>
        </div>
      `;

    // Add keyframes if not present
    if (!document.getElementById('veritas-keyframes')) {
      const style = document.createElement('style');
      style.id = 'veritas-keyframes';
      style.textContent = `
            @keyframes veritas-spin { to { transform: rotate(360deg); } }
            @keyframes veritas-wave { 0%, 100% { height: 20%; } 50% { height: 80%; } }
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
             ${result.bio_guard?.confidence ? `<div style="font-size:10px; opacity:0.6; margin-top:2px;">Conf: ${Math.round(result.bio_guard.confidence * 100)}%</div>` : ''}
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

const injector = new VeritasInjector();

// Global listener
chrome.runtime.onMessage.addListener((request, _sender, sendResponse) => {
  if (request.type === 'START_SCAN') {
    injector.handleExternalScan(sendResponse);
    return true;
  }
});
