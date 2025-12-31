# Veritas-AI Deployment Guide

This guide covers deploying Veritas-AI for production use, including local development, Docker deployment, and cloud platforms.

## Prerequisites

- Python 3.10+ or Docker
- Google Gemini API Key (free tier available)
- Node.js 18+ (for extension development)

## Quick Start (Local Development)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

### 2. Extension Setup

```bash
cd extension

# Install dependencies
npm install

# Build extension
npm run build

# Load in Chrome
# 1. Open chrome://extensions/
# 2. Enable "Developer mode"
# 3. Click "Load unpacked"
# 4. Select extension/dist folder
```

## Docker Deployment

### Build and Run

```bash
cd backend

# Build image
docker build -t veritas-ai-backend .

# Run container
docker-compose up -d

# Or manually:
docker run -d \
  -p 8000:8000 \
  -e GEMINI_API_KEY=your_key_here \
  --name veritas-backend \
  veritas-ai-backend
```

### Using Docker Compose

```bash
# Create .env file first
cp .env.example .env
# Edit .env with your API keys

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Production Deployment

### Option 1: Google Cloud Run (Recommended)

1. **Install Google Cloud SDK**
   ```bash
   # Follow: https://cloud.google.com/sdk/docs/install
   ```

2. **Build and Push Image**
   ```bash
   # Set your project
   gcloud config set project YOUR_PROJECT_ID
   
   # Build and push
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/veritas-ai
   ```

3. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy veritas-ai \
     --image gcr.io/YOUR_PROJECT_ID/veritas-ai \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars GEMINI_API_KEY=your_key_here \
     --memory 2Gi \
     --cpu 2 \
     --timeout 300
   ```

4. **Update Extension**
   - Update `API_BASE_URL` in `extension/shared/api-client.ts` to your Cloud Run URL
   - Rebuild extension

### Option 2: AWS Elastic Beanstalk

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB**
   ```bash
   cd backend
   eb init -p python-3.11 veritas-ai
   ```

3. **Create and Deploy**
   ```bash
   eb create veritas-ai-env
   eb setenv GEMINI_API_KEY=your_key_here
   eb deploy
   ```

### Option 3: Heroku

1. **Install Heroku CLI**
   ```bash
   # Follow: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Deploy**
   ```bash
   cd backend
   heroku create veritas-ai
   heroku config:set GEMINI_API_KEY=your_key_here
   git push heroku main
   ```

### Option 4: DigitalOcean App Platform

1. **Create App from Dockerfile**
   - Go to DigitalOcean App Platform
   - Create new app
   - Connect GitHub repository
   - Select Dockerfile in `backend/` directory

2. **Set Environment Variables**
   - `GEMINI_API_KEY`: Your API key
   - `HOST`: `0.0.0.0`
   - `PORT`: `8080` (DigitalOcean default)

3. **Deploy**

### Option 5: Railway

1. **Connect Repository**
   - Go to Railway.app
   - New Project → Deploy from GitHub
   - Select your repository

2. **Configure**
   - Set root directory to `backend/`
   - Add environment variable: `GEMINI_API_KEY`

3. **Deploy**

## Environment Variables

### Required
- `GEMINI_API_KEY`: Your Google Gemini API key (get from https://makersuite.google.com/app/apikey)

### Optional
- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8000`)
- `DEBUG`: Enable debug mode (default: `false`)
- `CORS_ORIGINS`: Comma-separated list of allowed origins

## Performance Tuning

### For Production

1. **Increase Workers** (if using multiple processes):
   ```bash
   uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
   ```

2. **Resource Limits**:
   - Minimum: 1 CPU, 1GB RAM
   - Recommended: 2 CPU, 2GB RAM
   - For high traffic: 4 CPU, 4GB RAM

3. **Timeout Settings**:
   - Analysis timeout: 60-120 seconds
   - Request timeout: 300 seconds

## Monitoring

### Health Check Endpoint

```bash
curl http://localhost:8000/api/health
```

Response:
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

### Logging

Logs are output to stdout/stderr. For production, consider:
- CloudWatch (AWS)
- Stackdriver (GCP)
- Datadog
- Sentry (for error tracking)

## Security Considerations

1. **API Keys**: Never commit `.env` files
2. **CORS**: Restrict origins in production
3. **Rate Limiting**: Implement rate limiting for production
4. **HTTPS**: Always use HTTPS in production
5. **Authentication**: Consider adding API authentication

## Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify GEMINI_API_KEY is set
- Check Python version (3.10+)

### Extension can't connect
- Verify backend is running
- Check CORS settings
- Update API_BASE_URL in extension

### Analysis fails
- Check API key is valid
- Verify sufficient frames are captured
- Check logs for specific errors

## Support

For issues or questions:
1. Check the logs
2. Review API documentation at `/docs`
3. Test health endpoint
4. Verify environment variables

## Cost Estimation

### Free Tier (Development)
- Gemini API: 1,500 requests/day (free)
- Local hosting: $0

### Production (Low Traffic)
- Gemini API: ~$0.50-2/month (pay-as-you-go)
- Cloud hosting: $5-20/month
- **Total: ~$5-25/month**

### Production (High Traffic)
- Gemini API: ~$10-50/month
- Cloud hosting: $20-100/month
- **Total: ~$30-150/month**

