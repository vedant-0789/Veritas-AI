# Veritas-AI Project Overview

## 🏗️ What We've Built

### Backend (Python FastAPI)

#### **6 Detection Modules:**

1. **Bio-Guard (rPPG)** - `modules/rppg.py`
   - Pulse detection (BPM, SNR)
   - Eye blink detection
   - Facial landmark stability
   - Signal quality analysis

2. **Physics-Guard (Gemini AI)** - `modules/gemini_analyzer.py`
   - Visual artifact detection
   - Lighting consistency
   - Natural feature analysis
   - Real/fake discrimination

3. **Temporal-Guard** - `modules/temporal_analyzer.py`
   - Frame-to-frame consistency
   - Motion smoothness
   - Color consistency
   - Temporal variance

4. **Advanced-Guard** - `modules/advanced_analyzer.py`
   - Lip-sync analysis
   - Breathing detection
   - Micro-expression analysis
   - Head movement analysis

5. **Vision-Guard** - `modules/vision_analyzer.py` (Optional)
   - Face detection quality
   - Emotional expressions
   - Image properties

6. **Ensemble** - `modules/ensemble.py`
   - Multi-modal fusion
   - Dynamic weighting
   - Evidence collection
   - Decision making

#### **API Endpoints:**

- `POST /api/analyze` - Async video analysis
- `POST /api/analyze-sync` - Synchronous analysis (faster)
- `GET /api/status/{task_id}` - Check analysis status
- `GET /api/health` - Health check
- `GET /api/metrics/stats` - Statistics & metrics
- `GET /api/metrics/health-detailed` - Detailed health

#### **Features:**
- ✅ Rate limiting (60 req/min)
- ✅ Security headers
- ✅ Structured logging
- ✅ Metrics tracking
- ✅ Error handling
- ✅ CORS enabled

### Frontend (Chrome Extension)

#### **Components:**

1. **Content Script** - `content/content-script.ts`
   - YouTube video detection
   - "VERITAS SEAL" button injection
   - Frame capture coordination
   - Results overlay display

2. **Video Capture** - `content/video-capture.ts`
   - Direct frame capture
   - Fallback capture (for CORS)
   - Frame sequence capture

3. **Background Service** - `background/background.ts`
   - API communication
   - Health checks
   - Tab capture handling

4. **Popup UI** - `popup/popup.tsx`
   - Backend connection status
   - Manual scan trigger
   - Results display

5. **Results Panel** - `popup/components/ResultsPanel.tsx`
   - Verdict display
   - Evidence list
   - Module breakdown
   - Confidence scores

#### **Features:**
- ✅ Beautiful glassmorphic UI
- ✅ Real-time analysis overlay
- ✅ Consent modal
- ✅ Error handling
- ✅ Progress indicators
- ✅ Color-coded evidence

## 📊 Detection Flow

```
YouTube Video
    ↓
Extension Captures 15 Frames
    ↓
Frames Sent to Backend
    ↓
6 Modules Analyze in Parallel:
  • Bio-Guard (rPPG)
  • Physics-Guard (Gemini)
  • Temporal-Guard
  • Advanced-Guard
  • Vision-Guard (optional)
  • Ensemble (combines all)
    ↓
Final Verdict + Evidence
    ↓
Results Displayed in Overlay
```

## 🎯 What Gets Detected

### Real Video Indicators:
- ✅ Biological pulse (heartbeat)
- ✅ Natural eye blinks
- ✅ Stable facial landmarks
- ✅ Consistent lighting
- ✅ Natural skin texture
- ✅ Smooth motion
- ✅ Natural breathing
- ✅ Proper lip-sync

### Fake Video Indicators:
- ❌ No pulse signal
- ❌ Unstable landmarks
- ❌ Flickering edges
- ❌ Inconsistent lighting
- ❌ Jerky motion
- ❌ Static face
- ❌ Poor lip-sync
- ❌ Unnatural textures

## 📁 Project Structure

```
Veritas-AI/
├── backend/
│   ├── main.py                 # FastAPI server
│   ├── modules/                # Detection modules
│   │   ├── rppg.py
│   │   ├── gemini_analyzer.py
│   │   ├── temporal_analyzer.py
│   │   ├── advanced_analyzer.py
│   │   ├── ensemble.py
│   │   └── ...
│   ├── api/                    # API utilities
│   │   ├── middleware.py
│   │   └── metrics.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── extension/
│   ├── content/                # Content scripts
│   │   ├── content-script.ts
│   │   └── video-capture.ts
│   ├── background/            # Background service
│   │   └── background.ts
│   ├── popup/                 # Popup UI
│   │   ├── popup.tsx
│   │   └── components/
│   ├── shared/                # Shared utilities
│   │   └── api-client.ts
│   └── dist/                  # Built extension
│
└── docs/
    ├── QUICK_START.md
    ├── DEPLOYMENT.md
    └── ...
```

## 🚀 Ready to Test!

Everything is built and ready. Follow the testing guide below!

