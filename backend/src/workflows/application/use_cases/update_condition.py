"""Use case for updating condition nodes."""

from uuid import UUID

from src.workflows.application.condition_dtos import (
    ConditionResponseDTO,
    UpdateConditionRequestDTO,
)
from src.workflows.domain.condition_entities import Branch, Condition
from src.workflows.domain.condition_exceptions import ConditionValidationError
from src.workflows.domain.condition_value_objects import BranchCriteria, ConditionConfig
from src.workflows.domain.exceptions import ConditionNotFoundError
from src.workflows.infrastructure.condition_repository import IConditionRepository


class UpdateConditionUseCase:
    """Use case for updating an existing condition node.

    This use case updates the condition configuration, position,
    or active state.
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
        request_dto: UpdateConditionRequestDTO,
        updated_by: UUID,
    ) -> ConditionResponseDTO:
        """Execute the use case.

        Args:
            condition_id: Condition configuration to update.
            account_id: Account/tenant ID.
            request_dto: Update request data.
            updated_by: User making the update.

        Returns:
            Updated condition configuration.

        Raises:
            ConditionNotFoundError: If condition doesn't exist.
            ConditionValidationError: If update data is invalid.
        """
        # Get existing condition
        condition = await self._condition_repository.get_by_id(condition_id, account_id)
        if condition is None:
            raise ConditionNotFoundError(str(condition_id))

        # Update configuration if provided
        if request_dto.configuration:
            new_config = ConditionConfig.from_dict(request_dto.configuration)
            condition.update_configuration(new_config)

        # Update position if provided
        if request_dto.position_x is not None:
            condition.position_x = request_dto.position_x
        if request_dto.position_y is not None:
            condition.position_y = request_dto.position_y

        # Update active state if provided
        if request_dto.is_active is not None:
            if request_dto.is_active:
                condition.activate()
            else:
                condition.deactivate()

        # Update branches if provided
        if request_dto.branches:
            # Replace all branches
            new_branches = []
            for b_data in request_dto.branches:
                branch = Branch(
                    id=b_data.get("id", condition.id),  # Use condition ID as fallback
                    condition_id=condition.id,
                    branch_name=b_data["branch_name"],
                    branch_order=b_data["branch_order"],
                    is_default=b_data.get("is_default", False),
                    percentage=b_data.get("percentage"),
                    next_node_id=b_data.get("next_node_id"),
                    criteria=None,  # Will be set in __post_init__
                )
                if b_data.get("criteria"):
                    branch.criteria = BranchCriteria.from_dict(b_data["criteria"])
                new_branches.append(branch)

            # Replace branches (direct assignment for domain update)
            object.__setattr__(condition, "branches", new_branches)
            condition._touch(updated_by)

        # Persist update
        updated_condition = await self._condition_repository.update(condition)

        return ConditionResponseDTO.model_validate(updated_condition.to_dict())
