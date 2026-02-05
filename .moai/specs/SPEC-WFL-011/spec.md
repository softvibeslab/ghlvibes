# SPEC-WFL-011: Bulk Enrollment

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-011 |
| **Title** | Bulk Enrollment |
| **Module** | workflows |
| **Domain** | automation |
| **Priority** | Medium |
| **Status** | Planned |
| **Created** | 2026-01-26 |
| **Version** | 1.0.0 |

---

## Overview

This specification defines the bulk enrollment feature for the GoHighLevel Clone workflow automation system. The feature enables users to enroll large numbers of contacts (up to 10,000) into workflows simultaneously through asynchronous batch processing with real-time progress tracking and comprehensive error handling for partial failures.

---

## EARS Requirements

### REQ-001: Bulk Enrollment Initiation (Event-Driven)

**WHEN** a user initiates bulk enrollment of contacts into a workflow
**THEN** the system shall validate the contact selection, create a bulk enrollment job, and begin asynchronous processing
**RESULTING IN** a bulk enrollment job created with a unique job ID and initial status "pending"
**STATE** pending

### REQ-002: Contact Selection Validation (Event-Driven)

**WHEN** validating contacts for bulk enrollment
**THEN** the system shall verify:
- Contact IDs exist and belong to the account
- Contacts are not already enrolled in the target workflow
- Contacts are not in a blocked or unsubscribed state
- Total contact count does not exceed 10,000

**RESULTING IN** validated contact list or validation errors returned
**STATE** validated

### REQ-003: Batch Queue Creation (Event-Driven)

**WHEN** a bulk enrollment job is created
**THEN** the system shall divide contacts into batches of 100 and queue them for processing
**RESULTING IN** multiple batch tasks queued in Redis with job metadata
**STATE** queued

### REQ-004: Contact Count Limits (Ubiquitous)

The system **shall** enforce the following limits for bulk enrollment:
- Maximum contacts per bulk operation: 10,000
- Batch size for processing: 100 contacts per batch
- Maximum concurrent batch processes per account: 5
- Maximum pending bulk jobs per account: 10

### REQ-005: Asynchronous Batch Processing (Event-Driven)

**WHEN** a batch is processed from the queue
**THEN** the system shall:
- Enroll each contact into the workflow
- Track individual enrollment success/failure
- Update batch progress in Redis
- Proceed to next batch upon completion

**RESULTING IN** contacts enrolled with individual status tracking
**STATE** processing

### REQ-006: Progress Tracking (State-Driven)

**WHILE** a bulk enrollment job is processing
**THEN** the system shall maintain real-time progress data:
- Total contacts to process
- Contacts processed successfully
- Contacts failed to process
- Current batch number
- Estimated time remaining
- Processing rate (contacts/second)

**RESULTING IN** real-time progress information accessible via API
**STATE** tracking

### REQ-007: Progress Update Broadcasting (Event-Driven)

**WHEN** batch processing progress is updated
**THEN** the system shall broadcast progress updates via WebSocket to subscribed clients
**RESULTING IN** real-time UI updates without polling
**STATE** broadcasting

### REQ-008: Individual Contact Enrollment (Event-Driven)

**WHEN** enrolling a single contact within a batch
**THEN** the system shall:
- Create workflow execution record
- Initialize contact at workflow start trigger
- Log enrollment event
- Update contact tags if configured

**RESULTING IN** contact enrolled and workflow execution initiated
**STATE** enrolled

### REQ-009: Duplicate Enrollment Prevention (Unwanted Behavior)

The system **shall NOT** enroll a contact who is already active in the target workflow.
**IF** a contact is already enrolled
**THEN** the system shall skip the contact and mark as "already_enrolled" without error.

### REQ-010: Partial Failure Handling (Event-Driven)

**WHEN** individual contact enrollments fail within a batch
**THEN** the system shall:
- Continue processing remaining contacts in the batch
- Log the failure with contact ID and error reason
- Increment failure counter
- Allow job completion with partial success

**RESULTING IN** maximum contacts enrolled despite individual failures
**STATE** partial_failure

### REQ-011: Batch Retry Mechanism (Event-Driven)

**WHEN** an entire batch fails due to transient error (database timeout, connection error)
**THEN** the system shall retry the batch with exponential backoff:
- Retry 1: Wait 10 seconds
- Retry 2: Wait 30 seconds
- Retry 3: Wait 90 seconds (final attempt)

**RESULTING IN** resilient batch processing with automatic recovery
**STATE** retrying

### REQ-012: Job Completion (Event-Driven)

