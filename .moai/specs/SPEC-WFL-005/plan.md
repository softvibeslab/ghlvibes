# SPEC-WFL-005: Execute Workflow - Implementation Plan

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-005 |
| **Title** | Execute Workflow - Implementation Plan |
| **Created** | 2026-01-26 |
| **Status** | Planned |

---

## Implementation Overview

This plan outlines the implementation strategy for the Workflow Execution Engine, the core component that powers automation processing in the GoHighLevel Clone platform.

---

## Milestones

### Primary Goal: Core Execution Engine

**Scope:** Implement the foundational workflow execution system with queue processing and state management.

**Deliverables:**

1. **Execution State Manager**
   - WorkflowExecution SQLAlchemy model
   - ExecutionLog SQLAlchemy model
   - State machine implementation
   - Database migrations

2. **Queue Infrastructure**
   - Redis queue setup and configuration
   - Celery/ARQ worker configuration
   - Priority queue implementation
   - Dead letter queue for failed jobs

3. **Execution Service**
   - WorkflowExecutionService class
   - Action dispatcher with type routing
   - Sequential action processing
   - Execution lifecycle management

4. **API Endpoints**
   - POST `/api/v1/workflows/{id}/execute`
   - GET `/api/v1/executions/{id}`
   - GET `/api/v1/executions/{id}/logs`
   - Pagination and filtering support

**Success Criteria:**
- Execute simple linear workflows end-to-end
- Process 100 concurrent executions
- State persistence across worker restarts

---

### Secondary Goal: Error Handling and Retry Logic

**Scope:** Implement robust error handling with configurable retry strategies.

**Deliverables:**

1. **Retry Manager**
   - Exponential backoff implementation
   - Configurable retry policies
   - Circuit breaker pattern
   - Retry state tracking

2. **Error Classification**
   - Error type enumeration
   - Retryable vs non-retryable errors
   - Error aggregation and categorization

3. **Notification System Integration**
   - Error notification triggers
   - Admin alert configuration
   - Email/SMS notification support
   - Slack/webhook integration

4. **Recovery Mechanisms**
   - Automatic checkpoint recovery
   - Manual retry endpoint
   - Bulk retry for failed executions

**Success Criteria:**
- Zero lost executions on worker crash
- Successful retry rate > 80% for transient errors
- Admin notification within 1 minute of critical failure

---

### Tertiary Goal: Performance and Scalability

**Scope:** Optimize execution engine for high throughput and horizontal scaling.

**Deliverables:**

1. **Queue Optimization**
   - Priority-based routing
   - Batch processing for bulk enrollments
   - Rate limiting per account
   - Queue health monitoring

2. **Database Optimization**
   - Index optimization for common queries
   - Partitioning for execution logs
   - Connection pooling configuration
   - Query optimization

3. **Worker Scaling**
   - Horizontal scaling configuration
   - Auto-scaling rules
   - Worker health checks
   - Load balancing

4. **Caching Layer**
   - Workflow definition caching
   - Contact data caching
   - Execution state caching
   - Cache invalidation strategies

**Success Criteria:**
- Process 10,000 actions per minute
- P95 action execution time < 500ms
- Support 1,000 concurrent workflows per account

---

### Final Goal: Monitoring and Observability

**Scope:** Implement comprehensive monitoring, logging, and analytics.

**Deliverables:**

1. **Metrics Collection**
   - Prometheus metrics endpoint
   - Execution duration histograms
   - Queue depth gauges
   - Error rate counters

2. **Logging Enhancement**
   - Structured JSON logging
   - Log aggregation setup
   - Sensitive data masking
   - Log retention policies

3. **Alerting System**
   - Alert rule configuration
   - PagerDuty/OpsGenie integration
   - Alert escalation policies
   - Runbook documentation

4. **Analytics Dashboard**
   - Execution analytics queries
   - Performance trends
   - Error analysis reports
   - Workflow efficiency metrics

**Success Criteria:**
- Real-time visibility into all executions
- Mean time to detection (MTTD) < 5 minutes
- Comprehensive audit trail for compliance

---

### Optional Goal: Advanced Features

**Scope:** Implement nice-to-have features for enhanced user experience.

**Deliverables:**

1. **Execution Predictions**
   - Estimated completion time
   - Resource usage forecasting
   - Bottleneck detection

2. **Action Batching**
   - Group similar email sends
   - Batch SMS delivery
   - Webhook aggregation

3. **Optimization Suggestions**
   - Workflow performance analysis
   - Unused step detection
   - Timing optimization recommendations

**Success Criteria:**
- Prediction accuracy > 80%
- 20% reduction in external API calls through batching

---

## Technical Approach

### Architecture Pattern

The execution engine follows an event-driven microservices pattern:

