"""API routes for workflow action management.

This module defines the FastAPI routes for workflow action CRUD operations.
All routes require authentication and enforce account isolation.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import AuthenticatedUser
from src.workflows.application.action_dtos import (
    ActionResponse,
    CreateActionRequest,
    ErrorResponse,
    ListActionsResponse,
    ReorderActionsRequest,
    UpdateActionRequest,
)
from src.workflows.application.use_cases.manage_actions import (
    DeleteActionResult,
    UpdateActionResult,
)
from src.workflows.domain.action_exceptions import (
    ActionDependencyCycleError,
    ActionExecutionError,
    ActionNotFoundError,
    ActionPositionConflictError,
    MaximumActionsExceededError,
    WorkflowMustBeInDraftError,
)
from src.workflows.domain.action_value_objects import ActionType
from src.workflows.infrastructure.rate_limiter import rate_limit_default


router = APIRouter(
    prefix="/workflows/{workflow_id}/actions",
    tags=["workflow-actions"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)


async def get_action_use_cases(
    request: Request,
    session: AsyncSession,
):
    """Dependency to get action use case instances.

    Args:
        request: FastAPI request.
        session: Database session.

    Returns:
        Tuple of action use cases.
    """
    from src.workflows.application.use_cases.manage_actions import (
        AddActionUseCase,
        DeleteActionUseCase,
        ListActionsUseCase,
        ReorderActionsUseCase,
        UpdateActionUseCase,
    )
    from src.workflows.infrastructure.action_repository import ActionRepository
    from src.workflows.infrastructure.repositories import WorkflowRepository

    # Initialize repositories
    action_repository = ActionRepository(session)
    workflow_repository = WorkflowRepository(session)

    # Initialize use cases
    add_action_use_case = AddActionUseCase(action_repository, workflow_repository)
    update_action_use_case = UpdateActionUseCase(action_repository, workflow_repository)
    delete_action_use_case = DeleteActionUseCase(action_repository, workflow_repository)
    list_actions_use_case = ListActionsUseCase(action_repository)
    reorder_actions_use_case = ReorderActionsUseCase(action_repository, workflow_repository)

    return {
        "add": add_action_use_case,
        "update": update_action_use_case,
        "delete": delete_action_use_case,
        "list": list_actions_use_case,
        "reorder": reorder_actions_use_case,
    }


@router.post(
    "",
    response_model=ActionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add action to workflow",
    description="Add a new action step to a workflow. Workflow must be in draft or paused status.",
    responses={
        201: {"description": "Action created successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request data"},
        404: {"model": ErrorResponse, "description": "Workflow not found"},
        409: {"model": ErrorResponse, "description": "Workflow status conflict or position conflict"},
    },
)
async def add_action(
    workflow_id: str,
    request: Request,
    body: CreateActionRequest,
    user: AuthenticatedUser,
    session: Annotated[AsyncSession, Depends(get_db)],
    _rate_limit: Annotated[None, Depends(rate_limit_default)] = None,
) -> ActionResponse:
    """Add a new action to a workflow.

    Args:
        workflow_id: The workflow ID.
        request: FastAPI request object.
        body: Action creation data.
        user: Authenticated user.
        session: Database session.

    Returns:
        The created action.

    Raises:
        HTTPException: If validation fails or workflow not found.
    """
    try:
        from uuid import UUID

        use_cases = await get_action_use_cases(request, session)

        result = await use_cases["add"].execute(
            request=body,
            workflow_id=UUID(workflow_id),
            account_id=user.account_id,
            user_id=user.user_id,
        )

        await session.commit()

        if not result.success or result.action is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "action_creation_failed",
                    "message": result.error or "Failed to create action",
                },
            )

        return result.action

    except WorkflowMustBeInDraftError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "workflow_status_invalid",
                "message": str(e),
            },
        ) from e
    except MaximumActionsExceededError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "maximum_actions_exceeded",
                "message": str(e),
            },
        ) from e
    except ActionPositionConflictError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "position_conflict",
                "message": str(e),
            },
        ) from e
    except ValueError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_action_type",
                "message": f"Invalid action type: {str(e)}",
            },
        ) from e
    except Exception:
        await session.rollback()
        raise


@router.get(
    "",
    response_model=ListActionsResponse,
    summary="List workflow actions",
    description="List all actions for a workflow, optionally including disabled actions.",
)
async def list_actions(
    workflow_id: str,
    request: Request,
    user: AuthenticatedUser,
    session: Annotated[AsyncSession, Depends(get_db)],
    include_disabled: Annotated[
        bool,
        Query(
            description="Include disabled actions in the list",
        ),
    ] = False,
    _rate_limit: Annotated[None, Depends(rate_limit_default)] = None,
) -> ListActionsResponse:
    """List actions for a workflow.

    Args:
        workflow_id: The workflow ID.
        request: FastAPI request object.
        user: Authenticated user.
        session: Database session.
        include_disabled: Whether to include disabled actions.

    Returns:
        List of actions.
    """
    from uuid import UUID

    use_cases = await get_action_use_cases(request, session)

    result = await use_cases["list"].execute(
        workflow_id=UUID(workflow_id),
        account_id=user.account_id,
        include_disabled=include_disabled,
    )

    return result


@router.get(
    "/{action_id}",
    response_model=ActionResponse,
    summary="Get action by ID",
    description="Retrieve a single action by its ID.",
    responses={
        404: {"model": ErrorResponse, "description": "Action not found"},
    },
)
async def get_action(
    workflow_id: str,
    action_id: str,
    request: Request,
    user: AuthenticatedUser,
    session: Annotated[AsyncSession, Depends(get_db)],
    _rate_limit: Annotated[None, Depends(rate_limit_default)] = None,
) -> ActionResponse:
    """Get an action by ID.

    Args:
        workflow_id: The workflow ID.
        action_id: The action ID.
        request: FastAPI request object.
        user: Authenticated user.
        session: Database session.

    Returns:
        The action if found.

    Raises:
        HTTPException: If action not found.
    """
    from uuid import UUID

    use_cases = await get_action_use_cases(request, session)

    # Get all actions and filter
    result = await use_cases["list"].execute(
        workflow_id=UUID(workflow_id),
        account_id=user.account_id,
        include_disabled=True,
    )

    action = next((a for a in result.items if str(a.id) == action_id), None)

    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "action_not_found",
                "message": f"Action with ID '{action_id}' not found",
            },
        )

    return action


@router.put(
    "/{action_id}",
    response_model=ActionResponse,
    summary="Update action",
    description="Update an existing action. Workflow must be in draft or paused status.",
    responses={
        404: {"model": ErrorResponse, "description": "Action not found"},
        409: {"model": ErrorResponse, "description": "Workflow status conflict"},
    },
)
async def update_action(
    workflow_id: str,
    action_id: str,
    request: Request,
    body: UpdateActionRequest,
    user: AuthenticatedUser,
    session: Annotated[AsyncSession, Depends(get_db)],
    _rate_limit: Annotated[None, Depends(rate_limit_default)] = None,
) -> ActionResponse:
    """Update an action.

    Args:
        workflow_id: The workflow ID.
        action_id: The action ID.
        request: FastAPI request object.
        body: Update data.
        user: Authenticated user.
        session: Database session.

    Returns:
        The updated action.

    Raises:
        HTTPException: If action not found or workflow status conflict.
    """
    try:
        from uuid import UUID

        use_cases = await get_action_use_cases(request, session)

        result = await use_cases["update"].execute(
            action_id=UUID(action_id),
            workflow_id=UUID(workflow_id),
            account_id=user.account_id,
            user_id=user.user_id,
            action_config=body.action_config,
            is_enabled=body.is_enabled,
            position=body.position,
        )

        await session.commit()

        if not result.success or result.action is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "action_not_found",
                    "message": result.error or "Action not found",
                },
            )

        return result.action

    except WorkflowMustBeInDraftError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "workflow_status_invalid",
                "message": str(e),
            },
        ) from e
    except Exception:
        await session.rollback()
        raise


@router.delete(
    "/{action_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete action",
    description="Delete an action from a workflow. Workflow must be in draft or paused status.",
    responses={
        404: {"model": ErrorResponse, "description": "Action not found"},
        409: {"model": ErrorResponse, "description": "Workflow status conflict"},
    },
)
async def delete_action(
    workflow_id: str,
    action_id: str,
    request: Request,
    user: AuthenticatedUser,
    session: Annotated[AsyncSession, Depends(get_db)],
    _rate_limit: Annotated[None, Depends(rate_limit_default)] = None,
) -> None:
    """Delete an action.

    Args:
        workflow_id: The workflow ID.
        action_id: The action ID.
        request: FastAPI request object.
        user: Authenticated user.
        session: Database session.

    Raises:
        HTTPException: If action not found or workflow status conflict.
    """
    try:
        from uuid import UUID

        use_cases = await get_action_use_cases(request, session)

        result = await use_cases["delete"].execute(
            action_id=UUID(action_id),
            workflow_id=UUID(workflow_id),
            account_id=user.account_id,
            user_id=user.user_id,
        )

        await session.commit()

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "action_not_found",
                    "message": result.error or "Action not found",
                },
            )

    except WorkflowMustBeInDraftError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "workflow_status_invalid",
                "message": str(e),
            },
        ) from e
    except Exception:
        await session.rollback()
        raise


@router.post(
    "/reorder",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Reorder actions",
    description="Reorder actions in a workflow. Workflow must be in draft or paused status.",
    responses={
        409: {"model": ErrorResponse, "description": "Workflow status conflict"},
    },
)
async def reorder_actions(
    workflow_id: str,
    request: Request,
    body: ReorderActionsRequest,
    user: AuthenticatedUser,
    session: Annotated[AsyncSession, Depends(get_db)],
    _rate_limit: Annotated[None, Depends(rate_limit_default)] = None,
) -> None:
    """Reorder actions in a workflow.

    Args:
        workflow_id: The workflow ID.
        request: FastAPI request object.
        body: Reorder request with action positions.
        user: Authenticated user.
        session: Database session.

    Raises:
        HTTPException: If workflow status conflict.
    """
    try:
        from uuid import UUID

        use_cases = await get_action_use_cases(request, session)

        await use_cases["reorder"].execute(
            request=body,
            workflow_id=UUID(workflow_id),
            account_id=user.account_id,
            user_id=user.user_id,
        )

        await session.commit()

    except ActionNotFoundError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "workflow_not_found",
                "message": str(e),
            },
        ) from e
    except WorkflowMustBeInDraftError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "workflow_status_invalid",
                "message": str(e),
            },
        ) from e
    except Exception:
        await session.rollback()
        raise
