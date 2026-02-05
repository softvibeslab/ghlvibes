# SPEC-WFL-004: Acceptance Criteria

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-004 |
| **Title** | Add Condition/Branch |
| **Module** | workflows |
| **Domain** | automation |
| **Priority** | Critical |

---

## Test Scenarios

### TS-001: If/Else Branch Creation

#### Scenario: Create basic if/else condition on workflow canvas

```gherkin
Feature: If/Else Branch Creation

  Scenario: User creates an if/else condition with contact field comparison
    Given I am authenticated as a user with "workflows.conditions.create" permission
    And I have an existing workflow with ID "wf-001" in "draft" status
    And the workflow canvas is open
    When I drag a condition node onto the canvas at position (200, 300)
    And I select condition type "contact_field_equals"
    And I configure the condition with:
      | field    | operator | value        |
      | email    | contains | @gmail.com   |
    And I click "Save Condition"
    Then the condition node should be created with a unique ID
    And the node should display "True" and "False" branch connectors
    And the condition should be saved to the database
    And I should see a success notification "Condition created successfully"

  Scenario: User connects branches to action nodes
    Given I have an if/else condition node on the canvas
    When I drag from the "True" connector to an "Send Email" action node
    And I drag from the "False" connector to a "Wait" action node
    Then the "True" branch should be connected to the email action
    And the "False" branch should be connected to the wait action
    And the workflow should be valid for activation

  Scenario: User attempts to activate workflow with unconfigured condition
    Given I have a condition node without configuration
    When I attempt to activate the workflow
    Then I should see validation error "Condition configuration is required"
    And the workflow should remain in "draft" status
```

---

### TS-002: Multi-Branch Decision Tree

#### Scenario: Create multi-branch condition with multiple outcomes

```gherkin
Feature: Multi-Branch Decision Tree

  Scenario: User creates a multi-branch condition with 4 outcomes
    Given I am editing workflow "wf-001"
    And I add a condition node with branch_type "multi_branch"
    When I configure the following branches:
      | branch_name | condition_type      | field        | operator | value    |
      | VIP         | contact_field_equals| membership   | equals   | vip      |
      | Premium     | contact_field_equals| membership   | equals   | premium  |
      | Basic       | contact_field_equals| membership   | equals   | basic    |
      | Default     | (default branch)    |              |          |          |
    And I save the condition
    Then the condition should have 4 branches
    And branch "Default" should be marked as is_default=true
    And branches should be evaluated in order: VIP, Premium, Basic, Default

  Scenario: Evaluation follows branch priority order
    Given a multi-branch condition with branches in order: A, B, C, Default
    And contact "c-001" matches conditions for both branch A and branch B
    When the workflow executes for contact "c-001"
    Then branch A should be selected (first match wins)
    And the execution log should show "branch_taken: A"

  Scenario: Default branch is used when no conditions match
    Given a multi-branch condition with branches: VIP, Premium, Default
    And contact "c-002" has membership="free" (matches no branch conditions)
    When the workflow executes for contact "c-002"
    Then branch "Default" should be selected
    And the execution log should show "branch_taken: Default"
```

---

### TS-003: Split Test Branch

#### Scenario: Create A/B split test with percentage distribution

```gherkin
Feature: Split Test Branch

  Scenario: User creates 50/50 A/B split test
    Given I am editing workflow "wf-001"
    And I add a condition node with branch_type "split_test"
    When I configure the following variants:
      | variant_name | percentage |
      | Variant A    | 50         |
      | Variant B    | 50         |
    And I save the condition
    Then the condition should have 2 branches
    And total percentage should equal 100%
    And the condition should be valid

  Scenario: Validation fails when percentages do not sum to 100
    Given I am configuring a split test condition
    When I set variant percentages to:
      | variant_name | percentage |
      | A            | 40         |
      | B            | 40         |
    And I attempt to save
    Then I should see validation error "Percentages must sum to 100%"
    And the condition should not be saved

  Scenario: Split test distributes traffic according to percentages
    Given a split test with Variant A (70%) and Variant B (30%)
    When I execute the workflow for 1000 contacts
    Then approximately 700 contacts should go to Variant A (within 5% tolerance)
    And approximately 300 contacts should go to Variant B (within 5% tolerance)
    And each contact's branch assignment should be logged

  Scenario: User creates multi-variant split test with 5 variants
    Given I am configuring a split test condition
    When I set variant percentages to:
      | variant_name | percentage |
      | A            | 20         |
      | B            | 20         |
      | C            | 20         |
      | D            | 20         |
      | E            | 20         |
    And I save the condition
    Then the condition should have 5 variants
    And all variants should be persisted correctly
```

