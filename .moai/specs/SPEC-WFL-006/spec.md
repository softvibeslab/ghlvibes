# SPEC-WFL-006: Wait Step Processing

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-006 |
| **Title** | Wait Step Processing |
| **Module** | workflows |
| **Domain** | automation |
| **Priority** | High |
| **Status** | Planned |
| **Created** | 2026-01-26 |
| **Version** | 1.0.0 |

## Skills Required

- moai-lang-python
- moai-lang-typescript
- moai-domain-database
- moai-platform-supabase

---

## Overview

The Wait Step Processing feature enables workflow automation to pause execution at designated points and resume when specific conditions are met. This capability is essential for time-based nurturing sequences, event-driven automation, and scheduled communication delivery.

### Business Context

Marketing automation workflows require precise timing control to:
- Send follow-up messages at optimal intervals
- Coordinate multi-channel campaigns across time zones
- Wait for recipient engagement before proceeding
- Schedule actions for specific dates or times of day

---

## EARS Format Requirements

### REQ-001: Fixed Time Wait (Ubiquitous)

**Type:** Event-Driven

**EARS Statement:**
WHEN a workflow execution reaches a wait step configured with fixed time duration,
THEN the system shall calculate the resume timestamp, persist the execution state, and schedule a job to resume processing after the specified duration.

**Wait Duration Units:**
- Minutes: 1-59 minutes
- Hours: 1-23 hours
- Days: 1-30 days
- Weeks: 1-12 weeks

**Constraints:**
- Minimum wait duration: 1 minute
- Maximum wait duration: 12 weeks (84 days)
- Duration must be a positive integer
- System shall handle timezone-aware calculations

**Example Scenarios:**
- Wait 30 minutes before sending follow-up SMS
- Wait 3 days before checking email engagement
- Wait 1 week before sending re-engagement campaign

---

### REQ-002: Wait Until Specific Date (Event-Driven)

**Type:** Event-Driven

**EARS Statement:**
WHEN a workflow execution reaches a wait step configured to wait until a specific date,
THEN the system shall validate the target date is in the future, persist the execution state, and schedule a job to resume at the specified date and time.

**Configuration Options:**
- Absolute date and time (ISO 8601 format)
- Contact field reference (e.g., subscription_end_date)
- Calculated date (e.g., 7 days before anniversary)

**Constraints:**
- Target date must be in the future relative to execution time
- Past dates shall trigger immediate continuation with warning log
- Maximum future date: 1 year from current date
- Date validation shall account for leap years and month boundaries

**Example Scenarios:**
- Wait until contract renewal date
- Wait until membership expiration minus 14 days
- Wait until a specific campaign launch date

---

### REQ-003: Wait Until Time of Day (Event-Driven)

**Type:** Event-Driven

**EARS Statement:**
WHEN a workflow execution reaches a wait step configured to wait until a specific time of day,
THEN the system shall calculate the next occurrence of that time in the specified timezone, persist the execution state, and schedule a job to resume at that time.

**Configuration Options:**
- Target time (HH:MM format, 24-hour)
- Timezone selection (IANA timezone database)
- Day restrictions (specific weekdays, business days only)

**Timezone Handling:**
- Contact timezone (from contact profile)
- Account timezone (from account settings)
- Explicit timezone selection
- Fallback to UTC if no timezone specified

**Constraints:**
- If current time has passed target time today, schedule for next valid day
- Business days calculation excludes configured holidays
- DST transitions shall be handled correctly

**Example Scenarios:**
- Wait until 9:00 AM in contact's timezone
- Wait until next Monday at 10:00 AM
- Wait until next business day at 2:00 PM

---

### REQ-004: Wait for Event (Event-Driven)

**Type:** Event-Driven

**EARS Statement:**
WHEN a workflow execution reaches a wait step configured to wait for a specific event,
THEN the system shall register an event listener, persist the execution state, and resume processing when the event is received or timeout expires.

**Supported Events:**
- `email_open`: Recipient opened email from previous step
- `email_click`: Recipient clicked a link in previous email
- `sms_reply`: Recipient replied to SMS message
- `form_submit`: Contact submitted a specific form
- `page_visit`: Contact visited a specific page
- `appointment_booked`: Contact booked an appointment

**Event Correlation:**
- Events must correlate to the specific workflow execution
- Events must reference the correct contact
- Events must match the configured event type

**Timeout Configuration:**
- Default timeout: 7 days
- Minimum timeout: 1 hour
- Maximum timeout: 90 days
- Timeout action: Continue workflow or exit

**Constraints:**
- Event listeners shall be cleaned up after timeout
- Multiple events of same type shall trigger on first occurrence
- Event listeners shall survive system restarts

**Example Scenarios:**
- Wait up to 3 days for email to be opened, then send reminder
- Wait for click event with 24-hour timeout
- Wait for form submission before proceeding to onboarding sequence

---

### REQ-005: Wait State Persistence (Ubiquitous)

**Type:** Ubiquitous

**EARS Statement:**
The system shall persist all wait step execution states in a durable storage system to ensure workflow continuity across system restarts, deployments, and failures.

