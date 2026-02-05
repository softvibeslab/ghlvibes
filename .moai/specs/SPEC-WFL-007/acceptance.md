# SPEC-WFL-007: Goal Tracking - Acceptance Criteria

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-007 |
| **Title** | Goal Tracking |
| **Module** | workflows |
| **Domain** | automation |
| **Priority** | Medium |

---

## Test Scenarios

### Feature: Goal Configuration

#### Scenario: Configure a tag_added goal for a workflow

```gherkin
Given a user with workflow edit permissions
And an existing workflow "Lead Nurturing" in draft status
When the user adds a goal with the following configuration:
  | goal_type | criteria                |
  | tag_added | {"tag_name": "Customer"} |
Then the goal should be saved successfully
And the goal should be associated with the workflow
And the goal should have status "active"
And an audit log entry should be created for the goal configuration
```

#### Scenario: Configure a purchase_made goal with amount criteria

```gherkin
Given a user with workflow edit permissions
And an existing workflow "Upsell Campaign"
When the user adds a goal with the following configuration:
  | goal_type     | criteria                                    |
  | purchase_made | {"product_id": null, "min_amount": 100.00}  |
Then the goal should be saved successfully
And the goal criteria should include minimum purchase amount of 100.00
And any purchase over $100 should trigger this goal
```

#### Scenario: Configure a form_submitted goal

```gherkin
Given a user with workflow edit permissions
And an existing workflow "Contact Form Follow-up"
And a form "Contact Us" with ID "form-123"
When the user adds a goal with the following configuration:
  | goal_type      | criteria              |
  | form_submitted | {"form_id": "form-123"} |
Then the goal should be saved successfully
And the goal should reference the correct form
```

#### Scenario: Configure an appointment_booked goal

```gherkin
Given a user with workflow edit permissions
And an existing workflow "Consultation Booking"
And a calendar "Sales Calendar" with ID "cal-456"
When the user adds a goal with the following configuration:
  | goal_type          | criteria                                        |
  | appointment_booked | {"calendar_id": "cal-456", "any_appointment": false} |
Then the goal should be saved successfully
And the goal should only trigger for appointments on the specified calendar
```

#### Scenario: Configure a pipeline_stage_reached goal

```gherkin
Given a user with workflow edit permissions
And an existing workflow "Sales Pipeline Automation"
And a pipeline "Sales Pipeline" with stage "Closed Won" ID "stage-789"
When the user adds a goal with the following configuration:
  | goal_type              | criteria                                          |
  | pipeline_stage_reached | {"pipeline_id": "pipe-123", "stage_id": "stage-789"} |
Then the goal should be saved successfully
And the goal should trigger when a contact reaches "Closed Won" stage
```

#### Scenario: Reject goal configuration with missing criteria

```gherkin
Given a user with workflow edit permissions
And an existing workflow "Test Workflow"
When the user attempts to add a goal with the following configuration:
  | goal_type | criteria |
  | tag_added | {}       |
Then the request should be rejected with status 400
And the error message should indicate "Goal criteria cannot be empty"
```

#### Scenario: Reject goal configuration referencing non-existent entity

```gherkin
Given a user with workflow edit permissions
And an existing workflow "Test Workflow"
When the user attempts to add a goal with the following configuration:
  | goal_type      | criteria                        |
  | form_submitted | {"form_id": "non-existent-form"} |
Then the request should be rejected with status 400
And the error message should indicate "Referenced form does not exist"
```

---

### Feature: Goal Achievement - Tag Added

#### Scenario: Contact achieves tag_added goal

```gherkin
Given a workflow "Lead Nurturing" with an active goal:
  | goal_type | criteria                |
  | tag_added | {"tag_name": "Customer"} |
And a contact "John Doe" is enrolled in the workflow
And the contact is at step 3 of the workflow
When the contact receives the tag "Customer"
Then the goal should be marked as achieved
And a goal achievement record should be created with:
  | field          | value                    |
  | contact_id     | john-doe-id              |
  | goal_type      | tag_added                |
  | trigger_event  | {"tag_name": "Customer"} |
And the contact should exit the workflow
And all pending actions for the contact should be cancelled
And the workflow enrollment status should be "completed_goal"
```

