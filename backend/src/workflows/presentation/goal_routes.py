"""FastAPI routes for goal tracking endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.workflows.application.goal_dtos import (
    CreateGoalRequestDTO,
    GoalResponseDTO,
    ListGoalsResponseDTO,
    UpdateGoalRequestDTO,
)
from src.workflows.application.use_cases.create_goal import CreateGoalUseCase
from src.workflows.application.use_cases.delete_goal import DeleteGoalUseCase
from src.workflows.application.use_cases.get_goal_stats import GetGoalStatsUseCase
from src.workflows.application.use_cases.list_goals import ListGoalsUseCase
from src.workflows.application.use_cases.update_goal import UpdateGoalUseCase
from src.workflows.presentation.dependencies import get_current_user_id


router = APIRouter(prefix="/api/v1/workflows", tags=["goals"])


@router.post(
    "/{workflow_id}/goals",
    response_model=GoalResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Configure a workflow goal",
    description="Create a new goal configuration for a workflow to track contact behavior.",
)
async def create_goal(
    workflow_id: UUID,
    request_dto: CreateGoalRequestDTO,
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
    current_user_id: UUID = Depends(get_current_user_id),  # noqa: B008
    create_goal_uc: CreateGoalUseCase = Depends(CreateGoalUseCase),  # noqa: B008
) -> GoalResponseDTO:
    """Create a new goal configuration for a workflow.
    Args:
        workflow_id: Workflow to associate goal with.
        request_dto: Goal creation request.
        account_id: Account/tenant ID.
        current_user_id: User creating the goal.
        create_goal_uc: Create goal use case.
    Returns:
        Created goal configuration.
    """
    return await create_goal_uc.execute(
        workflow_id=workflow_id,
        account_id=account_id,
        request_dto=request_dto,
        created_by=current_user_id,
    )


@router.get(
    "/{workflow_id}/goals",
    response_model=ListGoalsResponseDTO,
    summary="List workflow goals",
    description="Retrieve all goal configurations for a specific workflow.",
)
async def list_goals(
    workflow_id: UUID,
    offset: int = 0,
    limit: int = 50,
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
    list_goals_uc: ListGoalsUseCase = Depends(ListGoalsUseCase),  # noqa: B008
) -> ListGoalsResponseDTO:
    """List all goal configurations for a workflow.
    Args:
        workflow_id: Workflow to list goals for.
        offset: Pagination offset.
        limit: Maximum results to return.
        account_id: Account/tenant ID.
        list_goals_uc: List goals use case.
    Returns:
        List of goal configurations.
    """
    return await list_goals_uc.execute(
        workflow_id=workflow_id,
        account_id=account_id,
        offset=offset,
        limit=limit,
    )


@router.patch(
    "/{workflow_id}/goals/{goal_id}",
    response_model=GoalResponseDTO,
    summary="Update a workflow goal",
    description="Update goal criteria or active state for a specific goal configuration.",
)
async def update_goal(
    workflow_id: UUID,  # noqa: ARG001
    goal_id: UUID,
    request_dto: UpdateGoalRequestDTO,
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
    current_user_id: UUID = Depends(get_current_user_id),  # noqa: B008
    update_goal_uc: UpdateGoalUseCase = Depends(UpdateGoalUseCase),  # noqa: B008
) -> GoalResponseDTO:
    """Update a goal configuration.
    Args:
        workflow_id: Workflow ID (for routing).
        goal_id: Goal configuration to update.
        request_dto: Update request data.
        account_id: Account/tenant ID.
        current_user_id: User making the update.
        update_goal_uc: Update goal use case.
    Returns:
        Updated goal configuration.
    """
    return await update_goal_uc.execute(
        goal_id=goal_id,
        account_id=account_id,
        request_dto=request_dto,
        updated_by=current_user_id,
    )


@router.delete(
    "/{workflow_id}/goals/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a workflow goal",
    description="Permanently remove a goal configuration from the workflow.",
)
async def delete_goal(
    workflow_id: UUID,  # noqa: ARG001
    goal_id: UUID,
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
    current_user_id: UUID = Depends(get_current_user_id),  # noqa: B008
    delete_goal_uc: DeleteGoalUseCase = Depends(DeleteGoalUseCase),  # noqa: B008
) -> None:
    """Delete a goal configuration.
    Args:
        workflow_id: Workflow ID (for routing).
        goal_id: Goal configuration to delete.
        account_id: Account/tenant ID.
        current_user_id: User deleting the goal.
        delete_goal_uc: Delete goal use case.
    """
    await delete_goal_uc.execute(
        goal_id=goal_id,
        account_id=account_id,
        deleted_by=current_user_id,
    )


@router.get(
    "/{workflow_id}/goals/stats",
    summary="Get goal statistics",
    description="Retrieve achievement statistics and conversion metrics for workflow goals.",
)
async def get_goal_stats(
    workflow_id: UUID,
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
    get_goal_stats_uc: GetGoalStatsUseCase = Depends(GetGoalStatsUseCase),  # noqa: B008
):
    """Get goal achievement statistics.
    Args:
        workflow_id: Workflow to get stats for.
        account_id: Account/tenant ID.
        get_goal_stats_uc: Get goal stats use case.
    Returns:
        Goal statistics including conversion rates.
    """
    return await get_goal_stats_uc.execute(
        workflow_id=workflow_id,
        account_id=account_id,
    )
