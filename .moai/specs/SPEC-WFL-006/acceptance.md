# SPEC-WFL-006: Wait Step Processing - Acceptance Criteria

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-006 |
| **Title** | Wait Step Processing |
| **Phase** | Acceptance |
| **Format** | Given-When-Then (Gherkin) |

---

## Test Scenarios

### Feature: Fixed Time Wait

#### Scenario: AC-001 - Wait for fixed duration in minutes

```gherkin
Given a workflow execution is active for contact "john@example.com"
And the execution reaches a wait step configured for 30 minutes
When the wait step is processed
Then a wait execution record is created with status "scheduled"
And the scheduled_at timestamp is set to current time plus 30 minutes
And a scheduled job is registered in Redis
And the workflow execution is paused at this step
```

**Test Data:**
- Contact ID: UUID
- Duration: 30
- Unit: minutes
- Expected scheduled_at: NOW() + 30 minutes

---

#### Scenario: AC-002 - Wait for fixed duration in days

```gherkin
Given a workflow execution is active for contact "jane@example.com"
And the execution reaches a wait step configured for 3 days
When the wait step is processed
Then a wait execution record is created with status "scheduled"
And the scheduled_at timestamp is set to current time plus 72 hours
And a scheduled job is registered in Redis
```

**Test Data:**
- Duration: 3
- Unit: days
- Expected scheduled_at: NOW() + 72 hours

---

#### Scenario: AC-003 - Wait for fixed duration in weeks

```gherkin
Given a workflow execution is active for contact "bob@example.com"
And the execution reaches a wait step configured for 2 weeks
When the wait step is processed
Then a wait execution record is created with status "scheduled"
And the scheduled_at timestamp is set to current time plus 14 days
```

**Test Data:**
- Duration: 2
- Unit: weeks
- Expected scheduled_at: NOW() + 336 hours

---

#### Scenario: AC-004 - Resume workflow after wait duration expires

```gherkin
Given a wait step execution exists with scheduled_at in the past
And the wait step has status "scheduled"
When the scheduler processes the wait job
Then the workflow execution is resumed from the next step
And the wait execution status is updated to "resumed"
And the resumed_at timestamp is set to current time
And the resumed_by field is set to "scheduler"
```

---

#### Scenario: AC-005 - Validate maximum wait duration

```gherkin
Given a workflow execution is active
And a wait step is configured with duration 100 weeks
When the wait step creation is attempted
Then the request is rejected with validation error
And the error message indicates "Maximum wait duration is 12 weeks"
```

---

### Feature: Wait Until Date

#### Scenario: AC-006 - Wait until specific future date

```gherkin
Given a workflow execution is active for contact "alice@example.com"
And the current date is "2026-01-26"
And the execution reaches a wait step configured to wait until "2026-02-14 09:00:00"
When the wait step is processed
Then a wait execution record is created with status "scheduled"
And the scheduled_at timestamp is set to "2026-02-14 09:00:00 UTC"
```

**Test Data:**
- Target date: 2026-02-14T09:00:00Z
- Expected scheduled_at: 2026-02-14T09:00:00Z

---

#### Scenario: AC-007 - Wait until date from contact field

```gherkin
Given a workflow execution is active for contact "charlie@example.com"
And the contact has field "renewal_date" set to "2026-03-15 00:00:00"
And the execution reaches a wait step configured to wait until contact field "renewal_date"
When the wait step is processed
Then the scheduled_at timestamp is resolved from the contact field
And a wait execution record is created with status "scheduled"
```

---

#### Scenario: AC-008 - Handle past date gracefully

```gherkin
Given a workflow execution is active
And the current date is "2026-01-26"
And the execution reaches a wait step configured to wait until "2026-01-01"
When the wait step is processed
Then the workflow execution continues immediately
And a warning is logged indicating "Target date is in the past"
And the wait execution status is set to "resumed"
And the resumed_by field is set to "past_date"
```

---

#### Scenario: AC-009 - Validate date more than 1 year in future

```gherkin
Given a workflow execution is active
And the current date is "2026-01-26"
And a wait step is configured to wait until "2028-01-26"
When the wait step creation is attempted
Then the request is rejected with validation error
And the error message indicates "Maximum future date is 1 year"
```

---

### Feature: Wait Until Time of Day

#### Scenario: AC-010 - Wait until specific time in contact timezone

```gherkin
Given a workflow execution is active for contact "david@example.com"
And the contact has timezone "America/New_York"
And the current time in New York is "2026-01-26 14:00:00" (2:00 PM)
And the execution reaches a wait step configured for 09:00 AM
When the wait step is processed
Then the scheduled_at is calculated for the next day at 09:00 AM New York time
And the scheduled_at is stored as UTC equivalent "2026-01-27 14:00:00 UTC"
And a wait execution record is created with status "scheduled"
```

