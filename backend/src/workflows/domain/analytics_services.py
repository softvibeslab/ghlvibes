"""Domain services for workflow analytics.

These services encapsulate business logic that doesn't naturally fit
within a single entity. They coordinate between entities and value objects
to perform complex analytics operations.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from datetime import date as Date
from decimal import Decimal
from typing import Any
from uuid import UUID

from src.workflows.domain.analytics_entities import (
    MetricsSnapshot,
    WorkflowAnalytics,
    WorkflowStepMetrics,
)
from src.workflows.domain.analytics_exceptions import (
    AnalyticsAggregationError,
    FunnelAnalysisError,
    MetricsCalculationError,
)
from src.workflows.domain.analytics_value_objects import (
    CompletionRate,
    ConversionRate,
)


@dataclass
class FunnelStepData:
    """Funnel analysis data for a single step.

    Attributes:
        step_id: Step identifier.
        step_name: Human-readable step name.
        step_order: Position in workflow.
        entered: Contacts who entered this step.
        completed: Contacts who completed this step.
        dropped_off: Contacts who exited at this step.
        conversion_rate: Step conversion percentage.
        drop_off_rate: Drop-off percentage.
        is_bottleneck: Whether this step is a bottleneck.
    """

    step_id: UUID
    step_name: str
    step_order: int
    entered: int
    completed: int
    dropped_off: int
    conversion_rate: Decimal
    drop_off_rate: Decimal
    is_bottleneck: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "step_id": str(self.step_id),
            "step_name": self.step_name,
            "step_order": self.step_order,
            "entered": self.entered,
            "completed": self.completed,
            "dropped_off": self.dropped_off,
            "conversion_rate": float(self.conversion_rate),
            "drop_off_rate": float(self.drop_off_rate),
            "is_bottleneck": self.is_bottleneck,
        }


@dataclass
class FunnelAnalysis:
    """Complete funnel analysis results.

    Attributes:
        workflow_id: Workflow identifier.
        total_enrolled: Total enrollments at funnel start.
        final_converted: Contacts who completed funnel.
        overall_conversion_rate: Overall funnel conversion.
        bottleneck_step_id: Step with highest drop-off (if any).
        steps: List of funnel step data.
        analyzed_at: When analysis was performed.
    """

    workflow_id: UUID
    total_enrolled: int
    final_converted: int
    overall_conversion_rate: Decimal
    bottleneck_step_id: UUID | None
    steps: list[FunnelStepData]
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "workflow_id": str(self.workflow_id),
            "total_enrolled": self.total_enrolled,
            "final_converted": self.final_converted,
            "overall_conversion_rate": float(self.overall_conversion_rate),
            "bottleneck_step_id": str(self.bottleneck_step_id) if self.bottleneck_step_id else None,
            "steps": [step.to_dict() for step in self.steps],
            "analyzed_at": self.analyzed_at.isoformat(),
        }


@dataclass
class TimeRange:
    """Time range for analytics queries.

    Attributes:
        start_date: Range start date (inclusive).
        end_date: Range end date (inclusive).
    """

    start_date: Date
    end_date: Date

    def __post_init__(self) -> None:
        """Validate time range."""
        if self.start_date > self.end_date:
            raise ValueError("start_date must be before or equal to end_date")

    @classmethod
    def last_7_days(cls) -> "TimeRange":
        """Create time range for last 7 days."""
        today = datetime.now(UTC).date()
        return cls(end_date=today, start_date=today.subtract(days=7))

    @classmethod
    def last_30_days(cls) -> "TimeRange":
        """Create time range for last 30 days."""
        today = datetime.now(UTC).date()
        return cls(end_date=today, start_date=today.subtract(days=30))

    @classmethod
    def last_90_days(cls) -> "TimeRange":
        """Create time range for last 90 days."""
        today = datetime.now(UTC).date()
        return cls(end_date=today, start_date=today.subtract(days=90))

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary representation."""
        return {
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
        }


