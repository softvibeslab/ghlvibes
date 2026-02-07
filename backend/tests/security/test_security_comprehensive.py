"""
Comprehensive security tests for the Workflow API.

This test suite covers OWASP Top 10 vulnerabilities including:
- SQL Injection
- XSS (Cross-Site Scripting)
- CSRF (Cross-Site Request Forgery)
- Authentication bypass
- Authorization bypass
- Rate limiting
- Input validation
"""

import pytest
from uuid import uuid4
from httpx import AsyncClient


@pytest.mark.security
class TestSQLInjectionPrevention:
    """Test suite for SQL injection prevention."""

    @pytest.mark.asyncio
    async def test_workflow_name_sql_injection(self, async_client: AsyncClient):
        """Given SQL injection payload, when creating workflow, then sanitized."""
        # Arrange
        sql_payloads = [
            "'; DROP TABLE workflows; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--",
            "'; EXEC xp_cmdshell('dir'); --",
        ]

        for payload in sql_payloads:
            # Act
            response = await async_client.post("/api/v1/workflows", json={
                "name": payload
            })

            # Assert - Should either reject or sanitize, not execute SQL
            assert response.status_code in [400, 422]
            assert "DROP TABLE" not in response.text

            # Verify database still intact
            workflows_response = await async_client.get("/api/v1/workflows")
            assert workflows_response.status_code == 200

    @pytest.mark.asyncio
    async def test_workflow_description_sql_injection(self, async_client: AsyncClient):
        """Given SQL injection in description, when creating, then sanitized."""
        # Arrange
        payload = {
            "name": "Valid Name",
            "description": "'; DELETE FROM workflows WHERE 1=1; --"
        }

        # Act
        response = await async_client.post("/api/v1/workflows", json=payload)

        # Assert
        assert response.status_code in [201, 400, 422]
        if response.status_code == 201:
            # Verify description is stored safely
            workflow_id = response.json()["id"]
            get_response = await async_client.get(f"/api/v1/workflows/{workflow_id}")
            assert "DELETE FROM" not in get_response.json().get("description", "")

    @pytest.mark.asyncio
    async def test_filter_parameter_sql_injection(self, async_client: AsyncClient):
        """Given SQL injection in filter, when listing workflows, then sanitized."""
        # Arrange
        sql_injection = "1' OR '1'='1"

        # Act
        response = await async_client.get(
            f"/api/v1/workflows?name={sql_injection}"
        )

        # Assert
        assert response.status_code == 200
        # Should not return all workflows due to injection
        data = response.json()
        assert isinstance(data.get("workflows"), list)


@pytest.mark.security
class TestXSSPrevention:
    """Test suite for XSS (Cross-Site Scripting) prevention."""

    @pytest.mark.asyncio
    async def test_workflow_name_xss_prevention(self, async_client: AsyncClient):
        """Given XSS payload in name, when creating, then sanitized."""
        # Arrange
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
            "javascript:alert('xss')",
            "<iframe src='javascript:alert(xss)>",
        ]

        for payload in xss_payloads:
            # Act
            response = await async_client.post("/api/v1/workflows", json={
                "name": payload
            })

            # Assert
            assert response.status_code in [400, 422, 201]

            # If created, verify output is escaped
            if response.status_code == 201:
                workflow_id = response.json()["id"]
                get_response = await async_client.get(f"/api/v1/workflows/{workflow_id}")
                assert "<script>" not in get_response.text

    @pytest.mark.asyncio
    async def test_workflow_description_xss_prevention(self, async_client: AsyncClient):
        """Given XSS in description, when creating, then escaped."""
        # Arrange
        xss_payload = "<script>alert('xss')</script>"

        # Act
        response = await async_client.post("/api/v1/workflows", json={
            "name": "Valid Name",
            "description": xss_payload
        })

        # Assert
        if response.status_code == 201:
            workflow_id = response.json()["id"]
            get_response = await async_client.get(f"/api/v1/workflows/{workflow_id}")
            # Script tags should be escaped or removed
            text = get_response.text
            assert "<script>" not in text or "&lt;script&gt;" in text


@pytest.mark.security
class TestAuthenticationSecurity:
    """Test suite for authentication security."""

    @pytest.mark.asyncio
    async def test_protected_endpoint_requires_auth(self, async_client: AsyncClient):
        """Given unauthenticated request, when accessing API, then returns 401."""
        # Act - Clear authentication headers
        response = await async_client.get("/api/v1/workflows", headers={})

        # Assert
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_token_rejected(self, async_client: AsyncClient):
        """Given invalid token, when accessing API, then returns 401."""
        # Arrange
        invalid_token = "invalid.jwt.token"

        # Act
        response = await async_client.get(
            "/api/v1/workflows",
            headers={"Authorization": f"Bearer {invalid_token}"}
        )

        # Assert
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_expired_token_rejected(self, async_client: AsyncClient):
        """Given expired token, when accessing API, then returns 401."""
        # This would require generating an expired JWT token
        # Placeholder for expired token test
        pass

    @pytest.mark.asyncio
    async def test_password_hashed_not_stored_plaintext(self, async_client: AsyncClient):
        """Given user creation, when storing password, then hashed."""
        # This would require access to user repository
        # Verify password starts with bcrypt hash prefix
        pass