---

### TS-004: Contact Field Condition Evaluation

#### Scenario: Evaluate various operators on contact fields

```gherkin
Feature: Contact Field Condition Evaluation

  Scenario Outline: Field comparison with different operators
    Given a contact with <field> = "<contact_value>"
    And a condition configured with field="<field>", operator="<operator>", value="<target_value>"
    When the condition is evaluated for the contact
    Then the result should be <expected_result>

    Examples:
      | field      | contact_value        | operator      | target_value | expected_result |
      | email      | john@gmail.com       | contains      | @gmail       | true            |
      | email      | john@yahoo.com       | contains      | @gmail       | false           |
      | first_name | John                 | equals        | John         | true            |
      | first_name | John                 | equals        | john         | true            |
      | first_name | John                 | not_equals    | Jane         | true            |
      | first_name | John Smith           | starts_with   | John         | true            |
      | last_name  | Smith                | ends_with     | ith          | true            |
      | phone      |                      | is_empty      |              | true            |
      | phone      | +1234567890          | is_not_empty  |              | true            |
      | age        | 25                   | greater_than  | 18           | true            |
      | age        | 15                   | greater_than  | 18           | false           |
      | country    | USA                  | in_list       | USA,UK,CA    | true            |
      | country    | FR                   | not_in_list   | USA,UK,CA    | true            |

  Scenario: Handle null field value gracefully
    Given a contact with phone = null
    And a condition configured with field="phone", operator="equals", value="+1234567890"
    When the condition is evaluated
    Then the result should be false
    And no error should be thrown

  Scenario: Case-insensitive string comparison
    Given a contact with email = "JOHN@GMAIL.COM"
    And a condition configured with field="email", operator="contains", value="@gmail.com"
    When the condition is evaluated
    Then the result should be true (case-insensitive match)
```

---

### TS-005: Tag-Based Condition Evaluation

#### Scenario: Evaluate conditions based on contact tags

```gherkin
Feature: Tag-Based Condition Evaluation

  Scenario: Contact has specific tag
    Given a contact with tags ["vip", "newsletter", "active"]
    And a condition configured with mode="has_any_tag", tags=["vip"]
    When the condition is evaluated
    Then the result should be true

  Scenario: Contact has all specified tags
    Given a contact with tags ["vip", "newsletter", "active"]
    And a condition configured with mode="has_all_tags", tags=["vip", "newsletter"]
    When the condition is evaluated
    Then the result should be true

  Scenario: Contact missing one of the required tags
    Given a contact with tags ["vip", "active"]
    And a condition configured with mode="has_all_tags", tags=["vip", "newsletter"]
    When the condition is evaluated
    Then the result should be false

  Scenario: Contact has none of the specified tags
    Given a contact with tags ["free", "inactive"]
    And a condition configured with mode="has_no_tags", tags=["vip", "premium"]
    When the condition is evaluated
    Then the result should be true

  Scenario: Tag evaluation with empty tag list on contact
    Given a contact with tags []
    And a condition configured with mode="has_any_tag", tags=["vip"]
    When the condition is evaluated
    Then the result should be false
```

---

### TS-006: Pipeline Stage Condition Evaluation

#### Scenario: Evaluate conditions based on pipeline stage

```gherkin
Feature: Pipeline Stage Condition Evaluation

  Scenario: Contact is in specific pipeline stage
    Given a contact in pipeline "sales" at stage "proposal"
    And a condition configured with mode="is_in_stage", pipeline="sales", stage="proposal"
    When the condition is evaluated
    Then the result should be true

  Scenario: Contact is after a specific stage
    Given a pipeline "sales" with stages: lead -> qualified -> proposal -> negotiation -> won
    And a contact at stage "negotiation"
    And a condition configured with mode="is_after_stage", stage="proposal"
    When the condition is evaluated
    Then the result should be true

  Scenario: Contact is before a specific stage
    Given a pipeline "sales" with stages: lead -> qualified -> proposal -> negotiation -> won
    And a contact at stage "qualified"
    And a condition configured with mode="is_before_stage", stage="proposal"
    When the condition is evaluated
    Then the result should be true

  Scenario: Contact not in any pipeline
    Given a contact not associated with any pipeline
    And a condition configured with mode="is_in_stage", stage="lead"
    When the condition is evaluated
    Then the result should be false
```

