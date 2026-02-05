# SPEC-WFL-001: Acceptance Criteria

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-001 |
| **Title** | Create Workflow |
| **Format** | Given-When-Then (Gherkin) |

---

## Feature: Create Workflow

As a platform user with workflow permissions,
I want to create a new automation workflow,
So that I can automate actions based on triggers.

---

## Acceptance Criteria

### AC-001: Successful Workflow Creation

```gherkin
Feature: Create Workflow - Happy Path

  Scenario: Create a new workflow with minimal required fields
    Given I am authenticated as a user with "workflows:create" permission
    And I have account ID "550e8400-e29b-41d4-a716-446655440000"
    When I send a POST request to "/api/v1/workflows" with body:
      """
      {
        "name": "Welcome Sequence"
      }
      """
    Then the response status code should be 201
    And the response should contain:
      | field         | value                |
      | name          | Welcome Sequence     |
      | status        | draft                |
      | version       | 1                    |
      | trigger_type  | null                 |
      | description   |                      |
    And the response should contain a valid UUID in field "id"
    And the response should contain a valid ISO timestamp in field "created_at"
    And the workflow should be associated with account "550e8400-e29b-41d4-a716-446655440000"

  Scenario: Create a new workflow with all optional fields
    Given I am authenticated as a user with "workflows:create" permission
    When I send a POST request to "/api/v1/workflows" with body:
      """
      {
        "name": "Lead Nurturing Campaign",
        "description": "Automated follow-up for new leads",
        "trigger_type": "contact_created",
        "trigger_config": {
          "filters": {
            "tags": ["new-lead"]
          }
        }
      }
      """
    Then the response status code should be 201
    And the response should contain:
      | field         | value                              |
      | name          | Lead Nurturing Campaign            |
      | description   | Automated follow-up for new leads  |
      | trigger_type  | contact_created                    |
      | status        | draft                              |
    And the response trigger_config should contain filters with tags ["new-lead"]
```

### AC-002: Workflow Name Validation

```gherkin
Feature: Create Workflow - Name Validation

  Scenario: Reject workflow with name too short
    Given I am authenticated as a user with "workflows:create" permission
    When I send a POST request to "/api/v1/workflows" with body:
      """
      {
        "name": "AB"
      }
      """
    Then the response status code should be 400
    And the response should contain error code "VALIDATION_ERROR"
    And the response should contain message indicating minimum length is 3

  Scenario: Reject workflow with name too long
    Given I am authenticated as a user with "workflows:create" permission
    When I send a POST request to "/api/v1/workflows" with body:
      """
      {
        "name": "This is a very long workflow name that exceeds the maximum allowed length of one hundred characters which should fail validation"
      }
      """
    Then the response status code should be 400
    And the response should contain error code "VALIDATION_ERROR"
    And the response should contain message indicating maximum length is 100

  Scenario: Reject workflow with invalid characters in name
    Given I am authenticated as a user with "workflows:create" permission
    When I send a POST request to "/api/v1/workflows" with body:
      """
      {
        "name": "Invalid@Name#Here!"
      }
      """
    Then the response status code should be 400
    And the response should contain error code "VALIDATION_ERROR"
    And the response should contain message about allowed characters

  Scenario: Accept workflow with hyphens and underscores
    Given I am authenticated as a user with "workflows:create" permission
    When I send a POST request to "/api/v1/workflows" with body:
      """
      {
        "name": "lead-nurturing_v2"
      }
      """
    Then the response status code should be 201
    And the response name should be "lead-nurturing_v2"

  Scenario: Trim whitespace from workflow name
    Given I am authenticated as a user with "workflows:create" permission
    When I send a POST request to "/api/v1/workflows" with body:
      """
      {
        "name": "  Welcome Sequence  "
      }
      """
    Then the response status code should be 201
    And the response name should be "Welcome Sequence"
```

### AC-003: Workflow Name Uniqueness

