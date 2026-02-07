"""
Pydantic schemas for Workflow Analytics API.

Request and response schemas for FastAPI endpoints.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Dict, Optional
from uuid import UUID
from pydantic import BaseModel, Field


# Request Schemas

class AnalyticsQuerySchema(BaseModel):
    """Schema for analytics query requests."""

    start_date: date = Field(..., description="Start date for analytics period")
    end_date: date = Field(..., description="End date for analytics period")
    granularity: str = Field(default="daily", description="Aggregation level: hourly, daily, weekly")
    include_trends: bool = Field(default=True, description="Include time-series trends")
    include_comparison: bool = Field(default=False, description="Include comparison with previous period")
    comparison_period_days: int = Field(default=0, description="Days for comparison period")


class FunnelQuerySchema(BaseModel):
    """Schema for funnel analysis requests."""

    start_date: date = Field(..., description="Start date for analysis period")
    end_date: date = Field(..., description="End date for analysis period")
    include_step_details: bool = Field(default=True, description="Include detailed step metrics")
    bottleneck_threshold: float = Field(default=20.0, description="Drop-off percentage for bottleneck identification")


class ActionPerformanceQuerySchema(BaseModel):
    """Schema for action performance requests."""

    start_date: date = Field(..., description="Start date for analysis period")
    end_date: date = Field(..., description="End date for analysis period")
    action_types: Optional[List[str]] = Field(default=None, description="Filter by action types")


class ExportRequestSchema(BaseModel):
    """Schema for export requests."""

    start_date: date = Field(..., description="Start date for export period")
    end_date: date = Field(..., description="End date for export period")
    format: str = Field(..., description="Export format: csv, pdf, json")
    include_charts: bool = Field(default=False, description="Include visualizations in export")
    include_raw_data: bool = Field(default=True, description="Include raw data in export")


# Response Schemas

class EnrollmentMetricsSchema(BaseModel):
    """Schema for enrollment metrics."""

    total_enrolled: int
    currently_active: int
    new_enrollments: int
    enrollment_rate: float
    enrollment_sources: Dict[str, int]


class CompletionMetricsSchema(BaseModel):
    """Schema for completion metrics."""

    completed: int
    completion_rate: float
    average_duration_hours: float
    exit_reasons: Dict[str, int]


class ConversionMetricsSchema(BaseModel):
    """Schema for conversion metrics."""

    goals_achieved: int
    conversion_rate: float
    average_time_to_conversion_hours: float
    goal_breakdown: Dict[str, int]


class AnalyticsSummarySchema(BaseModel):
    """Schema for analytics summary."""

    total_enrolled: int
    currently_active: int
    new_enrollments: int
    enrollment_rate: float
    completed: int
    completion_rate: float
    average_duration_hours: float
    goals_achieved: int
    conversion_rate: float
    average_time_to_conversion_hours: float


class TrendDataPointSchema(BaseModel):
    """Schema for trend data point."""

    date: str
    new_enrollments: int
    completions: int
    conversions: int
    total_active: int


class AnalyticsResponseSchema(BaseModel):
    """Schema for complete analytics response."""

    workflow_id: UUID
    period: Dict[str, str]
    summary: AnalyticsSummarySchema
    trends: Optional[List[TrendDataPointSchema]] = None
    comparison: Optional[Dict[str, any]] = None
    generated_at: datetime


class FunnelStepSchema(BaseModel):
    """Schema for funnel step data."""

    step_id: str
    step_name: str
    step_order: int
    entered: int
    completed: int
    dropped_off: int
    conversion_rate: float
    average_time_seconds: int


class FunnelAnalyticsResponseSchema(BaseModel):
    """Schema for funnel analytics response."""

    workflow_id: UUID
    period: Dict[str, str]
    funnel_steps: List[FunnelStepSchema]
    overall_conversion_rate: float
    bottleneck_steps: List[str]
    total_enrolled: int
    final_converted: int


class ActionPerformanceSchema(BaseModel):
    """Schema for action performance data."""

    action_id: str
    action_type: str
    action_name: str
    execution_count: int
    success_count: int
    failure_count: int
    success_rate: float
    error_rate: float
    average_duration_ms: int


class ActionsAnalyticsResponseSchema(BaseModel):
    """Schema for actions analytics response."""

    workflow_id: UUID
    period: Dict[str, str]
    actions: List[ActionPerformanceSchema]


class ExportResponseSchema(BaseModel):
    """Schema for export response."""

    export_id: UUID
    workflow_id: UUID
    format: str
    file_size_bytes: int
    download_url: str
    expires_at: datetime
    created_at: datetime


class ExportStatusSchema(BaseModel):
    """Schema for export job status."""

    export_id: UUID
    status: str
    progress_percent: int
    download_url: Optional[str] = None
    error_message: Optional[str] = None


class RefreshResponseSchema(BaseModel):
    """Schema for analytics refresh response."""

    status: str
    job_id: UUID
    estimated_completion_seconds: int
