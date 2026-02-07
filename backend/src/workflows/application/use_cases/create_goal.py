"""Use case for creating goal configurations."""

from uuid import UUID

from src.workflows.application.goal_dtos import (
    CreateGoalRequestDTO,
    GoalResponseDTO,
)
from src.workflows.domain.exceptions import (
    GoalValidationError,
    WorkflowNotFoundError,
)
from src.workflows.domain.goal_entities import GoalConfig, GoalType
from src.workflows.infrastructure.goal_repository import IGoalRepository
from src.workflows.infrastructure.repositories import IWorkflowRepository


class CreateGoalUseCase:
    """Use case for creating a new goal configuration.

    This use case validates the workflow exists, creates the goal
    configuration, and persists it to the database.
    """

    def __init__(
        self,
        goal_repository: IGoalRepository,
        workflow_repository: IWorkflowRepository,
    ) -> None:
        """Initialize the use case.

        Args:
            goal_repository: Repository for goal configurations.
            workflow_repository: Repository for workflows.
        """
        self._goal_repository = goal_repository
        self._workflow_repository = workflow_repository

    async def execute(
        self,
        workflow_id: UUID,
        account_id: UUID,
        request_dto: CreateGoalRequestDTO,
        created_by: UUID,
    ) -> GoalResponseDTO:
        """Execute the use case.

        Args:
            workflow_id: Workflow to associate goal with.
            account_id: Account/tenant ID.
            request_dto: Goal creation request.
            created_by: User creating the goal.

        Returns:
            Created goal configuration.

        Raises:
            WorkflowNotFoundError: If workflow doesn't exist.
            GoalValidationError: If goal configuration is invalid.
        """
        # Verify workflow exists
        workflow = await self._workflow_repository.get_by_id(workflow_id, account_id)
        if workflow is None:
            raise WorkflowNotFoundError(str(workflow_id))

        # Validate goal type
        try:
            goal_type = GoalType(request_dto.goal_type)
        except ValueError as exc:
            raise GoalValidationError(f"Invalid goal type: {request_dto.goal_type}") from exc

        # Validate criteria based on goal type
        # Note: GoalCriteria value object will validate during GoalConfig.create

        # Create goal configuration
        goal = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=goal_type,
            criteria=request_dto.criteria,
            created_by=created_by,
        )

        # Persist goal
        saved_goal = await self._goal_repository.create(goal)

        return GoalResponseDTO.model_validate(saved_goal.to_dict())