---

### TS-007: Email Engagement Condition Evaluation

#### Scenario: Evaluate conditions based on email engagement

```gherkin
Feature: Email Engagement Condition Evaluation

  Scenario: Contact opened a specific email
    Given contact "c-001" opened email "email-123" on 2026-01-25
    And a condition configured with type="email_was_opened", email_id="email-123"
    When the condition is evaluated
    Then the result should be true

  Scenario: Contact opened email within time window
    Given contact "c-001" opened email "email-123" 2 hours ago
    And a condition configured with type="email_was_opened", email_id="email-123", time_window="24_hours"
    When the condition is evaluated
    Then the result should be true

  Scenario: Contact opened email outside time window
    Given contact "c-001" opened email "email-123" 48 hours ago
    And a condition configured with type="email_was_opened", email_id="email-123", time_window="24_hours"
    When the condition is evaluated
    Then the result should be false

  Scenario: Contact clicked specific link in email
    Given contact "c-001" clicked link "https://example.com/promo" in email "email-123"
    And a condition configured with type="link_was_clicked", link_pattern="*/promo"
    When the condition is evaluated
    Then the result should be true

  Scenario: Contact clicked at least N times
    Given contact "c-001" clicked links in campaign "campaign-001" 5 times
    And a condition configured with type="link_was_clicked", campaign_id="campaign-001", min_clicks=3
    When the condition is evaluated
    Then the result should be true
```

---

### TS-008: Time-Based Condition Evaluation

#### Scenario: Evaluate conditions based on time

```gherkin
Feature: Time-Based Condition Evaluation

  Scenario: Current day is Monday
    Given the current day is Monday
    And a condition configured with type="current_day_of_week", days=["Monday", "Wednesday", "Friday"]
    When the condition is evaluated
    Then the result should be true

  Scenario: Current time within business hours
    Given the current time is 10:30 AM in the account timezone
    And a condition configured with type="current_time_between", start="09:00", end="17:00"
    When the condition is evaluated
    Then the result should be true

  Scenario: Current time outside business hours
    Given the current time is 8:00 PM in the account timezone
    And a condition configured with type="current_time_between", start="09:00", end="17:00"
    When the condition is evaluated
    Then the result should be false

  Scenario: Days since contact created
    Given a contact created 10 days ago
    And a condition configured with type="days_since_event", event="contact_created", days_operator="greater_than", days_value=7
    When the condition is evaluated
    Then the result should be true

  Scenario: Contact birthday is today
    Given a contact with birthday = today's date
    And a condition configured with type="contact_date_field", field="birthday", condition="is_today"
    When the condition is evaluated
    Then the result should be true

  Scenario: Timezone-aware evaluation
    Given the account timezone is "America/New_York"
    And the current UTC time is 14:00 (which is 9:00 AM in New York)
    And a condition configured with type="current_time_between", start="09:00", end="10:00"
    When the condition is evaluated using account timezone
    Then the result should be true
```

---

### TS-009: Combined Logic Condition Evaluation

#### Scenario: Evaluate combined AND/OR conditions

```gherkin
Feature: Combined Logic Condition Evaluation

  Scenario: All conditions must match (AND logic)
    Given a contact with email="john@gmail.com", country="USA", tags=["vip"]
    And a condition with logic="ALL" containing:
      | type                 | configuration                      |
      | contact_field_equals | field=email, operator=contains, value=@gmail |
      | contact_field_equals | field=country, operator=equals, value=USA     |
      | contact_has_tag      | mode=has_any_tag, tags=["vip"]                |
    When the condition is evaluated
    Then the result should be true (all conditions match)

  Scenario: At least one condition must match (OR logic)
    Given a contact with email="john@yahoo.com", country="USA", tags=["free"]
    And a condition with logic="ANY" containing:
      | type                 | configuration                      |
      | contact_field_equals | field=email, operator=contains, value=@gmail |
      | contact_field_equals | field=country, operator=equals, value=USA     |
    When the condition is evaluated
    Then the result should be true (country matches)

  Scenario: AND logic fails when one condition is false
    Given a contact with email="john@gmail.com", country="UK"
    And a condition with logic="ALL" containing:
      | type                 | configuration                      |
      | contact_field_equals | field=email, operator=contains, value=@gmail |
      | contact_field_equals | field=country, operator=equals, value=USA     |
    When the condition is evaluated
    Then the result should be false (country does not match)

  Scenario: Nested condition groups
    Given a complex condition with nested groups:
      """
      (email contains @gmail AND country = USA)
      OR
      (membership = vip AND tags include premium)
      """
    And a contact with email="john@yahoo.com", membership="vip", tags=["premium"]
    When the condition is evaluated
    Then the result should be true (second group matches)
```

