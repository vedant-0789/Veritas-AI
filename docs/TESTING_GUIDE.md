# Testing Guide - Veritas-AI

## Step-by-Step Testing Instructions

### Step 1: Start the Backend Server

Open a terminal and run:

```bash
cd backend

# Activate virtual environment (if not already)
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Make sure you have .env file with GEMINI_API_KEY
# If not, create it:
# Copy .env.example to .env and add your API key

# Start the server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
🚀 Starting Veritas-AI Backend on 0.0.0.0:8000
📚 API Docs: http://localhost:8000/docs
```

✅ **Backend is running!** Keep this terminal open.

### Step 2: Verify Backend is Working

Open a new terminal and test:

```bash
# Test health endpoint
curl http://localhost:8000/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.1.0",
  "modules": {
    "rppg": "active",
    "gemini": "active",
    "temporal": "active",
    "ensemble": "active"
  }
}
```

✅ **Backend is healthy!**

### Step 3: Build the Extension

Open a new terminal:

```bash
cd extension

# Install dependencies (if not done)
npm install

# Build the extension
npm run build
```

**Expected Output:**
```
✓ built in XXXms
```

✅ **Extension built!** Files are in `extension/dist/`

### Step 4: Load Extension in Chrome

1. Open Chrome
2. Go to `chrome://extensions/`
3. **Enable "Developer mode"** (toggle in top-right)
4. Click **"Load unpacked"**
5. Navigate to: `Veritas-AI/extension/dist`
6. Select the folder

✅ **Extension loaded!** You should see "Veritas-AI | Deepfake Detector"

### Step 5: Test on YouTube

1. **Open YouTube** in Chrome
2. **Search for a video** with a person's face (e.g., "interview", "talking head", "news")
3. **Wait for video to load**
4. **Look for the "VERITAS SEAL" button** (top-left of video player)
   - It should have a pulsing blue glow
   - Shows "VERITAS SEAL" text

5. **Click the button**
   - First time: You'll see a consent modal
   - Click "I Agree"
   - Analysis overlay appears

6. **Watch the analysis:**
   - Status updates: "Acquiring Target..." → "Processing Biometrics..."
   - Takes 5-15 seconds
   - Results overlay appears

### Step 6: Review Results

The results overlay shows:

**Top Section:**
- Verdict: ✅ LIKELY REAL / ❌ LIKELY FAKE / ⚠️ UNCERTAIN
- Confidence: XX%

**Forensic Analysis:**
- List of evidence (color-coded)
- Green ✅ = Real indicators
- Red ❌ = Fake indicators
- Yellow ⚠️ = Warnings

**Module Breakdown:**
- **BIO-GUARD**: Pulse detected? BPM? SNR?
- **PHYSICS-GUARD**: Authentic or Suspicious?
- **TEMPORAL-GUARD**: Consistent or Inconsistent?

**Summary:**
- Human-readable explanation

### Step 7: Test Different Videos

Try different types:

1. **Real Person Video** (should show REAL)
   - News anchor
   - Interview
   - Vlog

2. **Deepfake Video** (if available, should show FAKE)
   - Known deepfake examples
   - AI-generated faces

3. **Compressed Video** (might show UNCERTAIN)
   - Low quality videos
   - Heavily compressed

## 🔍 What to Look For

### Good Signs:
- ✅ Button appears on YouTube videos
- ✅ Analysis completes in 5-15 seconds
- ✅ Results show detailed evidence
- ✅ Confidence scores are reasonable
- ✅ Real videos show pulse detection

### Troubleshooting:

**Button doesn't appear:**
- Refresh the YouTube page
- Check browser console (F12) for errors
- Make sure extension is enabled

**Analysis fails:**
- Check backend is running
- Check backend logs for errors
- Verify GEMINI_API_KEY is set
- Check browser console for errors

**Backend connection error:**
- Verify backend is running on port 8000
- Check `http://localhost:8000/api/health`
- Check extension's API URL in `shared/api-client.ts`

**No results:**
- Check backend terminal for errors
- Verify video has visible face
- Try a different video

## 📊 Expected Results

### For Real Videos:
```
Verdict: ✅ LIKELY REAL
Confidence: 75-95%

Evidence:
✅ Strong biological pulse detected: 72 BPM (SNR: 8.5)
✅ AI analysis confirms authentic human characteristics
✅ High temporal consistency detected
✅ Natural eye blinks detected
```

### For Fake Videos:
```
Verdict: ❌ LIKELY FAKE
Confidence: 70-90%

Evidence:
❌ No biological pulse signal detected
❌ AI detected manipulation artifacts
❌ Low temporal consistency (possible manipulation)
❌ Very static face (possible deepfake)
```

## 🎯 Testing Checklist

- [ ] Backend starts successfully
- [ ] Health endpoint works
- [ ] Extension loads in Chrome
- [ ] Button appears on YouTube
- [ ] Consent modal works
- [ ] Analysis completes
- [ ] Results display correctly
- [ ] Evidence is color-coded
- [ ] Module breakdown shows
- [ ] Summary is readable

## 🐛 Debugging

### Check Backend Logs:
Look at the terminal where backend is running. You should see:
```
INFO: Analysis request received: 15 frames
INFO: Starting analysis task abc123
INFO: Analysis completed: abc123 - Verdict: LIKELY_REAL (Confidence: 0.85) in 8.23s
```

### Check Browser Console:
1. Press F12 on YouTube page
2. Go to "Console" tab
3. Look for:
   - "Veritas-AI: Content script loaded"
   - "Veritas-AI: Player found, injecting button..."
   - Any errors (red text)

### Check Extension Popup:
1. Click extension icon
2. Should show "SYSTEM ACTIVE" if backend connected
3. If shows "Backend Disconnected", check backend is running

## ✅ Success Criteria

You've successfully tested if:
1. ✅ Button appears on YouTube videos
2. ✅ Analysis completes without errors
3. ✅ Results show verdict and evidence
4. ✅ Real videos show pulse detection
5. ✅ Evidence is clear and understandable

## 🎉 Ready for Demo!

Once everything works, you're ready to:
- Demo to judges
- Record a demo video
- Present your hackathon project

Good luck! 🚀