class MetricsCalculationService:
    """Service for calculating analytics metrics.

    Provides business logic for computing various metrics from
    raw execution data.
    """

    @staticmethod
    def calculate_enrollment_rate(
        new_enrollments: int,
        previous_enrollments: int,
        days: int,
    ) -> Decimal:
        """Calculate daily enrollment rate.

        Args:
            new_enrollments: New enrollments in period.
            previous_enrollments: Enrollments in previous period.
            days: Number of days in period.

        Returns:
            Enrollment rate as enrollments per day.

        Raises:
            MetricsCalculationError: If calculation fails.
        """
        try:
            if days <= 0:
                raise ValueError("days must be positive")

            rate = Decimal(new_enrollments) / Decimal(days)
            return rate.quantize(Decimal("0.01"))
        except (ValueError, ZeroDivisionError) as err:
            raise MetricsCalculationError(
                metric_name="enrollment_rate",
                reason=str(err),
            ) from err

    @staticmethod
    def calculate_average_duration(
        durations_seconds: list[int],
    ) -> Decimal | None:
        """Calculate average duration from list of durations.

        Args:
            durations_seconds: List of durations in seconds.

        Returns:
            Average duration in seconds, or None if list is empty.
        """
        if not durations_seconds:
            return None

        try:
            total = sum(Decimal(d) for d in durations_seconds)
            avg = total / Decimal(len(durations_seconds))
            return avg.quantize(Decimal("0.01"))
        except (ValueError, ZeroDivisionError):
            return None

    @staticmethod
    def calculate_median_duration(
        durations_seconds: list[int],
    ) -> Decimal | None:
        """Calculate median duration from list of durations.

        Args:
            durations_seconds: List of durations in seconds.

        Returns:
            Median duration in seconds, or None if list is empty.
        """
        if not durations_seconds:
            return None

        try:
            sorted_durations = sorted(durations_seconds)
            n = len(sorted_durations)
            mid = n // 2

            if n % 2 == 0:
                median = (sorted_durations[mid - 1] + sorted_durations[mid]) / 2
            else:
                median = sorted_durations[mid]

            return Decimal(str(median)).quantize(Decimal("0.01"))
        except (ValueError, IndexError):
            return None


class FunnelAnalysisService:
    """Service for analyzing workflow funnels.

    Provides business logic for identifying bottlenecks, drop-off points,
    and conversion patterns in workflow funnels.
    """

    def __init__(self, bottleneck_threshold: Decimal = Decimal("30")) -> None:
        """Initialize funnel analysis service.

        Args:
            bottleneck_threshold: Drop-off rate percentage to consider
                a step a bottleneck (default 30%).
        """
        self.bottleneck_threshold = bottleneck_threshold

    def analyze_funnel(
        self,
        step_metrics: list[WorkflowStepMetrics],
        total_enrolled: int,
    ) -> FunnelAnalysis:
        """Analyze workflow funnel from step metrics.

        Args:
            step_metrics: List of step metrics ordered by step_order.
            total_enrolled: Total enrollments at funnel start.

        Returns:
            FunnelAnalysis with complete funnel data.

        Raises:
            FunnelAnalysisError: If analysis fails.
        """
        try:
            if not step_metrics:
                raise FunnelAnalysisError("No step metrics provided")

            # Sort by step order
            sorted_steps = sorted(step_metrics, key=lambda s: s.step_order)

            # Build funnel step data
            funnel_steps: list[FunnelStepData] = []
            bottleneck_step_id: UUID | None = None
            highest_drop_off = Decimal("0")

            for step in sorted_steps:
                # Calculate drop-off rate
                if step.entered > 0:
                    drop_off_rate = (
                        Decimal(step.dropped_off) / Decimal(step.entered)
                    ) * Decimal("100")
                else:
                    drop_off_rate = Decimal("0")

                drop_off_rate = drop_off_rate.quantize(Decimal("0.01"))

                # Check if bottleneck
                is_bottleneck = drop_off_rate > self.bottleneck_threshold
                if is_bottleneck and drop_off_rate > highest_drop_off:
                    bottleneck_step_id = step.step_id
                    highest_drop_off = drop_off_rate

                funnel_step = FunnelStepData(
                    step_id=step.step_id,
                    step_name=step.step_name,
                    step_order=step.step_order,
                    entered=step.entered,
                    completed=step.completed,
                    dropped_off=step.dropped_off,
                    conversion_rate=step.step_conversion_rate,
                    drop_off_rate=drop_off_rate,
                    is_bottleneck=is_bottleneck,
                )
                funnel_steps.append(funnel_step)

            # Calculate overall conversion
            final_converted = (
                sorted_steps[-1].completed if sorted_steps else 0
            )
            overall_conversion = ConversionRate.calculate(
                final_converted,
                total_enrolled,
            )

            return FunnelAnalysis(
                workflow_id=sorted_steps[0].workflow_id,
                total_enrolled=total_enrolled,
                final_converted=final_converted,
                overall_conversion_rate=overall_conversion.value,
                bottleneck_step_id=bottleneck_step_id,
                steps=funnel_steps,
            )

        except (ValueError, IndexError) as err:
            raise FunnelAnalysisError(str(err)) from err

    def identify_bottlenecks(
        self,
        step_metrics: list[WorkflowStepMetrics],
    ) -> list[WorkflowStepMetrics]:
        """Identify bottleneck steps from metrics.

        Args:
            step_metrics: List of step metrics.

        Returns:
            List of steps identified as bottlenecks, ordered by severity.
        """
        bottlenecks = [
            step
            for step in step_metrics
            if step.is_bottleneck(self.bottleneck_threshold)
        ]

        # Sort by drop-off rate (highest first)
        bottlenecks.sort(key=lambda s: s.drop_off_rate, reverse=True)

        return bottlenecks


