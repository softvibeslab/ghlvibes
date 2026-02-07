"""Use case for deleting goal configurations."""

from uuid import UUID

from src.workflows.domain.exceptions import GoalConfigNotFoundError
from src.workflows.infrastructure.goal_repository import IGoalRepository


class DeleteGoalUseCase:
    """Use case for deleting a goal configuration.

    This use case permanently removes a goal configuration
    from the workflow.
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
        deleted_by: UUID,
    ) -> bool:
        """Execute the use case.

        Args:
            goal_id: Goal configuration to delete.
            account_id: Account/tenant ID.
            deleted_by: User deleting the goal.

        Returns:
            True if deleted successfully.

        Raises:
            GoalConfigNotFoundError: If goal doesn't exist.
        """
        # Verify goal exists
        goal = await self._goal_repository.get_by_id(goal_id, account_id)
        if goal is None:
            raise GoalConfigNotFoundError(str(goal_id))

        # Delete goal
        return await self._goal_repository.delete(goal_id, account_id, deleted_by)