```
Trigger Events --> Message Queue --> Worker Pool --> State Store
                        |                 |
                        v                 v
                   Dead Letter       External APIs
                     Queue
```

### Technology Choices

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Task Queue | Redis + ARQ | Async Python support, simplicity |
| State Store | PostgreSQL | ACID compliance, JSONB support |
| Cache | Redis | Low latency, pub/sub support |
| Worker | ARQ Workers | Native async/await, lightweight |

### Key Design Decisions

1. **Stateless Workers**
   - All state persisted to PostgreSQL
   - Workers can be killed/restarted safely
   - Horizontal scaling without coordination

2. **Pessimistic Locking**
   - Advisory locks prevent duplicate processing
   - SELECT FOR UPDATE for state transitions
   - Prevents race conditions

3. **Checkpoint-Based Recovery**
   - State saved after each action
   - Resume from last successful step
   - Idempotent action design

4. **Priority Queues**
   - High priority for real-time triggers
   - Normal priority for scheduled tasks
   - Low priority for bulk operations

### Database Schema

```sql
-- Workflow Executions
CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id),
    workflow_version INTEGER NOT NULL,
    contact_id UUID NOT NULL REFERENCES contacts(id),
    account_id UUID NOT NULL REFERENCES accounts(id),
    status VARCHAR(20) NOT NULL DEFAULT 'QUEUED',
    current_step_index INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_executions_workflow_id ON workflow_executions(workflow_id);
CREATE INDEX idx_executions_contact_id ON workflow_executions(contact_id);
CREATE INDEX idx_executions_account_status ON workflow_executions(account_id, status);
CREATE INDEX idx_executions_status_created ON workflow_executions(status, created_at);

-- Execution Logs (partitioned by month)
CREATE TABLE execution_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID NOT NULL REFERENCES workflow_executions(id),
    step_index INTEGER NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    action_config JSONB,
    status VARCHAR(20) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    error_details JSONB,
    response_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Create partitions
CREATE TABLE execution_logs_2026_01 PARTITION OF execution_logs
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```

### API Design

```python
# Execution Trigger Endpoint
@router.post("/workflows/{workflow_id}/execute")
async def trigger_execution(
    workflow_id: UUID,
    request: ExecutionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ExecutionResponse:
    """
    Trigger workflow execution for a contact.

    - Validates workflow exists and is active
    - Checks contact eligibility (not opted-out)
    - Creates execution record
    - Enqueues first action
    """
    pass

# Execution Status Endpoint
@router.get("/executions/{execution_id}")
async def get_execution(
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ExecutionDetailResponse:
    """
    Get detailed execution status with current step info.
    """
    pass
```

---

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Queue overflow during traffic spikes | Medium | High | Auto-scaling workers, rate limiting, priority queues |
| External API rate limiting | High | Medium | Request throttling, exponential backoff, batching |
| Database deadlocks | Low | High | Advisory locks, optimistic concurrency, retry logic |
| Worker memory leaks | Medium | Medium | Memory monitoring, periodic worker restart, leak detection |
| Data inconsistency on failure | Low | Critical | Transactional state updates, idempotent operations |

---

## Dependencies

### Internal Dependencies

| Module | Dependency Type | Required For |
|--------|-----------------|--------------|
| Workflows (SPEC-WFL-001-004) | Data | Workflow definitions |
| CRM Module | API | Contact data access |
| Marketing Module | API | Email/SMS actions |
| Integrations Module | API | Webhook execution |

### External Dependencies

| Service | Version | Purpose |
|---------|---------|---------|
| Redis | 7.x | Queue and caching |
| PostgreSQL | 16.x | State persistence |
| ARQ | Latest | Task worker |
| Prometheus | Latest | Metrics collection |

---

## Testing Strategy

### Unit Tests

- Action dispatcher routing
- State machine transitions
- Retry logic calculations
- Error classification

### Integration Tests

- End-to-end workflow execution
- Queue processing flow
- Database state persistence
- API endpoint validation

### Load Tests

- 10,000 concurrent executions
- Queue throughput benchmarks
- Database connection pooling
- Memory usage profiling

### Chaos Tests

- Worker crash recovery
- Redis failover
- Database connection loss
- Network partition handling

---

## Traceability

| SPEC ID | Plan Section | Implementation Milestone |
|---------|--------------|-------------------------|
| REQ-E1 | Core Execution Engine | Primary Goal |
| REQ-E2 | Execution Service | Primary Goal |
| REQ-E3 | Retry Manager | Secondary Goal |
| REQ-E4 | Notification Integration | Secondary Goal |
| REQ-S1 | Wait Step Handler | Primary Goal |
| REQ-U1 | Logging Enhancement | Final Goal |
| REQ-U4 | Rate Limiting | Tertiary Goal |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-26 | manager-spec | Initial implementation plan |
