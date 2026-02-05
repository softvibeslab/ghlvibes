# SPEC-WFL-005: Execute Workflow

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-005 |
| **Title** | Execute Workflow |
| **Module** | workflows |
| **Domain** | automation |
| **Priority** | Critical |
| **Status** | Planned |
| **Created** | 2026-01-26 |
| **Version** | 1.0.0 |

---

## Overview

The Execute Workflow specification defines the core workflow execution engine that processes automation workflows for contacts. When a workflow is triggered, the system executes configured actions in sequence with comprehensive error handling, retry logic, and execution logging. This is a critical component that powers the entire automation platform.

---

## Environment

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend Framework | FastAPI | Async API endpoints and workflow orchestration |
| Primary Database | PostgreSQL (Supabase) | Workflow execution state, history, and audit logs |
| Queue System | Redis | Job queuing, scheduling, and distributed processing |
| Task Worker | Celery / ARQ | Async task execution and retry handling |
| Cache Layer | Redis | Execution state caching and rate limiting |

### Infrastructure Requirements

| Requirement | Specification |
|-------------|---------------|
| Queue Workers | Minimum 3 worker instances for high availability |
| Database Connections | Connection pooling with 20-50 connections per worker |
| Redis Memory | Minimum 2GB for queue and state management |
| Monitoring | Prometheus metrics and Grafana dashboards |

### External Dependencies

| Service | Integration | Purpose |
|---------|-------------|---------|
| CRM Module | Internal API | Contact data retrieval and updates |
| Marketing Module | Internal API | Email/SMS sending actions |
| Integrations Module | Internal API | Webhook execution |
| Notification Service | Internal | Error alerts and notifications |

---

## Assumptions

### Technical Assumptions

| ID | Assumption | Confidence | Risk if Wrong |
|----|------------|------------|---------------|
| A1 | Redis cluster is available and configured with persistence | High | Queue data loss on failure |
| A2 | Database supports advisory locks for workflow state management | High | Race conditions in execution |
| A3 | Worker instances can scale horizontally | High | Performance bottlenecks |
| A4 | Network latency to external services is under 100ms | Medium | Timeout issues |

### Business Assumptions

| ID | Assumption | Confidence | Risk if Wrong |
|----|------------|------------|---------------|
| B1 | Maximum workflow execution time is 24 hours | High | Long-running workflow failures |
| B2 | Users expect real-time execution status visibility | High | Poor user experience |
| B3 | Retry attempts of 3 with exponential backoff is acceptable | High | User complaints on failures |
| B4 | Execution logs retained for 90 days meets compliance | Medium | Regulatory issues |

---

## Requirements

### Ubiquitous Requirements (Always Active)

| ID | Requirement | Rationale |
|----|-------------|-----------|
| REQ-U1 | The system shall log all workflow execution events with timestamps, contact ID, and action details | Auditability and debugging |
| REQ-U2 | The system shall encrypt sensitive data in execution logs at rest using AES-256 | Security compliance |
| REQ-U3 | The system shall maintain execution state across worker restarts | Reliability |
| REQ-U4 | The system shall enforce rate limits per account to prevent abuse | Fair resource usage |

### Event-Driven Requirements (Trigger-Response)

| ID | Event | Action | Result |
|----|-------|--------|--------|
| REQ-E1 | WHEN a workflow is triggered for a contact | THEN the system shall create an execution instance and enqueue the first action | Workflow execution initiated with unique execution ID |
| REQ-E2 | WHEN an action completes successfully | THEN the system shall update execution state and enqueue the next action | Sequential action processing |
| REQ-E3 | WHEN an action fails | THEN the system shall log the error, increment retry counter, and schedule retry with exponential backoff | Resilient error handling |
| REQ-E4 | WHEN all retries are exhausted | THEN the system shall mark execution as failed and send error notification | Failure notification |
| REQ-E5 | WHEN a workflow reaches a wait step | THEN the system shall schedule the resume time and pause execution | Timed execution control |
| REQ-E6 | WHEN a contact achieves workflow goal | THEN the system shall mark execution as completed and exit the workflow | Goal-based completion |
| REQ-E7 | WHEN execution is manually cancelled | THEN the system shall terminate all pending actions and mark as cancelled | Manual intervention support |

