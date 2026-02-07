"""
Data Retention Service for Workflow Analytics.

Manages lifecycle and cleanup of analytics data according to
retention policies (90 days detailed, 2 years daily aggregates).
"""

from datetime import date, datetime, timedelta
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, func

from .analytics_models import (
    WorkflowAnalyticsModel,
    WorkflowExecutionModel,
    WorkflowStepMetricsModel,
)


class DataRetentionService:
    """
    Service for enforcing data retention policies.

    Automatically cleans up old data according to retention rules:
    - Detailed execution logs: 90 days
    - Daily aggregated metrics: 2 years
    - Monthly summaries: Indefinite
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def cleanup_detailed_logs(self, before_date: date) -> Dict[str, int]:
        """
        Clean up detailed execution logs older than specified date.

        Args:
            before_date: Cutoff date - delete logs before this date

        Returns:
            Dictionary with cleanup results
        """
        cutoff_datetime = datetime.combine(before_date, datetime.min.time())

        # Count executions to delete
        count_query = select(func.count(WorkflowExecutionModel.id)).where(
            WorkflowExecutionModel.enrolled_at < cutoff_datetime
        )
        result = await self.db_session.execute(count_query)
        count = result.scalar() or 0

        # Delete old step metrics
        await self.db_session.execute(
            delete(WorkflowStepMetricsModel).where(
                WorkflowStepMetricsModel.date < before_date
            )
        )

        # Delete old executions
        await self.db_session.execute(
            delete(WorkflowExecutionModel).where(
                WorkflowExecutionModel.enrolled_at < cutoff_datetime
            )
        )

        await self.db_session.commit()

        return {
            "deleted_count": count,
            "cutoff_date": before_date.isoformat(),
        }

    async def cleanup_daily_aggregates(self, before_date: date) -> Dict[str, int]:
        """
        Clean up daily aggregates older than specified date.

        Args:
            before_date: Cutoff date - delete aggregates before this date

        Returns:
            Dictionary with cleanup results
        """
        # Count records to delete
        count_query = select(func.count(WorkflowAnalyticsModel.id)).where(
            WorkflowAnalyticsModel.date < before_date
        )
        result = await self.db_session.execute(count_query)
        count = result.scalar() or 0

        # Delete old daily aggregates
        await self.db_session.execute(
            delete(WorkflowAnalyticsModel).where(
                WorkflowAnalyticsModel.date < before_date
            )
        )

        await self.db_session.commit()

        return {
            "deleted_count": count,
            "cutoff_date": before_date.isoformat(),
        }

    async def enforce_retention_policies(self) -> Dict[str, Any]:
        """
        Enforce all retention policies.

        Returns:
            Summary of cleanup operations performed
        """
        today = date.today()

        # Cleanup detailed logs older than 90 days
        detailed_cutoff = today - timedelta(days=90)
        detailed_cleanup = await self.cleanup_detailed_logs(detailed_cutoff)

        # Cleanup daily aggregates older than 2 years
        aggregates_cutoff = today - timedelta(days=730)  # 2 years
        aggregates_cleanup = await self.cleanup_daily_aggregates(aggregates_cutoff)

        return {
            "detailed_logs": detailed_cleanup,
            "daily_aggregates": aggregates_cleanup,
            "monthly_summaries": "retained_indefinitely",
            "executed_at": datetime.utcnow().isoformat(),
        }

    def get_cleanup_job_status(self) -> Dict[str, Any]:
        """Get status of scheduled cleanup job."""
        return {
            "enabled": True,
            "schedule": "daily",
            "retention_policies": {
                "detailed_logs_days": 90,
                "daily_aggregates_days": 730,  # 2 years
                "monthly_summaries": "indefinite",
            },
        }

    async def get_retention_stats(self) -> Dict[str, Any]:
        """Get statistics about data retention."""
        today = date.today()

        # Count detailed logs
        detailed_count = await self.db_session.execute(
            select(func.count(WorkflowExecutionModel.id))
        )
        detailed_total = detailed_count.scalar() or 0

        # Count daily aggregates
        aggregates_count = await self.db_session.execute(
            select(func.count(WorkflowAnalyticsModel.id))
        )
        aggregates_total = aggregates_count.scalar() or 0

        return {
            "detailed_logs": {
                "total_records": detailed_total,
                "retention_days": 90,
                "cutoff_date": (today - timedelta(days=90)).isoformat(),
            },
            "daily_aggregates": {
                "total_records": aggregates_total,
                "retention_days": 730,
                "cutoff_date": (today - timedelta(days=730)).isoformat(),
            },
            "monthly_summaries": {
                "retention": "indefinite",
            },
        }
