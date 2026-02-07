"""Domain entities for webhook integration.

This module defines the core domain entities for webhook configuration
and execution tracking.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Self
from uuid import UUID

from src.workflows.domain.webhook_exceptions import (
    InvalidWebhookAuthError,
    InvalidWebhookURLError,
)


class WebhookAuthType(str, Enum):
    """Types of webhook authentication.

    - NONE: No authentication
    - BASIC: Basic authentication with username/password
    - BEARER: Bearer token authentication
    - API_KEY: API key in custom header
    """

    NONE = "none"
    BASIC = "basic"
    BEARER = "bearer"
    API_KEY = "api_key"


class WebhookExecutionStatus(str, Enum):
    """Status of webhook execution.

    Lifecycle:
    - pending: Execution is queued
    - running: Currently executing
    - success: Completed successfully (2xx response)
    - retry: Failed but will retry (5xx/network error)
    - failed: Failed with no retry (4xx/client error)
    - timeout: Request exceeded timeout
    """

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    RETRY = "retry"
    FAILED = "failed"
    TIMEOUT = "timeout"


class WebhookErrorType(str, Enum):
    """Classification of webhook errors.

    - NETWORK: Connection refused, DNS failure, SSL error
    - TIMEOUT: Request exceeded timeout limit
    - CLIENT_ERROR: 4xx status codes
    - SERVER_ERROR: 5xx status codes
    - UNKNOWN: Unclassified error
    """

    NETWORK = "network"
    TIMEOUT = "timeout"
    CLIENT_ERROR = "client_error"
    SERVER_ERROR = "server_error"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class WebhookAuthConfig:
    """Value object for webhook authentication configuration.

    This is an immutable value object containing authentication
    credentials based on the auth type.

    Attributes:
        auth_type: Type of authentication to use.
        username: Username for basic auth (optional).
        password: Password for basic auth (optional).
        token: Bearer token or API key value (optional).
        header_name: Custom header name for API key (optional).
    """

    auth_type: WebhookAuthType
    username: str | None = None
    password: str | None = None
    token: str | None = None
    header_name: str | None = None

    def __post_init__(self) -> None:
        """Validate authentication configuration.

        Raises:
            InvalidWebhookAuthError: If configuration is invalid.
        """
        errors = []

        if self.auth_type == WebhookAuthType.BASIC:
            if not self.username or not self.password:
                errors.append("username and password are required for basic auth")

        elif self.auth_type == WebhookAuthType.BEARER:
            if not self.token:
                errors.append("token is required for bearer auth")

        elif self.auth_type == WebhookAuthType.API_KEY:
            if not self.token or not self.header_name:
                errors.append("token and header_name are required for api_key auth")

        if errors:
            raise InvalidWebhookAuthError(self.auth_type.value, errors)

    @classmethod
    def none(cls) -> Self:
        """Create no-auth configuration.

        Returns:
            Auth config with no authentication.
        """
        return cls(auth_type=WebhookAuthType.NONE)

    @classmethod
    def basic(cls, username: str, password: str) -> Self:
        """Create basic auth configuration.

        Args:
            username: Username for authentication.
            password: Password for authentication.

        Returns:
            Auth config with basic authentication.
        """
        return cls(auth_type=WebhookAuthType.BASIC, username=username, password=password)

    @classmethod
    def bearer(cls, token: str) -> Self:
        """Create bearer token configuration.

        Args:
            token: Bearer token value.

        Returns:
            Auth config with bearer token authentication.
        """
        return cls(auth_type=WebhookAuthType.BEARER, token=token)

    @classmethod
    def api_key(cls, header_name: str, token: str) -> Self:
        """Create API key configuration.

        Args:
            header_name: Custom header name (e.g., "X-API-Key").
            token: API key value.

        Returns:
            Auth config with API key authentication.
        """
        return cls(auth_type=WebhookAuthType.API_KEY, header_name=header_name, token=token)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary with auth configuration (excluding secrets).
        """
        result = {"auth_type": self.auth_type.value}

        if self.auth_type == WebhookAuthType.BASIC and self.username:
            result["username"] = self.username
            # Password excluded for security
        elif self.auth_type == WebhookAuthType.API_KEY and self.header_name:
            result["header_name"] = self.header_name
            # Token excluded for security

        return result


