"""API routes for workflow execution management.

This module provides FastAPI routes for executing workflows and
managing execution instances.
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.workflows.application.use_cases.execute_workflow import (
    CancelExecutionUseCase,
    ExecuteWorkflowUseCase,
    GetExecutionStatusUseCase,
    RetryExecutionUseCase,
)
from src.workflows.domain.execution_entities import WorkflowExecution
from src.workflows.domain.execution_exceptions import (
    ConcurrentExecutionLimitError,
    ContactOptedOutError,
    ExecutionNotFoundError,
    InvalidExecutionStatusTransitionError,
    WorkflowExecutionError,
    WorkflowNotActiveError,
)
from src.workflows.infrastructure.execution_repository import ExecutionRepository

router = APIRouter(prefix="/api/v1/executions", tags=["executions"])


@router.post("/{execution_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_execution(
    execution_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Cancel a workflow execution.

    Args:
        execution_id: Execution ID to cancel.
        session: Database session.

    Returns:
        Updated execution details.

    Raises:
        HTTPException: If execution not found or cannot be cancelled.
    """
    repository = ExecutionRepository(session)
    use_case = CancelExecutionUseCase()

    # Get execution
    execution = await repository.get(execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution not found: {execution_id}",
        )

    try:
        # Cancel execution
        updated_execution = await use_case.cancel(execution)
        await repository.update(updated_execution)
        await session.commit()

        return {
            "id": str(updated_execution.id),
            "status": updated_execution.status.value,
            "message": "Execution cancelled successfully",
        }

    except InvalidExecutionStatusTransitionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{execution_id}/retry", status_code=status.HTTP_200_OK)
async def retry_execution(
    execution_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Retry a failed workflow execution.

    Args:
        execution_id: Execution ID to retry.
        session: Database session.

    Returns:
        Updated execution details.

    Raises:
        HTTPException: If execution not found or cannot be retried.
    """
    repository = ExecutionRepository(session)
    use_case = RetryExecutionUseCase()

    # Get execution
    execution = await repository.get(execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution not found: {execution_id}",
        )

    try:
        # Retry execution
        updated_execution = await use_case.retry(execution)
        await repository.update(updated_execution)
        await session.commit()

        return {
            "id": str(updated_execution.id),
            "status": updated_execution.status.value,
            "retry_count": updated_execution.retry_count,
            "message": "Execution queued for retry",
        }

    except WorkflowExecutionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{execution_id}", status_code=status.HTTP_200_OK)
async def get_execution(
    execution_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get execution status and details.

    Args:
        execution_id: Execution ID.
        session: Database session.

    Returns:
        Execution details.

    Raises:
        HTTPException: If execution not found.
    """
    repository = ExecutionRepository(session)
    use_case = GetExecutionStatusUseCase()

    # Get execution
    execution = await repository.get(execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution not found: {execution_id}",
        )

    return await use_case.get_status(execution)


@router.get("/{execution_id}/logs", status_code=status.HTTP_200_OK)
async def get_execution_logs(
    execution_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Get execution logs.

    Args:
        execution_id: Execution ID.
        session: Database session.

    Returns:
        List of execution logs.

    Raises:
        HTTPException: If execution not found.
    """
    repository = ExecutionRepository(session)

    # Verify execution exists
    execution = await repository.get(execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution not found: {execution_id}",
        )

    # Get logs
    logs = await repository.list_logs_by_execution(execution_id)

    return [log.to_dict() for log in logs]


@router.post("/workflows/{workflow_id}/execute", status_code=status.HTTP_201_CREATED)
async def trigger_workflow_execution(
    workflow_id: UUID,
    contact_id: UUID,
    session: AsyncSession = Depends(get_db),
    trigger_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Trigger workflow execution for a contact.

    Args:
        workflow_id: Workflow ID to execute.
        contact_id: Contact to process.
        session: Database session.
        trigger_metadata: Optional trigger event metadata.

    Returns:
        Created execution details.

    Raises:
        HTTPException: If workflow or contact not found, or execution fails.

    Note:
        This is a simplified implementation. In production, you would:
        - Fetch workflow from repository
        - Validate workflow is active
        - Fetch contact data
        - Fetch workflow actions and conditions
        - Enqueue execution job
        - Return execution ID
    """
    # This is a placeholder - real implementation would use repositories
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Use the ExecuteWorkflowUseCase directly with pre-fetched entities",
    )
