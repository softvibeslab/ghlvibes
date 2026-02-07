"""Database models for workflow analytics.

SQLAlchemy ORM models for analytics data persistence.
These models map to database tables for time-series metrics storage.
"""

from datetime import UTC, datetime
from datetime import date as Date
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Column,
    Computed,
    Date,
    DateTime,
    Enum,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase

from src.workflows.domain.analytics_exceptions import AnalyticsError


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class WorkflowAnalyticsModel(Base):
    """Daily aggregated workflow analytics.

    Stores time-series metrics for workflow performance.
    Indexed for efficient date-range queries.
    """

    __tablename__ = "workflow_analytics"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    workflow_id = Column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Reference to workflow",
    )
    account_id = Column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Account/tenant identifier",
    )
    date = Column(
        Date,
        nullable=False,
        index=True,
        comment="Aggregation date",
    )

    # Enrollment metrics
    total_enrolled = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Total enrollments at snapshot time",
    )
    new_enrollments = Column(
        Integer,
        nullable=False,
        default=0,
        comment="New enrollments on this date",
    )
    currently_active = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Contacts currently in workflow",
    )
    enrollment_sources = Column(
        JSON,
        nullable=False,
        default=dict,
        comment="Breakdown of enrollments by source",
    )

    # Completion metrics
    completed = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Total completions at snapshot time",
    )
    completion_rate = Column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0"),
        comment="Completion percentage",
    )
    average_duration_seconds = Column(
        Integer,
        nullable=True,
        comment="Average time from enrollment to completion",
    )
    exit_reasons = Column(
        JSON,
        nullable=False,
        default=dict,
        comment="Distribution of exit reasons",
    )

    # Conversion metrics
    goals_achieved = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Total goal achievements at snapshot time",
    )
    conversion_rate = Column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0"),
        comment="Conversion percentage",
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        comment="Record creation time",
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        comment="Last update time",
    )

    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint(
            "workflow_id",
            "date",
            name="uq_workflow_analytics_workflow_date",
        ),
        Index(
            "ix_workflow_analytics_workflow_date",
            "workflow_id",
            "date",
        ),
        Index(
            "ix_workflow_analytics_account_workflow",
            "account_id",
            "workflow_id",
        ),
    )

    def to_domain(self) -> Any:
        """Convert to domain entity.

        Returns:
            WorkflowAnalytics domain entity.
        """
        from src.workflows.domain.analytics_entities import WorkflowAnalytics

        return WorkflowAnalytics(
            id=self.id,
            workflow_id=self.workflow_id,
            account_id=self.account_id,
            total_enrolled=self.total_enrolled,
            currently_active=self.currently_active,
            completed=self.completed,
            goals_achieved=self.goals_achieved,
            enrollment_sources=self.enrollment_sources,
            exit_reasons=self.exit_reasons,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class WorkflowStepMetricsModel(Base):
    """Workflow step performance metrics.

    Stores step-level metrics for funnel analysis.
    Tracks entry, completion, and drop-off for each step.
    """

    __tablename__ = "workflow_step_metrics"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    workflow_id = Column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Reference to workflow",
    )
    step_id = Column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Reference to workflow step",
    )
    step_name = Column(
        String(255),
        nullable=False,
        comment="Human-readable step name",
    )
    step_order = Column(
        Integer,
        nullable=False,
        comment="Position in workflow sequence",
    )
    date = Column(
        Date,
        nullable=False,
        index=True,
        comment="Aggregation date",
    )

    # Step metrics
    entered = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Contacts who entered this step",
    )
    completed = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Contacts who completed this step",
    )
    dropped_off = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Contacts who exited at this step",
    )
    step_conversion_rate = Column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0"),
        comment="Step conversion percentage",
    )
    average_time_in_step_seconds = Column(
        Integer,
        nullable=True,
        comment="Average time spent in step",
    )

    # Action execution metrics (for action steps)
    executions = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of action executions",
    )
    successes = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Successful executions",
    )
    failures = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Failed executions",
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint(
            "workflow_id",
            "step_id",
            "date",
            name="uq_workflow_step_metrics_workflow_step_date",
        ),
        Index(
            "ix_workflow_step_metrics_workflow_date",
            "workflow_id",
            "date",
        ),
        Index(
            "ix_workflow_step_metrics_workflow_order",
            "workflow_id",
            "step_order",
        ),
    )

    def to_domain(self) -> Any:
        """Convert to domain entity.

        Returns:
            WorkflowStepMetrics domain entity.
        """
        from src.workflows.domain.analytics_entities import WorkflowStepMetrics

        return WorkflowStepMetrics(
            id=self.id,
            workflow_id=self.workflow_id,
            step_id=self.step_id,
            step_name=self.step_name,
            step_order=self.step_order,
            date=self.date,
            entered=self.entered,
            completed=self.completed,
            dropped_off=self.dropped_off,
            step_conversion_rate=self.step_conversion_rate,
            average_time_in_step_seconds=self.average_time_in_step_seconds,
            executions=self.executions,
            successes=self.successes,
            failures=self.failures,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class WorkflowExecutionModel(Base):
    """Workflow execution tracking.

    Tracks individual workflow executions for real-time analytics.
    Provides raw data for aggregation into time-series metrics.
    """

    __tablename__ = "workflow_executions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    workflow_id = Column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Reference to workflow",
    )
    contact_id = Column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Contact identifier",
    )
    account_id = Column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Account/tenant identifier",
    )

    # Status tracking
    status = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Execution status",
    )
    current_step_id = Column(
        PG_UUID(as_uuid=True),
        nullable=True,
        comment="Current step in workflow",
    )

    # Timestamps
    enrolled_at = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="When contact entered workflow",
    )
    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When workflow was completed",
    )
    goal_achieved_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When goal was achieved",
    )

    # Source tracking
    enrollment_source = Column(
        String(50),
        nullable=False,
        comment="How contact entered workflow",
    )
    exit_reason = Column(
        Text,
        nullable=True,
        comment="Reason for workflow exit",
    )

    # Metadata
    metadata = Column(
        JSON,
        nullable=True,
        comment="Additional execution metadata",
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Indexes for querying
    __table_args__ = (
        Index(
            "ix_workflow_executions_workflow_enrolled",
            "workflow_id",
            "enrolled_at",
        ),
        Index(
            "ix_workflow_executions_workflow_status",
            "workflow_id",
            "status",
        ),
        Index(
            "ix_workflow_executions_contact_workflow",
            "contact_id",
            "workflow_id",
        ),
    )
