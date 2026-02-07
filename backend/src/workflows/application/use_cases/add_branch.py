"""Use case for adding branches to conditions."""

from uuid import UUID

from src.workflows.application.condition_dtos import BranchResponseDTO
from src.workflows.domain.condition_entities import Branch
from src.workflows.domain.condition_value_objects import BranchCriteria
from src.workflows.domain.exceptions import ConditionNotFoundError
from src.workflows.infrastructure.condition_repository import IConditionRepository


class AddBranchUseCase:
    """Use case for adding a new branch to a condition.

    This use case adds a new branch path to an existing condition.
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
        branch_name: str,
        branch_order: int,
        is_default: bool = False,
        percentage: float | None = None,
        next_node_id: UUID | None = None,
        criteria: dict | None = None,
    ) -> BranchResponseDTO:
        """Execute the use case.

        Args:
            condition_id: Condition to add branch to.
            account_id: Account/tenant ID.
            branch_name: Branch display name.
            branch_order: Evaluation priority order.
            is_default: Whether this is default/else branch.
            percentage: Split test percentage.
            next_node_id: Connected next node ID.
            criteria: Branch-specific criteria.

        Returns:
            Created branch.

        Raises:
            ConditionNotFoundError: If condition doesn't exist.
        """
        # Get condition
        condition = await self._condition_repository.get_by_id(condition_id, account_id)
        if condition is None:
            raise ConditionNotFoundError(str(condition_id))

        # Convert criteria dict to BranchCriteria if provided
        branch_criteria: BranchCriteria | None = None
        if criteria:
            branch_criteria = BranchCriteria.from_dict(criteria)

        # Create branch
        branch = Branch.create(
            condition_id=condition_id,
            branch_name=branch_name,
            branch_order=branch_order,
            is_default=is_default,
            percentage=percentage,
            next_node_id=next_node_id,
            criteria=branch_criteria,
        )

        # Add to condition
        condition.add_branch(branch)

        # Persist update
        await self._condition_repository.update(condition)

        return BranchResponseDTO.model_validate(branch.to_dict())
