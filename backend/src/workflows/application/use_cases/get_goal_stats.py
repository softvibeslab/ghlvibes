"""Use case for retrieving goal statistics."""

from uuid import UUID

from src.workflows.application.goal_dtos import GoalStatsResponseDTO
from src.workflows.infrastructure.goal_repository import IGoalRepository


class GetGoalStatsUseCase:
    """Use case for retrieving goal achievement statistics.

    Calculates conversion metrics and performance indicators
    for workflow goals.
    """

    def __init__(
        self,
        goal_repository: IGoalRepository,
    ) -> None:
        """Initialize the use case.

        Args:
            goal_repository: Repository for goal data.
        """
        self._goal_repository = goal_repository

    async def execute(
        self,
        workflow_id: UUID,
        account_id: UUID,
    ) -> GoalStatsResponseDTO:
        """Execute the use case.

        Args:
            workflow_id: Workflow to get stats for.
            account_id: Account/tenant ID.

        Returns:
            Goal statistics including conversion rates.
        """
        # Get statistics from repository
        stats = await self._goal_repository.get_statistics(workflow_id, account_id)

        return GoalStatsResponseDTO(
            workflow_id=workflow_id,
            total_enrolled=stats.get("total_enrolled", 0),
            goals_achieved=stats.get("goals_achieved", 0),
            conversion_rate=stats.get("conversion_rate", 0.0),
            avg_time_to_goal_hours=stats.get("avg_time_to_goal_hours"),
            by_goal_type=stats.get("by_goal_type", {}),
        )
