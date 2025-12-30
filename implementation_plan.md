# Veritas-AI Hackathon MVP Implementation Plan (4-5 Days)

## Overview

This plan outlines a **hackathon-winning MVP** built in 4-5 days using **100% FREE technologies**. The goal is to create an impressive, working demonstration that showcases the deepfake detection concept without requiring paid cloud services.

**Key Strategy**: Build a polished, feature-rich demo that impresses judges while keeping infrastructure costs at $0.

## MVP Features (Hackathon-Optimized)

✅ Chrome Extension (React + TypeScript, Professional UI)  
✅ rPPG Bio-Guard (heartbeat detection) - Primary differentiator  
✅ Gemini AI Integration (FREE tier via AI Studio)  
✅ Local Python backend (FastAPI)  
✅ YouTube video analysis  
✅ Beautiful, modern UI design  
✅ Demo video and presentation materials  

## User Review Required

> [!IMPORTANT]
> **Hackathon Success Strategy**:
> 
> This MVP focuses on **maximum visual impact** and **working features** rather than production scalability:
> 
> 1. **Impressive Demo**: Chrome extension with stunning UI
> 2. **Working Detection**: Real rPPG pulse detection
> 3. **AI Integration**: Free Gemini API for credibility
> 4. **Strong Presentation**: Demo video, documentation, slides
> 5. **Cost**: $0 (everything runs locally + free API tier)
> 
> **What judges will see**:
> - Working Chrome extension on YouTube
> - Real-time deepfake detection
> - Scientific approach (biological watermarks)
> - Professional UI/UX
> - Technical depth (rPPG algorithm, MediaPipe, AI)

> [!TIP]
> **Hackathon Advantage**: Your approach is unique! Most teams will do:
> - Simple ML classifiers
> - Generic fake/real predictions
> - No biological proof
> 
> **Your edge**: Bio-signals + Physics + Professional execution

---

## Proposed Changes

### Component 1: Project Structure & Configuration

#### [NEW] Project Root Structure
```
Veritas-AI/
├── extension/          # Chrome extension code
│   ├── manifest.json
│   ├── popup/         # Extension popup UI
│   ├── content/       # Content scripts
│   ├── background/    # Background service worker
│   └── assets/        # Icons, images
├── backend/           # Python backend server
│   ├── app.py         # Main Flask/FastAPI app
│   ├── modules/       # Detection modules
│   │   └── rppg.py   # Bio-Guard module
│   └── requirements.txt
├── shared/            # Shared utilities
└── docs/              # Documentation
```

#### [NEW] [package.json](file:///c:/Users/Vedant%20Bapuji%20Patil/OneDrive/Desktop/Hackathon/Veritas-AI/package.json)
Chrome extension dependencies and build configuration.

**Key Dependencies**:
- React 18+ (UI framework)
- TypeScript (type safety)
- Webpack/Vite (bundler)
- Chrome types (@types/chrome)

#### [NEW] [manifest.json](file:///c:/Users/Vedant%20Bapuji%20Patil/OneDrive/Desktop/Hackathon/Veritas-AI/extension/manifest.json)
Chrome Extension Manifest V3 configuration.

**Key Permissions**:
- `activeTab`: Access current tab content
- `storage`: Save scan history
- `webRequest`: Intercept video requests (optional)

---

### Component 2: Chrome Extension Frontend

#### [NEW] [popup.tsx](file:///c:/Users/Vedant%20Bapuji%20Patil/OneDrive/Desktop/Hackathon/Veritas-AI/extension/popup/popup.tsx)
Main popup UI for the extension with:
- Video analysis trigger button
- Status display
- Results visualization
- Settings panel

#### [NEW] [content-script.ts](file:///c:/Users/Vedant%20Bapuji%20Patil/OneDrive/Desktop/Hackathon/Veritas-AI/extension/content/content-script.ts)
Injected script that:
- Detects video elements on YouTube
- Injects "Veritas Seal" verification button
- Captures video frames/segments
- Communicates with background script

#### [NEW] [background.ts](file:///c:/Users/Vedant%20Bapuji%20Patil/OneDrive/Desktop/Hackathon/Veritas-AI/extension/background/background.ts)
Service worker that:
- Manages API communication
- Handles video processing requests
- Stores scan results
- Manages extension state

---

### Component 3: Local Backend Server (FastAPI)

