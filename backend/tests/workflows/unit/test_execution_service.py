"""Unit tests for workflow execution service.

These tests verify the WorkflowExecutionService orchestrates
workflow execution correctly.
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.workflows.application.action_executor import (
    ActionContext,
    SendEmailExecutor,
    WaitTimeExecutor,
)
from src.workflows.application.execution_service import WorkflowExecutionService
from src.workflows.application.retry_service import RetryService, RetryStrategy
from src.workflows.domain.action_entities import Action, ActionExecution
from src.workflows.domain.action_value_objects import ActionConfig, ActionType
from src.workflows.domain.condition_entities import Branch, Condition
from src.workflows.domain.condition_value_objects import BranchCriteria, BranchType
from src.workflows.domain.entities import Workflow, WorkflowName, WorkflowStatus
from src.workflows.domain.execution_entities import ExecutionStatus, WorkflowExecution
from src.workflows.domain.execution_exceptions import (
    ConcurrentExecutionLimitError,
    ContactOptedOutError,
    WorkflowNotActiveError,
)


class TestWorkflowExecutionService:
    """Test suite for WorkflowExecutionService."""

    @pytest.fixture
    def execution_service(self) -> WorkflowExecutionService:
        """Fixture for execution service."""
        retry_strategy = RetryStrategy(
            max_attempts=3,
            base_delay_seconds=1,
            max_delay_seconds=60,
        )
        return WorkflowExecutionService(
            retry_service=RetryService(retry_strategy),
            max_concurrent_per_account=100,
        )

    @pytest.fixture
    def workflow(self) -> Workflow:
        """Fixture for test workflow."""
        workflow = Workflow.create(
            account_id=uuid4(),
            name="Test Workflow",
            created_by=uuid4(),
        )
        workflow.activate(updated_by=workflow.created_by)
        return workflow

    @pytest.fixture
    def contact_data(self) -> dict:
        """Fixture for test contact data."""
        return {
            "id": str(uuid4()),
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "tags": ["lead", "newsletter"],
            "opted_out": False,
        }

    @pytest.fixture
    def actions(self, workflow: Workflow) -> list[Action]:
        """Fixture for test actions."""
        action1 = Action.create(
            workflow_id=workflow.id,
            action_type=ActionType.SEND_EMAIL,
            action_config={
                "template_id": "welcome-email",
                "from_email": "noreply@example.com",
                "from_name": "GoHighLevel",
                "subject": "Welcome!",
            },
            position=0,
            created_by=workflow.created_by,
        )

        action2 = Action.create(
            workflow_id=workflow.id,
            action_type=ActionType.WAIT_TIME,
            action_config={"duration": 5, "unit": "minutes"},
            position=1,
            created_by=workflow.created_by,
        )

        return [action1, action2]

    @pytest.fixture
    def contact_id(self) -> str:
        """Fixture for test contact ID."""
        return uuid4()

    @pytest.mark.asyncio
    async def test_execute_workflow_success(
        self,
        execution_service: WorkflowExecutionService,
        workflow: Workflow,
        contact_id: str,
        contact_data: dict,
        actions: list[Action],
    ) -> None:
        """Test successful workflow execution."""
        execution = await execution_service.execute_workflow(
            workflow=workflow,
            contact_id=contact_id,
            contact_data=contact_data,
            actions=actions,
        )

        assert execution.status == ExecutionStatus.COMPLETED
        assert execution.current_step_index == 2  # Both actions executed
        assert execution.started_at is not None
        assert execution.completed_at is not None
        assert execution.error_message is None

    @pytest.mark.asyncio
    async def test_execute_workflow_not_active_fails(
        self,
        execution_service: WorkflowExecutionService,
        workflow: Workflow,
        contact_id: str,
        contact_data: dict,
        actions: list[Action],
    ) -> None:
        """Test that executing inactive workflow fails."""
        # Keep workflow in draft status
        assert workflow.is_draft is True

        with pytest.raises(WorkflowNotActiveError):
            await execution_service.execute_workflow(
                workflow=workflow,
                contact_id=contact_id,
                contact_data=contact_data,
                actions=actions,
            )

    @pytest.mark.asyncio
    async def test_execute_workflow_opted_out_contact_fails(
        self,
        execution_service: WorkflowExecutionService,
        workflow: Workflow,
        contact_id: str,
        actions: list[Action],
    ) -> None:
        """Test that executing for opted-out contact fails."""
        workflow.activate(updated_by=workflow.created_by)

        opted_out_contact_data = {
            "id": str(contact_id),
            "email": "test@example.com",
            "opted_out": True,  # Contact opted out
        }

        with pytest.raises(ContactOptedOutError):
            await execution_service.execute_workflow(
                workflow=workflow,
                contact_id=contact_id,
                contact_data=opted_out_contact_data,
                actions=actions,
            )

    @pytest.mark.asyncio
    async def test_execute_workflow_with_conditions(
        self,
        execution_service: WorkflowExecutionService,
        workflow: Workflow,
        contact_id: str,
        contact_data: dict,
        actions: list[Action],
    ) -> None:
        """Test workflow execution with conditional branching."""
        from src.workflows.domain.condition_value_objects import ConditionConfig, ConditionType

        # Create a condition
        condition = Condition.create(
            workflow_id=workflow.id,
            node_id=uuid4(),
            condition_type=ConditionType.CONTACT_HAS_TAG,
            branch_type=BranchType.IF_ELSE,
            configuration=ConditionConfig(
                condition_type=ConditionType.CONTACT_HAS_TAG,
                tags=["lead"],
                operator="has_any_tag",
            ),
            position_x=0,
            position_y=0,
            created_by=workflow.created_by,
        )

        # Add condition action
        condition_action = Action.create(
            workflow_id=workflow.id,
            action_type=ActionType.CONDITION,
            action_config={"condition_id": str(condition.id)},
            position=0,
            created_by=workflow.created_by,
        )

        # Reorder actions
        actions_with_condition = [condition_action] + actions

        execution = await execution_service.execute_workflow(
            workflow=workflow,
            contact_id=contact_id,
            contact_data=contact_data,
            actions=actions_with_condition,
            conditions=[condition],
        )

        assert execution.status == ExecutionStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_cancel_execution(
        self,
        execution_service: WorkflowExecutionService,
        workflow: Workflow,
        contact_id: str,
        contact_data: dict,
        actions: list[Action],
    ) -> None:
        """Test cancelling an execution."""
        execution = WorkflowExecution.create(
            workflow_id=workflow.id,
            workflow_version=workflow.version,
            contact_id=contact_id,
            account_id=workflow.account_id,
        )
        execution.start()

        # Cancel execution
        cancelled = await execution_service.cancel_execution(execution)

        assert cancelled.status == ExecutionStatus.CANCELLED
        assert cancelled.completed_at is not None

    @pytest.mark.asyncio
    async def test_retry_execution(
        self,
        execution_service: WorkflowExecutionService,
        workflow: Workflow,
        contact_id: str,
    ) -> None:
        """Test retrying a failed execution."""
        execution = WorkflowExecution.create(
            workflow_id=workflow.id,
            workflow_version=workflow.version,
            contact_id=contact_id,
            account_id=workflow.account_id,
        )
        execution.start()
        execution.fail("Action failed")

        # Retry execution
        retried = await execution_service.retry_execution(execution)

        assert retried.status == ExecutionStatus.QUEUED
        assert retried.retry_count == 1
        assert retried.error_message is None
        assert retried.current_step_index == 0

    @pytest.mark.asyncio
    async def test_retry_execution_exhausted_retries_fails(
        self,
        execution_service: WorkflowExecutionService,
        workflow: Workflow,
        contact_id: str,
    ) -> None:
        """Test that retrying after max retries fails."""
        execution = WorkflowExecution.create(
            workflow_id=workflow.id,
            workflow_version=workflow.version,
            contact_id=contact_id,
            account_id=workflow.account_id,
        )
        execution.start()
        execution.fail("Action failed")

        # Retry 3 times (max)
        await execution_service.retry_execution(execution)
        await execution_service.retry_execution(execution)
        await execution_service.retry_execution(execution)

        # 4th retry should fail
        assert execution.can_retry is False

    def test_sort_actions_by_position(
        self,
        execution_service: WorkflowExecutionService,
        workflow: Workflow,
    ) -> None:
        """Test sorting actions by position."""
        action1 = Action.create(
            workflow_id=workflow.id,
            action_type=ActionType.SEND_EMAIL,
            action_config={},
            position=2,
            created_by=workflow.created_by,
        )

        action2 = Action.create(
            workflow_id=workflow.id,
            action_type=ActionType.SEND_EMAIL,
            action_config={},
            position=0,
            created_by=workflow.created_by,
        )

        action3 = Action.create(
            workflow_id=workflow.id,
            action_type=ActionType.SEND_EMAIL,
            action_config={},
            position=1,
            created_by=workflow.created_by,
        )

        unsorted_actions = [action1, action2, action3]
        sorted_actions = execution_service._sort_actions_by_position(unsorted_actions)

        assert sorted_actions[0].position == 0
        assert sorted_actions[1].position == 1
        assert sorted_actions[2].position == 2


class TestActionExecutors:
    """Test suite for action executors."""

    @pytest.fixture
    def action_context(self) -> ActionContext:
        """Fixture for action context."""
        return ActionContext(
            execution_id=uuid4(),
            contact_id=uuid4(),
            account_id=uuid4(),
            action_id=uuid4(),
            action_config={
                "template_id": "test-template",
                "from_email": "test@example.com",
                "subject": "Test Email",
            },
        )

    @pytest.mark.asyncio
    async def test_send_email_executor_success(
        self,
        action_context: ActionContext,
    ) -> None:
        """Test successful email sending."""
        executor = SendEmailExecutor()
        result = await executor.execute(action_context)

        assert result.success is True
        assert result.data["template_id"] == "test-template"
        assert result.duration_ms >= 0
        assert result.should_retry is False

    @pytest.mark.asyncio
    async def test_send_email_executor_validation_fails(
        self,
        action_context: ActionContext,
    ) -> None:
        """Test that invalid config raises validation error."""
        executor = SendEmailExecutor()
        invalid_context = ActionContext(
            execution_id=action_context.execution_id,
            contact_id=action_context.contact_id,
            account_id=action_context.account_id,
            action_id=action_context.action_id,
            action_config={},
        )

        with pytest.raises(Exception):  # ActionExecutionError
            await executor.execute(invalid_context)

    @pytest.mark.asyncio
    async def test_wait_time_executor(
        self,
        action_context: ActionContext,
    ) -> None:
        """Test wait time executor."""
        executor = WaitTimeExecutor()
        wait_context = ActionContext(
            execution_id=action_context.execution_id,
            contact_id=action_context.contact_id,
            account_id=action_context.account_id,
            action_id=action_context.action_id,
            action_config={"duration": 5, "unit": "minutes"},
        )

        result = await executor.execute(wait_context)

        assert result.success is True
        assert "resume_at" in result.data
        assert result.data["duration"] == 5
        assert result.data["unit"] == "minutes"


class TestRetryService:
    """Test suite for retry service."""

    def test_calculate_delay_exponential_backoff(self) -> None:
        """Test exponential backoff calculation."""
        strategy = RetryStrategy(
            base_delay_seconds=60,
            max_delay_seconds=3600,
        )

        # Exponential: 60, 120, 240, 480, ...
        assert strategy.calculate_delay(1) == 60
        assert strategy.calculate_delay(2) == 120
        assert strategy.calculate_delay(3) == 240
        assert strategy.calculate_delay(4) == 480

    def test_calculate_delay_max_cap(self) -> None:
        """Test that delay is capped at max."""
        strategy = RetryStrategy(
            base_delay_seconds=60,
            max_delay_seconds=300,
        )

        # Should cap at 300
        assert strategy.calculate_delay(10) == 300

    def test_should_retry_transient_errors(self) -> None:
        """Test that transient errors are retried."""
        strategy = RetryStrategy()

        assert strategy.should_retry(1, error_category="timeout") is True
        assert strategy.should_retry(1, error_category="rate_limit") is True
        assert strategy.should_retry(1, error_category="server_error") is True
        assert strategy.should_retry(1, error_category="network") is True

    def test_should_not_retry_validation_errors(self) -> None:
        """Test that validation errors are not retried."""
        strategy = RetryStrategy()

        assert strategy.should_retry(1, error_category="validation") is False
        assert strategy.should_retry(1, error_category="authentication") is False
        assert strategy.should_retry(1, error_category="authorization") is False

    def test_should_not_retry_after_max_attempts(self) -> None:
        """Test that retries stop after max attempts."""
        strategy = RetryStrategy(max_attempts=3)

        assert strategy.should_retry(1) is True
        assert strategy.should_retry(2) is True
        assert strategy.should_retry(3) is False  # Max attempts reached

    def test_categorize_error(self) -> None:
        """Test error categorization."""
        from src.workflows.application.retry_service import RetryService

        retry_service = RetryService()

        assert retry_service.categorize_error("Validation failed") == "validation"
        assert retry_service.categorize_error("Authentication error") == "authentication"
        assert retry_service.categorize_error("Rate limit exceeded") == "rate_limit"
        assert retry_service.categorize_error("Request timeout") == "timeout"
        assert retry_service.categorize_error("500 Internal Server Error") == "server_error"
