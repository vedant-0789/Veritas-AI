# Veritas-AI: The Universal Truth Layer

## A Multimodal Forensic Defense Suite for Browser-Based Deepfake Detection

![Project Status](https://img.shields.io/badge/status-MVP%20Development-orange)
![License](https://img.shields.io/badge/license-MIT-blue)
![Platform](https://img.shields.io/badge/platform-Chrome%20Extension-green)

---

## 🎯 Problem Statement

In 2025, generative AI has reached a **"post-truth" era** where synthetic videos (Deepfakes) are indistinguishable from reality, leading to:

- 💰 **Massive financial fraud** ($40B projected by 2027)
- 🗳️ **Political disinformation** during critical elections
- 👥 **Social manipulation** and erosion of digital trust

### The Critical Gap

Most existing detection tools are:
- ❌ **"Black boxes"** that fail to explain their decisions
- ❌ **Enterprise-only** solutions inaccessible to average users
- ❌ **Vulnerable** to real-world social media compression
- ❌ **Biased** with significantly lower accuracy for darker skin tones

**We need a transparent, forensic-grade verification tool that works directly in the browser and provides verifiable "biological" and "physical" evidence of authenticity.**

---

## 💡 The Solution

**Veritas-AI** is a hybrid ecosystem consisting of a **Chrome Extension** and **Google Cloud-powered Backend** that provides **"One-Click Truth Verification."**

Unlike standard classifiers, Veritas-AI uses an **Ensemble Forensic Pipeline**:

### 🧬 The Bio-Engine
Extracts **remote Photoplethysmography (rPPG)** signals from facial regions to detect a human pulse—a biological watermark that synthetic models cannot currently replicate.

### 🔬 The Physics Engine (Gemini 1.5 Pro)
Analyzes scenes for **"Physical Hallucinations"**:
- Inconsistent shadows and lighting angles
- Phoneme-Viseme mismatches (lip movements vs. audio)
- Reflection inconsistencies
- Boundary artifacts

### 🎙️ The Audio Guard
Scans for synthetic spectral artifacts in voice cloning using:
- MFCC (Mel-frequency cepstral coefficients)
- Spectral consistency analysis
- Audio-visual synchronization checks

---

## ✨ Key Features

### 🌐 The "Veritas Seal" UI
- **Chrome Extension** that injects a verification button directly into YouTube, Instagram, and X video players
- Uses Base64/Blob capturing to bypass browser CORS/CSP restrictions
- One-click verification without leaving your browser

### 🎯 Compression-Resilient rPPG
- Implements **Signal-to-Noise Ratio (SNR)** and **Power Spectral Density (PSD)** checks
- Automatically pivots to "Multimodal Contextual Check" when compression is too high
- Works across various video qualities and platforms

### ⚖️ Fairness-First Detection
- Uses **MediaPipe** to isolate multiple facial Regions of Interest (Cheeks, Forehead, Chin)
- Implements **POS (Plane-Orthogonal-to-Skin)** algorithm
- Ensures accurate pulse detection across **all skin tones** and lighting conditions

### 📊 Asynchronous Forensic Dashboard
- React-based portal with detailed reports
- Heart-rate graphs and physics-anomaly heatmaps
- Explainable AI results with forensic evidence

### 🔒 Privacy-by-Design
- DPDP Act (India) compliant
- Biometric consent pop-up before analysis
- Video blobs purged from Cloud Run memory immediately after analysis
- Stateless processing with no permanent storage

---

## 🛠️ Technology Stack

### Core Infrastructure (Google Cloud)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend Hosting** | Google Cloud Run (GPU-enabled) | High-speed containerized Python services for video processing |
| **Development Platform** | Firebase Studio | Full-stack AI workspace with Authentication & Firestore |
| **Database** | Cloud Firestore | NoSQL database for scan history and metadata |
| **Storage** | Cloud Storage (GCS) | Secure, encrypted temporary bucket for video segments |
| **API Gateway** | Cloud Endpoints | Secure communication and rate limiting |

### AI Engine (Multimodal Analysis)

#### Primary Models
- **Gemini 3 Flash**: Real-time reasoning, spatial analysis, and agentic task sequencing
- **Gemini 1.5 Pro**: Deep scan with long-context analysis for temporal consistency
- **Vertex AI**: Custom CNN models for specialized artifact detection

### Specialized Analysis Modules

#### 1. Bio-Guard (The Heartbeat Module)

**Technology Stack:**
```
Libraries: OpenCV, SciPy, NumPy, MediaPipe
Algorithm: POS (Plane-Orthogonal-to-Skin)
Platform: Google Cloud Run
```

**How it works:**
- Detects microscopic skin color fluctuations (0.5%-1%) caused by blood flow
- Uses FFT (Fast Fourier Transform) and Butterworth filtering
- Works across all skin tones using the POS algorithm

#### 2. Physics-Guard (The Reality Module)

**Technology Stack:**
```
Primary Model: Gemini 1.5 Pro (via Vertex AI)
Pre-processing: Dlib/MTCNN for face detection
Platform: Vertex AI Studio
```

**Detection Capabilities:**
- Boundary flickering around chin/hair
- Specular reflection inconsistencies
- Shadow angle mismatches
- Environmental context verification

#### 3. Audio-Guard (The Voice Module)

**Technology Stack:**
```
Libraries: Librosa, Torchaudio
Algorithm: MFCC + Wav2Lip
Platform: Speech-to-Text API & Vertex AI
```

**Analysis:**
- Spectral consistency (vocal fingerprint)
- Detection of robotic artifacts
- Lip-sync accuracy within 50ms window

### Frontend & Integration

- **Browser Extension**: React + TypeScript (Manifest V3)
- **Communication Protocol**: Model Context Protocol (MCP)
- **Security**: reCAPTCHA Enterprise for bot prevention

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER'S BROWSER                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Chrome Extension (Veritas Seal)                      │  │
│  │  - Video Capture (Base64/Blob)                        │  │
│  │  - Biometric Consent UI                               │  │
│  └──────────────────┬───────────────────────────────────┘  │
└─────────────────────┼───────────────────────────────────────┘
                      │
                      ▼ (Encrypted HTTPS)
┌─────────────────────────────────────────────────────────────┐
│              GOOGLE CLOUD INFRASTRUCTURE                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Cloud Endpoints (API Gateway)                        │  │
│  │  - Authentication & Rate Limiting                     │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │  Google Cloud Run (Processing Core)                   │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │  Data Orchestrator (Python)                      │ │  │
│  │  │  - Splits video into parallel processing tracks  │ │  │
│  │  └─────────┬──────────────────────────┬─────────────┘ │  │
│  │            │                          │                │  │
│  │  ┌─────────▼─────────┐    ┌──────────▼─────────────┐ │  │
│  │  │  BIO-ENGINE       │    │  PHYSICS-ENGINE        │ │  │
│  │  │  (rPPG Module)    │    │  (Gemini 1.5 Pro)      │ │  │
│  │  │                   │    │                        │ │  │
│  │  │  - MediaPipe      │    │  - Vertex AI           │ │  │
│  │  │  - OpenCV         │    │  - Logic Scanning      │ │  │
│  │  │  - POS Algorithm  │    │  - Temporal Check      │ │  │
│  │  └─────────┬─────────┘    └──────────┬─────────────┘ │  │
│  │            │                          │                │  │
│  │            └──────────┬───────────────┘                │  │
│  │                       ▼                                │  │
│  │            ┌────────────────────────┐                  │  │
│  │            │  Decision Fusion Model │                  │  │
│  │            │  - Ensemble Algorithm  │                  │  │
│  │            └──────────┬─────────────┘                  │  │
│  └───────────────────────┼──────────────────────────────┘  │
│                          │                                  │
│  ┌───────────────────────▼──────────────────────────────┐  │
│  │  Cloud Firestore                                      │  │
│  │  - Stores forensic reports & scan history            │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  TRUTH REPORT         │
              │  - Confidence Score   │
              │  - Heartbeat Graph    │
              │  - Forensic Evidence  │
              └───────────────────────┘
```

---

## 🎭 How Veritas-AI is Different

| Feature | Traditional Detectors | Veritas-AI |
|---------|----------------------|-------------|
| **Accessibility** | Enterprise APIs ($$$) | Free Chrome Extension |
| **Detection Method** | Pixel artifact analysis | Biological watermarks (rPPG) |
| **Explainability** | Black box (80% Fake) | Forensic transparency reports |
| **Resilience** | Pattern matching | Physical reasoning + biology |
| **Skin Tone Bias** | Significant bias | Fairness-first (POS algorithm) |
| **Compression** | Fails on low quality | Adaptive multimodal fallback |
| **Proof Type** | Only catches fakes | Proves authenticity too |

### The "Liar's Dividend" Solution

Veritas-AI provides **Positive Authentication**: By confirming biological signs (heartbeat) and physical consistency, it can **prove a video is authentic**, preventing individuals from falsely claiming real evidence is a deepfake.

---

## 📈 Real-World Impact

### 💰 Economic Stability
**Problem**: $25.6M stolen in Hong Kong via deepfake CFO in video conference  
**Veritas Solution**: Bio-Guard instantly flags zero biological pulse + inconsistent lighting

### 🗳️ Democracy Protection
**Problem**: Slovakia election sabotage via deepfake audio during media moratorium  
**Veritas Solution**: Audio-Guard detects robotic spectral artifacts + unnatural speech rhythm

### 👨‍👩‍👧 Family Safety
**Problem**: Grandparent scams using cloned children's voices  
**Veritas Solution**: Real-time voice verification before wire transfers

### ⚖️ Digital Accountability
**Problem**: Public figures claiming real evidence is "just a deepfake"  
**Veritas Solution**: Forensic certificates prove authenticity with biological evidence

### 🛡️ Human Dignity
**Problem**: Non-consensual deepfake imagery (47M views in 17 hours)  
**Veritas Solution**: Pulse inconsistency detection + blending artifact identification

---


## 🎯 Use Cases & Applications

### 1. **Social Media Verification**
Instant verification while scrolling through YouTube, Instagram, X (Twitter), and Facebook.

### 2. **Election Integrity**
Real-time debunking of political deepfakes during sensitive election periods.

### 3. **Corporate Security**
Protection against CEO/CFO impersonation in video conferences.

### 4. **Financial Fraud Prevention**
Verification of celebrity endorsements in investment schemes.

### 5. **Journalism & Media**
Verification of source material before publication.

### 6. **Legal Evidence**
Forensic certificates for court proceedings and law enforcement.

### 7. **Personal Safety**
Protection against family emergency scams and voice cloning attacks.

---

## 🔐 Privacy & Security

### Compliance
- ✅ DPDP Act (Digital Personal Data Protection Act, India) compliant
- ✅ GDPR-ready architecture
- ✅ Biometric data consent workflows

### Data Protection
- 🔒 **Ephemeral Processing**: Videos processed in temporary Cloud Run instances
- 🔒 **No Permanent Storage**: Data purged immediately after analysis
- 🔒 **End-to-End Encryption**: All data transfers encrypted via HTTPS
- 🔒 **Anonymized Signals**: Biometric data never linked to personal identity
- 🔒 **reCAPTCHA Enterprise**: Bot prevention and abuse protection

---

## 📊 Success Metrics

By successfully implementing Veritas-AI, we aim to:

- 🎯 **Prevent $1B+** in deepfake-related fraud annually
- 🎯 **Protect 100M+** users from synthetic media manipulation
- 🎯 **Verify 10M+** videos in the first year
- 🎯 **Achieve 95%+** accuracy across all demographic groups
- 🎯 **Reduce "Liar's Dividend"** incidents by providing positive authentication

---

## 🌟 Why This Matters

> **"We are in an AI Arms Race. If we don't deploy accessible, forensic-grade verification tools now, we risk a future where digital trust completely collapses."**

Veritas-AI democratizes forensic science by:
- ✨ Moving detection from high-end labs to the browser
- ✨ Empowering 5.4 billion internet users to verify content in real-time
- ✨ Providing transparent explanations ("No biological pulse detected")
- ✨ Restoring public trust in digital media
- ✨ Creating a scalable, cross-platform defense against AI weaponization

---

## 👥 Who This Helps

### Everyday Users
Protect yourself from scams and manipulation while browsing social media.

### Voters & Citizens
Verify political content during elections to make informed decisions.

### Journalists & Media
Ensure source authenticity before publication.

### Businesses & Corporations
Prevent multi-million dollar fraud from deepfake impersonation.

### Law Enforcement
Generate forensic certificates for legal proceedings.

### Victims of Deepfakes
Obtain verifiable proof that harmful content is synthetic.

---

## 🛣️ Roadmap

### Q1 
- ✅ MVP Chrome Extension release
- ✅ Bio-Guard (rPPG) module deployment
- ✅ Physics-Guard (Gemini integration)

### Q2 
- 🔜 Mobile app (iOS/Android)
- 🔜 API for social media platforms
- 🔜 Enterprise licensing program

### Q3 
- 🔜 Real-time video call integration (Zoom, Meet)
- 🔜 Advanced audio deepfake detection
- 🔜 Multi-language support

### Q4 
- 🔜 Blockchain-based verification certificates
- 🔜 AI model updates for emerging deepfake techniques
- 🔜 Global partnership expansion

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

---

## 📧 Contact

For questions, partnerships, or media inquiries:
- **Email**: contact@veritas-ai.com
- **Website**: [www.veritas-ai.com](https://www.veritas-ai.com)
- **Twitter**: [@VeritasAI](https://twitter.com/VeritasAI)

---

## 🙏 Acknowledgments

Built with:
- Google Cloud Platform
- Gemini 1.5 Pro & Gemini 3 Flash
- Firebase
- MediaPipe
- The open-source community

---

<div align="center">

**Veritas-AI: Because Truth Matters**

*Restoring trust in the digital age, one verification at a time.*

[![Chrome Web Store](https://img.shields.io/badge/Chrome%20Web%20Store-Install-blue?logo=google-chrome)](https://chrome.google.com/webstore)
[![Documentation](https://img.shields.io/badge/Docs-Read-green)](https://docs.veritas-ai.com)
[![Support](https://img.shields.io/badge/Support-Get%20Help-orange)](https://support.veritas-ai.com)

</div>