class ConversionCalculationService:
    """Service for calculating conversion metrics.

    Provides business logic for computing conversion-related metrics
    including time-to-conversion statistics.
    """

    @staticmethod
    def calculate_conversion_rate(
        goals_achieved: int,
        total_enrolled: int,
    ) -> ConversionRate:
        """Calculate conversion rate.

        Args:
            goals_achieved: Number of goals achieved.
            total_enrolled: Total number enrolled.

        Returns:
            ConversionRate value object.
        """
        return ConversionRate.calculate(goals_achieved, total_enrolled)

    @staticmethod
    def calculate_time_to_conversion_stats(
        conversion_times_seconds: list[int],
    ) -> dict[str, Decimal | None]:
        """Calculate time-to-conversion statistics.

        Args:
            conversion_times_seconds: List of times from enrollment to goal.

        Returns:
            Dictionary with average and median times in seconds.
        """
        if not conversion_times_seconds:
            return {"average_seconds": None, "median_seconds": None}

        avg = MetricsCalculationService.calculate_average_duration(
            conversion_times_seconds,
        )
        median = MetricsCalculationService.calculate_median_duration(
            conversion_times_seconds,
        )

        return {
            "average_seconds": avg,
            "median_seconds": median,
        }


class AnalyticsAggregationService:
    """Service for aggregating analytics data.

    Coordinates the aggregation of raw execution events into
    time-series metrics snapshots.
    """

    @staticmethod
    def aggregate_daily_metrics(
        workflow_id: UUID,
        date: Date,
        executions: list[dict[str, Any]],
    ) -> MetricsSnapshot:
        """Aggregate execution data into daily metrics snapshot.

        Args:
            workflow_id: Workflow identifier.
            date: Aggregation date.
            executions: List of execution records for this date.

        Returns:
            MetricsSnapshot with aggregated metrics.

        Raises:
            AnalyticsAggregationError: If aggregation fails.
        """
        try:
            # Initialize counters
            total_enrolled = 0
            new_enrollments = 0
            currently_active = 0
            completed = 0
            goals_achieved = 0
            durations: list[int] = []

            for execution in executions:
                total_enrolled += 1

                status = execution.get("status")
                enrolled_at = execution.get("enrolled_at")
                completed_at = execution.get("completed_at")
                goal_achieved_at = execution.get("goal_achieved_at")

                # Check if new enrollment today
                if enrolled_at and enrolled_at.date() == date:
                    new_enrollments += 1

                # Count active
                if status == "active":
                    currently_active += 1

                # Count completions
                if status in ("completed", "goal_achieved"):
                    completed += 1

                    # Track duration if available
                    if enrolled_at and completed_at:
                        duration = int((completed_at - enrolled_at).total_seconds())
                        durations.append(duration)

                # Count goal achievements
                if status == "goal_achieved":
                    goals_achieved += 1

            # Calculate average duration
            avg_duration = (
                sum(durations) // len(durations) if durations else None
            )

            return MetricsSnapshot.create(
                workflow_id=workflow_id,
                snapshot_date=date,
                total_enrolled=total_enrolled,
                new_enrollments=new_enrollments,
                currently_active=currently_active,
                completed=completed,
                goals_achieved=goals_achieved,
                average_duration_seconds=avg_duration,
            )

        except (ValueError, KeyError, TypeError) as err:
            raise AnalyticsAggregationError(str(err)) from err
