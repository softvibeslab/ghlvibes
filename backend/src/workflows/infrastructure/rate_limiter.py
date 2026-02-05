"""Redis-based rate limiting for workflow API.

This module provides rate limiting functionality to prevent
abuse and ensure fair usage of the API.
"""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from redis.asyncio import Redis

from src.core.config import settings


@dataclass
class RateLimitResult:
    """Result of a rate limit check.

    Attributes:
        allowed: Whether the request is allowed.
        remaining: Number of requests remaining in the window.
        reset_at: Timestamp when the limit resets.
        limit: Maximum requests allowed per window.
    """

    allowed: bool
    remaining: int
    reset_at: int
    limit: int


class RateLimiter:
    """Redis-based sliding window rate limiter.

    This implementation uses Redis sorted sets to implement
    a sliding window rate limiting algorithm.
    """

    def __init__(
        self,
        redis: Redis,
        requests_per_window: int = 100,
        window_seconds: int = 60,
    ) -> None:
        """Initialize rate limiter.

        Args:
            redis: Redis client instance.
            requests_per_window: Max requests allowed per window.
            window_seconds: Window duration in seconds.
        """
        self._redis = redis
        self._requests_per_window = requests_per_window
        self._window_seconds = window_seconds

    async def check(self, key: str) -> RateLimitResult:
        """Check if a request is allowed under the rate limit.

        Uses a sliding window algorithm implemented with Redis sorted sets.

        Args:
            key: Unique identifier for the rate limit bucket
                 (e.g., user_id or IP address).

        Returns:
            RateLimitResult with the check outcome.
        """
        import time

        now = int(time.time() * 1000)  # Current time in milliseconds
        window_start = now - (self._window_seconds * 1000)

        # Redis key for this rate limit bucket
        redis_key = f"ratelimit:{key}"

        # Use pipeline for atomic operations
        pipe = self._redis.pipeline()

        # Remove expired entries (outside the window)
        pipe.zremrangebyscore(redis_key, 0, window_start)

        # Count current requests in window
        pipe.zcard(redis_key)

        # Add current request with timestamp as score
        pipe.zadd(redis_key, {str(now): now})

        # Set expiry on the key (cleanup)
        pipe.expire(redis_key, self._window_seconds + 1)

        results = await pipe.execute()
        current_count = results[1]

        # Determine if request is allowed
        allowed = current_count < self._requests_per_window
        remaining = max(0, self._requests_per_window - current_count - 1)
        reset_at = int((now / 1000) + self._window_seconds)

        if not allowed:
            # Remove the request we just added since it's not allowed
            await self._redis.zrem(redis_key, str(now))
            remaining = 0

        return RateLimitResult(
            allowed=allowed,
            remaining=remaining,
            reset_at=reset_at,
            limit=self._requests_per_window,
        )

    async def reset(self, key: str) -> None:
        """Reset rate limit for a key.

        Args:
            key: The rate limit bucket key to reset.
        """
        redis_key = f"ratelimit:{key}"
        await self._redis.delete(redis_key)


# Redis connection singleton
_redis_client: Redis | None = None


async def get_redis() -> Redis:
    """Get or create Redis client.

    Returns:
        Redis client instance.
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def get_rate_limiter(
    redis: Annotated[Redis, Depends(get_redis)],
) -> RateLimiter:
    """Dependency to get rate limiter instance.

    Args:
        redis: Redis client from dependency injection.

    Returns:
        Configured RateLimiter instance.
    """
    return RateLimiter(
        redis=redis,
        requests_per_window=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )


class RateLimitMiddlewareDep:
    """Dependency for rate limiting requests.

    Use this as a dependency in routes to enforce rate limits.
    """

    def __init__(
        self,
        requests_per_window: int | None = None,
        window_seconds: int | None = None,
        key_prefix: str = "api",
    ) -> None:
        """Initialize rate limit middleware dependency.

        Args:
            requests_per_window: Override default requests per window.
            window_seconds: Override default window seconds.
            key_prefix: Prefix for rate limit keys.
        """
        self._requests_per_window = requests_per_window or settings.rate_limit_requests
        self._window_seconds = window_seconds or settings.rate_limit_window_seconds
        self._key_prefix = key_prefix

    async def __call__(
        self,
        request: Request,
        redis: Annotated[Redis, Depends(get_redis)],
    ) -> None:
        """Check rate limit for the request.

        Args:
            request: The incoming request.
            redis: Redis client.

        Raises:
            HTTPException: If rate limit is exceeded.
        """
        # Get client identifier (prefer authenticated user, fallback to IP)
        client_id = self._get_client_id(request)

        rate_limiter = RateLimiter(
            redis=redis,
            requests_per_window=self._requests_per_window,
            window_seconds=self._window_seconds,
        )

        key = f"{self._key_prefix}:{client_id}"
        result = await rate_limiter.check(key)

        # Set rate limit headers
        request.state.rate_limit_remaining = result.remaining
        request.state.rate_limit_reset = result.reset_at
        request.state.rate_limit_limit = result.limit

        if not result.allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "retry_after": result.reset_at,
                    "limit": result.limit,
                },
                headers={
                    "Retry-After": str(result.reset_at),
                    "X-RateLimit-Limit": str(result.limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(result.reset_at),
                },
            )

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request.

        Prioritizes authenticated user ID over IP address.

        Args:
            request: The incoming request.

        Returns:
            Client identifier string.
        """
        # Check for authenticated user in request state
        if hasattr(request.state, "user") and request.state.user:
            return f"user:{request.state.user.user_id}"

        # Fallback to IP address
        if request.client:
            return f"ip:{request.client.host}"

        # Last resort: use a hash of headers
        return f"unknown:{hash(str(request.headers))}"


# Pre-configured rate limit dependencies
rate_limit_default = RateLimitMiddlewareDep()
rate_limit_strict = RateLimitMiddlewareDep(requests_per_window=20, window_seconds=60)
rate_limit_relaxed = RateLimitMiddlewareDep(requests_per_window=200, window_seconds=60)
