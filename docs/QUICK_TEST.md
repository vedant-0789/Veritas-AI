# Quick Test Instructions

## 🚀 Fast Setup (3 Steps)

### 1️⃣ Start Backend (Terminal 1)
```powershell
cd backend
venv\Scripts\activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**✅ Success when you see:** `Uvicorn running on http://0.0.0.0:8000`

### 2️⃣ Build Extension (Terminal 2)
```powershell
cd extension
npm run build
```

**✅ Success when you see:** `✓ built in XXXms`

### 3️⃣ Load in Chrome
1. Open `chrome://extensions/`
2. Enable **Developer mode** (top-right)
3. Click **Load unpacked**
4. Select: `Veritas-AI\extension\dist`

**✅ Success when you see:** Extension appears in list

## 🎬 Test on YouTube

1. Open any YouTube video with a face
2. Look for **"VERITAS SEAL"** button (top-left of video)
3. Click it → Agree to consent
4. Wait 5-15 seconds
5. See results!

## ✅ What You Should See

**On YouTube:**
- Blue pulsing button: "VERITAS SEAL"
- Analysis overlay with progress
- Results overlay with verdict

**Results Include:**
- ✅/❌/⚠️ Verdict
- Confidence %
- Evidence list
- Module breakdown
- Summary

## 🐛 Quick Fixes

**Button not showing?**
- Refresh YouTube page
- Check console (F12) for errors

**Backend error?**
- Check `.env` has `GEMINI_API_KEY`
- Check port 8000 is free

**Extension error?**
- Check backend is running
- Check `http://localhost:8000/api/health`

## 📊 Expected Analysis Time: 5-15 seconds

Ready! 🎉

