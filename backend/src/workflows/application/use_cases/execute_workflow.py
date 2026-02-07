"""Use case for executing workflows.

This module implements the use case for triggering and executing
workflows for contacts.
"""

from typing import Any
from uuid import UUID

from src.workflows.application.execution_service import (
    ExecutionContext,
    WorkflowExecutionService,
)
from src.workflows.domain.action_entities import Action
from src.workflows.domain.condition_entities import Condition
from src.workflows.domain.entities import Workflow
from src.workflows.domain.execution_entities import WorkflowExecution
from src.workflows.domain.execution_exceptions import WorkflowExecutionError


class ExecuteWorkflowUseCase:
    """Use case for executing workflows.

    This use case orchestrates the execution of a workflow for a specific
    contact, including validation, execution tracking, and error handling.
    """

    def __init__(
        self,
        execution_service: WorkflowExecutionService | None = None,
    ) -> None:
        """Initialize use case.

        Args:
            execution_service: Execution service (optional, uses default if None).
        """
        self.execution_service = execution_service or WorkflowExecutionService()

    async def execute(
        self,
        workflow: Workflow,
        contact_id: UUID,
        contact_data: dict[str, Any],
        actions: list[Action],
        conditions: list[Condition] | None = None,
        trigger_metadata: dict[str, Any] | None = None,
    ) -> WorkflowExecution:
        """Execute workflow for contact.

        Args:
            workflow: Workflow to execute.
            contact_id: Contact to process.
            contact_data: Contact data.
            actions: Workflow actions.
            conditions: Optional conditions.
            trigger_metadata: Trigger event metadata.

        Returns:
            Workflow execution instance.

        Raises:
            WorkflowExecutionError: If execution fails.
        """
        try:
            execution = await self.execution_service.execute_workflow(
                workflow=workflow,
                contact_id=contact_id,
                contact_data=contact_data,
                actions=actions,
                conditions=conditions,
                trigger_metadata=trigger_metadata,
            )

            return execution

        except Exception as e:
            raise WorkflowExecutionError(
                f"Failed to execute workflow {workflow.id}: {str(e)}"
            ) from e

    async def trigger_execution(
        self,
        workflow_id: UUID,
        contact_id: UUID,
        account_id: UUID,
        trigger_metadata: dict[str, Any] | None = None,
    ) -> WorkflowExecution:
        """Trigger workflow execution by ID.

        This is a convenience method that fetches the workflow and
        contact data, then executes the workflow.

        Args:
            workflow_id: Workflow ID to execute.
            contact_id: Contact to process.
            account_id: Account ID.
            trigger_metadata: Trigger event metadata.

        Returns:
            Workflow execution instance.

        Raises:
            WorkflowExecutionError: If execution fails.

        Note:
            This method requires repository dependencies to be injected
            for fetching workflow and contact data.
        """
        # In production, would fetch from repositories
        # workflow = await workflow_repository.get(workflow_id)
        # contact = await contact_repository.get(contact_id)
        # actions = await action_repository.list_by_workflow(workflow_id)
        # conditions = await condition_repository.list_by_workflow(workflow_id)

        raise NotImplementedError(
            "Use execute() method with pre-fetched entities. "
            "This method requires repository dependencies."
        )


class CancelExecutionUseCase:
    """Use case for cancelling workflow executions."""

    def __init__(
        self,
        execution_service: WorkflowExecutionService | None = None,
    ) -> None:
        """Initialize use case.

        Args:
            execution_service: Execution service.
        """
        self.execution_service = execution_service or WorkflowExecutionService()

    async def cancel(
        self,
        execution: WorkflowExecution,
    ) -> WorkflowExecution:
        """Cancel a workflow execution.

        Args:
            execution: Execution to cancel.

        Returns:
            Updated execution.

        Raises:
            WorkflowExecutionError: If cancellation fails.
        """
        try:
            return await self.execution_service.cancel_execution(execution)
        except Exception as e:
            raise WorkflowExecutionError(
                f"Failed to cancel execution {execution.id}: {str(e)}"
            ) from e


class RetryExecutionUseCase:
    """Use case for retrying failed workflow executions."""

    def __init__(
        self,
        execution_service: WorkflowExecutionService | None = None,
    ) -> None:
        """Initialize use case.

        Args:
            execution_service: Execution service.
        """
        self.execution_service = execution_service or WorkflowExecutionService()

    async def retry(
        self,
        execution: WorkflowExecution,
    ) -> WorkflowExecution:
        """Retry a failed workflow execution.

        Args:
            execution: Execution to retry.

        Returns:
            Updated execution.

        Raises:
            WorkflowExecutionError: If retry fails.
        """
        try:
            return await self.execution_service.retry_execution(execution)
        except Exception as e:
            raise WorkflowExecutionError(
                f"Failed to retry execution {execution.id}: {str(e)}"
            ) from e


class GetExecutionStatusUseCase:
    """Use case for getting workflow execution status."""

    async def get_status(
        self,
        execution: WorkflowExecution,
    ) -> dict[str, Any]:
        """Get execution status and details.

        Args:
            execution: Execution instance.

        Returns:
            Dictionary with execution status.
        """
        return execution.to_dict()
