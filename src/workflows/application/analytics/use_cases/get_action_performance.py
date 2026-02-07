"""
Use Case: Get Action Performance

Retrieves performance metrics for individual workflow actions,
including execution counts, success rates, and timing data.
"""

from datetime import date
from typing import List
from uuid import UUID

from ...domain.analytics import AnalyticsNotFoundException
from ..analytics_dtos import (
    ActionPerformanceQueryDTO,
    ActionsAnalyticsResponseDTO,
    ActionPerformanceResponseDTO,
)


class GetActionPerformanceUseCase:
    """
    Use case for retrieving action performance analytics.

    Tracks execution metrics for each action in the workflow,
    including success rates, error rates, and duration.
    """

    def __init__(self, analytics_repository):
        self.analytics_repository = analytics_repository

    async def execute(self, query: ActionPerformanceQueryDTO) -> ActionsAnalyticsResponseDTO:
        """
        Execute the use case to retrieve action performance metrics.

        Args:
            query: Action performance query parameters

        Returns:
            ActionsAnalyticsResponseDTO with action performance data

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

        # Fetch action performance data
        action_metrics = await self.analytics_repository.get_action_metrics(
            workflow_id=query.workflow_id,
            start_date=query.start_date,
            end_date=query.end_date,
            action_types=query.action_types,
        )

        # Convert to DTOs
        actions_dto = [
            ActionPerformanceResponseDTO(
                action_id=str(metric['action_id']),
                action_type=metric['action_type'],
                action_name=metric['action_name'],
                execution_count=metric['execution_count'],
                success_count=metric['success_count'],
                failure_count=metric['failure_count'],
                success_rate=float(metric['success_rate']),
                error_rate=float(metric['error_rate']),
                average_duration_ms=metric['average_duration_ms'],
            )
            for metric in action_metrics
        ]

        return ActionsAnalyticsResponseDTO(
            workflow_id=query.workflow_id,
            period={
                "start_date": query.start_date.isoformat(),
                "end_date": query.end_date.isoformat(),
            },
            actions=actions_dto,
        )
