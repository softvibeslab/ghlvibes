"""
Health Check Endpoints

Provides health check endpoints for monitoring and load balancer checks.
"""

from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model."""

    status: Literal["healthy", "unhealthy"] = Field(
        ...,
        description="Overall health status",
    )
    database: Literal["connected", "disconnected"] = Field(
        ...,
        description="Database connection status",
    )
    redis: Literal["connected", "disconnected"] = Field(
        ...,
        description="Redis connection status",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Health check timestamp",
    )


async def check_database(db: AsyncSession) -> bool:
    """Check if database is accessible.

    Args:
        db: Database session

    Returns:
        True if database is accessible, False otherwise
    """
    try:
        await db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def check_redis() -> bool:
    """Check if Redis is accessible.

    Returns:
        True if Redis is accessible, False otherwise
    """
    try:
        from src.config import settings

        # Import redis here to avoid import errors if not configured
        import redis.asyncio as redis

        client = redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        await client.ping()
        await client.close()
        return True
    except Exception:
        return False


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
    description="Check the health of the API and its dependencies",
)
async def health_check(
    db: AsyncSession = Depends(get_db),
) -> HealthResponse:
    """Check the health of the API and its dependencies.

    This endpoint is used by load balancers and monitoring systems to verify
    that the API is running and all dependencies are accessible.

    Returns:
        HealthResponse: Health status including database and Redis status
    """
    # Check database connection
    db_status = await check_database(db)
    database_status: Literal["connected", "disconnected"] = (
        "connected" if db_status else "disconnected"
    )

    # Check Redis connection
    redis_status = await check_redis()
    redis_status_value: Literal["connected", "disconnected"] = (
        "connected" if redis_status else "disconnected"
    )

    # Determine overall health
    overall_status: Literal["healthy", "unhealthy"] = (
        "healthy" if db_status and redis_status else "unhealthy"
    )

    return HealthResponse(
        status=overall_status,
        database=database_status,
        redis=redis_status_value,
    )


@router.get(
    "/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
    description="Check if the API is running (Kubernetes liveness probe)",
)
async def liveness() -> dict[str, str]:
    """Liveness probe endpoint.

    This endpoint returns 200 if the API is running, regardless of
    dependency health. Used by Kubernetes liveness probes.

    Returns:
        dict with status
    """
    return {"status": "alive"}


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness probe",
    description="Check if the API is ready to serve traffic",
)
async def readiness(
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Readiness probe endpoint.

    This endpoint checks if the API is ready to serve traffic by verifying
    all dependencies are accessible. Used by Kubernetes readiness probes.

    Returns:
        dict with status
    """
    db_healthy = await check_database(db)
    redis_healthy = await check_redis()

    if db_healthy and redis_healthy:
        return {"status": "ready"}

    return {"status": "not_ready"}
