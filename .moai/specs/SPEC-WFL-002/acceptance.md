# SPEC-WFL-002: Configure Trigger - Acceptance Criteria

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-002 |
| **Title** | Configure Trigger |
| **Related SPEC** | [spec.md](./spec.md) |
| **Implementation Plan** | [plan.md](./plan.md) |

---

## Acceptance Criteria Overview

This document defines the acceptance criteria for the workflow trigger configuration feature using Gherkin (Given-When-Then) format. All scenarios must pass before the feature is considered complete.

---

## Feature: Contact Triggers

### AC-001: Contact Created Trigger Configuration

```gherkin
Feature: Contact Created Trigger

  Background:
    Given a user is authenticated with "workflow:edit" permission
    And a workflow exists with id "wf-001" in "draft" status

  Scenario: Successfully configure contact created trigger
    When the user sends a POST request to "/api/v1/workflows/wf-001/trigger" with:
      | trigger_type  | contact        |
      | trigger_event | contact_created|
      | filters       | {}             |
    Then the response status code should be 201
    And the response should contain a "trigger_id"
    And the trigger should be stored in the database
    And the workflow should have exactly one trigger

  Scenario: Configure contact created trigger with tag filter
    When the user sends a POST request to "/api/v1/workflows/wf-001/trigger" with:
      """json
      {
        "trigger_type": "contact",
        "trigger_event": "contact_created",
        "filters": {
          "conditions": [
            {"field": "tags", "operator": "contains", "value": "lead"}
          ],
          "logic": "AND"
        }
      }
      """
    Then the response status code should be 201
    And the trigger filters should be persisted correctly

  Scenario: Contact created trigger fires on new contact
    Given a workflow "wf-001" has an active contact_created trigger
    And the trigger has filter {"field": "source", "operator": "equals", "value": "website"}
    When a new contact is created with source "website"
    Then the trigger should evaluate to "matched"
    And the contact should be enrolled in workflow "wf-001"
    And a trigger execution log should be created

  Scenario: Contact created trigger does not fire for non-matching contact
    Given a workflow "wf-001" has an active contact_created trigger
    And the trigger has filter {"field": "source", "operator": "equals", "value": "website"}
    When a new contact is created with source "referral"
    Then the trigger should evaluate to "not_matched"
    And the contact should NOT be enrolled in workflow "wf-001"
```

### AC-002: Tag Added/Removed Triggers

```gherkin
Feature: Tag Triggers

  Scenario: Tag added trigger fires when specific tag is added
    Given a workflow "wf-002" has an active tag_added trigger for tag "hot-lead"
    And a contact exists with id "contact-001"
    When tag "hot-lead" is added to contact "contact-001"
    Then the trigger should fire for workflow "wf-002"
    And contact "contact-001" should be enrolled in the workflow

  Scenario: Tag added trigger does not fire for different tag
    Given a workflow "wf-002" has an active tag_added trigger for tag "hot-lead"
    And a contact exists with id "contact-001"
    When tag "cold-lead" is added to contact "contact-001"
    Then the trigger should NOT fire for workflow "wf-002"

  Scenario: Tag removed trigger fires when specific tag is removed
    Given a workflow "wf-003" has an active tag_removed trigger for tag "do-not-contact"
    And a contact exists with id "contact-002" with tag "do-not-contact"
    When tag "do-not-contact" is removed from contact "contact-002"
    Then the trigger should fire for workflow "wf-003"
    And contact "contact-002" should be enrolled in the workflow
```

---

## Feature: Form Triggers

### AC-003: Form Submitted Trigger

```gherkin
Feature: Form Submitted Trigger

  Scenario: Form submission triggers workflow enrollment
    Given a workflow "wf-004" has an active form_submitted trigger for form "contact-form-001"
    When a form submission is received for form "contact-form-001" from contact "contact-003"
    Then the trigger should fire for workflow "wf-004"
    And contact "contact-003" should be enrolled with form submission data available

  Scenario: Form submission with field filters
    Given a workflow "wf-005" has an active form_submitted trigger for form "lead-form"
    And the trigger has filter {"field": "budget", "operator": "greater_than", "value": 10000}
    When a form submission is received with budget "15000"
    Then the trigger should fire and enroll the contact

  Scenario: Form submission does not match filter
    Given a workflow "wf-005" has an active form_submitted trigger for form "lead-form"
    And the trigger has filter {"field": "budget", "operator": "greater_than", "value": 10000}
    When a form submission is received with budget "5000"
    Then the trigger should NOT fire
    And the contact should NOT be enrolled
```

---

## Feature: Pipeline Triggers

### AC-004: Pipeline Stage Changed Trigger

