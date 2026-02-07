"""Domain entities for workflow analytics.

This module defines the core domain entities for workflow analytics,
including the analytics aggregate root and supporting entities.
These entities form the foundation for tracking and analyzing
workflow performance metrics.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from datetime import date as Date
from decimal import Decimal
from typing import Any, Self
from uuid import UUID, uuid4

from src.workflows.domain.analytics_value_objects import (
    CompletionRate,
    ConversionRate,
    EnrollmentSource,
    ExitReason,
    StepConversionRate,
)


@dataclass
class MetricsSnapshot:
    """Point-in-time snapshot of workflow metrics.

    This entity captures analytics metrics at a specific moment,
    used for trend analysis and historical comparisons.

    Attributes:
        id: Unique snapshot identifier.
        workflow_id: Reference to workflow.
        date: Aggregation date for this snapshot.
        total_enrolled: Cumulative enrollments at snapshot time.
        new_enrollments: New enrollments on this date.
        currently_active: Contacts currently in workflow at snapshot time.
        completed: Total completions at snapshot time.
        completion_rate: Completion percentage.
        goals_achieved: Total goal achievements at snapshot time.
        conversion_rate: Conversion percentage.
        average_duration_seconds: Average time from enrollment to completion.
        snapshot_at: Timestamp when snapshot was created.
    """

    id: UUID
    workflow_id: UUID
    date: Date
    total_enrolled: int
    new_enrollments: int
    currently_active: int
    completed: int
    completion_rate: Decimal
    goals_achieved: int
    conversion_rate: Decimal
    average_duration_seconds: int | None = None
    snapshot_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        workflow_id: UUID,
        snapshot_date: Date,
        total_enrolled: int = 0,
        new_enrollments: int = 0,
        currently_active: int = 0,
        completed: int = 0,
        goals_achieved: int = 0,
        average_duration_seconds: int | None = None,
    ) -> Self:
        """Factory method to create a metrics snapshot.

        Args:
            workflow_id: Workflow identifier.
            snapshot_date: Date for this snapshot.
            total_enrolled: Total enrollments.
            new_enrollments: New enrollments on this date.
            currently_active: Currently active contacts.
            completed: Total completions.
            goals_achieved: Total goal achievements.
            average_duration_seconds: Average completion duration.

        Returns:
            A new MetricsSnapshot instance with calculated rates.
        """
        # Calculate rates
        completion_rate = CompletionRate.calculate(completed, total_enrolled)
        conversion_rate = ConversionRate.calculate(goals_achieved, total_enrolled)

        now = datetime.now(UTC)

        return cls(
            id=uuid4(),
            workflow_id=workflow_id,
            date=snapshot_date,
            total_enrolled=total_enrolled,
            new_enrollments=new_enrollments,
            currently_active=currently_active,
            completed=completed,
            completion_rate=completion_rate.value,
            goals_achieved=goals_achieved,
            conversion_rate=conversion_rate.value,
            average_duration_seconds=average_duration_seconds,
            snapshot_at=now,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert snapshot to dictionary representation.

        Returns:
            Dictionary containing all snapshot attributes.
        """
        return {
            "id": str(self.id),
            "workflow_id": str(self.workflow_id),
            "date": self.date.isoformat(),
            "total_enrolled": self.total_enrolled,
            "new_enrollments": self.new_enrollments,
            "currently_active": self.currently_active,
            "completed": self.completed,
            "completion_rate": float(self.completion_rate),
            "goals_achieved": self.goals_achieved,
            "conversion_rate": float(self.conversion_rate),
            "average_duration_seconds": self.average_duration_seconds,
            "snapshot_at": self.snapshot_at.isoformat(),
        }


