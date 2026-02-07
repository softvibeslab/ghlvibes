"""SQLAlchemy models for the workflow module.

These models define the database schema for workflows and related entities.
They are separate from domain entities to maintain clean architecture.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.workflows.domain.value_objects import WorkflowStatus


class AccountModel(Base):
    """Account model (stub for foreign key reference).

    This is a minimal stub for the accounts table.
    The full implementation will be in the accounts module.
    """

    __tablename__ = "accounts"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    workflows: Mapped[list["WorkflowModel"]] = relationship(
        "WorkflowModel",
        back_populates="account",
        lazy="selectin",
    )


class UserModel(Base):
    """User model (stub for foreign key reference).

    This is a minimal stub for the users table.
    The full implementation will be in the auth module.
    """

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )


class WorkflowModel(Base):
    """SQLAlchemy model for workflows.

    This model represents the database schema for storing workflow data.
    It includes all fields, constraints, and indexes for optimal performance.
    """

    __tablename__ = "workflows"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Core fields
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

    # Status with enum
    status: Mapped[WorkflowStatus] = mapped_column(
        Enum(WorkflowStatus, name="workflow_status", create_constraint=True),
        nullable=False,
        default=WorkflowStatus.DRAFT,
        server_default="draft",
    )

    # Version for optimistic locking
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Audit fields
    created_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    updated_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    account: Mapped["AccountModel"] = relationship(
        "AccountModel",
        back_populates="workflows",
        lazy="selectin",
    )
    trigger: Mapped["TriggerModel"] = relationship(
        "TriggerModel",
        back_populates="workflow",
        lazy="selectin",
        uselist=False,  # One-to-one relationship
        cascade="all, delete-orphan",
    )
    audit_logs: Mapped[list["WorkflowAuditLog"]] = relationship(
        "WorkflowAuditLog",
        back_populates="workflow",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # Table constraints
    __table_args__ = (
        # Unique constraint on name within account (excluding deleted)
        # Note: For partial unique constraints, use CheckConstraint instead
        # and enforce uniqueness at application level
        CheckConstraint(
            "length(name) >= 3 AND length(name) <= 100",
            name="ck_workflow_name_length",
        ),
        # Indexes for common queries
        Index("ix_workflow_account_status", "account_id", "status"),
        Index("ix_workflow_created_at", "created_at"),
        Index("ix_workflow_trigger_type", "trigger_type"),
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Workflow(id={self.id}, name={self.name}, status={self.status})>"


class WorkflowAuditLog(Base):
    """Audit log for tracking workflow changes.

    This table records all modifications to workflows for
    compliance and debugging purposes.
    """

    __tablename__ = "workflow_audit_logs"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    workflow_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    old_values: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    new_values: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    changed_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(45),  # IPv6 max length
        nullable=True,
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Relationships
    workflow: Mapped["WorkflowModel"] = relationship(
        "WorkflowModel",
        back_populates="audit_logs",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_audit_workflow_changed_at", "workflow_id", "changed_at"),
        Index("ix_audit_action", "action"),
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"<WorkflowAuditLog(id={self.id}, workflow_id={self.workflow_id}, "
            f"action={self.action})>"
        )
