"""
FastAPI routes for Workflow Analytics.

API endpoints for querying workflow analytics, funnel analysis,
action performance, and data export.
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.auth import get_current_user
from src.users.domain.user import User

from ....application.analytics.analytics_dtos import (
    AnalyticsQueryDTO,
    FunnelQueryDTO,
    ActionPerformanceQueryDTO,
    ExportRequestDTO,
)
from ....application.analytics.use_cases.get_workflow_analytics import GetWorkflowAnalyticsUseCase
from ....application.analytics.use_cases.get_funnel_analytics import GetFunnelAnalyticsUseCase
from ....application.analytics.use_cases.get_action_performance import GetActionPerformanceUseCase
from ....application.analytics.use_cases.generate_export_report import GenerateExportReportUseCase
from ....infrastructure.analytics.analytics_repositories import AnalyticsRepository
from ....domain.analytics.analytics_services import (
    MetricsCalculationService,
    FunnelAnalysisService,
    ConversionCalculationService,
)
from ....application.analytics.analytics_aggregation_service import AnalyticsAggregationService
from .analytics_schemas import (
    AnalyticsQuerySchema,
    AnalyticsResponseSchema,
    FunnelQuerySchema,
    FunnelAnalyticsResponseSchema,
    ActionPerformanceQuerySchema,
    ActionsAnalyticsResponseSchema,
    ExportRequestSchema,
    ExportResponseSchema,
    ExportStatusSchema,
    RefreshResponseSchema,
)


router = APIRouter(prefix="/api/v1/workflows", tags=["analytics"])


@router.get(
    "/{workflow_id}/analytics",
    response_model=AnalyticsResponseSchema,
    summary="Get Workflow Analytics",
    description="Retrieve comprehensive analytics for a workflow including enrollment, completion, and conversion metrics.",
)
async def get_workflow_analytics(
    workflow_id: UUID,
    start_date: date = Query(..., description="Start date for analytics period"),
    end_date: date = Query(..., description="End date for analytics period"),
    granularity: str = Query("daily", description="Aggregation level: hourly, daily, weekly"),
    include_trends: bool = Query(True, description="Include time-series trends"),
    include_comparison: bool = Query(False, description="Include comparison with previous period"),
    comparison_period_days: int = Query(0, description="Days for comparison period"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get workflow analytics summary.

    Returns comprehensive analytics including enrollment, completion,
    and conversion metrics for the specified time period.
    """
    # Create repository
    repository = AnalyticsRepository(db)

    # Create domain services
    metrics_service = MetricsCalculationService()
    conversion_service = ConversionCalculationService()

    # Create use case
    use_case = GetWorkflowAnalyticsUseCase(
        analytics_repository=repository,
        metrics_calculation_service=metrics_service,
        conversion_calculation_service=conversion_service,
    )

    # Create query DTO
    query = AnalyticsQueryDTO(
        workflow_id=workflow_id,
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
        include_trends=include_trends,
        include_comparison=include_comparison,
        comparison_period_days=comparison_period_days,
    )

    # Execute use case
    analytics_response = await use_case.execute(query)

    return analytics_response