@dataclass
class WorkflowStepMetrics:
    """Metrics for a single workflow step.

    This entity tracks performance metrics for individual steps
    in a workflow, used for funnel analysis and bottleneck
    identification.

    Attributes:
        id: Unique metrics identifier.
        workflow_id: Reference to workflow.
        step_id: Reference to workflow step.
        step_name: Human-readable step name.
        step_order: Position of step in workflow sequence.
        date: Aggregation date.
        entered: Number of contacts who entered this step.
        completed: Number of contacts who completed this step.
        dropped_off: Number of contacts who exited at this step.
        step_conversion_rate: Conversion rate for this step.
        average_time_in_step_seconds: Average time spent in step.
        executions: Number of action executions (for action steps).
        successes: Number of successful executions.
        failures: Number of failed executions.
        created_at: Record creation time.
        updated_at: Last update time.
    """

    id: UUID
    workflow_id: UUID
    step_id: UUID
    step_name: str
    step_order: int
    date: Date
    entered: int
    completed: int
    dropped_off: int
    step_conversion_rate: Decimal
    average_time_in_step_seconds: int | None = None
    executions: int = 0
    successes: int = 0
    failures: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        workflow_id: UUID,
        step_id: UUID,
        step_name: str,
        step_order: int,
        metrics_date: Date,
        entered: int = 0,
        completed: int = 0,
        average_time_in_step_seconds: int | None = None,
    ) -> Self:
        """Factory method to create step metrics.

        Args:
            workflow_id: Workflow identifier.
            step_id: Step identifier.
            step_name: Human-readable step name.
            step_order: Step position in workflow.
            metrics_date: Date for these metrics.
            entered: Contacts who entered step.
            completed: Contacts who completed step.
            average_time_in_step_seconds: Average time in step.

        Returns:
            A new WorkflowStepMetrics instance with calculated metrics.
        """
        # Calculate dropped off
        dropped_off = entered - completed

        # Calculate conversion rate
        conversion_rate = StepConversionRate.calculate(completed, entered)

        now = datetime.now(UTC)

        return cls(
            id=uuid4(),
            workflow_id=workflow_id,
            step_id=step_id,
            step_name=step_name,
            step_order=step_order,
            date=metrics_date,
            entered=entered,
            completed=completed,
            dropped_off=dropped_off,
            step_conversion_rate=conversion_rate.value,
            average_time_in_step_seconds=average_time_in_step_seconds,
            created_at=now,
            updated_at=now,
        )

    @property
    def drop_off_rate(self) -> Decimal:
        """Calculate drop-off rate percentage.

        Returns:
            Drop-off rate as decimal (0-100).
        """
        if self.entered == 0:
            return Decimal("0")

        drop_off = (Decimal(self.dropped_off) / Decimal(self.entered)) * Decimal("100")
        return drop_off.quantize(Decimal("0.01"))

    @property
    def success_rate(self) -> Decimal:
        """Calculate action success rate.

        Returns:
            Success rate as decimal (0-100), or None if no executions.
        """
        if self.executions == 0:
            return Decimal("0")

        success_rate = (Decimal(self.successes) / Decimal(self.executions)) * Decimal("100")
        return success_rate.quantize(Decimal("0.01"))

    def is_bottleneck(self, threshold: Decimal = Decimal("30")) -> bool:
        """Check if this step is a bottleneck.

        A bottleneck is defined as a step with drop-off rate
        exceeding the threshold.

        Args:
            threshold: Drop-off rate threshold (default 30%).

        Returns:
            True if step is a bottleneck.
        """
        return self.drop_off_rate > threshold

    def to_dict(self) -> dict[str, Any]:
        """Convert step metrics to dictionary representation.

        Returns:
            Dictionary containing all step metrics.
        """
        return {
            "id": str(self.id),
            "workflow_id": str(self.workflow_id),
            "step_id": str(self.step_id),
            "step_name": self.step_name,
            "step_order": self.step_order,
            "date": self.date.isoformat(),
            "entered": self.entered,
            "completed": self.completed,
            "dropped_off": self.dropped_off,
            "conversion_rate": float(self.step_conversion_rate),
            "drop_off_rate": float(self.drop_off_rate),
            "average_time_in_step_seconds": self.average_time_in_step_seconds,
            "executions": self.executions,
            "successes": self.successes,
            "failures": self.failures,
            "success_rate": float(self.success_rate),
        }


