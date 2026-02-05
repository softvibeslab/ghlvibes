# SPEC-WFL-005: Execute Workflow - Acceptance Criteria

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-005 |
| **Title** | Execute Workflow - Acceptance Criteria |
| **Created** | 2026-01-26 |
| **Status** | Planned |

---

## Overview

This document defines the acceptance criteria for the Workflow Execution Engine using Given-When-Then (Gherkin) format. All criteria must pass for the SPEC to be considered complete.

---

## Feature: Workflow Execution Initiation

### Scenario: Successfully trigger workflow execution

```gherkin
Given a workflow "Welcome Sequence" exists with status "active"
And a contact "john@example.com" exists with opted_in status "true"
And the contact has not been enrolled in this workflow before
When a trigger event occurs for the contact
Then an execution record should be created with status "QUEUED"
And the execution should have a unique execution_id
And the first action should be enqueued in Redis
And an execution_started event should be logged
```

### Scenario: Prevent execution for opted-out contact

```gherkin
Given a workflow "Marketing Campaign" exists with status "active"
And a contact "jane@example.com" exists with opted_in status "false"
When a trigger event occurs for the contact
Then no execution record should be created
And an opt_out_blocked event should be logged
And the API should return status 403 with message "Contact has opted out"
```

### Scenario: Prevent duplicate execution within deduplication window

```gherkin
Given a workflow "Lead Nurture" exists with status "active"
And a contact "bob@example.com" has an active execution for this workflow
And the execution started less than 5 seconds ago
When the same trigger event occurs again
Then no new execution should be created
And the response should indicate "duplicate trigger ignored"
And a deduplication_blocked event should be logged
```

### Scenario: Handle inactive workflow trigger

```gherkin
Given a workflow "Old Campaign" exists with status "paused"
And a contact "alice@example.com" exists
When a trigger event occurs for the contact
Then no execution record should be created
And the API should return status 400 with message "Workflow is not active"
```

---

## Feature: Sequential Action Processing

### Scenario: Execute actions in correct sequence

```gherkin
Given an active execution for workflow with actions:
  | step | action_type | delay |
  | 1    | send_email  | 0     |
  | 2    | add_tag     | 0     |
  | 3    | send_sms    | 0     |
And the execution is at step 1
When the worker processes the execution
Then actions should be executed in order: send_email, add_tag, send_sms
And each action should have a log entry with status "SUCCESS"
And the execution should complete with status "COMPLETED"
```

### Scenario: Handle conditional branching

```gherkin
Given an active execution for workflow with a condition at step 2
And the condition checks "contact has tag 'VIP'"
And the contact does have the tag "VIP"
When the worker processes step 2
Then the execution should follow the "true" branch
And the execution log should record "condition_evaluated: true"
And the next step should be from the "true" branch
```

### Scenario: Process wait step correctly

```gherkin
Given an active execution at a wait step
And the wait step is configured for "2 hours"
When the worker processes the wait step
Then the execution status should change to "PAUSED"
And a scheduled resume job should be created for 2 hours later
And the execution log should record "wait_started" event
```

---

## Feature: Error Handling and Retry Logic

### Scenario: Retry action on transient error

```gherkin
Given an active execution at step 1 (send_email action)
And the email service returns a 503 error
And retry_count is 0
And max_retry_attempts is 3
When the worker processes the action
Then the action should be marked as "FAILED" temporarily
And retry_count should be incremented to 1
And a retry should be scheduled with 60 second delay
And the execution log should record the error details
```

### Scenario: Exponential backoff on repeated failures

```gherkin
Given an active execution that has failed 2 times
And retry_count is 2
And retry_base_delay_seconds is 60
When the third retry is scheduled
Then the delay should be 240 seconds (60 * 2^2)
And the job should be enqueued with the calculated delay
```

### Scenario: Mark execution as failed after max retries

```gherkin
Given an active execution at step 1
And retry_count equals max_retry_attempts (3)
And the action fails again
When the worker processes the action
Then the execution status should change to "FAILED"
And an error notification should be sent to the account admin
And the execution log should record "max_retries_exhausted"
And no further retries should be scheduled
```

### Scenario: Handle non-retryable error

```gherkin
Given an active execution at step 1 (send_email action)
And the email service returns a 400 error (invalid email format)
When the worker processes the action
Then the action should be marked as "FAILED"
And no retry should be scheduled
And the execution should continue to the next step
And the execution log should record "skipped_non_retryable_error"
```

### Scenario: Send error notification on failure

```gherkin
Given an execution that has just been marked as "FAILED"
And error_notification is enabled for the account
When the failure is processed
Then an email notification should be sent to the account admin
And the notification should include execution_id, workflow_name, and error_message
And the notification_sent event should be logged
```

---

## Feature: Execution State Management

### Scenario: Persist state after each action

```gherkin
Given an active execution processing action at step 3
When the action completes successfully
Then the database should record:
  | field              | value    |
  | current_step_index | 4        |
  | updated_at         | now()    |
And the execution log should have a new entry for step 3
And the next action should be enqueued
```

### Scenario: Recover execution after worker crash

```gherkin
Given an execution in "ACTIVE" status
And the execution was at step 5
And the worker processing it crashed
When a new worker picks up the execution
Then the execution should resume from step 5
And no duplicate actions should be executed
And the recovery should be logged
```

### Scenario: Cancel active execution

```gherkin
Given an active execution at step 3 of 10
When an admin calls POST /executions/{id}/cancel
Then the execution status should change to "CANCELLED"
And all pending queue jobs for this execution should be removed
And no further actions should be executed
And the cancellation should be logged with admin user_id
```