**WHEN** all batches in a bulk enrollment job are processed
**THEN** the system shall:
- Update job status to "completed" or "completed_with_errors"
- Calculate final statistics
- Send completion notification (email/webhook)
- Generate completion report

**RESULTING IN** job finalized with comprehensive summary
**STATE** completed

### REQ-013: Job Cancellation (Event-Driven)

**WHEN** a user requests cancellation of an in-progress bulk enrollment job
**THEN** the system shall:
- Mark job status as "cancelling"
- Allow current batch to complete
- Skip all pending batches
- Update final status to "cancelled"

**RESULTING IN** graceful job cancellation without data corruption
**STATE** cancelled

### REQ-014: Enrollment Rate Limiting (State-Driven)

**WHILE** bulk enrollment is processing
**THEN** the system shall enforce rate limits:
- Per-account: 500 enrollments per minute
- Global: 5,000 enrollments per minute
- Burst limit: 100 enrollments per second

**RESULTING IN** system stability under high enrollment load
**STATE** rate_limited

### REQ-015: Job History Retention (Ubiquitous)

The system **shall** retain bulk enrollment job history for 90 days, including:
- Job metadata (ID, workflow, contact count, timestamps)
- Completion statistics
- Error summaries
- Individual failure records (up to 1,000 per job)

### REQ-016: Enrollment Source Tracking (Event-Driven)

**WHEN** contacts are enrolled via bulk enrollment
**THEN** the system shall record enrollment source as "bulk_enrollment" with job ID reference
**RESULTING IN** traceable enrollment origin for analytics and debugging
**STATE** tracked

### REQ-017: Filter-Based Selection (Event-Driven)

**WHEN** a user selects contacts using filter criteria instead of explicit IDs
**THEN** the system shall:
- Execute filter query to resolve contact IDs
- Cache resolved IDs for the job duration
- Validate resolved count against limits
- Proceed with standard bulk enrollment flow

**RESULTING IN** dynamic contact selection without manual ID specification
**STATE** filtered

### REQ-018: CSV Upload Selection (Event-Driven)

**WHEN** a user uploads a CSV file with contact identifiers
**THEN** the system shall:
- Parse CSV file (email or contact_id columns)
- Match identifiers to existing contacts
- Report unmatched identifiers
- Proceed with matched contacts only

**RESULTING IN** bulk enrollment from external contact lists
**STATE** imported

### REQ-019: Scheduled Bulk Enrollment (Optional)

**WHERE** supported, the system **shall** allow scheduling bulk enrollment for future execution:
- Specify execution date and time
- Support timezone configuration
- Allow schedule modification before execution
- Auto-execute at scheduled time

### REQ-020: Dry Run Mode (Event-Driven)

**WHEN** a user requests a dry run of bulk enrollment
**THEN** the system shall simulate the enrollment without executing:
- Validate all contacts
- Identify duplicates and exclusions
- Calculate estimated processing time
- Return detailed preview report

**RESULTING IN** risk-free enrollment validation before execution
**STATE** simulated

---

## Technical Specifications

### Bulk Enrollment Architecture

```
+-------------------+     +------------------+     +------------------+
| Bulk Enrollment   |---->| Job Queue        |---->| Batch Worker     |
| API               |     | (Redis)          |     | Pool             |
+-------------------+     +------------------+     +------------------+
        |                         |                        |
        v                         v                        v
+---------------+         +---------------+        +---------------+
| Contact       |         | Progress      |        | Workflow      |
| Validator     |         | Tracker       |        | Engine        |
+---------------+         +---------------+        +---------------+
        |                         |                        |
        v                         v                        v
+---------------+         +---------------+        +---------------+
| Selection     |         | WebSocket     |        | Enrollment    |
| Resolver      |         | Broadcaster   |        | Logger        |
+---------------+         +---------------+        +---------------+
```

### Database Schema

