"""Domain exceptions for workflow execution.

This module defines custom exceptions for workflow execution errors.
"""


class WorkflowExecutionError(Exception):
    """Base exception for workflow execution errors."""

    pass


class InvalidExecutionStatusTransitionError(WorkflowExecutionError):
    """Exception raised when attempting an invalid status transition.

    Attributes:
        current_status: The current execution status.
        target_status: The target status that was invalid.
    """

    def __init__(self, current_status: str, target_status: str) -> None:
        """Initialize the exception.

        Args:
            current_status: Current status.
            target_status: Target status.
        """
        self.current_status = current_status
        self.target_status = target_status
        message = (
            f"Invalid status transition from '{current_status}' to '{target_status}'"
        )
        super().__init__(message)


class ExecutionNotFoundError(WorkflowExecutionError):
    """Exception raised when execution is not found.

    Attributes:
        execution_id: The execution ID that was not found.
    """

    def __init__(self, execution_id: str) -> None:
        """Initialize the exception.

        Args:
            execution_id: Execution ID.
        """
        self.execution_id = execution_id
        message = f"Execution not found: {execution_id}"
        super().__init__(message)


class ActionExecutionError(WorkflowExecutionError):
    """Exception raised when action execution fails.

    Attributes:
        action_type: The type of action that failed.
        error_details: Details about the error.
    """

    def __init__(self, action_type: str, error_details: str) -> None:
        """Initialize the exception.

        Args:
            action_type: Type of action.
            error_details: Error details.
        """
        self.action_type = action_type
        self.error_details = error_details
        message = f"Action execution failed for '{action_type}': {error_details}"
        super().__init__(message)


class RetryExhaustedError(WorkflowExecutionError):
    """Exception raised when max retry attempts are exhausted.

    Attributes:
        retry_count: The number of retry attempts made.
        max_retries: The maximum allowed retries.
    """

    def __init__(self, retry_count: int, max_retries: int) -> None:
        """Initialize the exception.

        Args:
            retry_count: Number of retry attempts.
            max_retries: Maximum allowed retries.
        """
        self.retry_count = retry_count
        self.max_retries = max_retries
        message = (
            f"Retry attempts exhausted ({retry_count}/{max_retries}). "
            "Execution marked as failed."
        )
        super().__init__(message)


class ExecutionLockError(WorkflowExecutionError):
    """Exception raised when execution lock cannot be acquired.

    This can happen when another worker is already processing the execution.
    """

    pass


class WorkflowNotActiveError(WorkflowExecutionError):
    """Exception raised when trying to execute a non-active workflow.

    Attributes:
        workflow_id: The workflow ID.
        status: The actual status of the workflow.
    """

    def __init__(self, workflow_id: str, status: str) -> None:
        """Initialize the exception.

        Args:
            workflow_id: Workflow ID.
            status: Actual workflow status.
        """
        self.workflow_id = workflow_id
        self.status = status
        message = (
            f"Workflow '{workflow_id}' is not active (status: {status}). "
            "Only active workflows can be executed."
        )
        super().__init__(message)


class ContactOptedOutError(WorkflowExecutionError):
    """Exception raised when trying to execute workflow for opted-out contact.

    Attributes:
        contact_id: The contact ID.
    """

    def __init__(self, contact_id: str) -> None:
        """Initialize the exception.

        Args:
            contact_id: Contact ID.
        """
        self.contact_id = contact_id
        message = (
            f"Contact '{contact_id}' has opted out of communications. "
            "Workflow cannot be executed."
        )
        super().__init__(message)


class ConcurrentExecutionLimitError(WorkflowExecutionError):
    """Exception raised when concurrent execution limit is reached.

    Attributes:
        account_id: The account ID.
        current_count: Current number of active executions.
        max_limit: Maximum allowed concurrent executions.
    """

    def __init__(self, account_id: str, current_count: int, max_limit: int) -> None:
        """Initialize the exception.

        Args:
            account_id: Account ID.
            current_count: Current active executions.
            max_limit: Maximum allowed executions.
        """
        self.account_id = account_id
        self.current_count = current_count
        self.max_limit = max_limit
        message = (
            f"Concurrent execution limit reached for account '{account_id}' "
            f"({current_count}/{max_limit}). Execution queued."
        )
        super().__init__(message)


class ExecutionTimeoutError(WorkflowExecutionError):
    """Exception raised when execution exceeds maximum duration.

    Attributes:
        execution_id: The execution ID.
        duration_hours: Execution duration in hours.
        max_hours: Maximum allowed duration.
    """

    def __init__(self, execution_id: str, duration_hours: float, max_hours: int) -> None:
        """Initialize the exception.

        Args:
            execution_id: Execution ID.
            duration_hours: Duration in hours.
            max_hours: Maximum allowed hours.
        """
        self.execution_id = execution_id
        self.duration_hours = duration_hours
        self.max_hours = max_hours
        message = (
            f"Execution '{execution_id}' exceeded maximum duration "
            f"({duration_hours:.2f}h > {max_hours}h). Terminated."
        )
        super().__init__(message)
