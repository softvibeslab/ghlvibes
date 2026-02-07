"""Domain entities for workflow actions.

This module defines the core domain entities for workflow actions.
Actions are the steps that execute when a workflow is triggered.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Self
from uuid import UUID, uuid4

from src.workflows.domain.action_exceptions import (
    InvalidActionConfigurationError,
    InvalidActionTypeError,
)
from src.workflows.domain.action_value_objects import ActionConfig, ActionType


class ActionExecutionStatus(str, Enum):
    """Status of an action execution.

    Lifecycle:
    - pending: Execution is queued
    - scheduled: Scheduled for future execution (wait actions)
    - running: Currently executing
    - completed: Finished successfully
    - failed: Failed with error
    - skipped: Skipped due to condition
    - waiting: Waiting for event/timeout
    """

    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WAITING = "waiting"


@dataclass
class Action:
    """Workflow action entity.

    An action represents a single step in a workflow that performs
    a specific operation (send email, update contact, wait, etc.).

    Attributes:
        id: Unique identifier for the action.
        workflow_id: The workflow this action belongs to.
        action_type: Type of action (send_email, wait_time, etc.).
        action_config: Configuration for this action instance.
        position: Order position in the workflow sequence.
        previous_action_id: ID of previous action (for linked list).
        next_action_id: ID of next action (for linked list).
        branch_id: ID of branch if this is in a conditional branch.
        is_enabled: Whether this action is active.
        created_at: Timestamp when action was created.
        updated_at: Timestamp of last update.
        created_by: User who created this action.
        updated_by: User who last updated this action.
    """

    id: UUID
    workflow_id: UUID
    action_type: ActionType
    action_config: ActionConfig
    position: int
    previous_action_id: UUID | None = None
    next_action_id: UUID | None = None
    branch_id: UUID | None = None
    is_enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: UUID | None = None
    updated_by: UUID | None = None

    def __post_init__(self) -> None:
        """Validate action state after initialization."""
        # Ensure action_type is ActionType instance
        if isinstance(self.action_type, str):
            object.__setattr__(self, "action_type", ActionType(self.action_type))

        # Ensure action_config is ActionConfig instance
        if isinstance(self.action_config, dict):
            object.__setattr__(
                self, "action_config", ActionConfig(self.action_type, self.action_config)
            )

    @classmethod
    def create(
        cls,
        workflow_id: UUID,
        action_type: str | ActionType,
        action_config: dict[str, Any] | ActionConfig,
        position: int,
        created_by: UUID,
        previous_action_id: UUID | None = None,
        branch_id: UUID | None = None,
    ) -> Self:
        """Factory method to create a new action.

        Args:
            workflow_id: The workflow this action belongs to.
            action_type: Type of action to create.
            action_config: Configuration for the action.
            position: Position in workflow sequence.
            created_by: User creating the action.
            previous_action_id: Optional previous action for linking.
            branch_id: Optional branch ID if in conditional branch.

        Returns:
            A new Action instance.

        Raises:
            InvalidActionTypeError: If action type is invalid.
            InvalidActionConfigurationError: If config is invalid.
        """
        # Validate and convert action type
        validated_type = (
            action_type if isinstance(action_type, ActionType) else ActionType(action_type)
        )

        # Validate and convert action config
        validated_config = (
            action_config
            if isinstance(action_config, ActionConfig)
            else ActionConfig(validated_type, action_config)
        )

        now = datetime.now(UTC)

        return cls(
            id=uuid4(),
            workflow_id=workflow_id,
            action_type=validated_type,
            action_config=validated_config,
            position=position,
            previous_action_id=previous_action_id,
            branch_id=branch_id,
            is_enabled=True,
            created_at=now,
            updated_at=now,
            created_by=created_by,
            updated_by=created_by,
        )

    def update(
        self,
        updated_by: UUID,
        action_config: dict[str, Any] | ActionConfig | None = None,
        is_enabled: bool | None = None,
        position: int | None = None,
    ) -> None:
        """Update action properties.

        Args:
            updated_by: User making the update.
            action_config: New action configuration (optional).
            is_enabled: New enabled state (optional).
            position: New position (optional).
        """
        if action_config is not None:
            if isinstance(action_config, dict):
                self.action_config = ActionConfig(self.action_type, action_config)
            else:
                self.action_config = action_config

        if is_enabled is not None:
            self.is_enabled = is_enabled

        if position is not None:
            self.position = position

        self._touch(updated_by)

    def disable(self, updated_by: UUID) -> None:
        """Disable this action.

        Args:
            updated_by: User disabling the action.
        """
        self.is_enabled = False
        self._touch(updated_by)

    def enable(self, updated_by: UUID) -> None:
        """Enable this action.

        Args:
            updated_by: User enabling the action.
        """
        self.is_enabled = True
        self._touch(updated_by)

    def set_next_action(self, next_action_id: UUID, updated_by: UUID) -> None:
        """Set the next action in the sequence.

        Args:
            next_action_id: ID of the next action.
            updated_by: User making the change.
        """
        self.next_action_id = next_action_id
        self._touch(updated_by)

    def set_previous_action(self, previous_action_id: UUID, updated_by: UUID) -> None:
        """Set the previous action in the sequence.

        Args:
            previous_action_id: ID of the previous action.
            updated_by: User making the change.
        """
        self.previous_action_id = previous_action_id
        self._touch(updated_by)

    def _touch(self, updated_by: UUID) -> None:
        """Update timestamp and user.

        Args:
            updated_by: User making the change.
        """
        self.updated_at = datetime.now(UTC)
        self.updated_by = updated_by

    @property
    def is_enabled_status(self) -> bool:
        """Check if action is enabled."""
        return self.is_enabled

    def to_dict(self) -> dict[str, Any]:
        """Convert action to dictionary representation.

        Returns:
            Dictionary containing all action attributes.
        """
        return {
            "id": str(self.id),
            "workflow_id": str(self.workflow_id),
            "action_type": self.action_type.value,
            "action_config": self.action_config.to_dict(),
            "position": self.position,
            "previous_action_id": str(self.previous_action_id) if self.previous_action_id else None,
            "next_action_id": str(self.next_action_id) if self.next_action_id else None,
            "branch_id": str(self.branch_id) if self.branch_id else None,
            "is_enabled": self.is_enabled,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": str(self.created_by) if self.created_by else None,
            "updated_by": str(self.updated_by) if self.updated_by else None,
        }


@dataclass
class ActionExecution:
    """Execution record for a workflow action.

    This entity tracks the execution of an action for a specific contact,
    including status, timing, and results.

    Attributes:
        id: Unique identifier for the execution.
        workflow_execution_id: The workflow execution instance.
        action_id: The action being executed.
        contact_id: The contact this execution is for.
        status: Current execution status.
        started_at: When execution started.
        completed_at: When execution completed.
        execution_data: Context data during execution.
        result_data: Result of the execution.
        error_message: Error message if failed.
        retry_count: Number of retry attempts.
        scheduled_at: When execution is scheduled (for wait actions).
    """

    id: UUID
    workflow_execution_id: UUID
    action_id: UUID
    contact_id: UUID
    status: ActionExecutionStatus = ActionExecutionStatus.PENDING
    started_at: datetime | None = None
    completed_at: datetime | None = None
    execution_data: dict[str, Any] = field(default_factory=dict)
    result_data: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
    retry_count: int = 0
    scheduled_at: datetime | None = None

    def mark_running(self) -> None:
        """Mark execution as running."""
        self.status = ActionExecutionStatus.RUNNING
        self.started_at = datetime.now(UTC)

    def mark_completed(self, result_data: dict[str, Any] | None = None) -> None:
        """Mark execution as completed.

        Args:
            result_data: Optional result data from execution.
        """
        self.status = ActionExecutionStatus.COMPLETED
        self.completed_at = datetime.now(UTC)
        if result_data:
            self.result_data = result_data

    def mark_failed(self, error_message: str, result_data: dict[str, Any] | None = None) -> None:
        """Mark execution as failed.

        Args:
            error_message: Error message describing the failure.
            result_data: Optional partial result data.
        """
        self.status = ActionExecutionStatus.FAILED
        self.completed_at = datetime.now(UTC)
        self.error_message = error_message
        if result_data:
            self.result_data = result_data

    def mark_scheduled(self, scheduled_at: datetime) -> None:
        """Mark execution as scheduled for future.

        Args:
            scheduled_at: When the execution should occur.
        """
        self.status = ActionExecutionStatus.SCHEDULED
        self.scheduled_at = scheduled_at

    def mark_waiting(self) -> None:
        """Mark execution as waiting for event."""
        self.status = ActionExecutionStatus.WAITING

    def mark_skipped(self) -> None:
        """Mark execution as skipped."""
        self.status = ActionExecutionStatus.SKIPPED
        self.completed_at = datetime.now(UTC)

    def increment_retry(self) -> None:
        """Increment retry count."""
        self.retry_count += 1

    @property
    def is_pending(self) -> bool:
        """Check if execution is pending."""
        return self.status == ActionExecutionStatus.PENDING

    @property
    def is_running(self) -> bool:
        """Check if execution is running."""
        return self.status == ActionExecutionStatus.RUNNING

    @property
    def is_completed(self) -> bool:
        """Check if execution completed successfully."""
        return self.status == ActionExecutionStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Check if execution failed."""
        return self.status == ActionExecutionStatus.FAILED

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
        """Convert execution to dictionary representation.

        Returns:
            Dictionary containing all execution attributes.
        """
        return {
            "id": str(self.id),
            "workflow_execution_id": str(self.workflow_execution_id),
            "action_id": str(self.action_id),
            "contact_id": str(self.contact_id),
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "execution_data": self.execution_data,
            "result_data": self.result_data,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "duration_seconds": self.duration_seconds,
        }