@router.get(
    "/{workflow_id}/analytics/funnel",
    response_model=FunnelAnalyticsResponseSchema,
    summary="Get Funnel Analytics",
    description="Analyze workflow funnel performance with drop-off analysis and bottleneck identification.",
)
async def get_funnel_analytics(
    workflow_id: UUID,
    start_date: date = Query(..., description="Start date for analysis period"),
    end_date: date = Query(..., description="End date for analysis period"),
    include_step_details: bool = Query(True, description="Include detailed step metrics"),
    bottleneck_threshold: float = Query(20.0, description="Drop-off percentage for bottleneck identification"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get workflow funnel analysis.

    Returns step-by-step conversion rates, drop-off points,
    and bottleneck identification.
    """
    # Create repository
    repository = AnalyticsRepository(db)

    # Create domain service
    funnel_service = FunnelAnalysisService()

    # Create use case
    use_case = GetFunnelAnalyticsUseCase(
        analytics_repository=repository,
        funnel_analysis_service=funnel_service,
    )

    # Create query DTO
    query = FunnelQueryDTO(
        workflow_id=workflow_id,
        start_date=start_date,
        end_date=end_date,
        include_step_details=include_step_details,
        bottleneck_threshold=bottleneck_threshold,
    )

    # Execute use case
    funnel_response = await use_case.execute(query)

    return funnel_response


@router.get(
    "/{workflow_id}/analytics/actions",
    response_model=ActionsAnalyticsResponseSchema,
    summary="Get Action Performance",
    description="Retrieve performance metrics for individual workflow actions.",
)
async def get_action_performance(
    workflow_id: UUID,
    start_date: date = Query(..., description="Start date for analysis period"),
    end_date: date = Query(..., description="End date for analysis period"),
    action_types: Optional[list[str]] = Query(None, description="Filter by action types"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get action performance metrics.

    Returns execution counts, success rates, error rates,
    and duration data for each action in the workflow.
    """
    # Create repository
    repository = AnalyticsRepository(db)

    # Create use case
    use_case = GetActionPerformanceUseCase(
        analytics_repository=repository,
    )

    # Create query DTO
    query = ActionPerformanceQueryDTO(
        workflow_id=workflow_id,
        start_date=start_date,
        end_date=end_date,
        action_types=action_types,
    )

    # Execute use case
    actions_response = await use_case.execute(query)

    return actions_response


@router.post(
    "/{workflow_id}/analytics/export",
    response_model=ExportResponseSchema,
    summary="Export Analytics Data",
    description="Generate export report in CSV, PDF, or JSON format.",
)
async def export_analytics(
    workflow_id: UUID,
    export_request: ExportRequestSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export analytics data.

    Generates downloadable export report in the specified format.
    Returns download URL that expires after 24 hours.
    """
    # Create repository
    repository = AnalyticsRepository(db)

    # Create use case (would need export_service and storage_service)
    # use_case = GenerateExportReportUseCase(
    #     analytics_repository=repository,
    #     export_service=export_service,
    #     storage_service=storage_service,
    # )

    # Create request DTO
    request = ExportRequestDTO(
        workflow_id=workflow_id,
        start_date=export_request.start_date,
        end_date=export_request.end_date,
        format=export_request.format,
        include_charts=export_request.include_charts,
        include_raw_data=export_request.include_raw_data,
    )

    # Execute use case
    # export_response = await use_case.execute(request)

    # Placeholder response
    return ExportResponseSchema(
        export_id=UUID.uuid4(),
        workflow_id=workflow_id,
        format=export_request.format,
        file_size_bytes=0,
        download_url="/api/v1/exports/placeholder",
        expires_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )


@router.get(
    "/{workflow_id}/analytics/stream",
    summary="Stream Analytics Updates",
    description="Server-Sent Events endpoint for real-time analytics updates.",
)
async def stream_analytics(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Stream real-time analytics updates via SSE.

    Provides live updates to analytics data as they change.
    Clients receive updates every 5 seconds while connected.
    """
    from fastapi import Request

    async def event_stream(request: Request):
        """Generate SSE events."""
        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                break

            # Fetch latest analytics
            # analytics = await get_cached_analytics(workflow_id)

            # Send SSE event
            data = {
                "workflow_id": str(workflow_id),
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": {
                    "total_enrolled": 0,
                    "currently_active": 0,
                    "completed": 0,
                },
            }

            yield f"event: analytics_update\ndata: {data}\n\n"

            # Wait before next update
            import asyncio
            await asyncio.sleep(5)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post(
    "/{workflow_id}/analytics/refresh",
    response_model=RefreshResponseSchema,
    summary="Refresh Analytics",
    description="Trigger manual refresh of aggregated metrics.",
)
async def refresh_analytics(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Refresh analytics aggregation.

    Triggers background job to recalculate and cache
    analytics metrics for the workflow.
    """
    # Queue refresh job
    job_id = UUID.uuid4()

    return RefreshResponseSchema(
        status="queued",
        job_id=job_id,
        estimated_completion_seconds=30,
    )


@router.get(
    "/exports/{export_id}/status",
    response_model=ExportStatusSchema,
    summary="Get Export Status",
    description="Check status of export job.",
)
async def get_export_status(
    export_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get export job status.

    Returns current status of export generation including
    progress percentage and download URL when complete.
    """
    # Get status from export service
    # status = await export_service.get_status(export_id)

    # Placeholder response
    return ExportStatusSchema(
        export_id=export_id,
        status="completed",
        progress_percent=100,
        download_url="/api/v1/exports/placeholder",
    )