```gherkin
Feature: Pipeline Stage Changed Trigger

  Scenario: Stage change triggers workflow
    Given a workflow "wf-006" has an active stage_changed trigger
    And the trigger is configured for pipeline "sales" stage "qualified"
    And a deal exists for contact "contact-004" in stage "new"
    When the deal is moved to stage "qualified"
    Then the trigger should fire for workflow "wf-006"
    And contact "contact-004" should be enrolled

  Scenario: Deal won trigger fires
    Given a workflow "wf-007" has an active deal_won trigger
    And a deal exists for contact "contact-005" in pipeline "sales"
    When the deal is marked as "won"
    Then the trigger should fire for workflow "wf-007"
    And contact "contact-005" should be enrolled with deal data

  Scenario: Deal lost trigger fires with loss reason
    Given a workflow "wf-008" has an active deal_lost trigger
    And a deal exists for contact "contact-006" in pipeline "sales"
    When the deal is marked as "lost" with reason "budget"
    Then the trigger should fire for workflow "wf-008"
    And the enrollment should include loss_reason "budget"
```

---

## Feature: Time Triggers

### AC-005: Scheduled and Recurring Triggers

```gherkin
Feature: Time-Based Triggers

  Scenario: Birthday trigger fires on contact's birthday
    Given a workflow "wf-009" has an active birthday trigger
    And contact "contact-007" has birthday "January 26"
    When the system processes birthday triggers on "January 26, 2026"
    Then the trigger should fire for contact "contact-007"
    And the contact should be enrolled in workflow "wf-009"

  Scenario: Anniversary trigger fires on signup anniversary
    Given a workflow "wf-010" has an active anniversary trigger for field "signup_date"
    And contact "contact-008" has signup_date "2025-01-26"
    When the system processes anniversary triggers on "January 26, 2026"
    Then the trigger should fire for contact "contact-008"

  Scenario: Recurring schedule trigger processes batch
    Given a workflow "wf-011" has an active recurring_schedule trigger
    And the trigger is set to run daily at 09:00 UTC
    And 500 contacts match the trigger criteria
    When the scheduler runs at 09:00 UTC
    Then all 500 contacts should be queued for enrollment
    And the processing should complete within the timeout

  Scenario: Scheduled date trigger with relative timing
    Given a workflow "wf-012" has a scheduled_date trigger
    And the trigger is set for "7 days before" field "renewal_date"
    And contact "contact-009" has renewal_date "February 2, 2026"
    When the system processes on "January 26, 2026"
    Then the trigger should fire for contact "contact-009"
```

---

## Feature: Trigger Filters

### AC-006: Complex Filter Conditions

```gherkin
Feature: Trigger Filter Evaluation

  Scenario: AND logic filter evaluation
    Given a trigger with filters:
      """json
      {
        "conditions": [
          {"field": "tags", "operator": "contains", "value": "customer"},
          {"field": "lifetime_value", "operator": "greater_than", "value": 1000}
        ],
        "logic": "AND"
      }
      """
    When the trigger evaluates a contact with tags ["customer"] and lifetime_value 1500
    Then the filter should match

  Scenario: AND logic fails when one condition fails
    Given a trigger with AND logic filter
    When the trigger evaluates a contact with tags ["customer"] and lifetime_value 500
    Then the filter should NOT match

  Scenario: OR logic filter evaluation
    Given a trigger with filters:
      """json
      {
        "conditions": [
          {"field": "source", "operator": "equals", "value": "facebook"},
          {"field": "source", "operator": "equals", "value": "google"}
        ],
        "logic": "OR"
      }
      """
    When the trigger evaluates a contact with source "google"
    Then the filter should match

  Scenario: Filter with not_equals operator
    Given a trigger with filter {"field": "status", "operator": "not_equals", "value": "inactive"}
    When the trigger evaluates a contact with status "active"
    Then the filter should match

  Scenario: Filter with in operator
    Given a trigger with filter {"field": "country", "operator": "in", "value": ["US", "CA", "UK"]}
    When the trigger evaluates a contact with country "CA"
    Then the filter should match
```

---

## Feature: Trigger Validation

### AC-007: Trigger Configuration Validation

```gherkin
Feature: Trigger Validation

  Scenario: Reject invalid trigger type
    When the user attempts to configure a trigger with:
      | trigger_type  | invalid_type |
      | trigger_event | some_event   |
    Then the response status code should be 400
    And the response should contain error "Invalid trigger type"

  Scenario: Reject trigger without required fields
    When the user attempts to configure a trigger without trigger_event
    Then the response status code should be 422
    And the response should contain validation error for "trigger_event"

  Scenario: Reject duplicate trigger on workflow
    Given workflow "wf-013" already has a contact_created trigger
    When the user attempts to add another contact_created trigger
    Then the response status code should be 409
    And the response should contain error "Trigger already exists"

  Scenario: Reject filter with invalid operator
    When the user attempts to configure a trigger with filter:
      | field    | name           |
      | operator | invalid_op     |
      | value    | test           |
    Then the response status code should be 400
    And the response should contain error "Invalid filter operator"

  Scenario: Validate maximum filter conditions
    Given the system allows maximum 20 filter conditions
    When the user attempts to configure a trigger with 25 conditions
    Then the response status code should be 400
    And the response should contain error "Maximum 20 filter conditions allowed"
```

---

