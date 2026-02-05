"""API routes for the workflow module.

This module defines the FastAPI routes for workflow CRUD operations.
All routes require authentication and enforce account isolation.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import AuthenticatedUser
from src.workflows.application.dtos import (
    CreateWorkflowRequest,
    ErrorResponse,
    PaginatedWorkflowResponse,
    UpdateWorkflowRequest,
    WorkflowResponse,
)
from src.workflows.domain.exceptions import (
    InvalidWorkflowNameError,
    WorkflowAlreadyExistsError,
    WorkflowDomainError,
    WorkflowNotFoundError,
)
from src.workflows.infrastructure.rate_limiter import rate_limit_default
from src.workflows.presentation.dependencies import (
    CreateWorkflowUseCaseDep,
    DeleteWorkflowUseCaseDep,
    GetWorkflowUseCaseDep,
    ListWorkflowsUseCaseDep,
    UpdateWorkflowUseCaseDep,
)


router = APIRouter(
    prefix="/workflows",
    tags=["workflows"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)


@router.post(
    "",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new workflow",
    description="Create a new automation workflow in draft status.",
    responses={
        201: {"description": "Workflow created successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request data"},
        409: {"model": ErrorResponse, "description": "Workflow name already exists"},
    },
)
async def create_workflow(
    request: Request,
    body: CreateWorkflowRequest,
    user: AuthenticatedUser,
    use_case: CreateWorkflowUseCaseDep,
    session: Annotated[AsyncSession, Depends(get_db)],
    _rate_limit: Annotated[None, Depends(rate_limit_default)] = None,
) -> WorkflowResponse:
    """Create a new workflow.

    Creates a new workflow in draft status. The workflow name must be
    unique within the account.

    Args:
        request: FastAPI request object.
        body: Workflow creation data.
        user: Authenticated user.
        use_case: Create workflow use case.
        session: Database session.

    Returns:
        The created workflow.

    Raises:
        HTTPException: If validation fails or name already exists.
    """
    try:
        # Get client info for audit
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        result = await use_case.execute(
            request=body,
            account_id=user.account_id,
            user_id=user.user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Commit the transaction
        await session.commit()

        if result.workflow is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create workflow",
            )

        return result.workflow

    except WorkflowAlreadyExistsError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "duplicate_workflow",
                "message": str(e),
            },
        ) from e
    except InvalidWorkflowNameError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_name",
                "message": str(e),
            },
        ) from e
    except WorkflowDomainError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "domain_error",
                "message": str(e),
            },
        ) from e
    except Exception:
        await session.rollback()
        raise


@router.get(
    "",
    response_model=PaginatedWorkflowResponse,
    summary="List workflows",
    description="List all workflows for the authenticated account with optional filtering.",
)
async def list_workflows(
    user: AuthenticatedUser,
    use_case: ListWorkflowsUseCaseDep,
    status_filter: Annotated[
        str | None,
        Query(
            alias="status",
            description="Filter by workflow status (draft, active, paused)",
        ),
    ] = None,
    offset: Annotated[
        int, Query(ge=0, description="Pagination offset")
    ] = 0,
    limit: Annotated[
        int, Query(ge=1, le=100, description="Maximum items per page")
    ] = 50,
    _rate_limit: Annotated[None, Depends(rate_limit_default)] = None,
) -> PaginatedWorkflowResponse:
    """List workflows for the authenticated account.

    Args:
        user: Authenticated user.
        use_case: List workflows use case.
        status_filter: Optional status filter.
        offset: Pagination offset.
        limit: Maximum items per page.

    Returns:
        Paginated list of workflows.
    """
    workflows, total = await use_case.execute(
        account_id=user.account_id,
        status=status_filter,
        offset=offset,
        limit=limit,
    )

    return PaginatedWorkflowResponse(
        items=workflows,
        total=total,
        offset=offset,
        limit=limit,
        has_more=(offset + len(workflows)) < total,
    )


@router.get(
    "/{workflow_id}",
    response_model=WorkflowResponse,
    summary="Get workflow by ID",
    description="Retrieve a single workflow by its ID.",
    responses={
        404: {"model": ErrorResponse, "description": "Workflow not found"},
    },
)
async def get_workflow(
    workflow_id: UUID,
    user: AuthenticatedUser,
    use_case: GetWorkflowUseCaseDep,
    _rate_limit: Annotated[None, Depends(rate_limit_default)] = None,
) -> WorkflowResponse:
    """Get a workflow by ID.

    Args:
        workflow_id: The workflow ID.
        user: Authenticated user.
        use_case: Get workflow use case.

    Returns:
        The workflow if found.

    Raises:
        HTTPException: If workflow not found.
    """
    workflow = await use_case.execute(
        workflow_id=workflow_id,
        account_id=user.account_id,
    )

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "workflow_not_found",
                "message": f"Workflow with ID '{workflow_id}' not found",
            },
        )

    return workflow


@router.patch(
    "/{workflow_id}",
    response_model=WorkflowResponse,
    summary="Update workflow",
    description="Update an existing workflow. Only provided fields will be updated.",
    responses={
        404: {"model": ErrorResponse, "description": "Workflow not found"},
        409: {"model": ErrorResponse, "description": "Workflow name already exists"},
    },
)
async def update_workflow(
    request: Request,
    workflow_id: UUID,
    body: UpdateWorkflowRequest,
    user: AuthenticatedUser,
    use_case: UpdateWorkflowUseCaseDep,
    session: Annotated[AsyncSession, Depends(get_db)],
    _rate_limit: Annotated[None, Depends(rate_limit_default)] = None,
) -> WorkflowResponse:
    """Update a workflow.

    Args:
        request: FastAPI request object.
        workflow_id: The workflow ID.
        body: Update data.
        user: Authenticated user.
        use_case: Update workflow use case.
        session: Database session.

    Returns:
        The updated workflow.

    Raises:
        HTTPException: If workflow not found or name conflict.
    """
    try:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        workflow = await use_case.execute(
            workflow_id=workflow_id,
            account_id=user.account_id,
            user_id=user.user_id,
            name=body.name,
            description=body.description,
            trigger_type=body.trigger_type,
            trigger_config=body.trigger_config,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "workflow_not_found",
                    "message": f"Workflow with ID '{workflow_id}' not found",
                },
            )

        await session.commit()
        return workflow

    except WorkflowAlreadyExistsError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "duplicate_workflow",
                "message": str(e),
            },
        ) from e
    except WorkflowDomainError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "domain_error",
                "message": str(e),
            },
        ) from e
    except HTTPException:
        raise
    except Exception:
        await session.rollback()
        raise


@router.delete(
    "/{workflow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete workflow",
    description="Soft delete a workflow. The workflow can be restored if needed.",
    responses={
        404: {"model": ErrorResponse, "description": "Workflow not found"},
    },
)
async def delete_workflow(
    request: Request,
    workflow_id: UUID,
    user: AuthenticatedUser,
    use_case: DeleteWorkflowUseCaseDep,
    session: Annotated[AsyncSession, Depends(get_db)],
    _rate_limit: Annotated[None, Depends(rate_limit_default)] = None,
) -> None:
    """Delete a workflow (soft delete).

    Args:
        request: FastAPI request object.
        workflow_id: The workflow ID.
        user: Authenticated user.
        use_case: Delete workflow use case.
        session: Database session.

    Raises:
        HTTPException: If workflow not found.
    """
    try:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        deleted = await use_case.execute(
            workflow_id=workflow_id,
            account_id=user.account_id,
            user_id=user.user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "workflow_not_found",
                    "message": f"Workflow with ID '{workflow_id}' not found",
                },
            )

        await session.commit()

    except HTTPException:
        raise
    except Exception:
        await session.rollback()
        raise
