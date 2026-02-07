"""Domain entities for workflow execution.

This module defines the core domain entities for tracking and managing
workflow executions. These entities form the execution aggregate root.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Self
from uuid import UUID, uuid4

from src.workflows.domain.execution_exceptions import (
    InvalidExecutionStatusTransitionError,
    WorkflowExecutionError,
)


class ExecutionStatus(str, Enum):
    """Status of a workflow execution.

    Lifecycle:
    - queued: Execution is queued and waiting to start
    - active: Execution is currently running
    - paused: Execution is paused (will resume)
    - waiting: Execution is waiting for external event/timeout
    - completed: Execution finished successfully
    - failed: Execution failed (may be retried)
    - cancelled: Execution was manually cancelled
    """

    QUEUED = "queued"
    ACTIVE = "active"
    PAUSED = "paused"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

    def can_transition_to(self, new_status: "ExecutionStatus") -> bool:
        """Check if status transition is valid.

        Args:
            new_status: Target status to transition to.

        Returns:
            True if transition is valid, False otherwise.
        """
        valid_transitions = {
            ExecutionStatus.QUEUED: {
                ExecutionStatus.ACTIVE,
                ExecutionStatus.CANCELLED,
            },
            ExecutionStatus.ACTIVE: {
                ExecutionStatus.PAUSED,
                ExecutionStatus.WAITING,
                ExecutionStatus.COMPLETED,
                ExecutionStatus.FAILED,
                ExecutionStatus.CANCELLED,
            },
            ExecutionStatus.PAUSED: {
                ExecutionStatus.ACTIVE,
                ExecutionStatus.CANCELLED,
            },
            ExecutionStatus.WAITING: {
                ExecutionStatus.ACTIVE,
                ExecutionStatus.FAILED,
                ExecutionStatus.CANCELLED,
            },
            ExecutionStatus.FAILED: {
                ExecutionStatus.QUEUED,  # Retry
                ExecutionStatus.CANCELLED,
            },
            # Terminal states have no valid transitions
            ExecutionStatus.COMPLETED: set(),
            ExecutionStatus.CANCELLED: set(),
        }

        return new_status in valid_transitions.get(self, set())


@dataclass
class ExecutionLog:
    """Execution log entry for audit trail.

    This entity captures detailed execution information for each
    action step, providing a complete audit trail.

    Attributes:
        id: Unique log identifier.
        execution_id: Reference to workflow execution.
        step_index: Workflow step index.
        action_type: Type of action executed.
        action_config: Configuration used (encrypted).
        status: Execution status (SUCCESS, FAILED, SKIPPED).
        started_at: Action start time.
        completed_at: Action completion time.
        duration_ms: Execution duration in milliseconds.
        error_details: Error information if failed.
        response_data: Action response data.
        created_at: Log entry creation time.
    """

    id: UUID
    execution_id: UUID
    step_index: int
    action_type: str
    action_config: dict[str, Any]
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    duration_ms: int | None = None
    error_details: dict[str, Any] | None = None
    response_data: dict[str, Any] | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        execution_id: UUID,
        step_index: int,
        action_type: str,
        action_config: dict[str, Any],
    ) -> Self:
        """Factory method to create a new execution log.

        Args:
            execution_id: Workflow execution ID.
            step_index: Step index in workflow.
            action_type: Type of action.
            action_config: Action configuration.

        Returns:
            A new ExecutionLog instance.
        """
        now = datetime.now(UTC)

        return cls(
            id=uuid4(),
            execution_id=execution_id,
            step_index=step_index,
            action_type=action_type,
            action_config=action_config,
            status="running",
            started_at=now,
            created_at=now,
        )

    def mark_success(
        self,
        response_data: dict[str, Any] | None = None,
    ) -> None:
        """Mark execution as successful.

        Args:
            response_data: Optional response data from action.
        """
        self.status = "SUCCESS"
        self.completed_at = datetime.now(UTC)
        self.duration_ms = int((self.completed_at - self.started_at).total_seconds() * 1000)
        if response_data:
            self.response_data = response_data

    def mark_failed(
        self,
        error_details: dict[str, Any] | None = None,
    ) -> None:
        """Mark execution as failed.

        Args:
            error_details: Error details.
        """
        self.status = "FAILED"
        self.completed_at = datetime.now(UTC)
        self.duration_ms = int((self.completed_at - self.started_at).total_seconds() * 1000)
        if error_details:
            self.error_details = error_details

    def mark_skipped(self) -> None:
        """Mark execution as skipped."""
        self.status = "SKIPPED"
        self.completed_at = datetime.now(UTC)
        self.duration_ms = 0

    @property
    def is_running(self) -> bool:
        """Check if execution is still running."""
        return self.status == "running"

    @property
    def is_successful(self) -> bool:
        """Check if execution completed successfully."""
        return self.status == "SUCCESS"

    @property
    def is_failed(self) -> bool:
        """Check if execution failed."""
        return self.status == "FAILED"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary containing all log attributes.
        """
        return {
            "id": str(self.id),
            "execution_id": str(self.execution_id),
            "step_index": self.step_index,
            "action_type": self.action_type,
            "action_config": self.action_config,
            "status": self.status,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms,
            "error_details": self.error_details,
            "response_data": self.response_data,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class WorkflowExecution:
    """Workflow execution aggregate root.

    This entity represents a single execution instance of a workflow
    for a specific contact. It tracks the execution state, progress,
    and provides methods for managing the execution lifecycle.

    Attributes:
        id: Unique execution identifier.
        workflow_id: Reference to workflow definition.
        workflow_version: Version of workflow at execution start.
        contact_id: Contact being processed.
        account_id: Account/tenant identifier.
        status: Current execution status.
        current_step_index: Current position in workflow.
        started_at: Execution start time.
        completed_at: Execution completion time.
        error_message: Last error message.
        retry_count: Number of retry attempts.
        metadata: Additional execution context.
        created_at: Record creation time.
        updated_at: Last update time.
    """

    id: UUID
    workflow_id: UUID
    workflow_version: int
    contact_id: UUID
    account_id: UUID
    status: ExecutionStatus = ExecutionStatus.QUEUED
    current_step_index: int = 0
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    retry_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        workflow_id: UUID,
        workflow_version: int,
        contact_id: UUID,
        account_id: UUID,
        metadata: dict[str, Any] | None = None,
    ) -> Self:
        """Factory method to create a new workflow execution.

        Args:
            workflow_id: Workflow to execute.
            workflow_version: Version of workflow.
            contact_id: Contact to process.
            account_id: Account identifier.
            metadata: Optional execution context.

        Returns:
            A new WorkflowExecution instance in QUEUED status.
        """
        now = datetime.now(UTC)

        return cls(
            id=uuid4(),
            workflow_id=workflow_id,
            workflow_version=workflow_version,
            contact_id=contact_id,
            account_id=account_id,
            status=ExecutionStatus.QUEUED,
            current_step_index=0,
            started_at=None,
            completed_at=None,
            error_message=None,
            retry_count=0,
            metadata=metadata or {},
            created_at=now,
            updated_at=now,
        )

    def start(self) -> None:
        """Start the execution.

        Raises:
            InvalidExecutionStatusTransitionError: If transition is invalid.
        """
        if not self.status.can_transition_to(ExecutionStatus.ACTIVE):
            raise InvalidExecutionStatusTransitionError(
                self.status.value,
                ExecutionStatus.ACTIVE.value,
            )

        self.status = ExecutionStatus.ACTIVE
        self.started_at = datetime.now(UTC)
        self._touch()

    def pause(self) -> None:
        """Pause the execution.

        Raises:
            InvalidExecutionStatusTransitionError: If transition is invalid.
        """
        if not self.status.can_transition_to(ExecutionStatus.PAUSED):
            raise InvalidExecutionStatusTransitionError(
                self.status.value,
                ExecutionStatus.PAUSED.value,
            )

        self.status = ExecutionStatus.PAUSED
        self._touch()

    def resume(self) -> None:
        """Resume a paused execution.

        Raises:
            InvalidExecutionStatusTransitionError: If transition is invalid.
        """
        if not self.status.can_transition_to(ExecutionStatus.ACTIVE):
            raise InvalidExecutionStatusTransitionError(
                self.status.value,
                ExecutionStatus.ACTIVE.value,
            )

        self.status = ExecutionStatus.ACTIVE
        self._touch()

    def wait(self) -> None:
        """Put execution into waiting state.

        Raises:
            InvalidExecutionStatusTransitionError: If transition is invalid.
        """
        if not self.status.can_transition_to(ExecutionStatus.WAITING):
            raise InvalidExecutionStatusTransitionError(
                self.status.value,
                ExecutionStatus.WAITING.value,
            )

        self.status = ExecutionStatus.WAITING
        self._touch()

    def complete(self) -> None:
        """Mark execution as completed.

        Raises:
            InvalidExecutionStatusTransitionError: If transition is invalid.
        """
        if not self.status.can_transition_to(ExecutionStatus.COMPLETED):
            raise InvalidExecutionStatusTransitionError(
                self.status.value,
                ExecutionStatus.COMPLETED.value,
            )

        self.status = ExecutionStatus.COMPLETED
        self.completed_at = datetime.now(UTC)
        self._touch()

    def fail(self, error_message: str) -> None:
        """Mark execution as failed.

        Args:
            error_message: Error message describing the failure.

        Raises:
            InvalidExecutionStatusTransitionError: If transition is invalid.
        """
        if not self.status.can_transition_to(ExecutionStatus.FAILED):
            raise InvalidExecutionStatusTransitionError(
                self.status.value,
                ExecutionStatus.FAILED.value,
            )

        self.status = ExecutionStatus.FAILED
        self.completed_at = datetime.now(UTC)
        self.error_message = error_message
        self._touch()

    def cancel(self) -> None:
        """Cancel the execution.

        Raises:
            InvalidExecutionStatusTransitionError: If transition is invalid.
        """
        if not self.status.can_transition_to(ExecutionStatus.CANCELLED):
            raise InvalidExecutionStatusTransitionError(
                self.status.value,
                ExecutionStatus.CANCELLED.value,
            )

        self.status = ExecutionStatus.CANCELLED
        self.completed_at = datetime.now(UTC)
        self._touch()

    def retry(self) -> None:
        """Prepare execution for retry.

        Resets the execution to QUEUED status for retry attempt.

        Raises:
            InvalidExecutionStatusTransitionError: If transition is invalid.
            WorkflowExecutionError: If max retries exceeded.
        """
        if not self.status.can_transition_to(ExecutionStatus.QUEUED):
            raise InvalidExecutionStatusTransitionError(
                self.status.value,
                ExecutionStatus.QUEUED.value,
            )

        self.status = ExecutionStatus.QUEUED
        self.retry_count += 1
        self.error_message = None
        self.current_step_index = 0  # Restart from beginning
        self._touch()

    def advance_step(self) -> None:
        """Advance to the next step in the workflow."""
        self.current_step_index += 1
        self._touch()

    def set_step(self, step_index: int) -> None:
        """Set the current step index.

        Args:
            step_index: Step index to set.
        """
        if step_index < 0:
            raise WorkflowExecutionError("Step index cannot be negative")

        self.current_step_index = step_index
        self._touch()

    def update_metadata(self, metadata: dict[str, Any]) -> None:
        """Update execution metadata.

        Args:
            metadata: Metadata to merge with existing.
        """
        self.metadata.update(metadata)
        self._touch()

    def _touch(self) -> None:
        """Update timestamp."""
        self.updated_at = datetime.now(UTC)

    @property
    def is_queued(self) -> bool:
        """Check if execution is queued."""
        return self.status == ExecutionStatus.QUEUED

    @property
    def is_active(self) -> bool:
        """Check if execution is active."""
        return self.status == ExecutionStatus.ACTIVE

    @property
    def is_paused(self) -> bool:
        """Check if execution is paused."""
        return self.status == ExecutionStatus.PAUSED

    @property
    def is_waiting(self) -> bool:
        """Check if execution is waiting."""
        return self.status == ExecutionStatus.WAITING

    @property
    def is_completed(self) -> bool:
        """Check if execution is completed."""
        return self.status == ExecutionStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Check if execution is failed."""
        return self.status == ExecutionStatus.FAILED

    @property
    def is_cancelled(self) -> bool:
        """Check if execution is cancelled."""
        return self.status == ExecutionStatus.CANCELLED

    @property
    def is_terminal(self) -> bool:
        """Check if execution is in a terminal state."""
        return self.status in (
            ExecutionStatus.COMPLETED,
            ExecutionStatus.FAILED,
            ExecutionStatus.CANCELLED,
        )

    @property
    def can_retry(self) -> bool:
        """Check if execution can be retried."""
        return self.is_failed and self.retry_count < 3

    @property
    def duration_seconds(self) -> float | None:
        """Calculate execution duration in seconds.

        Returns:
            Duration in seconds, or None if not completed.
        """
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary containing all execution attributes.
        """
        return {
            "id": str(self.id),
            "workflow_id": str(self.workflow_id),
            "workflow_version": self.workflow_version,
            "contact_id": str(self.contact_id),
            "account_id": str(self.account_id),
            "status": self.status.value,
            "current_step_index": self.current_step_index,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "metadata": self.metadata,
            "duration_seconds": self.duration_seconds,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
