"""Use cases for workflow action management.

This module contains the use cases for adding, updating, deleting,
and managing workflow actions.
"""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from src.workflows.application.action_dtos import (
    ActionResponse,
    CreateActionRequest,
    ListActionsResponse,
    ReorderActionsRequest,
    UpdateActionRequest,
)
from src.workflows.domain.action_entities import Action
from src.workflows.domain.action_exceptions import (
    ActionNotFoundError,
    ActionPositionConflictError,
    MaximumActionsExceededError,
    WorkflowMustBeInDraftError,
)
from src.workflows.domain.value_objects import WorkflowStatus
from src.workflows.infrastructure.action_repository import (
    ActionRepository,
    IActionRepository,
)


@dataclass
class CreateActionResult:
    """Result of the create action use case.

    Attributes:
        success: Whether the operation succeeded.
        action: The created action (if successful).
        error: Error message (if failed).
    """

    success: bool
    action: ActionResponse | None = None
    error: str | None = None


@dataclass
class UpdateActionResult:
    """Result of the update action use case.

    Attributes:
        success: Whether the operation succeeded.
        action: The updated action (if successful).
        error: Error message (if failed).
    """

    success: bool
    action: ActionResponse | None = None
    error: str | None = None


@dataclass
class DeleteActionResult:
    """Result of the delete action use case.

    Attributes:
        success: Whether the operation succeeded.
        error: Error message (if failed).
    """

    success: bool
    error: str | None = None


class AddActionUseCase:
    """Use case for adding an action to a workflow."""

    def __init__(
        self,
        action_repository: IActionRepository,
        workflow_repository: Any,  # IWorkflowRepository
    ) -> None:
        """Initialize the use case with dependencies.

        Args:
            action_repository: Repository for action persistence.
            workflow_repository: Repository for workflow access.
        """
        self._action_repository = action_repository
        self._workflow_repository = workflow_repository

    async def execute(
        self,
        request: CreateActionRequest,
        workflow_id: UUID,
        account_id: UUID,
        user_id: UUID,
    ) -> CreateActionResult:
        """Execute the add action use case.

        Args:
            request: The validated create action request.
            workflow_id: The workflow to add the action to.
            account_id: The account the workflow belongs to.
            user_id: The user creating the action.

        Returns:
            CreateActionResult with the outcome.
        """
        # Step 1: Verify workflow exists and belongs to account
        workflow = await self._workflow_repository.get_by_id(workflow_id, account_id)
        if not workflow:
            return CreateActionResult(
                success=False,
                error="Workflow not found",
            )

        # Step 2: Verify workflow is in draft or paused status
        if workflow.status not in [WorkflowStatus.DRAFT, WorkflowStatus.PAUSED]:
            raise WorkflowMustBeInDraftError(
                workflow_id=str(workflow_id),
                workflow_status=workflow.status.value,
            )

        # Step 3: Check maximum actions limit
        current_count = await self._action_repository.count_by_workflow(workflow_id)
        max_actions = 50
        if current_count >= max_actions:
            raise MaximumActionsExceededError(
                current_count=current_count,
                max_count=max_actions,
            )

        # Step 4: Determine position
        if request.position is not None:
            position = request.position
            # Verify no existing action at this position
            existing_actions = await self._action_repository.list_by_workflow(workflow_id)
            existing_positions = {a.position for a in existing_actions}
            if position in existing_positions:
                raise ActionPositionConflictError(position=position)
        else:
            # Auto-assign next position
            max_position = await self._action_repository.get_max_position(workflow_id)
            position = max_position + 1

        # Step 5: Create domain entity
        action = Action.create(
            workflow_id=workflow_id,
            action_type=request.action_type,
            action_config=request.action_config,
            position=position,
            created_by=user_id,
            previous_action_id=request.previous_action_id,
        )

        # Step 6: Persist action
        persisted_action = await self._action_repository.create(action)

        # Step 7: Update links if previous_action_id was provided
        if request.previous_action_id:
            await self._action_repository.update_action_links(
                action_id=request.previous_action_id,
                next_id=persisted_action.id,
            )

        # Step 8: Return success response
        return CreateActionResult(
            success=True,
            action=ActionResponse.from_entity(persisted_action),
        )


class UpdateActionUseCase:
    """Use case for updating an action."""

    def __init__(
        self,
        action_repository: IActionRepository,
        workflow_repository: Any,
    ) -> None:
        """Initialize with repositories."""
        self._action_repository = action_repository
        self._workflow_repository = workflow_repository

    async def execute(
        self,
        action_id: UUID,
        workflow_id: UUID,
        account_id: UUID,
        user_id: UUID,
        action_config: dict[str, Any] | None = None,
        is_enabled: bool | None = None,
        position: int | None = None,
    ) -> UpdateActionResult:
        """Update an action.

        Args:
            action_id: The action to update.
            workflow_id: The workflow the action belongs to.
            account_id: The account the workflow belongs to.
            user_id: The user making the update.
            action_config: New action configuration (optional).
            is_enabled: New enabled state (optional).
            position: New position (optional).

        Returns:
            UpdateActionResult with the outcome.
        """
        # Step 1: Verify workflow exists and belongs to account
        workflow = await self._workflow_repository.get_by_id(workflow_id, account_id)
        if not workflow:
            return UpdateActionResult(
                success=False,
                error="Workflow not found",
            )

        # Step 2: Verify workflow is in draft or paused status
        if workflow.status not in [WorkflowStatus.DRAFT, WorkflowStatus.PAUSED]:
            raise WorkflowMustBeInDraftError(
                workflow_id=str(workflow_id),
                workflow_status=workflow.status.value,
            )

        # Step 3: Get the action
        action = await self._action_repository.get_by_id(action_id, workflow_id)
        if not action:
            return UpdateActionResult(
                success=False,
                error="Action not found",
            )

        # Step 4: Update the entity
        action.update(
            updated_by=user_id,
            action_config=action_config,
            is_enabled=is_enabled,
            position=position,
        )

        # Step 5: Persist changes
        updated_action = await self._action_repository.update(action)

        # Step 6: Return success response
        return UpdateActionResult(
            success=True,
            action=ActionResponse.from_entity(updated_action),
        )