---

### TS-010: Condition Validation

#### Scenario: Validate condition configuration before save

```gherkin
Feature: Condition Configuration Validation

  Scenario: Valid condition configuration passes validation
    Given a condition configuration:
      | condition_type       | contact_field_equals |
      | field                | email                |
      | operator             | contains             |
      | value                | @gmail.com           |
    When validation is performed
    Then the validation should pass
    And no errors should be returned

  Scenario: Missing required field fails validation
    Given a condition configuration:
      | condition_type       | contact_field_equals |
      | operator             | contains             |
      | value                | @gmail.com           |
    When validation is performed
    Then the validation should fail
    And error should include "field is required"

  Scenario: Invalid operator for field type fails validation
    Given a condition configuration:
      | condition_type       | contact_field_equals |
      | field                | email                |
      | operator             | greater_than         |
      | value                | test                 |
    When validation is performed
    Then the validation should fail
    And error should include "greater_than operator not valid for text field"

  Scenario: Referenced field does not exist
    Given a condition configuration:
      | condition_type       | contact_field_equals |
      | field                | nonexistent_field    |
      | operator             | equals               |
      | value                | test                 |
    When validation is performed
    Then the validation should fail
    And error should include "field 'nonexistent_field' does not exist"

  Scenario: Referenced tag does not exist
    Given a condition configuration:
      | condition_type       | contact_has_tag      |
      | mode                 | has_any_tag          |
      | tags                 | ["nonexistent_tag"]  |
    When validation is performed
    Then the validation should fail
    And error should include "tag 'nonexistent_tag' does not exist"
```

---

### TS-011: Execution Logging

#### Scenario: Log condition evaluations

```gherkin
Feature: Condition Execution Logging

  Scenario: Successful evaluation is logged
    Given workflow "wf-001" with condition "cond-001"
    And contact "c-001" with email="john@gmail.com"
    When the condition is evaluated for the contact
    Then a log entry should be created with:
      | field             | value                    |
      | execution_id      | (current execution)      |
      | condition_id      | cond-001                 |
      | contact_id        | c-001                    |
      | evaluation_inputs | {"field_value": "john@gmail.com"} |
      | evaluation_result | True                     |
      | duration_ms       | (measured value)         |

  Scenario: Query logs for specific condition
    Given condition "cond-001" has been evaluated 100 times
    When I query logs with condition_id="cond-001" and date_range="last 7 days"
    Then I should receive up to 100 log entries
    And entries should be sorted by evaluated_at descending

  Scenario: PII is masked in logs
    Given a contact with email="john.doe@example.com" and phone="+1234567890"
    When the condition is evaluated and logged
    Then the log's evaluation_inputs should show:
      | field        | masked_value           |
      | email        | j***.d**@example.com   |
      | phone        | +1***4567890           |
```

---

### TS-012: Error Handling

#### Scenario: Handle evaluation errors gracefully

```gherkin
Feature: Condition Error Handling

  Scenario: Field access error routes to default branch
    Given a condition referencing field "custom_field_1"
    And the field access throws an unexpected error
    When the condition is evaluated
    Then the error should be logged with full context
    And the contact should be routed to the default/false branch
    And workflow execution should continue

  Scenario: Workflow owner is notified of evaluation errors
    Given a condition that fails evaluation 5 times within 1 hour
    When the error threshold is reached
    Then the workflow owner should receive an error notification
    And the notification should include:
      | field           | value                    |
      | workflow_name   | "Lead Nurturing Flow"    |
      | condition_name  | "Check VIP Status"       |
      | error_count     | 5                        |
      | sample_error    | "Field access error..."  |

  Scenario: Condition with error branch configured
    Given a condition with an explicit "Error" branch
    When an evaluation error occurs
    Then the contact should be routed to the "Error" branch
    And the error details should be available in the execution context
```

