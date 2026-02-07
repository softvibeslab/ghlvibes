"""Repository implementation for workflow versioning.

Provides data access operations for workflow versions,
migrations, and related entities using SQLAlchemy.
"""

from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.workflows.domain.version_entities import VersionDiff, VersionMigration, WorkflowVersion
from src.workflows.domain.version_exceptions import VersionNotFoundError
from src.workflows.infrastructure.version_models import (
    WorkflowVersionAuditLogModel,
    WorkflowVersionDraftModel,
    WorkflowVersionMigrationModel,
    WorkflowVersionModel,
)


class WorkflowVersionRepository:
    """Repository for workflow version data access.

    Provides methods for CRUD operations on workflow versions,
    migrations, drafts, and audit logs.
    """

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository.

        Args:
            db: Async database session.
        """
        self.db = db

    # Version CRUD operations

    async def create(self, version: WorkflowVersion) -> WorkflowVersion:
        """Create a new workflow version.

        Args:
            version: Domain entity to create.

        Returns:
            Created version with assigned ID.
        """
        model = WorkflowVersionModel(
            id=version.id,
            workflow_id=version.workflow_id,
            account_id=version.account_id,
            version_number=version.version_number.value,
            name=version.name,
            description=version.description,
            trigger_type=version.trigger_type,
            trigger_config=version.trigger_config,
            actions=version.actions,
            conditions=version.conditions,
            status=version.status.value,
            change_summary=str(version.change_summary) if version.change_summary else None,
            is_current=version.is_current,
            active_executions=version.active_executions,
            created_at=version.created_at,
            created_by=version.created_by,
            archived_at=version.archived_at,
        )

        self.db.add(model)
        await self.db.flush()
        await self.db.refresh(model)

        return self._model_to_entity(model)

    async def get_by_id(self, version_id: UUID, account_id: UUID) -> WorkflowVersion | None:
        """Get version by ID.

        Args:
            version_id: Version ID.
            account_id: Account ID for tenant isolation.

        Returns:
            Version if found, None otherwise.
        """
        result = await self.db.execute(
            select(WorkflowVersionModel).where(
                WorkflowVersionModel.id == version_id,
                WorkflowVersionModel.account_id == account_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_workflow_and_number(
        self,
        workflow_id: UUID,
        account_id: UUID,
        version_number: int,
    ) -> WorkflowVersion | None:
        """Get version by workflow ID and version number.

        Args:
            workflow_id: Workflow ID.
            account_id: Account ID for tenant isolation.
            version_number: Version number.

        Returns:
            Version if found, None otherwise.
        """
        result = await self.db.execute(
            select(WorkflowVersionModel).where(
                WorkflowVersionModel.workflow_id == workflow_id,
                WorkflowVersionModel.account_id == account_id,
                WorkflowVersionModel.version_number == version_number,
            )
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_current_version(
        self,
        workflow_id: UUID,
        account_id: UUID,
    ) -> WorkflowVersion | None:
        """Get current version of a workflow.

        Args:
            workflow_id: Workflow ID.
            account_id: Account ID for tenant isolation.

        Returns:
            Current version if found, None otherwise.
        """
        result = await self.db.execute(
            select(WorkflowVersionModel).where(
                WorkflowVersionModel.workflow_id == workflow_id,
                WorkflowVersionModel.account_id == account_id,
                WorkflowVersionModel.is_current == True,
            )
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def list_versions(
        self,
        workflow_id: UUID,
        account_id: UUID,
        include_archived: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[WorkflowVersion], int]:
        """List versions for a workflow.

        Args:
            workflow_id: Workflow ID.
            account_id: Account ID for tenant isolation.
            include_archived: Whether to include archived versions.
            limit: Maximum number of versions to return.
            offset: Number of versions to skip.

        Returns:
            Tuple of (list of versions, total count).
        """
        # Build base query
        query = select(WorkflowVersionModel).where(
            WorkflowVersionModel.workflow_id == workflow_id,
            WorkflowVersionModel.account_id == account_id,
        )

        # Filter archived if not included
        if not include_archived:
            query = query.where(WorkflowVersionModel.status != "archived")

        # Order by version_number descending
        query = query.order_by(WorkflowVersionModel.version_number.desc())

        # Get total count
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        # Apply pagination
        query = query.limit(limit).offset(offset)
        result = await self.db.execute(query)
        models = result.scalars().all()

        versions = [self._model_to_entity(model) for model in models]
        return versions, total

    async def update(self, version: WorkflowVersion) -> WorkflowVersion:
        """Update an existing version.

        Args:
            version: Domain entity with updated data.

        Returns:
            Updated version.

        Raises:
            VersionNotFoundError: If version doesn't exist.
        """
        result = await self.db.execute(
            select(WorkflowVersionModel).where(
                WorkflowVersionModel.id == version.id,
                WorkflowVersionModel.account_id == version.account_id,
            )
        )
        model = result.scalar_one_or_none()

        if not model:
            raise VersionNotFoundError(str(version.id))

        # Update fields
        model.status = version.status.value
        model.change_summary = str(version.change_summary) if version.change_summary else None
        model.is_current = version.is_current
        model.active_executions = version.active_executions
        model.archived_at = version.archived_at

        await self.db.flush()
        await self.db.refresh(model)

        return self._model_to_entity(model)

    async def increment_executions(self, version_id: UUID, account_id: UUID) -> None:
        """Increment active execution count for a version.

        Args:
            version_id: Version ID.
            account_id: Account ID for tenant isolation.
        """
        result = await self.db.execute(
            select(WorkflowVersionModel).where(
                WorkflowVersionModel.id == version_id,
                WorkflowVersionModel.account_id == account_id,
            )
        )
        model = result.scalar_one_or_none()

        if model:
            model.active_executions += 1
            await self.db.flush()

    async def decrement_executions(self, version_id: UUID, account_id: UUID) -> None:
        """Decrement active execution count for a version.

        Args:
            version_id: Version ID.
            account_id: Account ID for tenant isolation.
        """
        result = await self.db.execute(
            select(WorkflowVersionModel).where(
                WorkflowVersionModel.id == version_id,
                WorkflowVersionModel.account_id == account_id,
            )
        )
        model = result.scalar_one_or_none()

        if model:
            model.active_executions = max(0, model.active_executions - 1)
            await self.db.flush()

    async def get_next_version_number(self, workflow_id: UUID, account_id: UUID) -> int:
        """Get the next version number for a workflow.

        Args:
            workflow_id: Workflow ID.
            account_id: Account ID for tenant isolation.

        Returns:
            Next version number (1 if no versions exist).
        """
        result = await self.db.execute(
            select(func.max(WorkflowVersionModel.version_number)).where(
                WorkflowVersionModel.workflow_id == workflow_id,
                WorkflowVersionModel.account_id == account_id,
            )
        )
        max_version = result.scalar() or 0
        return max_version + 1

    async def count_versions(self, workflow_id: UUID, account_id: UUID) -> int:
        """Count total versions for a workflow.

        Args:
            workflow_id: Workflow ID.
            account_id: Account ID for tenant isolation.

        Returns:
            Total number of versions.
        """
        result = await self.db.execute(
            select(func.count()).select_from(
                select(WorkflowVersionModel.id).where(
                    WorkflowVersionModel.workflow_id == workflow_id,
                    WorkflowVersionModel.account_id == account_id,
                )
            )
        )
        return result.scalar() or 0

    # Migration operations

    async def create_migration(self, migration: VersionMigration) -> VersionMigration:
        """Create a new version migration.

        Args:
            migration: Domain entity to create.

        Returns:
            Created migration with assigned ID.
        """
        model = WorkflowVersionMigrationModel(
            id=migration.id,
            workflow_id=migration.workflow_id,
            source_version_id=migration.source_version_id,
            target_version_id=migration.target_version_id,
            account_id=migration.account_id,
            strategy=migration.strategy,
            mapping_rules=migration.mapping_rules,
            batch_size=migration.batch_size,
            status=migration.status,
            contacts_total=migration.contacts_total,
            contacts_migrated=migration.contacts_migrated,
            contacts_failed=migration.contacts_failed,
            error_log=migration.error_log,
            started_at=migration.started_at,
            completed_at=migration.completed_at,
            created_at=migration.created_at,
            created_by=migration.created_by,
        )

        self.db.add(model)
        await self.db.flush()
        await self.db.refresh(model)

        return self._migration_model_to_entity(model)

    async def get_migration_by_id(self, migration_id: UUID, account_id: UUID) -> VersionMigration | None:
        """Get migration by ID.

        Args:
            migration_id: Migration ID.
            account_id: Account ID for tenant isolation.

        Returns:
            Migration if found, None otherwise.
        """
        result = await self.db.execute(
            select(WorkflowVersionMigrationModel).where(
                WorkflowVersionMigrationModel.id == migration_id,
                WorkflowVersionMigrationModel.account_id == account_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._migration_model_to_entity(model) if model else None

    async def update_migration(self, migration: VersionMigration) -> VersionMigration:
        """Update an existing migration.

        Args:
            migration: Domain entity with updated data.

        Returns:
            Updated migration.
        """
        result = await self.db.execute(
            select(WorkflowVersionMigrationModel).where(
                WorkflowVersionMigrationModel.id == migration.id,
                WorkflowVersionMigrationModel.account_id == migration.account_id,
            )
        )
        model = result.scalar_one_or_none()

        if not model:
            raise VersionNotFoundError(str(migration.id))

        # Update fields
        model.status = migration.status
        model.contacts_migrated = migration.contacts_migrated
        model.contacts_failed = migration.contacts_failed
        model.error_log = migration.error_log
        model.started_at = migration.started_at
        model.completed_at = migration.completed_at

        await self.db.flush()
        await self.db.refresh(model)

        return self._migration_model_to_entity(model)

    # Draft operations

    async def save_draft(
        self,
        workflow_id: UUID,
        user_id: UUID,
        account_id: UUID,
        draft_data: dict[str, Any],
    ) -> None:
        """Save or update draft data for a workflow.

        Args:
            workflow_id: Workflow ID.
            user_id: User ID.
            account_id: Account ID.
            draft_data: Draft data to save.
        """
        result = await self.db.execute(
            select(WorkflowVersionDraftModel).where(
                WorkflowVersionDraftModel.workflow_id == workflow_id,
                WorkflowVersionDraftModel.user_id == user_id,
                WorkflowVersionDraftModel.account_id == account_id,
            )
        )
        model = result.scalar_one_or_none()

        if model:
            # Update existing draft
            model.draft_data = draft_data
            model.last_saved_at = func.now()
        else:
            # Create new draft
            model = WorkflowVersionDraftModel(
                workflow_id=workflow_id,
                user_id=user_id,
                account_id=account_id,
                draft_data=draft_data,
            )
            self.db.add(model)

        await self.db.flush()

    async def get_draft(
        self,
        workflow_id: UUID,
        user_id: UUID,
        account_id: UUID,
    ) -> dict[str, Any] | None:
        """Get draft data for a workflow.

        Args:
            workflow_id: Workflow ID.
            user_id: User ID.
            account_id: Account ID.

        Returns:
            Draft data if found, None otherwise.
        """
        result = await self.db.execute(
            select(WorkflowVersionDraftModel).where(
                WorkflowVersionDraftModel.workflow_id == workflow_id,
                WorkflowVersionDraftModel.user_id == user_id,
                WorkflowVersionDraftModel.account_id == account_id,
            )
        )
        model = result.scalar_one_or_none()
        return model.draft_data if model else None

    async def delete_draft(self, workflow_id: UUID, user_id: UUID, account_id: UUID) -> None:
        """Delete draft data for a workflow.

        Args:
            workflow_id: Workflow ID.
            user_id: User ID.
            account_id: Account ID.
        """
        result = await self.db.execute(
            select(WorkflowVersionDraftModel).where(
                WorkflowVersionDraftModel.workflow_id == workflow_id,
                WorkflowVersionDraftModel.user_id == user_id,
                WorkflowVersionDraftModel.account_id == account_id,
            )
        )
        model = result.scalar_one_or_none()

        if model:
            await self.db.delete(model)
            await self.db.flush()

    # Audit log operations

    async def create_audit_log(
        self,
        workflow_id: UUID,
        version_id: UUID | None,
        account_id: UUID,
        action: str,
        user_id: UUID,
        details: dict[str, Any],
    ) -> None:
        """Create an audit log entry.

        Args:
            workflow_id: Workflow ID.
            version_id: Version ID (optional).
            account_id: Account ID.
            action: Action performed.
            user_id: User who performed the action.
            details: Action details.
        """
        model = WorkflowVersionAuditLogModel(
            workflow_id=workflow_id,
            version_id=version_id,
            account_id=account_id,
            action=action,
            user_id=user_id,
            details=details,
        )
        self.db.add(model)
        await self.db.flush()

    # Helper methods

    def _model_to_entity(self, model: WorkflowVersionModel) -> WorkflowVersion:
        """Convert SQLAlchemy model to domain entity.

        Args:
            model: SQLAlchemy model.

        Returns:
            Domain entity.
        """
        from src.workflows.domain.version_entities import WorkflowVersion as DomainVersion
        from src.workflows.domain.version_value_objects import ChangeSummary, VersionNumber

        return DomainVersion(
            id=model.id,
            workflow_id=model.workflow_id,
            account_id=model.account_id,
            version_number=VersionNumber(model.version_number),
            name=model.name,
            status=model.status,  # Will be converted by __post_init__
            description=model.description,
            trigger_type=model.trigger_type,
            trigger_config=model.trigger_config,
            actions=model.actions,
            conditions=model.conditions,
            change_summary=ChangeSummary(model.change_summary) if model.change_summary else None,
            is_current=model.is_current,
            active_executions=model.active_executions,
            created_at=model.created_at,
            created_by=model.created_by,
            archived_at=model.archived_at,
        )

    def _migration_model_to_entity(self, model: WorkflowVersionMigrationModel) -> VersionMigration:
        """Convert SQLAlchemy migration model to domain entity.

        Args:
            model: SQLAlchemy model.

        Returns:
            Domain entity.
        """
        return VersionMigration(
            id=model.id,
            workflow_id=model.workflow_id,
            source_version_id=model.source_version_id,
            target_version_id=model.target_version_id,
            account_id=model.account_id,
            strategy=model.strategy,
            status=model.status,
            mapping_rules=model.mapping_rules,
            batch_size=model.batch_size,
            contacts_total=model.contacts_total,
            contacts_migrated=model.contacts_migrated,
            contacts_failed=model.contacts_failed,
            error_log=model.error_log,
            started_at=model.started_at,
            completed_at=model.completed_at,
            created_at=model.created_at,
            created_by=model.created_by,
        )
