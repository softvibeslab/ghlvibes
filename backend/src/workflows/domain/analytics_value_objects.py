"""Value objects for workflow analytics domain.

Value objects are immutable objects that represent measurements and
concepts in the analytics domain. They ensure data validity and
encapsulate business rules.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from src.workflows.domain.analytics_exceptions import (
    InvalidCompletionRateError,
    InvalidConversionRateError,
    InvalidEnrollmentSourceError,
)


class EnrollmentSource(StrEnum):
    """Source of workflow enrollment.

    Represents how a contact entered a workflow. This is used for
    enrollment source attribution and analytics.
    """

    TRIGGER = "trigger"  # Automatic trigger-based enrollment
    BULK = "bulk"  # Bulk enrollment by user
    API = "api"  # Enrollment via REST API
    MANUAL = "manual"  # Single contact manual enrollment

    @classmethod
    def from_string(cls, value: str) -> "EnrollmentSource":
        """Create EnrollmentSource from string.

        Args:
            value: String representation of enrollment source.

        Returns:
            EnrollmentSource enum value.

        Raises:
            InvalidEnrollmentSourceError: If value is not a valid source.
        """
        try:
            return cls(value.lower())
        except ValueError as err:
            valid = [s.value for s in cls]
            raise InvalidEnrollmentSourceError(
                value,
                valid,
            ) from err


class ExitReason(StrEnum):
    """Reason for workflow exit.

    Represents why a contact left a workflow. This is used for
    exit reason distribution analytics.
    """

    COMPLETED = "completed"  # Reached final step
    GOAL_ACHIEVED = "goal_achieved"  # Achieved workflow goal
    MANUAL_REMOVAL = "manual_removal"  # Removed by user
    UNSUBSCRIBED = "unsubscribed"  # Contact unsubscribed
    ERROR = "error"  # Execution error


@dataclass(frozen=True)
class ConversionRate:
    """Conversion rate value object.

    Represents the percentage of enrolled contacts who achieved
    a workflow goal. Valid range is 0.0 to 100.0.

    Attributes:
        value: Conversion rate as decimal (0-100).
    """

    value: Decimal

    def __post_init__(self) -> None:
        """Validate conversion rate.

        Raises:
            InvalidConversionRateError: If value is outside valid range.
        """
        if self.value < Decimal("0") or self.value > Decimal("100"):
            raise InvalidConversionRateError(self.value)

    @classmethod
    def calculate(
        cls,
        goals_achieved: int,
        total_enrolled: int,
    ) -> "ConversionRate":
        """Calculate conversion rate from counts.

        Args:
            goals_achieved: Number of contacts who achieved goal.
            total_enrolled: Total number of enrolled contacts.

        Returns:
            ConversionRate instance.

        Raises:
            InvalidConversionRateError: If inputs would produce invalid rate.
        """
        if total_enrolled == 0:
            return cls(Decimal("0"))

        rate = (Decimal(goals_achieved) / Decimal(total_enrolled)) * Decimal("100")
        # Round to 2 decimal places
        rate = rate.quantize(Decimal("0.01"))

        return cls(rate)

    @property
    def as_percentage(self) -> str:
        """Get conversion rate as percentage string.

        Returns:
            String representation with % sign.
        """
        return f"{self.value}%"


@dataclass(frozen=True)
class CompletionRate:
    """Completion rate value object.

    Represents the percentage of enrolled contacts who completed
    the workflow. Valid range is 0.0 to 100.0.

    Attributes:
        value: Completion rate as decimal (0-100).
    """

    value: Decimal

    def __post_init__(self) -> None:
        """Validate completion rate.

        Raises:
            InvalidCompletionRateError: If value is outside valid range.
        """
        if self.value < Decimal("0") or self.value > Decimal("100"):
            raise InvalidCompletionRateError(self.value)

    @classmethod
    def calculate(
        cls,
        completed: int,
        total_enrolled: int,
    ) -> "CompletionRate":
        """Calculate completion rate from counts.

        Args:
            completed: Number of contacts who completed.
            total_enrolled: Total number of enrolled contacts.

        Returns:
            CompletionRate instance.
        """
        if total_enrolled == 0:
            return cls(Decimal("0"))

        rate = (Decimal(completed) / Decimal(total_enrolled)) * Decimal("100")
        # Round to 2 decimal places
        rate = rate.quantize(Decimal("0.01"))

        return cls(rate)

    @property
    def as_percentage(self) -> str:
        """Get completion rate as percentage string.

        Returns:
            String representation with % sign.
        """
        return f"{self.value}%"


@dataclass(frozen=True)
class StepConversionRate:
    """Step conversion rate value object.

    Represents the percentage of contacts who completed a specific
    workflow step relative to those who entered it.

    Attributes:
        value: Step conversion rate as decimal (0-100).
    """

    value: Decimal

    def __post_init__(self) -> None:
        """Validate step conversion rate."""
        if self.value < Decimal("0") or self.value > Decimal("100"):
            raise ValueError(f"Step conversion rate must be between 0 and 100, got {self.value}")

    @classmethod
    def calculate(
        cls,
        completed: int,
        entered: int,
    ) -> "StepConversionRate":
        """Calculate step conversion rate from counts.

        Args:
            completed: Number of contacts who completed step.
            entered: Number of contacts who entered step.

        Returns:
            StepConversionRate instance.
        """
        if entered == 0:
            return cls(Decimal("0"))

        rate = (Decimal(completed) / Decimal(entered)) * Decimal("100")
        # Round to 2 decimal places
        rate = rate.quantize(Decimal("0.01"))

        return cls(rate)

    @property
    def as_percentage(self) -> str:
        """Get step conversion rate as percentage string."""
        return f"{self.value}%"
