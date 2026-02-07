"""API routes for wait step management.

These routes provide HTTP endpoints for creating, managing,
and monitoring wait steps in workflow executions.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db
from src.workflows.application.wait_service import (
    PendingWaitsSummary,
    WaitCreateResult,
    WaitNotFoundError,
    WaitSchedulingService,
    WaitStatus,
)
from src.workflows.domain.wait_entities import EventType, TimeUnit, WaitType

router = APIRouter(prefix="/api/v1/workflows", tags=["waits"])


@router.post(
    "/{workflow_id}/executions/{execution_id}/wait",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Create a wait step execution",
    description="Create a new wait step for a workflow execution with specified configuration.",
)
async def create_wait_step(
    workflow_id: UUID,
    execution_id: UUID,
    step_id: str,
    wait_type: WaitType,
    config: dict[str, Any],
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Create a wait step execution.

    Args:
        workflow_id: Workflow definition ID.
        execution_id: Workflow execution ID.
        step_id: Step identifier in workflow.
        wait_type: Type of wait (fixed_time, until_date, until_time, for_event).
        config: Wait configuration based on wait_type.
        db: Database session.

    Returns:
        Created wait execution information.

    Raises:
        HTTPException: If configuration is invalid or execution not found.
    """
    service = WaitSchedulingService(db)

    try:
        if wait_type == WaitType.FIXED_TIME:
            result = await service.create_fixed_time_wait(
                workflow_execution_id=execution_id,
                workflow_id=workflow_id,
                contact_id=config.get("contact_id", UUID("00000000-0000-0000-0000-000000000000")),
                account_id=config.get("account_id", UUID("00000000-0000-0000-0000-000000000000")),
                step_id=step_id,
                duration=config["duration"],
                unit=TimeUnit(config["unit"]),
                timezone=config.get("timezone", "UTC"),
            )
        elif wait_type == WaitType.UNTIL_DATE:
            result = await service.create_until_date_wait(
                workflow_execution_id=execution_id,
                workflow_id=workflow_id,
                contact_id=config.get("contact_id", UUID("00000000-0000-0000-0000-000000000000")),
                account_id=config.get("account_id", UUID("00000000-0000-0000-0000-000000000000")),
                step_id=step_id,
                target_date=datetime.fromisoformat(config["target_date"]),
                timezone=config.get("timezone", "UTC"),
            )
        elif wait_type == WaitType.UNTIL_TIME:
            result = await service.create_until_time_wait(
                workflow_execution_id=execution_id,
                workflow_id=workflow_id,
                contact_id=config.get("contact_id", UUID("00000000-0000-0000-0000-000000000000")),
                account_id=config.get("account_id", UUID("00000000-0000-0000-0000-000000000000")),
                step_id=step_id,
                target_time=config["target_time"],
                timezone=config["timezone"],
                days=config.get("days"),
            )
        elif wait_type == WaitType.FOR_EVENT:
            result = await service.create_event_wait(
                workflow_execution_id=execution_id,
                workflow_id=workflow_id,
                contact_id=config.get("contact_id", UUID("00000000-0000-0000-0000-000000000000")),
                account_id=config.get("account_id", UUID("00000000-0000-0000-0000-000000000000")),
                step_id=step_id,
                event_type=EventType(config["event_type"]),
                timeout_hours=config.get("timeout_hours", 168),
                timeout_action=config.get("timeout_action", "continue"),
                correlation_id=config.get("correlation_id"),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported wait type: {wait_type}",
            )

        return {
            "id": str(result.wait_execution.id),
            "scheduled_at": result.scheduled_at.isoformat() if result.scheduled_at else None,
            "status": result.status,
        }

    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required configuration parameter: {e}",
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid configuration value: {e}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create wait step: {e}",
        ) from e