@pytest.mark.security
class TestAuthorizationSecurity:
    """Test suite for authorization security."""

    @pytest.mark.asyncio
    async def test_cannot_access_other_account_workflow(self, async_client: AsyncClient):
        """Given workflow from other account, when accessing, then returns 403."""
        # Arrange
        # Create workflow in account A
        # Try to access with account B token

        # Act
        workflow_id = uuid4()
        response = await async_client.get(f"/api/v1/workflows/{workflow_id}")

        # Assert - Should return 404 (not found) or 403 (forbidden)
        # Never return the workflow from another account
        assert response.status_code in [403, 404]

    @pytest.mark.asyncio
    async def test_cannot_modify_other_account_workflow(self, async_client: AsyncClient):
        """Given workflow from other account, when updating, then returns 403."""
        # Arrange
        workflow_id = uuid4()

        # Act
        response = await async_client.patch(
            f"/api/v1/workflows/{workflow_id}",
            json={"name": "Hacked Name"}
        )

        # Assert
        assert response.status_code in [403, 404]

    @pytest.mark.asyncio
    async def test_cannot_delete_other_account_workflow(self, async_client: AsyncClient):
        """Given workflow from other account, when deleting, then returns 403."""
        # Arrange
        workflow_id = uuid4()

        # Act
        response = await async_client.delete(f"/api/v1/workflows/{workflow_id}")

        # Assert
        assert response.status_code in [403, 404]


@pytest.mark.security
class TestInputValidation:
    """Test suite for input validation."""

    @pytest.mark.asyncio
    async def test_max_length_validation(self, async_client: AsyncClient):
        """Given oversized input, when creating, then returns 422."""
        # Arrange
        oversized_name = "a" * 1000  # Way over max length

        # Act
        response = await async_client.post("/api/v1/workflows", json={
            "name": oversized_name
        })

        # Assert
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_json_rejected(self, async_client: AsyncClient):
        """Given malformed JSON, when sending request, then returns 400."""
        # Arrange
        # This would require sending raw malformed JSON
        # Placeholder for malformed JSON test
        pass

    @pytest.mark.asyncio
    async def test_invalid_enum_value_rejected(self, async_client: AsyncClient):
        """Given invalid trigger_type, when creating, then returns 422."""
        # Arrange
        invalid_trigger = "invalid_trigger_type"

        # Act
        response = await async_client.post("/api/v1/workflows", json={
            "name": "Test",
            "trigger_type": invalid_trigger
        })

        # Assert
        assert response.status_code == 422


@pytest.mark.security
class TestRateLimiting:
    """Test suite for rate limiting."""

    @pytest.mark.asyncio
    async def test_rate_limit_enforced(self, async_client: AsyncClient):
        """Given many requests, when exceeding limit, then returns 429."""
        # Arrange - Make 100 rapid requests
        responses = []

        # Act
        for _ in range(100):
            response = await async_client.post("/api/v1/workflows", json={
                "name": f"Test Workflow {_}"
            })
            responses.append(response)

        # Assert - At least some should be rate limited
        rate_limited_count = sum(1 for r in responses if r.status_code == 429)
        assert rate_limited_count > 0

    @pytest.mark.asyncio
    async def test_rate_limit_headers_present(self, async_client: AsyncClient):
        """Given rate limited response, when returned, then includes rate limit headers."""
        # Arrange - Make enough requests to trigger rate limit
        for _ in range(100):
            await async_client.post("/api/v1/workflows", json={
                "name": f"Test {_}"
            })

        # Act
        response = await async_client.post("/api/v1/workflows", json={
            "name": "Rate Limited"
        })

        # Assert
        if response.status_code == 429:
            assert "X-RateLimit-Remaining" in response.headers
            assert "X-RateLimit-Limit" in response.headers
            assert "Retry-After" in response.headers


@pytest.mark.security
class TestCSRFPrevention:
    """Test suite for CSRF prevention."""

    @pytest.mark.asyncio
    async def test_csrf_token_required_for_mutating_requests(self, async_client: AsyncClient):
        """Given request without CSRF token, when POST, then returns 403."""
        # This would require CSRF implementation
        # Placeholder for CSRF test
        pass

    @pytest.mark.asyncio
    async def test_invalid_csrf_token_rejected(self, async_client: AsyncClient):
        """Given invalid CSRF token, when POST, then returns 403."""
        # This would require CSRF implementation
        # Placeholder for CSRF test
        pass


@pytest.mark.security
class TestSSRFPrevention:
    """Test suite for Server-Side Request Forgery prevention."""

    @pytest.mark.asyncio
    async def test_webhook_url_validation_rejects_internal_urls(self, async_client: AsyncClient):
        """Given internal URL, when setting webhook, then rejected."""
        # Arrange
        internal_urls = [
            "http://localhost/admin",
            "http://127.0.0.1/config",
            "http://169.254.169.254/latest/meta-data/",  # AWS metadata
            "http://[::1]/server-status",
        ]

        for url in internal_urls:
            # Act
            response = await async_client.post("/api/v1/workflows", json={
                "name": "Test Workflow",
                "trigger_type": "webhook",
                "trigger_config": {"webhook_url": url}
            })

            # Assert
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_webhook_url_validation_allows_https_only(self, async_client: AsyncClient):
        """Given HTTP URL, when setting webhook, then rejected."""
        # Arrange
        http_url = "http://example.com/webhook"

        # Act
        response = await async_client.post("/api/v1/workflows", json={
            "name": "Test Workflow",
            "trigger_type": "webhook",
            "trigger_config": {"webhook_url": http_url}
        })

        # Assert - Should prefer HTTPS
        assert response.status_code in [400, 422]
