"""Value objects for webhook integration.

This module defines value objects for webhook URL validation,
merge field interpolation, and response processing.
"""

import base64
import json
import re
from ipaddress import IPv4Address, IPv6Address, ip_network
from typing import Any
from urllib.parse import urlparse


# URL validation patterns
PRIVATE_IP_PATTERNS = [
    re.compile(r"^10\."),
    re.compile(r"^172\.(1[6-9]|2[0-9]|3[01])\."),
    re.compile(r"^192\.168\."),
    re.compile(r"^127\."),
    re.compile(r"^0\."),
]

PRIVATE_NETWORKS = [
    ip_network("10.0.0.0/8"),
    ip_network("172.16.0.0/12"),
    ip_network("192.168.0.0/16"),
    ip_network("127.0.0.0/8"),
    ip_network("0.0.0.0/8"),
]

# Merge field pattern: {{field_name}} or {{contact.field_name}}
MERGE_FIELD_PATTERN = re.compile(r"\{\{([^}]+)\}\}")


def validate_webhook_url(url: str) -> list[str]:
    """Validate webhook URL.

    Checks:
    - URL format is valid (RFC 3986)
    - Protocol is HTTP or HTTPS
    - Domain is present
    - URL does not target internal/private IP ranges
    - URL does not exceed 2048 characters

    Args:
        url: The URL to validate.

    Returns:
        List of validation errors (empty if valid).
    """
    errors = []

    # Check length first
    if len(url) > 2048:
        errors.append("URL exceeds maximum length of 2048 characters")
        return errors

    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        errors.append(f"Invalid URL format: {e}")
        return errors

    # Check scheme
    if parsed.scheme not in ("http", "https"):
        errors.append("URL must use HTTP or HTTPS protocol")
        return errors

    # Check network location (domain)
    if not parsed.netloc:
        errors.append("URL must include a domain or host")
        return errors

    # Block localhost and internal hostnames
    hostname = parsed.hostname
    if hostname:
        hostname_lower = hostname.lower()

        # Block localhost variations
        if hostname_lower in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
            errors.append("URL cannot target localhost")
            return errors

        # Block private IP ranges
        try:
            # Try parsing as IP address
            addr = IPv4Address(hostname) if "." in hostname else IPv6Address(hostname)

            # Check if in private range
            for network in PRIVATE_NETWORKS:
                if addr in network:
                    errors.append(f"URL cannot target private IP address: {hostname}")
                    return errors
        except Exception:
            # Not an IP address, check hostname patterns
            for pattern in PRIVATE_IP_PATTERNS:
                if pattern.match(hostname_lower):
                    errors.append(f"URL cannot target private hostname: {hostname}")
                    return errors

    return errors


def interpolate_merge_fields(
    template: Any,
    context: dict[str, Any],
    max_depth: int = 10,
) -> Any:
    """Interpolate merge fields in a template.

    Supports:
    - {{contact.field_name}} - Contact fields
    - {{workflow.name}} - Workflow metadata
    - {{execution.id}} - Execution tracking
    - Custom fields in context

    Args:
        template: The template (string, dict, or list).
        context: Context data for interpolation.
        max_depth: Maximum recursion depth (prevent infinite loops).

    Returns:
        Template with merge fields replaced.

    Raises:
        WebhookMergeFieldError: If interpolation fails.
    """
    from src.workflows.domain.webhook_exceptions import WebhookMergeFieldError

    if max_depth <= 0:
        raise WebhookMergeFieldError("max_depth", "Maximum recursion depth exceeded")

    if isinstance(template, str):
        # Replace merge fields in string
        def replace_match(match: re.Match[str]) -> str:
            field_path = match.group(1).strip()
            value = _get_nested_value(context, field_path)

            if value is None:
                # Keep original if field not found
                return match.group(0)

            # Convert to string
            return str(value)

        return MERGE_FIELD_PATTERN.sub(replace_match, template)

    elif isinstance(template, dict):
        # Recursively interpolate dict values
        return {
            key: interpolate_merge_fields(value, context, max_depth - 1)
            for key, value in template.items()
        }

    elif isinstance(template, list):
        # Recursively interpolate list items
        return [
            interpolate_merge_fields(item, context, max_depth - 1) for item in template
        ]

    else:
        # Return as-is for other types
        return template


