"""Repository implementations for the workflow module.

Repositories provide an abstraction over data access, allowing
the domain layer to remain independent of persistence details.
"""

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.workflows.domain.entities import Workflow
from src.workflows.domain.exceptions import WorkflowNotFoundError
from src.workflows.domain.value_objects import WorkflowName, WorkflowStatus
from src.workflows.infrastructure.models import WorkflowAuditLog, WorkflowModel


class IWorkflowRepository(ABC):
    """Abstract interface for workflow repository.

    This interface defines the contract that any workflow
    repository implementation must follow.
    """

    @abstractmethod
    async def create(self, workflow: Workflow) -> Workflow:
        """Create a new workflow.

        Args:
            workflow: The workflow entity to persist.

        Returns:
            The persisted workflow with any generated fields.
        """
        pass

    @abstractmethod
    async def get_by_id(self, workflow_id: UUID, account_id: UUID) -> Workflow | None:
        """Get a workflow by ID.

        Args:
            workflow_id: The unique workflow identifier.
            account_id: The account the workflow belongs to.

        Returns:
            The workflow if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_by_name(self, name: str, account_id: UUID) -> Workflow | None:
        """Get a workflow by name within an account.

        Args:
            name: The workflow name.
            account_id: The account to search in.

        Returns:
            The workflow if found, None otherwise.
        """
        pass

    @abstractmethod
    async def list_by_account(
        self,
        account_id: UUID,
        status: WorkflowStatus | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[Workflow]:
        """List workflows for an account.

        Args:
            account_id: The account to list workflows for.
            status: Optional status filter.
            offset: Pagination offset.
            limit: Maximum number of results.

        Returns:
            List of workflows matching the criteria.
        """
        pass

    @abstractmethod
    async def update(self, workflow: Workflow) -> Workflow:
        """Update an existing workflow.

        Args:
            workflow: The workflow entity with updated values.

        Returns:
            The updated workflow.
        """
        pass

    @abstractmethod
    async def delete(self, workflow_id: UUID, account_id: UUID, deleted_by: UUID) -> bool:
        """Soft delete a workflow.

        Args:
            workflow_id: The workflow to delete.
            account_id: The account the workflow belongs to.
            deleted_by: The user performing the deletion.

        Returns:
            True if deleted, False if not found.
        """
        pass

    @abstractmethod
    async def count_by_account(
        self,
        account_id: UUID,
        status: WorkflowStatus | None = None,
    ) -> int:
        """Count workflows for an account.

        Args:
            account_id: The account to count workflows for.
            status: Optional status filter.

        Returns:
            The number of matching workflows.
        """
        pass


class WorkflowRepository(IWorkflowRepository):
    """SQLAlchemy implementation of the workflow repository.

    This implementation uses async SQLAlchemy for database operations
    and handles the mapping between domain entities and ORM models.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session.
        """
        self._session = session

    async def create(self, workflow: Workflow) -> Workflow:
        """Create a new workflow in the database."""
        model = WorkflowModel(
            id=workflow.id,
            account_id=workflow.account_id,
            name=str(workflow.name),
            description=workflow.description,
            trigger_type=workflow.trigger_type,
            trigger_config=workflow.trigger_config,
            status=workflow.status,
            version=workflow.version,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at,
            created_by=workflow.created_by,
            updated_by=workflow.updated_by,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, workflow_id: UUID, account_id: UUID) -> Workflow | None:
        """Get a workflow by ID."""
        query = select(WorkflowModel).where(
            and_(
                WorkflowModel.id == workflow_id,
                WorkflowModel.account_id == account_id,
                WorkflowModel.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()

        return self._to_entity(model) if model else None

    async def get_by_name(self, name: str, account_id: UUID) -> Workflow | None:
        """Get a workflow by name within an account."""
        query = select(WorkflowModel).where(
            and_(
                WorkflowModel.name == name,
                WorkflowModel.account_id == account_id,
                WorkflowModel.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()

        return self._to_entity(model) if model else None

    async def list_by_account(
        self,
        account_id: UUID,
        status: WorkflowStatus | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[Workflow]:
        """List workflows for an account with optional filtering."""
        query = select(WorkflowModel).where(
            and_(
                WorkflowModel.account_id == account_id,
                WorkflowModel.deleted_at.is_(None),
            )
        )

        if status is not None:
            query = query.where(WorkflowModel.status == status)

        query = query.order_by(WorkflowModel.created_at.desc()).offset(offset).limit(limit)

        result = await self._session.execute(query)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def update(self, workflow: Workflow) -> Workflow:
        """Update an existing workflow."""
        query = select(WorkflowModel).where(
            and_(
                WorkflowModel.id == workflow.id,
                WorkflowModel.account_id == workflow.account_id,
                WorkflowModel.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            raise WorkflowNotFoundError(str(workflow.id))

        # Update fields
        model.name = str(workflow.name)
        model.description = workflow.description
        model.trigger_type = workflow.trigger_type
        model.trigger_config = workflow.trigger_config
        model.status = workflow.status
        model.version = workflow.version
        model.updated_at = workflow.updated_at
        model.updated_by = workflow.updated_by

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(self, workflow_id: UUID, account_id: UUID, deleted_by: UUID) -> bool:
        """Soft delete a workflow."""
        query = select(WorkflowModel).where(
            and_(
                WorkflowModel.id == workflow_id,
                WorkflowModel.account_id == account_id,
                WorkflowModel.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            return False

        model.deleted_at = datetime.now(UTC)
        model.updated_by = deleted_by
        model.updated_at = datetime.now(UTC)

        await self._session.flush()
        return True

    async def count_by_account(
        self,
        account_id: UUID,
        status: WorkflowStatus | None = None,
    ) -> int:
        """Count workflows for an account."""
        from sqlalchemy import func

        query = select(func.count()).select_from(WorkflowModel).where(
            and_(
                WorkflowModel.account_id == account_id,
                WorkflowModel.deleted_at.is_(None),
            )
        )

        if status is not None:
            query = query.where(WorkflowModel.status == status)

        result = await self._session.execute(query)
        return result.scalar() or 0

    def _to_entity(self, model: WorkflowModel) -> Workflow:
        """Convert ORM model to domain entity."""
        return Workflow(
            id=model.id,
            account_id=model.account_id,
            name=WorkflowName(model.name),
            description=model.description,
            trigger_type=model.trigger_type,
            trigger_config=model.trigger_config,
            status=model.status,
            version=model.version,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by,
        )


class IAuditLogRepository(ABC):
    """Abstract interface for audit log repository."""

    @abstractmethod
    async def create(
        self,
        workflow_id: UUID,
        action: str,
        changed_by: UUID | None,
        old_values: dict[str, Any] | None = None,
        new_values: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """Create an audit log entry."""
        pass

    @abstractmethod
    async def list_by_workflow(
        self,
        workflow_id: UUID,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List audit logs for a workflow."""
        pass


class AuditLogRepository(IAuditLogRepository):
    """SQLAlchemy implementation of the audit log repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self._session = session

    async def create(
        self,
        workflow_id: UUID,
        action: str,
        changed_by: UUID | None,
        old_values: dict[str, Any] | None = None,
        new_values: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """Create an audit log entry."""
        log = WorkflowAuditLog(
            workflow_id=workflow_id,
            action=action,
            old_values=old_values,
            new_values=new_values,
            changed_by=changed_by,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self._session.add(log)
        await self._session.flush()

    async def list_by_workflow(
        self,
        workflow_id: UUID,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List audit logs for a workflow."""
        query = (
            select(WorkflowAuditLog)
            .where(WorkflowAuditLog.workflow_id == workflow_id)
            .order_by(WorkflowAuditLog.changed_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self._session.execute(query)
        logs = result.scalars().all()

        return [
            {
                "id": str(log.id),
                "workflow_id": str(log.workflow_id),
                "action": log.action,
                "old_values": log.old_values,
                "new_values": log.new_values,
                "changed_by": str(log.changed_by) if log.changed_by else None,
                "changed_at": log.changed_at.isoformat(),
                "ip_address": log.ip_address,
            }
            for log in logs
        ]
