# SPEC-FUN-005: Integrations - Third-Party Connections Backend

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-FUN-005 |
| **Title** | Integrations - Third-Party Connections Backend |
| **Module** | funnels-integrations |
| **Domain** | third-party-integrations |
| **Priority** | High |
| **Status** | Planned |
| **Created** | 2026-02-07 |
| **Version** | 1.0.0 |

---

## Overview

This specification defines the backend system for third-party integrations, including email marketing platforms, SMS services, webhook endpoints, and tracking pixels (Facebook Pixel, Google Analytics).

**Scope:** Complete backend API for managing external integrations with secure credential handling.

**Target Users:** Marketing teams connecting funnels to external tools.

---

## Environment

### Technical Environment

**Backend Framework:**
- FastAPI 0.115+ with Python 3.13+
- Async HTTP client for external API calls

**Security:**
- Encrypted credential storage (AES-256)
- OAuth 2.0 flows where applicable
- API key encryption at rest

**External Services:**
- Email: Mailchimp, SendGrid, ActiveCampaign, ConvertKit
- SMS: Twilio, Plivo, MessageBird
- Webhooks: Custom endpoints
- Tracking: Facebook Pixel, Google Analytics, TikTok Pixel

---

## Assumptions

**Assumption 1:** Encrypted storage available for API keys and credentials.

**Confidence Level:** High

**Evidence Basis:** Security best practice.

**Risk if Wrong:** Credentials exposed in database breach.

**Validation Method:** Verify encryption on startup.

**Assumption 2:** External APIs have rate limits we must respect.

**Confidence Level:** High

**Evidence Basis:** All major APIs rate-limited.

**Risk if Wrong:** API bans for excessive requests.

**Validation Method:** Implement rate limiting and retry logic.

**Assumption 3:** Webhook delivery requires retry mechanism for failures.

**Confidence Level:** High

**Evidence Basis:** Webhooks can fail temporarily.

**Risk if Wrong:** Data loss on webhook failures.

**Validation Method:** Exponential backoff retry queue.

---

## EARS Requirements

### REQ-FUN-005-01: Create Email Integration (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/integrations/email,
**THEN** the system shall create email service integration with encrypted credentials,
**RESULTING IN** 201 status with integration object,
**IN STATE** integration_created.

