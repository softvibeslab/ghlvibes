"""Use case for listing workflow goals."""

from uuid import UUID

from src.workflows.application.goal_dtos import (
    GoalResponseDTO,
    ListGoalsResponseDTO,
)
from src.workflows.infrastructure.goal_repository import IGoalRepository


class ListGoalsUseCase:
    """Use case for listing goal configurations for a workflow.

    Returns all goals configured for a specific workflow with
    pagination support.
    """

    def __init__(self, goal_repository: IGoalRepository) -> None:
        """Initialize the use case.

        Args:
            goal_repository: Repository for goal configurations.
        """
        self._goal_repository = goal_repository

    async def execute(
        self,
        workflow_id: UUID,
        account_id: UUID,
        offset: int = 0,
        limit: int = 50,
    ) -> ListGoalsResponseDTO:
        """Execute the use case.

        Args:
            workflow_id: Workflow to list goals for.
            account_id: Account/tenant ID.
            offset: Pagination offset.
            limit: Maximum results to return.

        Returns:
            List of goal configurations.
        """
        goals = await self._goal_repository.list_by_workflow(
            workflow_id=workflow_id,
            account_id=account_id,
            offset=offset,
            limit=limit,
        )
        total = await self._goal_repository.count_by_workflow(workflow_id, account_id)

        goal_dtos = [GoalResponseDTO.model_validate(goal.to_dict()) for goal in goals]

        return ListGoalsResponseDTO(
            goals=goal_dtos,
            total=total,
            offset=offset,
            limit=limit,
        )
