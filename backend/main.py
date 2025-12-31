"""
Veritas-AI Backend - Main FastAPI Application
Deepfake Detection API with Bio-Guard (rPPG) and Physics-Guard (Gemini AI)
"""

import os
import base64
import uuid
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our detection modules
from modules.rppg import RPPGAnalyzer
from modules.gemini_analyzer import GeminiAnalyzer
from modules.ensemble import EnsembleDecision

# Initialize FastAPI app
app = FastAPI(
    title="Veritas-AI API",
    description="Deepfake Detection API using Bio-Guard (rPPG) and Physics-Guard (Gemini AI)",
    version="1.0.0-mvp"
)

# Configure CORS for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzers
rppg_analyzer = RPPGAnalyzer()
gemini_analyzer = GeminiAnalyzer()
ensemble = EnsembleDecision()

# Store for async task results (in-memory for MVP)
task_results = {}


# ================== Request/Response Models ==================

class FrameData(BaseModel):
    """Single video frame as base64"""
    data: str = Field(..., description="Base64 encoded image frame")
    timestamp: Optional[float] = Field(None, description="Frame timestamp in seconds")


class AnalyzeRequest(BaseModel):
    """Request model for video analysis"""
    frames: List[FrameData] = Field(..., description="List of video frames to analyze")
    video_url: Optional[str] = Field(None, description="Source video URL (for reference)")
    consent_given: bool = Field(True, description="User consent for biometric analysis")


class AnalysisResult(BaseModel):
    """Response model for analysis results"""
    task_id: str
    status: str  # "pending", "processing", "completed", "error"
    verdict: Optional[str] = None  # "LIKELY_REAL", "LIKELY_FAKE", "UNCERTAIN"
    confidence: Optional[float] = None
    bio_guard: Optional[dict] = None
    physics_guard: Optional[dict] = None
    evidence: Optional[List[str]] = None
    processing_time: Optional[float] = None
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    modules: dict


# ================== API Endpoints ==================

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0-mvp",
        modules={
            "rppg": "active",
            "gemini": "active" if os.getenv("GEMINI_API_KEY") else "no_api_key",
            "ensemble": "active"
        }
    )


@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze_video(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Analyze video frames for deepfake detection.
    Returns immediately with task_id, processing happens in background.
    """
    if not request.consent_given:
        raise HTTPException(status_code=400, detail="Biometric consent required")
    
    if not request.frames or len(request.frames) < 5:
        raise HTTPException(status_code=400, detail="Minimum 5 frames required for analysis")
    
    if len(request.frames) > 60:
        raise HTTPException(status_code=400, detail="Maximum 60 frames allowed per request")
    
    # Generate task ID
    task_id = str(uuid.uuid4())[:8]
    
    # Initialize task
    task_results[task_id] = {
        "status": "processing",
        "timestamp": datetime.now().isoformat()
    }
    
    # Start background processing
    background_tasks.add_task(process_analysis, task_id, request)
    
    return AnalysisResult(
        task_id=task_id,
        status="processing",
        timestamp=datetime.now().isoformat()
    )


@app.get("/api/status/{task_id}", response_model=AnalysisResult)
async def get_analysis_status(task_id: str):
    """Get the status/result of an analysis task"""
    if task_id not in task_results:
        raise HTTPException(status_code=404, detail="Task not found")
    
    result = task_results[task_id]
    
    return AnalysisResult(
        task_id=task_id,
        status=result.get("status", "unknown"),
        verdict=result.get("verdict"),
        confidence=result.get("confidence"),
        bio_guard=result.get("bio_guard"),
        physics_guard=result.get("physics_guard"),
        evidence=result.get("evidence"),
        processing_time=result.get("processing_time"),
        timestamp=result.get("timestamp", datetime.now().isoformat())
    )


@app.post("/api/analyze-sync", response_model=AnalysisResult)
async def analyze_video_sync(request: AnalyzeRequest):
    """
    Synchronous analysis - waits for result before responding.
    Use for smaller frame sets or when immediate results needed.
    """
    if not request.consent_given:
        raise HTTPException(status_code=400, detail="Biometric consent required")
    
    if not request.frames or len(request.frames) < 5:
        raise HTTPException(status_code=400, detail="Minimum 5 frames required for analysis")
    
    task_id = str(uuid.uuid4())[:8]
    start_time = datetime.now()
    
    try:
        # Decode frames
        decoded_frames = []
        for frame in request.frames:
            try:
                frame_bytes = base64.b64decode(frame.data)
                decoded_frames.append({
                    "data": frame_bytes,
                    "timestamp": frame.timestamp
                })
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid frame data: {str(e)}")
        
        # Run Bio-Guard (rPPG) analysis
        bio_result = rppg_analyzer.analyze(decoded_frames)
        
        # Run Physics-Guard (Gemini) analysis
        physics_result = gemini_analyzer.analyze(decoded_frames)
        
        # Ensemble decision
        final_result = ensemble.make_decision(bio_result, physics_result)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AnalysisResult(
            task_id=task_id,
            status="completed",
            verdict=final_result["verdict"],
            confidence=final_result["confidence"],
            bio_guard=bio_result,
            physics_guard=physics_result,
            evidence=final_result["evidence"],
            processing_time=processing_time,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return AnalysisResult(
            task_id=task_id,
            status="error",
            evidence=[f"Analysis failed: {str(e)}"],
            timestamp=datetime.now().isoformat()
        )


# ================== Background Processing ==================

async def process_analysis(task_id: str, request: AnalyzeRequest):
    """Background task for processing video analysis"""
    start_time = datetime.now()
    
    try:
        # Decode frames
        decoded_frames = []
        for frame in request.frames:
            try:
                frame_bytes = base64.b64decode(frame.data)
                decoded_frames.append({
                    "data": frame_bytes,
                    "timestamp": frame.timestamp
                })
            except Exception:
                continue
        
        if len(decoded_frames) < 5:
            task_results[task_id] = {
                "status": "error",
                "evidence": ["Not enough valid frames to analyze"],
                "timestamp": datetime.now().isoformat()
            }
            return
        
        # Run Bio-Guard (rPPG) analysis
        bio_result = rppg_analyzer.analyze(decoded_frames)
        
        # Run Physics-Guard (Gemini) analysis
        physics_result = gemini_analyzer.analyze(decoded_frames)
        
        # Ensemble decision
        final_result = ensemble.make_decision(bio_result, physics_result)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Store result
        task_results[task_id] = {
            "status": "completed",
            "verdict": final_result["verdict"],
            "confidence": final_result["confidence"],
            "bio_guard": bio_result,
            "physics_guard": physics_result,
            "evidence": final_result["evidence"],
            "processing_time": processing_time,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        task_results[task_id] = {
            "status": "error",
            "evidence": [f"Analysis failed: {str(e)}"],
            "timestamp": datetime.now().isoformat()
        }


# ================== Run Server ==================

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    print(f"🚀 Starting Veritas-AI Backend on {host}:{port}")
    print(f"📚 API Docs: http://localhost:{port}/docs")
    
    uvicorn.run("main:app", host=host, port=port, reload=debug)
