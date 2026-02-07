"""Specification tests for webhook domain entities.

These tests define the expected behavior of webhook domain entities
according to SPEC-WFL-010 requirements.
"""

import pytest

from src.workflows.domain.webhook_entities import (
    WebhookAuthConfig,
    WebhookAuthType,
    WebhookErrorType,
    WebhookExecution,
    WebhookExecutionStatus,
    WebhookRequestConfig,
)
from src.workflows.domain.webhook_exceptions import (
    InvalidWebhookAuthError,
    InvalidWebhookURLError,
)


class TestWebhookAuthConfigSpecification:
    """Specification tests for WebhookAuthConfig.

    REQ-005: Authentication Support
    - None: No authentication headers added
    - Basic: Base64-encoded username:password in Authorization header
    - Bearer: JWT or API token in Authorization header with "Bearer" prefix
    - API Key: Custom header with API key value
    """

    def test_none_authentication_creates_valid_config(self) -> None:
        """Given: No authentication required
        When: Creating none auth config
        Then: Valid config is created with no credentials
        """
        config = WebhookAuthConfig.none()

        assert config.auth_type == WebhookAuthType.NONE
        assert config.username is None
        assert config.password is None
        assert config.token is None
        assert config.header_name is None

    def test_basic_authentication_with_valid_credentials(self) -> None:
        """Given: Valid username and password
        When: Creating basic auth config
        Then: Valid config is created with credentials
        """
        config = WebhookAuthConfig.basic(username="testuser", password="testpass")

        assert config.auth_type == WebhookAuthType.BASIC
        assert config.username == "testuser"
        assert config.password == "testpass"

    def test_basic_authentication_requires_username_and_password(self) -> None:
        """Given: Missing username or password
        When: Creating basic auth config
        Then: InvalidWebhookAuthError is raised
        """
        with pytest.raises(InvalidWebhookAuthError) as exc_info:
            WebhookAuthConfig.basic(username="", password="testpass")

        assert "username and password are required" in str(exc_info.value)

        with pytest.raises(InvalidWebhookAuthError) as exc_info:
            WebhookAuthConfig.basic(username="testuser", password="")

        assert "username and password are required" in str(exc_info.value)

    def test_bearer_authentication_with_valid_token(self) -> None:
        """Given: Valid bearer token
        When: Creating bearer auth config
        Then: Valid config is created with token
        """
        config = WebhookAuthConfig.bearer(token="test-token-123")

        assert config.auth_type == WebhookAuthType.BEARER
        assert config.token == "test-token-123"

    def test_bearer_authentication_requires_token(self) -> None:
        """Given: Missing token
        When: Creating bearer auth config
        Then: InvalidWebhookAuthError is raised
        """
        with pytest.raises(InvalidWebhookAuthError) as exc_info:
            WebhookAuthConfig.bearer(token="")

        assert "token is required" in str(exc_info.value)

    def test_api_key_authentication_with_valid_key(self) -> None:
        """Given: Valid API key and header name
        When: Creating API key auth config
        Then: Valid config is created with header and key
        """
        config = WebhookAuthConfig.api_key(header_name="X-API-Key", token="key-123")

        assert config.auth_type == WebhookAuthType.API_KEY
        assert config.header_name == "X-API-Key"
        assert config.token == "key-123"

    def test_api_key_authentication_requires_header_and_token(self) -> None:
        """Given: Missing header name or token
        When: Creating API key auth config
        Then: InvalidWebhookAuthError is raised
        """
        with pytest.raises(InvalidWebhookAuthError) as exc_info:
            WebhookAuthConfig.api_key(header_name="", token="key-123")

        assert "token and header_name are required" in str(exc_info.value)

        with pytest.raises(InvalidWebhookAuthError) as exc_info:
            WebhookAuthConfig.api_key(header_name="X-API-Key", token="")

        assert "token and header_name are required" in str(exc_info.value)

    def test_auth_config_to_dict_excludes_secrets(self) -> None:
        """Given: Auth config with secrets
        When: Converting to dictionary
        Then: Secrets are excluded from output
        """
        config = WebhookAuthConfig.basic(username="user", password="secret")
        result = config.to_dict()

        assert result["auth_type"] == "basic"
        assert result["username"] == "user"
        assert "password" not in result
        assert "secret" not in str(result)


