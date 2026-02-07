"""Repository implementations for workflow analytics.

Repositories handle data access and persistence for analytics entities.
They abstract database operations and provide query interfaces.
"""

from datetime import UTC, datetime
from datetime import date as Date
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import and_, asc, case, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.workflows.infrastructure.analytics_models import (
    WorkflowAnalyticsModel,
    WorkflowExecutionModel,
    WorkflowStepMetricsModel,
)


class AnalyticsRepository:
    """Repository for workflow analytics data access.

    Provides methods for querying and storing analytics metrics.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session.
        """
        self.session = session

    async def get_workflow_analytics(
        self,
        workflow_id: UUID,
        start_date: Date,
        end_date: Date,
        granularity: str = "daily",
    ) -> dict[str, Any]:
        """Get workflow analytics for date range.

        Args:
            workflow_id: Workflow identifier.
            start_date: Range start.
            end_date: Range end.
            granularity: Time granularity (daily, weekly).

        Returns:
            Dictionary with analytics data including summary and trends.
        """
        # Fetch metrics snapshots
        snapshots = await self._get_snapshots(
            workflow_id=workflow_id,
            start_date=start_date,
            end_date=end_date,
        )

        if not snapshots:
            return self._empty_response(workflow_id, start_date, end_date)

        # Build summary
        summary = self._build_summary(snapshots)

        # Build trends
        trends = self._build_trends(snapshots)

        return {
            "workflow_id": str(workflow_id),
            "summary": summary,
            "trends": trends,
        }

    async def _get_snapshots(
        self,
        workflow_id: UUID,
        start_date: Date,
        end_date: Date,
    ) -> list[WorkflowAnalyticsModel]:
        """Fetch analytics snapshots from database.

        Args:
            workflow_id: Workflow identifier.
            start_date: Range start.
            end_date: Range end.

        Returns:
            List of analytics model instances.
        """
        query = (
            select(WorkflowAnalyticsModel)
            .where(
                and_(
                    WorkflowAnalyticsModel.workflow_id == workflow_id,
                    WorkflowAnalyticsModel.date >= start_date,
                    WorkflowAnalyticsModel.date <= end_date,
                )
            )
            .order_by(asc(WorkflowAnalyticsModel.date))
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    def _build_summary(
        self,
        snapshots: list[WorkflowAnalyticsModel],
    ) -> dict[str, Any]:
        """Build summary metrics from snapshots.

        Args:
            snapshots: List of analytics snapshots.

        Returns:
            Summary dictionary.
        """
        if not snapshots:
            return {}

        latest = snapshots[-1]

        # Sum new enrollments for period
        new_enrollments = sum(s.new_enrollments for s in snapshots)

        # Calculate average duration (from latest snapshot)
        avg_duration_hours = None
        if latest.average_duration_seconds:
            avg_duration_hours = round(
                latest.average_duration_seconds / 3600,
                2,
            )

        # Calculate enrollment rate (per day)
        days = len(snapshots)
        enrollment_rate = round(new_enrollments / days, 2) if days > 0 else 0

        return {
            "total_enrolled": latest.total_enrolled,
            "currently_active": latest.currently_active,
            "new_enrollments": new_enrollments,
            "enrollment_rate": enrollment_rate,
            "enrollment_sources": latest.enrollment_sources,
            "completed": latest.completed,
            "completion_rate": float(latest.completion_rate),
            "average_duration_hours": avg_duration_hours,
            "exit_reasons": latest.exit_reasons,
            "goals_achieved": latest.goals_achieved,
            "conversion_rate": float(latest.conversion_rate),
        }

    def _build_trends(
        self,
        snapshots: list[WorkflowAnalyticsModel],
    ) -> list[dict[str, Any]]:
        """Build trend data from snapshots.

        Args:
            snapshots: List of analytics snapshots.

        Returns:
            List of trend data points.
        """
        return [
            {
                "date": snapshot.date.isoformat(),
                "new_enrollments": snapshot.new_enrollments,
                "completions": snapshot.completed,
                "conversions": snapshot.goals_achieved,
            }
            for snapshot in snapshots
        ]

    def _empty_response(
        self,
        workflow_id: UUID,
        start_date: Date,
        end_date: Date,
    ) -> dict[str, Any]:
        """Return empty analytics response.

        Args:
            workflow_id: Workflow identifier.
            start_date: Range start.
            end_date: Range end.

        Returns:
            Empty response dictionary.
        """
        return {
            "workflow_id": str(workflow_id),
            "summary": {
                "total_enrolled": 0,
                "currently_active": 0,
                "new_enrollments": 0,
                "enrollment_rate": 0,
                "enrollment_sources": {},
                "completed": 0,
                "completion_rate": 0,
                "average_duration_hours": None,
                "exit_reasons": {},
                "goals_achieved": 0,
                "conversion_rate": 0,
            },
            "trends": [],
        }

    async def store_snapshot(
        self,
        snapshot: Any,
    ) -> None:
        """Store analytics snapshot.

        Args:
            snapshot: MetricsSnapshot domain entity.
        """
        model = WorkflowAnalyticsModel(
            id=snapshot.id,
            workflow_id=snapshot.workflow_id,
            account_id=UUID("00000000-0000-0000-0000-000000000000"),  # From workflow
            date=snapshot.date,
            total_enrolled=snapshot.total_enrolled,
            new_enrollments=snapshot.new_enrollments,
            currently_active=snapshot.currently_active,
            completed=snapshot.completed,
            completion_rate=snapshot.completion_rate,
            goals_achieved=snapshot.goals_achieved,
            conversion_rate=snapshot.conversion_rate,
            average_duration_seconds=snapshot.average_duration_seconds,
            enrollment_sources={},
            exit_reasons={},
        )

        self.session.add(model)
        await self.session.flush()


class FunnelMetricsRepository:
    """Repository for funnel analytics data access.

    Provides methods for querying step-level metrics
    and funnel analysis data.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session.
        """
        self.session = session

    async def get_funnel_metrics(
        self,
        workflow_id: UUID,
        start_date: Date,
        end_date: Date,
        include_step_details: bool = True,
    ) -> dict[str, Any]:
        """Get funnel metrics for workflow.

        Args:
            workflow_id: Workflow identifier.
            start_date: Range start.
            end_date: Range end.
            include_step_details: Include detailed step metrics.

        Returns:
            Dictionary with funnel analysis data.
        """
        # Fetch step metrics aggregated over period
        step_metrics = await self._get_aggregated_step_metrics(
            workflow_id=workflow_id,
            start_date=start_date,
            end_date=end_date,
        )

        if not step_metrics:
            return self._empty_funnel_response(workflow_id)

        # Build funnel steps
        steps = self._build_funnel_steps(step_metrics)

        # Calculate overall metrics
        total_enrolled = steps[0]["entered"] if steps else 0
        final_converted = steps[-1]["completed"] if steps else 0

        overall_conversion = 0
        if total_enrolled > 0:
            overall_conversion = round(
                (final_converted / total_enrolled) * 100,
                2,
            )

        # Identify bottleneck
        bottleneck_id = self._identify_bottleneck(steps)

        return {
            "workflow_id": str(workflow_id),
            "total_enrolled": total_enrolled,
            "final_converted": final_converted,
            "overall_conversion_rate": overall_conversion,
            "bottleneck_step_id": bottleneck_id,
            "steps": steps if include_step_details else [],
        }

    async def _get_aggregated_step_metrics(
        self,
        workflow_id: UUID,
        start_date: Date,
        end_date: Date,
    ) -> list[dict[str, Any]]:
        """Fetch aggregated step metrics.

        Args:
            workflow_id: Workflow identifier.
            start_date: Range start.
            end_date: Range end.

        Returns:
            List of aggregated step metrics.
        """
        query = (
            select(
                WorkflowStepMetricsModel.step_id,
                WorkflowStepMetricsModel.step_name,
                WorkflowStepMetricsModel.step_order,
                func.sum(WorkflowStepMetricsModel.entered).label("entered"),
                func.sum(WorkflowStepMetricsModel.completed).label("completed"),
                func.sum(WorkflowStepMetricsModel.dropped_off).label("dropped_off"),
            )
            .where(
                and_(
                    WorkflowStepMetricsModel.workflow_id == workflow_id,
                    WorkflowStepMetricsModel.date >= start_date,
                    WorkflowStepMetricsModel.date <= end_date,
                )
            )
            .group_by(
                WorkflowStepMetricsModel.step_id,
                WorkflowStepMetricsModel.step_name,
                WorkflowStepMetricsModel.step_order,
            )
            .order_by(asc(WorkflowStepMetricsModel.step_order))
        )

        result = await self.session.execute(query)
        rows = result.all()

        return [
            {
                "step_id": str(row.step_id),
                "step_name": row.step_name,
                "step_order": row.step_order,
                "entered": int(row.entered or 0),
                "completed": int(row.completed or 0),
                "dropped_off": int(row.dropped_off or 0),
            }
            for row in rows
        ]

    def _build_funnel_steps(
        self,
        step_metrics: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Build funnel step data with conversions.

        Args:
            step_metrics: Raw aggregated step metrics.

        Returns:
            List of funnel step data with rates.
        """
        steps = []

        for step in step_metrics:
            entered = step["entered"]
            completed = step["completed"]
            dropped_off = step["dropped_off"]

            # Calculate conversion rate
            conversion_rate = 0
            if entered > 0:
                conversion_rate = round((completed / entered) * 100, 2)

            # Calculate drop-off rate
            drop_off_rate = 0
            if entered > 0:
                drop_off_rate = round((dropped_off / entered) * 100, 2)

            steps.append({
                **step,
                "conversion_rate": conversion_rate,
                "drop_off_rate": drop_off_rate,
                "is_bottleneck": drop_off_rate > 30,  # 30% threshold
            })

        return steps

    def _identify_bottleneck(
        self,
        steps: list[dict[str, Any]],
    ) -> str | None:
        """Identify bottleneck step.

        Args:
            steps: Funnel step data.

        Returns:
            Step ID with highest drop-off rate, or None.
        """
        if not steps:
            return None

        # Find step with highest drop-off
        bottleneck = max(steps, key=lambda s: s["drop_off_rate"])

        if bottleneck["drop_off_rate"] > 30:
            return bottleneck["step_id"]

        return None

    def _empty_funnel_response(
        self,
        workflow_id: UUID,
    ) -> dict[str, Any]:
        """Return empty funnel response.

        Args:
            workflow_id: Workflow identifier.

        Returns:
            Empty response dictionary.
        """
        return {
            "workflow_id": str(workflow_id),
            "total_enrolled": 0,
            "final_converted": 0,
            "overall_conversion_rate": 0,
            "bottleneck_step_id": None,
            "steps": [],
        }


class ActionMetricsRepository:
    """Repository for action performance metrics.

    Provides methods for querying per-action execution statistics.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session.
        """
        self.session = session

    async def get_action_metrics(
        self,
        workflow_id: UUID,
        start_date: Date,
        end_date: Date,
        action_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """Get action performance metrics.

        Args:
            workflow_id: Workflow identifier.
            start_date: Range start.
            end_date: Range end.
            action_types: Filter by action types.

        Returns:
            Dictionary with action metrics.
        """
        # This would query action execution tables
        # For now, return placeholder structure
        return {
            "workflow_id": str(workflow_id),
            "actions": [],
        }
