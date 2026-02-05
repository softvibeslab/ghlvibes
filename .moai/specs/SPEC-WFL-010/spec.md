# SPEC-WFL-010: Webhook Integration

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-010 |
| **Title** | Webhook Integration |
| **Module** | workflows |
| **Domain** | automation |
| **Priority** | High |
| **Status** | Planned |
| **Created** | 2026-01-26 |
| **Version** | 1.0.0 |

---

## Overview

This specification defines the webhook integration feature for the GoHighLevel Clone workflow automation system. The feature enables workflows to call external HTTP endpoints, handle responses, and integrate with third-party services through configurable webhook actions.

---

## EARS Requirements

### REQ-001: Webhook Action Execution (Event-Driven)

**WHEN** a workflow execution reaches a webhook action step
**THEN** the system shall send an HTTP request to the configured endpoint with the specified payload
**RESULTING IN** the external system receiving the webhook payload and the response being captured
**STATE** executed

### REQ-002: HTTP Method Support (Ubiquitous)

The system **shall** support the following HTTP methods for webhook calls:
- GET - for retrieving data from external systems
- POST - for sending data to external systems
- PUT - for updating resources in external systems
- PATCH - for partial updates to external resources
- DELETE - for removing resources in external systems

### REQ-003: Custom Headers Configuration (Event-Driven)

**WHEN** configuring a webhook action
**THEN** the system shall allow users to define custom HTTP headers as key-value pairs
**RESULTING IN** the webhook request including all configured headers
**STATE** configured

### REQ-004: JSON Payload Construction (Event-Driven)

**WHEN** a webhook action is configured with payload data
**THEN** the system shall construct a valid JSON payload using contact merge fields and static values
**RESULTING IN** a properly formatted JSON body sent with the request
**STATE** serialized

### REQ-005: Authentication Support (State-Driven)

**WHILE** authentication is configured for a webhook
**THEN** the system shall apply the appropriate authentication method:
- **None**: No authentication headers added
- **Basic**: Base64-encoded username:password in Authorization header
- **Bearer**: JWT or API token in Authorization header with "Bearer" prefix
- **API Key**: Custom header with API key value

**RESULTING IN** authenticated requests to secured endpoints
**STATE** authenticated

### REQ-006: Request Timeout Handling (Event-Driven)

**WHEN** a webhook request exceeds the configured timeout (default: 30 seconds)
**THEN** the system shall abort the request and mark the execution as timed out
**RESULTING IN** a timeout error logged with execution metadata
**STATE** timeout_error

### REQ-007: Retry Mechanism (Event-Driven)

**WHEN** a webhook call fails due to network error or 5xx server response
**THEN** the system shall retry the request with exponential backoff:
- Retry 1: Wait 5 seconds
- Retry 2: Wait 15 seconds
- Retry 3: Wait 45 seconds (final attempt)

**RESULTING IN** resilient webhook execution with automatic recovery
**STATE** retrying

### REQ-008: Response Logging (Event-Driven)

**WHEN** a webhook response is received (success or failure)
**THEN** the system shall log:
- HTTP status code
- Response headers
- Response body (truncated if > 10KB)
- Request duration in milliseconds
- Timestamp

**RESULTING IN** complete audit trail for webhook executions
**STATE** logged

### REQ-009: Response Data Mapping (Event-Driven)

**WHEN** a successful webhook response is received
**THEN** the system shall optionally extract JSON values from the response
**AND** store them in contact custom fields or workflow variables
**RESULTING IN** external data integrated into the workflow context
**STATE** mapped

### REQ-010: Error Classification (Event-Driven)

**WHEN** a webhook call fails
**THEN** the system shall classify the error:
- **Network Error**: Connection refused, DNS failure, SSL error
- **Timeout Error**: Request exceeded timeout limit
- **Client Error (4xx)**: Bad request, unauthorized, not found
- **Server Error (5xx)**: Internal server error, bad gateway

**RESULTING IN** actionable error information for debugging
**STATE** error_classified

