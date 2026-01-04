"""
Veritas-AI Backend - Main FastAPI Application
Deepfake Detection API with Bio-Guard (rPPG) and Physics-Guard (Gemini AI)
"""

import os
import base64
import uuid
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import logger
from modules.logger import logger

# Import our detection modules
from modules.rppg import RPPGAnalyzer
from modules.gemini_analyzer import GeminiAnalyzer
from modules.vision_analyzer import VisionAnalyzer
from modules.temporal_analyzer import TemporalAnalyzer
from modules.advanced_analyzer import AdvancedAnalyzer
from modules.ensemble import EnsembleDecision

# Import API components
from api.metrics import router as metrics_router, record_analysis
from api.middleware import RateLimitMiddleware, SecurityHeadersMiddleware

# Initialize FastAPI app
app = FastAPI(
    title="Veritas-AI API",
    description="Deepfake Detection API using Bio-Guard (rPPG), Physics-Guard (Gemini AI), and Temporal Analysis",
    version="1.1.0"
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
vision_analyzer = VisionAnalyzer()
temporal_analyzer = TemporalAnalyzer()
advanced_analyzer = AdvancedAnalyzer()
ensemble = EnsembleDecision()

# Add middleware
app.add_middleware(SecurityHeadersMiddleware)
# Rate limiting (60 requests per minute per IP)
if os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true":
    app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

# Include metrics router
app.include_router(metrics_router)

# ... (previous imports)

# Store for async task results (in-memory for MVP)
task_results = {}

def cleanup_stale_tasks():
    """Remove tasks older than 10 minutes to prevent memory leaks"""
    try:
        current_time = datetime.now()
        # Create list of keys to remove to avoid modification during iteration
        to_remove = []
        
        for tid, result in task_results.items():
            try:
                # Parse timestamp
                if "timestamp" in result:
                    task_time = datetime.fromisoformat(result["timestamp"])
                    age_seconds = (current_time - task_time).total_seconds()
                    
                    # Remove if older than 10 minutes (600 seconds)
                    if age_seconds > 600:
                        to_remove.append(tid)
            except Exception:
                # If timestamp parsing fails, mark for removal to be safe
                to_remove.append(tid)
                
        # Remove stale tasks
        for tid in to_remove:
            del task_results[tid]
            
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} stale analysis tasks")
            
    except Exception as e:
        logger.error(f"Error during task cleanup: {e}")

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
    enable_gemini: bool = Field(True, description="Enable Gemini AI analysis")
    fps: Optional[float] = Field(None, description="Frame rate of captured video")


class AnalysisResult(BaseModel):
    """Response model for analysis results"""
    task_id: str
    status: str  # "pending", "processing", "completed", "error"
    verdict: Optional[str] = None  # "LIKELY_REAL", "LIKELY_FAKE", "UNCERTAIN"
    confidence: Optional[float] = None
    bio_guard: Optional[dict] = None
    physics_guard: Optional[dict] = None
    temporal_guard: Optional[dict] = None
    advanced_guard: Optional[dict] = None
    vision_guard: Optional[dict] = None
    evidence: Optional[List[str]] = None
    processing_time: Optional[float] = None
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    modules: dict


# ================== API Endpoints ==================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else "An error occurred"
        }
    )


