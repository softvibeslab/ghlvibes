"""Core domain types and base classes.

This module contains fundamental domain types used across the application.
"""


class DomainError(Exception):
    """Base exception for domain errors.

    Domain errors represent business rule violations or domain-specific
    errors that occur during the execution of business logic.

    Examples:
    - Invalid email format
    - Invalid state transition
    - Business rule violation
    """

    def __init__(self, message: str) -> None:
        """Initialize the domain error.

        Args:
            message: A human-readable description of the error.
        """
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        """Return the error message."""
        return self.message
