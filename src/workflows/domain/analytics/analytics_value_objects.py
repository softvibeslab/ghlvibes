"""
Value objects for Workflow Analytics domain.

Value objects are immutable objects identified by their attributes
rather than a unique identity. They represent concepts in the domain
that don't need their own lifecycle.

Following DDD principles, these objects are compared by value,
not by identity.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, Optional, List
from uuid import UUID


class EnrollmentSource(Enum):
    """Source of workflow enrollment."""

    TRIGGER = "trigger"
    BULK = "bulk"
    API = "api"
    MANUAL = "manual"


class ExitReason(Enum):
    """Reasons for workflow exit."""

    COMPLETED = "completed"
    GOAL_ACHIEVED = "goal_achieved"
    REMOVED = "removed"
    ERROR = "error"
    TIMEOUT = "timeout"
    UNSUBSCRIBED = "unsubscribed"


class ExportFormat(Enum):
    """Supported export formats."""

    CSV = "csv"
    PDF = "pdf"
    JSON = "json"


@dataclass(frozen=True)
class TimeRange:
    """
    Immutable time range for analytics queries.

    Attributes:
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
    """

    start_date: date
    end_date: date

    def __post_init__(self):
        """Validate that start_date <= end_date."""
        if self.start_date > self.end_date:
            raise ValueError(
                f"Invalid time range: start_date {self.start_date} "
                f"must be <= end_date {self.end_date}"
            )

    def days_in_range(self) -> int:
        """Calculate number of days in range."""
        return (self.end_date - self.start_date).days + 1

    def to_previous_period(self, days: int) -> 'TimeRange':
        """
        Create a time range for the previous period.

        Args:
            days: Number of days in current period

        Returns:
            New TimeRange for previous period
        """
        period_length = self.days_in_range()
        new_end = self.start_date - timedelta(days=1)
        new_start = new_end - timedelta(days=period_length - 1)

        return TimeRange(start_date=new_start, end_date=new_end)


@dataclass(frozen=True)
class EnrollmentMetrics:
    """
    Value object containing enrollment tracking metrics.

    Attributes:
        total_enrolled: Total contacts ever enrolled
        currently_active: Contacts currently progressing
        new_enrollments: New enrollments in time range
        enrollment_sources: Breakdown by source
        enrollment_rate: New enrollments per day
    """

    total_enrolled: int
    currently_active: int
    new_enrollments: int
    enrollment_sources: Dict[EnrollmentSource, int]
    enrollment_rate: Decimal

    def __post_init__(self):
        """Validate enrollment metrics."""
        if self.total_enrolled < 0:
            raise ValueError("total_enrolled cannot be negative")
        if self.currently_active < 0:
            raise ValueError("currently_active cannot be negative")
        if self.new_enrollments < 0:
            raise ValueError("new_enrollments cannot be negative")


@dataclass(frozen=True)
class CompletionMetrics:
    """
    Value object containing completion tracking metrics.

    Attributes:
        completed: Total contacts who reached final step
        completion_rate: Percentage of enrolled who completed
        average_duration_seconds: Mean time to completion
        exit_reasons: Distribution of exit reasons
    """

    completed: int
    completion_rate: Decimal
    average_duration_seconds: int
    exit_reasons: Dict[ExitReason, int]

    def __post_init__(self):
        """Validate completion metrics."""
        if self.completed < 0:
            raise ValueError("completed cannot be negative")
        if not (Decimal('0') <= self.completion_rate <= Decimal('100')):
            raise ValueError("completion_rate must be between 0 and 100")
        if self.average_duration_seconds < 0:
            raise ValueError("average_duration_seconds cannot be negative")


@dataclass(frozen=True)
class ConversionMetrics:
    """
    Value object containing conversion tracking metrics.

    Attributes:
        goals_achieved: Total goal completions
        conversion_rate: Percentage achieving goal
        average_time_to_conversion_seconds: Mean time to conversion
        goal_breakdown: Conversions by goal type
    """

    goals_achieved: int
    conversion_rate: Decimal
    average_time_to_conversion_seconds: int
    goal_breakdown: Dict[str, int]

    def __post_init__(self):
        """Validate conversion metrics."""
        if self.goals_achieved < 0:
            raise ValueError("goals_achieved cannot be negative")
        if not (Decimal('0') <= self.conversion_rate <= Decimal('100')):
            raise ValueError("conversion_rate must be between 0 and 100")
        if self.average_time_to_conversion_seconds < 0:
            raise ValueError("average_time_to_conversion_seconds cannot be negative")


@dataclass(frozen=True)
class FunnelStepData:
    """
    Value object for individual funnel step metrics.

    Attributes:
        step_id: Step identifier
        step_name: Human-readable name
        step_order: Position in workflow (0-indexed)
        entered: Count of contacts entering step
        completed: Count of contacts completing step
        dropped_off: Count of contacts dropping off
        step_conversion_rate: Conversion percentage for this step
        average_time_in_step_seconds: Average time spent in step
    """

    step_id: UUID
    step_name: str
    step_order: int
    entered: int
    completed: int
    dropped_off: int
    step_conversion_rate: Decimal
    average_time_in_step_seconds: int

    def __post_init__(self):
        """Validate funnel step data."""
        if self.entered < 0:
            raise ValueError("entered cannot be negative")
        if self.completed < 0:
            raise ValueError("completed cannot be negative")
        if self.dropped_off < 0:
            raise ValueError("dropped_off cannot be negative")
        if not (Decimal('0') <= self.step_conversion_rate <= Decimal('100')):
            raise ValueError("step_conversion_rate must be between 0 and 100")
        if self.average_time_in_step_seconds < 0:
            raise ValueError("average_time_in_step_seconds cannot be negative")

        # Verify consistency: entered = completed + dropped_off
        if self.entered != self.completed + self.dropped_off:
            raise ValueError(
                f"Inconsistent funnel data: entered ({self.entered}) "
                f"!= completed ({self.completed}) + dropped_off ({self.dropped_off})"
            )


@dataclass(frozen=True)
class ActionPerformanceData:
    """
    Value object for action performance metrics.

    Attributes:
        action_id: Action identifier
        action_type: Type of action
        action_name: Human-readable name
        execution_count: Total executions
        success_count: Successful executions
        failure_count: Failed executions
        success_rate: Success percentage
        error_rate: Error percentage
        average_duration_ms: Average execution time
    """

    action_id: UUID
    action_type: str
    action_name: str
    execution_count: int
    success_count: int
    failure_count: int
    success_rate: Decimal
    error_rate: Decimal
    average_duration_ms: int

    def __post_init__(self):
        """Validate action performance data."""
        if self.execution_count < 0:
            raise ValueError("execution_count cannot be negative")
        if self.success_count < 0:
            raise ValueError("success_count cannot be negative")
        if self.failure_count < 0:
            raise ValueError("failure_count cannot be negative")
        if not (Decimal('0') <= self.success_rate <= Decimal('100')):
            raise ValueError("success_rate must be between 0 and 100")
        if not (Decimal('0') <= self.error_rate <= Decimal('100')):
            raise ValueError("error_rate must be between 0 and 100")
        if self.average_duration_ms < 0:
            raise ValueError("average_duration_ms cannot be negative")

        # Verify consistency
        if self.execution_count != self.success_count + self.failure_count:
            raise ValueError(
                f"Inconsistent execution data: execution_count ({self.execution_count}) "
                f"!= success_count ({self.success_count}) + failure_count ({self.failure_count})"
            )


from datetime import timedelta
