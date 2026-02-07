"""Use case for evaluating conditions."""

import time
from uuid import UUID

from src.workflows.application.condition_dtos import (
    ConditionEvaluationResultDTO,
    EvaluateConditionRequestDTO,
)
from src.workflows.domain.condition_evaluators import (
    ConditionEvaluatorFactory,
    EvaluationContext,
    EvaluationResult,
)
from src.workflows.domain.exceptions import ConditionNotFoundError
from src.workflows.infrastructure.condition_repository import IConditionRepository


class EvaluateConditionUseCase:
    """Use case for evaluating a condition against a contact.

    This use case evaluates a condition configuration using the
    appropriate evaluator strategy and returns the matching branch.
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
        request_dto: EvaluateConditionRequestDTO,
    ) -> ConditionEvaluationResultDTO:
        """Execute the use case.

        Args:
            condition_id: Condition configuration to evaluate.
            account_id: Account/tenant ID.
            request_dto: Evaluation request with contact data.

        Returns:
            Evaluation result with matching branch.

        Raises:
            ConditionNotFoundError: If condition doesn't exist.
        """
        # Get condition configuration
        condition = await self._condition_repository.get_by_id(condition_id, account_id)
        if condition is None:
            raise ConditionNotFoundError(str(condition_id))

        # Start timing
        start_time = time.perf_counter()

        # Create evaluation context
        context = EvaluationContext(
            contact_id=str(request_dto.contact_id),
            contact_data=request_dto.contact_data,
            tags=request_dto.tags,
            pipeline_stages=request_dto.pipeline_stages,
            custom_fields=request_dto.custom_fields,
            email_engagement=request_dto.email_engagement,
            execution_id=str(request_dto.execution_id) if request_dto.execution_id else None,
        )

        # Get appropriate evaluator
        evaluator = ConditionEvaluatorFactory.create(condition.condition_type)

        # Evaluate condition
        result: EvaluationResult = evaluator.evaluate(condition.configuration, context)

        # Calculate duration
        duration_ms = int((time.perf_counter() - start_time) * 1000)

        # Find matching branch based on result
        branch_id: UUID | None = None
        next_node_id: UUID | None = None
        branch_name = "Default"

        if result.match:
            # Find first non-default branch that matches
            for branch in condition.branches:
                if not branch.is_default:
                    branch_id = branch.id
                    next_node_id = branch.next_node_id
                    branch_name = branch.branch_name
                    break
        else:
            # Use default branch
            for branch in condition.branches:
                if branch.is_default:
                    branch_id = branch.id
                    next_node_id = branch.next_node_id
                    branch_name = branch.branch_name
                    break

        # Build response
        return ConditionEvaluationResultDTO(
            result=branch_name,
            branch_id=branch_id,
            next_node_id=next_node_id,
            evaluation_details={
                "match": result.match,
                "inputs": {
                    "contact_id": str(request_dto.contact_id),
                    "contact_data": request_dto.contact_data,
                },
                "evaluation_details": result.details,
            },
            duration_ms=duration_ms,
        )