#### [NEW] [main.py](file:///c:/Users/Vedant%20Bapuji%20Patil/OneDrive/Desktop/Hackathon/Veritas-AI/backend/main.py)
FastAPI server running locally with endpoints:
- `POST /api/analyze`: Main video analysis endpoint (accepts base64 frames)
- `GET /api/health`: Health check
- `GET /api/status/{task_id}`: Check analysis status (for async processing)

**Key Features**:
- CORS configuration for Chrome extension (localhost)
- Request validation and size limits
- Async processing for long-running tasks
- JSON response formatting
- Rate limiting (basic)

#### [NEW] [rppg.py](file:///c:/Users/Vedant%20Bapuji%20Patil/OneDrive/Desktop/Hackathon/Veritas-AI/backend/modules/rppg.py)
**Bio-Guard Module** - Your main differentiator!

Implements cutting-edge rPPG detection:
- MediaPipe face mesh (468 landmarks)
- Multi-ROI extraction (forehead, left cheek, right cheek)
- **POS (Plane-Orthogonal-to-Skin) algorithm** - skin-tone agnostic
- Bandpass filtering (0.7-4 Hz for 40-240 BPM)
- FFT analysis with peak detection
- SNR (Signal-to-Noise Ratio) calculation
- Confidence scoring based on signal quality

**Output**: 
```json
{
  "pulse_detected": true,
  "bpm": 72,
  "confidence": 0.87,
  "snr": 12.5,
  "assessment": "Likely Real - Strong biological signals"
}
```

#### [NEW] [gemini_analyzer.py](file:///c:/Users/Vedant%20Bapuji%20Patil/OneDrive/Desktop/Hackathon/Veritas-AI/backend/modules/gemini_analyzer.py)
**Physics-Guard Module** using FREE Gemini API:

- Uses **Google AI Studio** (free tier: 1500 requests/day)
- Multimodal analysis (sends video frames to Gemini)
- Detects:
  - Boundary artifacts (flickering edges)
  - Lighting inconsistencies
  - Unnatural facial movements
  - Background anomalies
  - Shadow/reflection mismatches

**Smart Prompting**:
```
"Analyze this video frame for AI-generated content. Look for:
1. Unnatural facial boundaries or blending
2. Inconsistent lighting/shadows
3. Unusual reflections in eyes
4. Background artifacts
Return JSON: {is_suspicious, confidence, findings[]}"
```

#### [NEW] [ensemble.py](file:///c:/Users/Vedant%20Bapuji%20Patil/OneDrive/Desktop/Hackathon/Veritas-AI/backend/modules/ensemble.py)
Decision fusion logic combining Bio-Guard + Physics-Guard:

```python
def make_final_decision(rppg_result, gemini_result):
    # Weighted ensemble
    bio_weight = 0.6  # rPPG is primary
    physics_weight = 0.4  # Gemini is secondary
    
    final_score = (bio_weight * rppg_result.confidence + 
                   physics_weight * gemini_result.confidence)
    
    return verdict, confidence, evidence_list
```

#### [NEW] [requirements.txt](file:///c:/Users/Vedant%20Bapuji%20Patil/OneDrive/Desktop/Hackathon/Veritas-AI/backend/requirements.txt)
```
fastapi==0.109.0
uvicorn==0.27.0
opencv-python==4.9.0.80
mediapipe==0.10.9
numpy==1.26.3
scipy==1.11.4
google-generativeai==0.3.2  # FREE Gemini API
python-multipart==0.0.6
python-dotenv==1.0.0
pillow==10.2.0
pydantic==2.5.3
```

**Total Size**: ~500MB (all dependencies)

---

### Component 4: Video Capture & Communication

#### [NEW] [video-capture.ts](file:///c:/Users/Vedant%20Bapuji%20Patil/OneDrive/Desktop/Hackathon/Veritas-AI/extension/content/video-capture.ts)
Utility for capturing video data:
- Extract frames from HTML5 video element
- Convert to Base64/Blob
- Handle CORS restrictions
- Optimize frame selection (every Nth frame)

#### [NEW] [api-client.ts](file:///c:/Users/Vedant%20Bapuji%20Patil/OneDrive/Desktop/Hackathon/Veritas-AI/extension/shared/api-client.ts)
API communication layer:
- POST video data to backend
- Handle responses and errors
- Implement retry logic
- Progress tracking