```sql
-- Bulk enrollment jobs
CREATE TABLE bulk_enrollment_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id),
    workflow_id UUID NOT NULL REFERENCES workflows(id),
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    -- pending, validating, queued, processing, completed, completed_with_errors, cancelled, failed

    -- Selection criteria
    selection_type VARCHAR(20) NOT NULL, -- manual, filter, csv
    contact_ids UUID[],
    filter_criteria JSONB,
    csv_file_url TEXT,

    -- Statistics
    total_contacts INTEGER NOT NULL DEFAULT 0,
    processed_count INTEGER NOT NULL DEFAULT 0,
    success_count INTEGER NOT NULL DEFAULT 0,
    failure_count INTEGER NOT NULL DEFAULT 0,
    skipped_count INTEGER NOT NULL DEFAULT 0,

    -- Batching
    batch_size INTEGER NOT NULL DEFAULT 100,
    total_batches INTEGER NOT NULL DEFAULT 0,
    completed_batches INTEGER NOT NULL DEFAULT 0,

    -- Timing
    scheduled_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    estimated_completion TIMESTAMPTZ,

    -- Metadata
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Batch processing records
CREATE TABLE bulk_enrollment_batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES bulk_enrollment_jobs(id) ON DELETE CASCADE,
    batch_number INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    -- pending, processing, completed, failed, skipped

    contact_ids UUID[] NOT NULL,
    success_ids UUID[],
    failure_ids UUID[],

    attempt_count INTEGER DEFAULT 0,
    error_message TEXT,

    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Individual enrollment failures (for debugging)
CREATE TABLE bulk_enrollment_failures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES bulk_enrollment_jobs(id) ON DELETE CASCADE,
    batch_id UUID REFERENCES bulk_enrollment_batches(id),
    contact_id UUID NOT NULL,

    error_code VARCHAR(50) NOT NULL,
    error_message TEXT NOT NULL,
    error_details JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_bulk_jobs_account ON bulk_enrollment_jobs(account_id);
CREATE INDEX idx_bulk_jobs_status ON bulk_enrollment_jobs(status);
CREATE INDEX idx_bulk_jobs_workflow ON bulk_enrollment_jobs(workflow_id);
CREATE INDEX idx_bulk_batches_job ON bulk_enrollment_batches(job_id);
CREATE INDEX idx_bulk_batches_status ON bulk_enrollment_batches(status);
CREATE INDEX idx_bulk_failures_job ON bulk_enrollment_failures(job_id);
CREATE INDEX idx_bulk_failures_contact ON bulk_enrollment_failures(contact_id);

-- Partial index for active jobs
CREATE INDEX idx_bulk_jobs_active ON bulk_enrollment_jobs(account_id, status)
    WHERE status IN ('pending', 'validating', 'queued', 'processing');
```

### Redis Data Structures

```
# Job progress tracking
bulk_enrollment:{job_id}:progress
    - total_contacts: 5000
    - processed: 2500
    - success: 2480
    - failed: 20
    - skipped: 0
    - current_batch: 25
    - total_batches: 50
    - started_at: timestamp
    - rate: 50.5  # contacts/second

# Batch queue (sorted set by priority)
bulk_enrollment:queue:{account_id}
    score: timestamp
    member: {job_id}:{batch_number}

# Rate limiting
bulk_enrollment:rate:{account_id}
    - window: 60 seconds
    - count: current_count
    - limit: 500

# Active job tracking
bulk_enrollment:active:{account_id}
    - job_ids set
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/workflows/{id}/bulk-enrollment` | Create bulk enrollment job |
| GET | `/api/v1/bulk-enrollment-jobs` | List jobs for account |
| GET | `/api/v1/bulk-enrollment-jobs/{id}` | Get job details |
| GET | `/api/v1/bulk-enrollment-jobs/{id}/progress` | Get real-time progress |
| POST | `/api/v1/bulk-enrollment-jobs/{id}/cancel` | Cancel job |
| GET | `/api/v1/bulk-enrollment-jobs/{id}/failures` | Get failure details |
| POST | `/api/v1/bulk-enrollment-jobs/{id}/retry-failures` | Retry failed contacts |
| POST | `/api/v1/workflows/{id}/bulk-enrollment/dry-run` | Execute dry run |
| POST | `/api/v1/workflows/{id}/bulk-enrollment/validate` | Validate contacts |

### Request/Response Models

```python
from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID
from datetime import datetime

# Selection types
class ManualSelection(BaseModel):
    type: Literal["manual"] = "manual"
    contact_ids: list[UUID] = Field(..., max_items=10000)

class FilterSelection(BaseModel):
    type: Literal["filter"] = "filter"
    filter: dict  # Contact filter criteria

class CSVSelection(BaseModel):
    type: Literal["csv"] = "csv"
    file_key: str  # Uploaded file reference
    identifier_column: Literal["email", "contact_id"] = "email"

# Create job request
class BulkEnrollmentCreate(BaseModel):
    selection: ManualSelection | FilterSelection | CSVSelection
    options: BulkEnrollmentOptions | None = None

class BulkEnrollmentOptions(BaseModel):
    batch_size: int = Field(default=100, ge=10, le=500)
    skip_duplicates: bool = True
    skip_unsubscribed: bool = True
    scheduled_at: datetime | None = None
    notify_on_completion: bool = True
    notification_email: str | None = None

# Job response
class BulkEnrollmentJobResponse(BaseModel):
    id: UUID
    workflow_id: UUID
    status: str
    selection_type: str
    total_contacts: int
    processed_count: int
    success_count: int
    failure_count: int
    skipped_count: int
    progress_percentage: float
    estimated_completion: datetime | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None

# Progress response
class BulkEnrollmentProgress(BaseModel):
    job_id: UUID
    status: str
    total_contacts: int
    processed: int
    success: int
    failed: int
    skipped: int
    current_batch: int
    total_batches: int
    progress_percentage: float
    rate: float  # contacts per second
    estimated_time_remaining_seconds: int | None

# Failure detail
class EnrollmentFailure(BaseModel):
    contact_id: UUID
    contact_email: str | None
    error_code: str
    error_message: str
    batch_number: int
    created_at: datetime
```

