# Veritas-AI Quick Start Guide

Get Veritas-AI running in 5 minutes!

## Prerequisites

- Python 3.10+ installed
- Google Gemini API Key (free): https://makersuite.google.com/app/apikey
- Chrome browser

## Step 1: Backend Setup (2 minutes)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
# Copy .env.example to .env and add your GEMINI_API_KEY

# Run server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

✅ Backend running at http://localhost:8000

## Step 2: Extension Setup (2 minutes)

```bash
cd extension

# Install dependencies
npm install

# Build extension
npm run build
```

## Step 3: Load Extension (1 minute)

1. Open Chrome
2. Go to `chrome://extensions/`
3. Enable **Developer mode** (top right)
4. Click **Load unpacked**
5. Select `extension/dist` folder

✅ Extension installed!

## Step 4: Test It!

1. Open any YouTube video with a face
2. Look for the **VERITAS SEAL** button (top-left of video)
3. Click it and wait for analysis
4. See detailed results!

## Troubleshooting

**Backend won't start?**
- Check if port 8000 is in use
- Verify GEMINI_API_KEY in .env file
- Check Python version: `python --version` (need 3.10+)

**Extension can't connect?**
- Make sure backend is running
- Check browser console for errors
- Verify API URL in extension code

**Analysis fails?**
- Check backend logs
- Verify API key is valid
- Make sure video has a visible face

## Next Steps

- Read `DEPLOYMENT.md` for production deployment
- Check `IMPROVEMENTS_SUMMARY.md` for all features
- Review API docs at http://localhost:8000/docs

## Support

For issues, check:
1. Backend logs in `backend/logs/`
2. Browser console (F12)
3. API health: http://localhost:8000/api/health

