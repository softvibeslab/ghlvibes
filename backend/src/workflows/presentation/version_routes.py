"""FastAPI routes for workflow versioning.

Defines all API endpoints for workflow version management,
including CRUD, comparison, publishing, rollback, and migration.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.workflows.application.use_cases.compare_versions import CompareVersionsUseCase
from src.workflows.application.use_cases.create_version import CreateVersionUseCase
from src.workflows.application.use_cases.list_versions import ListVersionsUseCase
from src.workflows.application.use_cases.migrate_executions import MigrateExecutionsUseCase
from src.workflows.application.use_cases.publish_version import PublishVersionUseCase
from src.workflows.application.use_cases.rollback_version import RollbackVersionUseCase
from src.workflows.application.version_dtos import (
    CompareVersionsDTO,
    CompareVersionsResponseDTO,
    CreateVersionDTO,
    CreateVersionResponseDTO,
    MigrateExecutionsDTO,
    MigrationResponseDTO,
    PublishVersionDTO,
    PublishVersionResponseDTO,
    RollbackVersionDTO,
    RollbackVersionResponseDTO,
    VersionListResponseDTO,
)

router = APIRouter(prefix="/api/v1/workflows/{workflow_id}/versions", tags=["versions"])


# Account ID dependency (placeholder - should come from auth context)
async def get_account_id() -> UUID:
    """Get account ID from authentication context.

    This is a placeholder. In production, this should extract
    the account_id from the JWT token or session.

    Returns:
        Account ID.
    """
    # TODO: Implement proper auth context extraction
    return UUID("00000000-0000-0000-0000-000000000000")


# User ID dependency (placeholder - should come from auth context)
async def get_user_id() -> UUID:
    """Get user ID from authentication context.

    This is a placeholder. In production, this should extract
    the user_id from the JWT token or session.

    Returns:
        User ID.
    """
    # TODO: Implement proper auth context extraction
    return UUID("00000000-0000-0000-0000-000000000000")


@router.post("", response_model=CreateVersionResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_workflow_version(
    workflow_id: UUID,
    dto: CreateVersionDTO,
    db: Annotated[AsyncSession, Depends(get_db)],
    account_id: Annotated[UUID, Depends(get_account_id)],
    user_id: Annotated[UUID, Depends(get_user_id)],
) -> CreateVersionResponseDTO:
    """Create a new workflow version.

    Creates a new version of the workflow by copying the current
    workflow state. The previous version is preserved and
    executions continue on their original version.

    Args:
        workflow_id: Workflow ID.
        dto: Create version request data.
        db: Database session.
        account_id: Account ID from auth.
        user_id: User ID from auth.

    Returns:
        Created version with previous version info.

    Raises:
        404: If workflow not found.
        409: If maximum versions exceeded.
    """
    use_case = CreateVersionUseCase(db)
    try:
        return await use_case.execute(
            workflow_id=workflow_id,
            account_id=account_id,
            user_id=user_id,
            dto=dto,
        )
    except Exception as e:
        if "maximum" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "MAX_VERSIONS_EXCEEDED", "message": str(e)},
            )
        raise


@router.get("", response_model=VersionListResponseDTO)
async def list_workflow_versions(
    workflow_id: UUID,
    include_archived: bool = Query(False, description="Include archived versions"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Annotated[AsyncSession, Depends(get_db)],
    account_id: Annotated[UUID, Depends(get_account_id)],
) -> VersionListResponseDTO:
    """List workflow versions.

    Returns a paginated list of versions for the specified workflow.

    Args:
        workflow_id: Workflow ID.
        include_archived: Whether to include archived versions.
        page: Page number (1-indexed).
        per_page: Items per page (max 100).
        db: Database session.
        account_id: Account ID from auth.

    Returns:
        Paginated list of workflow versions.
    """
    use_case = ListVersionsUseCase(db)
    return await use_case.execute(
        workflow_id=workflow_id,
        account_id=account_id,
        include_archived=include_archived,
        page=page,
        per_page=per_page,
    )


@router.get("/compare", response_model=CompareVersionsResponseDTO)
async def compare_workflow_versions(
    workflow_id: UUID,
    from_version: Annotated[int, Query(description="Source version number")],
    to_version: Annotated[int, Query(description="Target version number")],
    db: Annotated[AsyncSession, Depends(get_db)],
    account_id: Annotated[UUID, Depends(get_account_id)],
) -> CompareVersionsResponseDTO:
    """Compare two workflow versions.

    Returns a detailed diff showing the changes between two versions,
    including trigger changes, added/removed/modified actions and conditions.

    Args:
        workflow_id: Workflow ID.
        from_version: Source version number.
        to_version: Target version number.
        db: Database session.
        account_id: Account ID from auth.

    Returns:
        Version comparison with detailed diff.

    Raises:
        404: If either version not found.
    """
    use_case = CompareVersionsUseCase(db)
    try:
        return await use_case.execute(
            workflow_id=workflow_id,
            account_id=account_id,
            from_version=from_version,
            to_version=to_version,
        )
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": str(e)},
            )
        raise


@router.post("/{version_id}/publish", response_model=PublishVersionResponseDTO)
async def publish_workflow_version(
    workflow_id: UUID,
    version_id: UUID,
    dto: PublishVersionDTO,
    db: Annotated[AsyncSession, Depends(get_db)],
    account_id: Annotated[UUID, Depends(get_account_id)],
    user_id: Annotated[UUID, Depends(get_user_id)],
) -> PublishVersionResponseDTO:
    """Publish a workflow version.

    Activates a draft version, deactivating the current version.
    Optionally creates a migration for existing executions.

    Args:
        workflow_id: Workflow ID.
        version_id: Version ID to publish.
        dto: Publish version request data.
        db: Database session.
        account_id: Account ID from auth.
        user_id: User ID from auth.

    Returns:
        Published version with migration info.

    Raises:
        404: If version not found.
        400: If version cannot be published.
    """
    use_case = PublishVersionUseCase(db)
    try:
        return await use_case.execute(
            workflow_id=workflow_id,
            version_id=version_id,
            account_id=account_id,
            user_id=user_id,
            dto=dto,
        )
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": str(e)},
            )
        if "cannot transition" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_STATUS_TRANSITION", "message": str(e)},
            )
        raise


@router.post("/{version_id}/rollback", response_model=RollbackVersionResponseDTO)
async def rollback_workflow_version(
    workflow_id: UUID,
    version_id: UUID,
    dto: RollbackVersionDTO,
    db: Annotated[AsyncSession, Depends(get_db)],
    account_id: Annotated[UUID, Depends(get_account_id)],
    user_id: Annotated[UUID, Depends(get_user_id)],
) -> RollbackVersionResponseDTO:
    """Rollback to a previous workflow version.

    Restores a previous version as the current active version.
    New enrollments will use the rolled back version.

    Args:
        workflow_id: Workflow ID.
        version_id: Version ID to rollback to.
        dto: Rollback request (empty).
        db: Database session.
        account_id: Account ID from auth.
        user_id: User ID from auth.

    Returns:
        Rolled back version with rollback info.

    Raises:
        404: If version not found.
        400: If version cannot be activated.
    """
    use_case = RollbackVersionUseCase(db)
    try:
        return await use_case.execute(
            workflow_id=workflow_id,
            version_id=version_id,
            account_id=account_id,
            user_id=user_id,
        )
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": str(e)},
            )
        if "cannot transition" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_STATUS_TRANSITION", "message": str(e)},
            )
        raise


@router.post("/{version_id}/migrate", response_model=MigrationResponseDTO, status_code=status.HTTP_202_ACCEPTED)
async def migrate_workflow_executions(
    workflow_id: UUID,
    version_id: UUID,
    dto: MigrateExecutionsDTO,
    db: Annotated[AsyncSession, Depends(get_db)],
    account_id: Annotated[UUID, Depends(get_account_id)],
    user_id: Annotated[UUID, Depends(get_user_id)],
) -> MigrationResponseDTO:
    """Migrate executions between workflow versions.

    Initiates a migration of contact executions from the source
    version to the target version.

    Args:
        workflow_id: Workflow ID.
        version_id: Target version ID.
        dto: Migration request data.
        db: Database session.
        account_id: Account ID from auth.
        user_id: User ID from auth.

    Returns:
        Migration confirmation with migration ID.

    Raises:
        404: If version not found.
    """
    use_case = MigrateExecutionsUseCase(db)
    try:
        return await use_case.execute(
            workflow_id=workflow_id,
            target_version_id=version_id,
            account_id=account_id,
            user_id=user_id,
            source_version=dto.source_version,
            contact_ids=dto.contact_ids,
            mapping_rules=dto.mapping_rules,
            batch_size=dto.batch_size,
        )
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": str(e)},
            )
        raise