@router.get(
    "/executions/{execution_id}/wait/{step_id}",
    response_model=dict[str, Any],
    summary="Get wait step status",
    description="Retrieve the current status of a wait step execution.",
)
async def get_wait_status(
    execution_id: UUID,
    step_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get wait step status.

    Args:
        execution_id: Workflow execution ID.
        step_id: Step identifier.
        db: Database session.

    Returns:
        Wait step status information.

    Raises:
        HTTPException: If wait execution not found.
    """
    # Note: This requires a wait_id lookup by execution_id and step_id
    # For now, returning a placeholder response
    # In production, you'd query by execution_id and step_id
    return {
        "id": str(execution_id),
        "step_id": step_id,
        "status": "waiting",
        "scheduled_at": None,
        "resumed_at": None,
        "resumed_by": None,
    }


@router.delete(
    "/executions/{execution_id}/wait/{step_id}",
    response_model=dict[str, bool],
    summary="Cancel wait step",
    description="Cancel an active wait step execution.",
)
async def cancel_wait_step(
    execution_id: UUID,
    step_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, bool]:
    """Cancel a wait step.

    Args:
        execution_id: Workflow execution ID.
        step_id: Step identifier.
        db: Database session.

    Returns:
        Success status.

    Raises:
        HTTPException: If wait execution not found.
    """
    # Note: This requires a wait_id lookup by execution_id and step_id
    # For now, returning a placeholder response
    return {"success": True}


@router.get(
    "/executions/{execution_id}/wait/{wait_id}/status",
    response_model=dict[str, Any],
    summary="Get detailed wait status",
    description="Retrieve detailed status information for a specific wait execution.",
)
async def get_wait_status_by_id(
    execution_id: UUID,
    wait_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get detailed wait status by ID.

    Args:
        execution_id: Workflow execution ID.
        wait_id: Wait execution ID.
        db: Database session.

    Returns:
        Detailed wait status information.

    Raises:
        HTTPException: If wait execution not found.
    """
    service = WaitSchedulingService(db)

    try:
        status_info = await service.get_wait_status(wait_id)

        return {
            "id": str(status_info.id),
            "status": status_info.status,
            "scheduled_at": status_info.scheduled_at.isoformat() if status_info.scheduled_at else None,
            "resumed_at": status_info.resumed_at.isoformat() if status_info.resumed_at else None,
            "resumed_by": status_info.resumed_by,
        }

    except WaitNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve wait status: {e}",
        ) from e


@router.delete(
    "/executions/{execution_id}/wait/{wait_id}",
    response_model=dict[str, bool],
    summary="Cancel wait by ID",
    description="Cancel an active wait execution by ID.",
)
async def cancel_wait_by_id(
    execution_id: UUID,
    wait_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, bool]:
    """Cancel a wait by ID.

    Args:
        execution_id: Workflow execution ID.
        wait_id: Wait execution ID.
        db: Database session.

    Returns:
        Success status.

    Raises:
        HTTPException: If wait execution not found.
    """
    service = WaitSchedulingService(db)

    try:
        success = await service.cancel_wait(wait_id)
        return {"success": success}

    except WaitNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel wait: {e}",
        ) from e


@router.get(
    "/admin/waits/pending",
    response_model=dict[str, Any],
    summary="List pending waits",
    description="Retrieve a list of pending wait executions (admin endpoint).",
)
async def list_pending_waits(
    wait_type: WaitType | None = None,
    workflow_id: UUID | None = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List pending wait executions.

    Args:
        wait_type: Optional filter by wait type.
        workflow_id: Optional filter by workflow.
        limit: Maximum number of results.
        offset: Number of results to skip.
        db: Database session.

    Returns:
        List of pending wait executions.
    """
    # Note: This is a placeholder implementation
    # In production, you'd query the database with filters
    return {
        "items": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
    }


@router.post(
    "/tasks/wait/{wait_id}/resume",
    response_model=dict[str, bool],
    summary="Resume wait (internal)",
    description="Internal endpoint for resuming a wait execution (called by scheduler).",
)
async def resume_wait_execution(
    wait_id: UUID,
    resumed_by: str = "scheduler",
    db: AsyncSession = Depends(get_db),
) -> dict[str, bool]:
    """Resume a wait execution (internal endpoint).

    This endpoint is called by the background job scheduler when
    a wait period expires or an event is received.

    Args:
        wait_id: Wait execution ID.
        resumed_by: What triggered resumption (default: scheduler).
        db: Database session.

    Returns:
        Success status.

    Raises:
        HTTPException: If wait execution not found or cannot be resumed.
    """
    service = WaitSchedulingService(db)

    try:
        await service.resume_wait(wait_id, resumed_by)
        return {"success": True}

    except WaitNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resume wait: {e}",
        ) from e
