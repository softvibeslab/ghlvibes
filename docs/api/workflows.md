# Workflows API Documentation

## Overview

The Workflows API provides comprehensive automation workflow management capabilities for the GoHighLevel Clone platform. This API enables users to create, manage, and execute automation workflows that respond to triggers and perform actions on contacts.

**Base URL:** `https://api.example.com/api/v1/workflows`

**Authentication:** All endpoints require a valid Clerk JWT token in the `Authorization` header.

**Rate Limiting:** 100 requests per hour per account.

---

## Table of Contents

- [Create Workflow](#create-workflow)
- [List Workflows](#list-workflows)
- [Get Workflow](#get-workflow)
- [Update Workflow](#update-workflow)
- [Delete Workflow](#delete-workflow)
- [Error Codes](#error-codes)
- [Data Models](#data-models)

---

## Endpoints

### Create Workflow

Create a new automation workflow in draft status.

```http
POST /api/v1/workflows
```

#### Request Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer token from Clerk authentication |
| `Content-Type` | string | Yes | Must be `application/json` |
| `X-Account-ID` | string | No | Override account ID (admin only) |

#### Request Body

```json
{
  "name": "Welcome Email Sequence",
  "description": "Send welcome emails to new contacts",
  "trigger_type": "contact_added",
  "trigger_config": {
    "source": "manual_import"
  }
}
```

**Field Validation:**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `name` | string | Yes | 3-100 characters, alphanumeric with hyphens/underscores only | Workflow display name (must be unique within account) |
| `description` | string | No | Maximum 1000 characters | Optional workflow description |
| `trigger_type` | string | No | Must match configured trigger types | Type of trigger (can be configured later) |
| `trigger_config` | object | No | Valid JSON object | Trigger-specific configuration |

#### Response: 201 Created

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "account_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Welcome Email Sequence",
  "description": "Send welcome emails to new contacts",
  "trigger_type": "contact_added",
  "trigger_config": {
    "source": "manual_import"
  },
  "status": "draft",
  "version": 1,
  "created_at": "2026-02-05T10:00:00Z",
  "updated_at": "2026-02-05T10:00:00Z",
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "updated_by": "550e8400-e29b-41d4-a716-446655440001",
  "actions": [],
  "stats": {
    "total_enrolled": 0,
    "currently_active": 0,
    "completed": 0
  }
}
```

#### Error Responses

| Status | Error Code | Description |
|--------|-----------|-------------|
| 400 | `VALIDATION_ERROR` | Invalid request body or field validation failed |
| 401 | `UNAUTHORIZED` | Missing or invalid authentication token |
| 403 | `FORBIDDEN` | User lacks `workflows:create` permission |
| 409 | `duplicate_workflow` | Workflow name already exists in this account |
| 429 | `RATE_LIMITED` | Exceeded rate limit (100 requests/hour) |
| 500 | `INTERNAL_ERROR` | Server error during workflow creation |

#### Example: cURL

```bash
curl -X POST https://api.example.com/api/v1/workflows \
  -H "Authorization: Bearer YOUR_CLERK_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Welcome Email Sequence",
    "description": "Send welcome emails to new contacts",
    "trigger_type": "contact_added"
  }'
```

#### Example: Python (requests)

```python
import requests

url = "https://api.example.com/api/v1/workflows"
headers = {
    "Authorization": f"Bearer {clerk_token}",
    "Content-Type": "application/json"
}
data = {
    "name": "Welcome Email Sequence",
    "description": "Send welcome emails to new contacts",
    "trigger_type": "contact_added"
}

response = requests.post(url, json=data, headers=headers)
workflow = response.json()
print(f"Created workflow: {workflow['id']}")
```

---

### List Workflows

List all workflows for the authenticated account with optional filtering and pagination.

```http
GET /api/v1/workflows
```

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `status` | string | No | All | Filter by status: `draft`, `active`, or `paused` |
| `offset` | integer | No | 0 | Pagination offset (minimum 0) |
| `limit` | integer | No | 50 | Maximum items per page (1-100) |

#### Response: 200 OK

```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Welcome Email Sequence",
      "status": "active",
      "created_at": "2026-02-05T10:00:00Z"
    }
  ],
  "total": 15,
  "offset": 0,
  "limit": 50,
  "has_more": false
}
```

#### Example: cURL

```bash
curl -X GET "https://api.example.com/api/v1/workflows?status=active&limit=10" \
  -H "Authorization: Bearer YOUR_CLERK_JWT_TOKEN"
```

---

### Get Workflow

Retrieve a single workflow by its ID.

```http
GET /api/v1/workflows/{workflow_id}
```

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | UUID | Yes | The workflow identifier |

#### Response: 200 OK

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "account_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Welcome Email Sequence",
  "description": "Send welcome emails to new contacts",
  "trigger_type": "contact_added",
  "trigger_config": {},
  "status": "draft",
  "version": 1,
  "created_at": "2026-02-05T10:00:00Z",
  "updated_at": "2026-02-05T10:00:00Z",
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "updated_by": "550e8400-e29b-41d4-a716-446655440001",
  "actions": [],
  "stats": {
    "total_enrolled": 0,
    "currently_active": 0,
    "completed": 0
  }
}
```

#### Error Responses

| Status | Error Code | Description |
|--------|-----------|-------------|
| 401 | `UNAUTHORIZED` | Missing or invalid authentication token |
| 403 | `FORBIDDEN` | User lacks access to this workflow |
| 404 | `workflow_not_found` | Workflow not found or access denied |

---

### Update Workflow

Update an existing workflow. Only provided fields will be updated (partial update).

```http
PATCH /api/v1/workflows/{workflow_id}
```

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | UUID | Yes | The workflow identifier |

#### Request Body

All fields are optional. Only include fields you want to update.

```json
{
  "name": "Updated Workflow Name",
  "description": "Updated description",
  "trigger_type": "webhook_received",
  "trigger_config": {
    "webhook_url": "https://example.com/webhook"
  }
}
```

#### Response: 200 OK

Returns the updated workflow object (same format as Create Workflow response).

#### Error Responses

| Status | Error Code | Description |
|--------|-----------|-------------|
| 400 | `VALIDATION_ERROR` | Invalid field values |
| 401 | `UNAUTHORIZED` | Missing or invalid authentication token |
| 403 | `FORBIDDEN` | User lacks `workflows:update` permission |
| 404 | `workflow_not_found` | Workflow not found |
| 409 | `duplicate_workflow` | New workflow name already exists |

---

### Delete Workflow

Soft delete a workflow. The workflow is marked as deleted but can be restored if needed.

```http
DELETE /api/v1/workflows/{workflow_id}
```

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | UUID | Yes | The workflow identifier |

#### Response: 204 No Content

Success response with no body.

#### Error Responses

| Status | Error Code | Description |
|--------|-----------|-------------|
| 401 | `UNAUTHORIZED` | Missing or invalid authentication token |
| 403 | `FORBIDDEN` | User lacks `workflows:delete` permission |
| 404 | `workflow_not_found` | Workflow not found |

---

## Error Codes

### Standard Error Format

All error responses follow this format:

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {}
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `UNAUTHORIZED` | 401 | Authentication failed or token missing |
| `FORBIDDEN` | 403 | User lacks required permission |
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `duplicate_workflow` | 409 | Workflow name already exists |
| `workflow_not_found` | 404 | Workflow not found or access denied |
| `domain_error` | 400 | Workflow domain logic error |
| `invalid_name` | 400 | Workflow name validation failed |
| `RATE_LIMITED` | 429 | Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

### Rate Limiting

All endpoints are rate limited to **100 requests per hour per account**.

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1677628800
```

When rate limit is exceeded:

```json
{
  "error": "RATE_LIMITED",
  "message": "Rate limit exceeded. Try again in 3600 seconds.",
  "details": {
    "retry_after": 3600
  }
}
```

---

## Data Models

### WorkflowStatus Enum

| Value | Description |
|-------|-------------|
| `draft` | Workflow is being configured, not active |
| `active` | Workflow is live and processing triggers |
| `paused` | Workflow is temporarily disabled |

### CreateWorkflowRequest

```typescript
interface CreateWorkflowRequest {
  name: string;              // Required: 3-100 chars
  description?: string;      // Optional: max 1000 chars
  trigger_type?: string;     // Optional: trigger type
  trigger_config?: object;   // Optional: trigger configuration
}
```

### WorkflowResponse

```typescript
interface WorkflowResponse {
  id: string;                // UUID v4
  account_id: string;        // UUID v4
  name: string;
  description: string;
  trigger_type: string | null;
  trigger_config: object;
  status: 'draft' | 'active' | 'paused';
  version: number;
  created_at: string;        // ISO 8601 timestamp
  updated_at: string;        // ISO 8601 timestamp
  created_by: string;        // UUID v4
  updated_by: string;        // UUID v4
  actions: Array<any>;       // Workflow actions
  stats: {
    total_enrolled: number;
    currently_active: number;
    completed: number;
  };
}
```

### ErrorResponse

```typescript
interface ErrorResponse {
  error: string;
  message: string;
  details?: Record<string, any>;
}
```

---

## Multi-Tenancy

All workflows are **account-scoped** with automatic tenant isolation:

- Workflows are automatically filtered by `account_id` from JWT token
- Users cannot access workflows from other accounts
- Row-level security enforced at database level
- Account ID is automatically set from authentication context

**Security Guarantee:** Users can only create, read, update, or delete workflows within their own account.

---

## Audit Logging

All workflow operations are automatically logged for compliance and debugging:

```json
{
  "id": "audit-log-uuid",
  "workflow_id": "workflow-uuid",
  "account_id": "account-uuid",
  "action": "workflow.created",
  "user_id": "user-uuid",
  "changes": {
    "name": "Welcome Email Sequence",
    "status": "draft"
  },
  "created_at": "2026-02-05T10:00:00Z"
}
```

Logged information includes:
- User who performed the action
- IP address and user agent
- Timestamp of action
- Workflow snapshot before/after changes

---

## Testing

For testing examples and integration test patterns, refer to:

- [Testing Guide](../development/testing.md)
- [Acceptance Tests](../../backend/tests/workflows/acceptance/README.md)
- [SPEC-WFL-001 Test Coverage](../../.moai/specs/SPEC-WFL-001/DDD_IMPLEMENTATION_REPORT.md)

---

## OpenAPI/Swagger

Interactive API documentation is available at:

- **Swagger UI:** `https://api.example.com/docs`
- **ReDoc:** `https://api.example.com/redoc`

OpenAPI specification can be downloaded from:

- **JSON:** `https://api.example.com/openapi.json`
- **YAML:** `https://api.example.com/openapi.yaml`

---

## Related Documentation

- [Development Guide](../development/testing.md)
- [SPEC-WFL-001](../../.moai/specs/SPEC-WFL-001/spec.md)
- [DDD Implementation Report](../../.moai/specs/SPEC-WFL-001/DDD_IMPLEMENTATION_REPORT.md)

---

## Support

For issues or questions regarding the Workflows API:

1. Check the [Error Codes](#error-codes) section
2. Review the [Testing Guide](../development/testing.md)
3. Consult the [SPEC documentation](../../.moai/specs/SPEC-WFL-001/spec.md)
4. Open an issue in the project repository

**API Version:** v1
**Last Updated:** 2026-02-05
**Implementation:** SPEC-WFL-001 (Workflow CRUD)
