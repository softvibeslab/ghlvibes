"""Unit tests for workflow execution entities.

These tests verify the WorkflowExecution and ExecutionLog entities
behave correctly and enforce domain invariants.
"""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from src.workflows.domain.execution_entities import (
    ExecutionLog,
    ExecutionStatus,
    WorkflowExecution,
)
from src.workflows.domain.execution_exceptions import (
    InvalidExecutionStatusTransitionError,
    WorkflowExecutionError,
)


class TestExecutionStatus:
    """Test suite for ExecutionStatus enum."""

    def test_status_values(self) -> None:
        """Test that all expected statuses exist."""
        assert ExecutionStatus.QUEUED.value == "queued"
        assert ExecutionStatus.ACTIVE.value == "active"
        assert ExecutionStatus.PAUSED.value == "paused"
        assert ExecutionStatus.WAITING.value == "waiting"
        assert ExecutionStatus.COMPLETED.value == "completed"
        assert ExecutionStatus.FAILED.value == "failed"
        assert ExecutionStatus.CANCELLED.value == "cancelled"

    def test_valid_transitions_from_queued(self) -> None:
        """Test valid transitions from QUEUED status."""
        status = ExecutionStatus.QUEUED

        assert status.can_transition_to(ExecutionStatus.ACTIVE) is True
        assert status.can_transition_to(ExecutionStatus.CANCELLED) is True
        assert status.can_transition_to(ExecutionStatus.COMPLETED) is False
        assert status.can_transition_to(ExecutionStatus.FAILED) is False

    def test_valid_transitions_from_active(self) -> None:
        """Test valid transitions from ACTIVE status."""
        status = ExecutionStatus.ACTIVE

        assert status.can_transition_to(ExecutionStatus.PAUSED) is True
        assert status.can_transition_to(ExecutionStatus.WAITING) is True
        assert status.can_transition_to(ExecutionStatus.COMPLETED) is True
        assert status.can_transition_to(ExecutionStatus.FAILED) is True
        assert status.can_transition_to(ExecutionStatus.CANCELLED) is True
        assert status.can_transition_to(ExecutionStatus.QUEUED) is False

    def test_valid_transitions_from_completed(self) -> None:
        """Test that COMPLETED is a terminal state."""
        status = ExecutionStatus.COMPLETED

        assert status.can_transition_to(ExecutionStatus.ACTIVE) is False
        assert status.can_transition_to(ExecutionStatus.FAILED) is False
        assert status.can_transition_to(ExecutionStatus.CANCELLED) is False


