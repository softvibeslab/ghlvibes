"""Specification tests for webhook value objects.

These tests define the expected behavior of webhook value objects
according to SPEC-WFL-010 requirements.
"""

import pytest

from src.workflows.domain.webhook_exceptions import (
    InvalidWebhookURLError,
    WebhookMergeFieldError,
)
from src.workflows.domain.webhook_value_objects import (
    _get_nested_value,
    build_basic_auth_header,
    build_bearer_auth_header,
    calculate_payload_size,
    classify_http_error,
    classify_network_error,
    extract_response_mapping,
    interpolate_merge_fields,
    truncate_response_body,
    validate_webhook_url,
)


class TestWebhookURLValidationSpecification:
    """Specification tests for webhook URL validation.

    REQ-013: Webhook URL Validation
    - URL format is valid (RFC 3986 compliant)
    - Protocol is HTTP or HTTPS
    - Domain is resolvable
    - URL does not target internal/private IP ranges
    """

    def test_valid_https_url_accepted(self) -> None:
        """Given: Valid HTTPS URL
        When: Validating URL
        Then: No validation errors
        """
        url = "https://api.example.com/webhook"
        errors = validate_webhook_url(url)

        assert errors == []

    def test_valid_http_url_accepted(self) -> None:
        """Given: Valid HTTP URL
        When: Validating URL
        Then: No validation errors
        """
        url = "http://api.example.com/webhook"
        errors = validate_webhook_url(url)

        assert errors == []

    def test_url_with_port_accepted(self) -> None:
        """Given: Valid URL with port
        When: Validating URL
        Then: No validation errors
        """
        url = "https://api.example.com:8443/webhook"
        errors = validate_webhook_url(url)

        assert errors == []

    def test_ftp_url_rejected(self) -> None:
        """Given: URL with FTP protocol
        When: Validating URL
        Then: Validation error about protocol
        """
        url = "ftp://api.example.com/webhook"
        errors = validate_webhook_url(url)

        assert len(errors) > 0
        assert any("HTTP or HTTPS" in error for error in errors)

    def test_localhost_url_rejected(self) -> None:
        """Given: localhost URL
        When: Validating URL
        Then: Validation error about localhost
        """
        url = "http://localhost/webhook"
        errors = validate_webhook_url(url)

        assert len(errors) > 0
        assert any("localhost" in error.lower() for error in errors)

    def test_private_ip_ranges_rejected(self) -> None:
        """Given: URLs targeting private IP ranges
        When: Validating URL
        Then: Validation errors about private IPs
        """
        test_urls = [
            "http://192.168.1.1/webhook",
            "http://10.0.0.1/webhook",
            "http://172.16.0.1/webhook",
        ]

        for url in test_urls:
            errors = validate_webhook_url(url)
            assert len(errors) > 0, f"URL {url} should be rejected"
            assert any("private" in error.lower() or "ip address" in error.lower() for error in errors), f"Expected 'private' or 'ip address' in errors: {errors}"

    def test_url_exceeding_2048_characters_rejected(self) -> None:
        """Given: URL exceeding maximum length
        When: Validating URL
        Then: Validation error about length
        """
        url = f"https://api.example.com/webhook?data={'x' * 2100}"
        errors = validate_webhook_url(url)

        assert len(errors) > 0
        assert any("2048" in error for error in errors)

    def test_url_without_domain_rejected(self) -> None:
        """Given: URL without domain
        When: Validating URL
        Then: Validation error about missing domain
        """
        url = "https:///webhook"
        errors = validate_webhook_url(url)

        assert len(errors) > 0
        assert any("domain" in error.lower() or "host" in error.lower() for error in errors)


