var b=Object.defineProperty;var w=(d,l,h)=>l in d?b(d,l,{enumerable:!0,configurable:!0,writable:!0,value:h}):d[l]=h;var p=(d,l,h)=>w(d,typeof l!="symbol"?l+"":l,h);(function(){"use strict";class d{constructor(){p(this,"canvas");p(this,"ctx");this.canvas=document.createElement("canvas"),this.ctx=this.canvas.getContext("2d")}async captureFrame(t){const e=this.captureFrameDirect(t);return e||await this.captureFrameFallback(t)}captureFrameDirect(t){if(!this.ctx||t.videoWidth===0||t.videoHeight===0)return null;const e=t.videoWidth,i=t.videoHeight,a=640;let s=e,n=i;if(e>a||i>a){const o=Math.min(a/e,a/i);s=Math.round(e*o),n=Math.round(i*o)}this.canvas.width=s,this.canvas.height=n;try{return this.ctx.drawImage(t,0,0,s,n),{data:this.canvas.toDataURL("image/jpeg",.8).split(",")[1],timestamp:t.currentTime}}catch{return null}}async captureFrameFallback(t){return new Promise(e=>{chrome.runtime.sendMessage({type:"CAPTURE_TAB"},async i=>{if(!i||!i.success){e(null);return}const a=t.getBoundingClientRect();try{const s=await fetch(i.dataUrl).then(r=>r.blob()),n=await createImageBitmap(s),o=window.devicePixelRatio||1;if(this.canvas.width=640,this.canvas.height=360,this.ctx){this.ctx.drawImage(n,a.left*o,a.top*o,a.width*o,a.height*o,0,0,this.canvas.width,this.canvas.height);const r=this.canvas.toDataURL("image/jpeg",.8);e({data:r.split(",")[1],timestamp:t.currentTime})}else e(null)}catch(s){console.error("Fallback crop failed",s),e(null)}})})}async captureSequence(t,e=30,i=100){const a=[],s=this.captureFrameDirect(t),n=!s;s&&a.push(s);const o=n?Math.max(i,300):i;for(let r=0;r<e;r++){if(n){const c=await this.captureFrameFallback(t);c&&a.push(c)}else if(r>0){const c=this.captureFrameDirect(t);c&&a.push(c)}r<e-1&&await new Promise(c=>setTimeout(c,o))}return a}}console.log("Veritas-AI: Content script loaded");const l=document.createElement("style");l.textContent=`
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
`,document.head.appendChild(l);class h{constructor(){p(this,"videoCapture");p(this,"analyzing",!1);p(this,"overlay",null);p(this,"consentGiven",!1);this.videoCapture=new d,this.init()}init(){console.log("Veritas-AI: Init called"),setInterval(()=>{this.checkForVideo()},1e3),new MutationObserver(()=>{this.checkForVideo()}).observe(document.body,{childList:!0,subtree:!0})}checkForVideo(){const t=document.querySelector("video"),e=document.querySelector("#movie_player")||document.querySelector("#ytd-player");t&&e&&!document.querySelector("#veritas-btn")&&(console.log("Veritas-AI: Player found, injecting button..."),this.injectButton(e,t))}injectButton(t,e){if(document.querySelector("#veritas-btn"))return;const i=document.createElement("button");i.id="veritas-btn",i.className="veritas-glass veritas-btn-pulse",i.innerHTML=`
      <div style="display: flex; align-items: center; gap: 8px;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2.5">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        </svg>
        <span style="font-weight: 700; color: #fff; letter-spacing: 0.5px;">VERITAS SEAL</span>
      </div>
    `,Object.assign(i.style,{position:"absolute",top:"20px",left:"20px",zIndex:"2147483647",padding:"10px 20px",borderRadius:"30px",cursor:"pointer",fontSize:"14px",display:"flex",backgroundColor:"rgba(15, 23, 42, 0.9)",border:"1px solid #38bdf8",pointerEvents:"auto"}),i.onclick=async a=>{a.stopPropagation(),a.stopImmediatePropagation(),a.preventDefault(),console.log("Veritas-AI: Button clicked"),!this.analyzing&&(this.consentGiven?await this.startAnalysis(e,i):this.showConsentModal(e,i))},t.appendChild(i),console.log("Veritas-AI: Button injected successfully")}handleExternalScan(t){const e=document.querySelector("video"),i=document.querySelector("#veritas-btn");e&&i?(console.log("Veritas-AI: Scan triggered from popup"),this.analyzing||(this.consentGiven?this.startAnalysis(e,i):this.showConsentModal(e,i)),t({success:!0})):t({success:!1,error:"Video or button not found. Is the video playing?"})}showConsentModal(t,e){this.overlay&&this.overlay.remove(),this.overlay=document.createElement("div"),this.overlay.className="veritas-glass veritas-fade-in",Object.assign(this.overlay.style,{position:"absolute",top:"50%",left:"50%",transform:"translate(-50%, -50%)",width:"400px",padding:"24px",borderRadius:"16px",zIndex:"10000",textAlign:"left",pointerEvents:"auto"}),this.overlay.innerHTML=`
      <h3 style="margin:0 0 12px 0; font-size: 18px; font-weight: 700;">Biometric Analysis Consent</h3>
      <p style="font-size: 14px; color: #cbd5e1; line-height: 1.5; margin-bottom: 20px;">
        To detect authenticity, Veritas-AI analyzes biological signals (pulse) from faces in this video. 
        This data is processed locally and via secure AI for forensic analysis only.
      </p>
      <div style="display: flex; gap: 10px; justify-content: flex-end;">
         <button id="veritas-cancel" style="padding: 8px 16px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); background: transparent; color: white; cursor: pointer;">Cancel</button>
         <button id="veritas-agree" style="padding: 8px 16px; border-radius: 8px; background: #38bdf8; color: #0f172a; font-weight: 600; border: none; cursor: pointer;">I Agree</button>
      </div>
    `,document.querySelector("#movie_player").appendChild(this.overlay),document.getElementById("veritas-cancel").onclick=a=>{var s;a.stopPropagation(),a.stopImmediatePropagation(),(s=this.overlay)==null||s.remove(),this.overlay=null},document.getElementById("veritas-agree").onclick=async a=>{var s;a.stopPropagation(),a.stopImmediatePropagation(),this.consentGiven=!0,(s=this.overlay)==null||s.remove(),this.overlay=null,await this.startAnalysis(t,e)}}async startAnalysis(t,e){try{this.analyzing=!0,e.innerHTML='<span style="font-weight:600">Starting...</span>',e.style.opacity="0.8",this.showScanningOverlay();const i=document.getElementById("veritas-scan-status");i&&(i.textContent="Acquiring Target...");const a=await this.videoCapture.captureSequence(t,15,150);if(a.length===0)throw new Error("Capture failed");i&&(i.textContent="Processing Biometrics..."),e.innerHTML='<span style="font-weight:600">Processing...</span>';const s=await new Promise((n,o)=>{chrome.runtime.sendMessage({type:"ANALYZE_REQUEST",data:{frames:a,video_url:window.location.href,consent_given:!0}},r=>{chrome.runtime.lastError?o(chrome.runtime.lastError):r.success?n(r.result):o(new Error(r.error||"Analysis failed"))})});this.showDetailedResult(s),e.innerHTML=`
      <div style="display: flex; align-items: center; gap: 8px;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2.5">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        </svg>
        <span style="font-weight: 700; color: #fff;">VERITAS</span>
      </div>`,e.style.opacity="1"}catch(i){console.error(i),this.overlay&&this.overlay.remove();let a=i.message||"Unknown error";a.includes("Extension context invalidated")&&(a="Extension updated. Please refresh this page."),this.overlay=document.createElement("div"),this.overlay.className="veritas-glass veritas-fade-in",Object.assign(this.overlay.style,{position:"absolute",top:"50%",left:"50%",transform:"translate(-50%, -50%)",width:"350px",padding:"24px",borderRadius:"16px",zIndex:"10000",textAlign:"center",border:"1px solid rgba(239, 68, 68, 0.4)"}),this.overlay.innerHTML=`
        <div style="color: #ef4444; font-size: 48px; margin-bottom: 16px;">⚠️</div>
        <h3 style="margin: 0 0 8px 0; color: #ef4444;">Analysis Failed</h3>
        <p style="color: #cbd5e1; font-size: 13px; margin-bottom: 20px; word-break: break-word;">
           ${a}
        </p>
        <button id="veritas-error-close" style="padding: 8px 16px; background: rgba(255,255,255,0.1); border: none; border-radius: 8px; color: white; cursor: pointer;">Close</button>
      `,document.querySelector("#movie_player").appendChild(this.overlay),document.getElementById("veritas-error-close").onclick=n=>{var o;n.stopPropagation(),(o=this.overlay)==null||o.remove(),this.overlay=null},e.innerHTML='<span style="color:#ef4444; font-weight:700">Error</span>',setTimeout(()=>{e.innerHTML=`
          <div style="display: flex; align-items: center; gap: 8px;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2.5">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
            <span style="font-weight: 700; color: #fff;">VERITAS</span>
          </div>
        `},3e3)}finally{this.analyzing=!1}}showScanningOverlay(){if(this.overlay&&this.overlay.remove(),this.overlay=document.createElement("div"),this.overlay.className="veritas-glass veritas-fade-in",Object.assign(this.overlay.style,{position:"absolute",top:"50%",left:"50%",transform:"translate(-50%, -50%)",width:"300px",padding:"24px",borderRadius:"20px",zIndex:"10000",textAlign:"center",pointerEvents:"none"}),this.overlay.innerHTML=`
        <div style="margin-bottom: 16px;">
            <div style="width: 40px; height: 40px; border: 3px solid #38bdf8; border-top-color: transparent; border-radius: 50%; animation: veritas-spin 1s linear infinite; margin: 0 auto;"></div>
        </div>
        <div id="veritas-scan-status" style="font-family: 'Inter', monospace; font-size: 14px; color: #38bdf8; font-weight: 600; letter-spacing: 0.5px;">INITIALIZING</div>
        <div style="margin-top: 12px; height: 40px; overflow: hidden; position: relative; opacity: 0.6;">
            <!-- Fake waveform visualization -->
            <div style="display: flex; align-items: flex-end; justify-content: center; gap: 3px; height: 100%;">
                ${Array.from({length:15}).map(()=>`<div style="width: 4px; background: #38bdf8; border-radius: 2px; animation: veritas-wave ${.5+Math.random()}s ease-in-out infinite;"></div>`).join("")}
            </div>
        </div>
      `,!document.getElementById("veritas-keyframes")){const e=document.createElement("style");e.id="veritas-keyframes",e.textContent=`
            @keyframes veritas-spin { to { transform: rotate(360deg); } }
            @keyframes veritas-wave { 0%, 100% { height: 20%; } 50% { height: 80%; } }
          `,document.head.appendChild(e)}document.querySelector("#movie_player").appendChild(this.overlay)}showDetailedResult(t){var c,g,v,m;this.overlay&&this.overlay.remove();const e=t.verdict==="LIKELY_REAL",i=t.verdict==="LIKELY_FAKE",a=e?"#22c55e":i?"#ef4444":"#eab308",s=e?"LIKELY REAL":i?"LIKELY FAKE":"UNCERTAIN",n=Math.round((t.confidence||0)*100),o=(t.evidence||[]).map(u=>`<li style="margin-bottom:6px; opacity:0.9;">${u}</li>`).join("");this.overlay=document.createElement("div"),this.overlay.className="veritas-glass veritas-fade-in",Object.assign(this.overlay.style,{position:"absolute",top:"50%",left:"50%",transform:"translate(-50%, -50%)",width:"450px",padding:"0",borderRadius:"20px",zIndex:"10000",textAlign:"left",overflow:"hidden",pointerEvents:"auto"}),this.overlay.innerHTML=`
      <div style="padding: 24px; border-bottom: 1px solid rgba(255,255,255,0.1);">
         <div style="display:flex; justify-content:space-between; align-items:center;">
           <h2 style="margin:0; font-size: 24px; font-weight: 800; color: ${a}; letter-spacing: -0.5px;">${s}</h2>
           <div style="font-family: monospace; font-size: 14px; opacity: 0.7;">CONFIDENCE: ${n}%</div>
         </div>
      </div>
      
      <div style="padding: 24px; background: rgba(0,0,0,0.2);">
        <h4 style="margin:0 0 12px 0; font-size: 12px; text-transform:uppercase; letter-spacing:1px; opacity:0.6;">Forensic Analysis</h4>
        <ul style="margin:0; padding-left: 20px; font-size: 14px; line-height: 1.5; color: #e2e8f0;">
          ${o}
        </ul>
        
        <div style="margin-top: 20px; display:grid; grid-template-columns: 1fr 1fr; gap: 10px;">
           <div style="background: rgba(255,255,255,0.05); padding: 12px; border-radius: 12px;">
             <div style="font-size:11px; opacity:0.5; margin-bottom:4px;">BIO-GUARD</div>
             <div style="font-weight:600; color:${(c=t.bio_guard)!=null&&c.pulse_detected?"#22c55e":"#94a3b8"}">
               ${(g=t.bio_guard)!=null&&g.pulse_detected?`${Math.round(t.bio_guard.bpm)} BPM`:"No Pulse"}
             </div>
           </div>
           <div style="background: rgba(255,255,255,0.05); padding: 12px; border-radius: 12px;">
             <div style="font-size:11px; opacity:0.5; margin-bottom:4px;">PHYSICS-GUARD</div>
             <div style="font-weight:600; color:${(v=t.physics_guard)!=null&&v.is_suspicious?"#ef4444":"#22c55e"}">
               ${(m=t.physics_guard)!=null&&m.is_suspicious?"Suspicious":"Clear"}
             </div>
           </div>
        </div>
      </div>
      
      <div style="padding: 16px; background: rgba(0,0,0,0.4); text-align:center;">
        <button id="veritas-close" style="background: transparent; border: none; color: #94a3b8; font-size: 13px; cursor: pointer; text-decoration: underline;">Close Analysis</button>
      </div>
    `,document.querySelector("#movie_player").appendChild(this.overlay),document.getElementById("veritas-close").onclick=u=>{var f;u.stopPropagation(),u.stopImmediatePropagation(),(f=this.overlay)==null||f.remove(),this.overlay=null}}}const x=new h;chrome.runtime.onMessage.addListener((y,t,e)=>{if(y.type==="START_SCAN")return x.handleExternalScan(e),!0})})();
