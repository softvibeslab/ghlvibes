# SPEC-WFL-010: Acceptance Criteria

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-010 |
| **Title** | Webhook Integration |
| **Module** | workflows |
| **Domain** | automation |
| **Priority** | High |

---

## Test Scenarios

### Feature: Webhook Action Execution

#### Scenario: AC-001 - Successful POST Webhook Call

```gherkin
Given a workflow with a webhook action configured
  And the webhook URL is "https://api.example.com/webhook"
  And the method is "POST"
  And the payload template is {"contact_email": "{{contact.email}}", "event": "workflow_triggered"}
  And the contact email is "john@example.com"
When the workflow execution reaches the webhook action
Then the system shall send a POST request to "https://api.example.com/webhook"
  And the request body shall be {"contact_email": "john@example.com", "event": "workflow_triggered"}
  And the Content-Type header shall be "application/json"
  And the webhook execution shall be logged with status "success"
```

#### Scenario: AC-002 - GET Request with Query Parameters

```gherkin
Given a webhook action with method "GET"
  And the URL is "https://api.example.com/lookup?email={{contact.email}}"
  And the contact email is "jane@example.com"
When the webhook action executes
Then the system shall send a GET request to "https://api.example.com/lookup?email=jane%40example.com"
  And no request body shall be sent
  And the response shall be captured and logged
```

#### Scenario: AC-003 - Custom Headers Included

```gherkin
Given a webhook action with custom headers
  And the headers include "X-Custom-Header: my-value"
  And the headers include "X-Account-ID: {{account.id}}"
  And the account ID is "acc_123456"
When the webhook action executes
Then the request shall include header "X-Custom-Header" with value "my-value"
  And the request shall include header "X-Account-ID" with value "acc_123456"
```

---

### Feature: Authentication Handling

#### Scenario: AC-004 - Basic Authentication

```gherkin
Given a webhook action with auth_type "basic"
  And the username is "apiuser"
  And the password is "secret123"
When the webhook action executes
Then the request shall include an Authorization header
  And the Authorization header shall be "Basic YXBpdXNlcjpzZWNyZXQxMjM="
  And the credentials shall not appear in execution logs
```

#### Scenario: AC-005 - Bearer Token Authentication

```gherkin
Given a webhook action with auth_type "bearer"
  And the token is "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
When the webhook action executes
Then the request shall include an Authorization header
  And the Authorization header shall start with "Bearer "
  And the token shall be appended to the header value
```

#### Scenario: AC-006 - API Key Authentication

```gherkin
Given a webhook action with auth_type "api_key"
  And the header name is "X-API-Key"
  And the API key is "ak_live_abc123def456"
When the webhook action executes
Then the request shall include header "X-API-Key"
  And the header value shall be "ak_live_abc123def456"
```

#### Scenario: AC-007 - No Authentication

```gherkin
Given a webhook action with auth_type "none"
When the webhook action executes
Then the request shall not include an Authorization header
  And the request shall only include configured custom headers
```

---

### Feature: Timeout Handling

#### Scenario: AC-008 - Request Timeout

```gherkin
Given a webhook action with timeout_seconds set to 30
  And the external endpoint does not respond within 30 seconds
When the webhook action executes
Then the system shall abort the request after 30 seconds
  And the execution shall be logged with status "timeout"
  And the error_type shall be "timeout_error"
  And the workflow shall proceed to error handling
```

#### Scenario: AC-009 - Custom Timeout Configuration

```gherkin
Given a webhook action with timeout_seconds set to 10
  And the endpoint responds in 5 seconds
When the webhook action executes
Then the request shall complete successfully
  And the duration_ms shall be approximately 5000
```

---

### Feature: Retry Mechanism

#### Scenario: AC-010 - Retry on 5xx Server Error

```gherkin
Given a webhook action with retry_enabled set to true
  And retry_max_attempts set to 3
  And the first request returns HTTP 500
  And the second request returns HTTP 503
  And the third request returns HTTP 200
When the webhook action executes
Then the system shall attempt 3 requests total
  And the first retry shall wait approximately 5 seconds
  And the second retry shall wait approximately 15 seconds
  And the final status shall be "success"
  And all attempts shall be logged
```

#### Scenario: AC-011 - No Retry on 4xx Client Error

```gherkin
Given a webhook action with retry_enabled set to true
  And the request returns HTTP 404 Not Found
When the webhook action executes
Then the system shall NOT retry the request
  And the execution shall be logged with status "error"
  And the error_type shall be "client_error"
```

