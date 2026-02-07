"""Retry service for workflow execution.

This module implements exponential backoff retry logic for failed
action executions.
"""

from datetime import UTC, datetime, timedelta
from typing import Any


class RetryStrategy:
    """Retry strategy configuration.

    Attributes:
        max_attempts: Maximum number of retry attempts.
        base_delay_seconds: Base delay for exponential backoff.
        max_delay_seconds: Maximum delay between retries.
        exponential_base: Base for exponential calculation (default 2).
    """

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay_seconds: int = 60,
        max_delay_seconds: int = 3600,
        exponential_base: int = 2,
    ) -> None:
        """Initialize retry strategy.

        Args:
            max_attempts: Maximum retry attempts.
            base_delay_seconds: Base delay in seconds.
            max_delay_seconds: Maximum delay in seconds.
            exponential_base: Exponential base.
        """
        self.max_attempts = max_attempts
        self.base_delay_seconds = base_delay_seconds
        self.max_delay_seconds = max_delay_seconds
        self.exponential_base = exponential_base

    def calculate_delay(self, attempt: int) -> int:
        """Calculate delay for given attempt using exponential backoff.

        Args:
            attempt: Retry attempt number (1-indexed).

        Returns:
            Delay in seconds.
        """
        if attempt <= 0:
            return 0

        # Calculate exponential backoff: base * (2 ^ (attempt - 1))
        exponential_delay = self.base_delay_seconds * (
            self.exponential_base ** (attempt - 1)
        )

        # Cap at max delay
        return min(exponential_delay, self.max_delay_seconds)

    def calculate_retry_at(self, attempt: int) -> datetime:
        """Calculate when retry should occur.

        Args:
            attempt: Retry attempt number (1-indexed).

        Returns:
            Datetime when retry should occur.
        """
        delay_seconds = self.calculate_delay(attempt)
        return datetime.now(UTC) + timedelta(seconds=delay_seconds)

    def should_retry(
        self,
        attempt: int,
        error: str | None = None,
        error_category: str | None = None,
    ) -> bool:
        """Determine if execution should be retried.

        Args:
            attempt: Current attempt number.
            error: Error message (optional).
            error_category: Error category for retry decision.

        Returns:
            True if should retry, False otherwise.
        """
        # Check max attempts
        if attempt >= self.max_attempts:
            return False

        # Don't retry certain error types
        if error_category == "validation":
            return False
        if error_category == "authentication":
            return False
        if error_category == "authorization":
            return False

        # Retry on transient errors
        if error_category == "timeout":
            return True
        if error_category == "rate_limit":
            return True
        if error_category == "server_error":
            return True
        if error_category == "network":
            return True

        # Default to retry for unknown errors
        return True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "max_attempts": self.max_attempts,
            "base_delay_seconds": self.base_delay_seconds,
            "max_delay_seconds": self.max_delay_seconds,
            "exponential_base": self.exponential_base,
        }


