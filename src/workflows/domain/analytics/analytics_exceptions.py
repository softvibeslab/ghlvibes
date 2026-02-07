"""
Domain exceptions for Workflow Analytics.

Custom exceptions that represent domain-specific errors.
These exceptions help communicate business rule violations
and domain-specific error conditions.
"""

from typing import Optional
from uuid import UUID


class AnalyticsDomainException(Exception):
    """Base exception for all analytics domain errors."""

    def __init__(self, message: str, workflow_id: Optional[UUID] = None):
        self.message = message
        self.workflow_id = workflow_id
        super().__init__(message)


class InvalidTimeRangeException(AnalyticsDomainException):
    """
    Raised when an invalid time range is provided.

    This can occur when:
    - Start date is after end date
    - Time range exceeds maximum allowed duration
    - Time range is in the future
    """

    pass


class MetricsCalculationException(AnalyticsDomainException):
    """
    Raised when metrics calculation fails.

    This can occur when:
    - Required data is missing
    - Data integrity issues detected
    - Calculation errors occur
    """

    pass


class FunnelAnalysisException(AnalyticsDomainException):
    """
    Raised when funnel analysis fails.

    This can occur when:
    - Workflow steps are not properly configured
    - Step order is inconsistent
    - Funnel data is incomplete
    """

    pass


class ExportGenerationException(AnalyticsDomainException):
    """
    Raised when export generation fails.

    This can occur when:
    - Export format is not supported
    - Data size exceeds limits
    - File generation errors occur
    """

    pass


class DataRetentionException(AnalyticsDomainException):
    """
    Raised when data retention operations fail.

    This can occur when:
    - Retention policies are violated
    - Cleanup operations fail
    - Data archival errors occur
    """

    pass


class AnalyticsNotFoundException(AnalyticsDomainException):
    """
    Raised when analytics data is not found.

    This occurs when:
    - Workflow has no analytics data
    - Time range contains no data
    - Workflow does not exist
    """

    pass
