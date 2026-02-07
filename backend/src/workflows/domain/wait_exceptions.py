"""Domain exceptions for wait step processing.

These exceptions represent domain-level errors that can occur
during wait step execution and management.
"""

from src.workflows.domain.execution_exceptions import WorkflowExecutionError


class WaitStepError(WorkflowExecutionError):
    """Base exception for wait step errors."""

    pass


class InvalidWaitConfigurationError(WaitStepError):
    """Raised when wait step configuration is invalid."""

    pass


class InvalidWaitDurationError(InvalidWaitConfigurationError):
    """Raised when wait duration is out of valid range."""

    pass


class InvalidWaitDateError(InvalidWaitConfigurationError):
    """Raised when wait date is invalid (past or too far in future)."""

    pass


class InvalidWaitTimeError(InvalidWaitConfigurationError):
    """Raised when wait time format is invalid."""

    pass


class InvalidEventTypeError(InvalidWaitConfigurationError):
    """Raised when event type is invalid or not supported."""

    pass


class InvalidTimeoutError(InvalidWaitConfigurationError):
    """Raised when timeout duration is out of valid range."""

    pass


class WaitExecutionNotFoundError(WaitStepError):
    """Raised when wait execution is not found."""

    pass


class WaitExecutionExpiredError(WaitStepError):
    """Raised when wait execution has expired."""

    pass


class EventListenerNotFoundError(WaitStepError):
    """Raised when event listener is not found."""

    pass


class EventListenerExpiredError(WaitStepError):
    """Raised when event listener has expired."""

    pass