## Feature: Trigger State Management

### AC-008: Workflow Status and Trigger Behavior

```gherkin
Feature: Trigger State Management

  Scenario: Trigger does not fire when workflow is paused
    Given workflow "wf-014" is in "paused" status
    And the workflow has an active contact_created trigger
    When a new contact is created matching the trigger criteria
    Then the trigger should NOT fire
    And no enrollment should occur

  Scenario: Trigger does not fire when workflow is draft
    Given workflow "wf-015" is in "draft" status
    And the workflow has a configured trigger
    When an event matching the trigger occurs
    Then the trigger should NOT evaluate

  Scenario: Single enrollment prevents re-enrollment
    Given workflow "wf-016" has enrollment_limit "single"
    And contact "contact-010" is already enrolled in workflow "wf-016"
    When the trigger fires again for contact "contact-010"
    Then the contact should NOT be re-enrolled
    And the execution log should show "blocked: already_enrolled"

  Scenario: Multiple enrollment allows re-enrollment
    Given workflow "wf-017" has enrollment_limit "multiple"
    And contact "contact-011" is already enrolled in workflow "wf-017"
    When the trigger fires again for contact "contact-011"
    Then the contact should be re-enrolled
    And a new workflow execution should start
```

---

## Feature: Multi-Tenancy

### AC-009: Tenant Isolation

```gherkin
Feature: Multi-Tenant Trigger Isolation

  Scenario: Trigger only fires for same account events
    Given account "acc-001" has workflow "wf-018" with contact_created trigger
    And account "acc-002" has workflow "wf-019" with contact_created trigger
    When a contact is created in account "acc-001"
    Then only workflow "wf-018" trigger should evaluate
    And workflow "wf-019" trigger should NOT evaluate

  Scenario: Cannot access triggers from different account
    Given user belongs to account "acc-001"
    And workflow "wf-020" belongs to account "acc-002"
    When the user attempts to GET "/api/v1/workflows/wf-020/trigger"
    Then the response status code should be 403

  Scenario: Trigger logs are isolated by account
    Given account "acc-003" has trigger execution logs
    When account "acc-004" queries trigger logs
    Then only account "acc-004" logs should be returned
```

---

## Feature: Trigger Testing (Optional)

### AC-010: Trigger Test and Preview

```gherkin
Feature: Trigger Testing

  Scenario: Test trigger with specific contact
    Given workflow "wf-021" has a configured contact_created trigger
    When the user sends POST "/api/v1/workflows/wf-021/trigger/{id}/test" with:
      | contact_id | contact-012 |
    Then the response should show whether the contact matches
    And no actual enrollment should occur
    And a test log entry should be created

  Scenario: Preview matching contacts
    Given workflow "wf-022" has a trigger with filters
    When the user sends GET "/api/v1/workflows/wf-022/trigger/{id}/preview"
    Then the response should include estimated_count
    And the response should include sample_contacts (up to 10)
```

---

## Non-Functional Acceptance Criteria

### AC-NF-001: Performance

```gherkin
Feature: Trigger Performance

  Scenario: Trigger evaluation latency
    Given 100 active workflows with triggers
    When an event is published
    Then all applicable triggers should be evaluated within 100ms

  Scenario: High throughput event processing
    Given the system is under load with 1000 events/second
    When events are published continuously for 1 minute
    Then all events should be processed
    And no events should be lost
    And average latency should remain under 200ms
```

### AC-NF-002: Reliability

```gherkin
Feature: Trigger Reliability

  Scenario: Event processing survives service restart
    Given 50 events are queued for processing
    When the trigger service is restarted
    Then all 50 events should be processed after restart
    And no duplicate processing should occur

  Scenario: Failed trigger evaluation is logged
    Given a trigger with a malformed filter
    When an event triggers evaluation
    Then the error should be logged
    And the event should be marked for retry
    And other triggers should continue processing
```

---

## Definition of Done

- [ ] All Gherkin scenarios pass in automated tests
- [ ] API endpoints documented in OpenAPI specification
- [ ] 85%+ code coverage for trigger module
- [ ] Performance benchmarks meet targets
- [ ] Security review completed
- [ ] Code review approved
- [ ] Integration tests pass in CI/CD pipeline

---

## Test File Mapping

| Acceptance Criteria | Test File |
|---------------------|-----------|
| AC-001 | `tests/workflows/test_contact_triggers.py` |
| AC-002 | `tests/workflows/test_tag_triggers.py` |
| AC-003 | `tests/workflows/test_form_triggers.py` |
| AC-004 | `tests/workflows/test_pipeline_triggers.py` |
| AC-005 | `tests/workflows/test_time_triggers.py` |
| AC-006 | `tests/workflows/test_trigger_filters.py` |
| AC-007 | `tests/workflows/test_trigger_validation.py` |
| AC-008 | `tests/workflows/test_trigger_state.py` |
| AC-009 | `tests/workflows/test_trigger_multitenancy.py` |
| AC-010 | `tests/workflows/test_trigger_testing.py` |
