"""SQLAlchemy models for triggers and trigger execution logs.

These models define the database schema for storing trigger configurations
and logging trigger execution history.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class TriggerModel(Base):
    """SQLAlchemy model for workflow triggers.

    This model represents the database schema for storing trigger configurations.
    Each workflow has exactly one trigger.
    """

    __tablename__ = "workflow_triggers"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign key to workflow
    workflow_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # One trigger per workflow
        index=True,
    )

    # Trigger configuration
    event: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,  # For finding triggers by event type
    )
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,  # For finding triggers by category
    )
    filters: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )
    settings: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
        server_default="true",
        index=True,  # For finding active triggers
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

    # Audit
    created_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    workflow: Mapped["WorkflowModel"] = relationship(
        "WorkflowModel",
        back_populates="trigger",
        lazy="selectin",
    )
    execution_logs: Mapped[list["TriggerExecutionLogModel"]] = relationship(
        "TriggerExecutionLogModel",
        back_populates="trigger",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # Table constraints
    __table_args__ = (
        # Index for finding active triggers by event type
        Index(
            "ix_trigger_active_event",
            "category",
            "event",
            postgresql_where="is_active = True",
        ),
        # Index for event evaluation performance
        Index("ix_trigger_workflow_active", "workflow_id", "is_active"),
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Trigger(id={self.id}, event={self.event}, workflow_id={self.workflow_id})>"


class TriggerExecutionLogModel(Base):
    """Model for logging trigger execution events.

    This table records all trigger evaluation events for debugging,
    analytics, and audit purposes.
    """

    __tablename__ = "trigger_execution_logs"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys
    trigger_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workflow_triggers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    contact_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Event data
    event_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )

    # Evaluation results
    matched: Mapped[bool] = mapped_column(
        nullable=False,
        index=True,
    )
    enrolled: Mapped[bool] = mapped_column(
        nullable=False,
        index=True,
    )
    failure_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Execution timestamp
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        index=True,
    )

    # Relationships
    trigger: Mapped["TriggerModel"] = relationship(
        "TriggerModel",
        back_populates="execution_logs",
        lazy="selectin",
    )

    # Table constraints
    __table_args__ = (
        # Index for querying trigger execution history
        Index("ix_trigger_log_executed_at", "trigger_id", "executed_at"),
        # Index for finding successful enrollments
        Index(
            "ix_trigger_log_enrolled",
            "trigger_id",
            "enrolled",
            postgresql_where="enrolled = True",
        ),
        # Index for finding failed evaluations
        Index(
            "ix_trigger_log_failed",
            "trigger_id",
            "matched",
            postgresql_where="matched = False",
        ),
        # Index for contact trigger history
        Index("ix_trigger_log_contact", "contact_id", "executed_at"),
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"<TriggerExecutionLog(id={self.id}, trigger_id={self.trigger_id}, "
            f"matched={self.matched}, enrolled={self.enrolled})>"
        )
