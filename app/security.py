"""Security middleware for ContractML."""

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import asyncio
from collections import defaultdict, deque
from typing import Dict, Optional
import hashlib
import secrets

from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""

    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients: Dict[str, deque] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)
        current_time = time.time()

        # Clean old entries
        cutoff = current_time - self.period
        while self.clients[client_ip] and self.clients[client_ip][0] < cutoff:
            self.clients[client_ip].popleft()

        # Check rate limit
        if len(self.clients[client_ip]) >= self.calls:
            logger.warning("Rate limit exceeded", client_ip=client_ip)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )

        # Add current request
        self.clients[client_ip].append(current_time)

        response = await call_next(request)
        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP from request."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


class APIKeyMiddleware(BaseHTTPMiddleware):
    """API key authentication middleware."""

    def __init__(self, app, api_keys: Optional[list] = None):
        super().__init__(app)
        self.api_keys = set(api_keys or [])

    async def dispatch(self, request: Request, call_next):
        # Skip auth for health and metrics endpoints
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)

        # Skip if no API keys configured
        if not self.api_keys:
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key not in self.api_keys:
            logger.warning("Invalid API key", path=request.url.path)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key",
            )

        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response


def generate_api_key() -> str:
    """Generate a secure API key."""
    return f"cm_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()
