# SPEC-WFL-011: Acceptance Criteria

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-011 |
| **Title** | Bulk Enrollment |
| **Module** | workflows |
| **Domain** | automation |
| **Priority** | Medium |

---

## Test Scenarios

### Feature: Bulk Enrollment Job Creation

#### Scenario: AC-001 - Create Bulk Enrollment with Manual Selection

```gherkin
Given a user with "workflow:manage" permission
  And a workflow with ID "wfl_123" exists and is active
  And 500 valid contact IDs are provided
When the user creates a bulk enrollment job
Then the system shall return HTTP 201 Created
  And the response shall include a job_id
  And the job status shall be "pending"
  And the total_contacts shall be 500
```

#### Scenario: AC-002 - Create Bulk Enrollment with Filter Selection

```gherkin
Given a user with "workflow:manage" permission
  And a workflow with ID "wfl_123" exists and is active
  And a filter criteria {"tags": ["lead"], "created_after": "2026-01-01"}
When the user creates a bulk enrollment job with filter selection
Then the system shall resolve the filter to matching contact IDs
  And create a job with the resolved contacts
  And the selection_type shall be "filter"
```

#### Scenario: AC-003 - Create Bulk Enrollment with CSV Upload

```gherkin
Given a user uploads a CSV file with 1000 email addresses
  And 950 emails match existing contacts
  And 50 emails do not match any contacts
When the user creates a bulk enrollment job with CSV selection
Then the system shall create a job with 950 contacts
  And the response shall include unmatched_count of 50
  And the unmatched emails shall be available for download
```

#### Scenario: AC-004 - Reject Bulk Enrollment Exceeding Limit

```gherkin
Given a user provides 15,000 contact IDs
  And the maximum limit is 10,000 contacts
When the user attempts to create a bulk enrollment job
Then the system shall return HTTP 400 Bad Request
  And the error message shall indicate the maximum limit exceeded
  And no job shall be created
```

#### Scenario: AC-005 - Reject Bulk Enrollment for Inactive Workflow

```gherkin
Given a workflow with status "draft" or "paused"
When the user attempts to create a bulk enrollment job
Then the system shall return HTTP 400 Bad Request
  And the error message shall indicate workflow must be active
```

---

### Feature: Contact Validation

#### Scenario: AC-006 - Validate Contact Exists

```gherkin
Given a bulk enrollment job with 100 contact IDs
  And 95 contacts exist in the database
  And 5 contact IDs do not exist
When the validation phase runs
Then 5 contacts shall be marked as "CONTACT_NOT_FOUND"
  And these contacts shall be skipped during enrollment
  And the skipped_count shall include these 5 contacts
```

#### Scenario: AC-007 - Validate Contact Not Already Enrolled

```gherkin
Given a bulk enrollment job for workflow "wfl_123"
  And contact "ctc_456" is already enrolled in "wfl_123"
When the validation phase runs
Then contact "ctc_456" shall be marked as "already_enrolled"
  And shall be skipped without error
  And the skipped_count shall be incremented
```

#### Scenario: AC-008 - Validate Contact Not Blocked

```gherkin
Given a bulk enrollment job
  And contact "ctc_789" has status "unsubscribed"
  And skip_unsubscribed option is true
When the validation phase runs
Then contact "ctc_789" shall be marked as "CONTACT_BLOCKED"
  And shall be skipped during enrollment
```

#### Scenario: AC-009 - Validate All Contacts Eligible

```gherkin
Given a bulk enrollment job with 1000 contacts
  And all contacts exist and are eligible
When the validation phase completes
Then the job status shall change to "queued"
  And total_batches shall be 10 (1000 / 100)
```

---

### Feature: Batch Processing

#### Scenario: AC-010 - Process Batch Successfully

```gherkin
Given a queued bulk enrollment job
  And batch 1 contains 100 valid contacts
When the batch processor picks up batch 1
Then all 100 contacts shall be enrolled in the workflow
  And the batch status shall be "completed"
  And the job processed_count shall increase by 100
  And the success_count shall increase by 100
```

#### Scenario: AC-011 - Handle Partial Batch Failure

```gherkin
Given a batch with 100 contacts
  And 95 contacts enroll successfully
  And 5 contacts fail due to workflow errors
When the batch is processed
Then the batch shall complete with status "completed"
  And success_count shall increase by 95
  And failure_count shall increase by 5
  And failure details shall be recorded
  And processing shall continue to next batch
```

#### Scenario: AC-012 - Retry Failed Batch

```gherkin
Given a batch that fails entirely due to database timeout
  And retry is enabled with max_attempts = 3
When the batch fails on first attempt
Then the system shall wait 10 seconds
  And retry the batch
  And attempt_count shall be 2
When the retry succeeds
Then the batch status shall be "completed"
```

#### Scenario: AC-013 - Exhaust Batch Retries

```gherkin
Given a batch that fails on all 3 retry attempts
When all retries are exhausted
Then the batch status shall be "failed"
  And the job shall continue with remaining batches
  And an alert shall be logged for investigation
```

#### Scenario: AC-014 - Process Batches in Order