#### Scenario: AC-012 - Retry on Network Error

```gherkin
Given a webhook action targeting an unreachable host
  And retry_enabled is true
  And retry_max_attempts is 3
When the webhook action executes
Then the system shall retry 3 times
  And each attempt shall be logged with error_type "network_error"
  And the final status shall be "error" after all retries exhausted
```

#### Scenario: AC-013 - Retry on Rate Limit (429)

```gherkin
Given a webhook action where the endpoint returns HTTP 429
  And retry_enabled is true
When the webhook action executes
Then the system shall retry the request
  And the retry delay shall respect the Retry-After header if present
  And the execution shall be logged with error_type "rate_limited"
```

#### Scenario: AC-014 - Retry Disabled

```gherkin
Given a webhook action with retry_enabled set to false
  And the request returns HTTP 500
When the webhook action executes
Then the system shall NOT retry the request
  And the execution shall be logged with status "error" immediately
  And attempt_number shall be 1
```

---

### Feature: Response Logging

#### Scenario: AC-015 - Successful Response Logging

```gherkin
Given a webhook action that receives a successful response
  And the response status is 200
  And the response body is {"status": "received", "id": "msg_123"}
  And the response time is 150ms
When the response is processed
Then the execution log shall contain:
  | field            | value                                    |
  | response_status  | 200                                      |
  | response_body    | {"status": "received", "id": "msg_123"} |
  | duration_ms      | 150                                      |
  | status           | success                                  |
```

#### Scenario: AC-016 - Large Response Truncation

```gherkin
Given a webhook action that receives a response larger than 10KB
When the response is logged
Then the response_body shall be truncated to 10KB
  And a truncation indicator shall be appended
  And the full response size shall be recorded
```

---

### Feature: Response Data Mapping

#### Scenario: AC-017 - Map Response to Contact Field

```gherkin
Given a webhook action with response mapping configured
  And the mapping is {"external_id": "$.data.id"}
  And the response is {"data": {"id": "ext_123", "status": "active"}}
When the response is processed
Then the contact custom field "external_id" shall be updated to "ext_123"
  And the field update shall be logged
```

#### Scenario: AC-018 - Map Multiple Response Fields

```gherkin
Given a webhook action with multiple response mappings
  And the mappings include:
    | contact_field    | json_path         |
    | lead_score       | $.score           |
    | lead_grade       | $.grade           |
    | enrichment_date  | $.processed_at    |
  And the response contains all mapped fields
When the response is processed
Then all contact custom fields shall be updated
  And each mapping shall be logged individually
```

---

### Feature: URL Validation

#### Scenario: AC-019 - Valid HTTPS URL Accepted

```gherkin
Given a user configures a webhook with URL "https://api.example.com/webhook"
When the configuration is validated
Then the URL shall be accepted
  And SSL verification shall be enabled by default
```

#### Scenario: AC-020 - HTTP URL Accepted with Warning

```gherkin
Given a user configures a webhook with URL "http://api.example.com/webhook"
When the configuration is validated
Then the URL shall be accepted
  And a security warning shall be displayed
```

#### Scenario: AC-021 - Private IP Blocked

```gherkin
Given a user configures a webhook with URL "http://192.168.1.100/webhook"
When the configuration is validated
Then the URL shall be rejected
  And the error message shall indicate private IPs are not allowed
```

#### Scenario: AC-022 - Localhost Blocked

```gherkin
Given a user configures a webhook with URL "http://localhost:8080/webhook"
When the configuration is validated
Then the URL shall be rejected
  And the error message shall indicate localhost URLs are not allowed
```

#### Scenario: AC-023 - Invalid URL Format Rejected

```gherkin
Given a user configures a webhook with URL "not-a-valid-url"
When the configuration is validated
Then the URL shall be rejected
  And the error message shall indicate invalid URL format
```

---

### Feature: Merge Field Interpolation

#### Scenario: AC-024 - Contact Field Interpolation

```gherkin
Given a webhook payload template {"name": "{{contact.first_name}} {{contact.last_name}}"}
  And the contact has first_name "John" and last_name "Doe"
When the payload is constructed
Then the payload shall be {"name": "John Doe"}
```

#### Scenario: AC-025 - Missing Field Handling

```gherkin
Given a webhook payload template {"company": "{{contact.company}}"}
  And the contact does not have a company field
When the payload is constructed
Then the payload shall be {"company": ""}
  And no error shall occur
```

