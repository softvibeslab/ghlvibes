"""Use case for creating condition nodes."""

from uuid import UUID

from src.workflows.application.condition_dtos import (
    ConditionResponseDTO,
    CreateConditionRequestDTO,
)
from src.workflows.domain.condition_entities import Branch, Condition
from src.workflows.domain.condition_exceptions import ConditionValidationError
from src.workflows.domain.condition_value_objects import BranchType, ConditionConfig
from src.workflows.domain.exceptions import WorkflowNotFoundError
from src.workflows.infrastructure.condition_repository import IConditionRepository
from src.workflows.infrastructure.repositories import IWorkflowRepository


class CreateConditionUseCase:
    """Use case for creating a new condition node.

    This use case validates the workflow exists, creates the condition
    configuration with branches, and persists it to the database.
    """

    def __init__(
        self,
        condition_repository: IConditionRepository,
        workflow_repository: IWorkflowRepository,
    ) -> None:
        """Initialize the use case.

        Args:
            condition_repository: Repository for condition configurations.
            workflow_repository: Repository for workflows.
        """
        self._condition_repository = condition_repository
        self._workflow_repository = workflow_repository

    async def execute(
        self,
        workflow_id: UUID,
        account_id: UUID,
        request_dto: CreateConditionRequestDTO,
        created_by: UUID,
    ) -> ConditionResponseDTO:
        """Execute the use case.

        Args:
            workflow_id: Workflow to associate condition with.
            account_id: Account/tenant ID.
            request_dto: Condition creation request.
            created_by: User creating the condition.

        Returns:
            Created condition configuration.

        Raises:
            WorkflowNotFoundError: If workflow doesn't exist.
            ConditionValidationError: If condition configuration is invalid.
        """
        # Verify workflow exists
        workflow = await self._workflow_repository.get_by_id(workflow_id, account_id)
        if workflow is None:
            raise WorkflowNotFoundError(str(workflow_id))

        # Validate branch type
        try:
            branch_type = BranchType(request_dto.branch_type)
        except ValueError as exc:
            raise ConditionValidationError(f"Invalid branch type: {request_dto.branch_type}") from exc

        # Create condition configuration
        config = ConditionConfig.from_dict(request_dto.configuration)

        # Convert branch DTOs to domain entities if provided
        branches: list[Branch] | None = None
        if request_dto.branches:
            branches = [
                Branch.create(
                    condition_id=workflow_id,  # Temporary, will be updated
                    branch_name=b["branch_name"],
                    branch_order=b["branch_order"],
                    is_default=b.get("is_default", False),
                    percentage=b.get("percentage"),
                    next_node_id=b.get("next_node_id"),
                    criteria=b.get("criteria"),
                )
                for b in request_dto.branches
            ]

        # Create condition entity
        condition = Condition.create(
            workflow_id=workflow_id,
            node_id=request_dto.node_id,
            condition_type=request_dto.condition_type,
            branch_type=branch_type,
            configuration=config,
            position_x=request_dto.position_x,
            position_y=request_dto.position_y,
            created_by=created_by,
            branches=branches,
        )

        # Persist condition
        saved_condition = await self._condition_repository.create(condition)

        return ConditionResponseDTO.model_validate(saved_condition.to_dict())