class RetryContext:
    """Context for retry tracking.

    Attributes:
        execution_id: Workflow execution ID.
        action_id: Action being retried.
        attempt_number: Current attempt number.
        error_message: Last error message.
        error_category: Category of error.
        retry_at: When retry should occur.
        metadata: Additional retry context.
    """

    def __init__(
        self,
        execution_id: str,
        action_id: str,
        attempt_number: int,
        error_message: str,
        error_category: str | None = None,
        retry_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize retry context.

        Args:
            execution_id: Execution ID.
            action_id: Action ID.
            attempt_number: Attempt number.
            error_message: Error message.
            error_category: Error category.
            retry_at: When to retry.
            metadata: Optional metadata.
        """
        self.execution_id = execution_id
        self.action_id = action_id
        self.attempt_number = attempt_number
        self.error_message = error_message
        self.error_category = error_category
        self.retry_at = retry_at
        self.metadata = metadata or {}

    @property
    def is_final_attempt(self) -> bool:
        """Check if this is the final retry attempt."""
        return self.attempt_number >= 3  # Default max

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "execution_id": self.execution_id,
            "action_id": self.action_id,
            "attempt_number": self.attempt_number,
            "error_message": self.error_message,
            "error_category": self.error_category,
            "retry_at": self.retry_at.isoformat() if self.retry_at else None,
            "is_final_attempt": self.is_final_attempt,
            "metadata": self.metadata,
        }


class RetryService:
    """Service for managing retry logic.

    This service provides methods for calculating retry delays,
    determining if retries should occur, and tracking retry context.
    """

    def __init__(self, strategy: RetryStrategy | None = None) -> None:
        """Initialize retry service.

        Args:
            strategy: Retry strategy configuration.
        """
        self.strategy = strategy or RetryStrategy()

    def create_retry_context(
        self,
        execution_id: str,
        action_id: str,
        attempt_number: int,
        error_message: str,
        error_category: str | None = None,
    ) -> RetryContext:
        """Create a retry context for a failed execution.

        Args:
            execution_id: Execution ID.
            action_id: Action ID.
            attempt_number: Current attempt number.
            error_message: Error message.
            error_category: Error category.

        Returns:
            Retry context with calculated retry time.
        """
        retry_at = self.strategy.calculate_retry_at(attempt_number)

        return RetryContext(
            execution_id=execution_id,
            action_id=action_id,
            attempt_number=attempt_number,
            error_message=error_message,
            error_category=error_category,
            retry_at=retry_at,
        )

    def should_retry_execution(
        self,
        attempt_number: int,
        error_message: str,
        error_category: str | None = None,
    ) -> bool:
        """Determine if execution should be retried.

        Args:
            attempt_number: Current attempt number.
            error_message: Error message.
            error_category: Error category.

        Returns:
            True if should retry, False otherwise.
        """
        return self.strategy.should_retry(
            attempt=attempt_number,
            error=error_message,
            error_category=error_category,
        )

    def calculate_next_retry_delay(self, attempt_number: int) -> int:
        """Calculate delay for next retry.

        Args:
            attempt_number: Next attempt number.

        Returns:
            Delay in seconds.
        """
        return self.strategy.calculate_delay(attempt_number)

    def categorize_error(self, error_message: str) -> str:
        """Categorize error for retry decision.

        Args:
            error_message: Error message.

        Returns:
            Error category.
        """
        error_lower = error_message.lower()

        # Validation errors
        if any(
            keyword in error_lower
            for keyword in ["validation", "invalid", "required", "missing"]
        ):
            return "validation"

        # Authentication errors
        if any(
            keyword in error_lower
            for keyword in ["authentication", "unauthorized", "auth"]
        ):
            return "authentication"

        # Authorization errors
        if any(keyword in error_lower for keyword in ["forbidden", "permission"]):
            return "authorization"

        # Rate limit errors
        if any(
            keyword in error_lower
            for keyword in ["rate limit", "too many requests", "429"]
        ):
            return "rate_limit"

        # Timeout errors
        if any(keyword in error_lower for keyword in ["timeout", "timed out"]):
            return "timeout"

        # Server errors
        if any(keyword in error_lower for keyword in ["500", "502", "503", "504"]):
            return "server_error"

        # Network errors
        if any(
            keyword in error_lower
            for keyword in ["connection", "network", "dns", "unreachable"]
        ):
            return "network"

        # Default category
        return "unknown"

    def get_retry_delay_from_error_headers(
        self,
        headers: dict[str, str],
    ) -> int | None:
        """Extract retry delay from rate limit headers.

        Args:
            headers: HTTP response headers.

        Returns:
            Delay in seconds, or None if not specified.
        """
        # Check common rate limit headers
        retry_after = headers.get("Retry-After")
        if retry_after:
            try:
                return int(retry_after)
            except ValueError:
                pass

        # Check X-RateLimit-Reset
        reset_at = headers.get("X-RateLimit-Reset")
        if reset_at:
            try:
                reset_timestamp = int(reset_at)
                current_timestamp = int(datetime.now(UTC).timestamp())
                delay = max(0, reset_timestamp - current_timestamp)
                return delay
            except ValueError:
                pass

        return None

    def calculate_delay_with_jitter(self, delay_seconds: int, jitter_percent: int = 10) -> int:
        """Add jitter to delay to prevent thundering herd.

        Args:
            delay_seconds: Base delay in seconds.
            jitter_percent: Jitter percentage (default 10%).

        Returns:
            Delay with jitter applied.
        """
        if jitter_percent <= 0:
            return delay_seconds

        # Calculate jitter amount
        jitter_range = delay_seconds * (jitter_percent / 100)
        jitter = (hash(str(datetime.now(UTC))) % 20000 / 10000) - 1  # -1 to 1
        jittered_delay = delay_seconds + (jitter * jitter_range)

        return max(0, int(jittered_delay))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "strategy": self.strategy.to_dict(),
        }


# Default retry service instance
default_retry_service = RetryService()