### Scenario: Handle contact deletion during execution

```gherkin
Given an active execution for contact "deleted@example.com"
And the contact is deleted while execution is in progress
When the worker tries to process the next action
Then the execution should be marked as "CANCELLED"
And the reason should be "contact_deleted"
And no error notification should be sent
```

---

## Feature: Rate Limiting and Throttling

### Scenario: Enforce account concurrent execution limit

```gherkin
Given an account has 100 active executions
And concurrent_executions_per_account is set to 100
When a new execution is triggered for the account
Then the execution should be created with status "QUEUED"
And the execution should be placed in a waiting queue
And processing should begin when an active execution completes
```

### Scenario: Respect external API rate limits

```gherkin
Given an action that calls an external API
And the API returns a 429 error with Retry-After: 30
When the worker processes the response
Then the action should be retried after 30 seconds
And the rate_limit_hit event should be logged
And subsequent actions to this API should be delayed
```

---

## Feature: Execution Logging and Audit

### Scenario: Log all execution events

```gherkin
Given a workflow execution completes successfully
Then the execution_logs table should contain entries for:
  | event_type          |
  | execution_started   |
  | action_started (x3) |
  | action_completed(x3)|
  | execution_completed |
And each log entry should have:
  | field         | requirement           |
  | execution_id  | matches execution     |
  | timestamp     | accurate to 1 second  |
  | step_index    | correct step number   |
  | duration_ms   | actual duration       |
```

### Scenario: Mask sensitive data in logs

```gherkin
Given an email action with content containing personal data
When the action is logged
Then the action_config should NOT contain plaintext PII
And email addresses should be partially masked
And any API keys should be completely redacted
```

---

## Feature: API Endpoints

### Scenario: Get execution status

```gherkin
Given an execution with id "abc-123" exists
And the execution is at step 3 of 5 with status "ACTIVE"
When GET /api/v1/executions/abc-123 is called
Then the response status should be 200
And the response body should contain:
  | field              | value   |
  | id                 | abc-123 |
  | status             | ACTIVE  |
  | current_step_index | 3       |
  | total_steps        | 5       |
  | progress_percent   | 60      |
```

### Scenario: Get execution logs with pagination

```gherkin
Given an execution with 50 log entries
When GET /api/v1/executions/{id}/logs?page=1&limit=10 is called
Then the response should contain 10 log entries
And the response should include pagination metadata:
  | field       | value |
  | total       | 50    |
  | page        | 1     |
  | limit       | 10    |
  | total_pages | 5     |
```

### Scenario: Retry failed execution

```gherkin
Given an execution with status "FAILED"
And retry_count is 3
When POST /api/v1/executions/{id}/retry is called
Then the execution status should change to "QUEUED"
And retry_count should be reset to 0
And the execution should resume from the failed step
And the manual_retry event should be logged
```

### Scenario: List executions with filters

```gherkin
Given multiple executions exist for a workflow
When GET /api/v1/workflows/{id}/executions?status=FAILED&from=2026-01-01 is called
Then only executions matching the filters should be returned
And results should be sorted by created_at descending
And pagination should be applied
```

---

## Feature: Goal Tracking

### Scenario: Exit workflow on goal achievement

```gherkin
Given an active execution for a workflow with goal "appointment_booked"
And the execution is at step 5 of 10
When the contact books an appointment
Then the execution should be marked as "COMPLETED"
And the completion_reason should be "goal_achieved"
And remaining steps should not be executed
And the goal_achieved event should be logged
```

---

## Quality Gate Criteria

### Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| Action execution time (P95) | < 500ms | Prometheus histogram |
| Queue processing latency | < 1 second | Queue metrics |
| API response time (P95) | < 200ms | API metrics |
| Concurrent executions | 10,000+ | Load test |

### Reliability Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| Execution success rate | > 99% | Success/Total ratio |
| Recovery success rate | 100% | Crash test validation |
| Data consistency | 100% | State validation checks |

### Test Coverage Requirements

| Category | Target | Measurement |
|----------|--------|-------------|
| Unit test coverage | > 85% | pytest-cov |
| Integration test coverage | > 80% | pytest-cov |
| Critical path coverage | 100% | Manual review |

---

## Definition of Done

- [ ] All acceptance criteria scenarios pass
- [ ] Unit test coverage > 85%
- [ ] Integration tests pass for all API endpoints
- [ ] Load tests pass with 10,000 concurrent executions
- [ ] Error handling covers all identified error types
- [ ] Logging captures all required events
- [ ] Monitoring dashboards configured
- [ ] Alert rules configured and tested
- [ ] API documentation updated (OpenAPI spec)
- [ ] Security review completed
- [ ] Code review approved by 2 reviewers
- [ ] No critical or high severity bugs open
- [ ] Performance benchmarks met

---

## Traceability

| Test Scenario | Requirement ID | Priority |
|---------------|----------------|----------|
| Trigger workflow execution | REQ-E1 | Critical |
| Prevent opted-out execution | REQ-N1 | Critical |
| Prevent duplicate execution | REQ-N4 | High |
| Sequential action processing | REQ-E2 | Critical |
| Retry on transient error | REQ-E3 | Critical |
| Max retries exhausted | REQ-E4 | Critical |
| State persistence | REQ-U3 | Critical |
| Worker crash recovery | REQ-U3 | Critical |
| Rate limiting | REQ-U4 | High |
| Execution logging | REQ-U1 | High |
| Sensitive data masking | REQ-N3 | Critical |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-26 | manager-spec | Initial acceptance criteria |
