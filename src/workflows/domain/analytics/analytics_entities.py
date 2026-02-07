"""
Domain entities for Workflow Analytics.

This module defines the core domain entities for workflow analytics,
following Domain-Driven Design (DDD) principles.

Entities are objects with identity and lifecycle, distinct from value
objects which are identified by their attributes.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from .analytics_value_objects import (
    EnrollmentMetrics,
    CompletionMetrics,
    ConversionMetrics,
    FunnelStepData,
    TimeRange,
)


@dataclass
class WorkflowAnalytics:
    """
    Aggregate root for workflow analytics.

    Contains all analytics data for a workflow within a specific time range.
    This is the main entry point for workflow analytics queries.

    Attributes:
        id: Unique identifier for this analytics snapshot
        workflow_id: Associated workflow identifier
        time_range: Time period for this analytics data
        enrollment_metrics: Enrollment tracking data
        completion_metrics: Completion tracking data
        conversion_metrics: Goal conversion data
        created_at: When this analytics was computed
        updated_at: When this analytics was last updated
    """

    id: UUID = field(default_factory=uuid4)
    workflow_id: UUID = field(default_factory=uuid4)
    time_range: TimeRange = field(default_factory=lambda: TimeRange(
        start_date=date.today(),
        end_date=date.today()
    ))
    enrollment_metrics: Optional[EnrollmentMetrics] = None
    completion_metrics: Optional[CompletionMetrics] = None
    conversion_metrics: Optional[ConversionMetrics] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def calculate_oververage_conversion_rate(self) -> Decimal:
        """
        Calculate overall conversion rate across the time period.

        Returns:
            Conversion rate as percentage (0-100)
        """
        if not self.enrollment_metrics or not self.conversion_metrics:
            return Decimal('0.00')

        if self.enrollment_metrics.total_enrolled == 0:
            return Decimal('0.00')

        return (
            Decimal(self.conversion_metrics.goals_achieved) /
            Decimal(self.enrollment_metrics.total_enrolled) * 100
        ).quantize(Decimal('0.01'))

    def calculate_overall_completion_rate(self) -> Decimal:
        """
        Calculate overall completion rate across the time period.

        Returns:
            Completion rate as percentage (0-100)
        """
        if not self.enrollment_metrics or not self.completion_metrics:
            return Decimal('0.00')

        if self.enrollment_metrics.total_enrolled == 0:
            return Decimal('0.00')

        return (
            Decimal(self.completion_metrics.completed) /
            Decimal(self.enrollment_metrics.total_enrolled) * 100
        ).quantize(Decimal('0.01'))


@dataclass
class WorkflowFunnelMetrics:
    """
    Funnel analysis metrics for workflow performance.

    Tracks conversion rates through each step of the workflow,
    identifying drop-off points and bottlenecks.

    Attributes:
        id: Unique identifier
        workflow_id: Associated workflow
        time_range: Analysis time period
        funnel_steps: Step-by-step conversion data
        overall_conversion_rate: Total conversion from start to finish
        bottleneck_steps: Steps with highest drop-off rates
        created_at: When analysis was performed
    """

    id: UUID = field(default_factory=uuid4)
    workflow_id: UUID = field(default_factory=uuid4)
    time_range: TimeRange = field(default_factory=lambda: TimeRange(
        start_date=date.today(),
        end_date=date.today()
    ))
    funnel_steps: List[FunnelStepData] = field(default_factory=list)
    overall_conversion_rate: Decimal = Decimal('0.00')
    bottleneck_steps: List[UUID] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def identify_bottlenecks(self, threshold: Decimal = Decimal('20.0')) -> List[UUID]:
        """
        Identify steps with drop-off rates above threshold.

        Args:
            threshold: Drop-off percentage threshold (default: 20%)

        Returns:
            List of step IDs with high drop-off rates
        """
        bottlenecks = []
        for step in self.funnel_steps:
            drop_off_rate = Decimal('100') - step.step_conversion_rate
            if drop_off_rate > threshold:
                bottlenecks.append(step.step_id)

        self.bottleneck_steps = bottlenecks
        return bottlenecks

    def calculate_step_conversion_rates(self) -> None:
        """
        Calculate conversion rates for all funnel steps.

        Updates step_conversion_rate for each step based on
        entered and completed counts.
        """
        for step in self.funnel_steps:
            if step.entered == 0:
                step.step_conversion_rate = Decimal('0.00')
            else:
                rate = (
                    Decimal(step.completed) / Decimal(step.entered) * 100
                ).quantize(Decimal('0.01'))
                step.step_conversion_rate = rate


@dataclass
class WorkflowActionMetrics:
    """
    Performance metrics for individual workflow actions.

    Tracks execution counts, success rates, and timing data
    for each action in a workflow.

    Attributes:
        id: Unique identifier
        workflow_id: Associated workflow
        action_id: Specific action being measured
        action_type: Type of action (send_email, wait, etc.)
        action_name: Human-readable action name
        time_range: Measurement time period
        execution_count: Total times action was executed
        success_count: Successful executions
        failure_count: Failed executions
        success_rate: Success percentage
        error_rate: Error percentage
        average_duration_ms: Average execution time in milliseconds
        created_at: When metrics were collected
    """

    id: UUID = field(default_factory=uuid4)
    workflow_id: UUID = field(default_factory=uuid4)
    action_id: UUID = field(default_factory=uuid4)
    action_type: str = ""
    action_name: str = ""
    time_range: TimeRange = field(default_factory=lambda: TimeRange(
        start_date=date.today(),
        end_date=date.today()
    ))
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    success_rate: Decimal = Decimal('0.00')
    error_rate: Decimal = Decimal('0.00')
    average_duration_ms: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def calculate_rates(self) -> None:
        """Calculate success and error rates from execution counts."""
        if self.execution_count == 0:
            self.success_rate = Decimal('0.00')
            self.error_rate = Decimal('0.00')
        else:
            self.success_rate = (
                Decimal(self.success_count) / Decimal(self.execution_count) * 100
            ).quantize(Decimal('0.01'))

            self.error_rate = (
                Decimal(self.failure_count) / Decimal(self.execution_count) * 100
            ).quantize(Decimal('0.01'))

    def add_execution(self, success: bool, duration_ms: int) -> None:
        """
        Record a single action execution.

        Args:
            success: Whether execution succeeded
            duration_ms: Execution duration in milliseconds
        """
        self.execution_count += 1

        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

        # Update moving average
        if self.average_duration_ms == 0:
            self.average_duration_ms = duration_ms
        else:
            # Simple moving average
            self.average_duration_ms = (
                (self.average_duration_ms * (self.execution_count - 1) + duration_ms) //
                self.execution_count
            )

        self.calculate_rates()


@dataclass
class MetricsSnapshot:
    """
    Time-series snapshot of metrics at a specific point in time.

    Used for tracking metrics trends over time and generating
    performance graphs.

    Attributes:
        id: Unique identifier
        workflow_id: Associated workflow
        snapshot_date: Date of snapshot
        snapshot_timestamp: Exact timestamp when snapshot was taken
        metrics_data: JSON-serialized metrics data
        created_at: When snapshot was created
    """

    id: UUID = field(default_factory=uuid4)
    workflow_id: UUID = field(default_factory=uuid4)
    snapshot_date: date = field(default_factory=date.today)
    snapshot_timestamp: datetime = field(default_factory=datetime.utcnow)
    metrics_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary for serialization."""
        return {
            'workflow_id': str(self.workflow_id),
            'snapshot_date': self.snapshot_date.isoformat(),
            'snapshot_timestamp': self.snapshot_timestamp.isoformat(),
            'metrics_data': self.metrics_data,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetricsSnapshot':
        """Create snapshot from dictionary."""
        return cls(
            workflow_id=UUID(data['workflow_id']),
            snapshot_date=date.fromisoformat(data['snapshot_date']),
            snapshot_timestamp=datetime.fromisoformat(data['snapshot_timestamp']),
            metrics_data=data['metrics_data'],
        )
