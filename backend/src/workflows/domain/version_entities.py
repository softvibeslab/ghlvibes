"""Domain entities for workflow versioning.

Entities represent objects with identity that persists over time.
WorkflowVersion is the aggregate root for version management.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Self
from uuid import UUID, uuid4

from src.workflows.domain.version_exceptions import (
    InvalidVersionStatusError,
    VersionDomainError,
)
from src.workflows.domain.version_value_objects import (
    ChangeSummary,
    VersionNumber,
    VersionStatus,
)


@dataclass
class WorkflowVersion:
    """Workflow version aggregate root entity.

    Represents a specific version of a workflow configuration.
    When a workflow is modified while active, a new version is created
    to preserve the previous state for ongoing executions.

    Attributes:
        id: Unique identifier for the version.
        workflow_id: Workflow this version belongs to.
        account_id: Account/tenant this version belongs to.
        version_number: Sequential version number (value object).
        name: Workflow name at this version.
        description: Workflow description at this version.
        trigger_type: Trigger type configuration.
        trigger_config: Trigger-specific settings (JSON).
        actions: Array of action configurations (JSON).
        conditions: Array of condition configurations (JSON).
        status: Current version status.
        change_summary: Description of changes in this version.
        is_current: Whether this is the currently active version.
        active_executions: Count of active executions on this version.
        created_at: Timestamp when version was created.
        created_by: User who created this version.
        archived_at: Timestamp when version was archived (if applicable).
    """

    id: UUID
    workflow_id: UUID
    account_id: UUID
    version_number: VersionNumber
    name: str
    status: VersionStatus = VersionStatus.DRAFT
    description: str | None = None
    trigger_type: str | None = None
    trigger_config: dict[str, Any] = field(default_factory=dict)
    actions: list[dict[str, Any]] = field(default_factory=list)
    conditions: list[dict[str, Any]] = field(default_factory=list)
    change_summary: ChangeSummary | None = None
    is_current: bool = False
    active_executions: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: UUID | None = None
    archived_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate entity state after initialization."""
        # Ensure version_number is a VersionNumber instance
        if isinstance(self.version_number, int):
            object.__setattr__(self, "version_number", VersionNumber(self.version_number))

        # Ensure change_summary is a ChangeSummary instance if provided
        if self.change_summary is not None and isinstance(self.change_summary, str):
            object.__setattr__(self, "change_summary", ChangeSummary(self.change_summary))

        # Validate active_executions is non-negative
        if self.active_executions < 0:
            raise VersionDomainError("Active executions count cannot be negative")

    @classmethod
    def create(
        cls,
        workflow_id: UUID,
        account_id: UUID,
        version_number: int | VersionNumber,
        name: str,
        created_by: UUID,
        description: str | None = None,
        trigger_type: str | None = None,
        trigger_config: dict[str, Any] | None = None,
        actions: list[dict[str, Any]] | None = None,
        conditions: list[dict[str, Any]] | None = None,
        change_summary: str | ChangeSummary | None = None,
        is_current: bool = False,
    ) -> Self:
        """Factory method to create a new workflow version.

        Args:
            workflow_id: Workflow this version belongs to.
            account_id: Account/tenant this version belongs to.
            version_number: Sequential version number.
            name: Workflow name.
            created_by: User creating this version.
            description: Optional description.
            trigger_type: Optional trigger type.
            trigger_config: Optional trigger configuration.
            actions: Optional action configurations.
            conditions: Optional condition configurations.
            change_summary: Optional change summary.
            is_current: Whether this is the current version.

        Returns:
            A new WorkflowVersion instance in draft status.
        """
        vn = version_number if isinstance(version_number, VersionNumber) else VersionNumber(version_number)
        cs = ChangeSummary(change_summary) if change_summary and isinstance(change_summary, str) else None
        if change_summary and isinstance(change_summary, ChangeSummary):
            cs = change_summary

        now = datetime.now(UTC)

        return cls(
            id=uuid4(),
            workflow_id=workflow_id,
            account_id=account_id,
            version_number=vn,
            name=name,
            status=VersionStatus.DRAFT,
            description=description,
            trigger_type=trigger_type,
            trigger_config=trigger_config or {},
            actions=actions or [],
            conditions=conditions or [],
            change_summary=cs,
            is_current=is_current,
            active_executions=0,
            created_at=now,
            created_by=created_by,
            archived_at=None,
        )

    def publish(self) -> None:
        """Publish the version as active.

        Transitions the version from draft to active status.

        Raises:
            InvalidVersionStatusError: If not in draft status.
        """
        if self.status != VersionStatus.DRAFT:
            raise InvalidVersionStatusError(self.status.value, VersionStatus.ACTIVE.value)

        self.status = VersionStatus.ACTIVE
        self.is_current = True

    def archive(self) -> None:
        """Archive the version.

        Transitions the version from active to archived status.
        Only allowed if no active executions remain.

        Raises:
            InvalidVersionStatusError: If not in active status.
            VersionDomainError: If active executions remain.
        """
        if self.status != VersionStatus.ACTIVE:
            raise InvalidVersionStatusError(self.status.value, VersionStatus.ARCHIVED.value)

        if self.active_executions > 0:
            raise VersionDomainError(
                f"Cannot archive version with {self.active_executions} active executions"
            )

        self.status = VersionStatus.ARCHIVED
        self.is_current = False
        self.archived_at = datetime.now(UTC)

    def deactivate_current(self) -> None:
        """Mark this version as no longer current.

        Used when a newer version becomes active.
        Does not change the status, only the is_current flag.
        """
        self.is_current = False

    def increment_executions(self) -> None:
        """Increment the count of active executions."""
        self.active_executions += 1

    def decrement_executions(self) -> None:
        """Decrement the count of active executions.

        Raises:
            VersionDomainError: If count would become negative.
        """
        if self.active_executions <= 0:
            raise VersionDomainError("Cannot decrement executions below zero")
        self.active_executions -= 1

    @property
    def is_draft(self) -> bool:
        """Check if version is in draft status."""
        return self.status == VersionStatus.DRAFT

    @property
    def is_active(self) -> bool:
        """Check if version is active."""
        return self.status == VersionStatus.ACTIVE

    @property
    def is_archived(self) -> bool:
        """Check if version is archived."""
        return self.status == VersionStatus.ARCHIVED

    @property
    def can_be_published(self) -> bool:
        """Check if version can be published."""
        return self.is_draft

    @property
    def can_be_archived(self) -> bool:
        """Check if version can be archived."""
        return self.is_active and self.active_executions == 0

    def to_dict(self) -> dict[str, Any]:
        """Convert version to dictionary representation.

        Returns:
            Dictionary containing all version attributes.
        """
        return {
            "id": str(self.id),
            "workflow_id": str(self.workflow_id),
            "account_id": str(self.account_id),
            "version_number": self.version_number.value,
            "name": self.name,
            "description": self.description,
            "trigger_type": self.trigger_type,
            "trigger_config": self.trigger_config,
            "actions": self.actions,
            "conditions": self.conditions,
            "status": self.status.value,
            "change_summary": str(self.change_summary) if self.change_summary else None,
            "is_current": self.is_current,
            "active_executions": self.active_executions,
            "created_at": self.created_at.isoformat(),
            "created_by": str(self.created_by) if self.created_by else None,
            "archived_at": self.archived_at.isoformat() if self.archived_at else None,
        }


