"""Exceptions for workflow analytics domain.

Domain-specific exceptions that represent business rule violations
and error conditions in the analytics domain.
"""

from decimal import Decimal


class AnalyticsError(Exception):
    """Base exception for analytics domain errors."""

    pass


class InvalidConversionRateError(AnalyticsError):
    """Raised when conversion rate is outside valid range (0-100)."""

    def __init__(self, value: Decimal | float) -> None:
        """Initialize exception.

        Args:
            value: Invalid conversion rate value.
        """
        self.value = value
        super().__init__(
            f"Conversion rate must be between 0 and 100, got {value}"
        )


class InvalidCompletionRateError(AnalyticsError):
    """Raised when completion rate is outside valid range (0-100)."""

    def __init__(self, value: Decimal | float) -> None:
        """Initialize exception.

        Args:
            value: Invalid completion rate value.
        """
        self.value = value
        super().__init__(
            f"Completion rate must be between 0 and 100, got {value}"
        )


class InvalidEnrollmentSourceError(AnalyticsError):
    """Raised when enrollment source is not recognized."""

    def __init__(self, value: str, valid_sources: list[str]) -> None:
        """Initialize exception.

        Args:
            value: Invalid enrollment source value.
            valid_sources: List of valid enrollment sources.
        """
        self.value = value
        self.valid_sources = valid_sources
        super().__init__(
            f"Invalid enrollment source '{value}'. "
            f"Valid sources: {', '.join(valid_sources)}"
        )


class AnalyticsAggregationError(AnalyticsError):
    """Raised when analytics aggregation fails."""

    def __init__(self, message: str) -> None:
        """Initialize exception.

        Args:
            message: Error message describing the failure.
        """
        self.message = message
        super().__init__(f"Analytics aggregation failed: {message}")


class MetricsCalculationError(AnalyticsError):
    """Raised when metrics calculation fails."""

    def __init__(self, metric_name: str, reason: str) -> None:
        """Initialize exception.

        Args:
            metric_name: Name of the metric that failed calculation.
            reason: Reason for the failure.
        """
        self.metric_name = metric_name
        self.reason = reason
        super().__init__(
            f"Failed to calculate metric '{metric_name}': {reason}"
        )


class FunnelAnalysisError(AnalyticsError):
    """Raised when funnel analysis fails."""

    def __init__(self, reason: str) -> None:
        """Initialize exception.

        Args:
            reason: Reason for the analysis failure.
        """
        self.reason = reason
        super().__init__(f"Funnel analysis failed: {reason}")
