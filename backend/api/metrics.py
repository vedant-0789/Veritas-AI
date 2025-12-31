"""
Metrics and monitoring endpoints for Veritas-AI
"""

from fastapi import APIRouter
from typing import Dict
from datetime import datetime, timedelta
from collections import defaultdict
import time

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

# In-memory metrics storage (use Redis/database in production)
metrics_store = {
    "total_requests": 0,
    "successful_analyses": 0,
    "failed_analyses": 0,
    "average_processing_time": 0.0,
    "verdict_counts": defaultdict(int),
    "requests_by_hour": defaultdict(int),
    "last_reset": datetime.now()
}


def record_analysis(verdict: str, processing_time: float, success: bool = True):
    """Record analysis metrics"""
    metrics_store["total_requests"] += 1
    
    if success:
        metrics_store["successful_analyses"] += 1
        metrics_store["verdict_counts"][verdict] += 1
        
        # Update average processing time
        current_avg = metrics_store["average_processing_time"]
        total_successful = metrics_store["successful_analyses"]
        metrics_store["average_processing_time"] = (
            (current_avg * (total_successful - 1) + processing_time) / total_successful
        )
    else:
        metrics_store["failed_analyses"] += 1
    
    # Record by hour
    hour = datetime.now().replace(minute=0, second=0, microsecond=0)
    metrics_store["requests_by_hour"][hour.isoformat()] += 1


@router.get("/stats")
async def get_stats() -> Dict:
    """Get current statistics"""
    total = metrics_store["total_requests"]
    successful = metrics_store["successful_analyses"]
    failed = metrics_store["failed_analyses"]
    
    success_rate = (successful / total * 100) if total > 0 else 0
    
    return {
        "total_requests": total,
        "successful_analyses": successful,
        "failed_analyses": failed,
        "success_rate": round(success_rate, 2),
        "average_processing_time": round(metrics_store["average_processing_time"], 2),
        "verdict_distribution": dict(metrics_store["verdict_counts"]),
        "uptime_hours": (datetime.now() - metrics_store["last_reset"]).total_seconds() / 3600
    }


@router.get("/health-detailed")
async def get_detailed_health() -> Dict:
    """Get detailed health information"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "total_requests": metrics_store["total_requests"],
            "success_rate": round(
                (metrics_store["successful_analyses"] / metrics_store["total_requests"] * 100)
                if metrics_store["total_requests"] > 0 else 0,
                2
            ),
            "average_processing_time": round(metrics_store["average_processing_time"], 2)
        },
        "system": {
            "uptime": str(datetime.now() - metrics_store["last_reset"])
        }
    }


@router.post("/reset")
async def reset_metrics() -> Dict:
    """Reset metrics (admin only - add auth in production)"""
    global metrics_store
    metrics_store = {
        "total_requests": 0,
        "successful_analyses": 0,
        "failed_analyses": 0,
        "average_processing_time": 0.0,
        "verdict_counts": defaultdict(int),
        "requests_by_hour": defaultdict(int),
        "last_reset": datetime.now()
    }
    return {"message": "Metrics reset successfully"}