@dataclass
class WorkflowAnalytics:
    """Workflow analytics aggregate root.

    This entity is the aggregate root for all workflow analytics operations.
    It tracks enrollment, completion, and conversion metrics for a workflow.
    All modifications to analytics data should go through this entity.

    Attributes:
        id: Unique analytics identifier.
        workflow_id: Reference to workflow.
        account_id: Account/tenant identifier.
        total_enrolled: Total contacts ever enrolled.
        currently_active: Contacts currently in workflow.
        completed: Total contacts who completed workflow.
        goals_achieved: Total goal achievements.
        enrollment_sources: Breakdown of enrollments by source.
        exit_reasons: Distribution of exit reasons.
        created_at: Record creation time.
        updated_at: Last update time.
    """

    id: UUID
    workflow_id: UUID
    account_id: UUID
    total_enrolled: int = 0
    currently_active: int = 0
    completed: int = 0
    goals_achieved: int = 0
    enrollment_sources: dict[str, int] = field(default_factory=dict)
    exit_reasons: dict[str, int] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        workflow_id: UUID,
        account_id: UUID,
    ) -> Self:
        """Factory method to create new workflow analytics.

        Args:
            workflow_id: Workflow identifier.
            account_id: Account identifier.

        Returns:
            A new WorkflowAnalytics instance with zero metrics.
        """
        now = datetime.now(UTC)

        return cls(
            id=uuid4(),
            workflow_id=workflow_id,
            account_id=account_id,
            total_enrolled=0,
            currently_active=0,
            completed=0,
            goals_achieved=0,
            enrollment_sources={},
            exit_reasons={},
            created_at=now,
            updated_at=now,
        )

    def record_enrollment(
        self,
        source: str | EnrollmentSource,
        count: int = 1,
    ) -> None:
        """Record new enrollment(s).

        Args:
            source: Source of enrollment (trigger, bulk, api, manual).
            count: Number of enrollments (default 1).
        """
        # Normalize source
        if isinstance(source, str):
            source_enum = EnrollmentSource.from_string(source)
            source_str = source_enum.value
        else:
            source_str = source.value

        # Update metrics
        self.total_enrolled += count
        self.currently_active += count

        # Update source breakdown
        if source_str not in self.enrollment_sources:
            self.enrollment_sources[source_str] = 0
        self.enrollment_sources[source_str] += count

        self._touch()

    def record_completion(
        self,
        count: int = 1,
        exit_reason: str | ExitReason = ExitReason.COMPLETED,
    ) -> None:
        """Record workflow completion(s).

        Args:
            count: Number of completions (default 1).
            exit_reason: Reason for workflow exit.
        """
        # Update metrics
        self.completed += count
        self.currently_active -= count

        # Ensure currently_active doesn't go negative
        self.currently_active = max(0, self.currently_active)

        # Track exit reason
        exit_reason_str = exit_reason if isinstance(exit_reason, str) else exit_reason.value

        if exit_reason_str not in self.exit_reasons:
            self.exit_reasons[exit_reason_str] = 0
        self.exit_reasons[exit_reason_str] += count

        self._touch()

    def record_goal_achievement(self, count: int = 1) -> None:
        """Record goal achievement(s).

        Args:
            count: Number of goal achievements (default 1).
        """
        self.goals_achieved += count
        self._touch()

    def record_exit(
        self,
        exit_reason: str | ExitReason,
        count: int = 1,
    ) -> None:
        """Record workflow exit(s) without completion.

        Args:
            exit_reason: Reason for exit.
            count: Number of exits (default 1).
        """
        # Update active count
        self.currently_active -= count

        # Ensure currently_active doesn't go negative
        self.currently_active = max(0, self.currently_active)

        # Track exit reason
        exit_reason_str = exit_reason if isinstance(exit_reason, str) else exit_reason.value

        if exit_reason_str not in self.exit_reasons:
            self.exit_reasons[exit_reason_str] = 0
        self.exit_reasons[exit_reason_str] += count

        self._touch()

    @property
    def completion_rate(self) -> CompletionRate:
        """Calculate completion rate.

        Returns:
            CompletionRate value object.
        """
        return CompletionRate.calculate(self.completed, self.total_enrolled)

    @property
    def conversion_rate(self) -> ConversionRate:
        """Calculate conversion rate.

        Returns:
            ConversionRate value object.
        """
        return ConversionRate.calculate(self.goals_achieved, self.total_enrolled)

    def create_snapshot(self, snapshot_date: Date | None = None) -> MetricsSnapshot:
        """Create a point-in-time snapshot of current metrics.

        Args:
            snapshot_date: Date for snapshot (default: today).

        Returns:
            MetricsSnapshot instance.
        """
        if snapshot_date is None:
            snapshot_date = datetime.now(UTC).date()

        return MetricsSnapshot.create(
            workflow_id=self.workflow_id,
            snapshot_date=snapshot_date,
            total_enrolled=self.total_enrolled,
            new_enrollments=0,  # Calculated from aggregation
            currently_active=self.currently_active,
            completed=self.completed,
            goals_achieved=self.goals_achieved,
        )

    def _touch(self) -> None:
        """Update timestamp."""
        self.updated_at = datetime.now(UTC)

    def to_dict(self) -> dict[str, Any]:
        """Convert analytics to dictionary representation.

        Returns:
            Dictionary containing all analytics attributes.
        """
        return {
            "id": str(self.id),
            "workflow_id": str(self.workflow_id),
            "account_id": str(self.account_id),
            "total_enrolled": self.total_enrolled,
            "currently_active": self.currently_active,
            "completed": self.completed,
            "goals_achieved": self.goals_achieved,
            "completion_rate": float(self.completion_rate.value),
            "conversion_rate": float(self.conversion_rate.value),
            "enrollment_sources": self.enrollment_sources,
            "exit_reasons": self.exit_reasons,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
