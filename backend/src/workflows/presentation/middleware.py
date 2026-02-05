"""Middleware for workflow API.

This module provides middleware for rate limiting, request logging,
and other cross-cutting concerns.
"""

import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.config import settings


class RateLimitHeaderMiddleware(BaseHTTPMiddleware):
    """Middleware to add rate limit headers to responses.

    This middleware adds standard rate limit headers to all responses
    based on values set by the rate limiting dependency.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add rate limit headers.

        Args:
            request: Incoming request.
            call_next: Next middleware/handler.

        Returns:
            Response with rate limit headers.
        """
        response = await call_next(request)

        # Add rate limit headers if set by dependency
        if hasattr(request.state, "rate_limit_remaining"):
            response.headers["X-RateLimit-Remaining"] = str(
                request.state.rate_limit_remaining
            )
        if hasattr(request.state, "rate_limit_reset"):
            response.headers["X-RateLimit-Reset"] = str(request.state.rate_limit_reset)
        if hasattr(request.state, "rate_limit_limit"):
            response.headers["X-RateLimit-Limit"] = str(request.state.rate_limit_limit)

        return response


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Middleware to add request timing headers.

    Adds X-Response-Time header with request duration in milliseconds.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Time the request and add header.

        Args:
            request: Incoming request.
            call_next: Next middleware/handler.

        Returns:
            Response with timing header.
        """
        start_time = time.perf_counter()
        response = await call_next(request)
        duration = (time.perf_counter() - start_time) * 1000

        response.headers["X-Response-Time"] = f"{duration:.2f}ms"
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for consistent error handling.

    Catches unhandled exceptions and returns consistent error responses.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle request with error catching.

        Args:
            request: Incoming request.
            call_next: Next middleware/handler.

        Returns:
            Response or error response.
        """
        try:
            return await call_next(request)
        except Exception as e:
            # Log the error (in production, use proper logging)
            if settings.debug:
                import traceback

                traceback.print_exc()

            return JSONResponse(
                status_code=500,
                content={
                    "error": "internal_server_error",
                    "message": "An unexpected error occurred",
                    "details": str(e) if settings.debug else None,
                },
            )


def setup_middleware(app: FastAPI) -> None:
    """Configure all middleware for the application.

    Args:
        app: FastAPI application instance.
    """
    # Add middleware in order (last added is first executed)
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(RequestTimingMiddleware)
    app.add_middleware(RateLimitHeaderMiddleware)