#### Scenario: Contact receives non-matching tag

```gherkin
Given a workflow "Lead Nurturing" with an active goal:
  | goal_type | criteria                |
  | tag_added | {"tag_name": "Customer"} |
And a contact "Jane Doe" is enrolled in the workflow
When the contact receives the tag "Prospect"
Then the goal should NOT be marked as achieved
And the contact should remain in the workflow
And the workflow should continue normal execution
```

---

### Feature: Goal Achievement - Purchase Made

#### Scenario: Contact makes qualifying purchase

```gherkin
Given a workflow "Upsell Campaign" with an active goal:
  | goal_type     | criteria                 |
  | purchase_made | {"min_amount": 100.00}   |
And a contact "Alice Smith" is enrolled in the workflow
When the contact completes a purchase of $150.00
Then the goal should be marked as achieved
And a goal achievement record should be created with:
  | field          | value                      |
  | contact_id     | alice-smith-id             |
  | goal_type      | purchase_made              |
  | trigger_event  | {"amount": 150.00, ...}    |
And the contact should exit the workflow
```

#### Scenario: Contact makes non-qualifying purchase

```gherkin
Given a workflow "Upsell Campaign" with an active goal:
  | goal_type     | criteria                 |
  | purchase_made | {"min_amount": 100.00}   |
And a contact "Bob Jones" is enrolled in the workflow
When the contact completes a purchase of $50.00
Then the goal should NOT be marked as achieved
And the contact should remain in the workflow
```

#### Scenario: Contact makes any purchase when any_purchase is true

```gherkin
Given a workflow "First Purchase" with an active goal:
  | goal_type     | criteria                |
  | purchase_made | {"any_purchase": true}  |
And a contact "Charlie Brown" is enrolled in the workflow
When the contact completes a purchase of $10.00
Then the goal should be marked as achieved
And the contact should exit the workflow
```

---

### Feature: Goal Achievement - Appointment Booked

#### Scenario: Contact books appointment on specified calendar

```gherkin
Given a workflow "Consultation Booking" with an active goal:
  | goal_type          | criteria                   |
  | appointment_booked | {"calendar_id": "cal-456"} |
And a contact "David Lee" is enrolled in the workflow
When the contact books an appointment on calendar "cal-456"
Then the goal should be marked as achieved
And the contact should exit the workflow
And the achievement should log the appointment details
```

#### Scenario: Contact books appointment on different calendar

```gherkin
Given a workflow "Consultation Booking" with an active goal:
  | goal_type          | criteria                   |
  | appointment_booked | {"calendar_id": "cal-456"} |
And a contact "Emma Wilson" is enrolled in the workflow
When the contact books an appointment on calendar "cal-789"
Then the goal should NOT be marked as achieved
And the contact should remain in the workflow
```

---

### Feature: Goal Achievement - Form Submitted

#### Scenario: Contact submits target form

```gherkin
Given a workflow "Contact Form Follow-up" with an active goal:
  | goal_type      | criteria              |
  | form_submitted | {"form_id": "form-123"} |
And a contact "Frank Miller" is enrolled in the workflow
When the contact submits form "form-123"
Then the goal should be marked as achieved
And the contact should exit the workflow
```

---

### Feature: Goal Achievement - Pipeline Stage Reached

#### Scenario: Contact reaches target pipeline stage

```gherkin
Given a workflow "Sales Pipeline Automation" with an active goal:
  | goal_type              | criteria                                          |
  | pipeline_stage_reached | {"pipeline_id": "pipe-123", "stage_id": "stage-789"} |
And a contact "Grace Taylor" is enrolled in the workflow
When the contact moves to stage "stage-789" in pipeline "pipe-123"
Then the goal should be marked as achieved
And the contact should exit the workflow
```

---

### Feature: Workflow Exit on Goal Achievement

#### Scenario: Cancel pending actions on goal achievement

