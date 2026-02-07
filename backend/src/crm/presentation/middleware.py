"""Middleware for CRM module."""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class CRMLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging CRM API requests."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and log CRM-specific metrics."""
        # Add CRM-specific headers
        response = await call_next(request)
        response.headers["X-CRM-API-Version"] = "1.0.0"
        return response
