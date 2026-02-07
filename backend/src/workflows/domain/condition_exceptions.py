"""Domain exceptions for workflow conditions.

This module defines the domain-specific exceptions for condition
and branch operations.
"""

from src.workflows.domain.exceptions import WorkflowDomainError


class ConditionValidationError(WorkflowDomainError):
    """Raised when condition configuration is invalid.

    This exception is raised when validating condition configurations
    before they are saved or evaluated.
    """

    def __init__(self, errors: list[str]) -> None:
        """Initialize validation error.

        Args:
            errors: List of validation error messages.
        """
        self.errors = errors
        message = "; ".join(errors)
        super().__init__(f"Condition validation failed: {message}")


class InvalidConditionTypeError(WorkflowDomainError):
    """Raised when an invalid condition type is specified."""

    pass


class InvalidBranchTypeError(WorkflowDomainError):
    """Raised when an invalid branch type is specified."""

    pass


class InvalidOperatorError(WorkflowDomainError):
    """Raised when an invalid operator is specified for a condition type."""

    pass


class ConditionEvaluationError(WorkflowDomainError):
    """Raised when condition evaluation fails.

    This exception is raised when an error occurs during the
    evaluation of a condition, such as missing data or
    invalid references.
    """

    pass


class BranchValidationError(WorkflowDomainError):
    """Raised when branch configuration is invalid.

    This includes invalid percentage distributions in split tests,
    missing default branches, or invalid branch configurations.
    """

    pass


class InvalidPercentageError(WorkflowDomainError):
    """Raised when split test percentages don't sum to 100."""

    pass
