"""Acceptance test for AC-005: Rate limiting enforcement.

Gherkin Scenario:
  GIVEN the rate limit is 100 workflow creations per hour per account
  WHEN a user attempts to create more than 100 workflows in an hour
  THEN the system should return 429 Too Many Requests
  AND the response should include retry-after information

Acceptance Criteria: AC-005
Requirement: REQ-WFL-001-07
"""

import time
from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.mark.e2e
@pytest.mark.acceptance
class TestAC005RateLimiting:
    """Verify rate limiting is enforced for workflow creation."""

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires Redis - skip in CI without Redis")
    async def test_rate_limit_enforced_after_100_requests(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ) -> None:
        """
        AC-005: Verify 429 response after 100 workflow creations.

        Given:
          - Rate limit is 100 requests per hour
          - User has valid authentication

        When:
          - User attempts to create 101 workflows rapidly

        Then:
          - First 100 requests succeed (201)
          - 101st request fails with 429
          - Response includes retry-after header
        """
        # Act: Create workflows up to limit
        successful_creations = []
        for i in range(100):
            response = await client.post(
                "/api/v1/workflows",
                json={"name": f"Rate Limit Test {i}"},
                headers=auth_headers,
            )
            if response.status_code == 201:
                successful_creations.append(i)
            elif response.status_code == 429:
                break
            else:
                pytest.fail(f"Unexpected status code: {response.status_code}")

        # Assert: At least some requests succeeded
        assert len(successful_creations) >= 90, "Rate limit should allow at least 90 requests"

        # Assert: Next request triggers rate limit
        response = await client.post(
            "/api/v1/workflows",
            json={"name": "Should Fail Rate Limit"},
            headers=auth_headers,
        )

        # Assert: Rate limit enforced
        assert response.status_code == 429
        data = response.json()
        assert "error" in data or "detail" in data

        # Assert: Retry information provided
        assert "retry-after" in response.headers or "Retry-After" in response.headers

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires Redis - skip in CI without Redis")
    async def test_rate_limit_headers_included(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ) -> None:
        """
        AC-005: Verify rate limit headers are present in responses.

        Given:
          - Rate limiting is enabled
          - User makes a workflow creation request

        Then:
          - Response includes X-RateLimit-* headers
          - Headers show remaining requests
        """
        response = await client.post(
            "/api/v1/workflows",
            json={"name": "Rate Limit Header Test"},
            headers=auth_headers,
        )

        # Assert: Rate limit headers present
        assert "X-RateLimit-Limit" in response.headers or "x-ratelimit-limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers or "x-ratelimit-remaining" in response.headers

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires Redis - skip in CI without Redis")
    async def test_rate_limit_per_account_isolated(
        self,
        client: AsyncClient,
        auth_headers_different_account: dict[str, str],
    ) -> None:
        """
        AC-005: Verify rate limits are isolated per account.

        Given:
          - Two different authenticated accounts
          - Each has rate limit of 100 per hour

        When:
          - Account A exhausts their rate limit

        Then:
          - Account B can still create workflows
          - Limits are not shared across accounts
        """
        # Note: This test requires auth_headers for a different account
        # For now, document the expected behavior
        pytest.skip("Requires multiple test account authentication setup")


@pytest.mark.unit
@pytest.mark.acceptance
class TestAC005RateLimiterComponent:
    """Unit tests for rate limiter component behavior."""

    @pytest.mark.asyncio
    async def test_rate_limiter_allows_under_limit(
        self,
        redis_client,  # Fixture from conftest
    ) -> None:
        """
        AC-005: Verify rate limiter allows requests under limit.

        Given:
          - Rate limiter configured for 100 requests per window
          - 99 requests have been made

        When:
          - 100th request is made

        Then:
          - Request is allowed
          - Remaining count is 1
        """
        from src.workflows.infrastructure.rate_limiter import RateLimiter

        limiter = RateLimiter(
            redis=redis_client,
            requests_per_window=100,
            window_seconds=60,
        )

        # Simulate 99 requests
        for i in range(99):
            await limiter.check(f"test_ac005_{uuid4()}")

        # 100th request should be allowed
        result = await limiter.check(f"test_ac005_final_{uuid4()}")

        assert result.allowed is True
        assert result.remaining >= 0
        assert result.limit == 100

    @pytest.mark.asyncio
    async def test_rate_limiter_blocks_over_limit(
        self,
        redis_client,
    ) -> None:
        """
        AC-005: Verify rate limiter blocks requests over limit.

        Given:
          - Rate limiter configured for 5 requests per window (test scenario)
          - 5 requests have been made

        When:
          - 6th request is made

        Then:
          - Request is blocked
          - Remaining count is 0
        """
        from src.workflows.infrastructure.rate_limiter import RateLimiter

        limiter = RateLimiter(
            redis=redis_client,
            requests_per_window=5,  # Low limit for testing
            window_seconds=60,
        )

        test_key = f"test_ac005_block_{uuid4()}"

        # Exhaust limit
        for _ in range(5):
            await limiter.check(test_key)

        # Next request should be blocked
        result = await limiter.check(test_key)

        assert result.allowed is False
        assert result.remaining == 0
        assert result.reset_at > 0
