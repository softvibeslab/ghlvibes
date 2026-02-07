"""
Database models for Workflow Analytics infrastructure.

SQLAlchemy ORM models for analytics data persistence.
"""

from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Date,
    Numeric,
    ForeignKey,
    Index,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID, UUID as PG_UUID
from sqlalchemy.orm import relationship
from uuid import uuid4

from src.core.database import Base


class WorkflowAnalyticsModel(Base):
    """
    ORM model for daily aggregated workflow analytics.

    Stores pre-aggregated metrics for efficient querying.
    """

    __tablename__ = "workflow_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False, index=True)

    # Time period
    date = Column(Date, nullable=False, index=True)

    # Enrollment metrics
    total_enrolled = Column(Integer, nullable=False, default=0)
    new_enrollments = Column(Integer, nullable=False, default=0)
    currently_active = Column(Integer, nullable=False, default=0)

    # Completion metrics
    completed = Column(Integer, nullable=False, default=0)
    completion_rate = Column(Numeric(5, 2), nullable=False, default=0)
    average_duration_seconds = Column(Integer, nullable=False, default=0)

    # Conversion metrics
    goals_achieved = Column(Integer, nullable=False, default=0)
    conversion_rate = Column(Numeric(5, 2), nullable=False, default=0)

    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes for efficient querying
    __table_args__ = (
        Index("ix_workflow_analytics_workflow_date", "workflow_id", "date"),
        Index("ix_workflow_analytics_date", "date"),
    )

    def to_domain(self):
        """Convert ORM model to domain entity."""
        from src.workflows.domain.analytics import WorkflowAnalytics, TimeRange, EnrollmentMetrics, CompletionMetrics, ConversionMetrics

        return WorkflowAnalytics(
            id=self.id,
            workflow_id=self.workflow_id,
            time_range=TimeRange(
                start_date=self.date,
                end_date=self.date,
            ),
            enrollment_metrics=EnrollmentMetrics(
                total_enrolled=self.total_enrolled,
                currently_active=self.currently_active,
                new_enrollments=self.new_enrollments,
                enrollment_sources={},  # Would need separate table
                enrollment_rate=Decimal('0.00'),  # Would need calculation
            ),
            completion_metrics=CompletionMetrics(
                completed=self.completed,
                completion_rate=self.completion_rate,
                average_duration_seconds=self.average_duration_seconds,
                exit_reasons={},  # Would need separate table
            ),
            conversion_metrics=ConversionMetrics(
                goals_achieved=self.goals_achieved,
                conversion_rate=self.conversion_rate,
                average_time_to_conversion_seconds=0,  # Would need calculation
                goal_breakdown={},  # Would need separate table
            ),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class WorkflowStepMetricsModel(Base):
    """
    ORM model for workflow step-level metrics.

    Tracks performance data for each step in the workflow funnel.
    """

    __tablename__ = "workflow_step_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False, index=True)
    step_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Time period
    date = Column(Date, nullable=False, index=True)

    # Step performance
    entered = Column(Integer, nullable=False, default=0)
    completed = Column(Integer, nullable=False, default=0)
    dropped_off = Column(Integer, nullable=False, default=0)
    step_conversion_rate = Column(Numeric(5, 2), nullable=False, default=0)
    average_time_in_step_seconds = Column(Integer, nullable=False, default=0)

    # Action performance (if action step)
    executions = Column(Integer, nullable=False, default=0)
    successes = Column(Integer, nullable=False, default=0)
    failures = Column(Integer, nullable=False, default=0)

    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("ix_workflow_step_metrics_workflow_date", "workflow_id", "date"),
        Index("ix_workflow_step_metrics_step_date", "step_id", "date"),
    )


class WorkflowExecutionModel(Base):
    """
    ORM model for individual workflow execution tracking.

    Stores real-time execution data for analytics aggregation.
    """

    __tablename__ = "workflow_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False, index=True)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False, index=True)

    # Status tracking
    status = Column(
        SQLEnum("active", "completed", "goal_achieved", "exited", "error", name="execution_status"),
        nullable=False,
        default="active",
        index=True,
    )
    current_step_id = Column(UUID(as_uuid=True), nullable=True)

    # Timestamps
    enrolled_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    goal_achieved_at = Column(DateTime(timezone=True), nullable=True)

    # Source and exit tracking
    enrollment_source = Column(
        SQLEnum("trigger", "bulk", "api", "manual", name="enrollment_source"),
        nullable=False,
        default="manual",
    )
    exit_reason = Column(String(255), nullable=True)

    # Step progress (JSON)
    steps_entered = Column(JSON, nullable=False, default=list)
    steps_completed = Column(JSON, nullable=False, default=list)
    step_times = Column(JSON, nullable=False, default=dict)  # {step_id: seconds}

    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("ix_workflow_executions_workflow_enrolled", "workflow_id", "enrolled_at"),
        Index("ix_workflow_executions_contact_workflow", "contact_id", "workflow_id"),
    )
