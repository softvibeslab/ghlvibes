"""Unit tests for action domain entities.

These tests verify the behavior of Action and ActionExecution entities.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from src.workflows.domain.action_entities import Action, ActionExecution, ActionExecutionStatus
from src.workflows.domain.action_exceptions import InvalidActionConfigurationError
from src.workflows.domain.action_value_objects import ActionConfig, ActionType


class TestActionEntity:
    """Test Action domain entity."""

    def test_minimal_action_creation(self) -> None:
        """Test creating action with minimal data."""
        workflow_id = uuid4()
        user_id = uuid4()

        action = Action.create(
            workflow_id=workflow_id,
            action_type="send_email",
            action_config={
                "template_id": "test-id",
                "subject": "Test",
                "from_name": "Test",
                "from_email": "test@example.com",
            },
            position=1,
            created_by=user_id,
        )

        assert action.id is not None
        assert isinstance(action.id, UUID)
        assert action.workflow_id == workflow_id
        assert action.action_type == ActionType.SEND_EMAIL
        assert action.position == 1
        assert action.is_enabled is True
        assert action.created_by == user_id
        assert action.updated_by == user_id
        assert isinstance(action.created_at, datetime)
        assert isinstance(action.updated_at, datetime)

    def test_action_creation_with_all_fields(self) -> None:
        """Test creating action with all fields."""
        workflow_id = uuid4()
        user_id = uuid4()
        previous_id = uuid4()

        action = Action.create(
            workflow_id=workflow_id,
            action_type="wait_time",
            action_config={"duration": 5, "unit": "days"},
            position=2,
            created_by=user_id,
            previous_action_id=previous_id,
            branch_id=uuid4(),
        )

        assert action.previous_action_id == previous_id
        assert action.branch_id is not None
        assert action.action_type == ActionType.WAIT_TIME

    def test_action_creation_invalid_config(self) -> None:
        """Test that invalid config raises error."""
        workflow_id = uuid4()
        user_id = uuid4()

        with pytest.raises(InvalidActionConfigurationError):
            Action.create(
                workflow_id=workflow_id,
                action_type="send_email",
                action_config={},  # Missing required fields
                position=1,
                created_by=user_id,
            )

    def test_action_update_config(self) -> None:
        """Test updating action configuration."""
        workflow_id = uuid4()
        user_id = uuid4()

        action = Action.create(
            workflow_id=workflow_id,
            action_type="send_email",
            action_config={
                "template_id": "old-id",
                "subject": "Old Subject",
                "from_name": "Test",
                "from_email": "test@example.com",
            },
            position=1,
            created_by=user_id,
        )

        initial_version = action.updated_at

        action.update(
            updated_by=user_id,
            action_config={
                "template_id": "new-id",
                "subject": "New Subject",
                "from_name": "Test",
                "from_email": "test@example.com",
            },
        )

        assert action.action_config["template_id"] == "new-id"
        assert action.action_config["subject"] == "New Subject"
        assert action.updated_at > initial_version

    def test_action_enable_disable(self) -> None:
        """Test enabling and disabling action."""
        workflow_id = uuid4()
        user_id = uuid4()

        action = Action.create(
            workflow_id=workflow_id,
            action_type="send_email",
            action_config={
                "template_id": "test-id",
                "subject": "Test",
                "from_name": "Test",
                "from_email": "test@example.com",
            },
            position=1,
            created_by=user_id,
        )

        assert action.is_enabled is True

        action.disable(updated_by=user_id)
        assert action.is_enabled is False
        assert action.updated_by == user_id

        action.enable(updated_by=user_id)
        assert action.is_enabled is True

    def test_action_position_update(self) -> None:
        """Test updating action position."""
        workflow_id = uuid4()
        user_id = uuid4()

        action = Action.create(
            workflow_id=workflow_id,
            action_type="send_email",
            action_config={
                "template_id": "test-id",
                "subject": "Test",
                "from_name": "Test",
                "from_email": "test@example.com",
            },
            position=1,
            created_by=user_id,
        )

        action.update(updated_by=user_id, position=5)
        assert action.position == 5

    def test_action_linking(self) -> None:
        """Test setting previous and next action links."""
        workflow_id = uuid4()
        user_id = uuid4()
        previous_id = uuid4()
        next_id = uuid4()

        action = Action.create(
            workflow_id=workflow_id,
            action_type="send_email",
            action_config={
                "template_id": "test-id",
                "subject": "Test",
                "from_name": "Test",
                "from_email": "test@example.com",
            },
            position=1,
            created_by=user_id,
        )

        action.set_previous_action(previous_id, updated_by=user_id)
        assert action.previous_action_id == previous_id

        action.set_next_action(next_id, updated_by=user_id)
        assert action.next_action_id == next_id

    def test_action_to_dict(self) -> None:
        """Test action serialization to dict."""
        workflow_id = uuid4()
        user_id = uuid4()

        action = Action.create(
            workflow_id=workflow_id,
            action_type="send_email",
            action_config={
                "template_id": "test-id",
                "subject": "Test",
                "from_name": "Test",
                "from_email": "test@example.com",
            },
            position=1,
            created_by=user_id,
        )

        action_dict = action.to_dict()

        assert isinstance(action_dict, dict)
        assert "id" in action_dict
        assert "workflow_id" in action_dict
        assert "action_type" in action_dict
        assert action_dict["action_type"] == "send_email"
        assert action_dict["position"] == 1
        assert action_dict["is_enabled"] is True
        assert "created_at" in action_dict
        assert "updated_at" in action_dict


class TestActionExecutionEntity:
    """Test ActionExecution domain entity."""

    def test_execution_creation(self) -> None:
        """Test creating execution record."""
        workflow_execution_id = uuid4()
        action_id = uuid4()
        contact_id = uuid4()

        execution = ActionExecution(
            id=uuid4(),
            workflow_execution_id=workflow_execution_id,
            action_id=action_id,
            contact_id=contact_id,
        )

        assert execution.status == ActionExecutionStatus.PENDING
        assert execution.is_pending is True
        assert execution.is_running is False
        assert execution.is_completed is False
        assert execution.is_failed is False
        assert execution.started_at is None
        assert execution.completed_at is None
        assert execution.retry_count == 0

    def test_execution_mark_running(self) -> None:
        """Test marking execution as running."""
        execution = ActionExecution(
            id=uuid4(),
            workflow_execution_id=uuid4(),
            action_id=uuid4(),
            contact_id=uuid4(),
        )

        execution.mark_running()

        assert execution.status == ActionExecutionStatus.RUNNING
        assert execution.is_running is True
        assert execution.started_at is not None
        assert isinstance(execution.started_at, datetime)

    def test_execution_mark_completed(self) -> None:
        """Test marking execution as completed."""
        execution = ActionExecution(
            id=uuid4(),
            workflow_execution_id=uuid4(),
            action_id=uuid4(),
            contact_id=uuid4(),
        )

        execution.mark_running()
        result_data = {"sent": True, "message_id": "msg-123"}
        execution.mark_completed(result_data=result_data)

        assert execution.status == ActionExecutionStatus.COMPLETED
        assert execution.is_completed is True
        assert execution.completed_at is not None
        assert execution.result_data == result_data
        assert execution.duration_seconds is not None

    def test_execution_mark_failed(self) -> None:
        """Test marking execution as failed."""
        execution = ActionExecution(
            id=uuid4(),
            workflow_execution_id=uuid4(),
            action_id=uuid4(),
            contact_id=uuid4(),
        )

        execution.mark_running()
        execution.mark_failed("Network timeout")

        assert execution.status == ActionExecutionStatus.FAILED
        assert execution.is_failed is True
        assert execution.completed_at is not None
        assert execution.error_message == "Network timeout"

    def test_execution_mark_scheduled(self) -> None:
        """Test marking execution as scheduled."""
        execution = ActionExecution(
            id=uuid4(),
            workflow_execution_id=uuid4(),
            action_id=uuid4(),
            contact_id=uuid4(),
        )

        scheduled_time = datetime.now(UTC)
        execution.mark_scheduled(scheduled_time)

        assert execution.status == ActionExecutionStatus.SCHEDULED
        assert execution.scheduled_at == scheduled_time

    def test_execution_mark_waiting(self) -> None:
        """Test marking execution as waiting."""
        execution = ActionExecution(
            id=uuid4(),
            workflow_execution_id=uuid4(),
            action_id=uuid4(),
            contact_id=uuid4(),
        )

        execution.mark_waiting()

        assert execution.status == ActionExecutionStatus.WAITING

    def test_execution_mark_skipped(self) -> None:
        """Test marking execution as skipped."""
        execution = ActionExecution(
            id=uuid4(),
            workflow_execution_id=uuid4(),
            action_id=uuid4(),
            contact_id=uuid4(),
        )

        execution.mark_skipped()

        assert execution.status == ActionExecutionStatus.SKIPPED
        assert execution.completed_at is not None

    def test_execution_increment_retry(self) -> None:
        """Test incrementing retry count."""
        execution = ActionExecution(
            id=uuid4(),
            workflow_execution_id=uuid4(),
            action_id=uuid4(),
            contact_id=uuid4(),
        )

        assert execution.retry_count == 0

        execution.increment_retry()
        assert execution.retry_count == 1

        execution.increment_retry()
        assert execution.retry_count == 2

    def test_execution_duration_calculation(self) -> None:
        """Test execution duration calculation."""
        execution = ActionExecution(
            id=uuid4(),
            workflow_execution_id=uuid4(),
            action_id=uuid4(),
            contact_id=uuid4(),
        )

        # No duration before completion
        assert execution.duration_seconds is None

        # Duration after completion
        execution.mark_running()
        import time

        time.sleep(0.01)  # Small delay
        execution.mark_completed()

        duration = execution.duration_seconds
        assert duration is not None
        assert duration >= 0.01  # At least the sleep time

    def test_execution_to_dict(self) -> None:
        """Test execution serialization to dict."""
        execution = ActionExecution(
            id=uuid4(),
            workflow_execution_id=uuid4(),
            action_id=uuid4(),
            contact_id=uuid4(),
        )

        execution.mark_running()
        execution.mark_completed({"result": "success"})

        execution_dict = execution.to_dict()

        assert isinstance(execution_dict, dict)
        assert "id" in execution_dict
        assert "workflow_execution_id" in execution_dict
        assert "action_id" in execution_dict
        assert "contact_id" in execution_dict
        assert execution_dict["status"] == "completed"
        assert execution_dict["result_data"] == {"result": "success"}
        assert execution_dict["duration_seconds"] is not None

    def test_execution_with_data(self) -> None:
        """Test execution with execution and result data."""
        execution_data = {"contact": {"name": "John"}}
        result_data = {"email_id": "email-123", "sent": True}

        execution = ActionExecution(
            id=uuid4(),
            workflow_execution_id=uuid4(),
            action_id=uuid4(),
            contact_id=uuid4(),
            execution_data=execution_data,
        )

        assert execution.execution_data == execution_data

        execution.mark_running()
        execution.mark_completed(result_data=result_data)

        assert execution.result_data == result_data

    def test_execution_failure_with_result_data(self) -> None:
        """Test marking failed with partial result data."""
        execution = ActionExecution(
            id=uuid4(),
            workflow_execution_id=uuid4(),
            action_id=uuid4(),
            contact_id=uuid4(),
        )

        partial_result = {"attempted": True, "attempts": 3}

        execution.mark_running()
        execution.mark_failed(
            error_message="Max retries exceeded", result_data=partial_result
        )

        assert execution.status == ActionExecutionStatus.FAILED
        assert execution.result_data == partial_result
        assert execution.error_message == "Max retries exceeded"
