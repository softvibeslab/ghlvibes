"""Use case for publishing workflow versions."""

from datetime import timedelta, UTC
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.workflows.application.version_dtos import (
    MigrationInfoDTO,
    PublishVersionDTO,
    PublishVersionResponseDTO,
    VersionResponseDTO,
)
from src.workflows.domain.version_exceptions import InvalidVersionStatusError, VersionNotFoundError
from src.workflows.infrastructure.version_repository import WorkflowVersionRepository


class PublishVersionUseCase:
    """Use case for publishing workflow versions.

    Handles the business logic for activating a draft version,
    including deactivating the current version and managing
    execution migrations.
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
        version_id: UUID,
        account_id: UUID,
        user_id: UUID,
        dto: PublishVersionDTO,
    ) -> PublishVersionResponseDTO:
        """Execute the use case.

        Args:
            workflow_id: Workflow ID.
            version_id: Version ID to publish.
            account_id: Account ID for tenant isolation.
            user_id: User publishing the version.
            dto: Publish version request data.

        Returns:
            Published version response with migration info.

        Raises:
            VersionNotFoundError: If version not found.
            InvalidVersionStatusError: If version cannot be published.
        """
        # Fetch version to publish
        version = await self.repository.get_by_id(version_id, account_id)
        if version is None:
            raise VersionNotFoundError(str(version_id))

        # Validate version can be published
        if not version.can_be_published:
            raise InvalidVersionStatusError(version.status.value, "active")

        # Get current version
        current_version = await self.repository.get_current_version(workflow_id, account_id)

        # Deactivate current version
        if current_version:
            current_version.deactivate_current()
            await self.repository.update(current_version)

        # Publish new version
        version.publish()
        published_version = await self.repository.update(version)

        # Create migration if strategy specified
        migration_info = None
        if dto.migration_strategy and current_version:
            migration_info = await self._create_migration(
                workflow_id=workflow_id,
                source_version_id=current_version.id,
                target_version_id=version_id,
                account_id=account_id,
                user_id=user_id,
                strategy=dto.migration_strategy,
                batch_size=dto.batch_size,
            )

        # Create audit log
        await self.repository.create_audit_log(
            workflow_id=workflow_id,
            version_id=version_id,
            account_id=account_id,
            action="version_published",
            user_id=user_id,
            details={
                "version_number": published_version.version_number.value,
                "migration_strategy": dto.migration_strategy,
            },
        )

        # Commit transaction
        await self.db.commit()

        # Build response
        response = PublishVersionResponseDTO(
            **published_version.to_dict(),
            migration=migration_info,
        )

        return response

    async def _create_migration(
        self,
        workflow_id: UUID,
        source_version_id: UUID,
        target_version_id: UUID,
        account_id: UUID,
        user_id: UUID,
        strategy: str,
        batch_size: int,
    ) -> MigrationInfoDTO:
        """Create version migration.

        Args:
            workflow_id: Workflow ID.
            source_version_id: Source version ID.
            target_version_id: Target version ID.
            account_id: Account ID.
            user_id: User ID.
            strategy: Migration strategy.
            batch_size: Batch size.

        Returns:
            Migration info DTO.
        """
        # Get active execution count from source version
        source_version = await self.repository.get_by_id(source_version_id, account_id)
        contacts_total = source_version.active_executions if source_version else 0

        # Create migration entity
        from src.workflows.domain.version_entities import VersionMigration

        migration = VersionMigration.create(
            workflow_id=workflow_id,
            source_version_id=source_version_id,
            target_version_id=target_version_id,
            account_id=account_id,
            strategy=strategy,
            created_by=user_id,
            contacts_total=contacts_total,
            batch_size=batch_size,
        )

        # Save migration
        saved_migration = await self.repository.create_migration(migration)

        # Build migration info
        return MigrationInfoDTO(
            status="in_progress" if strategy == "immediate" else "pending",
            strategy=strategy,
            contacts_migrated=0,
            contacts_remaining=contacts_total,
            estimated_completion=self._calculate_estimated_completion(
                contacts_total, batch_size, strategy
            ),
        )

    def _calculate_estimated_completion(
        self, contacts_total: int, batch_size: int, strategy: str
    ) -> datetime | None:
        """Calculate estimated completion time.

        Args:
            contacts_total: Total contacts to migrate.
            batch_size: Batch size.
            strategy: Migration strategy.

        Returns:
            Estimated completion timestamp or None.
        """
        if contacts_total == 0:
            return None

        # Rough estimate: 1 minute per batch
        batches = (contacts_total + batch_size - 1) // batch_size
        minutes = batches * 1

        # Add buffer for gradual/manual strategies
        if strategy == "gradual":
            minutes *= 2
        elif strategy == "manual":
            minutes *= 10

        return datetime.now(UTC) + timedelta(minutes=minutes)
