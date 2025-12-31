#!/bin/bash

# Veritas-AI Deployment Script
# This script helps deploy the backend to various platforms

set -e

echo "🚀 Veritas-AI Deployment Script"
echo "================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please update it with your API keys."
    else
        echo "❌ Error: .env.example not found. Cannot proceed."
        exit 1
    fi
fi

# Function to deploy locally
deploy_local() {
    echo "📦 Deploying locally..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate || source venv/Scripts/activate
    
    # Install dependencies
    echo "Installing dependencies..."
    pip install -r requirements.txt
    
    # Run server
    echo "Starting server..."
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
}

# Function to deploy with Docker
deploy_docker() {
    echo "🐳 Deploying with Docker..."
    
    # Build Docker image
    docker build -t veritas-ai-backend .
    
    # Run container
    docker-compose up -d
    
    echo "✅ Backend deployed! Access at http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
}

# Function to deploy to production
deploy_production() {
    echo "☁️  Production deployment guide:"
    echo ""
    echo "Option 1: Google Cloud Run"
    echo "  1. gcloud builds submit --tag gcr.io/YOUR_PROJECT/veritas-ai"
    echo "  2. gcloud run deploy veritas-ai --image gcr.io/YOUR_PROJECT/veritas-ai --platform managed"
    echo ""
    echo "Option 2: AWS Elastic Beanstalk"
    echo "  1. eb init"
    echo "  2. eb create veritas-ai-env"
    echo "  3. eb deploy"
    echo ""
    echo "Option 3: Heroku"
    echo "  1. heroku create veritas-ai"
    echo "  2. heroku config:set GEMINI_API_KEY=your_key"
    echo "  3. git push heroku main"
    echo ""
    echo "Option 4: DigitalOcean App Platform"
    echo "  1. Create app from Dockerfile"
    echo "  2. Set environment variables"
    echo "  3. Deploy"
}

# Main menu
case "$1" in
    local)
        deploy_local
        ;;
    docker)
        deploy_docker
        ;;
    production)
        deploy_production
        ;;
    *)
        echo "Usage: $0 {local|docker|production}"
        echo ""
        echo "  local      - Run locally with Python"
        echo "  docker     - Deploy with Docker"
        echo "  production - Show production deployment guide"
        exit 1
        ;;
esac