**Request Body:**
```json
{
  "provider": "mailchimp | sendgrid | activecampaign | convertkit | getresponse | aweber",
  "name": "string (3-100 chars)",
  "credentials": {
    "api_key": "string (encrypted at rest)",
    "api_url": "string (optional, for self-hosted)"
  },
  "settings": {
    "default_list_id": "string (optional)",
    "double_optin": "boolean (default: false)",
    "update_existing": "boolean (default: true)"
  },
  "mappings": [
    {
      "funnel_field": "string",
      "provider_field": "string"
    }
  ]
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "account_id": "uuid",
  "provider": "string",
  "name": "string",
  "status": "active | inactive | error",
  "settings": "object",
  "mappings": ["array"],
  "last_verified_at": "ISO8601 or null",
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

**Acceptance Criteria:**
- Credentials encrypted before storage
- API test call to verify credentials
- Returns 400 if validation fails
- Returns 401 if credentials invalid

### REQ-FUN-005-02: List Integrations (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/integrations,
**THEN** the system shall return list of integrations for the account,
**RESULTING IN** 200 status with integrations array,
**IN STATE** retrieved.

**Query Parameters:**
- provider: string (optional)
- status: string (optional)
- type: string (optional: email, sms, webhook, tracking)

**Response 200:**
```json
{
  "items": ["array of integration objects (without credentials)"],
  "total": "integer"
}
```

**Acceptance Criteria:**
- Credentials never returned in list
- Only integrations for account_id from JWT
- Status reflects health check results

### REQ-FUN-005-03: Get Integration Detail (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/integrations/{id},
**THEN** the system shall return integration details (without full credentials),
**RESULTING IN** 200 status with integration object,
**IN STATE** retrieved.

**Response 200:**
Includes all fields except sensitive credentials (masked):
```json
{
  "credentials": {
    "api_key": "********",
    "api_url": "string (shown)"
  },
  "health_status": {
    "status": "healthy | degraded | error",
    "last_check_at": "ISO8601",
    "error_message": "string or null"
  }
}
```

**Acceptance Criteria:**
- Sensitive data masked
- Includes recent health check results
- Returns 404 if not found
- Returns 403 if different account

### REQ-FUN-005-04: Update Integration (Event-Driven)

**WHEN** a user submits a PATCH request to /api/v1/integrations/{id},
**THEN** the system shall update integration fields,
**RESULTING IN** 200 status with updated object,
**IN STATE** updated.

**Request Body (partial):**
```json
{
  "name": "string",
  "credentials": "object",
  "settings": "object",
  "mappings": "array",
  "status": "active | inactive"
}
```

**Acceptance Criteria:**
- Credentials re-encrypted if updated
- Verification call if credentials changed
- Returns 404 if not found
- Returns 403 if different account

### REQ-FUN-005-05: Delete Integration (Event-Driven)

**WHEN** a user submits a DELETE request to /api/v1/integrations/{id},
**THEN** the system shall delete the integration,
**RESULTING IN** 204 status with no body,
**IN STATE** deleted.

**Acceptance Criteria:**
- Hard delete from database
- Associated webhooks disabled
- Returns 404 if not found
- Returns 403 if different account

### REQ-FUN-005-06: Test Integration Connection (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/integrations/{id}/test,
**THEN** the system shall test connection to external service,
**RESULTING IN** 200 status with test results,
**IN STATE** tested.

**Response 200:**
```json
{
  "success": "boolean",
  "response_time_ms": "integer",
  "message": "string",
  "tested_at": "ISO8601",
  "details": {
    "api_version": "string or null",
    "account_name": "string or null",
    "quota_remaining": "integer or null"
  }
}
```

**Acceptance Criteria:**
- Makes actual API call to provider
- Records health status
- Returns 404 if integration not found
- Returns 503 if provider unreachable

### REQ-FUN-005-07: Create SMS Integration (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/integrations/sms,
**THEN** the system shall create SMS service integration,
**RESULTING IN** 201 status with integration object,
**IN STATE** integration_created.

**Request Body:**
```json
{
  "provider": "twilio | plivo | messagebird | bandwidth | telnyx",
  "name": "string",
  "credentials": {
    "account_sid": "string",
    "auth_token": "string (encrypted)",
    "api_key": "string (encrypted, alternative)"
  },
  "settings": {
    "from_number": "string (phone number)",
    "default_country_code": "string (default: +1)"
  }
}
```

**Acceptance Criteria:**
- Phone number validated
- Test SMS sent (configurable)
- Returns 400 if phone number invalid

### REQ-FUN-005-08: Create Webhook Integration (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/integrations/webhooks,
**THEN** the system shall create webhook endpoint for external events,
**RESULTING IN** 201 status with webhook object,
**IN STATE** webhook_created.

**Request Body:**
```json
{
  "name": "string (3-100 chars)",
  "description": "string (optional)",
  "events": ["array of event types to subscribe to"],
  "url": "string (https endpoint)",
  "method": "POST (default) | PUT",
  "headers": [
    {
      "name": "string",
      "value": "string"
    }
  ],
  "retry_config": {
    "enabled": "boolean (default: true)",
    "max_retries": "integer (default: 3)",
    "retry_after_seconds": "integer (default: 60)"
  },
  "secret": "string (optional, for signature verification)"
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "account_id": "uuid",
  "name": "string",
  "description": "string",
  "events": ["array"],
  "url": "string",
  "method": "string",
  "headers": ["array"],
  "retry_config": "object",
  "status": "active | inactive",
  "last_triggered_at": "ISO8601 or null",
  "trigger_count": "integer",
  "failure_count": "integer",
  "created_at": "ISO8601"
}
```

**Acceptance Criteria:**
- URL validated (HTTPS required)
- Event types validated against available events
- Returns 400 if URL invalid

### REQ-FUN-005-09: Trigger Webhook (Event-Driven)

**WHEN** a funnel event occurs and matching webhooks exist,
**THEN** the system shall deliver webhook payload to registered endpoints,
**RESULTING IN** async delivery with retries,
**IN STATE** webhook_delivered.

**Webhook Payload Format:**
```json
{
  "event_id": "uuid",
  "event_type": "string",
  "timestamp": "ISO8601",
  "account_id": "uuid",
  "funnel_id": "uuid",
  "data": "object (event-specific data)",
  "signature": "string (HMAC if secret provided)"
}
```

**Acceptance Criteria:**
- Delivered asynchronously via queue
- Retry on failure with exponential backoff
- Signature calculated if webhook has secret
- Max 3 retries by default
- Webhook marked as failed after max retries

### REQ-FUN-005-10: List Webhook Deliveries (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/integrations/webhooks/{id}/deliveries,
**THEN** the system shall return delivery history for webhook,
**RESULTING IN** 200 status with deliveries array,
**IN STATE** retrieved.

**Query Parameters:**
- status: string (optional: success, failed, pending)
- date_from, date_to
- page, page_size

**Response 200:**
```json
{
  "items": [
    {
      "id": "uuid",
      "webhook_id": "uuid",
      "event_type": "string",
      "payload": "object",
      "response_status": "integer",
      "response_body": "string",
      "attempt_number": "integer",
      "delivered_at": "ISO8601 or null",
      "failed_at": "ISO8601 or null",
      "error_message": "string or null"
    }
  ],
  "total": "integer",
  "page": "integer",
  "page_size": "integer"
}
```

**Acceptance Criteria:**
- Most recent first
- Pagination for large datasets

### REQ-FUN-005-11: Create Tracking Pixel Integration (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/integrations/tracking,
**THEN** the system shall create tracking pixel integration,
**RESULTING IN** 201 status with integration object,
**IN STATE** integration_created.

**Request Body:**
```json
{
  "provider": "facebook | google_analytics | tiktok | pinterest | twitter",
  "name": "string",
  "credentials": {
    "pixel_id": "string",
    "access_token": "string (encrypted)",
    "tracking_id": "string (for GA)",
    "measurement_id": "string (for GA4)"
  },
  "settings": {
    "track_page_views": "boolean (default: true)",
    "track_conversions": "boolean (default: true)",
    "enhanced_conversions": "boolean (default: false)"
  }
}
```

**Acceptance Criteria:**
- Pixel ID validated
- Returns 400 if credentials invalid

### REQ-FUN-005-12: Get Tracking Pixel Code (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/integrations/tracking/{id}/code,
**THEN** the system shall return embed code for tracking pixel,
**RESULTING IN** 200 status with code snippets,
**IN STATE** code_retrieved.

**Response 200:**
```json
{
  "integration_id": "uuid",
  "provider": "string",
  "pixel_id": "string",
  "head_code": "string (HTML for <head>)",
  "body_code": "string (HTML for <body>, optional)",
  "noscript_code": "string (noscript fallback, optional)",
  "verification_url": "string (for verification)"
}
```

**Acceptance Criteria:**
- Returns provider-specific code
- Includes placeholder variables for dynamic values
- Returns 404 if integration not found

### REQ-FUN-005-13: Sync Contact to Email List (Event-Driven)

**WHEN** a contact event occurs (form submit, etc.),
**THEN** the system shall sync contact to configured email lists,
**RESULTING IN** async sync with status tracking,
**IN STATE** contact_synced.

**Sync Logic:**
- Map funnel fields to provider fields
- Apply double optin setting
- Update existing contacts if enabled
- Handle merge fields

**Acceptance Criteria:**
- Async processing via queue
- Retry on temporary failures
- Status logged for audit
- Respects rate limits

### REQ-FUN-005-14: Send SMS via Integration (Event-Driven)

**WHEN** a funnel action sends SMS,
**THEN** the system shall deliver via configured SMS integration,
**RESULTING IN** message sent with delivery tracking,
**IN STATE** sms_sent.

**Request Payload:**
```json
{
  "integration_id": "uuid",
  "to": "string (phone number)",
  "message": "string",
  "media_urls": ["array of image URLs (optional, for MMS)"]
}
```

**Acceptance Criteria:**
- Phone number normalized to E.164
- Message length validated
- Delivery receipt webhook registered
- Returns 400 if rate limit exceeded

### REQ-FUN-005-15: Get Integration Usage Stats (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/integrations/{id}/stats,
**THEN** the system shall return usage statistics for integration,
**RESULTING IN** 200 status with stats object,
**IN STATE** stats_retrieved.

**Query Parameters:**
- date_from: ISO8601 (required)
- date_to: ISO8601 (required)

**Response 200:**
```json
{
  "integration_id": "uuid",
  "provider": "string",
  "period": {"start": "ISO8601", "end": "ISO8601"},
  "usage": {
    "total_requests": "integer",
    "successful_requests": "integer",
    "failed_requests": "integer",
    "success_rate": "decimal",
    "avg_response_time_ms": "integer"
  },
  "quota": {
    "limit": "integer or null",
    "remaining": "integer or null",
    "reset_at": "ISO8601 or null"
  },
  "breakdown_by_day": [
    {
      "date": "ISO8601",
      "requests": "integer",
      "successes": "integer",
      "failures": "integer"
    }
  ]
}
```

**Acceptance Criteria:**
- Date range max 90 days
- Cached for 5 minutes
- Returns 404 if integration not found

### REQ-FUN-005-16: Redeliver Webhook (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/integrations/webhooks/deliveries/{delivery_id}/redeliver,
**THEN** the system shall redeliver failed webhook,
**RESULTING IN** 202 status (queued for redelivery),
**IN STATE** webhook_redelivered.

**Acceptance Criteria:**
- Original payload reused
- New delivery record created
- Does not retry immediately (uses queue)
- Returns 404 if delivery not found
- Returns 400 if delivery succeeded (cannot redeliver success)

---

## Technical Specifications

### Database Schema

```sql
-- Integrations table
CREATE TABLE integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id),
    provider VARCHAR(50) NOT NULL,
    integration_type VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    credentials ENCRYPTED TEXT NOT NULL,
    settings JSONB NOT NULL DEFAULT '{}',
    mappings JSONB NOT NULL DEFAULT '[]',
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    last_verified_at TIMESTAMPTZ,
    health_status VARCHAR(20) NOT NULL DEFAULT 'unknown',
    last_health_check_at TIMESTAMPTZ,
    health_error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_integrations_account_id ON integrations(account_id);
