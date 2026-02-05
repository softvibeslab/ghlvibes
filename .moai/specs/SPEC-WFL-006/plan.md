# SPEC-WFL-006: Wait Step Processing - Implementation Plan

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-006 |
| **Title** | Wait Step Processing |
| **Phase** | Plan |
| **Status** | Ready for Implementation |

---

## Implementation Overview

This document outlines the implementation plan for the Wait Step Processing feature, enabling workflow automation to pause and resume based on time delays or event triggers.

### Architecture Summary

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Wait Step Architecture                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐       │
│   │   Workflow   │────▶│  Wait Step   │────▶│    State     │       │
│   │   Engine     │     │  Processor   │     │   Manager    │       │
│   └──────────────┘     └──────────────┘     └──────────────┘       │
│                              │                     │                 │
│                              ▼                     ▼                 │
│                        ┌──────────────┐     ┌──────────────┐       │
│                        │   Scheduler  │     │  PostgreSQL  │       │
│                        │   (Redis +   │     │  (Supabase)  │       │
│                        │   Celery)    │     │              │       │
│                        └──────────────┘     └──────────────┘       │
│                              │                                       │
│                              ▼                                       │
│                        ┌──────────────┐                             │
│                        │    Event     │                             │
│                        │   Listener   │                             │
│                        │   Manager    │                             │
│                        └──────────────┘                             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Milestone Breakdown

### Milestone 1: Core Infrastructure (Primary Goal)

**Objective:** Establish database schema, domain models, and base service layer.

**Deliverables:**

1. **Database Migrations**
   - Create `workflow_wait_executions` table
   - Create `workflow_event_listeners` table
   - Add required indexes for performance
   - Create database functions for atomic operations

2. **Domain Models**
   - `WaitExecution` entity with value objects
   - `EventListener` entity
   - `WaitType` enum (fixed_time, until_date, until_time, for_event)
   - `WaitStatus` enum (waiting, scheduled, resumed, timeout, cancelled, error)
   - `WaitConfig` value objects per wait type

3. **Repository Layer**
   - `WaitExecutionRepository` with CRUD operations
   - `EventListenerRepository` with lookup methods
   - Query methods for scheduled job polling
   - Bulk operations for cleanup tasks

**Technical Approach:**
- Use SQLAlchemy 2.0 async ORM for database operations
- Implement repository pattern for data access abstraction
- Use Pydantic v2 models for configuration validation
- Apply database-level constraints for data integrity

**Files to Create:**
```
src/backend/domain/workflows/entities/
├── wait_execution.py
├── event_listener.py
└── wait_config.py

src/backend/infrastructure/repositories/
├── wait_execution_repository.py
└── event_listener_repository.py

migrations/versions/
└── xxxx_create_wait_step_tables.py
```

---

### Milestone 2: Wait Step Service (Primary Goal)

**Objective:** Implement core wait step processing logic.

**Deliverables:**

1. **Wait Step Service**
   - `create_wait_step()` - Initialize wait step execution
   - `calculate_resume_time()` - Compute scheduled timestamp
   - `schedule_resume()` - Create scheduled job
   - `resume_execution()` - Resume workflow from wait
   - `cancel_wait_step()` - Cancel pending wait

2. **Time Calculation Utilities**
   - Fixed time duration calculation
   - Date-based scheduling with validation
   - Time-of-day calculation with timezone
   - Business day computation

3. **Timezone Handling**
   - Timezone resolution service (contact -> account -> UTC)
   - DST-aware calculations using `pytz` or `zoneinfo`
   - Timezone validation against IANA database

**Technical Approach:**
- Use dependency injection for service composition
- Implement strategy pattern for different wait types
- Use `datetime` with `zoneinfo` for timezone operations (Python 3.9+)
- Apply factory pattern for wait configuration parsing

**Files to Create:**
```
src/backend/domain/workflows/services/
├── wait_step_service.py
├── time_calculation_service.py
└── timezone_service.py

src/backend/domain/workflows/strategies/
├── base_wait_strategy.py
├── fixed_time_strategy.py
├── until_date_strategy.py
├── until_time_strategy.py
└── for_event_strategy.py
```

---

### Milestone 3: Job Scheduling System (Primary Goal)

**Objective:** Implement reliable scheduled job processing with Redis and Celery.

**Deliverables:**

1. **Celery Task Definitions**
   - `process_scheduled_wait` - Resume workflow at scheduled time
   - `poll_scheduled_waits` - Periodic job polling task
   - `cleanup_expired_listeners` - Remove stale event listeners
   - `process_wait_timeout` - Handle event wait timeouts

2. **Redis Integration**
   - Sorted set for scheduled jobs (score = timestamp)
   - Hash maps for event listener lookup
   - Cache for frequently accessed wait states
   - Distributed locking for concurrent processing

3. **Job Processing Pipeline**
   - Atomic job claiming with distributed lock
   - Idempotent execution with deduplication
   - Retry mechanism with exponential backoff
   - Dead letter queue for failed jobs

