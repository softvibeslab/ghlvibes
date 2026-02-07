"""
Data Transfer Objects (DTOs) for Workflow Analytics Application Layer.

DTOs define the interface between application layer and presentation layer.
They structure data for API requests and responses.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import List, Dict, Optional, Any
from uuid import UUID


# Request DTOs

@dataclass
class AnalyticsQueryDTO:
    """DTO for analytics query requests."""

    workflow_id: UUID
    start_date: date
    end_date: date
    granularity: str = "daily"  # hourly, daily, weekly
    include_trends: bool = True
    include_comparison: bool = False
    comparison_period_days: int = 0


@dataclass
class FunnelQueryDTO:
    """DTO for funnel analysis requests."""

    workflow_id: UUID
    start_date: date
    end_date: date
    include_step_details: bool = True
    bottleneck_threshold: float = 20.0  # Drop-off percentage


@dataclass
class ActionPerformanceQueryDTO:
    """DTO for action performance requests."""

    workflow_id: UUID
    start_date: date
    end_date: date
    action_types: Optional[List[str]] = None


@dataclass
class ExportRequestDTO:
    """DTO for export requests."""

    workflow_id: UUID
    start_date: date
    end_date: date
    format: str  # csv, pdf, json
    include_charts: bool = False
    include_raw_data: bool = True


# Response DTOs

@dataclass
class EnrollmentMetricsResponseDTO:
    """DTO for enrollment metrics response."""

    total_enrolled: int
    currently_active: int
    new_enrollments: int
    enrollment_rate: float
    enrollment_sources: Dict[str, int]


@dataclass
class CompletionMetricsResponseDTO:
    """DTO for completion metrics response."""

    completed: int
    completion_rate: float
    average_duration_hours: float
    exit_reasons: Dict[str, int]


@dataclass
class ConversionMetricsResponseDTO:
    """DTO for conversion metrics response."""

    goals_achieved: int
    conversion_rate: float
    average_time_to_conversion_hours: float
    goal_breakdown: Dict[str, int]


@dataclass
class AnalyticsResponseDTO:
    """DTO for complete analytics response."""

    workflow_id: UUID
    period: Dict[str, str]  # start_date, end_date
    summary: Dict[str, Any]  # All key metrics
    trends: Optional[List[Dict[str, Any]]] = None
    comparison: Optional[Dict[str, Any]] = None
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FunnelStepResponseDTO:
    """DTO for individual funnel step response."""

    step_id: str
    step_name: str
    step_order: int
    entered: int
    completed: int
    dropped_off: int
    conversion_rate: float
    average_time_seconds: int


@dataclass
class FunnelAnalyticsResponseDTO:
    """DTO for funnel analysis response."""

    workflow_id: UUID
    period: Dict[str, str]
    funnel_steps: List[FunnelStepResponseDTO]
    overall_conversion_rate: float
    bottleneck_steps: List[str]
    total_enrolled: int
    final_converted: int


@dataclass
class ActionPerformanceResponseDTO:
    """DTO for action performance response."""

    action_id: str
    action_type: str
    action_name: str
    execution_count: int
    success_count: int
    failure_count: int
    success_rate: float
    error_rate: float
    average_duration_ms: int


@dataclass
class ActionsAnalyticsResponseDTO:
    """DTO for actions analytics response."""

    workflow_id: UUID
    period: Dict[str, str]
    actions: List[ActionPerformanceResponseDTO]


@dataclass
class ExportResponseDTO:
    """DTO for export response."""

    export_id: UUID
    workflow_id: UUID
    format: str
    file_size_bytes: int
    download_url: str
    expires_at: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ExportStatusDTO:
    """DTO for export job status."""

    export_id: UUID
    status: str  # queued, processing, completed, failed
    progress_percent: int
    download_url: Optional[str] = None
    error_message: Optional[str] = None


# Internal DTOs for use cases

@dataclass
class TimeSeriesDataPoint:
    """DTO for time-series data point."""

    date: date
    timestamp: datetime
    new_enrollments: int
    completions: int
    conversions: int
    total_active: int


@dataclass
class ComparisonMetricsDTO:
    """DTO for comparison metrics."""

    current_period: Dict[str, Any]
    previous_period: Dict[str, Any]
    change_percent: Dict[str, float]
    trend: str  # up, down, stable
