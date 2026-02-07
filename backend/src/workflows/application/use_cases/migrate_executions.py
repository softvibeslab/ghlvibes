"""Use case for migrating executions between workflow versions."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.workflows.application.version_dtos import MigrationResponseDTO
from src.workflows.domain.version_entities import VersionMigration
from src.workflows.domain.version_exceptions import VersionNotFoundError
from src.workflows.infrastructure.version_repository import WorkflowVersionRepository


class MigrateExecutionsUseCase:
    """Use case for migrating workflow executions between versions.

    Handles the business logic for migrating contact executions
    from one version to another.
    """

    def __init__(self, db: AsyncSession) -> None:
        """Initialize use case.

        Args:
            db: Async database session.
        """
        self.db = db
        self.repository = WorkflowVersionRepository(db)

    async def execute(
        self,
        workflow_id: UUID,
        target_version_id: UUID,
        account_id: UUID,
        user_id: UUID,
        source_version: int,
        contact_ids: list[UUID] | None = None,
        mapping_rules: dict | None = None,
        batch_size: int = 100,
    ) -> MigrationResponseDTO:
        """Execute the use case.

        Args:
            workflow_id: Workflow ID.
            target_version_id: Target version ID.
            account_id: Account ID for tenant isolation.
            user_id: User initiating migration.
            source_version: Source version number.
            contact_ids: Optional specific contacts to migrate.
            mapping_rules: Optional action-to-action mapping rules.
            batch_size: Batch size for migration.

        Returns:
            Migration response with migration ID and details.

        Raises:
            VersionNotFoundError: If source or target version not found.
        """
        # Get source version
        source_version_entity = await self.repository.get_by_workflow_and_number(
            workflow_id, account_id, source_version
        )
        if source_version_entity is None:
            raise VersionNotFoundError(f"Source version {source_version}")

        # Get target version
        target_version_entity = await self.repository.get_by_id(target_version_id, account_id)
        if target_version_entity is None:
            raise VersionNotFoundError(str(target_version_id))

        # Determine contacts to migrate
        if contact_ids:
            contacts_total = len(contact_ids)
        else:
            contacts_total = source_version_entity.active_executions

        # Create migration entity
        migration = VersionMigration.create(
            workflow_id=workflow_id,
            source_version_id=source_version_entity.id,
            target_version_id=target_version_id,
            account_id=account_id,
            strategy="manual",  # Manual migration initiated by user
            created_by=user_id,
            contacts_total=contacts_total,
            mapping_rules=mapping_rules or {},
            batch_size=batch_size,
        )

        # Save migration
        saved_migration = await self.repository.create_migration(migration)

        # Create audit log
        await self.repository.create_audit_log(
            workflow_id=workflow_id,
            version_id=target_version_id,
            account_id=account_id,
            action="execution_migration_created",
            user_id=user_id,
            details={
                "source_version": source_version,
                "target_version": target_version_entity.version_number.value,
                "contacts_total": contacts_total,
                "batch_size": batch_size,
            },
        )

        # Commit transaction
        await self.db.commit()

        # Calculate estimated duration (rough estimate: 1 minute per 100 contacts)
        estimated_duration = max(1, (contacts_total + 99) // 100)

        return MigrationResponseDTO(
            migration_id=saved_migration.id,
            status="queued",
            contacts_to_migrate=contacts_total,
            estimated_duration_minutes=estimated_duration,
        )