**Technical Approach:**
- Use Celery with Redis broker for task queuing
- Implement distributed locking with Redlock algorithm
- Use Redis sorted sets for efficient time-based queries
- Apply circuit breaker pattern for external dependencies

**Files to Create:**
```
src/backend/infrastructure/tasks/
├── wait_step_tasks.py
├── scheduler_tasks.py
└── cleanup_tasks.py

src/backend/infrastructure/redis/
├── wait_scheduler.py
├── event_listener_cache.py
└── distributed_lock.py

src/backend/core/celery/
└── celery_config.py (update)
```

---

### Milestone 4: Event Listener System (Secondary Goal)

**Objective:** Implement event-based wait resume mechanism.

**Deliverables:**

1. **Event Listener Service**
   - Register event listeners for wait steps
   - Match incoming events to listeners
   - Trigger workflow resume on event match
   - Handle listener expiration and cleanup

2. **Event Consumer Integration**
   - Subscribe to email events (open, click)
   - Subscribe to SMS events (reply)
   - Subscribe to form submission events
   - Subscribe to appointment events

3. **Event Correlation**
   - Correlation ID management
   - Contact-event matching logic
   - Workflow execution context validation

**Technical Approach:**
- Use pub/sub pattern for event distribution
- Implement event sourcing for audit trail
- Use Redis pub/sub for real-time event matching
- Apply event-driven architecture patterns

**Files to Create:**
```
src/backend/domain/workflows/services/
├── event_listener_service.py
└── event_matcher_service.py

src/backend/infrastructure/events/
├── event_consumer.py
├── event_handlers/
│   ├── email_event_handler.py
│   ├── sms_event_handler.py
│   └── form_event_handler.py
└── event_publisher.py
```

---

### Milestone 5: API Layer (Secondary Goal)

**Objective:** Implement REST API endpoints for wait step management.

**Deliverables:**

1. **API Endpoints**
   - `POST /workflows/{id}/executions/{id}/wait` - Create wait step
   - `GET /workflows/executions/{id}/wait/{step_id}` - Get wait status
   - `DELETE /workflows/executions/{id}/wait/{step_id}` - Cancel wait
   - `GET /admin/workflows/waits/pending` - List pending waits

2. **Request/Response Models**
   - `CreateWaitStepRequest` with validation
   - `WaitStepResponse` with status details
   - `PendingWaitsResponse` with pagination

3. **Error Handling**
   - Custom exception classes
   - RFC 7807 Problem Details format
   - Validation error responses

**Technical Approach:**
- Use FastAPI with Pydantic validation
- Implement OpenAPI documentation
- Apply consistent error response format
- Use dependency injection for services

**Files to Create:**
```
src/backend/api/v1/workflows/
├── wait_routes.py
└── wait_schemas.py

src/backend/api/v1/admin/
└── wait_admin_routes.py
```

---

### Milestone 6: Integration and Testing (Final Goal)

**Objective:** Integrate with workflow engine and implement comprehensive tests.

**Deliverables:**

1. **Workflow Engine Integration**
   - Wait step handler in workflow executor
   - State machine integration
   - Resume callback mechanism

2. **Test Suite**
   - Unit tests for all services (target: 90% coverage)
   - Integration tests for API endpoints
   - End-to-end workflow tests
   - Performance benchmarks

3. **Monitoring and Observability**
   - Prometheus metrics for wait operations
   - Structured logging with correlation IDs
   - Health check endpoints

**Files to Create:**
```
src/backend/tests/unit/workflows/
├── test_wait_step_service.py
├── test_time_calculation_service.py
├── test_event_listener_service.py
└── test_wait_strategies.py

src/backend/tests/integration/
├── test_wait_api.py
├── test_wait_scheduling.py
└── test_event_resume.py

src/backend/tests/e2e/
└── test_workflow_with_waits.py
```

---

## Technical Approach

### Fixed Time Wait Implementation

```python
async def create_fixed_time_wait(
    self,
    execution_id: UUID,
    step_id: str,
    duration: int,
    unit: TimeUnit,
    contact_timezone: str | None = None
) -> WaitExecution:
    """Create a fixed duration wait step."""
    # Calculate resume timestamp
    now = datetime.now(timezone.utc)
    delta = self._calculate_duration_delta(duration, unit)
    scheduled_at = now + delta

    # Create wait execution record
    wait_execution = WaitExecution(
        workflow_execution_id=execution_id,
        step_id=step_id,
        wait_type=WaitType.FIXED_TIME,
        wait_config={"duration": duration, "unit": unit.value},
        scheduled_at=scheduled_at,
        timezone=contact_timezone or "UTC",
        status=WaitStatus.SCHEDULED,
    )

    # Persist to database
    await self.repository.create(wait_execution)

    # Schedule resume job in Redis
    await self.scheduler.schedule_job(
        job_id=f"{execution_id}:{step_id}",
        scheduled_at=scheduled_at,
        task="process_scheduled_wait",
        args=[str(execution_id), step_id],
    )

    return wait_execution
```

### Time-of-Day Wait Implementation

