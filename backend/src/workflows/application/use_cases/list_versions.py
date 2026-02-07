"""Use case for listing workflow versions."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.workflows.application.version_dtos import (
    PaginationDTO,
    VersionListItemDTO,
    VersionListResponseDTO,
)
from src.workflows.infrastructure.version_repository import WorkflowVersionRepository


class ListVersionsUseCase:
    """Use case for listing workflow versions.

    Retrieves paginated list of versions for a workflow.
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
        include_archived: bool = False,
        page: int = 1,
        per_page: int = 20,
    ) -> VersionListResponseDTO:
        """Execute the use case.

        Args:
            workflow_id: Workflow ID.
            account_id: Account ID for tenant isolation.
            include_archived: Whether to include archived versions.
            page: Page number (1-indexed).
            per_page: Items per page (max 100).

        Returns:
            Paginated list of workflow versions.
        """
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 20
        if per_page > 100:
            per_page = 100

        # Calculate offset
        offset = (page - 1) * per_page

        # Fetch versions
        versions, total = await self.repository.list_versions(
            workflow_id=workflow_id,
            account_id=account_id,
            include_archived=include_archived,
            limit=per_page,
            offset=offset,
        )

        # Convert to DTOs
        version_dtos = [
            VersionListItemDTO(
                id=v.id,
                version_number=v.version_number.value,
                status=v.status.value,
                is_current=v.is_current,
                active_executions=v.active_executions,
                change_summary=str(v.change_summary) if v.change_summary else None,
                created_at=v.created_at,
                created_by=v.created_by,
            )
            for v in versions
        ]

        # Calculate pagination metadata
        total_pages = (total + per_page - 1) // per_page  # Ceiling division

        pagination = PaginationDTO(
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )

        return VersionListResponseDTO(
            versions=version_dtos,
            pagination=pagination,
        )