#### Scenario: AC-026 - Special Character Escaping

```gherkin
Given a webhook payload template {"bio": "{{contact.bio}}"}
  And the contact bio contains '"quotes" and <html>'
When the payload is constructed
Then the JSON shall be properly escaped
  And no XSS vulnerabilities shall exist
```

---

### Feature: Concurrent Execution Limits

#### Scenario: AC-027 - Per-Account Rate Limit

```gherkin
Given an account has 100 concurrent webhook requests in progress
When another webhook action attempts to execute
Then the execution shall be queued
  And the execution shall proceed when a slot becomes available
  And no requests shall be dropped
```

#### Scenario: AC-028 - Per-Endpoint Rate Limit

```gherkin
Given 10 concurrent requests to "https://api.example.com/webhook"
When an 11th request to the same endpoint is triggered
Then the execution shall be queued
  And the queue position shall be logged
```

---

### Feature: Webhook Test Endpoint

#### Scenario: AC-029 - Test Webhook Configuration

```gherkin
Given a user wants to test a webhook configuration
  And the configuration is valid
When the user calls POST /api/v1/webhooks/test with the config
Then the system shall send a test request to the endpoint
  And the response shall include:
    | field           | description                    |
    | success         | boolean indicating test result |
    | response_status | HTTP status code received      |
    | response_time   | Request duration in ms         |
    | error_message   | Error details if failed        |
```

#### Scenario: AC-030 - Test with Mock Data

```gherkin
Given a webhook configuration with merge fields
When testing the webhook
Then the system shall use sample/mock data for merge fields
  And the payload shall show interpolated values
  And the user shall see the exact request that will be sent
```

---

### Feature: Error Classification

#### Scenario: AC-031 - Network Error Classification

```gherkin
Given a webhook request fails due to DNS resolution failure
When the error is processed
Then the error_type shall be "network_error"
  And the error_message shall contain "DNS resolution failed"
  And retry shall be attempted if enabled
```

#### Scenario: AC-032 - SSL Error Classification

```gherkin
Given a webhook request fails due to invalid SSL certificate
  And ssl_verify is true
When the error is processed
Then the error_type shall be "ssl_error"
  And retry shall NOT be attempted
  And the user shall be notified of the SSL issue
```

---

## Quality Gates

### Coverage Requirements

- [ ] All scenarios have automated tests
- [ ] Unit test coverage >= 85%
- [ ] Integration test coverage >= 80%
- [ ] End-to-end tests for critical paths

### Performance Requirements

- [ ] Webhook execution starts within 100ms
- [ ] 95th percentile response processing < 50ms
- [ ] System handles 100 concurrent requests per account
- [ ] No memory leaks under sustained load

### Security Requirements

- [ ] Credentials encrypted at rest
- [ ] No credentials in logs
- [ ] Private IPs blocked
- [ ] XSS prevention in merge fields

---

## Traceability Matrix

| Acceptance Criteria | EARS Requirement | Test File |
|---------------------|------------------|-----------|
| AC-001, AC-002 | REQ-001, REQ-002 | test_webhook_call.py |
| AC-003 | REQ-003 | test_webhook_headers.py |
| AC-004 to AC-007 | REQ-005 | test_webhook_auth.py |
| AC-008, AC-009 | REQ-006 | test_webhook_timeout.py |
| AC-010 to AC-014 | REQ-007 | test_webhook_error_retry.py |
| AC-015, AC-016 | REQ-008 | test_webhook_logging.py |
| AC-017, AC-018 | REQ-009 | test_webhook_response_mapping.py |
| AC-019 to AC-023 | REQ-013 | test_webhook_url_validation.py |
| AC-024 to AC-026 | REQ-014 | test_merge_field_interpolation.py |
| AC-027, AC-028 | REQ-015 | test_webhook_rate_limiting.py |
| AC-029, AC-030 | REQ-001 | test_webhook_test_endpoint.py |
| AC-031, AC-032 | REQ-010 | test_webhook_error_classification.py |

---

## Definition of Done

1. All acceptance criteria tests passing
2. Code review approved
3. Security review completed
4. Performance benchmarks met
5. Documentation updated
6. Deployed to staging
7. Product owner sign-off

---

## Traceability

| Tag | Reference |
|-----|-----------|
| SPEC-WFL-010 | Parent specification |
| ACC-WFL-010 | This acceptance criteria |
