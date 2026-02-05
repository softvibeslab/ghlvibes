# SPEC-WFL-003: Add Action Step - Acceptance Criteria

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-003 |
| **Title** | Add Action Step |
| **Related SPEC** | [spec.md](./spec.md) |
| **Implementation Plan** | [plan.md](./plan.md) |

---

## Acceptance Criteria Overview

This document defines the acceptance criteria for the workflow action step functionality using Given-When-Then (Gherkin) format.

---

## AC-001: Add Action to Workflow

### Scenario: Successfully add action to workflow in draft state

```gherkin
Given a workflow exists with id "wf-123" in "draft" status
And the user has "workflow:edit" permission
When the user sends POST request to "/api/v1/workflows/wf-123/actions"
With body:
  | field       | value        |
  | action_type | send_email   |
  | position    | 1            |
Then the response status should be 201
And the response should contain:
  | field       | value        |
  | action_type | send_email   |
  | position    | 1            |
  | is_enabled  | true         |
And the action should be linked in the workflow sequence
```

### Scenario: Reject action addition to active workflow

```gherkin
Given a workflow exists with id "wf-456" in "active" status
And contacts are currently enrolled in the workflow
When the user sends POST request to "/api/v1/workflows/wf-456/actions"
Then the response status should be 403
And the response should contain error:
  | code    | WORKFLOW_LOCKED          |
  | message | Cannot modify active workflow with enrollments |
```

### Scenario: Reject action addition without permission

```gherkin
Given a workflow exists with id "wf-789"
And the user does NOT have "workflow:edit" permission
When the user sends POST request to "/api/v1/workflows/wf-789/actions"
Then the response status should be 403
And the response should contain error:
  | code    | PERMISSION_DENIED        |
  | message | Workflow edit permission required |
```

---

## AC-002: Action Position Management

### Scenario: Insert action at specific position

```gherkin
Given a workflow "wf-123" has actions:
  | id   | position | action_type |
  | a-1  | 1        | send_email  |
  | a-2  | 2        | wait_time   |
  | a-3  | 3        | add_tag     |
When the user adds a new action at position 2
Then the existing actions should be reordered:
  | id   | position | action_type |
  | a-1  | 1        | send_email  |
  | new  | 2        | send_sms    |
  | a-2  | 3        | wait_time   |
  | a-3  | 4        | add_tag     |
```

### Scenario: Reorder actions via drag-drop

```gherkin
Given a workflow "wf-123" has actions at positions [1, 2, 3]
When the user sends POST request to "/api/v1/workflows/wf-123/actions/reorder"
With body:
  | action_id | new_position |
  | a-3       | 1            |
Then the actions should be reordered to [a-3, a-1, a-2]
And all action links should be updated correctly
```

### Scenario: Delete action and reconnect sequence

```gherkin
Given a workflow "wf-123" has a linear sequence: a-1 -> a-2 -> a-3
When the user deletes action "a-2"
Then action "a-1" should link directly to "a-3"
And the positions should be renumbered to [1, 2]
```

---

## AC-003: Action Configuration Validation

### Scenario: Validate required fields for email action

```gherkin
Given the user is adding a "send_email" action
When the user submits configuration without "template_id"
Then the response status should be 422
And the response should contain validation error:
  | field       | error                      |
  | template_id | Field is required          |
```

### Scenario: Validate email template exists

```gherkin
Given the user is adding a "send_email" action
And template_id "tmpl-invalid" does not exist
When the user submits the action configuration
Then the response status should be 400
And the response should contain error:
  | code    | TEMPLATE_NOT_FOUND         |
  | message | Email template not found   |
```

### Scenario: Validate action-specific constraints

```gherkin
Given the user is adding a "send_sms" action
When the user submits message longer than 1600 characters
Then the response status should be 422
And the response should contain validation error:
  | field   | error                              |
  | message | SMS message exceeds 1600 character limit |
```

---

## AC-010: Send Email Action Execution

### Scenario: Execute email action successfully

```gherkin
Given a workflow execution is in progress for contact "contact-123"
And the current action is "send_email" with valid configuration
When the action executor processes the action
Then an email should be queued via SendGrid
And the email should contain merged contact data:
  | merge_field              | value          |
  | {{contact.first_name}}   | John           |
  | {{contact.email}}        | john@test.com  |
And the action execution should be logged with status "completed"
And tracking pixels should be inserted if track_opens is true
```

### Scenario: Handle email delivery failure

```gherkin
Given a workflow execution is in progress
And the email action encounters a SendGrid API error
When the action executor retries 3 times and still fails
Then the action execution should be marked as "failed"
And an error notification should be sent to the workflow owner
And the execution log should contain:
  | field         | value                    |
  | status        | failed                   |
  | retry_count   | 3                        |
  | error_message | SendGrid API unavailable |
```

### Scenario: Track email opens and clicks

```gherkin
Given an email was sent with tracking enabled
When the recipient opens the email
Then an "email_opened" event should be recorded
And the event should trigger any waiting "wait_for_event" actions
When the recipient clicks a tracked link
Then an "email_clicked" event should be recorded with link URL
```