**Test Data:**
- Target time: 09:00
- Contact timezone: America/New_York
- Current time (NY): 2026-01-26 14:00 EST
- Expected scheduled_at: 2026-01-27 14:00 UTC (09:00 EST)

---

#### Scenario: AC-011 - Wait until time today if not yet passed

```gherkin
Given a workflow execution is active for contact "emma@example.com"
And the contact has timezone "Europe/London"
And the current time in London is "2026-01-26 08:00:00"
And the execution reaches a wait step configured for 14:00 (2:00 PM)
When the wait step is processed
Then the scheduled_at is calculated for today at 14:00 London time
And the scheduled_at is stored as UTC equivalent
And a wait execution record is created with status "scheduled"
```

---

#### Scenario: AC-012 - Wait until time on specific weekdays only

```gherkin
Given a workflow execution is active for contact "frank@example.com"
And the contact has timezone "America/Los_Angeles"
And the current day is Friday 2026-01-26
And the execution reaches a wait step configured for 10:00 AM on Monday only
When the wait step is processed
Then the scheduled_at is calculated for Monday 2026-01-29 at 10:00 AM Pacific
And a wait execution record is created with status "scheduled"
```

**Test Data:**
- Target time: 10:00
- Allowed days: ["monday"]
- Current day: Friday
- Expected next occurrence: Monday

---

#### Scenario: AC-013 - Handle DST transition correctly

```gherkin
Given a workflow execution is active for contact "grace@example.com"
And the contact has timezone "America/New_York"
And the current date is "2026-03-07" (before DST spring forward on March 8)
And the execution reaches a wait step configured for 02:30 AM on March 8
When the wait step is processed
Then the scheduled_at handles the DST transition correctly
And 02:30 AM which does not exist is adjusted to 03:00 AM
And the scheduled_at is stored as the correct UTC equivalent
```

---

#### Scenario: AC-014 - Fallback to UTC when no timezone specified

```gherkin
Given a workflow execution is active for contact "henry@example.com"
And the contact has no timezone set
And the account has no default timezone set
And the execution reaches a wait step configured for 15:00
When the wait step is processed
Then the timezone defaults to UTC
And the scheduled_at is calculated using UTC
```

---

### Feature: Wait for Event

#### Scenario: AC-015 - Wait for email open event

```gherkin
Given a workflow execution is active for contact "ivan@example.com"
And the previous step sent an email with tracking ID "email-123"
And the execution reaches a wait step configured to wait for "email_open"
And the timeout is configured for 72 hours
When the wait step is processed
Then an event listener is registered for "email_open" event
And the listener is associated with contact "ivan@example.com"
And the listener expires at current time plus 72 hours
And a wait execution record is created with status "waiting"
And the event_type is set to "email_open"
```

---

#### Scenario: AC-016 - Resume on matching event received

```gherkin
Given a wait step is waiting for "email_open" event for contact "julia@example.com"
And the wait execution status is "waiting"
When an "email_open" event is received for contact "julia@example.com"
Then the event listener matches the incoming event
And the workflow execution is resumed immediately
And the wait execution status is updated to "resumed"
And the resumed_by field is set to "event"
And the event listener is cleaned up
```

---

#### Scenario: AC-017 - Wait for email click event

```gherkin
Given a workflow execution is active for contact "kevin@example.com"
And the previous step sent an email with links
And the execution reaches a wait step configured to wait for "email_click"
When the wait step is processed
Then an event listener is registered for "email_click" event
And the listener is associated with the workflow execution
```

---

#### Scenario: AC-018 - Wait for SMS reply event

```gherkin
Given a workflow execution is active for contact "laura@example.com"
And the previous step sent an SMS message
And the execution reaches a wait step configured to wait for "sms_reply"
And the timeout is configured for 48 hours
When the wait step is processed
Then an event listener is registered for "sms_reply" event
And the listener includes the contact's phone number for matching
```

---

#### Scenario: AC-019 - Handle event timeout - continue workflow

```gherkin
Given a wait step is waiting for "email_open" event for contact "mike@example.com"
And the timeout is configured for 24 hours
And the timeout_action is "continue"
And 24 hours have passed without the event occurring
When the timeout job is processed
Then the workflow execution is resumed from the next step
And the wait execution status is updated to "timeout"
And the resumed_by field is set to "timeout"
And the event listener is cleaned up
```

---

#### Scenario: AC-020 - Handle event timeout - exit workflow

```gherkin
Given a wait step is waiting for "email_click" event for contact "nina@example.com"
And the timeout is configured for 72 hours
And the timeout_action is "exit"
And 72 hours have passed without the event occurring
When the timeout job is processed
Then the workflow execution is terminated
And the wait execution status is updated to "timeout"
And the execution status is set to "exited"
And the exit reason is recorded as "wait_timeout"
```

---

