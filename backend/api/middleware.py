"""
API Middleware for Veritas-AI
Includes rate limiting, request validation, and security headers
"""

import time
from collections import defaultdict
from typing import Callable
from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from modules.logger import logger


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware
    Limits requests per IP address
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
        self.cleanup_interval = 60  # Clean up old entries every 60 seconds
        self.last_cleanup = time.time()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path == "/api/health":
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Clean up old entries periodically
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries(current_time)
            self.last_cleanup = current_time
        
        # Check rate limit
        if self._is_rate_limited(client_ip, current_time):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return Response(
                content='{"error": "Rate limit exceeded. Please try again later."}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0"
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self._get_remaining_requests(client_ip, current_time)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
    
    def _is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """Check if IP is rate limited"""
        # Remove requests older than 1 minute
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < 60
        ]
        
        # Check if limit exceeded
        return len(self.requests[client_ip]) >= self.requests_per_minute
    
    def _get_remaining_requests(self, client_ip: str, current_time: float) -> int:
        """Get remaining requests for IP"""
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < 60
        ]
        return max(0, self.requests_per_minute - len(self.requests[client_ip]))
    
    def _cleanup_old_entries(self, current_time: float):
        """Remove old entries from all IPs"""
        for ip in list(self.requests.keys()):
            self.requests[ip] = [
                req_time for req_time in self.requests[ip]
                if current_time - req_time < 60
            ]
            if not self.requests[ip]:
                del self.requests[ip]


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

