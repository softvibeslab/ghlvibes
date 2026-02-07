"""Domain exceptions for workflow versioning.

These exceptions represent business rule violations in the
workflow versioning domain.
"""

from src.workflows.domain.exceptions import WorkflowDomainError


class VersionDomainError(WorkflowDomainError):
    """Base exception for workflow versioning domain errors."""

    pass


class InvalidVersionStatusError(VersionDomainError):
    """Raised when attempting an invalid version status transition."""

    def __init__(self, current_status: str, target_status: str) -> None:
        """Initialize exception.

        Args:
            current_status: Current version status.
            target_status: Target status that is invalid.
        """
        self.current_status = current_status
        self.target_status = target_status
        super().__init__(
            f"Cannot transition version status from '{current_status}' to '{target_status}'"
        )


class MaxVersionsExceededError(VersionDomainError):
    """Raised when attempting to create more than the maximum allowed versions."""

    def __init__(self, current_count: int, max_versions: int = 1000) -> None:
        """Initialize exception.

        Args:
            current_count: Current number of versions.
            max_versions: Maximum allowed versions.
        """
        self.current_count = current_count
        self.max_versions = max_versions
        super().__init__(
            f"Maximum versions exceeded: {current_count}/{max_versions}. "
            f"Cannot create more versions."
        )


class VersionNotFoundError(VersionDomainError):
    """Raised when attempting to access a non-existent version."""

    def __init__(self, version_id: str) -> None:
        """Initialize exception.

        Args:
            version_id: ID of the version that was not found.
        """
        self.version_id = version_id
        super().__init__(f"Version '{version_id}' not found")


class VersionConflictError(VersionDomainError):
    """Raised when concurrent modification conflict is detected."""

    def __init__(self, message: str = "Workflow version was modified by another user") -> None:
        """Initialize exception.

        Args:
            message: Error message.
        """
        super().__init__(message)


class InvalidVersionNumberError(VersionDomainError):
    """Raised when an invalid version number is provided."""

    def __init__(self, version_number: int) -> None:
        """Initialize exception.

        Args:
            version_number: Invalid version number.
        """
        self.version_number = version_number
        super().__init__(f"Invalid version number: {version_number}")


class MigrationInProgressError(VersionDomainError):
    """Raised when attempting to modify a version during active migration."""

    def __init__(self, version_id: str) -> None:
        """Initialize exception.

        Args:
            version_id: ID of version with active migration.
        """
        self.version_id = version_id
        super().__init__(
            f"Cannot modify version '{version_id}' while migration is in progress"
        )
