"""Use case for deleting condition nodes."""

from uuid import UUID

from src.workflows.domain.exceptions import ConditionNotFoundError
from src.workflows.infrastructure.condition_repository import IConditionRepository


class DeleteConditionUseCase:
    """Use case for deleting a condition node.

    This use case removes a condition configuration and its branches
    from the workflow.
    """

    def __init__(self, condition_repository: IConditionRepository) -> None:
        """Initialize the use case.

        Args:
            condition_repository: Repository for condition configurations.
        """
        self._condition_repository = condition_repository

    async def execute(
        self,
        condition_id: UUID,
        account_id: UUID,
        deleted_by: UUID,
    ) -> None:
        """Execute the use case.

        Args:
            condition_id: Condition configuration to delete.
            account_id: Account/tenant ID.
            deleted_by: User deleting the condition.

        Raises:
            ConditionNotFoundError: If condition doesn't exist.
        """
        # Verify condition exists before deletion
        condition = await self._condition_repository.get_by_id(condition_id, account_id)
        if condition is None:
            raise ConditionNotFoundError(str(condition_id))

        # Delete condition
        await self._condition_repository.delete(condition_id, account_id, deleted_by)