@dataclass(frozen=True)
class WebhookRequestConfig:
    """Value object for webhook request configuration.

    This immutable value object contains all parameters needed
    to make an HTTP request to a webhook endpoint.

    Attributes:
        url: Webhook URL (validated).
        method: HTTP method to use.
        headers: Custom HTTP headers (merged with auth headers).
        body: Request body (JSON payload template).
        timeout_seconds: Request timeout in seconds.
        ssl_verify: Whether to verify SSL certificates.
        retry_enabled: Whether to retry on failure.
        retry_max_attempts: Maximum retry attempts (1-5).
    """

    url: str
    method: str = "POST"
    headers: dict[str, str] = field(default_factory=dict)
    body: dict[str, Any] | None = None
    timeout_seconds: int = 30
    ssl_verify: bool = True
    retry_enabled: bool = True
    retry_max_attempts: int = 3

    def __post_init__(self) -> None:
        """Validate request configuration.

        Raises:
            InvalidWebhookURLError: If URL is invalid.
        """
        from src.workflows.domain.webhook_value_objects import validate_webhook_url

        # Validate URL
        validation_errors = validate_webhook_url(self.url)
        if validation_errors:
            raise InvalidWebhookURLError(self.url, validation_errors)

        # Validate method
        valid_methods = {"GET", "POST", "PUT", "PATCH", "DELETE"}
        object.__setattr__(self, "method", self.method.upper())

        if self.method not in valid_methods:
            raise ValueError(f"Invalid HTTP method: {self.method}")

        # Validate timeout
        if not (1 <= self.timeout_seconds <= 120):
            raise ValueError("timeout_seconds must be between 1 and 120")

        # Validate retry attempts
        if not (1 <= self.retry_max_attempts <= 5):
            raise ValueError("retry_max_attempts must be between 1 and 5")

    @property
    def has_body(self) -> bool:
        """Check if request has a body.

        Returns:
            True if method typically has a body.
        """
        return self.method in {"POST", "PUT", "PATCH"}

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary with request configuration.
        """
        return {
            "url": self.url,
            "method": self.method,
            "headers": self.headers.copy(),
            "body": self.body.copy() if self.body else None,
            "timeout_seconds": self.timeout_seconds,
            "ssl_verify": self.ssl_verify,
            "retry_enabled": self.retry_enabled,
            "retry_max_attempts": self.retry_max_attempts,
        }


@dataclass
class WebhookExecution:
    """Execution record for a webhook call.

    This entity tracks the execution of a webhook for a specific
    workflow action, including request/response details and status.

    Attributes:
        id: Unique identifier for the execution.
        workflow_execution_id: The workflow execution instance.
        webhook_config_id: The webhook configuration being used.
        status: Current execution status.
        attempt_number: Current attempt number (starts at 1).
        request_url: The URL that was called.
        request_method: HTTP method used.
        request_headers: Headers sent (excluding auth).
        request_body: Body sent (truncated if large).
        response_status: HTTP status code received.
        response_headers: Response headers received.
        response_body: Response body (truncated if > 10KB).
        duration_ms: Request duration in milliseconds.
        error_type: Classified error type (if failed).
        error_message: Error message (if failed).
        created_at: When the execution was created.
        completed_at: When the execution completed.
    """

    id: UUID
    workflow_execution_id: UUID
    webhook_config_id: UUID
    status: WebhookExecutionStatus = WebhookExecutionStatus.PENDING
    attempt_number: int = 1
    request_url: str = ""
    request_method: str = ""
    request_headers: dict[str, str] = field(default_factory=dict)
    request_body: dict[str, Any] | None = None
    response_status: int | None = None
    response_headers: dict[str, str] = field(default_factory=dict)
    response_body: str | None = None
    duration_ms: int | None = None
    error_type: WebhookErrorType | None = None
    error_message: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    def mark_running(self, request_url: str, request_method: str) -> None:
        """Mark execution as running.

        Args:
            request_url: The URL being called.
            request_method: HTTP method being used.
        """
        self.status = WebhookExecutionStatus.RUNNING
        self.request_url = request_url
        self.request_method = request_method

    def mark_success(
        self,
        response_status: int,
        response_headers: dict[str, str],
        response_body: str,
        duration_ms: int,
    ) -> None:
        """Mark execution as successful.

        Args:
            response_status: HTTP status code.
            response_headers: Response headers.
            response_body: Response body (truncated).
            duration_ms: Duration in milliseconds.
        """
        self.status = WebhookExecutionStatus.SUCCESS
        self.response_status = response_status
        self.response_headers = response_headers
        self.response_body = response_body
        self.duration_ms = duration_ms
        self.completed_at = datetime.now(UTC)

    def mark_retry(
        self,
        error_type: WebhookErrorType,
        error_message: str,
        attempt_number: int,
    ) -> None:
        """Mark execution for retry.

        Args:
            error_type: Classified error type.
            error_message: Error message.
            attempt_number: Next attempt number.
        """
        self.status = WebhookExecutionStatus.RETRY
        self.error_type = error_type
        self.error_message = error_message
        self.attempt_number = attempt_number
        self.completed_at = datetime.now(UTC)

    def mark_failed(
        self,
        error_type: WebhookErrorType,
        error_message: str,
        duration_ms: int | None = None,
    ) -> None:
        """Mark execution as failed.

        Args:
            error_type: Classified error type.
            error_message: Error message.
            duration_ms: Duration if request was made.
        """
        self.status = WebhookExecutionStatus.FAILED
        self.error_type = error_type
        self.error_message = error_message
        self.duration_ms = duration_ms
        self.completed_at = datetime.now(UTC)

    def mark_timeout(self, error_message: str, duration_ms: int | None = None) -> None:
        """Mark execution as timed out.

        Args:
            error_message: Error message.
            duration_ms: Duration until timeout.
        """
        self.status = WebhookExecutionStatus.TIMEOUT
        self.error_type = WebhookErrorType.TIMEOUT
        self.error_message = error_message
        self.duration_ms = duration_ms
        self.completed_at = datetime.now(UTC)

    @property
    def is_final_status(self) -> bool:
        """Check if execution is in a final state.

        Returns:
            True if status is success, failed, or timeout.
        """
        return self.status in {
            WebhookExecutionStatus.SUCCESS,
            WebhookExecutionStatus.FAILED,
            WebhookExecutionStatus.TIMEOUT,
        }

    @property
    def should_retry(self) -> bool:
        """Check if execution should be retried.

        Returns:
            True if status is retry and attempts not exhausted.
        """
        return self.status == WebhookExecutionStatus.RETRY

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary containing all execution attributes.
        """
        return {
            "id": str(self.id),
            "workflow_execution_id": str(self.workflow_execution_id),
            "webhook_config_id": str(self.webhook_config_id),
            "status": self.status.value,
            "attempt_number": self.attempt_number,
            "request_url": self.request_url,
            "request_method": self.request_method,
            "request_headers": self.request_headers,
            "request_body": self.request_body,
            "response_status": self.response_status,
            "response_headers": self.response_headers,
            "response_body": self.response_body,
            "duration_ms": self.duration_ms,
            "error_type": self.error_type.value if self.error_type else None,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
