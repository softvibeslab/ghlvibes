"""
Repository implementations for Workflow Analytics.

Repositories handle data access and persistence for analytics entities.
"""

from datetime import date, datetime
from typing import List, Dict, Optional, Any
from uuid import UUID
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from .analytics_models import (
    WorkflowAnalyticsModel,
    WorkflowStepMetricsModel,
    WorkflowExecutionModel,
)


class AnalyticsRepository:
    """
    Repository for workflow analytics data access.

    Provides methods for querying and aggregating analytics data.
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_workflow(self, workflow_id: UUID) -> Optional[Dict]:
        """Get workflow by ID."""
        from src.workflows.infrastructure.workflow_models import WorkflowModel

        result = await self.db_session.execute(
            select(WorkflowModel).where(WorkflowModel.id == workflow_id)
        )
        workflow = result.scalar_one_or_none()

        if workflow:
            return {
                "id": workflow.id,
                "name": workflow.name,
                "status": workflow.status,
            }
        return None

    async def get_execution_data(
        self,
        workflow_id: UUID,
        start_date: date,
        end_date: date,
    ) -> List[Dict[str, Any]]:
        """
        Get execution data for analytics calculation.

        Args:
            workflow_id: Workflow identifier
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List of execution records as dictionaries
        """
        query = select(WorkflowExecutionModel).where(
            and_(
                WorkflowExecutionModel.workflow_id == workflow_id,
                WorkflowExecutionModel.enrolled_at >= datetime.combine(start_date, datetime.min.time()),
                WorkflowExecutionModel.enrolled_at <= datetime.combine(end_date, datetime.max.time()),
            )
        )

        result = await self.db_session.execute(query)
        executions = result.scalars().all()

        return [
            {
                "id": e.id,
                "contact_id": e.contact_id,
                "status": e.status,
                "current_step_id": e.current_step_id,
                "enrolled_at": e.enrolled_at,
                "completed_at": e.completed_at,
                "goal_achieved_at": e.goal_achieved_at,
                "enrollment_source": e.enrollment_source,
                "exit_reason": e.exit_reason,
                "steps_entered": e.steps_entered or [],
                "steps_completed": e.steps_completed or [],
                "step_times": e.step_times or {},
            }
            for e in executions
        ]

    async def get_execution_data_with_steps(
        self,
        workflow_id: UUID,
        start_date: date,
        end_date: date,
    ) -> List[Dict[str, Any]]:
        """Get execution data with detailed step progress."""
        # Reuse get_execution_data
        return await self.get_execution_data(workflow_id, start_date, end_date)

    async def get_workflow_steps(self, workflow_id: UUID) -> List[Dict]:
        """Get workflow step configuration."""
        from src.workflows.infrastructure.step_models import WorkflowStepModel

        query = select(WorkflowStepModel).where(
            WorkflowStepModel.workflow_id == workflow_id
        ).order_by(WorkflowStepModel.order)

        result = await self.db_session.execute(query)
        steps = result.scalars().all()

        return [
            {
                "id": str(s.id),
                "name": s.name,
                "type": s.step_type,
                "order": s.order,
                "config": s.config,
            }
            for s in steps
        ]

    async def get_goal_data(
        self,
        workflow_id: UUID,
        start_date: date,
        end_date: date,
    ) -> List[Dict]:
        """Get goal achievement data for conversion metrics."""
        # Query executions with goal achievements
        query = select(WorkflowExecutionModel).where(
            and_(
                WorkflowExecutionModel.workflow_id == workflow_id,
                WorkflowExecutionModel.goal_achieved_at >= datetime.combine(start_date, datetime.min.time()),
                WorkflowExecutionModel.goal_achieved_at <= datetime.combine(end_date, datetime.max.time()),
            )
        )

        result = await self.db_session.execute(query)
        executions = result.scalars().all()

        return [
            {
                "id": e.id,
                "contact_id": e.contact_id,
                "goal_achieved_at": e.goal_achieved_at,
                "enrolled_at": e.enrolled_at,
            }
            for e in executions
            if e.goal_achieved_at
        ]

    async def get_action_metrics(
        self,
        workflow_id: UUID,
        start_date: date,
        end_date: date,
        action_types: Optional[List[str]] = None,
    ) -> List[Dict]:
        """Get action performance metrics."""
        # Query step metrics for actions
        query = select(WorkflowStepMetricsModel).where(
            and_(
                WorkflowStepMetricsModel.workflow_id == workflow_id,
                WorkflowStepMetricsModel.date >= start_date,
                WorkflowStepMetricsModel.date <= end_date,
            )
        )

        result = await self.db_session.execute(query)
        step_metrics = result.scalars().all()

        # Aggregate by action
        action_metrics = {}
        for metric in step_metrics:
            # Group by step_id (representing action)
            if metric.step_id not in action_metrics:
                action_metrics[metric.step_id] = {
                    "action_id": metric.step_id,
                    "execution_count": 0,
                    "success_count": 0,
                    "failure_count": 0,
                    "average_duration_ms": 0,
                }

            action_metrics[metric.step_id]["execution_count"] += metric.executions
            action_metrics[metric.step_id]["success_count"] += metric.successes
            action_metrics[metric.step_id]["failure_count"] += metric.failures

        # Calculate rates
        for metrics in action_metrics.values():
            total = metrics["execution_count"]
            if total > 0:
                metrics["success_rate"] = (metrics["success_count"] / total) * 100
                metrics["error_rate"] = (metrics["failure_count"] / total) * 100
            else:
                metrics["success_rate"] = 0.0
                metrics["error_rate"] = 0.0

        return list(action_metrics.values())

    async def get_trends(
        self,
        workflow_id: UUID,
        start_date: date,
        end_date: date,
        granularity: str = "daily",
    ) -> List[Dict[str, Any]]:
        """Get time-series trends data."""
        query = select(WorkflowAnalyticsModel).where(
            and_(
                WorkflowAnalyticsModel.workflow_id == workflow_id,
                WorkflowAnalyticsModel.date >= start_date,
                WorkflowAnalyticsModel.date <= end_date,
            )
        ).order_by(WorkflowAnalyticsModel.date)

        result = await self.db_session.execute(query)
        analytics = result.scalars().all()

        return [
            {
                "date": a.date,
                "new_enrollments": a.new_enrollments,
                "completions": a.completed,
                "conversions": a.goals_achieved,
                "total_active": a.currently_active,
            }
            for a in analytics
        ]

    async def get_workflow_analytics(
        self,
        workflow_id: UUID,
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        """Get aggregated workflow analytics."""
        # Query daily analytics
        query = select(WorkflowAnalyticsModel).where(
            and_(
                WorkflowAnalyticsModel.workflow_id == workflow_id,
                WorkflowAnalyticsModel.date >= start_date,
                WorkflowAnalyticsModel.date <= end_date,
            )
        )

        result = await self.db_session.execute(query)
        analytics = result.scalars().all()

        # Aggregate across period
        total_enrolled = sum(a.total_enrolled for a in analytics)
        new_enrollments = sum(a.new_enrollments for a in analytics)
        completed = sum(a.completed for a in analytics)
        goals_achieved = sum(a.goals_achieved for a in analytics)

        return {
            "workflow_id": str(workflow_id),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_enrolled": total_enrolled,
            "new_enrollments": new_enrollments,
            "completed": completed,
            "goals_achieved": goals_achieved,
        }

    async def save_analytics(self, analytics: Any) -> None:
        """Save analytics snapshot."""
        model = WorkflowAnalyticsModel(
            workflow_id=analytics.workflow_id,
            date=analytics.snapshot_date,
            total_enrolled=analytics.metrics_data.get("total_enrolled", 0),
            new_enrollments=analytics.metrics_data.get("new_enrollments", 0),
            completed=analytics.metrics_data.get("completed", 0),
            goals_achieved=analytics.metrics_data.get("goals_achieved", 0),
        )

        self.db_session.add(model)
        await self.db_session.commit()


class DataRetentionService:
    """
    Service for managing data retention policies.

    Handles cleanup of old data according to retention rules.
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def cleanup_detailed_logs(self, before_date: date) -> Dict[str, int]:
        """
        Clean up detailed execution logs older than specified date.

        Args:
            before_date: Cutoff date - delete logs before this date

        Returns:
            Dictionary with deletion counts
        """
        cutoff_datetime = datetime.combine(before_date, datetime.min.time())

        # Delete old executions
        delete_query = select(func.count(WorkflowExecutionModel.id)).where(
            WorkflowExecutionModel.enrolled_at < cutoff_datetime
        )

        result = await self.db_session.execute(delete_query)
        count = result.scalar()

        # Perform deletion
        from sqlalchemy import delete
        await self.db_session.execute(
            delete(WorkflowExecutionModel).where(
                WorkflowExecutionModel.enrolled_at < cutoff_datetime
            )
        )
        await self.db_session.commit()

        return {"deleted_count": count}

    def get_cleanup_job_status(self) -> Dict[str, Any]:
        """Get status of scheduled cleanup job."""
        return {
            "enabled": True,
            "schedule": "daily",
            "last_run": datetime.utcnow(),
        }

    async def get_daily_aggregates(self, after_date: date) -> List[Any]:
        """Get daily aggregate data after specified date."""
        query = select(WorkflowAnalyticsModel).where(
            WorkflowAnalyticsModel.date >= after_date
        )

        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def get_monthly_summaries(self) -> List[Any]:
        """Get monthly summary data."""
        # Would require separate monthly summary table
        return []
