"""SQLAlchemy models for workflow actions.

These models define the database schema for workflow actions
and their execution records.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ActionModel(Base):
    """SQLAlchemy model for workflow actions.

    This model represents the database schema for storing workflow action data.
    """

    __tablename__ = "workflow_actions"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys
    workflow_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Core fields
    action_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    action_config: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    # Position and linking
    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    previous_action_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workflow_actions.id", ondelete="SET NULL"),
        nullable=True,
    )
    next_action_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workflow_actions.id", ondelete="SET NULL"),
        nullable=True,
    )
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        comment="Branch ID if action is in a conditional branch",
    )

    # Status
    is_enabled: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
        server_default="true",
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

    # Table constraints
    __table_args__ = (
        # Valid action types constraint
        CheckConstraint(
            "action_type IN ("
            "'send_email', 'send_sms', 'send_voicemail', 'send_messenger', 'make_call',"
            "'create_contact', 'update_contact', 'add_tag', 'remove_tag',"
            "'add_to_campaign', 'remove_from_campaign', 'move_pipeline_stage',"
            "'assign_to_user', 'create_task', 'add_note',"
            "'wait_time', 'wait_until_date', 'wait_for_event',"
            "'send_notification', 'create_opportunity', 'webhook_call', 'custom_code',"
            "'grant_course_access', 'revoke_course_access'"
            ")",
            name="ck_action_type",
        ),
        # Position must be positive
        CheckConstraint(
            "position >= 0",
            name="ck_action_position",
        ),
        # Indexes
        Index("ix_action_workflow_position", "workflow_id", "position"),
        Index("ix_action_type", "action_type"),
        Index("ix_action_enabled", "workflow_id", "is_enabled"),
        Index("ix_action_previous", "previous_action_id"),
        Index("ix_action_next", "next_action_id"),
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<ActionModel(id={self.id}, type={self.action_type}, pos={self.position})>"


class ActionExecutionModel(Base):
    """SQLAlchemy model for action execution records.

    This model tracks the execution of actions for specific contacts,
    including status, timing, and results.
    """

    __tablename__ = "workflow_action_executions"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys
    workflow_execution_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workflow_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workflow_actions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    contact_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Execution status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending",
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
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    # Execution data
    execution_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )
    result_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    # Table constraints
    __table_args__ = (
        # Valid status values
        CheckConstraint(
            "status IN ('pending', 'scheduled', 'running', 'completed', 'failed', 'skipped', 'waiting')",
            name="ck_execution_status",
        ),
        # Retry count must be non-negative
        CheckConstraint(
            "retry_count >= 0",
            name="ck_execution_retry_count",
        ),
        # Indexes
        Index("ix_execution_workflow", "workflow_execution_id"),
        Index("ix_execution_contact", "contact_id"),
        Index("ix_execution_status", "status"),
        Index("ix_execution_action_status", "action_id", "status"),
        # Partial index for scheduled executions
        Index(
            "ix_execution_scheduled",
            "scheduled_at",
            postgresql_where="status = 'scheduled'",
        ),
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"<ActionExecutionModel(id={self.id}, action_id={self.action_id}, "
            f"status={self.status})>"
        )


# Stub for workflow_executions table (will be created in SPEC-WFL-005)
class WorkflowExecutionModel(Base):
    """Stub model for workflow executions.

    This is a placeholder for the full workflow execution model
    that will be implemented in SPEC-WFL-005 (Execute Workflow).
    """

    __tablename__ = "workflow_executions"

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
    contact_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="running",
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<WorkflowExecutionModel(id={self.id}, workflow_id={self.workflow_id})>"


# Stub for contacts table (will be created in contacts module)
class ContactModel(Base):
    """Stub model for contacts.

    This is a placeholder for the full contact model
    that will be implemented in the contacts module.
    """

    __tablename__ = "contacts"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<ContactModel(id={self.id}, email={self.email})>"
