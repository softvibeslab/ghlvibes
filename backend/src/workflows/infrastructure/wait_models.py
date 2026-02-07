"""SQLAlchemy models for wait step executions.

These models define the database schema for storing wait step
executions and event listeners in workflow automation.
"""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.workflows.domain.wait_entities import (
    EventType,
    TimeUnit,
    WaitExecutionStatus,
    WaitType,
)


class WaitExecutionModel(Base):
    """SQLAlchemy model for wait step executions.

    This model represents the database schema for storing
    wait step execution state and configuration.
    """

    __tablename__ = "workflow_wait_executions"

    # Primary key
    id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
    )

    # Foreign keys
    workflow_execution_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workflow_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workflow_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    contact_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    account_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Wait configuration
    step_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    wait_type: Mapped[WaitType] = mapped_column(
        Enum(WaitType, name="wait_type", create_constraint=True),
        nullable=False,
    )
    wait_config: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    # Scheduling
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    timezone: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="UTC",
        server_default="UTC",
    )

    # Event waiting
    event_type: Mapped[EventType | None] = mapped_column(
        Enum(EventType, name="event_type", create_constraint=True),
        nullable=True,
    )
    event_correlation_id: Mapped[PG_UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )
    event_timeout_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    # Status tracking
    status: Mapped[WaitExecutionStatus] = mapped_column(
        Enum(WaitExecutionStatus, name="wait_execution_status", create_constraint=True),
        nullable=False,
        default=WaitExecutionStatus.WAITING,
        server_default="waiting",
        index=True,
    )
    resumed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    resumed_by: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
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

    # Relationships
    execution: Mapped["WorkflowExecutionModel"] = relationship(
        "WorkflowExecutionModel",
        backref="wait_executions",
        lazy="selectin",
    )
    event_listeners: Mapped[list["EventListenerModel"]] = relationship(
        "EventListenerModel",
        back_populates="wait_execution",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # Table constraints
    __table_args__ = (
        # Unique constraint on execution and step
        Index(
            "uq_wait_execution_step",
            "workflow_execution_id",
            "step_id",
            unique=True,
        ),
        # Indexes for scheduled job processing
        Index(
            "ix_wait_executions_scheduled",
            "scheduled_at",
            postgresql_where="status = 'scheduled'",
        ),
        # Index for event listener lookup
        Index(
            "ix_wait_executions_event",
            "event_type",
            "event_correlation_id",
            postgresql_where="status = 'waiting'",
        ),
        # Check constraint on resumed_by values
        CheckConstraint(
            "resumed_by IN ('scheduler', 'event', 'timeout', 'manual', 'cancelled') OR resumed_by IS NULL",
            name="ck_wait_resumed_by_valid",
        ),
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"<WaitExecution(id={self.id}, workflow_execution_id={self.workflow_execution_id}, "
            f"step_id={self.step_id}, wait_type={self.wait_type}, status={self.status})>"
        )


class EventListenerModel(Base):
    """SQLAlchemy model for event listeners.

    This model represents the database schema for storing
    event listener registrations for wait steps.
    """

    __tablename__ = "workflow_event_listeners"

    # Primary key
    id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
    )

    # Foreign key
    wait_execution_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workflow_wait_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Event configuration
    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType, name="listener_event_type", create_constraint=True),
        nullable=False,
    )
    correlation_id: Mapped[PG_UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )
    contact_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workflow_execution_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workflow_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Matching criteria
    match_criteria: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    # Timeout
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
        server_default="active",
        index=True,
    )
    matched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    matched_event_id: Mapped[PG_UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    # Relationships
    wait_execution: Mapped["WaitExecutionModel"] = relationship(
        "WaitExecutionModel",
        back_populates="event_listeners",
        lazy="selectin",
    )

    # Table constraints
    __table_args__ = (
        # Unique constraint on wait execution and event type
        Index(
            "uq_event_listener",
            "wait_execution_id",
            "event_type",
            unique=True,
        ),
        # Index for active listener lookup
        Index(
            "ix_event_listeners_lookup",
            "event_type",
            "contact_id",
            postgresql_where="status = 'active'",
        ),
        # Index for expiration cleanup
        Index(
            "ix_event_listeners_expires",
            "expires_at",
            postgresql_where="status = 'active'",
        ),
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"<EventListener(id={self.id}, wait_execution_id={self.wait_execution_id}, "
            f"event_type={self.event_type}, status={self.status})>"
        )