---

### Component 5: UI Components

#### [NEW] [VeritasSeal.tsx](file:///c:/Users/Vedant%20Bapuji%20Patil/OneDrive/Desktop/Hackathon/Veritas-AI/extension/content/components/VeritasSeal.tsx)
Injectable button component for video players with:
- Eye-catching design
- Click handler to trigger analysis
- Loading states
- Result badge display

#### [NEW] [ResultsPanel.tsx](file:///c:/Users/Vedant%20Bapuji%20Patil/OneDrive/Desktop/Hackathon/Veritas-AI/extension/popup/components/ResultsPanel.tsx)
Results display component showing:
- Authenticity verdict (Real/Fake/Uncertain)
- Confidence score
- Pulse detection graph (if available)
- Key findings

---

## MVP Feature Scope (6-Day Sprint)

### ✅ Included in MVP
1. **Chrome Extension** (React + TypeScript, Manifest V3)
2. **YouTube video detection** and frame capture (canvas-based)
3. **rPPG Bio-Guard module** (heartbeat detection)
4. **Gemini AI Physics-Guard** (scene analysis, artifacts)
5. **Google Cloud Run** backend deployment
6. **Ensemble decision fusion** (Bio + Physics)
7. **Results UI** with confidence scores and key findings
8. **Biometric consent UI**

### 🔜 Post-MVP Features (Deferred)
1. Audio deepfake detection (Audio-Guard)
2. Firestore database and scan history
3. Multi-platform support (Instagram, X/Twitter)
4. Advanced forensic dashboard with graphs
5. Real-time video call analysis
6. User authentication and accounts
7. API for third-party integration
8. Chrome Web Store public listing

---

## MVP Feature Scope (Hackathon Edition)

### ✅ Core Features (Must-Have)
1. **Chrome Extension** with professional UI
2. **YouTube video capture** (canvas-based, works around CORS)
3. **rPPG Bio-Guard** - Heartbeat detection (WOW factor!)
4. **Gemini AI Physics-Guard** - Scene analysis (credibility)
5. **Ensemble decision** - Combined verdict
6. **Results visualization** - Charts, confidence scores
7. **Consent UI** - Professional touch

### 🎨 Presentation Features (Hackathon Edge)
1. **Demo video** (2-3 minutes showing the extension in action)
2. **Beautiful UI** - Modern, glassmorphic design
3. **Loading animations** - Professional polish
4. **Evidence display** - Show WHY it's fake/real
5. **GitHub README** - Comprehensive documentation
6. **Presentation deck** - Technical slides for judges

### 🔜 Post-Hackathon (If Selected)
- Cloud deployment (Google Cloud Run)
- Multi-platform support (Instagram, X)
- Audio deepfake detection
- User accounts and history
- Chrome Web Store listing

---

## 4-5 Day Development Plan

### **Day 1: Setup & Backend Foundation** ⚡
**Time**: 6-8 hours

**Morning**:
- ✅ Create project structure
- ✅ Set up Python virtual environment
- ✅ Implement MediaPipe face detection
- ✅ Start rPPG algorithm (ROI extraction)

**Afternoon**:
- ✅ Complete rPPG module (POS algorithm, FFT)
- ✅ Create FastAPI server with `/analyze` endpoint
- ✅ Test rPPG with sample images/videos
- ✅ Get Gemini API key (free tier)

**Deliverable**: Working backend that detects pulse from video frames

---

### **Day 2: Gemini Integration & Polish** 🤖
**Time**: 6-8 hours

**Morning**:
- ✅ Implement Gemini analyzer module
- ✅ Design effective prompts for deepfake detection
- ✅ Test Gemini with various video frames

**Afternoon**:
- ✅ Create ensemble decision logic
- ✅ Format responses for frontend
- ✅ Add error handling and fallbacks
- ✅ Test full backend pipeline

**Deliverable**: Complete backend with Bio + AI analysis

---

### **Day 3: Chrome Extension - Core** 🔧
**Time**: 8-10 hours

**Morning**:
- ✅ Initialize extension (manifest.json, webpack config)
- ✅ Create content script for YouTube
- ✅ Implement video frame capture (canvas API)
- ✅ Build API communication layer

**Afternoon**:
- ✅ Create popup UI structure (React)
- ✅ Build results display component
- ✅ Inject "Veritas Seal" button on YouTube
- ✅ Test extension loading and injection