@app.get("/")
async def root():
    """Root endpoint for basic connectivity test"""
    return {
        "message": "Veritas-AI API is running",
        "docs_url": "/docs",
        "health_check": "/api/health"
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        return HealthResponse(
            status="healthy",
            version="1.1.0",
            modules={
                "rppg": "active",
                "gemini": "active" if os.getenv("GEMINI_API_KEY") else "no_api_key",
                "temporal": "active",
                "ensemble": "active"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")


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
    
    # Run cleanup occasionally
    if len(task_results) > 100:
        background_tasks.add_task(cleanup_stale_tasks)
    
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
        # Check if it was cleaned up
        raise HTTPException(status_code=404, detail="Task not found (may have expired)")
    
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
def analyze_video_sync(request: AnalyzeRequest):
    """
    Synchronous analysis - waits for result before responding.
    NOTE: Defined as synchronous 'def' so FastAPI runs it in a threadpool,
    preventing the event loop from being blocked by heavy computation.
    """
    logger.info(f"Analysis request received: {len(request.frames)} frames")
    
    if not request.consent_given:
        logger.warning("Analysis rejected: No biometric consent")
        raise HTTPException(status_code=400, detail="Biometric consent required")
    
    if not request.frames or len(request.frames) < 5:
        logger.warning(f"Analysis rejected: Insufficient frames ({len(request.frames) if request.frames else 0})")
        raise HTTPException(status_code=400, detail="Minimum 5 frames required for analysis")
    
    task_id = str(uuid.uuid4())[:8]
    start_time = datetime.now()
    
    try:
        logger.info(f"Starting analysis task {task_id}")
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
        bio_result = rppg_analyzer.analyze(decoded_frames, fps=request.fps)
        
        # Run Physics-Guard (Gemini) analysis
        if request.enable_gemini:
            physics_result = gemini_analyzer.analyze(decoded_frames)
        else:
            physics_result = {
                "available": False, 
                "assessment": "Skipped by user settings (Bio-Guard Only)",
                "confidence": 0.5,
                "is_suspicious": None
            }
        
        # Run Temporal analysis
        temporal_result = temporal_analyzer.analyze(decoded_frames)
        
        # Run Advanced analysis
        advanced_result = advanced_analyzer.analyze(decoded_frames)
        
        # Optional: Vision API analysis (if available)
        vision_result = vision_analyzer.analyze(decoded_frames)
        
        # Ensemble decision
        final_result = ensemble.make_decision(bio_result, physics_result, vision_result, temporal_result)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Record metrics
        record_analysis(final_result['verdict'], processing_time, success=True)
        
        logger.info(f"Analysis completed: {task_id} - Verdict: {final_result['verdict']} (Confidence: {final_result['confidence']:.2f}) in {processing_time:.2f}s")
        
        return AnalysisResult(
            task_id=task_id,
            status="completed",
            verdict=final_result["verdict"],
            confidence=final_result["confidence"],
            bio_guard=bio_result,
            physics_guard=physics_result,
            temporal_guard=temporal_result,
            advanced_guard=advanced_result,
            vision_guard=vision_result,
            evidence=final_result["evidence"],
            processing_time=processing_time,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed for task {task_id}: {str(e)}", exc_info=True)
        record_analysis("ERROR", 0, success=False)
        return AnalysisResult(
            task_id=task_id,
            status="error",
            evidence=[f"Analysis failed: {str(e)}"],
            timestamp=datetime.now().isoformat()
        )


# ================== Background Processing ==================

def process_analysis(task_id: str, request: AnalyzeRequest):
    """
    Background task for processing video analysis.
    Defined as synchronous 'def' so FastAPI runs it in a threadpool,
    avoiding event loop blocking during heavy computation.
    """
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
        bio_result = rppg_analyzer.analyze(decoded_frames, fps=request.fps)
        
        # Run Physics-Guard (Gemini) analysis
        if request.enable_gemini:
            physics_result = gemini_analyzer.analyze(decoded_frames)
        else:
            physics_result = {
                "available": False, 
                "assessment": "Skipped by user settings (Bio-Guard Only)",
                "confidence": 0.5,
                "is_suspicious": None
            }
        
        # Run Temporal analysis
        temporal_result = temporal_analyzer.analyze(decoded_frames)
        
        # Run Advanced analysis
        advanced_result = advanced_analyzer.analyze(decoded_frames)
        
        # Optional: Vision API analysis (if available)
        vision_result = vision_analyzer.analyze(decoded_frames)
        
        # Ensemble decision
        final_result = ensemble.make_decision(bio_result, physics_result, vision_result, temporal_result)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Record metrics
        record_analysis(final_result['verdict'], processing_time, success=True)
        
        # Store result
        task_results[task_id] = {
            "status": "completed",
            "verdict": final_result["verdict"],
            "confidence": final_result["confidence"],
            "bio_guard": bio_result,
            "physics_guard": physics_result,
            "temporal_guard": temporal_result,
            "advanced_guard": advanced_result,
            "vision_guard": vision_result,
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
    
    logger.info(f"Starting Veritas-AI Backend on {host}:{port}")
    logger.info(f"API Docs: http://localhost:{port}/docs")
    logger.info(f"Debug mode: {debug}")
    
    uvicorn.run("main:app", host=host, port=port, reload=debug, log_config=None)
