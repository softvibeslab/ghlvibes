"""Use case for creating workflow versions.

Implements the workflow version creation process following
domain-driven design principles.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.workflows.application.version_dtos import (
    CreateVersionDTO,
    CreateVersionResponseDTO,
    PreviousVersionDTO,
    VersionResponseDTO,
)
from src.workflows.domain.version_entities import WorkflowVersion
from src.workflows.domain.version_exceptions import MaxVersionsExceededError
from src.workflows.domain.version_value_objects import VersionNumber
from src.workflows.infrastructure.version_repository import WorkflowVersionRepository


class CreateVersionUseCase:
    """Use case for creating new workflow versions.

    Handles the business logic for creating a new version of a workflow,
    including validation, version number assignment, and ensuring
    the previous version is properly preserved.
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
        account_id: UUID,
        user_id: UUID,
        dto: CreateVersionDTO,
    ) -> CreateVersionResponseDTO:
        """Execute the use case.

        Args:
            workflow_id: Workflow ID to create version for.
            account_id: Account ID for tenant isolation.
            user_id: User creating the version.
            dto: Create version request data.

        Returns:
            Created version response with previous version info.

        Raises:
            MaxVersionsExceededError: If maximum versions reached.
            VersionNotFoundError: If workflow not found.
        """
        # Get current version
        current_version = await self.repository.get_current_version(workflow_id, account_id)

        if current_version is None:
            # First version creation
            version_number = 1
            previous_version_info = None
            source_workflow = None  # TODO: Get from workflow repository
        else:
            # Check max version limit
            version_count = await self.repository.count_versions(workflow_id, account_id)
            if version_count >= 1000:
                raise MaxVersionsExceededError(version_count, 1000)

            # Get next version number
            version_number = await self.repository.get_next_version_number(workflow_id, account_id)

            # Store previous version info
            previous_version_info = PreviousVersionDTO(
                id=current_version.id,
                version_number=current_version.version_number.value,
                active_executions=current_version.active_executions,
            )

            # Use current version as source
            source_workflow = current_version

        # Create new version
        new_version = WorkflowVersion.create(
            workflow_id=workflow_id,
            account_id=account_id,
            version_number=version_number,
            name=source_workflow.name if source_workflow else "New Workflow",
            created_by=user_id,
            description=source_workflow.description if source_workflow else None,
            trigger_type=source_workflow.trigger_type if source_workflow else None,
            trigger_config=source_workflow.trigger_config if source_workflow else None,
            actions=source_workflow.actions if source_workflow else [],
            conditions=source_workflow.conditions if source_workflow else [],
            change_summary=dto.change_summary,
            is_current=False,  # Not current until published
        )

        # Save new version
        created_version = await self.repository.create(new_version)

        # Publish immediately if requested
        if dto.publish_immediately:
            # Deactivate current version
            if current_version:
                current_version.deactivate_current()
                await self.repository.update(current_version)

            # Publish new version
            created_version.publish()
            await self.repository.update(created_version)

        # Create audit log
        await self.repository.create_audit_log(
            workflow_id=workflow_id,
            version_id=created_version.id,
            account_id=account_id,
            action="version_created",
            user_id=user_id,
            details={
                "version_number": created_version.version_number.value,
                "change_summary": dto.change_summary,
                "published_immediately": dto.publish_immediately,
            },
        )

        # Commit transaction
        await self.db.commit()

        # Build response
        response = CreateVersionResponseDTO(
            **created_version.to_dict(),
            previous_version=previous_version_info,
        )

        return response

    async def get_workflow_for_versioning(
        self,
        workflow_id: UUID,
        account_id: UUID,
    ) -> dict | None:
        """Get workflow data for versioning.

        This is a placeholder method that should be implemented
        when the workflow repository is available.

        Args:
            workflow_id: Workflow ID.
            account_id: Account ID.

        Returns:
            Workflow data dict or None.
        """
        # TODO: Implement when workflow repository is available
        # This should fetch from WorkflowRepository
        return None