### REQ-011: SSL/TLS Verification (Ubiquitous)

The system **shall** verify SSL/TLS certificates for HTTPS endpoints by default.
The system **shall** allow disabling SSL verification for development/testing purposes only (with security warning).

### REQ-012: Request Size Limits (Unwanted Behavior)

The system **shall NOT** send webhook payloads exceeding 1MB in size.
**IF** a payload exceeds the limit
**THEN** the system shall reject the configuration with a validation error.

### REQ-013: Webhook URL Validation (Event-Driven)

**WHEN** configuring a webhook URL
**THEN** the system shall validate:
- URL format is valid (RFC 3986 compliant)
- Protocol is HTTP or HTTPS
- Domain is resolvable
- URL does not target internal/private IP ranges

**RESULTING IN** only valid external URLs accepted
**STATE** validated

### REQ-014: Merge Field Interpolation (Event-Driven)

**WHEN** constructing webhook URL, headers, or payload
**THEN** the system shall interpolate merge fields using double curly brace syntax:
- `{{contact.first_name}}` - Contact fields
- `{{contact.email}}` - Contact email
- `{{contact.custom_fields.field_name}}` - Custom fields
- `{{workflow.name}}` - Workflow metadata
- `{{execution.id}}` - Execution tracking

**RESULTING IN** dynamic, contact-specific webhook requests
**STATE** interpolated

### REQ-015: Concurrent Execution Limits (State-Driven)

**WHILE** webhook actions are executing
**THEN** the system shall limit concurrent outbound requests to prevent resource exhaustion:
- Per-account limit: 100 concurrent requests
- Per-endpoint limit: 10 concurrent requests
- Global limit: 1000 concurrent requests

**RESULTING IN** stable system performance under load
**STATE** rate_limited

---

## Technical Specifications

### HTTP Client Architecture

```
+-------------------+     +------------------+     +------------------+
| Workflow Engine   |---->| Webhook Service  |---->| HTTP Client Pool |
+-------------------+     +------------------+     +------------------+
                                  |                        |
                                  v                        v
                          +---------------+        +---------------+
                          | Retry Handler |        | Circuit Breaker|
                          +---------------+        +---------------+
                                  |                        |
                                  v                        v
                          +---------------+        +---------------+
                          | Response Logger|       | External API  |
                          +---------------+        +---------------+
```

### Database Schema

```sql
-- Webhook configurations stored with workflow actions
CREATE TABLE webhook_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action_id UUID NOT NULL REFERENCES workflow_actions(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    method VARCHAR(10) NOT NULL DEFAULT 'POST',
    headers JSONB DEFAULT '{}',
    payload_template JSONB,
    auth_type VARCHAR(20) DEFAULT 'none',
    auth_credentials JSONB,  -- Encrypted
    timeout_seconds INTEGER DEFAULT 30,
    retry_enabled BOOLEAN DEFAULT true,
    retry_max_attempts INTEGER DEFAULT 3,
    ssl_verify BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Webhook execution logs
CREATE TABLE webhook_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID NOT NULL REFERENCES workflow_executions(id),
    webhook_config_id UUID NOT NULL REFERENCES webhook_configs(id),
    request_url TEXT NOT NULL,
    request_method VARCHAR(10) NOT NULL,
    request_headers JSONB,
    request_body JSONB,
    response_status INTEGER,
    response_headers JSONB,
    response_body TEXT,  -- Truncated if large
    duration_ms INTEGER,
    attempt_number INTEGER DEFAULT 1,
    status VARCHAR(20) NOT NULL,  -- success, error, timeout, retrying
    error_message TEXT,
    error_type VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_webhook_executions_execution_id ON webhook_executions(execution_id);
CREATE INDEX idx_webhook_executions_status ON webhook_executions(status);
CREATE INDEX idx_webhook_executions_created_at ON webhook_executions(created_at);
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/workflows/{id}/actions/webhook` | Create webhook action |
| GET | `/api/v1/workflows/{id}/actions/{action_id}/webhook` | Get webhook config |
| PUT | `/api/v1/workflows/{id}/actions/{action_id}/webhook` | Update webhook config |
| DELETE | `/api/v1/workflows/{id}/actions/{action_id}/webhook` | Delete webhook action |
| POST | `/api/v1/webhooks/test` | Test webhook configuration |
| GET | `/api/v1/webhook-executions` | List webhook execution logs |
| GET | `/api/v1/webhook-executions/{id}` | Get execution details |