```python
async def create_time_of_day_wait(
    self,
    execution_id: UUID,
    step_id: str,
    target_time: time,
    timezone: str,
    allowed_days: list[str] | None = None
) -> WaitExecution:
    """Create a wait-until-time-of-day step."""
    # Resolve timezone
    tz = ZoneInfo(timezone)
    now_local = datetime.now(tz)

    # Calculate next occurrence
    target_datetime = datetime.combine(now_local.date(), target_time)
    target_datetime = target_datetime.replace(tzinfo=tz)

    # If time has passed today, move to next valid day
    if target_datetime <= now_local:
        target_datetime += timedelta(days=1)

    # Apply day restrictions if configured
    if allowed_days:
        target_datetime = self._find_next_allowed_day(
            target_datetime, allowed_days, tz
        )

    # Convert to UTC for storage
    scheduled_at_utc = target_datetime.astimezone(timezone.utc)

    # Create and persist wait execution
    # ... (similar to fixed_time)
```

### Event Listener Implementation

```python
async def create_event_wait(
    self,
    execution_id: UUID,
    step_id: str,
    contact_id: UUID,
    event_type: str,
    timeout_hours: int = 168,  # 7 days default
    timeout_action: str = "continue"
) -> WaitExecution:
    """Create an event-based wait step."""
    correlation_id = uuid4()
    timeout_at = datetime.now(timezone.utc) + timedelta(hours=timeout_hours)

    # Create wait execution
    wait_execution = WaitExecution(
        workflow_execution_id=execution_id,
        step_id=step_id,
        wait_type=WaitType.FOR_EVENT,
        wait_config={
            "event_type": event_type,
            "timeout_hours": timeout_hours,
            "timeout_action": timeout_action,
        },
        event_type=event_type,
        event_correlation_id=correlation_id,
        event_timeout_at=timeout_at,
        status=WaitStatus.WAITING,
    )

    await self.repository.create(wait_execution)

    # Register event listener
    listener = EventListener(
        wait_execution_id=wait_execution.id,
        event_type=event_type,
        correlation_id=correlation_id,
        contact_id=contact_id,
        workflow_execution_id=execution_id,
        expires_at=timeout_at,
    )

    await self.listener_repository.create(listener)

    # Add to Redis for fast lookup
    await self.redis.hset(
        f"workflow:event_listeners:{event_type}:{contact_id}",
        str(execution_id),
        listener.model_dump_json(),
    )

    # Schedule timeout job
    await self.scheduler.schedule_job(
        job_id=f"{execution_id}:{step_id}:timeout",
        scheduled_at=timeout_at,
        task="process_wait_timeout",
        args=[str(execution_id), step_id],
    )

    return wait_execution
```

---

## Risk Assessment

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Job scheduling delays under load | High | Medium | Implement horizontal scaling, use dedicated Redis cluster |
| Timezone calculation errors | High | Low | Comprehensive test suite, use well-tested library (zoneinfo) |
| Event listener memory leak | Medium | Medium | Implement aggressive cleanup, set expiration policies |
| Database connection exhaustion | High | Low | Connection pooling, async queries, circuit breaker |

### Operational Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Redis outage | High | Low | Redis Sentinel/Cluster, fallback to database polling |
| Celery worker crash | Medium | Medium | Worker auto-restart, job persistence, idempotent tasks |
| High volume of concurrent waits | Medium | Medium | Batch processing, rate limiting, monitoring alerts |

---

## Quality Gates

### Code Quality

- [ ] All code follows Python style guide (PEP 8, black, ruff)
- [ ] Type hints on all public functions
- [ ] Docstrings on all classes and public methods
- [ ] No linter warnings or errors

### Test Coverage

- [ ] Unit test coverage >= 85%
- [ ] Integration tests for all API endpoints
- [ ] E2E tests for happy path scenarios
- [ ] Performance benchmarks established

### Security

- [ ] Input validation on all endpoints
- [ ] SQL injection prevention verified
- [ ] RBAC enforcement tested
- [ ] Audit logging implemented

### Documentation

- [ ] API documentation generated (OpenAPI)
- [ ] Architecture decision records updated
- [ ] Runbook for operational procedures

---

## Dependencies and Prerequisites

### Required Before Implementation

1. **Workflow Engine (SPEC-WFL-005)**
   - Execution state machine
   - Step execution framework
   - Resume callback interface

2. **Infrastructure**
   - Redis cluster configured
   - Celery workers deployed
   - Database migrations system

3. **Event System**
   - Email tracking events
   - SMS delivery events
   - Form submission events

### Development Environment

```bash
# Required services
docker compose up -d postgres redis

# Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start Celery worker
celery -A src.backend.core.celery worker -l info

# Start Celery beat
celery -A src.backend.core.celery beat -l info
```

---

## Traceability

| Artifact | Reference |
|----------|-----------|
| SPEC Document | .moai/specs/SPEC-WFL-006/spec.md |
| Acceptance Criteria | .moai/specs/SPEC-WFL-006/acceptance.md |
| Parent Plan | specs/workflows/plan.md |
| Product Requirements | .moai/project/product.md |
| Technical Stack | .moai/project/tech.md |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-26 | manager-spec | Initial implementation plan |