class DeleteActionUseCase:
    """Use case for deleting an action."""

    def __init__(
        self,
        action_repository: IActionRepository,
        workflow_repository: Any,
    ) -> None:
        """Initialize with repositories."""
        self._action_repository = action_repository
        self._workflow_repository = workflow_repository

    async def execute(
        self,
        action_id: UUID,
        workflow_id: UUID,
        account_id: UUID,
        user_id: UUID,
    ) -> DeleteActionResult:
        """Delete an action.

        Args:
            action_id: The action to delete.
            workflow_id: The workflow the action belongs to.
            account_id: The account the workflow belongs to.
            user_id: The user deleting the action.

        Returns:
            DeleteActionResult with the outcome.
        """
        # Step 1: Verify workflow exists and belongs to account
        workflow = await self._workflow_repository.get_by_id(workflow_id, account_id)
        if not workflow:
            return DeleteActionResult(
                success=False,
                error="Workflow not found",
            )

        # Step 2: Verify workflow is in draft or paused status
        if workflow.status not in [WorkflowStatus.DRAFT, WorkflowStatus.PAUSED]:
            raise WorkflowMustBeInDraftError(
                workflow_id=str(workflow_id),
                workflow_status=workflow.status.value,
            )

        # Step 3: Get the action to update links
        action = await self._action_repository.get_by_id(action_id, workflow_id)
        if not action:
            return DeleteActionResult(
                success=False,
                error="Action not found",
            )

        # Step 4: Update links before deleting
        if action.previous_action_id:
            # Link previous action to next action
            await self._action_repository.update_action_links(
                action_id=action.previous_action_id,
                next_id=action.next_action_id,
            )
        if action.next_action_id:
            # Link next action to previous action
            await self._action_repository.update_action_links(
                action_id=action.next_action_id,
                previous_id=action.previous_action_id,
            )

        # Step 5: Delete the action
        deleted = await self._action_repository.delete(action_id, workflow_id)

        if not deleted:
            return DeleteActionResult(
                success=False,
                error="Failed to delete action",
            )

        return DeleteActionResult(success=True)


class ListActionsUseCase:
    """Use case for listing workflow actions."""

    def __init__(self, action_repository: IActionRepository) -> None:
        """Initialize with repository."""
        self._action_repository = action_repository

    async def execute(
        self,
        workflow_id: UUID,
        account_id: UUID,
        include_disabled: bool = False,
    ) -> ListActionsResponse:
        """List actions for a workflow.

        Args:
            workflow_id: The workflow to list actions for.
            account_id: The account the workflow belongs to (for ownership verification).
            include_disabled: Whether to include disabled actions.

        Returns:
            ListActionsResponse with actions.
        """
        # Note: We don't verify workflow ownership here for performance,
        # but we do verify it in the API layer

        actions = await self._action_repository.list_by_workflow(
            workflow_id=workflow_id,
            include_disabled=include_disabled,
        )

        return ListActionsResponse(
            items=[ActionResponse.from_entity(a) for a in actions],
            total=len(actions),
            workflow_id=workflow_id,
        )


class ReorderActionsUseCase:
    """Use case for reordering actions in a workflow."""

    def __init__(
        self,
        action_repository: IActionRepository,
        workflow_repository: Any,
    ) -> None:
        """Initialize with repositories."""
        self._action_repository = action_repository
        self._workflow_repository = workflow_repository

    async def execute(
        self,
        request: ReorderActionsRequest,
        workflow_id: UUID,
        account_id: UUID,
        user_id: UUID,
    ) -> None:
        """Reorder actions in a workflow.

        Args:
            request: The reorder request with action positions.
            workflow_id: The workflow containing the actions.
            account_id: The account the workflow belongs to.
            user_id: The user reordering the actions.
        """
        # Step 1: Verify workflow exists and belongs to account
        workflow = await self._workflow_repository.get_by_id(workflow_id, account_id)
        if not workflow:
            raise ActionNotFoundError(action_id=str(workflow_id))

        # Step 2: Verify workflow is in draft or paused status
        if workflow.status not in [WorkflowStatus.DRAFT, WorkflowStatus.PAUSED]:
            raise WorkflowMustBeInDraftError(
                workflow_id=str(workflow_id),
                workflow_status=workflow.status.value,
            )

        # Step 3: Convert string UUIDs to UUID objects
        action_positions = {
            UUID(k): v for k, v in request.action_positions.items()
        }

        # Step 4: Reorder actions
        await self._action_repository.reorder_actions(
            workflow_id=workflow_id,
            action_positions=action_positions,
        )