---

## AC-011: Send SMS Action Execution

### Scenario: Execute SMS action with TCPA compliance

```gherkin
Given a workflow execution for contact "contact-123"
And the contact is in timezone "America/New_York"
And the current time in that timezone is 22:30 (after quiet hours)
When the "send_sms" action is processed
Then the SMS should NOT be sent immediately
And the SMS should be scheduled for 09:00 next day
And the execution status should be "scheduled"
```

### Scenario: Execute SMS within allowed hours

```gherkin
Given a workflow execution for contact "contact-456"
And the contact is in timezone "America/Los_Angeles"
And the current time in that timezone is 14:00
When the "send_sms" action is processed
Then the SMS should be sent immediately via Twilio
And the execution status should be "completed"
And the Twilio message SID should be stored in result_data
```

### Scenario: Handle SMS opt-out

```gherkin
Given a contact has opted out of SMS communications
When the "send_sms" action is processed for that contact
Then the SMS should NOT be sent
And the execution status should be "skipped"
And the skip reason should be "Contact opted out of SMS"
```

---

## AC-020: CRM Actions Execution

### Scenario: Create contact action

```gherkin
Given a workflow execution with context containing:
  | field      | value           |
  | email      | new@example.com |
  | first_name | Jane            |
When the "create_contact" action executes
Then a new contact should be created with the context data
And a "contact_created" event should be emitted
And the new contact ID should be stored in execution result
```

### Scenario: Handle duplicate contact creation

```gherkin
Given a contact with email "existing@example.com" already exists
And the "create_contact" action has duplicate_handling: "update"
When the action executes with email "existing@example.com"
Then the existing contact should be updated
And NO new contact should be created
And the execution log should indicate "Duplicate found - updated existing"
```

### Scenario: Add tag to contact

```gherkin
Given a workflow execution for contact "contact-123"
And the contact does not have tag "VIP"
When the "add_tag" action executes with tag_name: "VIP"
Then the tag should be added to the contact
And if the tag did not exist, it should be created
And a "tag_added" event should be emitted
```

### Scenario: Move pipeline stage

```gherkin
Given contact "contact-123" has an opportunity in pipeline "sales"
And the opportunity is currently in stage "Lead"
When the "move_pipeline_stage" action executes to stage "Qualified"
Then the opportunity stage should be updated to "Qualified"
And the stage transition should be logged
And a "stage_changed" event should be emitted
```

### Scenario: Assign to user with round robin

```gherkin
Given a team "sales-team" has users: [user-1, user-2, user-3]
And the last assignment was to "user-2"
When the "assign_to_user" action executes with assignment_type: "round_robin"
Then the contact should be assigned to "user-3"
And if notify_assignee is true, a notification should be sent
```

---

## AC-030: Timing Actions Execution

### Scenario: Wait time action pauses execution

```gherkin
Given a workflow execution reaches a "wait_time" action
And the action is configured for 2 days
When the action is processed
Then the execution should be paused
And a scheduled job should be created for 2 days from now
And the execution status should be "waiting"
And the scheduled_at timestamp should be stored
```

### Scenario: Wait time action resumes correctly

```gherkin
Given a workflow execution is waiting with scheduled_at "2026-01-28T10:00:00Z"
When the current time reaches "2026-01-28T10:00:00Z"
Then the scheduler should pick up the execution
And the workflow should resume from the next action
And the wait action status should change to "completed"
```

### Scenario: Wait until date action

```gherkin
Given a workflow execution reaches a "wait_until_date" action
And the action is configured for contact field "appointment_date"
And contact.appointment_date is "2026-02-15"
And time_of_day is "09:00"
And timezone_mode is "contact"
When the action is processed
Then execution should be scheduled for "2026-02-15T09:00:00" in contact's timezone
```

### Scenario: Wait for event with timeout

```gherkin
Given a workflow execution reaches a "wait_for_event" action
And the action is waiting for "email_open" event
And timeout is configured for 3 days
When 3 days pass without the email being opened
Then the timeout should trigger
And if timeout_action is "continue", execution should proceed to next action
And the wait action status should be "completed" with result "timeout"
```

---

## AC-040: Webhook Action Execution

### Scenario: Execute webhook successfully

```gherkin
Given a workflow execution reaches a "webhook_call" action
And the action is configured with:
  | field   | value                        |
  | url     | https://api.example.com/hook |
  | method  | POST                         |
  | payload | {"contact_id": "{{contact.id}}"} |
When the action executes
Then an HTTP POST request should be sent to the URL
And the payload should contain the merged contact ID
And the response should be stored if store_response is true
And the execution status should be "completed"
```

### Scenario: Webhook retry on failure

```gherkin
Given a webhook action encounters a 500 error
When the retry logic processes the failure
Then the action should be retried with exponential backoff
And retry intervals should be: 1s, 2s, 4s
After 3 failed retries
Then the action should be marked as "failed"
And the error should be logged with all retry attempts
```

### Scenario: Webhook with authentication