```gherkin
Given a job with 5 batches
When the job processes
Then batches shall complete in order: 1, 2, 3, 4, 5
  And progress shall update after each batch
  And current_batch shall reflect the active batch number
```

---

### Feature: Progress Tracking

#### Scenario: AC-015 - Real-Time Progress Updates

```gherkin
Given a bulk enrollment job is processing
  And a client is connected via WebSocket
When a batch completes
Then the client shall receive a progress update within 100ms
  And the update shall include:
    | field                    | description                 |
    | processed                | Total contacts processed    |
    | success                  | Successful enrollments      |
    | failed                   | Failed enrollments          |
    | progress_percentage      | Completion percentage       |
    | current_batch            | Current batch number        |
    | estimated_time_remaining | Seconds remaining           |
```

#### Scenario: AC-016 - Calculate Progress Percentage

```gherkin
Given a job with 500 total contacts
  And 250 contacts have been processed
When progress is calculated
Then progress_percentage shall be 50.0
  And the calculation shall be (processed / total) * 100
```

#### Scenario: AC-017 - Estimate Time Remaining

```gherkin
Given a job that has processed 100 contacts in 60 seconds
  And 400 contacts remain
When estimated_time_remaining is calculated
Then the estimate shall be approximately 240 seconds
  And the rate shall be approximately 1.67 contacts/second
```

#### Scenario: AC-018 - Progress API Endpoint

```gherkin
Given a processing bulk enrollment job with ID "job_123"
When the user calls GET /api/v1/bulk-enrollment-jobs/job_123/progress
Then the response shall include:
    | field                          | type    |
    | job_id                         | UUID    |
    | status                         | string  |
    | total_contacts                 | integer |
    | processed                      | integer |
    | success                        | integer |
    | failed                         | integer |
    | progress_percentage            | float   |
    | rate                           | float   |
    | estimated_time_remaining_seconds | integer |
```

---

### Feature: Job Completion

#### Scenario: AC-019 - Complete Job Successfully

```gherkin
Given all batches in a job have completed
  And success_count equals total_contacts
When the job finalizes
Then the job status shall be "completed"
  And completed_at timestamp shall be set
  And a completion notification shall be sent
```

#### Scenario: AC-020 - Complete Job with Partial Errors

```gherkin
Given all batches in a job have completed
  And success_count is 980
  And failure_count is 20
When the job finalizes
Then the job status shall be "completed_with_errors"
  And completed_at timestamp shall be set
  And failure report shall be available
```

#### Scenario: AC-021 - Completion Notification Email

```gherkin
Given a job with notify_on_completion enabled
  And notification_email is "admin@example.com"
When the job completes
Then an email shall be sent to "admin@example.com"
  And the email shall include:
    | content              |
    | Job ID               |
    | Workflow name        |
    | Total enrolled       |
    | Success count        |
    | Failure count        |
    | Processing duration  |
```

---

### Feature: Job Cancellation

#### Scenario: AC-022 - Cancel Processing Job

```gherkin
Given a bulk enrollment job with status "processing"
  And 3 of 10 batches have completed
When the user requests cancellation
Then the job status shall change to "cancelling"
  And the current batch shall complete
  And remaining batches shall be skipped
  And final status shall be "cancelled"
```

#### Scenario: AC-023 - Cancel Pending Job

```gherkin
Given a bulk enrollment job with status "pending"
When the user requests cancellation
Then the job status shall change to "cancelled" immediately
  And no contacts shall be enrolled
```

#### Scenario: AC-024 - Cannot Cancel Completed Job

```gherkin
Given a bulk enrollment job with status "completed"
When the user requests cancellation
Then the system shall return HTTP 400 Bad Request
  And the error message shall indicate job already completed
```

---

### Feature: Rate Limiting

#### Scenario: AC-025 - Enforce Per-Account Rate Limit

```gherkin
Given an account with rate limit of 500 enrollments/minute
  And the account has already enrolled 490 contacts this minute
When the next batch of 100 contacts starts processing
Then the system shall throttle processing
  And only 10 contacts shall enroll in the current minute
  And remaining 90 shall process after the rate window resets
```

#### Scenario: AC-026 - Concurrent Job Limit

```gherkin
Given an account already has 10 pending or processing bulk jobs
When the user attempts to create another bulk job
Then the system shall return HTTP 429 Too Many Requests
  And the error message shall indicate maximum concurrent jobs reached
```

---

### Feature: Failure Handling

#### Scenario: AC-027 - List Enrollment Failures

```gherkin
Given a completed job with 50 failures
When the user calls GET /api/v1/bulk-enrollment-jobs/{id}/failures
Then the response shall include paginated failure records
  And each record shall include:
    | field          | description             |
    | contact_id     | Failed contact ID       |
    | contact_email  | Contact email if available |
    | error_code     | Standardized error code |
    | error_message  | Human-readable message  |
    | batch_number   | Batch where failure occurred |
```

#### Scenario: AC-028 - Retry Failed Contacts

```gherkin
Given a completed job with 30 failed contacts
  And the failures were due to transient errors
When the user calls POST /api/v1/bulk-enrollment-jobs/{id}/retry-failures
Then a new job shall be created with only the failed contacts
  And the new job shall reference the original job
```