class TestWebhookRequestConfigSpecification:
    """Specification tests for WebhookRequestConfig.

    REQ-002: HTTP Method Support
    - GET, POST, PUT, PATCH, DELETE

    REQ-003: Custom Headers Configuration
    - Allow users to define custom HTTP headers as key-value pairs

    REQ-004: JSON Payload Construction
    - Construct valid JSON payload using merge fields and static values

    REQ-006: Request Timeout Handling
    - Default timeout: 30 seconds
    - Abort request if timeout exceeded

    REQ-011: SSL/TLS Verification
    - Verify SSL/TLS certificates by default
    - Allow disabling for development/testing
    """

    def test_valid_webhook_request_config(self) -> None:
        """Given: Valid URL and method
        When: Creating request config
        Then: Config is created successfully
        """
        config = WebhookRequestConfig(
            url="https://api.example.com/webhook",
            method="POST",
            headers={"Content-Type": "application/json"},
            body={"data": "test"},
            timeout_seconds=30,
            ssl_verify=True,
        )

        assert config.url == "https://api.example.com/webhook"
        assert config.method == "POST"
        assert config.headers == {"Content-Type": "application/json"}
        assert config.body == {"data": "test"}
        assert config.timeout_seconds == 30
        assert config.ssl_verify is True

    def test_invalid_webhook_url_rejected(self) -> None:
        """Given: Invalid URL (private IP)
        When: Creating request config
        Then: InvalidWebhookURLError is raised

        REQ-013: Webhook URL Validation
        - URL must be valid (RFC 3986)
        - Protocol must be HTTP or HTTPS
        - URL must not target private IP ranges
        """
        with pytest.raises(InvalidWebhookURLError) as exc_info:
            WebhookRequestConfig(url="http://192.168.1.1/webhook")

        assert "private ip address" in str(exc_info.value).lower()

    def test_localhost_url_rejected(self) -> None:
        """Given: localhost URL
        When: Creating request config
        Then: InvalidWebhookURLError is raised
        """
        with pytest.raises(InvalidWebhookURLError) as exc_info:
            WebhookRequestConfig(url="http://localhost/webhook")

        assert "localhost" in str(exc_info.value).lower()

    def test_invalid_http_method_rejected(self) -> None:
        """Given: Invalid HTTP method
        When: Creating request config
        Then: ValueError is raised
        """
        with pytest.raises(ValueError) as exc_info:
            WebhookRequestConfig(url="https://api.example.com", method="INVALID")

        assert "Invalid HTTP method" in str(exc_info.value)

    def test_timeout_must_be_between_1_and_120_seconds(self) -> None:
        """Given: Timeout outside valid range
        When: Creating request config
        Then: ValueError is raised
        """
        with pytest.raises(ValueError):
            WebhookRequestConfig(
                url="https://api.example.com",
                timeout_seconds=0,
            )

        with pytest.raises(ValueError):
            WebhookRequestConfig(
                url="https://api.example.com",
                timeout_seconds=121,
            )

    def test_retry_max_attempts_must_be_between_1_and_5(self) -> None:
        """Given: Retry attempts outside valid range
        When: Creating request config
        Then: ValueError is raised
        """
        with pytest.raises(ValueError):
            WebhookRequestConfig(
                url="https://api.example.com",
                retry_max_attempts=0,
            )

        with pytest.raises(ValueError):
            WebhookRequestConfig(
                url="https://api.example.com",
                retry_max_attempts=6,
            )

    def test_has_body_for_post_put_patch(self) -> None:
        """Given: HTTP method that supports body
        When: Checking has_body
        Then: Returns True
        """
        config = WebhookRequestConfig(url="https://api.example.com", method="POST")
        assert config.has_body is True

        config = WebhookRequestConfig(url="https://api.example.com", method="PUT")
        assert config.has_body is True

        config = WebhookRequestConfig(url="https://api.example.com", method="PATCH")
        assert config.has_body is True

    def test_has_body_false_for_get_delete(self) -> None:
        """Given: HTTP method without body
        When: Checking has_body
        Then: Returns False
        """
        config = WebhookRequestConfig(url="https://api.example.com", method="GET")
        assert config.has_body is False

        config = WebhookRequestConfig(url="https://api.example.com", method="DELETE")
        assert config.has_body is False


