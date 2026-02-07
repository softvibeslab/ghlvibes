"""Data Transfer Objects for workflow analytics.

DTOs define the contract between application layers and external interfaces.
They provide structured data formats for API requests and responses.
"""

from dataclasses import dataclass
from datetime import date as Date
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ExportFormat(StrEnum):
    """Supported analytics export formats."""

    CSV = "csv"
    JSON = "json"
    PDF = "pdf"


class Granularity(StrEnum):
    """Time granularity for analytics aggregation."""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"


class DatePreset(StrEnum):
    """Preset date ranges for analytics queries."""

    TODAY = "today"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    LAST_90_DAYS = "last_90_days"
    CUSTOM = "custom"


# =============================================================================
# Request DTOs
# =============================================================================


class AnalyticsQueryDTO(BaseModel):
    """Query parameters for analytics requests.

    Attributes:
        workflow_id: Target workflow identifier.
        start_date: Range start date (inclusive).
        end_date: Range end date (inclusive).
        granularity: Time aggregation granularity.
        date_preset: Preset date range (optional).
        compare_with_previous: Enable comparison with previous period.
    """

    workflow_id: UUID
    start_date: Date
    end_date: Date
    granularity: Granularity = Field(default=Granularity.DAILY)
    date_preset: DatePreset | None = Field(default=None)
    compare_with_previous: bool = Field(default=False)


class FunnelQueryDTO(BaseModel):
    """Query parameters for funnel analytics.

    Attributes:
        workflow_id: Target workflow identifier.
        start_date: Range start date.
        end_date: Range end date.
        include_step_details: Include detailed step metrics.
    """

    workflow_id: UUID
    start_date: Date
    end_date: Date
    include_step_details: bool = Field(default=True)


class ActionPerformanceQueryDTO(BaseModel):
    """Query parameters for action performance metrics.

    Attributes:
        workflow_id: Target workflow identifier.
        start_date: Range start date.
        end_date: Range end date.
        action_types: Filter by action types (empty = all).
    """

    workflow_id: UUID
    start_date: Date
    end_date: Date
    action_types: list[str] = Field(default_factory=list)


class ExportRequestDTO(BaseModel):
    """Request parameters for analytics export.

    Attributes:
        workflow_id: Target workflow identifier.
        start_date: Range start date.
        end_date: Range end date.
        format: Export format (CSV, JSON, PDF).
        include_charts: Include visualizations (PDF only).
    """

    workflow_id: UUID
    start_date: Date
    end_date: Date
    format: ExportFormat
    include_charts: bool = Field(default=False)


# =============================================================================
# Response DTOs
# =============================================================================


class EnrollmentMetricsDTO(BaseModel):
    """Enrollment metrics response.

    Attributes:
        total_enrolled: Total contacts ever enrolled.
        currently_active: Contacts currently in workflow.
        new_enrollments: New enrollments in period.
        enrollment_rate: Enrollments per day.
        enrollment_sources: Breakdown by source.
    """

    total_enrolled: int
    currently_active: int
    new_enrollments: int
    enrollment_rate: float
    enrollment_sources: dict[str, int] = Field(default_factory=dict)


class CompletionMetricsDTO(BaseModel):
    """Completion metrics response.

    Attributes:
        completed: Total contacts who completed workflow.
        completion_rate: Completion percentage.
        average_duration_hours: Average time to completion.
        exit_reasons: Distribution of exit reasons.
    """

    completed: int
    completion_rate: float
    average_duration_hours: float | None = None
    exit_reasons: dict[str, int] = Field(default_factory=dict)


class ConversionMetricsDTO(BaseModel):
    """Conversion metrics response.

    Attributes:
        goals_achieved: Total goal achievements.
        conversion_rate: Conversion percentage.
        average_time_to_conversion_hours: Average time to goal.
        median_time_to_conversion_hours: Median time to goal.
    """

    goals_achieved: int
    conversion_rate: float
    average_time_to_conversion_hours: float | None = None
    median_time_to_conversion_hours: float | None = None


class TrendDataPointDTO(BaseModel):
    """Single data point in trend analysis.

    Attributes:
        date: Data point date.
        new_enrollments: New enrollments on this date.
        completions: Completions on this date.
        conversions: Goal achievements on this date.
    """

    date: Date
    new_enrollments: int
    completions: int
    conversions: int