class TestMergeFieldInterpolationSpecification:
    """Specification tests for merge field interpolation.

    REQ-014: Merge Field Interpolation
    - Interpolate using double curly brace syntax
    - Support contact fields, workflow metadata, execution tracking
    """

    def test_simple_string_interpolation(self) -> None:
        """Given: Template with merge field
        When: Interpolating with context
        Then: Field is replaced with context value
        """
        template = "Hello {{contact.name}}"
        context = {"contact": {"name": "John Doe"}}

        result = interpolate_merge_fields(template, context)

        assert result == "Hello John Doe"

    def test_nested_field_interpolation(self) -> None:
        """Given: Template with nested field path
        When: Interpolating with nested context
        Then: Nested field is resolved correctly
        """
        template = "{{contact.email.address}}"
        context = {"contact": {"email": {"address": "john@example.com"}}}

        result = interpolate_merge_fields(template, context)

        assert result == "john@example.com"

    def test_dict_interpolation(self) -> None:
        """Given: Template dictionary with merge fields
        When: Interpolating with context
        Then: All fields in dict are interpolated
        """
        template = {
            "name": "{{contact.name}}",
            "email": "{{contact.email}}",
            "static": "value",
        }
        context = {"contact": {"name": "John", "email": "john@example.com"}}

        result = interpolate_merge_fields(template, context)

        assert result["name"] == "John"
        assert result["email"] == "john@example.com"
        assert result["static"] == "value"

    def test_list_interpolation(self) -> None:
        """Given: Template list with merge fields
        When: Interpolating with context
        Then: All items in list are interpolated
        """
        template = ["{{contact.first}}", "{{contact.last}}", "static"]
        context = {"contact": {"first": "John", "last": "Doe"}}

        result = interpolate_merge_fields(template, context)

        assert result == ["John", "Doe", "static"]

    def test_missing_field_leaves_template_unchanged(self) -> None:
        """Given: Template with non-existent field
        When: Interpolating with context
        Then: Original template is preserved
        """
        template = "{{contact.missing.field}}"
        context = {"contact": {"name": "John"}}

        result = interpolate_merge_fields(template, context)

        assert result == "{{contact.missing.field}}"

    def test_get_nested_value_resolves_paths(self) -> None:
        """Given: Nested dictionary
        When: Getting value by dot path
        Then: Correct value is returned
        """
        data = {
            "contact": {
                "profile": {
                    "email": "test@example.com",
                }
            }
        }

        result = _get_nested_value(data, "contact.profile.email")

        assert result == "test@example.com"

    def test_get_nested_value_returns_none_for_missing_path(self) -> None:
        """Given: Dictionary without nested path
        When: Getting non-existent value
        Then: None is returned
        """
        data = {"contact": {"name": "John"}}

        result = _get_nested_value(data, "contact.email")

        assert result is None


