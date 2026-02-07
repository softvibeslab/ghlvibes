"""SQLAlchemy models for workflow versioning.

These models define the database schema for workflow versions,
migrations, and related entities.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class WorkflowVersionModel(Base):
    """SQLAlchemy model for workflow versions.

    This model represents the database schema for storing workflow
    version data including configuration, status, and metadata.
    """

    __tablename__ = "workflow_versions"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys
    workflow_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Version information
    version_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Workflow configuration at this version
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    trigger_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    trigger_config: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )
    actions: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
    )
    conditions: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
    )

    # Status and metadata
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="draft",
        server_default="draft",
    )
    change_summary: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    is_current: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
        server_default="false",
    )
    active_executions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    created_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Table constraints
    __table_args__ = (
        # Unique constraint on (workflow_id, version_number)
        UniqueConstraint("workflow_id", "version_number", name="uq_workflow_version_number"),
        # Max version limit
        CheckConstraint("version_number >= 1", name="ck_version_number_min"),
        CheckConstraint("version_number <= 1000", name="ck_version_number_max"),
        # Status validation
        CheckConstraint(
            "status IN ('draft', 'active', 'archived')",
            name="ck_version_status",
        ),
        # Active executions cannot be negative
        CheckConstraint("active_executions >= 0", name="ck_active_executions"),
        # Indexes for common queries
        Index("ix_workflow_versions_workflow_id", "workflow_id"),
        Index("ix_workflow_versions_status", "status"),
        Index("ix_workflow_versions_is_current", "is_current"),
        Index("ix_workflow_versions_created_at", "created_at"),
        Index("ix_workflow_versions_active_executions", "active_executions"),
        # Partial index for current versions (only one per workflow)
        Index(
            "ix_workflow_versions_current_unique",
            "workflow_id",
            unique=True,
            postgresql_where="is_current = true",
        ),
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"<WorkflowVersionModel(id={self.id}, workflow_id={self.workflow_id}, "
            f"version_number={self.version_number}, status={self.status})>"
        )


class WorkflowVersionMigrationModel(Base):
    """SQLAlchemy model for workflow version migrations.

    Tracks migrations of executions from one version to another.
    """

    __tablename__ = "workflow_version_migrations"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys
    workflow_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    source_version_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )
    target_version_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )

    # Migration configuration
    strategy: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    mapping_rules: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )
    batch_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=100,
        server_default="100",
    )

    # Migration status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending",
    )
    contacts_total: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    contacts_migrated: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    contacts_failed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    error_log: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
    )

    # Timestamps
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    created_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )

    # Table constraints
    __table_args__ = (
        # Strategy validation
        CheckConstraint(
            "strategy IN ('immediate', 'gradual', 'manual')",
            name="ck_migration_strategy",
        ),
        # Status validation
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed', 'failed', 'cancelled')",
            name="ck_migration_status",
        ),
        # Counts cannot be negative
        CheckConstraint("contacts_total >= 0", name="ck_contacts_total"),
        CheckConstraint("contacts_migrated >= 0", name="ck_contacts_migrated"),
        CheckConstraint("contacts_failed >= 0", name="ck_contacts_failed"),
        # Indexes for common queries
        Index("ix_version_migrations_workflow_id", "workflow_id"),
        Index("ix_version_migrations_status", "status"),
        Index("ix_version_migrations_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"<WorkflowVersionMigrationModel(id={self.id}, workflow_id={self.workflow_id}, "
            f"status={self.status}, contacts_migrated={self.contacts_migrated})>"
        )


class WorkflowVersionDraftModel(Base):
    """SQLAlchemy model for workflow version drafts.

    Stores auto-saved draft data for workflows being edited.
    """

    __tablename__ = "workflow_version_drafts"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys
    workflow_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )

    # Draft data
    draft_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )

    # Timestamps
    last_saved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    # Table constraints
    __table_args__ = (
        # Unique constraint on (workflow_id, user_id) - one draft per user per workflow
        UniqueConstraint("workflow_id", "user_id", name="uq_workflow_version_draft"),
        # Indexes for common queries
        Index("ix_version_drafts_workflow_id", "workflow_id"),
        Index("ix_version_drafts_user_id", "user_id"),
        Index("ix_version_drafts_last_saved_at", "last_saved_at"),
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"<WorkflowVersionDraftModel(id={self.id}, workflow_id={self.workflow_id}, "
            f"user_id={self.user_id})>"
        )


class WorkflowVersionAuditLogModel(Base):
    """SQLAlchemy model for workflow version audit logs.

    Tracks all version-related operations for compliance and debugging.
    """

    __tablename__ = "workflow_version_audit_logs"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys
    workflow_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    version_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        index=True,
    )
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )

    # Audit information
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )
    details: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    # Table constraints
    __table_args__ = (
        # Indexes for common queries
        Index("ix_version_audit_workflow_id", "workflow_id"),
        Index("ix_version_audit_version_id", "version_id"),
        Index("ix_version_audit_action", "action"),
        Index("ix_version_audit_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"<WorkflowVersionAuditLogModel(id={self.id}, workflow_id={self.workflow_id}, "
            f"action={self.action})>"
        )