```gherkin
Feature: Create Workflow - Name Uniqueness

  Scenario: Reject duplicate workflow name within same account
    Given I am authenticated as a user with "workflows:create" permission
    And a workflow named "Existing Workflow" exists in my account
    When I send a POST request to "/api/v1/workflows" with body:
      """
      {
        "name": "Existing Workflow"
      }
      """
    Then the response status code should be 409
    And the response should contain error code "CONFLICT"
    And the response should contain message "Workflow name already exists"

  Scenario: Allow same workflow name in different accounts
    Given I am authenticated as a user in account "account-1"
    And a workflow named "Welcome Sequence" exists in account "account-2"
    When I send a POST request to "/api/v1/workflows" with body:
      """
      {
        "name": "Welcome Sequence"
      }
      """
    Then the response status code should be 201
    And the workflow should be created successfully

  Scenario: Allow reusing name of soft-deleted workflow
    Given I am authenticated as a user with "workflows:create" permission
    And a workflow named "Old Workflow" was soft-deleted in my account
    When I send a POST request to "/api/v1/workflows" with body:
      """
      {
        "name": "Old Workflow"
      }
      """
    Then the response status code should be 201
    And a new workflow with name "Old Workflow" should be created
```

### AC-004: Authentication and Authorization

```gherkin
Feature: Create Workflow - Security

  Scenario: Reject unauthenticated request
    Given I am not authenticated
    When I send a POST request to "/api/v1/workflows" with body:
      """
      {
        "name": "Test Workflow"
      }
      """
    Then the response status code should be 401
    And the response should contain error code "UNAUTHORIZED"

  Scenario: Reject request without required permission
    Given I am authenticated as a user without "workflows:create" permission
    When I send a POST request to "/api/v1/workflows" with body:
      """
      {
        "name": "Test Workflow"
      }
      """
    Then the response status code should be 403
    And the response should contain error code "FORBIDDEN"

  Scenario: Accept request with valid authentication and permission
    Given I am authenticated as a user with "workflows:create" permission
    When I send a POST request to "/api/v1/workflows" with body:
      """
      {
        "name": "Valid Workflow"
      }
      """
    Then the response status code should be 201
    And the response created_by should match my user ID
```

### AC-005: Rate Limiting

```gherkin
Feature: Create Workflow - Rate Limiting

  Scenario: Enforce rate limit on workflow creation
    Given I am authenticated as a user with "workflows:create" permission
    And I have already created 100 workflows in the past hour
    When I send a POST request to "/api/v1/workflows" with body:
      """
      {
        "name": "One More Workflow"
      }
      """
    Then the response status code should be 429
    And the response should contain error code "RATE_LIMITED"
    And the response should include Retry-After header

  Scenario: Allow creation under rate limit
    Given I am authenticated as a user with "workflows:create" permission
    And I have created 50 workflows in the past hour
    When I send a POST request to "/api/v1/workflows" with body:
      """
      {
        "name": "Still Under Limit"
      }
      """
    Then the response status code should be 201
```

### AC-006: Audit Logging

```gherkin
Feature: Create Workflow - Audit Trail

  Scenario: Log workflow creation event
    Given I am authenticated as user "user-123" with "workflows:create" permission
    When I send a POST request to "/api/v1/workflows" with body:
      """
      {
        "name": "Audit Test Workflow"
      }
      """
    Then the response status code should be 201
    And an audit log entry should be created with:
      | field        | value                  |
      | action       | workflow.created       |
      | user_id      | user-123               |
      | workflow_id  | <created workflow id>  |
    And the audit log should contain the initial workflow configuration
```

### AC-007: Multi-Tenancy Isolation

```gherkin
Feature: Create Workflow - Tenant Isolation

  Scenario: Workflow associated with correct tenant
    Given I am authenticated as a user in account "tenant-abc"
    When I send a POST request to "/api/v1/workflows" with body:
      """
      {
        "name": "Tenant Specific Workflow"
      }
      """
    Then the response status code should be 201
    And the response account_id should be "tenant-abc"
    And the workflow should only be visible to users in account "tenant-abc"

  Scenario: Cannot access workflows from other tenants
    Given I am authenticated as a user in account "tenant-abc"
    And a workflow exists in account "tenant-xyz"
    When I try to access workflows
    Then I should not see workflows from account "tenant-xyz"
```