class TestWorkflowExecution:
    """Test suite for WorkflowExecution entity."""

    @pytest.fixture
    def workflow_id(self) -> str:
        """Fixture for test workflow ID."""
        return uuid4()

    @pytest.fixture
    def contact_id(self) -> str:
        """Fixture for test contact ID."""
        return uuid4()

    @pytest.fixture
    def account_id(self) -> str:
        """Fixture for test account ID."""
        return uuid4()

    @pytest.fixture
    def execution(
        self,
        workflow_id: str,
        contact_id: str,
        account_id: str,
    ) -> WorkflowExecution:
        """Fixture for test execution."""
        return WorkflowExecution.create(
            workflow_id=workflow_id,
            workflow_version=1,
            contact_id=contact_id,
            account_id=account_id,
        )

    def test_create_execution(self, execution: WorkflowExecution) -> None:
        """Test creating a workflow execution."""
        assert execution.status == ExecutionStatus.QUEUED
        assert execution.current_step_index == 0
        assert execution.retry_count == 0
        assert execution.started_at is None
        assert execution.completed_at is None
        assert execution.error_message is None
        assert execution.metadata == {}

    def test_create_execution_with_metadata(
        self,
        workflow_id: str,
        contact_id: str,
        account_id: str,
    ) -> None:
        """Test creating execution with metadata."""
        metadata = {"trigger_source": "form_submission", "trigger_id": str(uuid4())}

        execution = WorkflowExecution.create(
            workflow_id=workflow_id,
            workflow_version=1,
            contact_id=contact_id,
            account_id=account_id,
            metadata=metadata,
        )

        assert execution.metadata == metadata

    def test_start_execution(
        self,
        execution: WorkflowExecution,
    ) -> None:
        """Test starting an execution."""
        execution.start()

        assert execution.status == ExecutionStatus.ACTIVE
        assert execution.started_at is not None
        assert execution.is_active is True

    def test_start_execution_from_invalid_status(
        self,
        execution: WorkflowExecution,
    ) -> None:
        """Test that starting from completed status raises error."""
        execution.start()
        execution.complete()

        with pytest.raises(InvalidExecutionStatusTransitionError):
            execution.start()

    def test_pause_execution(
        self,
        execution: WorkflowExecution,
    ) -> None:
        """Test pausing an execution."""
        execution.start()
        execution.pause()

        assert execution.status == ExecutionStatus.PAUSED
        assert execution.is_paused is True

    def test_pause_execution_from_queued_fails(
        self,
        execution: WorkflowExecution,
    ) -> None:
        """Test that pausing from QUEUED status fails."""
        with pytest.raises(InvalidExecutionStatusTransitionError):
            execution.pause()

    def test_resume_execution(
        self,
        execution: WorkflowExecution,
    ) -> None:
        """Test resuming a paused execution."""
        execution.start()
        execution.pause()
        execution.resume()

        assert execution.status == ExecutionStatus.ACTIVE

    def test_wait_execution(
        self,
        execution: WorkflowExecution,
    ) -> None:
        """Test putting execution into waiting state."""
        execution.start()
        execution.wait()

        assert execution.status == ExecutionStatus.WAITING
        assert execution.is_waiting is True

    def test_complete_execution(
        self,
        execution: WorkflowExecution,
    ) -> None:
        """Test completing an execution."""
        execution.start()
        execution.complete()

        assert execution.status == ExecutionStatus.COMPLETED
        assert execution.completed_at is not None
        assert execution.is_completed is True
        assert execution.is_terminal is True

    def test_fail_execution(
        self,
        execution: WorkflowExecution,
    ) -> None:
        """Test failing an execution."""
        execution.start()
        execution.fail("Action execution failed")

        assert execution.status == ExecutionStatus.FAILED
        assert execution.error_message == "Action execution failed"
        assert execution.completed_at is not None
        assert execution.is_failed is True

    def test_cancel_execution(
        self,
        execution: WorkflowExecution,
    ) -> None:
        """Test cancelling an execution."""
        execution.start()
        execution.cancel()

        assert execution.status == ExecutionStatus.CANCELLED
        assert execution.completed_at is not None
        assert execution.is_cancelled is True
        assert execution.is_terminal is True

    def test_retry_execution(
        self,
        execution: WorkflowExecution,
    ) -> None:
        """Test retrying a failed execution."""
        execution.start()
        execution.fail("Error")
        initial_retry_count = execution.retry_count

        execution.retry()

        assert execution.status == ExecutionStatus.QUEUED
        assert execution.retry_count == initial_retry_count + 1
        assert execution.error_message is None
        assert execution.current_step_index == 0  # Reset to beginning

    def test_retry_execution_from_non_failed_status_fails(
        self,
        execution: WorkflowExecution,
    ) -> None:
        """Test that retrying from non-failed status fails."""
        execution.start()

        with pytest.raises(InvalidExecutionStatusTransitionError):
            execution.retry()

    def test_advance_step(
        self,
        execution: WorkflowExecution,
    ) -> None:
        """Test advancing to next step."""
        execution.start()
        initial_step = execution.current_step_index

        execution.advance_step()

        assert execution.current_step_index == initial_step + 1

    def test_set_step(
        self,
        execution: WorkflowExecution,
    ) -> None:
        """Test setting current step."""
        execution.start()
        execution.set_step(5)

        assert execution.current_step_index == 5

    def test_set_negative_step_fails(
        self,
        execution: WorkflowExecution,
    ) -> None:
        """Test that setting negative step fails."""
        execution.start()

        with pytest.raises(WorkflowExecutionError):
            execution.set_step(-1)

    def test_update_metadata(
        self,
        execution: WorkflowExecution,
    ) -> None:
        """Test updating execution metadata."""
        execution.update_metadata({"key1": "value1"})
        execution.update_metadata({"key2": "value2"})

        assert execution.metadata["key1"] == "value1"
        assert execution.metadata["key2"] == "value2"

    def test_duration_seconds(
        self,
        execution: WorkflowExecution,
    ) -> None:
        """Test calculating execution duration."""
        execution.start()

        # Simulate some time passing
        import time
        time.sleep(0.01)

        execution.complete()

        duration = execution.duration_seconds
        assert duration is not None
        assert duration > 0
        assert duration < 1  # Should be less than 1 second

    def test_duration_seconds_before_completion(
        self,
        execution: WorkflowExecution,
    ) -> None:
        """Test that duration is None before completion."""
        execution.start()

        assert execution.duration_seconds is None

    def test_can_retry(
        self,
        execution: WorkflowExecution,
    ) -> None:
        """Test can_retry property."""
        execution.start()
        execution.fail("Error")

        # Can retry when failed and retry_count < 3
        assert execution.is_failed is True
        assert execution.can_retry is True
        assert execution.retry_count == 0

        # After first retry, status changes to QUEUED
        execution.retry()
        assert execution.status == ExecutionStatus.QUEUED
        assert execution.retry_count == 1
        assert execution.can_retry is False  # Not failed anymore

        # Fail again and retry
        execution.start()
        execution.fail("Error 2")
        assert execution.can_retry is True  # Failed again
        assert execution.retry_count == 1

        execution.retry()
        assert execution.retry_count == 2

        # Fail third time and retry
        execution.start()
        execution.fail("Error 3")
        assert execution.can_retry is True
        assert execution.retry_count == 2

        execution.retry()
        assert execution.retry_count == 3

        # After reaching max retries, still can't retry
        execution.start()
        execution.fail("Error 4")
        assert execution.can_retry is False  # retry_count >= 3

    def test_to_dict(
        self,
        execution: WorkflowExecution,
    ) -> None:
        """Test converting execution to dictionary."""
        execution.start()
        execution.complete()

        result = execution.to_dict()

        assert "id" in result
        assert "workflow_id" in result
        assert "contact_id" in result
        assert "account_id" in result
        assert result["status"] == "completed"
        assert result["current_step_index"] == 0
        assert "started_at" in result
        assert "completed_at" in result
        assert "duration_seconds" in result