class TestWebhookExecutionSpecification:
    """Specification tests for WebhookExecution.

    REQ-008: Response Logging
    - Log HTTP status code
    - Log response headers
    - Log response body (truncated if > 10KB)
    - Log request duration in milliseconds
    - Log timestamp

    REQ-010: Error Classification
    - Network Error: Connection refused, DNS failure, SSL error
    - Timeout Error: Request exceeded timeout limit
    - Client Error (4xx): Bad request, unauthorized, not found
    - Server Error (5xx): Internal server error, bad gateway
    """

    def test_webhook_execution_initial_state(self) -> None:
        """Given: New webhook execution
        When: Created
        Then: Status is pending with no results
        """
        execution = WebhookExecution(
            id="test-id",
            workflow_execution_id="workflow-id",
            webhook_config_id="config-id",
        )

        assert execution.status == WebhookExecutionStatus.PENDING
        assert execution.attempt_number == 1
        assert execution.response_status is None
        assert execution.error_message is None

    def test_mark_running_updates_execution_state(self) -> None:
        """Given: Pending execution
        When: Marked as running
        Then: Status is running with request details
        """
        execution = WebhookExecution(
            id="test-id",
            workflow_execution_id="workflow-id",
            webhook_config_id="config-id",
        )

        execution.mark_running(
            request_url="https://api.example.com/webhook",
            request_method="POST",
        )

        assert execution.status == WebhookExecutionStatus.RUNNING
        assert execution.request_url == "https://api.example.com/webhook"
        assert execution.request_method == "POST"

    def test_mark_success_records_response_details(self) -> None:
        """Given: Running execution
        When: Marked as successful
        Then: Status is success with response details
        """
        execution = WebhookExecution(
            id="test-id",
            workflow_execution_id="workflow-id",
            webhook_config_id="config-id",
        )

        execution.mark_success(
            response_status=200,
            response_headers={"Content-Type": "application/json"},
            response_body='{"status": "ok"}',
            duration_ms=150,
        )

        assert execution.status == WebhookExecutionStatus.SUCCESS
        assert execution.response_status == 200
        assert execution.response_headers == {"Content-Type": "application/json"}
        assert execution.response_body == '{"status": "ok"}'
        assert execution.duration_ms == 150
        assert execution.completed_at is not None

    def test_mark_retry_sets_retry_status(self) -> None:
        """Given: Failed execution that can retry
        When: Marked for retry
        Then: Status is retry with error classification
        """
        execution = WebhookExecution(
            id="test-id",
            workflow_execution_id="workflow-id",
            webhook_config_id="config-id",
        )

        execution.mark_retry(
            error_type=WebhookErrorType.SERVER_ERROR,
            error_message="Internal server error",
            attempt_number=2,
        )

        assert execution.status == WebhookExecutionStatus.RETRY
        assert execution.error_type == WebhookErrorType.SERVER_ERROR
        assert execution.error_message == "Internal server error"
        assert execution.attempt_number == 2
        assert execution.should_retry is True

    def test_mark_failed_sets_final_failed_status(self) -> None:
        """Given: Execution that cannot retry
        When: Marked as failed
        Then: Status is failed with error classification
        """
        execution = WebhookExecution(
            id="test-id",
            workflow_execution_id="workflow-id",
            webhook_config_id="config-id",
        )

        execution.mark_failed(
            error_type=WebhookErrorType.CLIENT_ERROR,
            error_message="Bad request",
            duration_ms=100,
        )

        assert execution.status == WebhookExecutionStatus.FAILED
        assert execution.error_type == WebhookErrorType.CLIENT_ERROR
        assert execution.error_message == "Bad request"
        assert execution.duration_ms == 100
        assert execution.is_final_status is True

    def test_mark_timeout_sets_timeout_status(self) -> None:
        """Given: Execution that timed out
        When: Marked as timeout
        Then: Status is timeout with error classification
        """
        execution = WebhookExecution(
            id="test-id",
            workflow_execution_id="workflow-id",
            webhook_config_id="config-id",
        )

        execution.mark_timeout(
            error_message="Request exceeded 30 second timeout",
            duration_ms=30000,
        )

        assert execution.status == WebhookExecutionStatus.TIMEOUT
        assert execution.error_type == WebhookErrorType.TIMEOUT
        assert execution.error_message == "Request exceeded 30 second timeout"
        assert execution.duration_ms == 30000
        assert execution.is_final_status is True

    def test_is_final_status_for_terminal_states(self) -> None:
        """Given: Execution in various states
        When: Checking if final
        Then: Returns True only for terminal states
        """
        execution = WebhookExecution(
            id="test-id",
            workflow_execution_id="workflow-id",
            webhook_config_id="config-id",
        )

        # Non-final states
        execution.status = WebhookExecutionStatus.PENDING
        assert execution.is_final_status is False

        execution.status = WebhookExecutionStatus.RUNNING
        assert execution.is_final_status is False

        execution.status = WebhookExecutionStatus.RETRY
        assert execution.is_final_status is False

        # Final states
        execution.status = WebhookExecutionStatus.SUCCESS
        assert execution.is_final_status is True

        execution.status = WebhookExecutionStatus.FAILED
        assert execution.is_final_status is True

        execution.status = WebhookExecutionStatus.TIMEOUT
        assert execution.is_final_status is True