**Deliverable**: Functional extension that captures and sends video

---

### **Day 4: UI/UX & Integration** 🎨
**Time**: 8-10 hours

**Morning**:
- ✅ Design beautiful, modern UI (glassmorphism)
- ✅ Add loading animations and transitions
- ✅ Create consent modal
- ✅ Build evidence/results cards

**Afternoon**:
- ✅ Connect extension to backend (localhost)
- ✅ Test end-to-end flow
- ✅ Fix bugs and edge cases
- ✅ Polish UI/UX details

**Deliverable**: Working end-to-end system with great UX

---

### **Day 5: Testing, Demo & Presentation** 🚀
**Time**: 8-10 hours

**Morning**:
- ✅ Comprehensive testing (real videos, deepfakes)
- ✅ Record demo video (screen capture)
- ✅ Create presentation slides
- ✅ Write comprehensive README

**Afternoon**:
- ✅ Final bug fixes
- ✅ Create "How to Run" guide
- ✅ Package extension for judges
- ✅ Prepare pitch and talking points

**Deliverable**: Polished MVP ready for presentation

---

## Prerequisites

### Required Software
```bash
# Check installations
node --version   # Need 18+
python --version # Need 3.10+
git --version
```

### Free API Access
1. **Gemini API** (Google AI Studio):
   - Visit: https://makersuite.google.com/app/apikey
   - Create free API key
   - Limit: 60 requests/minute (plenty for demo)

### Development Tools
- VS Code (recommended)
- Chrome browser
- Postman/Thunder Client (API testing)

---

## Hackathon Presentation Strategy

### Demo Flow (2-3 minutes)
1. **Open YouTube** → Show real person video
2. **Click Veritas Seal** → Show analysis in progress
3. **Show Results** → "Likely Real - Biological pulse detected (72 BPM)"
4. **Open deepfake video** → Show detection
5. **Show Results** → "Likely Fake - No biological signals, boundary artifacts"

### Key Talking Points
- "We don't just detect fakes - we **prove authenticity** with biology"
- "Most detectors are black boxes - we show **forensic evidence**"
- "Works across all skin tones using POS algorithm"
- "Gemini AI adds physics-based reasoning"
- "Free tier, accessible to everyone"

### Technical Depth (For Judges)
- Explain rPPG algorithm
- Show MediaPipe face mesh
- Demonstrate FFT analysis
- Explain ensemble fusion
- Show code architecture

---

## Success Metrics

### Must-Have for Top Selection
✅ Working demo on **real YouTube videos**  
✅ Accurate detection (at least 70%+ on test cases)  
✅ Professional, polished UI  
✅ Clear, compelling demo video  
✅ Technical documentation  
✅ Unique approach (biological watermarks)  

### Bonus Points
- Real-time performance (<30s analysis)
- Beautiful visualizations (pulse graphs)
- Good error handling
- Code quality and structure
- Innovation in approach

---

## Risk Mitigation

| Risk | Solution |
|------|----------|
| rPPG doesn't work well | Use Gemini as primary, rPPG as experimental feature |
| Gemini API limits hit | Cache responses, use rPPG-only mode |
| Video capture fails | Use screenshot mode instead |
| Extension doesn't inject | Show standalone web app version |
| Time runs short | Focus on backend + simple UI (still impressive) |

---

## Cost Breakdown

**Total Cost: $0** 🎉

- Local backend: Free
- Gemini API: Free tier (60 req/min)
- Chrome extension: Free
- Hosting (for hackathon): Local/ngrok
- MediaPipe/OpenCV: Free open-source

**Post-selection costs** (if you advance):
- Google Cloud Run: ~$5-10/month
- Domain: ~$10/year
- Total: <$15/month

---

## Next Steps

Once approved, I'll immediately start:

1. **Create project structure** (extension + backend folders)
2. **Set up Python backend** with FastAPI
3. **Implement rPPG module** (Bio-Guard)
4. **Get you a Gemini API key** (I'll guide you)
5. **Build Chrome extension skeleton**
6. **Start coding!** 🚀

**Timeline**: Start today (Dec 30) → Complete by Jan 3-4

**Effort required**: ~6-10 hours/day for 4-5 days

**Outcome**: Hackathon-ready MVP that demonstrates innovation, technical depth, and real-world impact!
