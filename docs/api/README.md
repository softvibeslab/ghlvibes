# API Documentation

Complete API reference for the GoHighLevel Clone platform.

## Base URL

```
Production: https://api.gohighlevel-clone.com
Staging: https://api-staging.gohighlevel-clone.com
Development: http://localhost:8000
```

## Authentication

All API requests require authentication using JWT bearer tokens.

### Headers

```http
Authorization: Bearer <token>
Content-Type: application/json
```

### Authentication Flow

1. **Login**: Send credentials to `/api/v1/auth/login`
2. **Receive Token**: Get access token (15min expiry) and refresh token (7 days)
3. **Use Token**: Include access token in Authorization header
4. **Refresh**: Use refresh token to get new access token before expiry

### Example

```bash
# Login
curl -X POST https://api.example.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "expires_in": 900
}

# Use access token
curl https://api.example.com/api/v1/workflows \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."

# Refresh token
curl -X POST https://api.example.com/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."}'
```

## API Modules

- **[Workflows API](./workflows.md)** - Automation workflow management
- **Actions API](./actions.md) - Workflow action steps
- **Triggers API](./triggers.md) - Workflow triggers
- **Conditions API](./conditions.md) - Workflow condition logic
- **Contacts API](./contacts.md) - Contact management
- **Campaigns API](./campaigns.md) - Marketing campaigns
- **Pipelines API](./pipelines.md) - Sales pipelines
- **Analytics API](./analytics.md) - Reporting and insights
- **Webhooks API](./webhooks.md) - Webhook management
- **Templates API](./templates.md) - Workflow templates
- **Bulk Enrollment API](./bulk-enrollment.md) - Bulk operations

## Rate Limiting

API requests are rate limited per account to ensure fair usage.

### Limits

| Plan | Requests | Time Window |
|------|----------|-------------|
| Free | 100 | 1 hour |
| Starter | 1,000 | 1 hour |
| Professional | 10,000 | 1 hour |
| Enterprise | Unlimited | - |

### Rate Limit Headers

Every API response includes rate limit headers:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1704067200
```

### Error Response

When rate limit is exceeded:

```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Please try again later.",
  "details": {
    "limit": 1000,
    "remaining": 0,
    "reset_at": "2024-01-01T00:00:00Z"
  }
}
```

HTTP Status Code: `429 Too Many Requests`

## Response Format

All API responses follow a consistent format.

### Success Response

```json
{
  "data": { /* response data */ },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### Paginated Response

```json
{
  "data": [ /* array of items */ ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 150,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### Error Response

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": { /* additional error context */ },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## HTTP Status Codes

| Code | Description |
|------|-------------|
| `200 OK` | Request succeeded |
| `201 Created` | Resource created successfully |
| `204 No Content` | Request succeeded, no response body |
| `400 Bad Request` | Invalid request data |
| `401 Unauthorized` | Authentication required |
| `403 Forbidden` | Insufficient permissions |
| `404 Not Found` | Resource not found |
| `409 Conflict` | Resource conflict (duplicate, invalid state) |
| `422 Unprocessable Entity` | Validation error |
| `429 Too Many Requests` | Rate limit exceeded |
| `500 Internal Server Error` | Server error |
| `503 Service Unavailable` | Service temporarily unavailable |

## Common Error Codes

| Error Code | Description |
|------------|-------------|
| `authentication_required` | No valid authentication token provided |
| `invalid_token` | Authentication token is invalid or expired |
| `insufficient_permissions` | User lacks required permissions |
| `validation_error` | Request validation failed |
| `resource_not_found` | Requested resource does not exist |
| `duplicate_resource` | Resource with given identifier already exists |
| `invalid_state_transition` | Invalid state transition requested |
| `rate_limit_exceeded` | Rate limit exceeded |
| `domain_error` | Business logic violation |

## Request ID

Every API request is assigned a unique request ID for tracking and debugging.

```http
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
```

Include this ID in support requests for faster resolution.

## Versioning

The API is versioned using URL path versioning: `/api/v1/`, `/api/v2/`, etc.

Major versions may introduce breaking changes. Minor versions are backward compatible.

Current version: **v1**

## SDKs and Libraries

Official SDKs are available for popular languages:

- **Python**: `pip install gohighlevel-python`
- **JavaScript/TypeScript**: `npm install @gohighlevel/js-sdk`
- **Go**: `go get github.com/gohighlevel/go-sdk`

See [SDK Documentation](./sdk/) for detailed usage guides.

## Webhooks

Webhooks enable real-time notifications for events in your account.

See [Webhooks API](./webhooks.md) for configuration and event reference.

## OpenAPI/Swagger

Interactive API documentation is available at:

```
https://api.gohighlevel-clone.com/docs (Swagger UI)
https://api.gohighlevel-clone.com/redoc (ReDoc)
```

Download OpenAPI specification:

```
https://api.gohighlevel-clone.com/openapi.json
```

## Support

- **Documentation**: [https://docs.gohighlevel-clone.com](https://docs.gohighlevel-clone.com)
- **API Status**: [https://status.gohighlevel-clone.com](https://status.gohighlevel-clone.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/gohighlevel-clone/issues)
- **Email**: api-support@gohighlevel-clone.com

## Changelog

See [CHANGELOG.md](../../CHANGELOG.md) for API version history and changes.