### State-Driven Requirements (Conditional Behavior)

| ID | Condition | Action | Result |
|----|-----------|--------|--------|
| REQ-S1 | IF workflow execution is in 'waiting' state AND wait condition is met | THEN the system shall resume execution from the wait step | Scheduled resume |
| REQ-S2 | IF concurrent execution limit is reached for the account | THEN the system shall queue new executions with priority ordering | Throttled execution |
| REQ-S3 | IF workflow version changes during execution | THEN the system shall continue with the original version until completion | Version stability |
| REQ-S4 | IF contact is deleted during workflow execution | THEN the system shall gracefully terminate execution | Data consistency |

### Unwanted Requirements (Prohibited Actions)

| ID | Prohibition | Rationale |
|----|-------------|-----------|
| REQ-N1 | The system shall NOT execute workflows for opted-out contacts | Legal compliance (CAN-SPAM, GDPR) |
| REQ-N2 | The system shall NOT exceed configured rate limits for external services | API rate limit compliance |
| REQ-N3 | The system shall NOT store plaintext credentials in execution logs | Security best practice |
| REQ-N4 | The system shall NOT process duplicate trigger events within 5-second window | Deduplication |

### Optional Requirements (Nice-to-Have)

| ID | Feature | Benefit |
|----|---------|---------|
| REQ-O1 | Where possible, the system shall batch similar actions for efficiency | Performance optimization |
| REQ-O2 | Where possible, the system shall provide execution time predictions | User experience |
| REQ-O3 | Where possible, the system shall suggest workflow optimizations | Automation improvement |

---

## Specifications

### 1. Workflow Execution Engine Architecture

```
+------------------+     +------------------+     +------------------+
|   Trigger Event  |---->|  Execution Queue |---->|   Worker Pool    |
|   (API/Webhook)  |     |     (Redis)      |     |   (Celery/ARQ)   |
+------------------+     +------------------+     +------------------+
                                                           |
                                                           v
+------------------+     +------------------+     +------------------+
| Execution State  |<----|  Action Handler  |---->|  External APIs   |
|   (PostgreSQL)   |     |                  |     |  (CRM, Email)    |
+------------------+     +------------------+     +------------------+
                                 |
                                 v
+------------------+     +------------------+
|  Error Handler   |---->|  Notification    |
|                  |     |    Service       |
+------------------+     +------------------+
```

### 2. Execution State Machine

```
                    +--------+
                    | QUEUED |
                    +--------+
                         |
                         v
+--------+         +---------+         +--------+
| PAUSED |<--------|  ACTIVE |-------->| FAILED |
+--------+         +---------+         +--------+
    |                   |                   |
    v                   v                   v
+--------+         +-----------+       +--------+
| ACTIVE |-------->| COMPLETED |<------| RETRY  |
+--------+         +-----------+       +--------+
                         ^
                         |
                   +-----------+
                   | CANCELLED |
                   +-----------+
```

### 3. Data Models

#### WorkflowExecution

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique execution identifier |
| workflow_id | UUID | Reference to workflow definition |
| workflow_version | Integer | Version of workflow at execution start |
| contact_id | UUID | Contact being processed |
| account_id | UUID | Account/tenant identifier |
| status | Enum | QUEUED, ACTIVE, PAUSED, COMPLETED, FAILED, CANCELLED |
| current_step_index | Integer | Current position in workflow |
| started_at | Timestamp | Execution start time |
| completed_at | Timestamp | Execution completion time (nullable) |
| error_message | Text | Last error message (nullable) |
| retry_count | Integer | Number of retry attempts |
| metadata | JSONB | Additional execution context |
| created_at | Timestamp | Record creation time |
| updated_at | Timestamp | Last update time |

#### ExecutionLog

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique log identifier |
| execution_id | UUID | Reference to execution |
| step_index | Integer | Workflow step index |
| action_type | String | Type of action executed |
| action_config | JSONB | Action configuration (encrypted) |
| status | Enum | SUCCESS, FAILED, SKIPPED |
| started_at | Timestamp | Action start time |
| completed_at | Timestamp | Action completion time |
| duration_ms | Integer | Execution duration in milliseconds |
| error_details | JSONB | Error information (if failed) |
| response_data | JSONB | Action response data |
| created_at | Timestamp | Record creation time |