class AnalyticsResponseDTO(BaseModel):
    """Complete analytics response.

    Attributes:
        workflow_id: Workflow identifier.
        period: Query period information.
        summary: Summary metrics.
        enrollment: Enrollment metrics.
        completion: Completion metrics.
        conversion: Conversion metrics.
        trends: Time-series trend data.
        generated_at: When response was generated.
    """

    workflow_id: UUID
    period: dict[str, str]
    summary: dict[str, Any]
    enrollment: EnrollmentMetricsDTO
    completion: CompletionMetricsDTO
    conversion: ConversionMetricsDTO
    trends: list[TrendDataPointDTO]
    generated_at: datetime


class FunnelStepDTO(BaseModel):
    """Funnel step data in response.

    Attributes:
        step_id: Step identifier.
        step_name: Human-readable step name.
        step_order: Position in workflow.
        entered: Contacts who entered this step.
        completed: Contacts who completed this step.
        dropped_off: Contacts who exited at this step.
        conversion_rate: Step conversion percentage.
        drop_off_rate: Drop-off percentage.
        is_bottleneck: Whether this is a bottleneck step.
    """

    step_id: UUID
    step_name: str
    step_order: int
    entered: int
    completed: int
    dropped_off: int
    conversion_rate: float
    drop_off_rate: float
    is_bottleneck: bool


class FunnelAnalyticsDTO(BaseModel):
    """Funnel analytics response.

    Attributes:
        workflow_id: Workflow identifier.
        total_enrolled: Total enrollments at funnel start.
        final_converted: Contacts who completed funnel.
        overall_conversion_rate: Overall funnel conversion.
        bottleneck_step_id: Step with highest drop-off.
        steps: List of funnel step data.
        analyzed_at: When analysis was performed.
    """

    workflow_id: UUID
    total_enrolled: int
    final_converted: int
    overall_conversion_rate: float
    bottleneck_step_id: UUID | None
    steps: list[FunnelStepDTO]
    analyzed_at: datetime


class ActionPerformanceDTO(BaseModel):
    """Action performance metrics response.

    Attributes:
        action_id: Action identifier.
        action_type: Type of action (send_email, wait, etc.).
        action_name: Human-readable action name.
        executions: Number of times action was executed.
        successes: Number of successful executions.
        failures: Number of failed executions.
        success_rate: Success percentage.
        average_duration_ms: Average execution time in milliseconds.
    """

    action_id: UUID
    action_type: str
    action_name: str
    executions: int
    successes: int
    failures: int
    success_rate: float
    average_duration_ms: float | None


class ActionPerformanceResponseDTO(BaseModel):
    """Action performance analytics response.

    Attributes:
        workflow_id: Workflow identifier.
        period: Query period information.
        actions: List of action performance metrics.
        generated_at: When response was generated.
    """

    workflow_id: UUID
    period: dict[str, str]
    actions: list[ActionPerformanceDTO]
    generated_at: datetime


class ExportResponseDTO(BaseModel):
    """Export request response.

    Attributes:
        export_id: Export job identifier.
        status: Export status (pending, processing, completed, failed).
        download_url: URL to download export (when completed).
        expires_at: When export URL expires.
        created_at: When export was requested.
    """

    export_id: UUID
    status: str
    download_url: str | None = None
    expires_at: datetime | None = None
    created_at: datetime


class ComparisonMetricsDTO(BaseModel):
    """Comparison metrics for period-over-period analysis.

    Attributes:
        current_period: Current period metrics.
        previous_period: Previous period metrics.
        change_absolute: Absolute change in values.
        change_percentage: Percentage change.
    """

    metric_name: str
    current_period: float
    previous_period: float
    change_absolute: float
    change_percentage: float


class ComparisonResponseDTO(BaseModel):
    """Period comparison response.

    Attributes:
        workflow_id: Workflow identifier.
        current_period: Current period date range.
        previous_period: Previous period date range.
        metrics: List of compared metrics.
        generated_at: When comparison was generated.
    """

    workflow_id: UUID
    current_period: dict[str, str]
    previous_period: dict[str, str]
    metrics: list[ComparisonMetricsDTO]
    generated_at: datetime
