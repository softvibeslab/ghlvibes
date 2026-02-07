"""Use case for rolling back workflow versions."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.workflows.application.version_dtos import (
    RollbackInfoDTO,
    RollbackVersionResponseDTO,
)
from src.workflows.domain.version_exceptions import InvalidVersionStatusError, VersionNotFoundError
from src.workflows.infrastructure.version_repository import WorkflowVersionRepository


class RollbackVersionUseCase:
    """Use case for rolling back to previous workflow versions.

    Handles the business logic for restoring a previous version
    as the current active version.
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
    ) -> RollbackVersionResponseDTO:
        """Execute the use case.

        Args:
            workflow_id: Workflow ID.
            version_id: Version ID to rollback to.
            account_id: Account ID for tenant isolation.
            user_id: User performing rollback.

        Returns:
            Rolled back version response with rollback info.

        Raises:
            VersionNotFoundError: If version not found.
            InvalidVersionStatusError: If version cannot be activated.
        """
        # Fetch version to rollback to
        target_version = await self.repository.get_by_id(version_id, account_id)
        if target_version is None:
            raise VersionNotFoundError(str(version_id))

        # Validate version can be activated
        if target_version.status.value not in ("active", "draft"):
            raise InvalidVersionStatusError(target_version.status.value, "active")

        # Get current version
        current_version = await self.repository.get_current_version(workflow_id, account_id)

        # Record rollback info before making changes
        rolled_back_from = current_version.version_number.value if current_version else 0

        # Deactivate current version
        if current_version:
            current_version.deactivate_current()
            await self.repository.update(current_version)

        # Activate target version
        target_version.status = target_version.status.value  # Keep status but make current
        target_version.is_current = True
        rolled_back_version = await self.repository.update(target_version)

        # Create audit log
        await self.repository.create_audit_log(
            workflow_id=workflow_id,
            version_id=version_id,
            account_id=account_id,
            action="version_rollback",
            user_id=user_id,
            details={
                "version_number": rolled_back_version.version_number.value,
                "rolled_back_from": rolled_back_from,
            },
        )

        # Commit transaction
        await self.db.commit()

        # Build response
        rollback_info = RollbackInfoDTO(
            rolled_back_from=rolled_back_from,
            rolled_back_at=datetime.now(UTC),
            rolled_back_by=user_id,
        )

        return RollbackVersionResponseDTO(
            **rolled_back_version.to_dict(),
            rollback_info=rollback_info,
        )