### Error Codes

| Code | Description | Retryable |
|------|-------------|-----------|
| `CONTACT_NOT_FOUND` | Contact ID does not exist | No |
| `CONTACT_BLOCKED` | Contact is blocked/unsubscribed | No |
| `ALREADY_ENROLLED` | Contact already in workflow | No |
| `WORKFLOW_INACTIVE` | Target workflow not active | No |
| `WORKFLOW_NOT_FOUND` | Workflow does not exist | No |
| `ENROLLMENT_ERROR` | General enrollment failure | Yes |
| `DATABASE_ERROR` | Database operation failed | Yes |
| `TIMEOUT_ERROR` | Operation timed out | Yes |
| `RATE_LIMIT_ERROR` | Rate limit exceeded | Yes |
| `VALIDATION_ERROR` | Contact validation failed | No |

---

## Queue Management Architecture

### Job Processing Flow

1. **Job Creation**
   - Validate request and contact selection
   - Create job record with "pending" status
   - Return job ID immediately

2. **Validation Phase**
   - Update status to "validating"
   - Resolve contact IDs (filter/CSV)
   - Validate each contact eligibility
   - Create validation report

3. **Queue Phase**
   - Update status to "queued"
   - Divide contacts into batches
   - Add batches to Redis queue
   - Initialize progress tracking

4. **Processing Phase**
   - Update status to "processing"
   - Workers pull batches from queue
   - Process contacts in parallel
   - Update progress after each batch

5. **Completion Phase**
   - Update status based on results
   - Generate completion report
   - Send notifications
   - Archive job data

### Worker Pool Configuration

```python
WORKER_CONFIG = {
    "max_workers": 5,           # Per account
    "batch_timeout": 300,       # 5 minutes per batch
    "idle_timeout": 60,         # Worker idle before shutdown
    "prefetch_count": 2,        # Batches to prefetch
    "retry_delay_base": 10,     # Base retry delay in seconds
    "retry_max_attempts": 3,    # Maximum retry attempts
}
```

---

## Security Considerations

### Authorization
- Only account admins and users with "workflow:manage" permission can create bulk enrollments
- Users can only enroll contacts they have access to
- Rate limits enforced per account to prevent abuse

### Data Protection
- Contact IDs validated against account ownership
- CSV files scanned for malicious content
- File uploads restricted to 10MB max size
- Temporary files deleted after processing

### Audit Logging
- All bulk enrollment operations logged
- Job creation, cancellation, completion events tracked
- Failure reasons recorded for compliance

---

## Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| Job creation response | < 500ms | API response time |
| Validation throughput | 1,000 contacts/second | Contacts validated |
| Enrollment throughput | 100 contacts/second | Contacts enrolled per batch |
| Progress update latency | < 100ms | Redis to WebSocket |
| Maximum batch processing | 5 minutes | Per batch timeout |
| Job history query | < 100ms | List jobs with pagination |

---

## Dependencies

### Internal Dependencies
- Workflow Engine (SPEC-WFL-005) - For contact enrollment
- Contact Management (SPEC-CRM-001) - For contact validation
- Authentication Service - For permission checks
- WebSocket Service - For progress broadcasting

### External Dependencies
- PostgreSQL/Supabase (database storage)
- Redis (queue, rate limiting, progress tracking)
- Celery (async task processing)

---

## Traceability

| Tag | Reference |
|-----|-----------|
| SPEC-WFL-011 | This specification |
| SPEC-WFL-005 | Execute Workflow (enrollment target) |
| SPEC-WFL-001 | Create Workflow (prerequisite) |
| SPEC-CRM-001 | Contact Management (contact validation) |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-26 | manager-spec | Initial specification |