```gherkin
Given a workflow with the following scheduled actions for contact "Henry Adams":
  | action_type | scheduled_time       | status    |
  | send_email  | 2026-01-27T10:00:00Z | pending   |
  | send_sms    | 2026-01-28T14:00:00Z | pending   |
  | add_tag     | 2026-01-29T09:00:00Z | pending   |
And the workflow has an active tag_added goal
When the contact achieves the goal
Then all pending actions should be cancelled
And no further actions should be executed for this enrollment
```

#### Scenario: Cancel wait step on goal achievement

```gherkin
Given a contact "Ivy Chen" is enrolled in a workflow
And the contact is currently in a wait step scheduled to complete in 3 days
And the workflow has an active purchase_made goal
When the contact makes a qualifying purchase
Then the wait step should be cancelled
And the contact should exit the workflow immediately
```

#### Scenario: Emit workflow exit event on goal achievement

```gherkin
Given a contact "Jack Robinson" is enrolled in workflow "Lead Nurturing"
And the workflow has an active tag_added goal
When the contact achieves the goal
Then a "workflow.exit.goal" event should be emitted with:
  | field              | value              |
  | workflow_id        | lead-nurturing-id  |
  | contact_id         | jack-robinson-id   |
  | exit_reason        | goal_achieved      |
  | goal_type          | tag_added          |
```

---

### Feature: Event Listener Lifecycle

#### Scenario: Register listeners when workflow is activated

```gherkin
Given a workflow "New Campaign" with the following goals:
  | goal_type     |
  | tag_added     |
  | purchase_made |
When the workflow is activated
Then event listeners should be registered for:
  | event_type          |
  | contact.tag.added   |
  | payment.completed   |
And the listeners should be associated with the workflow ID
```

#### Scenario: Unregister listeners when workflow is deactivated

```gherkin
Given an active workflow "Old Campaign" with registered listeners
When the workflow is deactivated
Then all goal event listeners should be unregistered
And no goal events should be processed for this workflow
```

#### Scenario: Cleanup listener when contact exits workflow

```gherkin
Given a contact "Kate Brown" enrolled in workflow "Sales Sequence"
And goal listeners are active for this contact
When the contact exits the workflow (for any reason)
Then the contact-specific listener associations should be cleaned up
```

---

### Feature: Goal Analytics

#### Scenario: Track goal achievement metrics

```gherkin
Given a workflow "Lead Conversion" with an active purchase_made goal
And the following enrollment history:
  | contact_id | enrolled_at          | status         | goal_achieved |
  | contact-1  | 2026-01-01T00:00:00Z | completed_goal | true          |
  | contact-2  | 2026-01-02T00:00:00Z | completed_goal | true          |
  | contact-3  | 2026-01-03T00:00:00Z | active         | false         |
  | contact-4  | 2026-01-04T00:00:00Z | completed      | false         |
  | contact-5  | 2026-01-05T00:00:00Z | active         | false         |
When requesting goal statistics for the workflow
Then the response should include:
  | metric           | value |
  | total_enrolled   | 5     |
  | goals_achieved   | 2     |
  | conversion_rate  | 40.0  |
```

#### Scenario: Calculate average time to goal achievement

```gherkin
Given a workflow with the following goal achievements:
  | contact_id | enrolled_at          | achieved_at          |
  | contact-1  | 2026-01-01T00:00:00Z | 2026-01-03T00:00:00Z |
  | contact-2  | 2026-01-02T00:00:00Z | 2026-01-05T00:00:00Z |
When requesting goal statistics
Then the average time to goal should be 60 hours
```

---

### Feature: Multiple Goals (Optional)

#### Scenario: Workflow with multiple goals - any goal logic

```gherkin
Given a workflow "Multi-Goal Campaign" with multiple goals:
  | goal_type     | criteria                |
  | tag_added     | {"tag_name": "Customer"} |
  | purchase_made | {"any_purchase": true}  |
And goal completion logic is set to "any"
And a contact "Leo Martinez" is enrolled
When the contact receives the tag "Customer"
Then the contact should exit the workflow
And only one goal achievement should be recorded
```

#### Scenario: Workflow with multiple goals - all goals logic