### 4. Queue Message Schema

```json
{
  "execution_id": "uuid",
  "workflow_id": "uuid",
  "contact_id": "uuid",
  "account_id": "uuid",
  "step_index": 0,
  "action": {
    "type": "send_email",
    "config": { ... }
  },
  "retry_count": 0,
  "scheduled_at": "ISO-8601 timestamp",
  "priority": 5,
  "metadata": {
    "trigger_source": "form_submission",
    "trigger_id": "uuid"
  }
}
```

### 5. API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/workflows/{id}/execute` | Trigger workflow execution for contact |
| GET | `/api/v1/executions/{id}` | Get execution status and details |
| GET | `/api/v1/executions/{id}/logs` | Get execution logs |
| POST | `/api/v1/executions/{id}/cancel` | Cancel active execution |
| POST | `/api/v1/executions/{id}/retry` | Retry failed execution |
| GET | `/api/v1/workflows/{id}/executions` | List executions for workflow |
| GET | `/api/v1/contacts/{id}/executions` | List executions for contact |

### 6. Execution Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| max_retry_attempts | 3 | Maximum retry attempts per action |
| retry_base_delay_seconds | 60 | Base delay for exponential backoff |
| retry_max_delay_seconds | 3600 | Maximum delay between retries |
| execution_timeout_hours | 24 | Maximum execution duration |
| concurrent_executions_per_account | 100 | Account-level execution limit |
| queue_processing_batch_size | 50 | Actions processed per batch |
| error_notification_enabled | true | Send notifications on failures |
| execution_logging_enabled | true | Log all execution events |

### 7. Error Handling Strategy

| Error Type | Handling Strategy | Retry |
|------------|-------------------|-------|
| Network Timeout | Retry with exponential backoff | Yes |
| External API Error (4xx) | Log and skip to next action | No |
| External API Error (5xx) | Retry with exponential backoff | Yes |
| Rate Limit Exceeded | Queue with delay based on rate limit headers | Yes |
| Invalid Contact Data | Log error, skip action, continue workflow | No |
| Configuration Error | Mark execution as failed, notify admin | No |
| Database Error | Retry with backoff | Yes |
| Worker Crash | Auto-recover from last checkpoint | Yes |

### 8. Monitoring and Observability

#### Metrics to Track

| Metric | Type | Description |
|--------|------|-------------|
| workflow_executions_total | Counter | Total executions by status |
| workflow_execution_duration_seconds | Histogram | Execution duration distribution |
| workflow_action_duration_seconds | Histogram | Action duration by type |
| workflow_queue_depth | Gauge | Current queue depth |
| workflow_retry_total | Counter | Retry attempts by error type |
| workflow_error_total | Counter | Errors by type and workflow |

#### Alerting Rules

| Alert | Condition | Severity |
|-------|-----------|----------|
| HighFailureRate | Error rate > 5% over 5 minutes | High |
| QueueBacklog | Queue depth > 10,000 for 10 minutes | Medium |
| WorkerDown | Worker heartbeat missing for 2 minutes | Critical |
| ExecutionStuck | Execution in ACTIVE state > 2 hours | Medium |

---

## Traceability

| SPEC ID | Related SPECs | Dependencies |
|---------|---------------|--------------|
| SPEC-WFL-005 | SPEC-WFL-001 (Create Workflow) | Workflow definition |
| SPEC-WFL-005 | SPEC-WFL-002 (Configure Trigger) | Trigger configuration |
| SPEC-WFL-005 | SPEC-WFL-003 (Add Action Step) | Action definitions |
| SPEC-WFL-005 | SPEC-WFL-004 (Add Condition/Branch) | Conditional logic |
| SPEC-WFL-005 | SPEC-WFL-006 (Wait Step Processing) | Wait step handling |
| SPEC-WFL-005 | SPEC-WFL-007 (Goal Tracking) | Goal evaluation |
| SPEC-WFL-005 | SPEC-WFL-010 (Webhook Integration) | External webhooks |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-26 | manager-spec | Initial specification |
