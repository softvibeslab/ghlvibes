"""Domain exceptions for CRM module.

These exceptions represent business rule violations and domain errors.
They are distinct from infrastructure errors (database, network) and
presentation errors (HTTP status codes).
"""

from src.core.domain import DomainError


class ContactValidationError(DomainError):
    """Base exception for contact validation errors."""


class InvalidEmailError(ContactValidationError):
    """Raised when an email address is invalid."""


class InvalidPhoneNumberError(ContactValidationError):
    """Raised when a phone number is invalid."""


class CompanyValidationError(DomainError):
    """Base exception for company validation errors."""


class PipelineValidationError(DomainError):
    """Base exception for pipeline validation errors."""


class InvalidStageTransitionError(PipelineValidationError):
    """Raised when attempting an invalid pipeline stage transition."""


class DealValidationError(DomainError):
    """Base exception for deal validation errors."""


class ActivityValidationError(DomainError):
    """Base exception for activity validation errors."""


class NoteValidationError(DomainError):
    """Base exception for note validation errors."""


class TagValidationError(DomainError):
    """Base exception for tag validation errors."""
