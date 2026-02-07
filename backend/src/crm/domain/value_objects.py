"""Value objects for CRM module.

Value objects are immutable objects defined by their attributes rather than identity.
They provide type safety and validation for domain concepts.
"""

import re
from dataclasses import dataclass
from enum import Enum

from src.crm.domain.exceptions import InvalidEmailError, InvalidPhoneNumberError


class Email(str):
    """Email value object with validation.

    Email addresses must be valid format and are stored in lowercase.
    """

    EMAIL_PATTERN = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )

    def __new__(cls, value: str) -> "Email":
        """Create and validate an Email instance.

        Args:
            value: Email address string.

        Returns:
            Email instance.

        Raises:
            InvalidEmailError: If email format is invalid.
        """
        if not isinstance(value, str):
            raise InvalidEmailError("Email must be a string")

        value = value.strip().lower()

        if not value or len(value) > 255:
            raise InvalidEmailError("Email is required and must be 255 characters or less")

        if not cls.EMAIL_PATTERN.match(value):
            raise InvalidEmailError(f"Invalid email format: {value}")

        instance = super().__new__(cls, value)
        return instance


@dataclass(frozen=True)
class PhoneNumber:
    """Phone number value object with validation.

    Supports international formats with country code.
    """

    number: str
    country_code: str | None = None  # e.g., +1, +44

    def __post_init__(self) -> None:
        """Validate phone number."""
        if not isinstance(self.number, str):
            raise InvalidPhoneNumberError("Phone number must be a string")

        # Remove common formatting characters
        cleaned = re.sub(r"[\s\-\(\)\.]", "", self.number)

        if not cleaned or len(cleaned) < 10 or len(cleaned) > 15:
            raise InvalidPhoneNumberError(
                "Phone number must be between 10 and 15 digits"
            )

        # Store cleaned number
        object.__setattr__(self, "number", cleaned)

    def formatted(self) -> str:
        """Return formatted phone number.

        Returns:
            Formatted phone number string.
        """
        if self.country_code:
            return f"{self.country_code} {self.number}"
        return self.number


@dataclass(frozen=True)
class Money:
    """Money value object for currency amounts.

    Provides precise monetary calculations with currency support.
    """

    amount: int  # Store as integer cents to avoid floating point errors
    currency: str = "USD"

    def __post_init__(self) -> None:
        """Validate money value."""
        if not isinstance(self.amount, int):
            raise ValueError("Amount must be an integer (cents)")

        if self.amount < 0:
            raise ValueError("Amount cannot be negative")

        if not isinstance(self.currency, str) or len(self.currency) != 3:
            raise ValueError("Currency must be a valid ISO 4217 code")

    @classmethod
    def from_decimal(cls, amount: float, currency: str = "USD") -> "Money":
        """Create Money from decimal amount.

        Args:
            amount: Decimal amount (e.g., 99.99).
            currency: ISO 4217 currency code.

        Returns:
            Money instance.
        """
        return cls(int(round(amount * 100)), currency)

    def to_decimal(self) -> float:
        """Convert to decimal amount.

        Returns:
            Decimal amount (e.g., 99.99).
        """
        return self.amount / 100.0

    def __str__(self) -> str:
        """Return formatted money string."""
        return f"{self.currency} {self.to_decimal():.2f}"


class ActivityStatus(str, Enum):
    """Activity lifecycle status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ActivityType(str, Enum):
    """Types of activities."""

    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    TASK = "task"
    NOTE = "note"
    SMS = "sms"
    OTHER = "other"


class DealStatus(str, Enum):
    """Deal statuses."""

    OPEN = "open"
    WON = "won"
    LOST = "lost"
    ABANDONED = "abandoned"
