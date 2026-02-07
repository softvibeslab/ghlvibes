"""Workflow execution service.

This module implements the core workflow execution engine that orchestrates
action execution, handles conditions, manages state transitions, and provides
comprehensive error handling and retry logic.
"""

from typing import Any
from uuid import UUID

from src.workflows.application.action_executor import (
    ActionContext,
    ActionExecutorFactory,
)
from src.workflows.application.retry_service import RetryService
from src.workflows.domain.action_entities import Action
from src.workflows.domain.condition_entities import Condition
from src.workflows.domain.condition_evaluators import (
    ConditionEvaluatorFactory,
    EvaluationContext,
)
from src.workflows.domain.entities import Workflow
from src.workflows.domain.execution_entities import ExecutionLog, WorkflowExecution
from src.workflows.domain.execution_exceptions import (
    ActionExecutionError,
    ConcurrentExecutionLimitError,
    ContactOptedOutError,
    WorkflowExecutionError,
    WorkflowNotActiveError,
)


class ExecutionContext:
    """Context for workflow execution.

    Attributes:
        workflow: Workflow being executed.
        execution: Execution instance.
        contact_data: Contact information.
        actions: List of workflow actions.
        conditions: List of workflow conditions.
        metadata: Additional execution context.
    """

    def __init__(
        self,
        workflow: Workflow,
        execution: WorkflowExecution,
        contact_data: dict[str, Any],
        actions: list[Action],
        conditions: list[Condition] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize execution context.

        Args:
            workflow: Workflow definition.
            execution: Execution instance.
            contact_data: Contact data.
            actions: Workflow actions.
            conditions: Optional conditions.
            metadata: Optional metadata.
        """
        self.workflow = workflow
        self.execution = execution
        self.contact_data = contact_data
        self.actions = actions
        self.conditions = conditions or []
        self.metadata = metadata or {}


class WorkflowExecutionService:
    """Service for executing workflows.

    This service is the core execution engine that:
    - Manages execution lifecycle
    - Executes actions sequentially
    - Evaluates conditions for branching
    - Handles errors and retries
    - Logs execution details
    """

    def __init__(
        self,
        retry_service: RetryService | None = None,
        max_concurrent_per_account: int = 100,
    ) -> None:
        """Initialize execution service.

        Args:
            retry_service: Retry service for failed actions.
            max_concurrent_per_account: Max concurrent executions per account.
        """
        self.retry_service = retry_service or RetryService()
        self.max_concurrent_per_account = max_concurrent_per_account
        self._active_executions: dict[str, int] = {}  # account_id -> count

    async def execute_workflow(
        self,
        workflow: Workflow,
        contact_id: UUID,
        contact_data: dict[str, Any],
        actions: list[Action],
        conditions: list[Condition] | None = None,
        trigger_metadata: dict[str, Any] | None = None,
    ) -> WorkflowExecution:
        """Execute a workflow for a contact.

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
            WorkflowNotActiveError: If workflow is not active.
            ContactOptedOutError: If contact opted out.
            ConcurrentExecutionLimitError: If concurrent limit reached.
        """
        # Validate workflow is active
        if not workflow.is_active:
            raise WorkflowNotActiveError(
                workflow_id=str(workflow.id),
                status=workflow.status.value,
            )

        # Check contact opt-out
        if contact_data.get("opted_out", False):
            raise ContactOptedOutError(contact_id=str(contact_id))

        # Check concurrent execution limit
        await self._check_concurrent_limit(str(workflow.account_id))

        # Create execution instance
        execution = WorkflowExecution.create(
            workflow_id=workflow.id,
            workflow_version=workflow.version,
            contact_id=contact_id,
            account_id=workflow.account_id,
            metadata={
                "trigger": trigger_metadata or {},
            },
        )

        # Create execution context
        context = ExecutionContext(
            workflow=workflow,
            execution=execution,
            contact_data=contact_data,
            actions=actions,
            conditions=conditions or [],
            metadata=trigger_metadata or {},
        )

        # Start execution
        execution.start()
        await self._increment_execution_count(str(workflow.account_id))

        try:
            # Execute workflow steps
            await self._execute_workflow_steps(context)

            # Mark as completed
            execution.complete()

        except Exception as e:
            # Handle execution error
            execution.fail(error_message=str(e))
            raise

        finally:
            await self._decrement_execution_count(str(workflow.account_id))

        return execution

    async def _execute_workflow_steps(self, context: ExecutionContext) -> None:
        """Execute workflow steps sequentially.

        Args:
            context: Execution context.
        """
        actions = self._sort_actions_by_position(context.actions)
        current_index = context.execution.current_step_index

        while current_index < len(actions):
            action = actions[current_index]
            context.execution.set_step(current_index)

            # Check if action is a condition
            if self._is_condition_action(action):
                # Evaluate condition and determine next step
                current_index = await self._execute_condition(
                    context,
                    action,
                    current_index,
                )
            else:
                # Execute regular action
                await self._execute_action(context, action)
                current_index += 1

    async def _execute_action(
        self,
        context: ExecutionContext,
        action: Action,
    ) -> None:
        """Execute a single action.

        Args:
            context: Execution context.
            action: Action to execute.
        """
        # Create action context
        action_context = ActionContext(
            execution_id=context.execution.id,
            contact_id=context.execution.contact_id,
            account_id=context.execution.account_id,
            action_id=action.id,
            action_config=action.action_config.to_dict(),
            metadata=context.metadata,
        )

        # Create execution log
        log = ExecutionLog.create(
            execution_id=context.execution.id,
            step_index=context.execution.current_step_index,
            action_type=action.action_type.value,
            action_config=action.action_config.to_dict(),
        )

        # Get executor
        executor = ActionExecutorFactory.create(action.action_type.value)

        # Execute action with retry logic
        attempt = 0
        max_attempts = 3

        while attempt < max_attempts:
            attempt += 1

            try:
                # Execute action
                result = await executor.execute(action_context)

                if result.success:
                    # Mark log as success
                    log.mark_success(response_data=result.data)
                    break
                # Check if should retry
                elif result.should_retry and attempt < max_attempts:
                    # Calculate retry delay
                    delay_seconds = self.retry_service.calculate_next_retry_delay(
                        attempt,
                    )

                    # In production, would schedule retry here
                    # For now, continue to next attempt
                    continue
                else:
                    # Mark as failed
                    log.mark_failed(
                        error_details={
                            "error": result.error,
                            "attempt": attempt,
                        },
                    )
                    raise ActionExecutionError(
                        action.action_type.value,
                        result.error or "Unknown error",
                    )

            except ActionExecutionError:
                # Re-raise action execution errors
                raise
            except Exception as e:
                # Handle unexpected errors
                if attempt < max_attempts:
                    continue
                else:
                    log.mark_failed(
                        error_details={
                            "error": str(e),
                            "attempt": attempt,
                        },
                    )
                    raise ActionExecutionError(
                        action.action_type.value,
                        str(e),
                    )

        # Store log (in production, would persist to database)
        context.metadata[f"log_{context.execution.current_step_index}"] = log.to_dict()

    async def _execute_condition(
        self,
        context: ExecutionContext,
        action: Action,
        current_index: int,
    ) -> int:
        """Execute a condition and determine next step.

        Args:
            context: Execution context.
            action: Condition action.
            current_index: Current step index.

        Returns:
            Next step index.
        """
        # Find condition node
        condition = next(
            (c for c in context.conditions if c.node_id == UUID(action.action_config.value)),
            None,
        )

        if not condition:
            # Skip if condition not found
            return current_index + 1

        # Create evaluation context
        eval_context = EvaluationContext(
            contact_id=str(context.execution.contact_id),
            contact_data=context.contact_data,
            tags=context.contact_data.get("tags", []),
            pipeline_stages=context.contact_data.get("pipeline_stages", {}),
            custom_fields=context.contact_data.get("custom_fields", {}),
            email_engagement=context.contact_data.get("email_engagement", {}),
            execution_id=str(context.execution.id),
        )

        # Evaluate condition
        evaluator = ConditionEvaluatorFactory.create(condition.condition_type)
        result = evaluator.evaluate(condition.configuration, eval_context)

        # Find matching branch
        if result.match:
            # Find branch by name or use default
            branch = next(
                (b for b in condition.branches if b.branch_name == result.branch_name),
                None,
            ) or next((b for b in condition.branches if b.is_default), None)
        else:
            # Use default branch
            branch = next((b for b in condition.branches if b.is_default), None)

        if branch and branch.next_node_id:
            # Jump to next action in branch
            target_action = next(
                (a for a in context.actions if a.id == branch.next_node_id),
                None,
            )
            if target_action:
                return context.actions.index(target_action)

        # Default: continue to next action
        return current_index + 1

    def _is_condition_action(self, action: Action) -> bool:
        """Check if action is a condition node.

        Args:
            action: Action to check.

        Returns:
            True if action is a condition.
        """
        return action.action_type.value == "condition"

    def _sort_actions_by_position(self, actions: list[Action]) -> list[Action]:
        """Sort actions by position.

        Args:
            actions: Actions to sort.

        Returns:
            Sorted actions.
        """
        return sorted(actions, key=lambda a: a.position)

    async def _check_concurrent_limit(self, account_id: str) -> None:
        """Check if concurrent execution limit is reached.

        Args:
            account_id: Account ID.

        Raises:
            ConcurrentExecutionLimitError: If limit reached.
        """
        current_count = self._active_executions.get(account_id, 0)

        if current_count >= self.max_concurrent_per_account:
            raise ConcurrentExecutionLimitError(
                account_id=account_id,
                current_count=current_count,
                max_limit=self.max_concurrent_per_account,
            )

    async def _increment_execution_count(self, account_id: str) -> None:
        """Increment active execution count for account.

        Args:
            account_id: Account ID.
        """
        self._active_executions[account_id] = (
            self._active_executions.get(account_id, 0) + 1
        )

    async def _decrement_execution_count(self, account_id: str) -> None:
        """Decrement active execution count for account.

        Args:
            account_id: Account ID.
        """
        current = self._active_executions.get(account_id, 0)
        if current > 0:
            self._active_executions[account_id] = current - 1

    async def cancel_execution(
        self,
        execution: WorkflowExecution,
    ) -> WorkflowExecution:
        """Cancel a workflow execution.

        Args:
            execution: Execution to cancel.

        Returns:
            Updated execution.

        Raises:
            InvalidExecutionStatusTransitionError: If cannot cancel.
        """
        execution.cancel()
        return execution

    async def retry_execution(
        self,
        execution: WorkflowExecution,
    ) -> WorkflowExecution:
        """Retry a failed execution.

        Args:
            execution: Execution to retry.

        Returns:
            Updated execution.

        Raises:
            InvalidExecutionStatusTransitionError: If cannot retry.
        """
        if not execution.can_retry:
            raise WorkflowExecutionError(
                f"Execution {execution.id} cannot be retried. "
                f"Status: {execution.status}, Retries: {execution.retry_count}/3"
            )

        execution.retry()
        return execution
