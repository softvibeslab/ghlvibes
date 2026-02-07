"""
Workflow Analytics Application Layer

This module contains the application layer for workflow analytics,
including use cases, DTOs, and application services.

Components:
- Use Cases: GetWorkflowAnalytics, GetFunnelAnalytics, GetActionPerformance, GenerateExportReport
- DTOs: Request/Response data transfer objects
- Services: Aggregation, caching, export generation
"""

from .analytics_dtos import (
    AnalyticsQueryDTO,
    FunnelQueryDTO,
    ActionPerformanceQueryDTO,
    ExportRequestDTO,
    AnalyticsResponseDTO,
    FunnelAnalyticsResponseDTO,
    ActionsAnalyticsResponseDTO,
    ExportResponseDTO,
    ExportStatusDTO,
)

from .analytics_aggregation_service import (
    AnalyticsAggregationService,
    AnalyticsCacheService,
    ExportGenerationService,
)

__all__ = [
    # DTOs
    "AnalyticsQueryDTO",
    "FunnelQueryDTO",
    "ActionPerformanceQueryDTO",
    "ExportRequestDTO",
    "AnalyticsResponseDTO",
    "FunnelAnalyticsResponseDTO",
    "ActionsAnalyticsResponseDTO",
    "ExportResponseDTO",
    "ExportStatusDTO",
    # Services
    "AnalyticsAggregationService",
    "AnalyticsCacheService",
    "ExportGenerationService",
]
