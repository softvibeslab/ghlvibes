"""Use case for listing workflow conditions."""

from uuid import UUID

from src.workflows.application.condition_dtos import (
    ConditionResponseDTO,
    ListConditionsResponseDTO,
)
from src.workflows.infrastructure.condition_repository import IConditionRepository


class ListConditionsUseCase:
    """Use case for listing condition configurations for a workflow.

    This use case retrieves all condition configurations associated
    with a specific workflow.
    """

    def __init__(self, condition_repository: IConditionRepository) -> None:
        """Initialize the use case.

        Args:
            condition_repository: Repository for condition configurations.
        """
        self._condition_repository = condition_repository

    async def execute(
        self,
        workflow_id: UUID,
        account_id: UUID,
        offset: int = 0,
        limit: int = 50,
    ) -> ListConditionsResponseDTO:
        """Execute the use case.

        Args:
            workflow_id: Workflow to list conditions for.
            account_id: Account/tenant ID.
            offset: Pagination offset.
            limit: Maximum results to return.

        Returns:
            List of condition configurations.
        """
        # Get conditions
        conditions = await self._condition_repository.list_by_workflow(
            workflow_id, account_id, offset, limit
        )

        # Get total count
        total = await self._condition_repository.count_by_workflow(workflow_id, account_id)

        # Convert to DTOs
        condition_dtos = [
            ConditionResponseDTO.model_validate(c.to_dict()) for c in conditions
        ]

        return ListConditionsResponseDTO(
            conditions=condition_dtos,
            total=total,
            offset=offset,
            limit=limit,
        )