def _get_nested_value(data: dict[str, Any], path: str) -> Any:
    """Get nested value from dictionary using dot notation.

    Args:
        data: Source dictionary.
        path: Dot-separated path (e.g., "contact.email").

    Returns:
        Value at path, or None if not found.
    """
    keys = path.split(".")
    value: Any = data

    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return None

        if value is None:
            return None

    return value


def build_basic_auth_header(username: str, password: str) -> str:
    """Build Basic authentication header value.

    Args:
        username: Username.
        password: Password.

    Returns:
        Base64-encoded "username:password" string for Authorization header.
    """
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


def build_bearer_auth_header(token: str) -> str:
    """Build Bearer authentication header value.

    Args:
        token: Bearer token.

    Returns:
        "Bearer {token}" string for Authorization header.
    """
    return f"Bearer {token}"


def truncate_response_body(body: str, max_length: int = 10240) -> str:
    """Truncate response body if too large.

    Args:
        body: Response body string.
        max_length: Maximum length (default 10KB).

    Returns:
        Truncated body with ellipsis if needed.
    """
    if len(body) <= max_length:
        return body

    return body[:max_length] + "... (truncated)"


def calculate_payload_size(payload: dict[str, Any]) -> int:
    """Calculate payload size in bytes.

    Args:
        payload: JSON payload.

    Returns:
        Size in bytes when JSON-serialized.
    """
    return len(json.dumps(payload).encode())


def classify_http_error(status_code: int) -> str:
    """Classify HTTP error into error type.

    Args:
        status_code: HTTP status code.

    Returns:
        Error type string (client_error, server_error, or unknown).
    """
    if 400 <= status_code < 500:
        return "client_error"
    elif 500 <= status_code < 600:
        return "server_error"
    else:
        return "unknown"


def classify_network_error(error: Exception) -> tuple[str, str]:
    """Classify network error into error type and message.

    Args:
        error: The exception that occurred.

    Returns:
        Tuple of (error_type, error_message).
    """
    error_message = str(error)
    error_type = "network"

    error_lower = error_message.lower()

    # Check for timeout
    if any(keyword in error_lower for keyword in ["timeout", "timed out"]):
        error_type = "timeout"

    # Check for DNS errors
    elif any(keyword in error_lower for keyword in ["dns", "hostname", "name resolution"]) or any(keyword in error_lower for keyword in ["connection", "refused", "reset"]) or any(keyword in error_lower for keyword in ["ssl", "tls", "certificate"]):
        error_type = "network"

    return error_type, error_message


def extract_response_mapping(
    response_body: dict[str, Any] | str | None,
    field_mappings: dict[str, str],
) -> dict[str, Any]:
    """Extract values from response using field mappings.

    Args:
        response_body: Parsed JSON response body.
        field_mappings: Mapping of target field to JSON path.

    Returns:
        Dictionary of extracted values.

    Example:
        response_body = {"user": {"id": 123, "email": "test@example.com"}}
        field_mappings = {"user_id": "user.id", "user_email": "user.email"}
        Result: {"user_id": 123, "user_email": "test@example.com"}
    """
    if not response_body or not field_mappings:
        return {}

    # Parse response body if string
    if isinstance(response_body, str):
        try:
            response_body = json.loads(response_body)
        except json.JSONDecodeError:
            return {}

    # Ensure response_body is a dict
    if not isinstance(response_body, dict):
        return {}

    extracted: dict[str, Any] = {}

    for target_field, json_path in field_mappings.items():
        value = _get_nested_value(response_body, json_path)
        if value is not None:
            extracted[target_field] = value

    return extracted
