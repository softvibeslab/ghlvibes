"""FastAPI routes for condition/branch endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.workflows.application.condition_dtos import (
    AddBranchRequestDTO,
    BranchResponseDTO,
    ConditionEvaluationResultDTO,
    ConditionResponseDTO,
    EvaluateConditionRequestDTO,
    ListConditionsResponseDTO,
    UpdateConditionRequestDTO,
)
from src.workflows.application.use_cases.add_branch import AddBranchUseCase
from src.workflows.application.use_cases.create_condition import CreateConditionUseCase
from src.workflows.application.use_cases.delete_condition import DeleteConditionUseCase
from src.workflows.application.use_cases.evaluate_condition import EvaluateConditionUseCase
from src.workflows.application.use_cases.list_conditions import ListConditionsUseCase
from src.workflows.application.use_cases.update_condition import UpdateConditionUseCase
from src.workflows.presentation.dependencies import get_current_user_id


router = APIRouter(prefix="/api/v1/workflows", tags=["conditions"])


@router.post(
    "/{workflow_id}/conditions",
    response_model=ConditionResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a condition node",
    description="Add a new conditional branching node to a workflow.",
)
async def create_condition(
    workflow_id: UUID,  # noqa: ARG001
    request_dto: dict,  # Using dict to accept CreateConditionRequestDTO
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
    current_user_id: UUID = Depends(get_current_user_id),  # noqa: B008
    create_condition_uc: CreateConditionUseCase = Depends(CreateConditionUseCase),  # noqa: B008
) -> ConditionResponseDTO:
    """Create a new condition node.

    Args:
        workflow_id: Workflow to add condition to.
        request_dto: Condition creation request.
        account_id: Account/tenant ID.
        current_user_id: User creating the condition.
        create_condition_uc: Create condition use case.

    Returns:
        Created condition configuration.
    """
    from src.workflows.application.condition_dtos import CreateConditionRequestDTO

    typed_dto = CreateConditionRequestDTO.model_validate(request_dto)
    return await create_condition_uc.execute(
        workflow_id=workflow_id,
        account_id=account_id,
        request_dto=typed_dto,
        created_by=current_user_id,
    )


@router.get(
    "/{workflow_id}/conditions",
    response_model=ListConditionsResponseDTO,
    summary="List workflow conditions",
    description="Retrieve all condition configurations for a workflow.",
)
async def list_conditions(
    workflow_id: UUID,  # noqa: ARG001
    offset: int = 0,
    limit: int = 50,
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
    list_conditions_uc: ListConditionsUseCase = Depends(ListConditionsUseCase),  # noqa: B008
) -> ListConditionsResponseDTO:
    """List all condition configurations for a workflow.

    Args:
        workflow_id: Workflow to list conditions for.
        offset: Pagination offset.
        limit: Maximum results to return.
        account_id: Account/tenant ID.
        list_conditions_uc: List conditions use case.

    Returns:
        List of condition configurations.
    """
    return await list_conditions_uc.execute(
        workflow_id=workflow_id,
        account_id=account_id,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{workflow_id}/conditions/{condition_id}",
    response_model=ConditionResponseDTO,
    summary="Get a condition",
    description="Retrieve a specific condition configuration.",
)
async def get_condition(
    workflow_id: UUID,  # noqa: ARG001
    condition_id: UUID,
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
    list_conditions_uc: ListConditionsUseCase = Depends(ListConditionsUseCase),  # noqa: B008
) -> ConditionResponseDTO:
    """Get a specific condition configuration.

    Args:
        workflow_id: Workflow ID (for routing).
        condition_id: Condition configuration ID.
        account_id: Account/tenant ID.
        list_conditions_uc: List conditions use case.

    Returns:
        Condition configuration.
    """
    # Use list use case to get single condition (limit=1)
    result = await list_conditions_uc.execute(
        workflow_id=workflow_id,
        account_id=account_id,
        offset=0,
        limit=1,
    )

    # Find matching condition in results
    for condition in result.conditions:
        if condition.id == condition_id:
            return condition

    from fastapi import HTTPException

    raise HTTPException(status_code=404, detail="Condition not found")


@router.patch(
    "/{workflow_id}/conditions/{condition_id}",
    response_model=ConditionResponseDTO,
    summary="Update a condition",
    description="Update condition configuration, position, or active state.",
)
async def update_condition(
    workflow_id: UUID,  # noqa: ARG001
    condition_id: UUID,
    request_dto: UpdateConditionRequestDTO,
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
    current_user_id: UUID = Depends(get_current_user_id),  # noqa: B008
    update_condition_uc: UpdateConditionUseCase = Depends(UpdateConditionUseCase),  # noqa: B008
) -> ConditionResponseDTO:
    """Update a condition configuration.

    Args:
        workflow_id: Workflow ID (for routing).
        condition_id: Condition configuration to update.
        request_dto: Update request data.
        account_id: Account/tenant ID.
        current_user_id: User making the update.
        update_condition_uc: Update condition use case.

    Returns:
        Updated condition configuration.
    """
    return await update_condition_uc.execute(
        condition_id=condition_id,
        account_id=account_id,
        request_dto=request_dto,
        updated_by=current_user_id,
    )


@router.delete(
    "/{workflow_id}/conditions/{condition_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a condition",
    description="Permanently remove a condition configuration from the workflow.",
)
async def delete_condition(
    workflow_id: UUID,  # noqa: ARG001
    condition_id: UUID,
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
    current_user_id: UUID = Depends(get_current_user_id),  # noqa: B008
    delete_condition_uc: DeleteConditionUseCase = Depends(DeleteConditionUseCase),  # noqa: B008
) -> None:
    """Delete a condition configuration.

    Args:
        workflow_id: Workflow ID (for routing).
        condition_id: Condition configuration to delete.
        account_id: Account/tenant ID.
        current_user_id: User deleting the condition.
        delete_condition_uc: Delete condition use case.
    """
    await delete_condition_uc.execute(
        condition_id=condition_id,
        account_id=account_id,
        deleted_by=current_user_id,
    )


@router.post(
    "/{workflow_id}/conditions/{condition_id}/branches",
    response_model=BranchResponseDTO,
    summary="Add a branch to condition",
    description="Add a new branch path to an existing condition.",
)
async def add_branch(
    workflow_id: UUID,  # noqa: ARG001
    condition_id: UUID,
    request_dto: AddBranchRequestDTO,
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
    add_branch_uc: AddBranchUseCase = Depends(AddBranchUseCase),  # noqa: B008
) -> BranchResponseDTO:
    """Add a new branch to a condition.

    Args:
        workflow_id: Workflow ID (for routing).
        condition_id: Condition to add branch to.
        request_dto: Branch creation request.
        account_id: Account/tenant ID.
        add_branch_uc: Add branch use case.

    Returns:
        Created branch.
    """
    return await add_branch_uc.execute(
        condition_id=condition_id,
        account_id=account_id,
        branch_name=request_dto.branch_name,
        branch_order=request_dto.branch_order,
        is_default=request_dto.is_default,
        percentage=request_dto.percentage,
        next_node_id=request_dto.next_node_id,
        criteria=request_dto.criteria if request_dto.criteria else None,
    )


@router.post(
    "/internal/conditions/{condition_id}/evaluate",
    response_model=ConditionEvaluationResultDTO,
    summary="Evaluate a condition (internal)",
    description="Evaluate a condition against contact data to determine branch path.",
)
async def evaluate_condition(
    condition_id: UUID,
    request_dto: EvaluateConditionRequestDTO,
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
    evaluate_condition_uc: EvaluateConditionUseCase = Depends(EvaluateConditionUseCase),  # noqa: B008
) -> ConditionEvaluationResultDTO:
    """Evaluate a condition against contact data.

    Args:
        condition_id: Condition configuration to evaluate.
        request_dto: Evaluation request with contact data.
        account_id: Account/tenant ID.
        evaluate_condition_uc: Evaluate condition use case.

    Returns:
        Evaluation result with matching branch.
    """
    return await evaluate_condition_uc.execute(
        condition_id=condition_id,
        account_id=account_id,
        request_dto=request_dto,
    )