**State Data:**
- Workflow execution ID
- Contact ID
- Wait step ID
- Wait type and configuration
- Scheduled resume timestamp
- Event listener registrations
- Retry count and history

**Durability Requirements:**
- State must survive application restarts
- State must be recoverable after database failover
- State changes must be atomic

---

### REQ-006: Scheduled Job Processing (Ubiquitous)

**Type:** Ubiquitous

**EARS Statement:**
The system shall process scheduled resume jobs within 60 seconds of the target timestamp under normal operating conditions.

**Processing Characteristics:**
- Jobs shall be distributed across worker instances
- Job execution shall be idempotent
- Failed jobs shall retry with exponential backoff
- Job status shall be trackable

**Performance Targets:**
- P95 job execution latency: < 60 seconds from scheduled time
- P99 job execution latency: < 300 seconds from scheduled time
- Throughput: 1,000+ scheduled resumes per minute

---

### REQ-007: Event-Based Resume (Event-Driven)

**Type:** Event-Driven

**EARS Statement:**
WHEN a qualifying event is received that matches a registered wait-for-event listener,
THEN the system shall immediately resume the associated workflow execution and clean up the listener registration.

**Event Processing:**
- Event matching shall complete within 100ms
- Multiple workflows waiting for same event type shall all resume
- Event shall be logged for audit purposes

---

### REQ-008: Wait Step Cancellation (Event-Driven)

**Type:** Event-Driven

**EARS Statement:**
WHEN a workflow execution is cancelled, paused, or the contact is removed from the workflow,
THEN the system shall cancel all pending wait jobs and clean up all event listeners associated with that execution.

**Cancellation Triggers:**
- Manual workflow cancellation
- Contact opt-out
- Goal achievement
- Workflow deactivation
- Contact deletion

---

### REQ-009: Wait Step Monitoring (Ubiquitous)

**Type:** Ubiquitous

**EARS Statement:**
The system shall provide visibility into all active wait steps including count by type, upcoming resumes, and overdue jobs.

**Monitoring Metrics:**
- Total active wait steps by type
- Wait steps scheduled per hour/day
- Average wait duration by type
- Overdue job count and age
- Event listener count and age

---

### REQ-010: Timezone Consistency (Unwanted)

**Type:** Unwanted

**EARS Statement:**
The system shall NOT apply timezone conversions inconsistently. All internal timestamps shall be stored in UTC, and timezone conversions shall only occur at display time or when explicitly configured.

**Prohibited Behaviors:**
- Storing timestamps in local timezone without UTC reference
- Applying double timezone conversions
- Ignoring DST transitions
- Using system timezone instead of configured timezone

---

## Technical Specifications

### Database Schema

```sql
-- Wait step executions table
CREATE TABLE workflow_wait_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_execution_id UUID NOT NULL REFERENCES workflow_executions(id) ON DELETE CASCADE,
    workflow_id UUID NOT NULL REFERENCES workflows(id),
    contact_id UUID NOT NULL REFERENCES contacts(id),
    step_id VARCHAR(100) NOT NULL,

    -- Wait configuration
    wait_type VARCHAR(50) NOT NULL CHECK (wait_type IN ('fixed_time', 'until_date', 'until_time', 'for_event')),
    wait_config JSONB NOT NULL,

    -- Scheduling
    scheduled_at TIMESTAMPTZ,
    timezone VARCHAR(100) DEFAULT 'UTC',

    -- Event waiting
    event_type VARCHAR(100),
    event_correlation_id UUID,
    event_timeout_at TIMESTAMPTZ,

    -- Status tracking
    status VARCHAR(50) NOT NULL DEFAULT 'waiting' CHECK (status IN ('waiting', 'scheduled', 'resumed', 'timeout', 'cancelled', 'error')),
    resumed_at TIMESTAMPTZ,
    resumed_by VARCHAR(50), -- 'scheduler', 'event', 'timeout', 'manual', 'cancelled'

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Indexes
    CONSTRAINT unique_execution_step UNIQUE (workflow_execution_id, step_id)
);

-- Indexes for efficient querying
CREATE INDEX idx_wait_executions_scheduled ON workflow_wait_executions(scheduled_at) WHERE status = 'scheduled';
CREATE INDEX idx_wait_executions_event ON workflow_wait_executions(event_type, event_correlation_id) WHERE status = 'waiting';
CREATE INDEX idx_wait_executions_contact ON workflow_wait_executions(contact_id);
CREATE INDEX idx_wait_executions_workflow ON workflow_wait_executions(workflow_id);

-- Event listeners table
CREATE TABLE workflow_event_listeners (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wait_execution_id UUID NOT NULL REFERENCES workflow_wait_executions(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    correlation_id UUID,
    contact_id UUID NOT NULL,
    workflow_execution_id UUID NOT NULL,

    -- Matching criteria
    match_criteria JSONB,

    -- Timeout
    expires_at TIMESTAMPTZ NOT NULL,

    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'matched', 'expired', 'cancelled')),
    matched_at TIMESTAMPTZ,
    matched_event_id UUID,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_listener UNIQUE (wait_execution_id, event_type)
);

CREATE INDEX idx_event_listeners_lookup ON workflow_event_listeners(event_type, contact_id) WHERE status = 'active';
CREATE INDEX idx_event_listeners_expires ON workflow_event_listeners(expires_at) WHERE status = 'active';
```