@dataclass
class VersionDiff:
    """Value object representing differences between workflow versions.

    Provides structured diff information for triggers, actions, and conditions.

    Attributes:
        from_version_number: Source version number.
        to_version_number: Target version number.
        trigger_changed: Whether trigger configuration changed.
        added_actions: Actions added in target version.
        removed_actions: Actions removed from source version.
        modified_actions: Actions modified between versions.
        added_conditions: Conditions added in target version.
        removed_conditions: Conditions removed from source version.
        modified_conditions: Conditions modified between versions.
        total_changes: Total count of all changes.
        breaking_changes: Count of breaking changes.
    """

    from_version_number: int
    to_version_number: int
    trigger_changed: bool = False
    added_actions: list[dict[str, Any]] = field(default_factory=list)
    removed_actions: list[dict[str, Any]] = field(default_factory=list)
    modified_actions: list[dict[str, Any]] = field(default_factory=list)
    added_conditions: list[dict[str, Any]] = field(default_factory=list)
    removed_conditions: list[dict[str, Any]] = field(default_factory=list)
    modified_conditions: list[dict[str, Any]] = field(default_factory=list)
    total_changes: int = 0
    breaking_changes: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert diff to dictionary representation.

        Returns:
            Dictionary containing diff information.
        """
        return {
            "from_version": self.from_version_number,
            "to_version": self.to_version_number,
            "diff": {
                "trigger": {"changed": self.trigger_changed},
                "actions": {
                    "added": self.added_actions,
                    "removed": self.removed_actions,
                    "modified": self.modified_actions,
                },
                "conditions": {
                    "added": self.added_conditions,
                    "removed": self.removed_conditions,
                    "modified": self.modified_conditions,
                },
            },
            "summary": {
                "total_changes": self.total_changes,
                "breaking_changes": self.breaking_changes,
            },
        }


@dataclass
class VersionMigration:
    """Version execution migration entity.

    Represents the migration of workflow executions from one version to another.

    Attributes:
        id: Unique identifier for the migration.
        workflow_id: Workflow being migrated.
        source_version_id: Source version ID.
        target_version_id: Target version ID.
        account_id: Account/tenant this migration belongs to.
        strategy: Migration strategy (immediate, gradual, manual).
        mapping_rules: Action-to-action mapping rules.
        batch_size: Number of contacts per batch.
        status: Current migration status.
        contacts_total: Total contacts to migrate.
        contacts_migrated: Number of contacts successfully migrated.
        contacts_failed: Number of contacts that failed migration.
        error_log: Log of migration errors.
        started_at: Timestamp when migration started.
        completed_at: Timestamp when migration completed.
        created_at: Timestamp when migration was created.
        created_by: User who initiated the migration.
    """

    id: UUID
    workflow_id: UUID
    source_version_id: UUID
    target_version_id: UUID
    account_id: UUID
    strategy: str
    status: str
    mapping_rules: dict[str, Any] = field(default_factory=dict)
    batch_size: int = 100
    contacts_total: int = 0
    contacts_migrated: int = 0
    contacts_failed: int = 0
    error_log: list[dict[str, Any]] = field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: UUID | None = None

    @classmethod
    def create(
        cls,
        workflow_id: UUID,
        source_version_id: UUID,
        target_version_id: UUID,
        account_id: UUID,
        strategy: str,
        created_by: UUID,
        contacts_total: int = 0,
        mapping_rules: dict[str, Any] | None = None,
        batch_size: int = 100,
    ) -> Self:
        """Factory method to create a new version migration.

        Args:
            workflow_id: Workflow being migrated.
            source_version_id: Source version ID.
            target_version_id: Target version ID.
            account_id: Account/tenant this migration belongs to.
            strategy: Migration strategy.
            created_by: User initiating the migration.
            contacts_total: Total contacts to migrate.
            mapping_rules: Optional mapping rules.
            batch_size: Batch size for gradual migration.

        Returns:
            A new VersionMigration instance in pending status.
        """
        now = datetime.now(UTC)

        return cls(
            id=uuid4(),
            workflow_id=workflow_id,
            source_version_id=source_version_id,
            target_version_id=target_version_id,
            account_id=account_id,
            strategy=strategy,
            status="pending",
            mapping_rules=mapping_rules or {},
            batch_size=batch_size,
            contacts_total=contacts_total,
            contacts_migrated=0,
            contacts_failed=0,
            error_log=[],
            started_at=None,
            completed_at=None,
            created_at=now,
            created_by=created_by,
        )

    def start(self) -> None:
        """Mark migration as started."""
        if self.status != "pending":
            raise VersionDomainError(f"Cannot start migration with status '{self.status}'")
        self.status = "in_progress"
        self.started_at = datetime.now(UTC)

    def complete(self) -> None:
        """Mark migration as completed."""
        if self.status != "in_progress":
            raise VersionDomainError(f"Cannot complete migration with status '{self.status}'")
        self.status = "completed"
        self.completed_at = datetime.now(UTC)

    def fail(self, error: dict[str, Any]) -> None:
        """Mark migration as failed.

        Args:
            error: Error details to log.
        """
        self.status = "failed"
        self.completed_at = datetime.now(UTC)
        self.error_log.append(error)

    def cancel(self) -> None:
        """Cancel the migration."""
        if self.status not in ("pending", "in_progress"):
            raise VersionDomainError(f"Cannot cancel migration with status '{self.status}'")
        self.status = "cancelled"
        self.completed_at = datetime.now(UTC)

    def record_success(self, count: int = 1) -> None:
        """Record successful migration of contacts.

        Args:
            count: Number of contacts migrated.
        """
        self.contacts_migrated += count

    def record_failure(self, error: dict[str, Any]) -> None:
        """Record a migration failure.

        Args:
            error: Error details.
        """
        self.contacts_failed += 1
        self.error_log.append(error)

    @property
    def is_pending(self) -> bool:
        """Check if migration is pending."""
        return self.status == "pending"

    @property
    def is_in_progress(self) -> bool:
        """Check if migration is in progress."""
        return self.status == "in_progress"

    @property
    def is_completed(self) -> bool:
        """Check if migration is completed."""
        return self.status == "completed"

    @property
    def is_failed(self) -> bool:
        """Check if migration failed."""
        return self.status == "failed"

    @property
    def is_cancelled(self) -> bool:
        """Check if migration was cancelled."""
        return self.status == "cancelled"

    @property
    def completion_percentage(self) -> float:
        """Calculate migration completion percentage.

        Returns:
            Completion percentage (0-100).
        """
        if self.contacts_total == 0:
            return 0.0
        return (self.contacts_migrated / self.contacts_total) * 100

    @property
    def remaining_contacts(self) -> int:
        """Calculate remaining contacts to migrate.

        Returns:
            Number of contacts remaining.
        """
        return self.contacts_total - self.contacts_migrated

    def to_dict(self) -> dict[str, Any]:
        """Convert migration to dictionary representation.

        Returns:
            Dictionary containing all migration attributes.
        """
        return {
            "id": str(self.id),
            "workflow_id": str(self.workflow_id),
            "source_version_id": str(self.source_version_id),
            "target_version_id": str(self.target_version_id),
            "account_id": str(self.account_id),
            "strategy": self.strategy,
            "status": self.status,
            "mapping_rules": self.mapping_rules,
            "batch_size": self.batch_size,
            "contacts_total": self.contacts_total,
            "contacts_migrated": self.contacts_migrated,
            "contacts_failed": self.contacts_failed,
            "error_log": self.error_log,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat(),
            "created_by": str(self.created_by) if self.created_by else None,
        }
