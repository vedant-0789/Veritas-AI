# Veritas-AI 🛡️

> **Real-time Deepfake Detection using Biometric Signal Analysis (rPPG) and Multimodal AI.**

![Veritas-AI Banner](https://via.placeholder.com/1200x400/0f172a/38bdf8?text=Veritas-AI+|+Defending+Authenticity)

Veritas-AI is a Chrome Extension that acts as a digital "Bio-Guard", verifying video authenticity by detecting the subtle, invisible physiological signals of life (hair-color changes due to blood flow) that generative AI currently fails to replicate.

## 🌟 Key Features

- **❤️ Bio-Guard (rPPG)**: Detects human pulse signals from video pixels (Remote Photoplethysmography). Deepfakes don't have a heartbeat.
- **🧠 Physics-Guard (Gemini AI)**: Analyzes scene lighting, reflections, and boundary artifacts using Google's Gemini 2.0 Flash.
- **⚡ Real-time Analysis**: In-browser analysis with instant feedback directly on the YouTube player.
- **🔒 Privacy First**: Analysis happens locally or via secure ephemeral API calls; no video data is stored.
- **✨ Glassmorphic UI**: A premium, trustworthy user interface designed for transparency.

## 🛠️ Technology Stack

- **Frontend**: React, TypeScript, Vite, Tailwind CSS (Chrome Extension)
- **Backend**: Python, FastAPI, OpenCV, NumPy, SciPy
- **AI Core**: MediaPipe (Face Mesh), Google Gemini 2.0 Flash
- **Communication**: REST API (Localhost)

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Google Gemini API Key (Free)

### 1. Setup Backend

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Create .env file with your GEMINI_API_KEY
cp .env.example .env
```

### 2. Run Server

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. Build Extension

```bash
cd extension
npm install
npm run build
```

### 4. Install in Chrome

1. Open `chrome://extensions/`
2. Enable **Developer mode**
3. Click **Load unpacked**
4. Select `Veritas-AI/extension/dist`

## 🧪 How to Test

1. Open any YouTube video containing a face.
2. Look for the **VERITAS** button in the top-right of the video player.
3. Click to authorize a scan.
4. Wait ~5 seconds for **Bio-Guard** and **Physics-Guard** to complete.
5. Review the authenticity score and forensic evidence.

## 🏆 Hackathon Notes

- **Novelty**: First browser extension to combine rPPG (Heartbeat detection) with GenAI artifacts.
- **Feasibility**: Runs on consumer hardware; rPPG is computationally lightweight.
- **Impact**: Restores trust in digital media by proving what is _real_, not just detecting what is _fake_.

## 📄 License

MIT © 2025 Veritas-AI Team