#### Scenario: AC-021 - Multiple workflows waiting for same event

```gherkin
Given workflow execution A is waiting for "form_submit" event for contact "oscar@example.com"
And workflow execution B is also waiting for "form_submit" event for contact "oscar@example.com"
When a "form_submit" event is received for contact "oscar@example.com"
Then both workflow executions A and B are resumed
And both wait execution records are updated to "resumed"
```

---

### Feature: Wait Step Cancellation

#### Scenario: AC-022 - Cancel wait step manually

```gherkin
Given a wait step execution exists with status "scheduled"
And the scheduled_at is in the future
When a cancellation request is received for the wait step
Then the wait execution status is updated to "cancelled"
And the scheduled job is removed from Redis
And the workflow execution remains paused
And a cancellation event is logged
```

---

#### Scenario: AC-023 - Cancel all waits when workflow is deactivated

```gherkin
Given a workflow has 10 active executions with wait steps
And the workflow status is changed to "paused"
When the workflow deactivation is processed
Then all pending wait executions are cancelled
And all scheduled jobs are removed
And all event listeners are cleaned up
```

---

#### Scenario: AC-024 - Cancel wait on contact opt-out

```gherkin
Given a wait step execution exists for contact "paul@example.com"
When the contact "paul@example.com" opts out of communications
Then all pending wait executions for this contact are cancelled
And all event listeners for this contact are cleaned up
```

---

#### Scenario: AC-025 - Cancel wait on goal achievement

```gherkin
Given a workflow execution is active with goal "appointment_booked"
And a wait step execution exists with status "scheduled"
When the contact achieves the goal by booking an appointment
Then the wait execution is cancelled
And the scheduled job is removed
And the workflow exits with status "goal_achieved"
```

---

### Feature: Wait State Persistence

#### Scenario: AC-026 - Persist wait state to database

```gherkin
Given a wait step is created for a workflow execution
When the wait step is persisted
Then all wait configuration is stored in the database
And the scheduled_at timestamp is stored in UTC
And the wait_config JSONB contains all configuration details
And the record includes created_at and updated_at timestamps
```

---

#### Scenario: AC-027 - Recover wait state after application restart

```gherkin
Given wait step executions exist in the database with status "scheduled"
And the scheduled_at times are in the past (missed during downtime)
When the application starts up
Then the scheduler recovery job identifies missed wait steps
And the missed wait steps are processed immediately
And the workflow executions are resumed
```

---

#### Scenario: AC-028 - Idempotent wait step processing

```gherkin
Given a wait step execution with status "scheduled"
When the scheduler processes the same wait step twice simultaneously
Then only one resume action is executed
And the second attempt recognizes the step is already resumed
And no duplicate workflow actions occur
```

---

### Feature: Wait Step Monitoring

#### Scenario: AC-029 - Query pending wait steps by type

```gherkin
Given 100 wait step executions exist in the system
And 30 are of type "fixed_time"
And 50 are of type "for_event"
And 20 are of type "until_date"
When an admin queries pending waits filtered by type "for_event"
Then the response includes 50 wait executions
And each execution includes status, contact, and workflow information
```

---

#### Scenario: AC-030 - View overdue wait steps

```gherkin
Given wait step executions exist with scheduled_at in the past
And these executions have not been processed
When an admin views the overdue waits dashboard
Then the overdue wait steps are displayed
And each shows the overdue duration
And alerts are triggered for waits overdue by more than 5 minutes
```

---

### Feature: API Endpoints

#### Scenario: AC-031 - Create wait step via API

```gherkin
Given an authenticated user with workflow edit permission
And an active workflow execution exists
When a POST request is sent to /api/v1/workflows/{id}/executions/{id}/wait
With body:
  {
    "step_id": "wait_1",
    "wait_type": "fixed_time",
    "config": {
      "duration": 30,
      "unit": "minutes"
    }
  }
Then the response status is 201 Created
And the response includes the wait execution ID
And the response includes the scheduled_at timestamp
And the response includes status "scheduled"
```

---

#### Scenario: AC-032 - Get wait step status via API

```gherkin
Given a wait step execution exists with ID "wait-exec-123"
When a GET request is sent to /api/v1/workflows/executions/{id}/wait/{step_id}
Then the response status is 200 OK
And the response includes:
  - id: "wait-exec-123"
  - status: "scheduled"
  - wait_type: "fixed_time"
  - scheduled_at: ISO8601 timestamp
  - config: wait configuration object
```

---

#### Scenario: AC-033 - Cancel wait step via API

```gherkin
Given a wait step execution exists with status "scheduled"
When a DELETE request is sent to /api/v1/workflows/executions/{id}/wait/{step_id}
Then the response status is 200 OK
And the response includes success: true
And the wait execution status is updated to "cancelled"
```

---

#### Scenario: AC-034 - Validation error for invalid wait configuration