CREATE INDEX idx_integrations_provider ON integrations(provider);
CREATE INDEX idx_integrations_type ON integrations(integration_type);
CREATE INDEX idx_integrations_status ON integrations(status);

-- Webhooks table
CREATE TABLE webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    events TEXT[] NOT NULL,
    url VARCHAR(500) NOT NULL,
    method VARCHAR(10) NOT NULL DEFAULT 'POST',
    headers JSONB NOT NULL DEFAULT '[]',
    retry_config JSONB NOT NULL DEFAULT '{"enabled": true, "max_retries": 3, "retry_after_seconds": 60}',
    secret VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    last_triggered_at TIMESTAMPTZ,
    trigger_count INTEGER NOT NULL DEFAULT 0,
    failure_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_webhooks_account_id ON webhooks(account_id);
CREATE INDEX idx_webhooks_status ON webhooks(status);

-- Webhook deliveries table
CREATE TABLE webhook_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_id UUID NOT NULL REFERENCES webhooks(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    response_status INTEGER,
    response_body TEXT,
    attempt_number INTEGER NOT NULL DEFAULT 1,
    delivered_at TIMESTAMPTZ,
    failed_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_webhook_deliveries_webhook_id ON webhook_deliveries(webhook_id);
CREATE INDEX idx_webhook_deliveries_created_at ON webhook_deliveries(created_at);

-- Integration sync logs table
CREATE TABLE integration_sync_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    integration_id UUID NOT NULL REFERENCES integrations(id) ON DELETE CASCADE,
    sync_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL,
    request_payload JSONB,
    response_payload JSONB,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_integration_sync_logs_integration_id ON integration_sync_logs(integration_id);
CREATE INDEX idx_integration_sync_logs_created_at ON integration_sync_logs(created_at);
```

### Supported Providers

**Email Marketing:**
- Mailchimp
- SendGrid
- ActiveCampaign
- ConvertKit
- GetResponse
- AWeber

**SMS:**
- Twilio
- Plivo
- MessageBird
- Bandwidth
- Telnyx

**Tracking Pixels:**
- Facebook Pixel
- Google Analytics (UA & GA4)
- TikTok Pixel
- Pinterest Tag
- Twitter Pixel

### API Endpoints Summary

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/integrations/email | Create email integration |
| GET | /api/v1/integrations | List integrations |
| GET | /api/v1/integrations/{id} | Get integration detail |
| PATCH | /api/v1/integrations/{id} | Update integration |
| DELETE | /api/v1/integrations/{id} | Delete integration |
| POST | /api/v1/integrations/{id}/test | Test connection |
| POST | /api/v1/integrations/sms | Create SMS integration |
| POST | /api/v1/integrations/webhooks | Create webhook |
| POST | /api/v1/integrations/webhooks/deliveries/{id}/redeliver | Redeliver webhook |
| GET | /api/v1/integrations/webhooks/{id}/deliveries | List deliveries |
| POST | /api/v1/integrations/tracking | Create tracking pixel |
| GET | /api/v1/integrations/tracking/{id}/code | Get pixel code |
| GET | /api/v1/integrations/{id}/stats | Get usage stats |

**Total Endpoints: 14**

---

## Constraints

### Technical Constraints

- Credentials encrypted with AES-256
- Webhook URLs must be HTTPS
- Webhook timeout: 30 seconds
- Rate limiting per provider

### Business Constraints

- Maximum 50 integrations per account
- Maximum 20 webhooks per account
- Webhook retry: max 3 attempts
- Sync log retention: 90 days

### Security Constraints

- Credentials never logged
- Credentials never returned in API responses
- Webhook secrets hashed before storage
- API key rotation recommended every 90 days

---

## Dependencies

### Internal Dependencies

| Module | Dependency Type | Description |
|--------|-----------------|-------------|
| Funnels Module | Soft | Funnel events trigger integrations |
| Contacts Module | Hard | Contact sync requires contacts |
| Accounts Module | Hard | Multi-tenancy |

### External Dependencies

| Service | Purpose |
|---------|---------|
| Redis Queue | Async webhook delivery |
| Encryption Service | Credential encryption |

---

## Related SPECs

| SPEC ID | Title | Relationship |
|---------|-------|--------------|
| SPEC-FUN-001 | Funnel Builder | Integrations connect to funnels |
| SPEC-FUN-002 | Pages & Elements | Tracking pixels on pages |
| SPEC-FUN-003 | Orders & Payments | Post-purchase integrations |

---

## Traceability Tags

- TAG:SPEC-FUN-005
- TAG:MODULE-FUNNELS-INTEGRATIONS
- TAG:DOMAIN-THIRD-PARTY-INTEGRATIONS
- TAG:PRIORITY-HIGH
- TAG:API-REST
- TAG:WEBHOOKS
- TAG:ENCRYPTION
- TAG:DDD-IMPLEMENTATION