### Redis Data Structures

```
# Scheduled jobs sorted set (score = scheduled timestamp)
ZADD workflow:scheduled_jobs <timestamp> <execution_id>:<step_id>

# Event listener hash
HSET workflow:event_listeners:<event_type>:<contact_id> <execution_id> <listener_config_json>

# Wait execution cache
SET workflow:wait:<execution_id>:<step_id> <state_json> EX 86400
```

### API Endpoints

```yaml
# Create wait step execution
POST /api/v1/workflows/{workflow_id}/executions/{execution_id}/wait
Request:
  step_id: string
  wait_type: "fixed_time" | "until_date" | "until_time" | "for_event"
  config:
    # For fixed_time
    duration: number
    unit: "minutes" | "hours" | "days" | "weeks"

    # For until_date
    target_date: ISO8601 string

    # For until_time
    target_time: "HH:MM"
    timezone: IANA timezone string
    days: ["monday", "tuesday", ...] (optional)

    # For for_event
    event_type: string
    timeout_hours: number
    timeout_action: "continue" | "exit"

Response:
  id: UUID
  scheduled_at: ISO8601 timestamp
  status: "scheduled" | "waiting"

# Get wait step status
GET /api/v1/workflows/executions/{execution_id}/wait/{step_id}
Response:
  id: UUID
  status: string
  scheduled_at: ISO8601 timestamp
  resumed_at: ISO8601 timestamp (nullable)
  resumed_by: string (nullable)

# Cancel wait step
DELETE /api/v1/workflows/executions/{execution_id}/wait/{step_id}
Response:
  success: boolean

# List pending waits (admin)
GET /api/v1/admin/workflows/waits/pending
Query:
  wait_type: string (optional)
  workflow_id: UUID (optional)
  limit: number
  offset: number
Response:
  items: WaitExecution[]
  total: number
```

### Background Job Architecture

```python
# Celery task for scheduled wait processing
@celery.task(
    bind=True,
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=300
)
def process_scheduled_wait(self, execution_id: str, step_id: str):
    """Process a scheduled wait step resume."""
    pass

# Celery beat schedule for polling
CELERY_BEAT_SCHEDULE = {
    'process-scheduled-waits': {
        'task': 'workflows.tasks.poll_scheduled_waits',
        'schedule': 10.0,  # Every 10 seconds
    },
    'cleanup-expired-listeners': {
        'task': 'workflows.tasks.cleanup_expired_listeners',
        'schedule': 300.0,  # Every 5 minutes
    },
}
```

---

## Dependencies

### Upstream Dependencies

| SPEC ID | Title | Dependency Type |
|---------|-------|-----------------|
| SPEC-WFL-001 | Create Workflow | Required - Workflow must exist |
| SPEC-WFL-002 | Configure Trigger | Required - Execution context |
| SPEC-WFL-003 | Add Action Step | Required - Step definitions |
| SPEC-WFL-005 | Execute Workflow | Required - Execution engine |

### Downstream Dependencies

| SPEC ID | Title | Dependency Type |
|---------|-------|-----------------|
| SPEC-WFL-007 | Goal Tracking | Consumes - Cancel on goal |
| SPEC-WFL-009 | Workflow Analytics | Consumes - Wait metrics |

### External Dependencies

| Service | Purpose | Version |
|---------|---------|---------|
| PostgreSQL (Supabase) | State persistence | 16+ |
| Redis | Job scheduling, caching | 7+ |
| Celery | Background task processing | 5.3+ |
| APScheduler | Alternative scheduler | 3.10+ |

---

## Security Considerations

### Data Access

- Wait executions inherit workflow RBAC permissions
- Cross-tenant isolation via account_id filtering
- Event correlation must validate contact ownership

### Audit Requirements

- Log all wait step creations with configuration
- Log all resume events with trigger type
- Log all cancellations with reason
- Retain logs for 90 days minimum

### Rate Limiting

- Maximum 100 concurrent wait steps per workflow execution
- Maximum 10,000 scheduled waits per account
- Event listener creation rate limited to 100/minute

---

## Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| Wait scheduling latency | < 100ms | P95 |
| Scheduled resume accuracy | +/- 60s | P95 |
| Event matching latency | < 100ms | P95 |
| Concurrent wait capacity | 100,000+ | Per cluster |
| Database query time | < 50ms | P95 |

---

## Traceability

| Artifact | Reference |
|----------|-----------|
| Product Requirement | product.md - Workflows Module |
| Technical Stack | tech.md - FastAPI, PostgreSQL, Redis |
| Parent SPEC | specs/workflows/plan.md - SPEC-WFL-006 |
| Plan Document | .moai/specs/SPEC-WFL-006/plan.md |
| Acceptance Criteria | .moai/specs/SPEC-WFL-006/acceptance.md |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-26 | manager-spec | Initial specification |
