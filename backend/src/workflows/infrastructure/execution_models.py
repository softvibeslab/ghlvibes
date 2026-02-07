"""SQLAlchemy models for workflow execution.

These models define the database schema for workflow execution tracking.
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
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.workflows.domain.execution_entities import ExecutionStatus


class WorkflowExecutionModel(Base):
    """SQLAlchemy model for workflow executions.

    This model represents the database schema for storing
    workflow execution state and tracking information.
    """

    __tablename__ = "workflow_executions"

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
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Execution tracking
    workflow_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    contact_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    status: Mapped[ExecutionStatus] = mapped_column(
        Enum(ExecutionStatus, name="execution_status", create_constraint=True),
        nullable=False,
        default=ExecutionStatus.QUEUED,
        server_default="queued",
        index=True,
    )
    current_step_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    # Timestamps
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
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

    # Error tracking
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

    # Execution metadata
    metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    # Relationships
    workflow: Mapped["WorkflowModel"] = relationship(
        "WorkflowModel",
        backref="executions",
        lazy="selectin",
    )
    logs: Mapped[list["ExecutionLogModel"]] = relationship(
        "ExecutionLogModel",
        back_populates="execution",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # Table constraints
    __table_args__ = (
        # Check constraint on step index
        CheckConstraint(
            "current_step_index >= 0",
            name="ck_execution_step_index_positive",
        ),
        # Check constraint on retry count
        CheckConstraint(
            "retry_count >= 0",
            name="ck_execution_retry_count_positive",
        ),
        # Indexes for common queries
        Index("ix_execution_workflow_status", "workflow_id", "status"),
        Index("ix_execution_account_status", "account_id", "status"),
        Index("ix_execution_contact", "contact_id"),
        Index("ix_execution_created_at", "created_at"),
        # Partial index for active executions
        Index(
            "ix_execution_active",
            "account_id",
            "status",
            postgresql_where="status IN ('queued', 'active', 'waiting')",
        ),
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"<WorkflowExecution(id={self.id}, workflow_id={self.workflow_id}, "
            f"status={self.status}, contact_id={self.contact_id})>"
        )


class ExecutionLogModel(Base):
    """SQLAlchemy model for execution logs.

    This model represents the database schema for storing
    detailed execution logs for each action.
    """

    __tablename__ = "execution_logs"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign key
    execution_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workflow_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Execution details
    step_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )
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
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
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

    # Execution metrics
    duration_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Result data
    error_details: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    response_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    # Relationships
    execution: Mapped["WorkflowExecutionModel"] = relationship(
        "WorkflowExecutionModel",
        back_populates="logs",
        lazy="selectin",
    )

    # Table constraints
    __table_args__ = (
        # Check constraint on step index
        CheckConstraint(
            "step_index >= 0",
            name="ck_execution_log_step_index_positive",
        ),
        # Check constraint on duration
        CheckConstraint(
            "duration_ms >= 0",
            name="ck_execution_log_duration_positive",
        ),
        # Indexes for common queries
        Index("ix_execution_log_execution_step", "execution_id", "step_index"),
        Index("ix_execution_log_status", "status"),
        Index("ix_execution_log_started_at", "started_at"),
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"<ExecutionLog(id={self.id}, execution_id={self.execution_id}, "
            f"step={self.step_index}, action_type={self.action_type}, "
            f"status={self.status})>"
        )
