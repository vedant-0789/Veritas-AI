
### Option 0: Render.com (Free & Easiest for MVP)

**Cost**: $0/month

1. **Prepare Repository**:
   - Ensure your code is pushed to GitHub.
   - We have already updated `requirements.txt` to use headless OpenCV (required for cloud).

2. **Create Service on Render**:
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Click **New +** -> **Web Service**
   - Connect your GitHub repository `Veritas-AI`
   - **Root Directory**: `backend` (Important!)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free

3. **Environment Variables** (on Render setup page):
   - Key: `GEMINI_API_KEY`
   - Value: `Your_Actual_Gemini_Key`
   - Key: `PYTHON_VERSION`
   - Value: `3.10.12`

4. **Deploy**:
   - Click "Create Web Service".
   - Wait for deployment to finish (green "Live" badge).
   - Copy your service URL (e.g., `https://veritas-ai.onrender.com`).

5. **Update Extension**:
   - Open `extension/shared/api-client.ts`
   - Change `API_BASE_URL` to your Render URL: `https://veritas-ai.onrender.com/api`
   - Rebuild extension:
     ```bash
     cd extension
     npm run build
     ```
   - Zip the `extension/dist` folder for your submission.
