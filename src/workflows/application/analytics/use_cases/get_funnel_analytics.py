"""
Use Case: Get Funnel Analytics

Analyzes workflow funnel performance to identify drop-off points,
bottlenecks, and step-by-step conversion rates.
"""

from datetime import date
from typing import List
from uuid import UUID

from ...domain.analytics import (
    WorkflowFunnelMetrics,
    TimeRange,
    FunnelAnalysisService,
    AnalyticsNotFoundException,
)
from ..analytics_dtos import (
    FunnelQueryDTO,
    FunnelAnalyticsResponseDTO,
    FunnelStepResponseDTO,
)


class GetFunnelAnalyticsUseCase:
    """
    Use case for retrieving funnel analytics.

    Analyzes workflow performance through each step, identifying
    conversion rates and bottlenecks.
    """

    def __init__(
        self,
        analytics_repository,
        funnel_analysis_service: FunnelAnalysisService,
    ):
        self.analytics_repository = analytics_repository
        self.funnel_analysis = funnel_analysis_service

    async def execute(self, query: FunnelQueryDTO) -> FunnelAnalyticsResponseDTO:
        """
        Execute the use case to retrieve funnel analytics.

        Args:
            query: Funnel query parameters

        Returns:
            FunnelAnalyticsResponseDTO with funnel analysis data

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

        # Fetch workflow steps
        step_data = await self.analytics_repository.get_workflow_steps(
            workflow_id=query.workflow_id,
        )

        if not step_data:
            raise AnalyticsNotFoundException(
                f"No steps found for workflow {query.workflow_id}",
                workflow_id=query.workflow_id,
            )

        # Fetch execution data with step progress
        execution_data = await self.analytics_repository.get_execution_data_with_steps(
            workflow_id=query.workflow_id,
            start_date=query.start_date,
            end_date=query.end_date,
        )

        # Perform funnel analysis using domain service
        funnel_metrics = self.funnel_analysis.analyze_funnel(
            workflow_id=query.workflow_id,
            time_range=time_range,
            step_data=step_data,
            execution_data=execution_data,
        )

        # Convert funnel steps to DTOs
        funnel_steps_dto = [
            FunnelStepResponseDTO(
                step_id=str(step.step_id),
                step_name=step.step_name,
                step_order=step.step_order,
                entered=step.entered,
                completed=step.completed,
                dropped_off=step.dropped_off,
                conversion_rate=float(step.step_conversion_rate),
                average_time_seconds=step.average_time_in_step_seconds,
            )
            for step in funnel_metrics.funnel_steps
        ]

        # Calculate total conversions
        final_converted = (
            funnel_metrics.funnel_steps[-1].completed
            if funnel_metrics.funnel_steps
            else 0
        )
        total_enrolled = (
            funnel_metrics.funnel_steps[0].entered
            if funnel_metrics.funnel_steps
            else 0
        )

        # Convert bottleneck steps to strings
        bottleneck_steps_str = [str(uuid) for uuid in funnel_metrics.bottleneck_steps]

        return FunnelAnalyticsResponseDTO(
            workflow_id=query.workflow_id,
            period={
                "start_date": query.start_date.isoformat(),
                "end_date": query.end_date.isoformat(),
            },
            funnel_steps=funnel_steps_dto,
            overall_conversion_rate=float(funnel_metrics.overall_conversion_rate),
            bottleneck_steps=bottleneck_steps_str,
            total_enrolled=total_enrolled,
            final_converted=final_converted,
        )
