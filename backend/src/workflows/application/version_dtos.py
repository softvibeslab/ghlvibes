"""DTOs for workflow versioning use cases.

Data Transfer Objects define the input/output contracts
for workflow versioning operations.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# Request DTOs

class CreateVersionDTO(BaseModel):
    """DTO for creating a new workflow version.

    Attributes:
        change_summary: Optional description of changes (max 500 chars).
        publish_immediately: Whether to publish version immediately.
    """

    change_summary: str | None = Field(None, max_length=500, description="Description of changes")
    publish_immediately: bool = Field(False, description="Whether to publish immediately")

    @field_validator("change_summary")
    @classmethod
    def validate_summary(cls, v: str | None) -> str | None:
        """Validate change summary.

        Args:
            v: Change summary value.

        Returns:
            Validated summary or None.
        """
        if v is not None and len(v.strip()) == 0:
            return None
        return v


class PublishVersionDTO(BaseModel):
    """DTO for publishing a workflow version.

    Attributes:
        migration_strategy: Strategy for migrating executions (immediate, gradual, manual).
        batch_size: Batch size for gradual migration.
        notify_on_complete: Whether to send notification on completion.
    """

    migration_strategy: str | None = Field(
        None,
        pattern="^(immediate|gradual|manual)$",
        description="Migration strategy",
    )
    batch_size: int = Field(100, ge=1, le=1000, description="Batch size for gradual migration")
    notify_on_complete: bool = Field(True, description="Send notification on completion")


class RollbackVersionDTO(BaseModel):
    """DTO for rolling back to a previous version.

    Empty DTO - all information comes from path parameters.
    """

    pass


class MigrateExecutionsDTO(BaseModel):
    """DTO for migrating executions between versions.

    Attributes:
        source_version: Source version number.
        contact_ids: Optional specific contacts to migrate.
        mapping_rules: Action-to-action mapping rules.
        batch_size: Batch size for migration.
    """

    source_version: int = Field(..., ge=1, description="Source version number")
    contact_ids: list[UUID] | None = Field(None, description="Specific contacts to migrate")
    mapping_rules: dict[str, Any] = Field(
        default_factory=dict,
        description="Action-to-action mapping rules",
    )
    batch_size: int = Field(100, ge=1, le=1000, description="Batch size for migration")


class CompareVersionsDTO(BaseModel):
    """DTO for comparing two versions.

    All parameters come from query string, so this is empty.
    """

    pass


class SaveDraftDTO(BaseModel):
    """DTO for saving workflow draft.

    Attributes:
        draft_data: Draft data to save.
    """

    draft_data: dict[str, Any] = Field(..., description="Draft workflow data")


# Response DTOs

class VersionResponseDTO(BaseModel):
    """DTO for workflow version response.

    Attributes:
        id: Version ID.
        workflow_id: Workflow ID.
        version_number: Version number.
        name: Workflow name at this version.
        description: Workflow description.
        trigger_type: Trigger type.
        trigger_config: Trigger configuration.
        actions: Action configurations.
        conditions: Condition configurations.
        status: Version status.
        change_summary: Change summary.
        is_current: Whether this is the current version.
        active_executions: Count of active executions.
        created_at: Creation timestamp.
        created_by: User who created version.
        archived_at: Archival timestamp (if applicable).
    """

    id: UUID = Field(..., description="Version ID")
    workflow_id: UUID = Field(..., description="Workflow ID")
    version_number: int = Field(..., description="Version number")
    name: str = Field(..., description="Workflow name")
    description: str | None = Field(None, description="Workflow description")
    trigger_type: str | None = Field(None, description="Trigger type")
    trigger_config: dict[str, Any] = Field(default_factory=dict, description="Trigger configuration")
    actions: list[dict[str, Any]] = Field(default_factory=list, description="Action configurations")
    conditions: list[dict[str, Any]] = Field(default_factory=list, description="Condition configurations")
    status: str = Field(..., description="Version status")
    change_summary: str | None = Field(None, description="Change summary")
    is_current: bool = Field(..., description="Whether this is the current version")
    active_executions: int = Field(..., description="Active execution count")
    created_at: datetime = Field(..., description="Creation timestamp")
    created_by: UUID | None = Field(None, description="Creator user ID")
    archived_at: datetime | None = Field(None, description="Archival timestamp")


class VersionListItemDTO(BaseModel):
    """DTO for workflow version list item.

    Simplified version of VersionResponseDTO for list views.

    Attributes:
        id: Version ID.
        version_number: Version number.
        status: Version status.
        is_current: Whether this is the current version.
        active_executions: Count of active executions.
        change_summary: Change summary.
        created_at: Creation timestamp.
        created_by: Creator information.
    """

    id: UUID = Field(..., description="Version ID")
    version_number: int = Field(..., description="Version number")
    status: str = Field(..., description="Version status")
    is_current: bool = Field(..., description="Whether this is the current version")
    active_executions: int = Field(..., description="Active execution count")
    change_summary: str | None = Field(None, description="Change summary")
    created_at: datetime = Field(..., description="Creation timestamp")
    created_by: UUID | None = Field(None, description="Creator user ID")


class VersionListResponseDTO(BaseModel):
    """DTO for workflow version list response.

    Attributes:
        versions: List of workflow versions.
        pagination: Pagination metadata.
    """

    versions: list[VersionListItemDTO] = Field(default_factory=list, description="List of versions")
    pagination: "PaginationDTO" = Field(..., description="Pagination metadata")


class PaginationDTO(BaseModel):
    """DTO for pagination metadata.

    Attributes:
        total: Total number of items.
        page: Current page number.
        per_page: Items per page.
        total_pages: Total number of pages.
    """

    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")


class PreviousVersionDTO(BaseModel):
    """DTO for previous version reference.

    Attributes:
        id: Version ID.
        version_number: Version number.
        active_executions: Count of active executions.
    """

    id: UUID = Field(..., description="Version ID")
    version_number: int = Field(..., description="Version number")
    active_executions: int = Field(..., description="Active execution count")


class CreateVersionResponseDTO(VersionResponseDTO):
    """DTO for create version response.

    Extends base version response with previous version info.

    Attributes:
        previous_version: Information about previous version.
    """

    previous_version: PreviousVersionDTO | None = Field(None, description="Previous version info")


class VersionDiffDTO(BaseModel):
    """DTO for version diff component.

    Attributes:
        changed: Whether this component changed.
    """

    changed: bool = Field(..., description="Whether this component changed")


class VersionActionDiffDTO(BaseModel):
    """DTO for action diff.

    Attributes:
        added: List of added actions.
        removed: List of removed actions.
        modified: List of modified actions.
    """

    added: list[dict[str, Any]] = Field(default_factory=list, description="Added actions")
    removed: list[dict[str, Any]] = Field(default_factory=list, description="Removed actions")
    modified: list[dict[str, Any]] = Field(default_factory=list, description="Modified actions")


class VersionDiffDetailDTO(BaseModel):
    """DTO for version diff details.

    Attributes:
        trigger: Trigger diff.
        actions: Action diff.
        conditions: Condition diff.
    """

    trigger: VersionDiffDTO = Field(..., description="Trigger diff")
    actions: VersionActionDiffDTO = Field(..., description="Action diff")
    conditions: VersionActionDiffDTO = Field(..., description="Condition diff")


class VersionDiffSummaryDTO(BaseModel):
    """DTO for version diff summary.

    Attributes:
        total_changes: Total number of changes.
        breaking_changes: Number of breaking changes.
    """

    total_changes: int = Field(..., description="Total number of changes")
    breaking_changes: int = Field(..., description="Number of breaking changes")


class CompareVersionsResponseDTO(BaseModel):
    """DTO for version comparison response.

    Attributes:
        from_version: Source version number.
        to_version: Target version number.
        diff: Detailed diff information.
        summary: Summary of changes.
    """

    from_version: int = Field(..., description="Source version number")
    to_version: int = Field(..., description="Target version number")
    diff: VersionDiffDetailDTO = Field(..., description="Detailed diff")
    summary: VersionDiffSummaryDTO = Field(..., description="Summary of changes")


class MigrationInfoDTO(BaseModel):
    """DTO for migration information.

    Attributes:
        status: Migration status.
        strategy: Migration strategy.
        contacts_migrated: Number of contacts migrated.
        contacts_remaining: Number of contacts remaining.
        estimated_completion: Estimated completion timestamp.
    """

    status: str = Field(..., description="Migration status")
    strategy: str = Field(..., description="Migration strategy")
    contacts_migrated: int = Field(..., description="Contacts migrated")
    contacts_remaining: int = Field(..., description="Contacts remaining")
    estimated_completion: datetime | None = Field(None, description="Estimated completion time")


class PublishVersionResponseDTO(VersionResponseDTO):
    """DTO for publish version response.

    Extends base version response with migration info.

    Attributes:
        migration: Migration information.
    """

    migration: MigrationInfoDTO | None = Field(None, description="Migration information")


class RollbackInfoDTO(BaseModel):
    """DTO for rollback information.

    Attributes:
        rolled_back_from: Version number rolled back from.
        rolled_back_at: Rollback timestamp.
        rolled_back_by: User who performed rollback.
    """

    rolled_back_from: int = Field(..., description="Version rolled back from")
    rolled_back_at: datetime = Field(..., description="Rollback timestamp")
    rolled_back_by: UUID = Field(..., description="User who performed rollback")


class RollbackVersionResponseDTO(VersionResponseDTO):
    """DTO for rollback version response.

    Extends base version response with rollback info.

    Attributes:
        rollback_info: Rollback information.
    """

    rollback_info: RollbackInfoDTO = Field(..., description="Rollback information")


class MigrationResponseDTO(BaseModel):
    """DTO for migration response.

    Attributes:
        migration_id: Migration ID.
        status: Migration status.
        contacts_to_migrate: Number of contacts to migrate.
        estimated_duration_minutes: Estimated duration in minutes.
    """

    migration_id: UUID = Field(..., description="Migration ID")
    status: str = Field(..., description="Migration status")
    contacts_to_migrate: int = Field(..., description="Contacts to migrate")
    estimated_duration_minutes: int = Field(..., description="Estimated duration (minutes)")


class DraftDataDTO(BaseModel):
    """DTO for draft data response.

    Attributes:
        draft_data: Draft workflow data.
        last_saved_at: Last save timestamp.
    """

    draft_data: dict[str, Any] = Field(..., description="Draft workflow data")
    last_saved_at: datetime = Field(..., description="Last save timestamp")