```gherkin
Given an authenticated user
When a POST request is sent to create a wait step
With invalid configuration:
  {
    "step_id": "wait_1",
    "wait_type": "fixed_time",
    "config": {
      "duration": -5,
      "unit": "minutes"
    }
  }
Then the response status is 422 Unprocessable Entity
And the response follows RFC 7807 Problem Details format
And the error detail indicates "duration must be a positive integer"
```

---

### Feature: Performance Requirements

#### Scenario: AC-035 - Schedule wait step within latency target

```gherkin
Given the system is under normal load
When 100 wait step creation requests are processed
Then 95% of requests complete within 100ms
And all requests complete within 500ms
And all scheduled jobs are registered in Redis
```

---

#### Scenario: AC-036 - Process scheduled resumes at scale

```gherkin
Given 1000 wait steps are scheduled to resume within the same minute
When the scheduler processes the scheduled jobs
Then all 1000 workflow executions are resumed within 60 seconds
And no jobs are lost or duplicated
And the system maintains stability
```

---

#### Scenario: AC-037 - Event matching performance

```gherkin
Given 10,000 active event listeners exist in the system
When an email_open event is received for a contact
Then the matching listener is found within 100ms
And the workflow execution is resumed promptly
```

---

## Test Matrix

### Unit Tests

| Test ID | Scenario | Priority |
|---------|----------|----------|
| test_fixed_time_minutes | AC-001 | Critical |
| test_fixed_time_days | AC-002 | Critical |
| test_fixed_time_weeks | AC-003 | High |
| test_resume_after_wait | AC-004 | Critical |
| test_max_duration_validation | AC-005 | High |
| test_until_date_future | AC-006 | Critical |
| test_until_date_contact_field | AC-007 | High |
| test_until_date_past | AC-008 | High |
| test_until_date_max_validation | AC-009 | Medium |
| test_time_of_day_contact_tz | AC-010 | Critical |
| test_time_of_day_same_day | AC-011 | High |
| test_time_of_day_weekdays | AC-012 | High |
| test_time_of_day_dst | AC-013 | High |
| test_time_of_day_fallback_utc | AC-014 | High |
| test_event_wait_email_open | AC-015 | Critical |
| test_event_resume_on_match | AC-016 | Critical |
| test_event_wait_email_click | AC-017 | High |
| test_event_wait_sms_reply | AC-018 | High |
| test_event_timeout_continue | AC-019 | Critical |
| test_event_timeout_exit | AC-020 | Critical |
| test_event_multiple_workflows | AC-021 | High |

### Integration Tests

| Test ID | Scenario | Priority |
|---------|----------|----------|
| test_cancel_wait_manual | AC-022 | High |
| test_cancel_workflow_deactivation | AC-023 | High |
| test_cancel_contact_optout | AC-024 | High |
| test_cancel_goal_achieved | AC-025 | High |
| test_state_persistence | AC-026 | Critical |
| test_state_recovery | AC-027 | Critical |
| test_idempotent_processing | AC-028 | Critical |
| test_query_by_type | AC-029 | Medium |
| test_overdue_monitoring | AC-030 | Medium |

### API Tests

| Test ID | Scenario | Priority |
|---------|----------|----------|
| test_api_create_wait | AC-031 | Critical |
| test_api_get_status | AC-032 | High |
| test_api_cancel_wait | AC-033 | High |
| test_api_validation_error | AC-034 | High |

### Performance Tests

| Test ID | Scenario | Priority |
|---------|----------|----------|
| test_perf_scheduling_latency | AC-035 | High |
| test_perf_bulk_resume | AC-036 | High |
| test_perf_event_matching | AC-037 | High |

---

## Definition of Done

### Code Complete

- [ ] All EARS requirements implemented (REQ-001 through REQ-010)
- [ ] All acceptance criteria passing (AC-001 through AC-037)
- [ ] Code reviewed and approved
- [ ] No critical or high severity bugs

### Test Complete

- [ ] Unit test coverage >= 85%
- [ ] All integration tests passing
- [ ] All API tests passing
- [ ] Performance benchmarks met

### Documentation Complete

- [ ] API documentation updated (OpenAPI)
- [ ] Architecture documentation updated
- [ ] Runbook created for operations

### Deployment Ready

- [ ] Database migrations reviewed
- [ ] Redis configuration verified
- [ ] Celery workers scaled appropriately
- [ ] Monitoring dashboards configured
- [ ] Alerts configured for overdue waits

---

## Traceability

| Artifact | Reference |
|----------|-----------|
| SPEC Document | .moai/specs/SPEC-WFL-006/spec.md |
| Implementation Plan | .moai/specs/SPEC-WFL-006/plan.md |
| Parent Plan | specs/workflows/plan.md |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-26 | manager-spec | Initial acceptance criteria |
