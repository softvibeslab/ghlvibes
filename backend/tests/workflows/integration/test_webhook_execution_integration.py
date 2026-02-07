"""Integration tests for webhook execution.

These tests verify the webhook executor works end-to-end
with HTTP client, retry logic, and error handling.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import Response as HTTPXResponse

from src.workflows.application.action_executor import ActionContext, ExecutionResult
from src.workflows.application.enhanced_webhook_executor import EnhancedWebhookExecutor
from src.workflows.domain.webhook_entities import (
    WebhookAuthConfig,
    WebhookAuthType,
    WebhookErrorType,
)


@pytest_asyncio.fixture
async def webhook_executor():
    """Create webhook executor for testing."""
    executor = EnhancedWebhookExecutor()
    yield executor
    await executor.close()


class TestWebhookExecutorIntegration:
    """Integration tests for EnhancedWebhookExecutor."""

    @pytest.mark.asyncio
    async def test_execute_webhook_with_success_response(
        self,
        webhook_executor: EnhancedWebhookExecutor,
    ) -> None:
        """Given: Valid webhook configuration
        When: Executing webhook with successful response
        Then: Returns success result with response data
        """
        context = ActionContext(
            execution_id="exec-123",
            contact_id="contact-123",
            account_id="account-123",
            action_id="action-123",
            action_config={
                "url": "https://api.example.com/webhook",
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "body": {"test": "data"},
                "auth_type": "none",
                "timeout_seconds": 30,
            },
        )

        # Mock HTTP client
        with patch.object(
            webhook_executor._http_client,
            "execute_request",
            AsyncMock(
                return_value=(
                    True,
                    {
                        "status_code": 200,
                        "response_headers": {"content-type": "application/json"},
                        "response_body": '{"success": true}',
                        "duration_ms": 150,
                    },
                )
            ),
        ):
            result = await webhook_executor.execute(context)

        assert result.success is True
        assert result.data["status_code"] == 200
        assert result.duration_ms > 0
        assert result.should_retry is False

    @pytest.mark.asyncio
    async def test_execute_webhook_with_bearer_auth(
        self,
        webhook_executor: EnhancedWebhookExecutor,
    ) -> None:
        """Given: Webhook with bearer authentication
        When: Executing webhook
        Then: Request includes bearer token header
        """
        context = ActionContext(
            execution_id="exec-123",
            contact_id="contact-123",
            account_id="account-123",
            action_id="action-123",
            action_config={
                "url": "https://api.example.com/webhook",
                "method": "POST",
                "auth_type": "bearer",
                "auth_token": "test-token-123",
            },
        )

        with patch.object(
            webhook_executor._http_client,
            "execute_request",
            AsyncMock(
                return_value=(
                    True,
                    {
                        "status_code": 200,
                        "response_headers": {},
                        "response_body": '{"ok": true}',
                        "duration_ms": 100,
                    },
                )
            ),
        ) as mock_execute:
            result = await webhook_executor.execute(context)

            # Verify auth config was passed
            assert result.success is True
            call_args = mock_execute.call_args
            auth_config = call_args[0][1]
            assert isinstance(auth_config, WebhookAuthConfig)
            assert auth_config.auth_type == WebhookAuthType.BEARER

    @pytest.mark.asyncio
    async def test_execute_webhook_with_merge_fields(
        self,
        webhook_executor: EnhancedWebhookExecutor,
    ) -> None:
        """Given: Webhook URL and body with merge fields
        When: Executing webhook with contact context
        Then: Merge fields are interpolated correctly
        """
        context = ActionContext(
            execution_id="exec-123",
            contact_id="contact-123",
            account_id="account-123",
            action_id="action-123",
            action_config={
                "url": "https://api.example.com/webhook/{{contact.id}}",
                "method": "POST",
                "body": {
                    "contact_id": "{{contact.id}}",
                    "execution_id": "{{execution.id}}",
                    "static": "value",
                },
                "auth_type": "none",
            },
        )

        with patch.object(
            webhook_executor._http_client,
            "execute_request",
            AsyncMock(
                return_value=(
                    True,
                    {
                        "status_code": 200,
                        "response_headers": {},
                        "response_body": "{}",
                        "duration_ms": 100,
                    },
                )
            ),
        ) as mock_execute:
            result = await webhook_executor.execute(context)

            assert result.success is True

            # Verify interpolated URL and body
            call_args = mock_execute.call_args
            request_config = call_args[0][0]
            assert str(context.contact_id) in request_config.url

    @pytest.mark.asyncio
    async def test_execute_webhook_with_retry_on_server_error(
        self,
        webhook_executor: EnhancedWebhookExecutor,
    ) -> None:
        """Given: Webhook that returns 500 error
        When: Executing with retry enabled
        Then: Retries with exponential backoff

        REQ-007: Retry Mechanism
        - Retry on 5xx server errors
        - Exponential backoff: 5s, 15s, 45s
        """
        context = ActionContext(
            execution_id="exec-123",
            contact_id="contact-123",
            account_id="account-123",
            action_id="action-123",
            action_config={
                "url": "https://api.example.com/webhook",
                "method": "POST",
                "retry_enabled": True,
                "retry_max_attempts": 3,
                "auth_type": "none",
            },
        )

        # Mock first attempt fails, second succeeds
        with patch.object(
            webhook_executor._http_client,
            "execute_request",
            AsyncMock(
                side_effect=[
                    (
                        False,
                        {
                            "error_type": WebhookErrorType.SERVER_ERROR,
                            "status_code": 500,
                            "error_message": "Internal server error",
                        },
                    ),
                    (
                        True,
                        {
                            "status_code": 200,
                            "response_headers": {},
                            "response_body": '{"success": true}',
                            "duration_ms": 100,
                        },
                    ),
                ]
            ),
        ):
            result = await webhook_executor.execute(context)

        assert result.success is True
        assert result.data.get("attempt_number") == 2

    @pytest.mark.asyncio
    async def test_execute_webhook_fails_on_client_error(
        self,
        webhook_executor: EnhancedWebhookExecutor,
    ) -> None:
        """Given: Webhook that returns 401 unauthorized
        When: Executing
        Then: Does not retry, returns failure

        REQ-010: Error Classification
        - Client Error (4xx): Don't retry
        """
        context = ActionContext(
            execution_id="exec-123",
            contact_id="contact-123",
            account_id="account-123",
            action_id="action-123",
            action_config={
                "url": "https://api.example.com/webhook",
                "method": "POST",
                "auth_type": "bearer",
                "auth_token": "invalid-token",
            },
        )

        with patch.object(
            webhook_executor._http_client,
            "execute_request",
            AsyncMock(
                return_value=(
                    False,
                    {
                        "error_type": WebhookErrorType.CLIENT_ERROR,
                        "status_code": 401,
                        "error_message": "Unauthorized",
                    },
                )
            ),
        ):
            result = await webhook_executor.execute(context)

        assert result.success is False
        assert result.should_retry is False
        assert "Unauthorized" in result.error

    @pytest.mark.asyncio
    async def test_execute_webhook_with_timeout(
        self,
        webhook_executor: EnhancedWebhookExecutor,
    ) -> None:
        """Given: Webhook that times out
        When: Executing
        Then: Returns timeout error with retry enabled

        REQ-006: Request Timeout Handling
        - Abort request if timeout exceeded
        - Mark as timeout error
        """
        context = ActionContext(
            execution_id="exec-123",
            contact_id="contact-123",
            account_id="account-123",
            action_id="action-123",
            action_config={
                "url": "https://api.example.com/webhook",
                "method": "POST",
                "timeout_seconds": 5,
                "auth_type": "none",
            },
        )

        with patch.object(
            webhook_executor._http_client,
            "execute_request",
            AsyncMock(
                return_value=(
                    False,
                    {
                        "error_type": WebhookErrorType.TIMEOUT,
                        "error_message": "Request timeout after 5 seconds",
                        "duration_ms": 5000,
                    },
                )
            ),
        ):
            result = await webhook_executor.execute(context)

        assert result.success is False
        assert result.should_retry is True
        assert "timeout" in result.error.lower()

    @pytest.mark.asyncio
    async def test_execute_webhook_all_http_methods(
        self,
        webhook_executor: EnhancedWebhookExecutor,
    ) -> None:
        """Given: Webhook with various HTTP methods
        When: Executing GET, POST, PUT, PATCH, DELETE
        Then: Each method executes correctly

        REQ-002: HTTP Method Support
        """
        methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]

        for method in methods:
            context = ActionContext(
                execution_id="exec-123",
                contact_id="contact-123",
                account_id="account-123",
                action_id="action-123",
                action_config={
                    "url": "https://api.example.com/webhook",
                    "method": method,
                    "auth_type": "none",
                },
            )

            with patch.object(
                webhook_executor._http_client,
                "execute_request",
                AsyncMock(
                    return_value=(
                        True,
                        {
                            "status_code": 200,
                            "response_headers": {},
                            "response_body": "{}",
                            "duration_ms": 50,
                        },
                    )
                ),
            ):
                result = await webhook_executor.execute(context)

            assert result.success is True, f"Method {method} failed"

    @pytest.mark.asyncio
    async def test_execute_webhook_custom_headers(
        self,
        webhook_executor: EnhancedWebhookExecutor,
    ) -> None:
        """Given: Webhook with custom headers
        When: Executing
        Then: Custom headers are included in request

        REQ-003: Custom Headers Configuration
        """
        context = ActionContext(
            execution_id="exec-123",
            contact_id="contact-123",
            account_id="account-123",
            action_id="action-123",
            action_config={
                "url": "https://api.example.com/webhook",
                "method": "POST",
                "headers": {
                    "X-Custom-Header": "custom-value",
                    "X-Request-ID": "req-123",
                },
                "auth_type": "none",
            },
        )

        with patch.object(
            webhook_executor._http_client,
            "execute_request",
            AsyncMock(
                return_value=(
                    True,
                    {
                        "status_code": 200,
                        "response_headers": {},
                        "response_body": "{}",
                        "duration_ms": 100,
                    },
                )
            ),
        ) as mock_execute:
            result = await webhook_executor.execute(context)

            assert result.success is True

            # Verify headers were passed
            call_args = mock_execute.call_args
            request_config = call_args[0][0]
            assert request_config.headers["X-Custom-Header"] == "custom-value"
            assert request_config.headers["X-Request-ID"] == "req-123"

    @pytest.mark.asyncio
    async def test_execute_webhook_ssl_verification_control(
        self,
        webhook_executor: EnhancedWebhookExecutor,
    ) -> None:
        """Given: Webhook with SSL verification disabled
        When: Executing
        Then: Request is made without SSL verification

        REQ-011: SSL/TLS Verification
        """
        context = ActionContext(
            execution_id="exec-123",
            contact_id="contact-123",
            account_id="account-123",
            action_id="action-123",
            action_config={
                "url": "https://api.example.com/webhook",
                "method": "POST",
                "ssl_verify": False,  # Disable for testing
                "auth_type": "none",
            },
        )

        with patch.object(
            webhook_executor._http_client,
            "execute_request",
            AsyncMock(
                return_value=(
                    True,
                    {
                        "status_code": 200,
                        "response_headers": {},
                        "response_body": "{}",
                        "duration_ms": 100,
                    },
                )
            ),
        ) as mock_execute:
            result = await webhook_executor.execute(context)

            assert result.success is True

            # Verify SSL config was passed
            call_args = mock_execute.call_args
            request_config = call_args[0][0]
            assert request_config.ssl_verify is False