```gherkin
Given a workflow "Complete Journey" with multiple goals:
  | goal_type          | criteria                   |
  | tag_added          | {"tag_name": "Qualified"}  |
  | appointment_booked | {"any_appointment": true}  |
And goal completion logic is set to "all"
And a contact "Maria Garcia" is enrolled
When the contact receives the tag "Qualified"
Then the contact should NOT exit the workflow
When the contact books an appointment
Then the contact should exit the workflow
And two goal achievements should be recorded
```

---

### Feature: Goal Validation

#### Scenario: Prevent workflow activation with invalid goal

```gherkin
Given a workflow "Invalid Setup" with a goal:
  | goal_type | criteria                        |
  | tag_added | {"tag_id": "non-existent-tag"}  |
When attempting to activate the workflow
Then the activation should fail
And the error should indicate "Invalid goal configuration: tag does not exist"
```

#### Scenario: Limit maximum goals per workflow

```gherkin
Given a workflow already has 3 configured goals
When attempting to add a 4th goal
Then the request should be rejected with status 400
And the error should indicate "Maximum of 3 goals per workflow exceeded"
```

---

## Quality Gates

### Definition of Done

- [ ] All acceptance scenarios pass
- [ ] Unit test coverage >= 85%
- [ ] Integration tests for all goal types pass
- [ ] API documentation complete in OpenAPI format
- [ ] Performance tests pass (event processing < 100ms p95)
- [ ] Security review complete (tenant isolation verified)
- [ ] Code review approved by 2 reviewers
- [ ] No critical or high severity bugs
- [ ] Monitoring dashboards configured
- [ ] Runbook documentation complete

### Performance Criteria

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Goal event processing latency | < 100ms p95 | APM monitoring |
| Goal evaluation throughput | > 10,000/sec | Load testing |
| API response time | < 200ms p95 | API metrics |
| Database query time | < 50ms p95 | Query monitoring |

### Security Criteria

| Requirement | Verification Method |
|-------------|---------------------|
| Tenant isolation | Penetration testing, code review |
| Input validation | Automated security scanning |
| Audit logging | Log analysis, compliance review |
| Authorization checks | Unit tests, integration tests |

---

## Test Data Requirements

### Test Contacts

| Contact ID | Name | Tags | Pipeline Stage |
|------------|------|------|----------------|
| test-contact-1 | John Doe | Prospect | Lead |
| test-contact-2 | Jane Smith | Customer | Qualified |
| test-contact-3 | Bob Wilson | Prospect, VIP | Opportunity |

### Test Workflows

| Workflow ID | Name | Status | Goals |
|-------------|------|--------|-------|
| test-workflow-1 | Lead Nurturing | active | tag_added |
| test-workflow-2 | Upsell Campaign | active | purchase_made |
| test-workflow-3 | Multi-Goal | active | tag_added, purchase_made |

### Test Events

| Event Type | Payload |
|------------|---------|
| contact.tag.added | {"contact_id": "...", "tag_name": "Customer"} |
| payment.completed | {"contact_id": "...", "amount": 150.00} |
| appointment.booked | {"contact_id": "...", "calendar_id": "cal-456"} |
| form.submitted | {"contact_id": "...", "form_id": "form-123"} |
| pipeline.stage.changed | {"contact_id": "...", "stage_id": "stage-789"} |

---

## Traceability Matrix

| Requirement | Scenario | Test File |
|-------------|----------|-----------|
| R1 | Configure a tag_added goal | test_goal_configuration.py |
| R2 | All goal type scenarios | test_goal_types.py |
| R3 | Contact achieves tag_added goal | test_tag_goal_achievement.py |
| R4 | Contact makes qualifying purchase | test_purchase_goal_achievement.py |
| R5 | Contact books appointment | test_appointment_goal_achievement.py |
| R6 | Contact submits target form | test_form_goal_achievement.py |
| R7 | Contact reaches pipeline stage | test_pipeline_goal_achievement.py |
| R8 | Cancel pending actions | test_workflow_exit.py |
| R9 | Register listeners | test_listener_lifecycle.py |
| R10 | Unregister listeners | test_listener_lifecycle.py |
| R11 | Multiple goals scenarios | test_multiple_goals.py |
| R12 | Track goal achievement metrics | test_goal_analytics.py |
| R13 | Prevent invalid goal | test_goal_validation.py |