```gherkin
Given a webhook action is configured with auth_type: "bearer"
And auth_config contains token: "secret-token"
When the webhook request is sent
Then the request should include header "Authorization: Bearer secret-token"
```

---

## AC-050: Membership Actions Execution

### Scenario: Grant course access

```gherkin
Given a workflow execution for contact "contact-123"
And the "grant_course_access" action is configured for course "course-456"
When the action executes
Then the contact should have access to the course
And if duration_days is set, access should expire after that period
And if send_welcome is true, a welcome email should be sent
And an "access_granted" event should be emitted
```

### Scenario: Revoke course access

```gherkin
Given contact "contact-123" has access to course "course-456"
And the contact has 50% progress in the course
When the "revoke_course_access" action executes with retain_progress: true
Then the contact's access should be revoked
And the progress data should be preserved
And an "access_revoked" event should be emitted
```

---

## AC-060: Error Handling

### Scenario: Non-retryable error stops execution

```gherkin
Given a workflow execution is processing an action
And the action encounters an authentication error (non-retryable)
When the error handler processes the error
Then the action should NOT be retried
And the execution should be marked as "failed"
And the workflow execution should pause
And an error notification should be sent to the owner
```

### Scenario: Action with fallback continues workflow

```gherkin
Given a workflow action is configured with a fallback action
And the primary action fails
When the error handler processes the failure
Then the fallback action should be executed
And if fallback succeeds, execution should continue
And the primary action should be logged as "failed_with_fallback"
```

### Scenario: Comprehensive execution logging

```gherkin
Given any workflow action executes
Then the execution log should contain:
  | field              | requirement        |
  | id                 | UUID               |
  | workflow_execution_id | UUID            |
  | action_id          | UUID               |
  | contact_id         | UUID               |
  | status             | enum               |
  | started_at         | timestamp          |
  | completed_at       | timestamp or null  |
  | execution_data     | input parameters   |
  | result_data        | output data        |
  | error_message      | string or null     |
  | retry_count        | integer            |
```

---

## AC-070: API Response Formats

### Scenario: List actions with pagination

```gherkin
Given a workflow has 15 actions
When the user requests GET "/api/v1/workflows/wf-123/actions?limit=10&offset=0"
Then the response should contain 10 actions
And the response should include pagination metadata:
  | field    | value |
  | total    | 15    |
  | limit    | 10    |
  | offset   | 0     |
  | has_more | true  |
```

### Scenario: Get action details

```gherkin
Given an action "action-123" exists in workflow "wf-456"
When the user requests GET "/api/v1/workflows/wf-456/actions/action-123"
Then the response should contain full action details:
  | field         | present |
  | id            | yes     |
  | action_type   | yes     |
  | action_config | yes     |
  | position      | yes     |
  | is_enabled    | yes     |
  | created_at    | yes     |
  | updated_at    | yes     |
```

---

## AC-080: Performance Requirements

### Scenario: Action creation response time

```gherkin
Given a valid action creation request
When the request is processed
Then the response should be returned within 200ms
And the action should be persisted to database
```

### Scenario: Bulk action operations

```gherkin
Given a workflow with 50 actions (maximum allowed)
When a reorder operation is performed
Then all position updates should complete within 500ms
And database constraints should be maintained
```

### Scenario: Concurrent action executions

```gherkin
Given 1000 workflows are triggered simultaneously
When all initial actions are queued for execution
Then the queue should process at least 1000 actions per second
And no actions should be lost or duplicated
```

---

## Test Matrix

| AC ID | Test Type | Priority | Automated |
|-------|-----------|----------|-----------|
| AC-001 | Integration | Critical | Yes |
| AC-002 | Integration | Critical | Yes |
| AC-003 | Unit | Critical | Yes |
| AC-010 | Integration | Critical | Yes |
| AC-011 | Integration | Critical | Yes |
| AC-020 | Integration | High | Yes |
| AC-030 | Integration | High | Yes |
| AC-040 | Integration | High | Yes |
| AC-050 | Integration | Medium | Yes |
| AC-060 | Unit | Critical | Yes |
| AC-070 | Integration | High | Yes |
| AC-080 | Performance | High | Yes |

---

## Quality Gates

### Code Quality

- [ ] All acceptance criteria have corresponding test cases
- [ ] Test coverage >= 85% for action module
- [ ] No critical or high severity security issues
- [ ] All API endpoints documented in OpenAPI

### Performance

- [ ] Action creation < 200ms response time
- [ ] Action execution throughput >= 1000/second
- [ ] No memory leaks in long-running tests

### Security

- [ ] Input validation for all action configurations
- [ ] Authorization checks on all endpoints
- [ ] Audit logging for all CRUD operations
- [ ] Custom code execution sandboxed

---

## Definition of Done

- [ ] All AC scenarios passing in CI/CD pipeline
- [ ] Performance benchmarks within targets
- [ ] Security review completed
- [ ] API documentation updated
- [ ] Code review approved by 2 reviewers
- [ ] Integration tests stable (no flaky tests)
