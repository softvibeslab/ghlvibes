"""
Analytics API routes - SPEC-FUN-004.
10 endpoints for funnel performance tracking.
"""
from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.core.dependencies import get_db, get_current_account
from src.funnels_analytics.application.use_cases import (
    TrackEventUseCase,
    GetFunnelOverviewUseCase,
    GetStepAnalyticsUseCase,
    GetConversionMetricsUseCase,
    GetDropoffAnalysisUseCase,
    GetABTestResultsUseCase,
    GetRevenueMetricsUseCase,
    GetRealTimeAnalyticsUseCase,
    ExportAnalyticsUseCase,
    GetVisitorJourneyUseCase,
)

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


class TrackEventRequest(BaseModel):
    event_type: str
    funnel_id: UUID
    page_id: UUID | None = None
    session_id: str
    visitor_id: UUID
    url: str | None = None
    user_agent: str | None = None
    ip_address: str | None = None
    referrer: str | None = None
    utm_source: str | None = None
    utm_medium: str | None = None
    utm_campaign: str | None = None
    conversion_type: str | None = None
    value_cents: int | None = None
    funnel_step_id: UUID | None = None
    exit_outcome: str | None = None
    next_step_id: UUID | None = None
    metadata: dict = {}


@router.post("/track", status_code=202)
async def track_event(
    data: TrackEventRequest,
    db: AsyncSession = Depends(get_db),
):
    """Track analytics event (async processing)."""
    use_case = TrackEventUseCase(db)
    await use_case.execute(data.dict())
    return {"status": "accepted"}


@router.get("/funnels/{funnel_id}/overview")
async def get_funnel_overview(
    funnel_id: UUID,
    date_from: str,
    date_to: str,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Get funnel overview analytics."""
    use_case = GetFunnelOverviewUseCase(db)
    overview = await use_case.execute(funnel_id, account_id, date_from, date_to)
    if not overview:
        raise HTTPException(status_code=404, detail="Funnel not found")
    return overview


@router.get("/funnels/{funnel_id}/steps/{step_id}")
async def get_step_analytics(
    funnel_id: UUID,
    step_id: UUID,
    date_from: str,
    date_to: str,
    granularity: str = "day",
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Get detailed step analytics."""
    use_case = GetStepAnalyticsUseCase(db)
    analytics = await use_case.execute(funnel_id, step_id, account_id, date_from, date_to, granularity)
    if not analytics:
        raise HTTPException(status_code=404, detail="Step not found")
    return analytics


@router.get("/funnels/{funnel_id}/conversions")
async def get_conversion_metrics(
    funnel_id: UUID,
    date_from: str,
    date_to: str,
    granularity: str = "day",
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Get conversion analytics."""
    use_case = GetConversionMetricsUseCase(db)
    return await use_case.execute(funnel_id, account_id, date_from, date_to, granularity)


@router.get("/funnels/{funnel_id}/dropoffs")
async def get_dropoff_analysis(
    funnel_id: UUID,
    date_from: str,
    date_to: str,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Get drop-off analysis."""
    use_case = GetDropoffAnalysisUseCase(db)
    return await use_case.execute(funnel_id, account_id, date_from, date_to)


@router.get("/funnels/{funnel_id}/ab-tests")
async def get_ab_test_results(
    funnel_id: UUID,
    date_from: str | None = None,
    date_to: str | None = None,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Get A/B test results."""
    use_case = GetABTestResultsUseCase(db)
    return await use_case.execute(funnel_id, account_id, date_from, date_to)


@router.get("/funnels/{funnel_id}/revenue")
async def get_revenue_metrics(
    funnel_id: UUID,
    date_from: str,
    date_to: str,
    granularity: str = "day",
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Get revenue analytics."""
    use_case = GetRevenueMetricsUseCase(db)
    return await use_case.execute(funnel_id, account_id, date_from, date_to, granularity)


@router.get("/funnels/{funnel_id}/realtime")
async def get_realtime_analytics(
    funnel_id: UUID,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Get real-time analytics data."""
    use_case = GetRealTimeAnalyticsUseCase(db)
    return await use_case.execute(funnel_id, account_id)


@router.post("/export")
async def export_analytics(
    funnel_id: UUID,
    report_type: str,
    date_from: str,
    date_to: str,
    format: str = "csv",
    include_charts: bool = False,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Export analytics data."""
    use_case = ExportAnalyticsUseCase(db)
    result = await use_case.execute(account_id, {
        "funnel_id": funnel_id,
        "report_type": report_type,
        "date_from": date_from,
        "date_to": date_to,
        "format": format,
        "include_charts": include_charts,
    })
    return result


@router.get("/visitors/{visitor_id}/journey")
async def get_visitor_journey(
    visitor_id: UUID,
    funnel_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Get complete visitor journey."""
    use_case = GetVisitorJourneyUseCase(db)
    journey = await use_case.execute(visitor_id, account_id, funnel_id)
    if not journey:
        raise HTTPException(status_code=404, detail="Visitor not found")
    return journey