### Request/Response Models

```python
# Webhook Configuration Request
class WebhookConfigCreate(BaseModel):
    url: str  # Max 2048 chars
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] = "POST"
    headers: dict[str, str] = {}
    payload_template: dict | None = None
    auth_type: Literal["none", "basic", "bearer", "api_key"] = "none"
    auth_config: AuthConfig | None = None
    timeout_seconds: int = Field(default=30, ge=1, le=120)
    retry_enabled: bool = True
    retry_max_attempts: int = Field(default=3, ge=1, le=5)
    ssl_verify: bool = True

# Authentication Configuration
class AuthConfig(BaseModel):
    # For basic auth
    username: str | None = None
    password: SecretStr | None = None
    # For bearer auth
    token: SecretStr | None = None
    # For API key auth
    header_name: str | None = None
    api_key: SecretStr | None = None

# Webhook Execution Response
class WebhookExecutionResponse(BaseModel):
    id: UUID
    execution_id: UUID
    status: str
    response_status: int | None
    duration_ms: int | None
    error_message: str | None
    created_at: datetime
```

### Error Handling Strategy

| Error Type | HTTP Status | Retry | User Message |
|------------|-------------|-------|--------------|
| Network Error | - | Yes | "Unable to connect to webhook endpoint" |
| DNS Resolution | - | Yes | "Could not resolve webhook domain" |
| SSL Certificate | - | No | "SSL certificate validation failed" |
| Timeout | - | Yes | "Webhook request timed out" |
| 400 Bad Request | 400 | No | "Invalid request to webhook endpoint" |
| 401 Unauthorized | 401 | No | "Webhook authentication failed" |
| 403 Forbidden | 403 | No | "Access denied to webhook endpoint" |
| 404 Not Found | 404 | No | "Webhook endpoint not found" |
| 429 Rate Limited | 429 | Yes | "Webhook endpoint rate limit exceeded" |
| 500 Server Error | 5xx | Yes | "Webhook endpoint server error" |

---

## Security Considerations

### Credential Storage
- All authentication credentials encrypted at rest using AES-256
- Credentials never logged in plaintext
- Separate encryption key per account

### Request Validation
- Block requests to private IP ranges (10.x, 172.16-31.x, 192.168.x)
- Block requests to localhost and internal hostnames
- Validate URL schemes (HTTP/HTTPS only)
- Sanitize user inputs in merge fields

### Rate Limiting
- Per-account webhook rate limits
- Circuit breaker for failing endpoints
- Queue-based execution to prevent thundering herd

---

## Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| Webhook execution start | < 100ms | From action trigger to request sent |
| Response processing | < 50ms | From response received to logged |
| Concurrent requests | 100/account | Maximum simultaneous webhook calls |
| Retry queue processing | < 1 minute | Time between retry attempts start |
| Log retention | 30 days | Webhook execution history |

---

## Dependencies

### Internal Dependencies
- Workflow Engine (SPEC-WFL-005)
- Action Step System (SPEC-WFL-003)
- Contact Merge Fields System
- Encryption Service

### External Dependencies
- PostgreSQL/Supabase (database)
- Redis (rate limiting, circuit breaker state)
- httpx/aiohttp (async HTTP client)

---

## Traceability

| Tag | Reference |
|-----|-----------|
| SPEC-WFL-010 | This specification |
| SPEC-WFL-003 | Add Action Step (parent) |
| SPEC-WFL-005 | Execute Workflow (integration) |
| SPEC-INT-007 | Zapier/Webhook Integration (related) |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-26 | manager-spec | Initial specification |
