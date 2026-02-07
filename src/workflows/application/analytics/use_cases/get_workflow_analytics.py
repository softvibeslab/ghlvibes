"""
Use Case: Get Workflow Analytics

Retrieves comprehensive analytics for a workflow including
enrollment, completion, and conversion metrics.
"""

from datetime import date, datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from ...domain.analytics import (
    WorkflowAnalytics,
    TimeRange,
    MetricsCalculationService,
    ConversionCalculationService,
    AnalyticsNotFoundException,
)
from ..analytics_dtos import (
    AnalyticsQueryDTO,
    AnalyticsResponseDTO,
    TimeSeriesDataPoint,
)


class GetWorkflowAnalyticsUseCase:
    """
    Use case for retrieving workflow analytics.

    Orchestrates the retrieval and calculation of workflow metrics
    from multiple data sources and returns comprehensive analytics.
    """

    def __init__(
        self,
        analytics_repository,
        metrics_calculation_service: MetricsCalculationService,
        conversion_calculation_service: ConversionCalculationService,
    ):
        self.analytics_repository = analytics_repository
        self.metrics_calculation = metrics_calculation_service
        self.conversion_calculation = conversion_calculation_service

    async def execute(self, query: AnalyticsQueryDTO) -> AnalyticsResponseDTO:
        """
        Execute the use case to retrieve workflow analytics.

        Args:
            query: Analytics query parameters

        Returns:
            AnalyticsResponseDTO with complete analytics data

        Raises:
            AnalyticsNotFoundException: If workflow or data not found
        """
        # Validate workflow exists
        workflow = await self.analytics_repository.get_workflow(query.workflow_id)
        if not workflow:
            raise AnalyticsNotFoundException(
                f"Workflow {query.workflow_id} not found",
                workflow_id=query.workflow_id,
            )

        # Create time range
        time_range = TimeRange(
            start_date=query.start_date,
            end_date=query.end_date,
        )

        # Fetch execution data
        execution_data = await self.analytics_repository.get_execution_data(
            workflow_id=query.workflow_id,
            start_date=query.start_date,
            end_date=query.end_date,
        )

        if not execution_data:
            raise AnalyticsNotFoundException(
                f"No analytics data found for workflow {query.workflow_id} in specified range",
                workflow_id=query.workflow_id,
            )

        # Calculate metrics using domain services
        enrollment_metrics = self.metrics_calculation.calculate_enrollment_metrics(
            workflow_id=query.workflow_id,
            time_range=time_range,
            execution_data=execution_data,
        )

        completion_metrics = self.metrics_calculation.calculate_completion_metrics(
            workflow_id=query.workflow_id,
            time_range=time_range,
            execution_data=execution_data,
        )

        # Fetch goal data and calculate conversion metrics
        goal_data = await self.analytics_repository.get_goal_data(
            workflow_id=query.workflow_id,
            start_date=query.start_date,
            end_date=query.end_date,
        )

        conversion_metrics = self.conversion_calculation.calculate_conversion_metrics(
            workflow_id=query.workflow_id,
            time_range=time_range,
            execution_data=execution_data,
            goal_data=goal_data,
        )

        # Build summary
        summary = self._build_summary(
            enrollment_metrics,
            completion_metrics,
            conversion_metrics,
        )

        # Build response
        response = AnalyticsResponseDTO(
            workflow_id=query.workflow_id,
            period={
                "start_date": query.start_date.isoformat(),
                "end_date": query.end_date.isoformat(),
            },
            summary=summary,
        )

        # Add trends if requested
        if query.include_trends:
            response.trends = await self._get_trends(
                workflow_id=query.workflow_id,
                time_range=time_range,
                granularity=query.granularity,
            )

        # Add comparison if requested
        if query.include_comparison and query.comparison_period_days > 0:
            response.comparison = await self._get_comparison(
                workflow_id=query.workflow_id,
                time_range=time_range,
                comparison_days=query.comparison_period_days,
            )

        return response

    def _build_summary(
        self,
        enrollment_metrics,
        completion_metrics,
        conversion_metrics,
    ) -> Dict[str, Any]:
        """Build summary dictionary from metrics."""
        return {
            "total_enrolled": enrollment_metrics.total_enrolled,
            "currently_active": enrollment_metrics.currently_active,
            "new_enrollments": enrollment_metrics.new_enrollments,
            "enrollment_rate": float(enrollment_metrics.enrollment_rate),
            "completed": completion_metrics.completed,
            "completion_rate": float(completion_metrics.completion_rate),
            "average_duration_hours": completion_metrics.average_duration_seconds / 3600,
            "goals_achieved": conversion_metrics.goals_achieved,
            "conversion_rate": float(conversion_metrics.conversion_rate),
            "average_time_to_conversion_hours": conversion_metrics.average_time_to_conversion_seconds / 3600,
        }

    async def _get_trends(
        self,
        workflow_id: UUID,
        time_range: TimeRange,
        granularity: str,
    ) -> List[Dict[str, Any]]:
        """Get time-series trends data."""
        # Fetch aggregated data for trends
        trends_data = await self.analytics_repository.get_trends(
            workflow_id=workflow_id,
            start_date=time_range.start_date,
            end_date=time_range.end_date,
            granularity=granularity,
        )

        return [
            {
                "date": trend["date"].isoformat(),
                "new_enrollments": trend.get("new_enrollments", 0),
                "completions": trend.get("completions", 0),
                "conversions": trend.get("conversions", 0),
                "total_active": trend.get("total_active", 0),
            }
            for trend in trends_data
        ]

    async def _get_comparison(
        self,
        workflow_id: UUID,
        time_range: TimeRange,
        comparison_days: int,
    ) -> Dict[str, Any]:
        """Get comparison with previous period."""
        # Calculate previous period
        period_length = time_range.days_in_range()
        previous_end = time_range.start_date - timedelta(days=1)
        previous_start = previous_end - timedelta(days=period_length - 1)

        # Fetch previous period data
        previous_execution_data = await self.analytics_repository.get_execution_data(
            workflow_id=workflow_id,
            start_date=previous_start,
            end_date=previous_end,
        )

        previous_time_range = TimeRange(
            start_date=previous_start,
            end_date=previous_end,
        )

        # Calculate previous period metrics
        previous_enrollment = self.metrics_calculation.calculate_enrollment_metrics(
            workflow_id=workflow_id,
            time_range=previous_time_range,
            execution_data=previous_execution_data,
        )

        # Calculate percentage changes
        enrollment_change = self._calculate_percentage_change(
            previous_enrollment.new_enrollments,
            time_range.new_enrollments,
        )

        return {
            "previous_period": {
                "start_date": previous_start.isoformat(),
                "end_date": previous_end.isoformat(),
            },
            "metrics": {
                "new_enrollments": previous_enrollment.new_enrollments,
                "enrollment_rate": float(previous_enrollment.enrollment_rate),
            },
            "change_percent": {
                "new_enrollments": enrollment_change,
            },
        }

    def _calculate_percentage_change(self, previous: int, current: int) -> float:
        """Calculate percentage change between periods."""
        if previous == 0:
            return 100.0 if current > 0 else 0.0

        return float(((current - previous) / previous) * 100)