---

## Test Scenarios

### Unit Tests

| Test ID | Description | Input | Expected Output |
|---------|-------------|-------|-----------------|
| test_create_workflow_entity | Create workflow from valid data | Valid params | Workflow instance |
| test_workflow_name_validation_min | Name too short | "AB" | ValidationError |
| test_workflow_name_validation_max | Name too long | 101 chars | ValidationError |
| test_workflow_name_validation_chars | Invalid characters | "@#$" | ValidationError |
| test_workflow_status_default | Default status | No status | "draft" |
| test_workflow_version_default | Default version | No version | 1 |

### Integration Tests

| Test ID | Description | Setup | Expected Behavior |
|---------|-------------|-------|-------------------|
| test_repository_save | Persist workflow | DB connection | Workflow saved |
| test_repository_find_by_name | Find existing | Create workflow | Found workflow |
| test_repository_find_by_name_not_found | Find non-existent | Empty DB | None returned |
| test_repository_name_unique | Enforce uniqueness | Existing name | IntegrityError |

### End-to-End Tests

| Test ID | Description | Setup | Expected Response |
|---------|-------------|-------|-------------------|
| test_api_create_workflow_success | Full creation flow | Auth user | 201 Created |
| test_api_create_workflow_unauthorized | Missing auth | No token | 401 Unauthorized |
| test_api_create_workflow_forbidden | Missing permission | Limited user | 403 Forbidden |
| test_api_create_workflow_conflict | Duplicate name | Existing workflow | 409 Conflict |
| test_api_create_workflow_rate_limited | Exceed limit | 100+ requests | 429 Rate Limited |

---

## Quality Gates

### Definition of Done

- [ ] All acceptance criteria scenarios pass
- [ ] Unit test coverage >= 95% for domain layer
- [ ] Integration test coverage >= 85% for infrastructure layer
- [ ] E2E test coverage >= 80% for presentation layer
- [ ] Overall test coverage >= 85%
- [ ] Zero Ruff linting errors
- [ ] Zero Pyright type errors
- [ ] API documentation updated in OpenAPI spec
- [ ] Database migration tested and reversible
- [ ] Audit logging verified
- [ ] Rate limiting verified
- [ ] Performance benchmarks met (p95 < 200ms)

### TRUST 5 Validation

| Pillar | Requirement | Status |
|--------|-------------|--------|
| **Tested** | 85%+ coverage, characterization tests | Pending |
| **Readable** | Clear naming, minimal comments | Pending |
| **Unified** | Single source of truth, consistent patterns | Pending |
| **Secured** | OWASP compliance, input validation | Pending |
| **Trackable** | Audit logs, conventional commits | Pending |

---

## Verification Methods

### Automated Testing

```bash
# Run all workflow tests
pytest tests/workflows/ -v --cov=src/workflows --cov-report=html

# Run specific test categories
pytest tests/workflows/unit/ -v
pytest tests/workflows/integration/ -v
pytest tests/workflows/e2e/ -v

# Run with coverage threshold
pytest tests/workflows/ --cov=src/workflows --cov-fail-under=85
```

### Manual Testing Checklist

- [ ] Create workflow via API with minimal fields
- [ ] Create workflow via API with all fields
- [ ] Verify workflow appears in database
- [ ] Verify audit log created
- [ ] Test duplicate name rejection
- [ ] Test permission denial
- [ ] Test rate limiting
- [ ] Verify tenant isolation

### Performance Testing

```bash
# Load test with k6
k6 run tests/performance/workflow_creation.js

# Expected results:
# - p95 response time < 200ms
# - Error rate < 0.1%
# - Throughput >= 100 rps
```

---

## Traceability Tags

- TAG:SPEC-WFL-001
- TAG:ACCEPTANCE
- TAG:GHERKIN
- TAG:TRUST-5
