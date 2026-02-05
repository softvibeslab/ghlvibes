"""Domain exceptions for the workflow module.

These exceptions represent domain-level errors that occur
when business rules are violated.
"""


class WorkflowDomainError(Exception):
    """Base exception for all workflow domain errors.

    All domain-specific exceptions should inherit from this class
    to allow for easy catching of workflow-related errors.
    """

    def __init__(self, message: str) -> None:
        """Initialize the exception with a message.

        Args:
            message: Human-readable error description.
        """
        self.message = message
        super().__init__(message)


class InvalidWorkflowNameError(WorkflowDomainError):
    """Raised when a workflow name violates naming rules.

    This exception is raised when:
    - Name is empty or whitespace only
    - Name is too short (< 3 characters)
    - Name is too long (> 100 characters)
    - Name contains invalid characters
    - Name has leading/trailing spaces
    """

    pass


class InvalidWorkflowStatusTransitionError(WorkflowDomainError):
    """Raised when an invalid status transition is attempted.

    Valid transitions:
    - draft -> active
    - active -> paused
    - active -> draft
    - paused -> active
    - paused -> draft
    """

    def __init__(self, current_status: str, target_status: str) -> None:
        """Initialize with current and target status.

        Args:
            current_status: The current workflow status.
            target_status: The status attempted to transition to.
        """
        message = (
            f"Cannot transition workflow from '{current_status}' to '{target_status}'. "
            f"This transition is not allowed."
        )
        super().__init__(message)
        self.current_status = current_status
        self.target_status = target_status


class WorkflowNotFoundError(WorkflowDomainError):
    """Raised when a workflow cannot be found.

    This exception is raised when attempting to access
    a workflow that does not exist or has been deleted.
    """

    def __init__(self, workflow_id: str) -> None:
        """Initialize with the workflow ID.

        Args:
            workflow_id: The ID of the workflow that was not found.
        """
        message = f"Workflow with ID '{workflow_id}' not found"
        super().__init__(message)
        self.workflow_id = workflow_id


class WorkflowValidationError(WorkflowDomainError):
    """Raised when workflow data fails validation.

    This exception is raised when the workflow data
    does not meet business validation requirements.
    """

    def __init__(self, errors: list[str]) -> None:
        """Initialize with validation errors.

        Args:
            errors: List of validation error messages.
        """
        message = f"Workflow validation failed: {'; '.join(errors)}"
        super().__init__(message)
        self.errors = errors


class WorkflowAlreadyExistsError(WorkflowDomainError):
    """Raised when attempting to create a duplicate workflow.

    This exception is raised when a workflow with the same
    name already exists in the same account.
    """

    def __init__(self, name: str, account_id: str) -> None:
        """Initialize with workflow name and account ID.

        Args:
            name: The workflow name that already exists.
            account_id: The account where the duplicate was found.
        """
        message = f"Workflow with name '{name}' already exists in account '{account_id}'"
        super().__init__(message)
        self.name = name
        self.account_id = account_id


class WorkflowOperationError(WorkflowDomainError):
    """Raised when a workflow operation fails.

    This is a general exception for workflow operations
    that fail due to unexpected conditions.
    """

    pass