class TestResponseProcessingSpecification:
    """Specification tests for response processing.

    REQ-008: Response Logging
    - Log HTTP status code
    - Log response headers
    - Log response body (truncated if > 10KB)

    REQ-009: Response Data Mapping
    - Extract JSON values from response
    - Store in contact custom fields or workflow variables
    """

    def test_truncate_response_body_under_limit(self) -> None:
        """Given: Response body under 10KB
        When: Truncating response
        Then: Body is returned unchanged
        """
        body = "x" * 5000  # 5KB
        result = truncate_response_body(body)

        assert result == body
        assert len(result) == 5000

    def test_truncate_response_body_over_limit(self) -> None:
        """Given: Response body over 10KB
        When: Truncating response
        Then: Body is truncated with ellipsis
        """
        body = "x" * 15000  # 15KB
        result = truncate_response_body(body, max_length=10240)

        assert len(result) == 10240 + len("... (truncated)")
        assert result.endswith("... (truncated)")

    def test_calculate_payload_size_for_json(self) -> None:
        """Given: JSON payload
        When: Calculating size
        Then: Correct byte size is returned
        """
        payload = {"data": "test", "value": 123}
        size = calculate_payload_size(payload)

        # JSON serialization: {"data": "test", "value": 123}
        assert size > 0
        assert size < 100  # Should be small

    def test_calculate_payload_size_for_large_payload(self) -> None:
        """Given: Large JSON payload
        When: Calculating size
        Then: Correct size is returned
        """
        payload = {"data": "x" * 1000000}  # ~1MB of data
        size = calculate_payload_size(payload)

        assert size > 1000000  # Should be over 1MB

    def test_classify_http_error_for_client_errors(self) -> None:
        """Given: 4xx status code
        When: Classifying error
        Then: Returns "client_error"
        """
        for code in [400, 401, 403, 404, 422, 429]:
            result = classify_http_error(code)
            assert result == "client_error"

    def test_classify_http_error_for_server_errors(self) -> None:
        """Given: 5xx status code
        When: Classifying error
        Then: Returns "server_error"
        """
        for code in [500, 502, 503, 504]:
            result = classify_http_error(code)
            assert result == "server_error"

    def test_classify_http_error_for_unknown_codes(self) -> None:
        """Given: Non-error status code
        When: Classifying error
        Then: Returns "unknown"
        """
        for code in [200, 201, 301, 302]:
            result = classify_http_error(code)
            assert result == "unknown"

    def test_extract_response_mapping_from_json(self) -> None:
        """Given: Response body and field mappings
        When: Extracting values
        Then: Correct values are extracted
        """
        response = {
            "user": {"id": 123, "email": "test@example.com"},
            "status": "active",
        }
        mappings = {
            "user_id": "user.id",
            "user_email": "user.email",
            "account_status": "status",
        }

        result = extract_response_mapping(response, mappings)

        assert result == {
            "user_id": 123,
            "user_email": "test@example.com",
            "account_status": "active",
        }

    def test_extract_response_mapping_handles_missing_fields(self) -> None:
        """Given: Response without mapped fields
        When: Extracting values
        Then: Only available fields are extracted
        """
        response = {"user": {"id": 123}}
        mappings = {
            "user_id": "user.id",
            "user_name": "user.name",  # Doesn't exist
        }

        result = extract_response_mapping(response, mappings)

        assert result == {"user_id": 123}
        assert "user_name" not in result


class TestAuthenticationHelpersSpecification:
    """Specification tests for authentication helpers.

    REQ-005: Authentication Support
    """

    def test_build_basic_auth_header(self) -> None:
        """Given: Username and password
        When: Building basic auth header
        Then: Returns Base64-encoded "username:password"
        """
        header = build_basic_auth_header("testuser", "testpass")

        assert header.startswith("Basic ")
        # Base64 encoding of "testuser:testpass"
        assert "dGVzdHVzZXI6dGVzdHBhc3M=" in header or header == "Basic dGVzdHVzZXI6dGVzdHBhc3M="

    def test_build_bearer_auth_header(self) -> None:
        """Given: Bearer token
        When: Building bearer auth header
        Then: Returns "Bearer {token}"
        """
        header = build_bearer_auth_header("test-token-123")

        assert header == "Bearer test-token-123"


class TestNetworkErrorClassificationSpecification:
    """Specification tests for network error classification.

    REQ-010: Error Classification
    - Network Error: Connection refused, DNS failure, SSL error
    - Timeout Error: Request exceeded timeout limit
    """

    def test_classify_timeout_error(self) -> None:
        """Given: Timeout exception
        When: Classifying error
        Then: Returns timeout error type
        """
        error = Exception("Request timeout after 30 seconds")

        error_type, error_message = classify_network_error(error)

        assert error_type == "timeout"

    def test_classify_dns_error(self) -> None:
        """Given: DNS resolution exception
        When: Classifying error
        Then: Returns network error type
        """
        error = Exception("DNS resolution failed for api.example.com")

        error_type, error_message = classify_network_error(error)

        assert error_type == "network"

    def test_classify_connection_error(self) -> None:
        """Given: Connection refused exception
        When: Classifying error
        Then: Returns network error type
        """
        error = Exception("Connection refused by server")

        error_type, error_message = classify_network_error(error)

        assert error_type == "network"

    def test_classify_ssl_error(self) -> None:
        """Given: SSL certificate exception
        When: Classifying error
        Then: Returns network error type
        """
        error = Exception("SSL certificate verification failed")

        error_type, error_message = classify_network_error(error)

        assert error_type == "network"
