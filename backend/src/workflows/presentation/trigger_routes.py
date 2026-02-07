"""API routes for trigger configuration.

This module provides FastAPI routes for configuring workflow triggers
as specified in SPEC-WFL-002.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorization

from src.workflows.application.use_cases.configure_trigger import (
    ConfigureTriggerRequest,
    ConfigureTriggerUseCase,
    DeleteTriggerUseCase,
    GetTriggerUseCase,
    TestTriggerRequest,
    TestTriggerResult,
    TriggerResponse,
    UpdateTriggerUseCase,
)
from src.workflows.infrastructure.trigger_repository import TriggerRepository
from src.workflows.presentation.dependencies import get_current_user_id

router = APIRouter(prefix="/workflows", tags=["triggers"])


@router.post(
    "/{workflow_id}/trigger",
    response_model=TriggerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Configure workflow trigger",
    description="Create or update a trigger for a workflow. Each workflow has exactly one trigger.",
)
async def configure_trigger(
    workflow_id: UUID,
    request: ConfigureTriggerRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    _authorization: Annotated[HTTPAuthorization, Depends()],
) -> TriggerResponse:
    """Configure a trigger for a workflow.

    Args:
        workflow_id: The workflow ID.
        request: Trigger configuration.
        user_id: Current user ID.
        _authorization: Authorization header.

    Returns:
        Configured trigger.

    Raises:
        HTTPException: If configuration fails.
    """
    from src.core.database import get_db_session

    async with get_db_session() as session:
        repository = TriggerRepository(session)
        use_case = ConfigureTriggerUseCase(repository)

        result = await use_case.execute(
            workflow_id=workflow_id,
            request=request,
            created_by=user_id,
        )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error,
            )

        return result.trigger


@router.get(
    "/{workflow_id}/trigger",
    response_model=TriggerResponse,
    summary="Get workflow trigger",
    description="Retrieve the trigger configuration for a workflow.",
)
async def get_trigger(
    workflow_id: UUID,
    _authorization: Annotated[HTTPAuthorization, Depends()],
) -> TriggerResponse:
    """Get workflow trigger.

    Args:
        workflow_id: The workflow ID.
        _authorization: Authorization header.

    Returns:
        Trigger configuration.

    Raises:
        HTTPException: If trigger not found.
    """
    from src.core.database import get_db_session

    async with get_db_session() as session:
        repository = TriggerRepository(session)
        use_case = GetTriggerUseCase(repository)

        trigger = await use_case.execute(workflow_id)

        if not trigger:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trigger not found",
            )

        return trigger


@router.put(
    "/{workflow_id}/trigger",
    response_model=TriggerResponse,
    summary="Update workflow trigger",
    description="Update an existing workflow trigger configuration.",
)
async def update_trigger(
    workflow_id: UUID,
    event: str | None = None,
    filters: dict[str, object] | None = None,
    settings: dict[str, object] | None = None,
    is_active: bool | None = None,
    _authorization: Annotated[HTTPAuthorization, Depends()],
) -> TriggerResponse:
    """Update workflow trigger.

    Args:
        workflow_id: The workflow ID.
        event: New trigger event.
        filters: New filter conditions.
        settings: New trigger settings.
        is_active: New active state.
        _authorization: Authorization header.

    Returns:
        Updated trigger.

    Raises:
        HTTPException: If trigger not found.
    """
    from src.core.database import get_db_session

    async with get_db_session() as session:
        repository = TriggerRepository(session)
        use_case = UpdateTriggerUseCase(repository)

        trigger = await use_case.execute(
            workflow_id=workflow_id,
            event=event,
            filters=filters,
            settings=settings,
            is_active=is_active,
        )

        if not trigger:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trigger not found",
            )

        return trigger


@router.delete(
    "/{workflow_id}/trigger",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete workflow trigger",
    description="Remove the trigger from a workflow.",
)
async def delete_trigger(
    workflow_id: UUID,
    _authorization: Annotated[HTTPAuthorization, Depends()],
) -> None:
    """Delete workflow trigger.

    Args:
        workflow_id: The workflow ID.
        _authorization: Authorization header.

    Raises:
        HTTPException: If trigger not found.
    """
    from src.core.database import get_db_session

    async with get_db_session() as session:
        repository = TriggerRepository(session)
        use_case = DeleteTriggerUseCase(repository)

        deleted = await use_case.execute(workflow_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trigger not found",
            )


@router.post(
    "/{workflow_id}/trigger/test",
    response_model=TestTriggerResult,
    summary="Test workflow trigger",
    description="Test a trigger with simulated event data without enrolling contacts.",
)
async def test_trigger(
    workflow_id: UUID,
    request: TestTriggerRequest,
    _authorization: Annotated[HTTPAuthorization, Depends()],
) -> TestTriggerResult:
    """Test workflow trigger.

    Args:
        workflow_id: The workflow ID.
        request: Test request with event data.
        _authorization: Authorization header.

    Returns:
        Test results showing if filters matched.

    Raises:
        HTTPException: If trigger not found.
    """
    from src.core.database import get_db_session

    async with get_db_session() as session:
        repository = TriggerRepository(session)
        use_case = TestTriggerUseCase(repository)

        result = await use_case.execute(
            workflow_id=workflow_id,
            request=request,
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trigger not found",
            )

        return result
