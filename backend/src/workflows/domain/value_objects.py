"""Domain value objects for the workflow module.

Value objects are immutable objects that represent domain concepts
with no identity. They are defined by their attributes.
"""

import re
from enum import Enum
from typing import Self

from src.workflows.domain.exceptions import InvalidWorkflowNameError


class WorkflowStatus(str, Enum):
    """Workflow lifecycle status.

    Workflows transition through these states:
    - draft: Initial state, workflow is being configured
    - active: Workflow is running and processing triggers
    - paused: Workflow is temporarily stopped

    Valid transitions:
    - draft -> active (activation)
    - active -> paused (pause)
    - paused -> active (resume)
    - draft -> draft (editing)
    - active -> draft (deactivate for editing)
    - paused -> draft (deactivate for editing)
    """

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"

    def can_transition_to(self, target: "WorkflowStatus") -> bool:
        """Check if transition to target status is valid.

        Args:
            target: The status to transition to.

        Returns:
            True if the transition is valid, False otherwise.
        """
        valid_transitions: dict[WorkflowStatus, set[WorkflowStatus]] = {
            WorkflowStatus.DRAFT: {WorkflowStatus.ACTIVE, WorkflowStatus.DRAFT},
            WorkflowStatus.ACTIVE: {WorkflowStatus.PAUSED, WorkflowStatus.DRAFT},
            WorkflowStatus.PAUSED: {WorkflowStatus.ACTIVE, WorkflowStatus.DRAFT},
        }
        return target in valid_transitions.get(self, set())


class WorkflowName:
    """Value object representing a workflow name.

    Business rules:
    - Length: 3-100 characters
    - Allowed characters: alphanumeric, hyphen, underscore, spaces
    - No leading or trailing whitespace
    - Cannot be empty or whitespace only

    This is an immutable value object - once created, it cannot be changed.
    """

    # Regex pattern for valid workflow names
    # Allows alphanumeric, hyphen, underscore, and spaces
    _VALID_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9\s\-_]*[a-zA-Z0-9]$|^[a-zA-Z0-9]{1,2}$")
    _MIN_LENGTH = 3
    _MAX_LENGTH = 100

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        """Initialize workflow name with validation.

        Args:
            value: The workflow name string.

        Raises:
            InvalidWorkflowNameError: If the name is invalid.
        """
        validated_value = self._validate(value)
        object.__setattr__(self, "_value", validated_value)

    def _validate(self, value: str) -> str:
        """Validate the workflow name.

        Args:
            value: The name to validate.

        Returns:
            The validated and normalized name.

        Raises:
            InvalidWorkflowNameError: If validation fails.
        """
        if not isinstance(value, str):
            raise InvalidWorkflowNameError(
                f"Workflow name must be a string, got {type(value).__name__}"
            )

        # Strip leading/trailing whitespace
        normalized = value.strip()

        # Check for empty or whitespace-only
        if not normalized:
            raise InvalidWorkflowNameError("Workflow name cannot be empty or whitespace only")

        # Check length constraints
        if len(normalized) < self._MIN_LENGTH:
            raise InvalidWorkflowNameError(
                f"Workflow name must be at least {self._MIN_LENGTH} characters, "
                f"got {len(normalized)}"
            )

        if len(normalized) > self._MAX_LENGTH:
            raise InvalidWorkflowNameError(
                f"Workflow name must not exceed {self._MAX_LENGTH} characters, "
                f"got {len(normalized)}"
            )

        # Check for valid characters
        # For names of length 1-2, we allow single alphanumeric characters
        if len(normalized) <= 2:
            if not normalized.isalnum():
                raise InvalidWorkflowNameError(
                    "Workflow name must contain only alphanumeric characters, "
                    "hyphens, underscores, or spaces"
                )
        elif not self._VALID_PATTERN.match(normalized):
            raise InvalidWorkflowNameError(
                "Workflow name must start and end with alphanumeric characters "
                "and contain only alphanumeric characters, hyphens, underscores, or spaces"
            )

        return normalized

    @property
    def value(self) -> str:
        """Get the workflow name value."""
        return self._value

    def __str__(self) -> str:
        """Return the string representation."""
        return self._value

    def __repr__(self) -> str:
        """Return the repr representation."""
        return f"WorkflowName({self._value!r})"

    def __eq__(self, other: object) -> bool:
        """Check equality with another WorkflowName."""
        if isinstance(other, WorkflowName):
            return self._value == other._value
        if isinstance(other, str):
            return self._value == other
        return NotImplemented

    def __hash__(self) -> int:
        """Return hash for use in sets and dicts."""
        return hash(self._value)

    def __setattr__(self, name: str, value: object) -> None:
        """Prevent attribute modification (immutability)."""
        if hasattr(self, "_value"):
            raise AttributeError("WorkflowName is immutable")
        super().__setattr__(name, value)

    @classmethod
    def create(cls, value: str) -> Self:
        """Factory method to create a WorkflowName.

        Args:
            value: The workflow name string.

        Returns:
            A new WorkflowName instance.

        Raises:
            InvalidWorkflowNameError: If the name is invalid.
        """
        return cls(value)
