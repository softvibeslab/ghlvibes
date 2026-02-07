"""HTTP client infrastructure for webhook execution.

This module provides an async HTTP client pool with connection management,
circuit breaker pattern, and SSL/TLS configuration.
"""

import asyncio
from typing import Any

import httpx
from httpx import AsyncClient, AsyncHTTPTransport, TimeoutException

from src.workflows.domain.webhook_entities import (
    WebhookAuthConfig,
    WebhookAuthType,
    WebhookErrorType,
    WebhookRequestConfig,
)
from src.workflows.domain.webhook_exceptions import (
    WebhookConnectionLimitError,
    WebhookPayloadSizeError,
)
from src.workflows.domain.webhook_value_objects import (
    build_basic_auth_header,
    build_bearer_auth_header,
    calculate_payload_size,
    classify_network_error,
    truncate_response_body,
)


class CircuitBreaker:
    """Circuit breaker for failing webhook endpoints.

    Prevents cascading failures by temporarily disabling requests
    to endpoints that are experiencing failures.

    States:
    - CLOSED: Requests pass through normally
    - OPEN: Requests fail immediately (breaker is tripped)
    - HALF_OPEN: Limited requests allowed to test recovery
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        half_open_attempts: int = 3,
    ) -> None:
        """Initialize circuit breaker.

        Args:
            failure_threshold: Failures before opening circuit.
            timeout_seconds: Seconds to wait before trying again.
            half_open_attempts: Attempts allowed in half-open state.
        """
        self._failure_threshold = failure_threshold
        self._timeout_seconds = timeout_seconds
        self._half_open_attempts = half_open_attempts
        self._failures: dict[str, int] = {}
        self._last_failure_time: dict[str, float] = {}
        self._half_open_count: dict[str, int] = {}
        self._lock = asyncio.Lock()

    async def is_open(self, endpoint: str) -> bool:
        """Check if circuit is open for endpoint.

        Args:
            endpoint: The endpoint URL.

        Returns:
            True if circuit is open (should not make request).
        """
        async with self._lock:
            if endpoint not in self._failures:
                return False

            # Check if timeout has expired
            if endpoint in self._last_failure_time:
                elapsed = asyncio.get_event_loop().time() - self._last_failure_time[endpoint]
                if elapsed > self._timeout_seconds:
                    # Reset to half-open
                    self._half_open_count[endpoint] = 0
                    return False

            return self._failures[endpoint] >= self._failure_threshold

    async def record_success(self, endpoint: str) -> None:
        """Record successful request.

        Args:
            endpoint: The endpoint URL.
        """
        async with self._lock:
            if endpoint in self._failures:
                # Reset on success
                del self._failures[endpoint]
            if endpoint in self._last_failure_time:
                del self._last_failure_time[endpoint]
            if endpoint in self._half_open_count:
                del self._half_open_count[endpoint]

    async def record_failure(self, endpoint: str) -> None:
        """Record failed request.

        Args:
            endpoint: The endpoint URL.
        """
        async with self._lock:
            self._failures[endpoint] = self._failures.get(endpoint, 0) + 1
            self._last_failure_time[endpoint] = asyncio.get_event_loop().time()


class WebhookHTTPClient:
    """HTTP client for webhook execution with connection pooling and circuit breaker.

    Features:
    - Connection pooling for performance
    - Circuit breaker for failing endpoints
    - SSL/TLS verification control
    - Request timeout management
    - Concurrent request limits
    """

    def __init__(
        self,
        pool_connections: int = 100,
        pool_maxsize: int = 100,
        circuit_breaker_failure_threshold: int = 5,
        circuit_breaker_timeout: int = 60,
        max_concurrent_requests: int = 1000,
    ) -> None:
        """Initialize HTTP client.

        Args:
            pool_connections: Number of connection pools to cache.
            pool_maxsize: Maximum number of connections in pool.
            circuit_breaker_failure_threshold: Failures before opening circuit.
            circuit_breaker_timeout: Seconds before retrying open circuit.
            max_concurrent_requests: Maximum concurrent requests globally.
        """
        self._pool_connections = pool_connections
        self._pool_maxsize = pool_maxsize
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_breaker_failure_threshold,
            timeout_seconds=circuit_breaker_timeout,
        )
        self._max_concurrent_requests = max_concurrent_requests
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)
        self._clients: dict[bool, AsyncClient] = {}

    def _get_client(self, ssl_verify: bool) -> AsyncClient:
        """Get or create HTTP client for SSL verification setting.

        Args:
            ssl_verify: Whether to verify SSL certificates.

        Returns:
            AsyncHTTP client instance.
        """
        if ssl_verify not in self._clients:
            limits = httpx.Limits(
                max_connections=self._pool_maxsize,
                max_keepalive_connections=self._pool_connections,
            )
            transport = AsyncHTTPTransport(
                retries=0,  # We handle retries manually
            )

            # SSL verification
            verify = ssl_verify

            self._clients[ssl_verify] = AsyncClient(
                limits=limits,
                transport=transport,
                verify=verify,
                timeout=httpx.Timeout(120.0),  # Max timeout
            )

        return self._clients[ssl_verify]

    async def execute_request(
        self,
        request_config: WebhookRequestConfig,
        auth_config: WebhookAuthConfig,
        body: dict[str, Any] | None = None,
    ) -> tuple[bool, dict[str, Any]]:
        """Execute HTTP request with circuit breaker and retry logic.

        Args:
            request_config: Request configuration.
            auth_config: Authentication configuration.
            body: Optional request body (after interpolation).

        Returns:
            Tuple of (success, result_data).

        Raises:
            WebhookConnectionLimitError: If concurrent limit reached.
            WebhookPayloadSizeError: If payload exceeds size limit.
        """
        # Check concurrent limit
        if self._semaphore.locked():
            raise WebhookConnectionLimitError(
                current=self._max_concurrent_requests,
                limit=self._max_concurrent_requests,
            )

        # Check circuit breaker
        if await self._circuit_breaker.is_open(request_config.url):
            return False, {
                "error_type": WebhookErrorType.SERVER_ERROR,
                "error_message": "Circuit breaker is open for this endpoint",
                "circuit_breaker_open": True,
            }

        # Calculate payload size
        if body:
            payload_size = calculate_payload_size(body)
            if payload_size > 1048576:  # 1MB limit
                raise WebhookPayloadSizeError(payload_size)

        # Acquire semaphore
        async with self._semaphore:
            return await self._execute_request_internal(
                request_config,
                auth_config,
                body,
            )

    async def _execute_request_internal(
        self,
        request_config: WebhookRequestConfig,
        auth_config: WebhookAuthConfig,
        body: dict[str, Any] | None = None,
    ) -> tuple[bool, dict[str, Any]]:
        """Internal request execution.

        Args:
            request_config: Request configuration.
            auth_config: Authentication configuration.
            body: Request body (after interpolation).

        Returns:
            Tuple of (success, result_data).
        """
        client = self._get_client(request_config.ssl_verify)

        # Prepare headers
        headers = request_config.headers.copy()

        # Add authentication headers
        auth_headers = self._build_auth_headers(auth_config)
        headers.update(auth_headers)

        # Prepare request parameters
        request_kwargs: dict[str, Any] = {
            "headers": headers,
            "timeout": request_config.timeout_seconds,
        }

        # Add body for methods that support it
        if request_config.has_body and body:
            request_kwargs["json"] = body
        elif request_config.method == "GET" and body:
            request_kwargs["params"] = body

        start_time = asyncio.get_event_loop().time()

        try:
            # Execute request
            response = await client.request(
                method=request_config.method,
                url=request_config.url,
                **request_kwargs,
            )

            duration_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)

            # Process response
            success = 200 <= response.status_code < 300

            # Extract response body
            response_body = None
            if response.text:
                response_body = truncate_response_body(response.text)

            result_data = {
                "status_code": response.status_code,
                "response_headers": dict(response.headers),
                "response_body": response_body,
                "duration_ms": duration_ms,
            }

            # Record success/failure in circuit breaker
            if success:
                await self._circuit_breaker.record_success(request_config.url)
            else:
                await self._circuit_breaker.record_failure(request_config.url)

            return success, result_data

        except TimeoutException as e:
            duration_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
            await self._circuit_breaker.record_failure(request_config.url)

            return False, {
                "error_type": WebhookErrorType.TIMEOUT,
                "error_message": f"Request timeout: {e!s}",
                "duration_ms": duration_ms,
            }

        except (httpx.HTTPError, httpx.ConnectError) as e:
            duration_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
            await self._circuit_breaker.record_failure(request_config.url)

            error_type_str, error_message = classify_network_error(e)
            error_type = WebhookErrorType(error_type_str) if error_type_str in WebhookErrorType else WebhookErrorType.NETWORK

            return False, {
                "error_type": error_type,
                "error_message": error_message,
                "duration_ms": duration_ms,
            }

        except Exception as e:
            duration_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
            await self._circuit_breaker.record_failure(request_config.url)

            return False, {
                "error_type": WebhookErrorType.UNKNOWN,
                "error_message": f"Unexpected error: {e!s}",
                "duration_ms": duration_ms,
            }

    def _build_auth_headers(self, auth_config: WebhookAuthConfig) -> dict[str, str]:
        """Build authentication headers.

        Args:
            auth_config: Authentication configuration.

        Returns:
            Dictionary of authentication headers.
        """
        headers = {}

        if auth_config.auth_type == WebhookAuthType.BASIC:
            headers["Authorization"] = build_basic_auth_header(
                auth_config.username,  # type: ignore
                auth_config.password,  # type: ignore
            )
        elif auth_config.auth_type == WebhookAuthType.BEARER:
            headers["Authorization"] = build_bearer_auth_header(
                auth_config.token,  # type: ignore
            )
        elif auth_config.auth_type == WebhookAuthType.API_KEY:
            header_name = auth_config.header_name or "X-API-Key"
            headers[header_name] = auth_config.token  # type: ignore

        return headers

    async def close(self) -> None:
        """Close all HTTP clients."""
        for client in self._clients.values():
            await client.aclose()
        self._clients.clear()

    async def __aenter__(self) -> "WebhookHTTPClient":
        """Context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Context manager exit."""
        await self.close()
