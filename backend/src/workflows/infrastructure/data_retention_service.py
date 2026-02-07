"""Data retention service for workflow analytics.

Manages lifecycle of analytics data according to retention policies:
- Detailed execution logs: 90 days
- Daily aggregated metrics: 2 years
- Monthly summaries: Indefinite
"""

from datetime import UTC, datetime, timedelta
from datetime import date as Date
from typing import Any
from uuid import UUID

from sqlalchemy import and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.workflows.infrastructure.analytics_models import (
    WorkflowAnalyticsModel,
    WorkflowExecutionModel,
    WorkflowStepMetricsModel,
)


class DataRetentionService:
    """Service for managing analytics data retention.

    Implements data lifecycle policies to balance storage costs
    with analytics requirements.
    """

    # Retention periods
    DETAILED_LOGS_RETENTION_DAYS = 90
    DAILY_METRICS_RETENTION_DAYS = 730  # 2 years
    MONTHLY_SUMMARY_RETENTION_DAYS = None  # Indefinite

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session.
        """
        self.session = session

    async def cleanup_old_execution_logs(self) -> dict[str, int]:
        """Clean up detailed execution logs older than retention period.

        Returns:
            Dictionary with cleanup statistics.
        """
        cutoff_date = datetime.now(UTC) - timedelta(
            days=self.DETAILED_LOGS_RETENTION_DAYS
        )

        # Delete old executions
        query = delete(WorkflowExecutionModel).where(
            WorkflowExecutionModel.enrolled_at < cutoff_date
        )

        result = await self.session.execute(query)
        deleted_count = result.rowcount

        await self.session.commit()

        return {
            "deleted_executions": deleted_count,
            "cutoff_date": cutoff_date.isoformat(),
        }

    async def cleanup_old_daily_metrics(self) -> dict[str, int]:
        """Clean up daily metrics older than retention period.

        Note: Monthly summaries should be created before cleanup.

        Returns:
            Dictionary with cleanup statistics.
        """
        cutoff_date = Date.today() - timedelta(
            days=self.DAILY_METRICS_RETENTION_DAYS
        )

        # Delete old daily metrics (keep only monthly)
        query = delete(WorkflowAnalyticsModel).where(
            and_(
                WorkflowAnalyticsModel.date < cutoff_date,
                # Keep first day of each month (monthly summary)
                WorkflowAnalyticsModel.date != WorkflowAnalyticsModel.date.replace(day=1),
            )
        )

        result = await self.session.execute(query)
        deleted_count = result.rowcount

        await self.session.commit()

        return {
            "deleted_metrics": deleted_count,
            "cutoff_date": cutoff_date.isoformat(),
        }

    async def create_monthly_summaries(
        self,
        workflow_id: UUID,
        year: int,
        month: int,
    ) -> dict[str, Any]:
        """Create monthly summary metrics.

        Aggregates daily metrics into monthly summary.

        Args:
            workflow_id: Workflow identifier.
            year: Year for summary.
            month: Month for summary.

        Returns:
            Summary metrics dictionary.
        """
        # Get first and last day of month
        first_day = Date(year, month, 1)
        if month == 12:
            last_day = Date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = Date(year, month + 1, 1) - timedelta(days=1)

        # Query daily metrics for month
        query = select(WorkflowAnalyticsModel).where(
            and_(
                WorkflowAnalyticsModel.workflow_id == workflow_id,
                WorkflowAnalyticsModel.date >= first_day,
                WorkflowAnalyticsModel.date <= last_day,
            )
        )

        result = await self.session.execute(query)
        daily_metrics = result.scalars().all()

        if not daily_metrics:
            return {"error": "No data found for period"}

        # Aggregate into monthly summary
        latest = daily_metrics[-1]

        monthly_summary = {
            "workflow_id": str(workflow_id),
            "year": year,
            "month": month,
            "total_enrolled": latest.total_enrolled,
            "new_enrollments": sum(m.new_enrollments for m in daily_metrics),
            "completed": latest.completed,
            "goals_achieved": latest.goals_achieved,
            "completion_rate": float(latest.completion_rate),
            "conversion_rate": float(latest.conversion_rate),
        }

        return monthly_summary

    async def get_retention_stats(self) -> dict[str, Any]:
        """Get statistics about data retention status.

        Returns:
            Dictionary with retention statistics.
        """
        # Count execution logs
        execution_cutoff = datetime.now(UTC) - timedelta(
            days=self.DETAILED_LOGS_RETENTION_DAYS
        )
        recent_executions = await self.session.execute(
            select(func.count(WorkflowExecutionModel.id)).where(
                WorkflowExecutionModel.enrolled_at >= execution_cutoff
            )
        )
        execution_count = recent_executions.scalar() or 0

        # Count daily metrics
        metrics_cutoff = Date.today() - timedelta(
            days=self.DAILY_METRICS_RETENTION_DAYS
        )
        recent_metrics = await self.session.execute(
            select(func.count(WorkflowAnalyticsModel.id)).where(
                WorkflowAnalyticsModel.date >= metrics_cutoff
            )
        )
        metrics_count = recent_metrics.scalar() or 0

        return {
            "detailed_logs_retention_days": self.DETAILED_LOGS_RETENTION_DAYS,
            "daily_metrics_retention_days": self.DAILY_METRICS_RETENTION_DAYS,
            "execution_logs_count": execution_count,
            "daily_metrics_count": metrics_count,
            "execution_cutoff_date": execution_cutoff.isoformat(),
            "metrics_cutoff_date": metrics_cutoff.isoformat(),
        }
