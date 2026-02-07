"""Value objects for workflow versioning.

Value objects are immutable objects defined by their attributes.
They have no identity and are compared by value, not reference.
"""

from dataclasses import dataclass
from enum import StrEnum

from src.workflows.domain.exceptions import ValidationError


class VersionStatus(StrEnum):
    """Status of a workflow version.

    Draft: Version is being edited, not published
    Active: Version is the current live version
    Archived: Version has been archived after inactivity
    """

    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class VersionNumber:
    """Value object for workflow version numbers.

    Version numbers must be positive integers starting from 1.
    They are sequential and never reused or decremented.

    Attributes:
        value: The version number value.

    Raises:
        ValidationError: If version number is invalid.
    """

    value: int

    def __post_init__(self) -> None:
        """Validate version number."""
        if not isinstance(self.value, int):
            raise ValidationError("Version number must be an integer")
        if self.value < 1:
            raise ValidationError("Version number must be at least 1")
        if self.value > 1000:
            raise ValidationError("Version number cannot exceed 1000")

    def __str__(self) -> str:
        """Return string representation."""
        return f"v{self.value}"

    def increment(self) -> "VersionNumber":
        """Return the next version number.

        Returns:
            A new VersionNumber with value incremented by 1.
        """
        return VersionNumber(self.value + 1)


@dataclass(frozen=True)
class ChangeSummary:
    """Value object for version change summary.

    Represents a human-readable description of changes made in a version.

    Attributes:
        text: The change summary text.

    Raises:
        ValidationError: If summary is invalid.
    """

    text: str

    def __post_init__(self) -> None:
        """Validate change summary."""
        if not isinstance(self.text, str):
            raise ValidationError("Change summary must be a string")
        if len(self.text) > 500:
            raise ValidationError("Change summary cannot exceed 500 characters")

    def __str__(self) -> str:
        """Return string representation."""
        return self.text

    @property
    def is_empty(self) -> bool:
        """Check if summary is empty or whitespace only."""
        return not self.text or self.text.isspace()