---

### Feature: Dry Run Mode

#### Scenario: AC-029 - Execute Dry Run

```gherkin
Given a user wants to preview a bulk enrollment
  And provides 500 contact IDs
When the user calls POST /api/v1/workflows/{id}/bulk-enrollment/dry-run
Then the system shall validate all contacts without enrolling
  And the response shall include:
    | field                   | description                     |
    | total_contacts          | Total contacts provided         |
    | eligible_count          | Contacts that would be enrolled |
    | already_enrolled_count  | Already in workflow             |
    | invalid_count           | Invalid or blocked contacts     |
    | estimated_duration      | Estimated processing time       |
```

#### Scenario: AC-030 - Dry Run Does Not Modify Data

```gherkin
Given a dry run is executed
When the dry run completes
Then no workflow executions shall be created
  And no contact data shall be modified
  And no job record shall be created
```

---

### Feature: Enrollment Source Tracking

#### Scenario: AC-031 - Track Bulk Enrollment Source

```gherkin
Given a contact is enrolled via bulk enrollment job "job_123"
When the workflow execution is created
Then the enrollment_source shall be "bulk_enrollment"
  And the enrollment_source_id shall be "job_123"
  And this information shall be visible in contact activity
```

---

### Feature: Job History

#### Scenario: AC-032 - List Job History

```gherkin
Given an account has 50 bulk enrollment jobs in history
When the user calls GET /api/v1/bulk-enrollment-jobs?limit=10
Then the response shall include 10 most recent jobs
  And pagination metadata shall be included
  And jobs shall be sorted by created_at descending
```

#### Scenario: AC-033 - Filter Job History by Status

```gherkin
Given an account has jobs with various statuses
When the user calls GET /api/v1/bulk-enrollment-jobs?status=completed
Then only jobs with status "completed" shall be returned
```

#### Scenario: AC-034 - Get Job Details

```gherkin
Given a bulk enrollment job with ID "job_456"
When the user calls GET /api/v1/bulk-enrollment-jobs/job_456
Then the response shall include complete job information:
    | field              | description                    |
    | id                 | Job UUID                       |
    | workflow_id        | Target workflow ID             |
    | workflow_name      | Target workflow name           |
    | status             | Current job status             |
    | selection_type     | manual, filter, or csv         |
    | total_contacts     | Total contacts in job          |
    | processed_count    | Contacts processed so far      |
    | success_count      | Successful enrollments         |
    | failure_count      | Failed enrollments             |
    | skipped_count      | Skipped contacts               |
    | created_at         | Job creation timestamp         |
    | started_at         | Processing start timestamp     |
    | completed_at       | Completion timestamp           |
```

---

## Quality Gates

### Coverage Requirements

- [ ] All scenarios have automated tests
- [ ] Unit test coverage >= 85%
- [ ] Integration test coverage >= 80%
- [ ] End-to-end tests for critical paths
- [ ] Load tests for 10,000 contact jobs

### Performance Requirements

- [ ] Job creation response < 500ms
- [ ] Batch processing rate >= 100 contacts/second
- [ ] Progress updates delivered < 100ms
- [ ] 10,000 contact job completes < 15 minutes
- [ ] No memory leaks under sustained load

### Reliability Requirements

- [ ] Partial failures do not stop job processing
- [ ] Batch retries recover from transient errors
- [ ] Job cancellation is graceful and consistent
- [ ] Rate limiting protects system stability

### Security Requirements

- [ ] Permission checks enforced on all endpoints
- [ ] Contact ownership validated
- [ ] CSV files scanned for malicious content
- [ ] Rate limiting prevents abuse

---

## Traceability Matrix

| Acceptance Criteria | EARS Requirement | Test File |
|---------------------|------------------|-----------|
| AC-001 to AC-005 | REQ-001, REQ-002, REQ-004 | test_bulk_enrollment_creation.py |
| AC-006 to AC-009 | REQ-002, REQ-009 | test_contact_validation.py |
| AC-010 to AC-014 | REQ-003, REQ-005, REQ-011 | test_batch_processing.py |
| AC-015 to AC-018 | REQ-006, REQ-007 | test_progress_tracking.py |
| AC-019 to AC-021 | REQ-012 | test_job_completion.py |
| AC-022 to AC-024 | REQ-013 | test_job_cancellation.py |
| AC-025, AC-026 | REQ-004, REQ-014 | test_rate_limiting.py |
| AC-027, AC-028 | REQ-010 | test_failure_handling.py |
| AC-029, AC-030 | REQ-020 | test_dry_run.py |
| AC-031 | REQ-016 | test_enrollment_tracking.py |
| AC-032 to AC-034 | REQ-015 | test_job_history.py |

---

## Definition of Done

1. All acceptance criteria tests passing
2. Code review approved
3. Security review completed
4. Performance benchmarks met
5. Load testing completed
6. Documentation updated
7. Deployed to staging
8. Product owner sign-off

---

## Traceability

| Tag | Reference |
|-----|-----------|
| SPEC-WFL-011 | Parent specification |
| ACC-WFL-011 | This acceptance criteria |
