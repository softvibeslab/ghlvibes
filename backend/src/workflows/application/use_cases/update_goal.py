"""Use case for updating goal configurations."""

from uuid import UUID

from src.workflows.application.goal_dtos import (
    GoalResponseDTO,
    UpdateGoalRequestDTO,
)
from src.workflows.domain.exceptions import GoalConfigNotFoundError
from src.workflows.infrastructure.goal_repository import IGoalRepository


class UpdateGoalUseCase:
    """Use case for updating an existing goal configuration.

    This use case updates goal criteria or active state while
    maintaining audit trail with version tracking.
    """

    def __init__(self, goal_repository: IGoalRepository) -> None:
        """Initialize the use case.

        Args:
            goal_repository: Repository for goal configurations.
        """
        self._goal_repository = goal_repository

    async def execute(
        self,
        goal_id: UUID,
        account_id: UUID,
        request_dto: UpdateGoalRequestDTO,
        updated_by: UUID,
    ) -> GoalResponseDTO:
        """Execute the use case.

        Args:
            goal_id: Goal configuration to update.
            account_id: Account/tenant ID.
            request_dto: Update request data.
            updated_by: User making the update.

        Returns:
            Updated goal configuration.

        Raises:
            GoalConfigNotFoundError: If goal doesn't exist.
        """
        # Get existing goal
        goal = await self._goal_repository.get_by_id(goal_id, account_id)
        if goal is None:
            raise GoalConfigNotFoundError(str(goal_id))

        # Update goal
        goal.update(
            updated_by=updated_by,
            criteria=request_dto.criteria,
            is_active=request_dto.is_active,
        )

        # Persist update
        saved_goal = await self._goal_repository.update(goal)

        return GoalResponseDTO.model_validate(saved_goal.to_dict())
