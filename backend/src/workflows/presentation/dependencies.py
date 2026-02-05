"""Dependency injection for workflow routes.

This module provides FastAPI dependencies for injecting
use cases and other services into route handlers.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import AuthenticatedUser, get_current_user
from src.workflows.application.use_cases.create_workflow import (
    CreateWorkflowUseCase,
    DeleteWorkflowUseCase,
    GetWorkflowUseCase,
    ListWorkflowsUseCase,
    UpdateWorkflowUseCase,
)
from src.workflows.infrastructure.repositories import (
    AuditLogRepository,
    WorkflowRepository,
)


async def get_workflow_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> WorkflowRepository:
    """Get workflow repository instance.

    Args:
        session: Database session.

    Returns:
        WorkflowRepository instance.
    """
    return WorkflowRepository(session)


async def get_audit_log_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> AuditLogRepository:
    """Get audit log repository instance.

    Args:
        session: Database session.

    Returns:
        AuditLogRepository instance.
    """
    return AuditLogRepository(session)


async def get_create_workflow_use_case(
    workflow_repo: Annotated[WorkflowRepository, Depends(get_workflow_repository)],
    audit_repo: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
) -> CreateWorkflowUseCase:
    """Get create workflow use case.

    Args:
        workflow_repo: Workflow repository.
        audit_repo: Audit log repository.

    Returns:
        CreateWorkflowUseCase instance.
    """
    return CreateWorkflowUseCase(
        workflow_repository=workflow_repo,
        audit_log_repository=audit_repo,
    )


async def get_get_workflow_use_case(
    workflow_repo: Annotated[WorkflowRepository, Depends(get_workflow_repository)],
) -> GetWorkflowUseCase:
    """Get get workflow use case.

    Args:
        workflow_repo: Workflow repository.

    Returns:
        GetWorkflowUseCase instance.
    """
    return GetWorkflowUseCase(workflow_repository=workflow_repo)


async def get_list_workflows_use_case(
    workflow_repo: Annotated[WorkflowRepository, Depends(get_workflow_repository)],
) -> ListWorkflowsUseCase:
    """Get list workflows use case.

    Args:
        workflow_repo: Workflow repository.

    Returns:
        ListWorkflowsUseCase instance.
    """
    return ListWorkflowsUseCase(workflow_repository=workflow_repo)


async def get_update_workflow_use_case(
    workflow_repo: Annotated[WorkflowRepository, Depends(get_workflow_repository)],
    audit_repo: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
) -> UpdateWorkflowUseCase:
    """Get update workflow use case.

    Args:
        workflow_repo: Workflow repository.
        audit_repo: Audit log repository.

    Returns:
        UpdateWorkflowUseCase instance.
    """
    return UpdateWorkflowUseCase(
        workflow_repository=workflow_repo,
        audit_log_repository=audit_repo,
    )


async def get_delete_workflow_use_case(
    workflow_repo: Annotated[WorkflowRepository, Depends(get_workflow_repository)],
    audit_repo: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
) -> DeleteWorkflowUseCase:
    """Get delete workflow use case.

    Args:
        workflow_repo: Workflow repository.
        audit_repo: Audit log repository.

    Returns:
        DeleteWorkflowUseCase instance.
    """
    return DeleteWorkflowUseCase(
        workflow_repository=workflow_repo,
        audit_log_repository=audit_repo,
    )


# Type aliases for cleaner route signatures
CreateWorkflowUseCaseDep = Annotated[
    CreateWorkflowUseCase, Depends(get_create_workflow_use_case)
]
GetWorkflowUseCaseDep = Annotated[GetWorkflowUseCase, Depends(get_get_workflow_use_case)]
ListWorkflowsUseCaseDep = Annotated[
    ListWorkflowsUseCase, Depends(get_list_workflows_use_case)
]
UpdateWorkflowUseCaseDep = Annotated[
    UpdateWorkflowUseCase, Depends(get_update_workflow_use_case)
]
DeleteWorkflowUseCaseDep = Annotated[
    DeleteWorkflowUseCase, Depends(get_delete_workflow_use_case)
]
