"""Exceptions for webhook integration.

This module defines custom exceptions for webhook-related errors.
"""



class WebhookError(Exception):
    """Base exception for webhook errors."""

    def __init__(self, message: str) -> None:
        """Initialize webhook error.

        Args:
            message: Error message.
        """
        self.message = message
        super().__init__(self.message)


class InvalidWebhookURLError(WebhookError):
    """Raised when webhook URL is invalid."""

    def __init__(self, url: str, errors: list[str]) -> None:
        """Initialize invalid URL error.

        Args:
            url: The invalid URL.
            errors: List of validation errors.
        """
        self.url = url
        self.errors = errors
        self.message = f"Invalid webhook URL '{url}': {', '.join(errors)}"
        super().__init__(self.message)


class InvalidWebhookAuthError(WebhookError):
    """Raised when webhook authentication configuration is invalid."""

    def __init__(self, auth_type: str, errors: list[str]) -> None:
        """Initialize invalid auth error.

        Args:
            auth_type: The authentication type.
            errors: List of validation errors.
        """
        self.auth_type = auth_type
        self.errors = errors
        self.message = f"Invalid webhook auth for type '{auth_type}': {', '.join(errors)}"
        super().__init__(self.message)


class WebhookExecutionError(WebhookError):
    """Raised when webhook execution fails critically."""

    def __init__(
        self,
        message: str,
        error_type: str = "unknown",
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        """Initialize execution error.

        Args:
            message: Error message.
            error_type: Type of error (network, timeout, client_error, server_error).
            status_code: HTTP status code if applicable.
            response_body: Response body if applicable.
        """
        self.error_type = error_type
        self.status_code = status_code
        self.response_body = response_body
        self.message = message
        super().__init__(self.message)


class WebhookPayloadSizeError(WebhookError):
    """Raised when webhook payload exceeds size limit."""

    def __init__(self, size_bytes: int, max_bytes: int = 1048576) -> None:
        """Initialize payload size error.

        Args:
            size_bytes: Actual payload size in bytes.
            max_bytes: Maximum allowed size (default 1MB).
        """
        self.size_bytes = size_bytes
        self.max_bytes = max_bytes
        self.message = (
            f"Webhook payload size ({size_bytes} bytes) "
            f"exceeds maximum allowed size ({max_bytes} bytes)"
        )
        super().__init__(self.message)


class WebhookMergeFieldError(WebhookError):
    """Raised when merge field interpolation fails."""

    def __init__(self, field_name: str, reason: str) -> None:
        """Initialize merge field error.

        Args:
            field_name: The field name that failed.
            reason: Reason for failure.
        """
        self.field_name = field_name
        self.reason = reason
        self.message = f"Failed to interpolate merge field '{{{field_name}}}': {reason}"
        super().__init__(self.message)


class WebhookConnectionLimitError(WebhookError):
    """Raised when concurrent connection limit is reached."""

    def __init__(self, current: int, limit: int) -> None:
        """Initialize connection limit error.

        Args:
            current: Current connection count.
            limit: Maximum allowed connections.
        """
        self.current = current
        self.limit = limit
        self.message = (
            f"Webhook concurrent connection limit reached: {current}/{limit}"
        )
        super().__init__(self.message)


class WebhookConfigurationNotFoundError(WebhookError):
    """Raised when webhook configuration is not found."""

    def __init__(self, config_id: str) -> None:
        """Initialize not found error.

        Args:
            config_id: The configuration ID.
        """
        self.config_id = config_id
        self.message = f"Webhook configuration not found: {config_id}"
        super().__init__(self.message)
