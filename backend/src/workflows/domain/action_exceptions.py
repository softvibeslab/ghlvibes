"""Domain exceptions for workflow actions.

These exceptions represent domain-level errors that occur
when action business rules are violated.
"""


class ActionDomainError(Exception):
    """Base exception for all action domain errors.

    All action-specific exceptions should inherit from this class
    to allow for easy catching of action-related errors.
    """

    def __init__(self, message: str) -> None:
        """Initialize the exception with a message.

        Args:
            message: Human-readable error description.
        """
        self.message = message
        super().__init__(message)


class InvalidActionTypeError(ActionDomainError):
    """Raised when an invalid action type is provided.

    This exception is raised when attempting to create an action
    with a type that is not supported.
    """

    def __init__(self, action_type: str) -> None:
        """Initialize with the invalid action type.

        Args:
            action_type: The invalid action type that was provided.
        """
        message = f"Invalid action type: '{action_type}'. Must be one of the supported action types."
        super().__init__(message)
        self.action_type = action_type


class InvalidActionConfigurationError(ActionDomainError):
    """Raised when action configuration fails validation.

    This exception is raised when the action configuration does not
    meet the requirements for the specific action type.
    """

    def __init__(self, action_type: str, errors: list[str]) -> None:
        """Initialize with action type and validation errors.

        Args:
            action_type: The action type that failed validation.
            errors: List of validation error messages.
        """
        message = f"Action configuration validation failed for '{action_type}': {'; '.join(errors)}"
        super().__init__(message)
        self.action_type = action_type
        self.errors = errors


class ActionNotFoundError(ActionDomainError):
    """Raised when an action cannot be found.

    This exception is raised when attempting to access an action
    that does not exist or has been deleted.
    """

    def __init__(self, action_id: str) -> None:
        """Initialize with the action ID.

        Args:
            action_id: The ID of the action that was not found.
        """
        message = f"Action with ID '{action_id}' not found"
        super().__init__(message)
        self.action_id = action_id


class WorkflowMustBeInDraftError(ActionDomainError):
    """Raised when attempting to modify actions in an active workflow.

    Actions can only be added, updated, or removed when the workflow
    is in draft or paused status.
    """

    def __init__(self, workflow_id: str, workflow_status: str) -> None:
        """Initialize with workflow ID and status.

        Args:
            workflow_id: The workflow ID.
            workflow_status: The current status of the workflow.
        """
        message = (
            f"Cannot modify actions in workflow '{workflow_id}' with status '{workflow_status}'. "
            "Workflow must be in draft or paused status."
        )
        super().__init__(message)
        self.workflow_id = workflow_id
        self.workflow_status = workflow_status


class ActionPositionConflictError(ActionDomainError):
    """Raised when attempting to place multiple actions at the same position.

    Each action in a workflow must have a unique position value.
    """

    def __init__(self, position: int) -> None:
        """Initialize with the conflicting position.

        Args:
            position: The position that caused the conflict.
        """
        message = (
            f"Position conflict: An action already exists at position {position}. "
            "Please use a different position or reorder actions first."
        )
        super().__init__(message)
        self.position = position


class MaximumActionsExceededError(ActionDomainError):
    """Raised when attempting to exceed the maximum allowed actions per workflow.

    Workflows are limited to 50 actions to ensure performance.
    """

    def __init__(self, current_count: int, max_count: int = 50) -> None:
        """Initialize with current and maximum counts.

        Args:
            current_count: Current number of actions.
            max_count: Maximum allowed actions (default: 50).
        """
        message = (
            f"Cannot add more actions. Workflow already has {current_count} actions, "
            f"maximum allowed is {max_count}."
        )
        super().__init__(message)
        self.current_count = current_count
        self.max_count = max_count


class ActionExecutionError(ActionDomainError):
    """Raised when an action execution fails.

    This exception represents errors that occur during the actual
    execution of an action (as opposed to configuration errors).
    """

    def __init__(
        self,
        action_id: str,
        action_type: str,
        error_message: str,
        retryable: bool = False,
    ) -> None:
        """Initialize with execution details.

        Args:
            action_id: The action that failed.
            action_type: Type of action that failed.
            error_message: Description of the failure.
            retryable: Whether the error is retryable.
        """
        message = (
            f"Action execution failed for '{action_type}' (ID: {action_id}): {error_message}"
        )
        super().__init__(message)
        self.action_id = action_id
        self.action_type = action_type
        self.error_message = error_message
        self.retryable = retryable


class ActionDependencyCycleError(ActionDomainError):
    """Raised when action dependencies would create a cycle.

    Actions cannot form circular dependencies as this would create
    infinite loops during execution.
    """

    def __init__(self, cycle_path: list[str]) -> None:
        """Initialize with the cycle path.

        Args:
            cycle_path: List of action IDs forming the cycle.
        """
        message = (
            f"Action dependency cycle detected: {' -> '.join(cycle_path)}. "
            "Cycles are not allowed in workflow action chains."
        )
        super().__init__(message)
        self.cycle_path = cycle_path