---

## API Acceptance Tests

### API-001: Create Condition Endpoint

```gherkin
Feature: Create Condition API

  Scenario: Successfully create condition via API
    Given I am authenticated with valid JWT token
    And I have permission "workflows.conditions.create"
    When I send POST request to "/api/v1/workflows/{workflow_id}/conditions" with:
      """json
      {
        "node_id": "550e8400-e29b-41d4-a716-446655440000",
        "condition_type": "contact_field_equals",
        "branch_type": "if_else",
        "configuration": {
          "field": "email",
          "operator": "contains",
          "value": "@gmail.com"
        },
        "position": { "x": 200, "y": 300 }
      }
      """
    Then response status should be 201
    And response body should contain:
      | field           | type   |
      | id              | UUID   |
      | workflow_id     | UUID   |
      | branches        | array  |
    And 2 branches should be created (True, False)

  Scenario: Create condition without authentication
    Given I am not authenticated
    When I send POST request to "/api/v1/workflows/{workflow_id}/conditions"
    Then response status should be 401
    And response body should contain error "Authentication required"

  Scenario: Create condition without permission
    Given I am authenticated but without "workflows.conditions.create" permission
    When I send POST request to "/api/v1/workflows/{workflow_id}/conditions"
    Then response status should be 403
    And response body should contain error "Permission denied"

  Scenario: Create condition with invalid configuration
    Given I am authenticated with valid permissions
    When I send POST request with invalid configuration:
      """json
      {
        "node_id": "550e8400-e29b-41d4-a716-446655440000",
        "condition_type": "contact_field_equals",
        "branch_type": "if_else",
        "configuration": {
          "field": "",
          "operator": "invalid_op",
          "value": null
        }
      }
      """
    Then response status should be 422
    And response body should contain validation errors for:
      | field    | error                    |
      | field    | Field cannot be empty    |
      | operator | Invalid operator         |
```

---

## Performance Acceptance Criteria

### PERF-001: Evaluation Latency

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Simple condition evaluation | < 20ms P95 | Load test with 1000 concurrent evaluations |
| Complex condition (10 criteria) | < 100ms P95 | Load test with AND/OR nested conditions |
| Split test random selection | < 5ms P95 | Benchmark test |
| Database query for condition | < 10ms P95 | Query profiling |

### PERF-002: Throughput

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Concurrent evaluations | 1000/second | Load test |
| Condition CRUD operations | 500/second | Load test |
| Log writes | 2000/second | Load test |

### PERF-003: Resource Usage

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Memory per evaluation | < 10MB | Profiling |
| Database connections | < 50 concurrent | Connection pool monitoring |
| Cache hit rate | > 80% | Redis metrics |

---

## Security Acceptance Criteria

### SEC-001: Authorization

```gherkin
Scenario: User cannot access conditions in workflows they don't own
  Given user "A" owns workflow "wf-001"
  And user "B" does not have access to "wf-001"
  When user "B" attempts to GET "/api/v1/workflows/wf-001/conditions"
  Then response status should be 403

Scenario: Admin can access all workflow conditions
  Given user "admin" has role "admin"
  And workflow "wf-001" is owned by user "A"
  When user "admin" attempts to GET "/api/v1/workflows/wf-001/conditions"
  Then response status should be 200
```

### SEC-002: Input Validation

```gherkin
Scenario: SQL injection attempt in field value is sanitized
  Given a condition configuration with value="'; DROP TABLE contacts; --"
  When the condition is evaluated
  Then the value should be treated as a literal string
  And no SQL injection should occur

Scenario: XSS attempt in branch name is sanitized
  Given a branch name containing "<script>alert('xss')</script>"
  When the branch is created
  Then the name should be HTML-escaped in storage
  And the name should be safely rendered in UI
```

---

## Definition of Done

- [ ] All EARS requirements implemented and tested
- [ ] All acceptance test scenarios passing
- [ ] API documentation complete (OpenAPI spec updated)
- [ ] Unit test coverage >= 95%
- [ ] Integration tests passing
- [ ] Performance benchmarks meeting targets
- [ ] Security scan passing (0 critical/high vulnerabilities)
- [ ] Code review approved by 2 reviewers
- [ ] PII masking verified in all logs
- [ ] Audit logging enabled for all condition operations
- [ ] Error handling covers all edge cases
- [ ] Documentation updated (developer guide, user guide)
