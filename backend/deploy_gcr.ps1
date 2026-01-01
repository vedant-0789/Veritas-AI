# Veritas-AI Google Cloud Run Deployment Script
# Run this in PowerShell

param (
    [string]$ProjectID,
    [string]$Region = "us-central1"
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Veritas-AI Cloud Run Deployment" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Check for gcloud
if (-not (Get-Command "gcloud" -ErrorAction SilentlyContinue)) {
    Write-Error "❌ 'gcloud' CLI is not installed. Please install the Google Cloud SDK first."
    exit 1
}

# Check for Project ID
if (-z $ProjectID) {
    # Try to get from config
    $ProjectID = gcloud config get-value project 2>$null
    if (-z $ProjectID -or $ProjectID -eq "(unset)") {
        $ProjectID = Read-Host "Please enter your Google Cloud Project ID"
    } else {
        Write-Host "Using current project: $ProjectID" -ForegroundColor Gray
    }
}

if (-z $ProjectID) {
    Write-Error "❌ No Project ID provided."
    exit 1
}

# 1. Enable APIs
Write-Host "`n📦 Enabling necessary APIs (Cloud Build, Cloud Run)..." -ForegroundColor Yellow
gcloud services enable cloudbuild.googleapis.com run.googleapis.com --project $ProjectID

# 2. Submit Build
Write-Host "`n🏗️  Building Container Image (this may take a few minutes)..." -ForegroundColor Yellow
$ImageName = "gcr.io/$ProjectID/veritas-ai-backend"
gcloud builds submit --tag $ImageName . --project $ProjectID

# 3. Deploy
Write-Host "`n🚀 Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy veritas-ai-backend `
    --image $ImageName `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --memory 2Gi `
    --cpu 2 `
    --project $ProjectID

# 4. Success
Write-Host "`n✅ Deployment Complete!" -ForegroundColor Green
Write-Host "You should see the Service URL above." -ForegroundColor Cyan
