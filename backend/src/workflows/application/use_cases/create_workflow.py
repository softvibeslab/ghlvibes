"""Create Workflow use case.

This use case handles the creation of new workflows, including
validation, domain entity creation, and persistence.
"""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from src.workflows.application.dtos import CreateWorkflowRequest, WorkflowResponse
from src.workflows.domain.entities import Workflow
from src.workflows.domain.exceptions import WorkflowAlreadyExistsError
from src.workflows.infrastructure.repositories import (
    AuditLogRepository,
    WorkflowRepository,
)


@dataclass
class CreateWorkflowResult:
    """Result of the create workflow use case.

    Attributes:
        success: Whether the operation succeeded.
        workflow: The created workflow (if successful).
        error: Error message (if failed).
    """

    success: bool
    workflow: WorkflowResponse | None = None
    error: str | None = None


class CreateWorkflowUseCase:
    """Use case for creating a new workflow.

    This use case validates the request, checks for duplicates,
    creates the domain entity, persists it, and logs the action.
    """

    def __init__(
        self,
        workflow_repository: WorkflowRepository,
        audit_log_repository: AuditLogRepository,
    ) -> None:
        """Initialize the use case with dependencies.

        Args:
            workflow_repository: Repository for workflow persistence.
            audit_log_repository: Repository for audit logging.
        """
        self._workflow_repository = workflow_repository
        self._audit_log_repository = audit_log_repository

    async def execute(
        self,
        request: CreateWorkflowRequest,
        account_id: UUID,
        user_id: UUID,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> CreateWorkflowResult:
        """Execute the create workflow use case.

        Args:
            request: The validated create workflow request.
            account_id: The account creating the workflow.
            user_id: The user creating the workflow.
            ip_address: Client IP address for audit logging.
            user_agent: Client user agent for audit logging.

        Returns:
            CreateWorkflowResult with the outcome.
        """
        # Check for duplicate name within account
        existing = await self._workflow_repository.get_by_name(
            name=request.name,
            account_id=account_id,
        )
        if existing:
            raise WorkflowAlreadyExistsError(
                name=request.name,
                account_id=str(account_id),
            )

        # Create domain entity
        workflow = Workflow.create(
            account_id=account_id,
            name=request.name,
            created_by=user_id,
            description=request.description,
            trigger_type=request.trigger_type,
            trigger_config=request.trigger_config,
        )

        # Persist workflow
        persisted_workflow = await self._workflow_repository.create(workflow)

        # Create audit log
        await self._audit_log_repository.create(
            workflow_id=persisted_workflow.id,
            action="created",
            changed_by=user_id,
            new_values=persisted_workflow.to_dict(),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Return success response
        return CreateWorkflowResult(
            success=True,
            workflow=WorkflowResponse.from_entity(persisted_workflow),
        )


class GetWorkflowUseCase:
    """Use case for retrieving a workflow by ID."""

    def __init__(self, workflow_repository: WorkflowRepository) -> None:
        """Initialize with repository."""
        self._workflow_repository = workflow_repository

    async def execute(
        self,
        workflow_id: UUID,
        account_id: UUID,
    ) -> WorkflowResponse | None:
        """Get a workflow by ID.

        Args:
            workflow_id: The workflow ID.
            account_id: The account ID.

        Returns:
            WorkflowResponse if found, None otherwise.
        """
        workflow = await self._workflow_repository.get_by_id(
            workflow_id=workflow_id,
            account_id=account_id,
        )
        return WorkflowResponse.from_entity(workflow) if workflow else None


class ListWorkflowsUseCase:
    """Use case for listing workflows."""

    def __init__(self, workflow_repository: WorkflowRepository) -> None:
        """Initialize with repository."""
        self._workflow_repository = workflow_repository

    async def execute(
        self,
        account_id: UUID,
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[WorkflowResponse], int]:
        """List workflows for an account.

        Args:
            account_id: The account ID.
            status: Optional status filter.
            offset: Pagination offset.
            limit: Maximum items.

        Returns:
            Tuple of (workflows, total_count).
        """
        from src.workflows.domain.value_objects import WorkflowStatus

        status_enum = WorkflowStatus(status) if status else None

        workflows = await self._workflow_repository.list_by_account(
            account_id=account_id,
            status=status_enum,
            offset=offset,
            limit=limit,
        )
        total = await self._workflow_repository.count_by_account(
            account_id=account_id,
            status=status_enum,
        )

        return [WorkflowResponse.from_entity(w) for w in workflows], total


class UpdateWorkflowUseCase:
    """Use case for updating a workflow."""

    def __init__(
        self,
        workflow_repository: WorkflowRepository,
        audit_log_repository: AuditLogRepository,
    ) -> None:
        """Initialize with repositories."""
        self._workflow_repository = workflow_repository
        self._audit_log_repository = audit_log_repository

    async def execute(
        self,
        workflow_id: UUID,
        account_id: UUID,
        user_id: UUID,
        name: str | None = None,
        description: str | None = None,
        trigger_type: str | None = None,
        trigger_config: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> WorkflowResponse | None:
        """Update a workflow.

        Args:
            workflow_id: The workflow ID.
            account_id: The account ID.
            user_id: The user making the update.
            name: New name (optional).
            description: New description (optional).
            trigger_type: New trigger type (optional).
            trigger_config: New trigger config (optional).
            ip_address: Client IP for audit.
            user_agent: Client user agent for audit.

        Returns:
            Updated WorkflowResponse if successful, None if not found.
        """
        workflow = await self._workflow_repository.get_by_id(
            workflow_id=workflow_id,
            account_id=account_id,
        )
        if not workflow:
            return None

        old_values = workflow.to_dict()

        # Check for duplicate name if changing
        if name and name != str(workflow.name):
            existing = await self._workflow_repository.get_by_name(
                name=name,
                account_id=account_id,
            )
            if existing and existing.id != workflow_id:
                raise WorkflowAlreadyExistsError(
                    name=name,
                    account_id=str(account_id),
                )

        # Update the entity
        workflow.update(
            updated_by=user_id,
            name=name,
            description=description,
            trigger_type=trigger_type,
            trigger_config=trigger_config,
        )

        # Persist changes
        updated_workflow = await self._workflow_repository.update(workflow)

        # Audit log
        await self._audit_log_repository.create(
            workflow_id=workflow_id,
            action="updated",
            changed_by=user_id,
            old_values=old_values,
            new_values=updated_workflow.to_dict(),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return WorkflowResponse.from_entity(updated_workflow)


class DeleteWorkflowUseCase:
    """Use case for deleting a workflow."""

    def __init__(
        self,
        workflow_repository: WorkflowRepository,
        audit_log_repository: AuditLogRepository,
    ) -> None:
        """Initialize with repositories."""
        self._workflow_repository = workflow_repository
        self._audit_log_repository = audit_log_repository

    async def execute(
        self,
        workflow_id: UUID,
        account_id: UUID,
        user_id: UUID,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> bool:
        """Delete a workflow (soft delete).

        Args:
            workflow_id: The workflow ID.
            account_id: The account ID.
            user_id: The user deleting.
            ip_address: Client IP for audit.
            user_agent: Client user agent for audit.

        Returns:
            True if deleted, False if not found.
        """
        workflow = await self._workflow_repository.get_by_id(
            workflow_id=workflow_id,
            account_id=account_id,
        )
        if not workflow:
            return False

        old_values = workflow.to_dict()

        deleted = await self._workflow_repository.delete(
            workflow_id=workflow_id,
            account_id=account_id,
            deleted_by=user_id,
        )

        if deleted:
            await self._audit_log_repository.create(
                workflow_id=workflow_id,
                action="deleted",
                changed_by=user_id,
                old_values=old_values,
                ip_address=ip_address,
                user_agent=user_agent,
            )

        return deleted
