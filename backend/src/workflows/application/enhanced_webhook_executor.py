"""Enhanced webhook executor with comprehensive features.

This module implements the webhook executor with:
- All HTTP methods (GET/POST/PUT/PATCH/DELETE)
- Custom headers
- JSON payload with merge field interpolation
- Multiple authentication methods
- Timeout handling
- Retry with exponential backoff
- Response logging and error classification
- SSL/TLS verification
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from src.workflows.application.action_executor import (
    ActionContext,
    BaseActionExecutor,
    ExecutionResult,
)
from src.workflows.domain.webhook_entities import (
    WebhookAuthConfig,
    WebhookAuthType,
    WebhookErrorType,
    WebhookRequestConfig,
)
from src.workflows.domain.webhook_value_objects import (
    interpolate_merge_fields,
)


class EnhancedWebhookExecutor(BaseActionExecutor):
    """Enhanced executor for webhook_call action type.

    This executor provides comprehensive webhook functionality:
    - All HTTP methods with proper request construction
    - Merge field interpolation in URL, headers, and body
    - Multiple authentication methods
    - Configurable timeout and retry with exponential backoff
    - Comprehensive error classification
    - Response logging with truncation
    """

    # Retry delays in seconds: 5s, 15s, 45s
    RETRY_DELAYS = [5, 15, 45]

    def __init__(self) -> None:
        """Initialize webhook executor."""
        super().__init__()
        # Import here to avoid circular imports
        from src.workflows.infrastructure.webhook_http_client import WebhookHTTPClient

        self._http_client = WebhookHTTPClient()

    async def execute(self, context: ActionContext) -> ExecutionResult:
        """Execute webhook action.

        Args:
            context: Action execution context.

        Returns:
            Execution result with response data or error information.
        """
        from src.workflows.domain.webhook_exceptions import (
            WebhookConnectionLimitError,
            WebhookExecutionError,
            WebhookMergeFieldError,
            WebhookPayloadSizeError,
        )

        start_time = datetime.now(UTC)

        try:
            # Validate configuration
            self._validate_config(
                context,
                ["url", "method"],
            )

            # Parse authentication configuration
            auth_config = self._parse_auth_config(context.action_config)

            # Create request configuration
            request_config = self._parse_request_config(context.action_config, auth_config)

            # Build merge field context
            merge_context = self._build_merge_context(context)

            # Interpolate merge fields in URL
            url = interpolate_merge_fields(
                request_config.url,
                merge_context,
            )

            # Interpolate merge fields in headers
            headers = {}
            for key, value in request_config.headers.items():
                headers[key] = interpolate_merge_fields(value, merge_context)

            # Interpolate merge fields in body
            body = None
            if request_config.body:
                body = interpolate_merge_fields(request_config.body, merge_context)

            # Execute with retry logic
            result = await self._execute_with_retry(
                context.action_id,
                context.execution_id,
                context.contact_id,
                url,
                request_config.method,
                headers,
                body,
                request_config,
                auth_config,
                merge_context,
            )

            duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            result["duration_ms"] = duration_ms

            if result.get("success"):
                return ExecutionResult(
                    success=True,
                    data=result,
                    duration_ms=duration_ms,
                    should_retry=False,
                )
            else:
                error_message = result.get("error_message", "Unknown error")
                should_retry = result.get("should_retry", False)
                retry_delay = result.get("retry_delay_seconds", 60)

                return ExecutionResult(
                    success=False,
                    error=error_message,
                    data=result,
                    duration_ms=duration_ms,
                    should_retry=should_retry,
                    retry_delay_seconds=retry_delay,
                )

        except WebhookExecutionError:
            # Re-raise execution errors
            raise
        except (WebhookConnectionLimitError, WebhookPayloadSizeError) as e:
            # Handle expected errors
            duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            return ExecutionResult(
                success=False,
                error=str(e),
                duration_ms=duration_ms,
                should_retry=False,
            )
        except WebhookMergeFieldError as e:
            # Merge field errors should not retry
            duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            return ExecutionResult(
                success=False,
                error=str(e),
                duration_ms=duration_ms,
                should_retry=False,
            )
        except Exception as e:
            # Handle unexpected errors
            duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            return ExecutionResult(
                success=False,
                error=f"Unexpected error: {e!s}",
                duration_ms=duration_ms,
                should_retry=True,
                retry_delay_seconds=60,
            )

    async def _execute_with_retry(
        self,
        action_id: UUID,
        execution_id: UUID,
        contact_id: UUID,
        url: str,
        method: str,
        headers: dict[str, str],
        body: dict[str, Any] | None,
        request_config: WebhookRequestConfig,
        auth_config: WebhookAuthConfig,
        merge_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute webhook request with retry logic.

        Args:
            action_id: Action being executed.
            execution_id: Workflow execution ID.
            contact_id: Contact being processed.
            url: Interpolated URL.
            method: HTTP method.
            headers: Interpolated headers.
            body: Interpolated body.
            request_config: Request configuration.
            auth_config: Authentication configuration.
            merge_context: Context for merge fields.

        Returns:
            Result dictionary with execution details.
        """
        max_attempts = request_config.retry_max_attempts if request_config.retry_enabled else 1

        for attempt in range(1, max_attempts + 1):
            # Update request config with interpolated values
            interpolated_config = WebhookRequestConfig(
                url=url,
                method=method,
                headers=headers,
                body=body,
                timeout_seconds=request_config.timeout_seconds,
                ssl_verify=request_config.ssl_verify,
                retry_enabled=request_config.retry_enabled,
                retry_max_attempts=request_config.retry_max_attempts,
            )

            # Execute request
            success, result_data = await self._http_client.execute_request(
                interpolated_config,
                auth_config,
                body,
            )

            # Check result
            if success:
                result_data["success"] = True
                result_data["attempt_number"] = attempt
                return result_data

            # Determine if should retry
            error_type = result_data.get("error_type", WebhookErrorType.UNKNOWN)

            should_retry = attempt < max_attempts and self._should_retry_error(
                error_type,
                result_data.get("status_code"),
            )

            if not should_retry:
                # Final failure
                result_data["success"] = False
                result_data["attempt_number"] = attempt
                result_data["should_retry"] = False
                return result_data

            # Calculate retry delay
            retry_delay = self.RETRY_DELAYS[min(attempt - 1, len(self.RETRY_DELAYS) - 1)]
            result_data["retry_delay_seconds"] = retry_delay

            # Wait before retry
            import asyncio

            await asyncio.sleep(retry_delay)

        # All attempts exhausted
        result_data["success"] = False
        result_data["attempt_number"] = max_attempts
        result_data["should_retry"] = False
        return result_data

    def _should_retry_error(
        self,
        error_type: WebhookErrorType,
        status_code: int | None = None,
    ) -> bool:
        """Determine if error should be retried.

        Retry conditions:
        - Network errors (connection, DNS, SSL)
        - Timeout errors
        - Server errors (5xx)
        - 429 (rate limit)

        Don't retry:
        - Client errors (4xx except 429)
        - Configuration errors

        Args:
            error_type: The error type.
            status_code: HTTP status code if applicable.

        Returns:
            True if should retry.
        """
        if error_type in (WebhookErrorType.NETWORK, WebhookErrorType.TIMEOUT):
            return True

        if error_type == WebhookErrorType.SERVER_ERROR:
            return True

        if error_type == WebhookErrorType.CLIENT_ERROR:
            # Retry only on 429 (rate limit)
            return status_code == 429

        return False

    def _parse_auth_config(self, action_config: dict[str, Any]) -> WebhookAuthConfig:
        """Parse authentication configuration from action config.

        Args:
            action_config: Action configuration dictionary.

        Returns:
            WebhookAuthConfig instance.
        """
        auth_type_str = action_config.get("auth_type", "none")
        auth_type = WebhookAuthType(auth_type_str)

        if auth_type == WebhookAuthType.NONE:
            return WebhookAuthConfig.none()

        elif auth_type == WebhookAuthType.BASIC:
            return WebhookAuthConfig.basic(
                username=action_config.get("auth_username", ""),
                password=action_config.get("auth_password", ""),
            )

        elif auth_type == WebhookAuthType.BEARER:
            return WebhookAuthConfig.bearer(
                token=action_config.get("auth_token", ""),
            )

        elif auth_type == WebhookAuthType.API_KEY:
            return WebhookAuthConfig.api_key(
                header_name=action_config.get("auth_header_name", "X-API-Key"),
                token=action_config.get("auth_token", ""),
            )

        else:
            return WebhookAuthConfig.none()

    def _parse_request_config(
        self,
        action_config: dict[str, Any],
        auth_config: WebhookAuthConfig,
    ) -> WebhookRequestConfig:
        """Parse request configuration from action config.

        Args:
            action_config: Action configuration dictionary.
            auth_config: Authentication configuration.

        Returns:
            WebhookRequestConfig instance.
        """
        return WebhookRequestConfig(
            url=action_config["url"],
            method=action_config.get("method", "POST"),
            headers=action_config.get("headers", {}),
            body=action_config.get("body"),
            timeout_seconds=action_config.get("timeout_seconds", 30),
            ssl_verify=action_config.get("ssl_verify", True),
            retry_enabled=action_config.get("retry_enabled", True),
            retry_max_attempts=action_config.get("retry_max_attempts", 3),
        )

    def _build_merge_context(self, context: ActionContext) -> dict[str, Any]:
        """Build context for merge field interpolation.

        Args:
            context: Action execution context.

        Returns:
            Dictionary with available merge fields.
        """
        # This would be populated from:
        # - Contact data (from contacts module)
        # - Workflow data (from workflow execution)
        # - Execution metadata

        return {
            "contact": {
                "id": str(context.contact_id),
                # Additional fields would be loaded from database
            },
            "workflow": {
                "id": str(context.execution_id),
                # Additional fields from workflow config
            },
            "execution": {
                "id": str(context.execution_id),
            },
        }

    async def close(self) -> None:
        """Close HTTP client."""
        await self._http_client.close()