class TestExecutionLog:
    """Test suite for ExecutionLog entity."""

    @pytest.fixture
    def execution_id(self) -> str:
        """Fixture for test execution ID."""
        return uuid4()

    def test_create_log(
        self,
        execution_id: str,
    ) -> None:
        """Test creating an execution log."""
        log = ExecutionLog.create(
            execution_id=execution_id,
            step_index=0,
            action_type="send_email",
            action_config={"template_id": "123"},
        )

        assert log.execution_id == execution_id
        assert log.step_index == 0
        assert log.action_type == "send_email"
        assert log.status == "running"
        assert log.started_at is not None
        assert log.completed_at is None
        assert log.is_running is True

    def test_mark_success(
        self,
        execution_id: str,
    ) -> None:
        """Test marking log as successful."""
        log = ExecutionLog.create(
            execution_id=execution_id,
            step_index=0,
            action_type="send_email",
            action_config={"template_id": "123"},
        )

        log.mark_success(response_data={"email_id": str(uuid4())})

        assert log.status == "SUCCESS"
        assert log.completed_at is not None
        assert log.duration_ms is not None
        assert log.duration_ms >= 0
        assert log.is_successful is True
        assert log.response_data["email_id"] is not None

    def test_mark_failed(
        self,
        execution_id: str,
    ) -> None:
        """Test marking log as failed."""
        log = ExecutionLog.create(
            execution_id=execution_id,
            step_index=0,
            action_type="send_email",
            action_config={"template_id": "123"},
        )

        log.mark_failed(error_details={"error": "SMTP connection failed"})

        assert log.status == "FAILED"
        assert log.completed_at is not None
        assert log.duration_ms is not None
        assert log.is_failed is True
        assert log.error_details["error"] == "SMTP connection failed"

    def test_mark_skipped(
        self,
        execution_id: str,
    ) -> None:
        """Test marking log as skipped."""
        log = ExecutionLog.create(
            execution_id=execution_id,
            step_index=0,
            action_type="send_email",
            action_config={"template_id": "123"},
        )

        log.mark_skipped()

        assert log.status == "SKIPPED"
        assert log.completed_at is not None
        assert log.duration_ms == 0

    def test_to_dict(
        self,
        execution_id: str,
    ) -> None:
        """Test converting log to dictionary."""
        log = ExecutionLog.create(
            execution_id=execution_id,
            step_index=0,
            action_type="send_email",
            action_config={"template_id": "123"},
        )

        log.mark_success(response_data={"email_id": str(uuid4())})

        result = log.to_dict()

        assert "id" in result
        assert "execution_id" in result
        assert result["step_index"] == 0
        assert result["action_type"] == "send_email"
        assert result["status"] == "SUCCESS"
        assert "started_at" in result
        assert "completed_at" in result
        assert "duration_ms" in result
