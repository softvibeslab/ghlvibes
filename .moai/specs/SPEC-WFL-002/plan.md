# SPEC-WFL-002: Configure Trigger - Implementation Plan

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-002 |
| **Title** | Configure Trigger |
| **Related SPEC** | [spec.md](./spec.md) |
| **Acceptance Criteria** | [acceptance.md](./acceptance.md) |

---

## Implementation Overview

This plan outlines the development approach for implementing the workflow trigger configuration system. The implementation follows the DDD (Domain-Driven Development) methodology with ANALYZE-PRESERVE-IMPROVE cycles.

---

## Milestones

### Primary Goals (Must Complete)

#### Milestone 1: Domain Layer Foundation

**Objective:** Establish core domain models and business logic for trigger management.

**Deliverables:**
- Trigger entity with all trigger types enumeration
- Filter condition value objects
- Trigger validation service
- Domain events for trigger lifecycle

**Technical Approach:**
- Define `Trigger` aggregate root with embedded `FilterCondition` value objects
- Implement trigger type registry pattern for extensibility
- Create domain validation rules using Pydantic models
- Define domain events: `TriggerConfigured`, `TriggerActivated`, `TriggerDeactivated`

**Files to Create:**
- `src/backend/domain/workflows/entities/trigger.py`
- `src/backend/domain/workflows/value_objects/filter_condition.py`
- `src/backend/domain/workflows/services/trigger_validator.py`
- `src/backend/domain/workflows/events/trigger_events.py`

---

#### Milestone 2: Infrastructure Layer - Database

**Objective:** Implement database schema and repository for trigger persistence.

**Deliverables:**
- SQLAlchemy models for trigger tables
- Alembic migration scripts
- Trigger repository implementation
- Database indexes for query optimization

**Technical Approach:**
- Create SQLAlchemy 2.0 async models with JSONB support
- Implement repository pattern with async session management
- Add composite indexes on (workflow_id, trigger_type, is_active)
- Implement soft delete with deleted_at timestamp

**Files to Create:**
- `src/backend/infrastructure/database/models/trigger.py`
- `src/backend/infrastructure/database/migrations/versions/xxx_create_trigger_tables.py`
- `src/backend/infrastructure/repositories/trigger_repository.py`

**Database Migration:**
```sql
-- workflow_triggers table
CREATE TABLE workflow_triggers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    trigger_type VARCHAR(50) NOT NULL,
    trigger_event VARCHAR(50) NOT NULL,
    filters JSONB DEFAULT '{}',
    settings JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_triggers_workflow_active ON workflow_triggers(workflow_id, is_active) WHERE deleted_at IS NULL;
CREATE INDEX idx_triggers_type_event ON workflow_triggers(trigger_type, trigger_event) WHERE is_active = true;

-- trigger_execution_logs table
CREATE TABLE trigger_execution_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trigger_id UUID NOT NULL REFERENCES workflow_triggers(id),
    contact_id UUID NOT NULL,
    event_data JSONB NOT NULL,
    matched BOOLEAN NOT NULL,
    enrolled BOOLEAN NOT NULL,
    failure_reason TEXT,
    executed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_trigger_logs_trigger ON trigger_execution_logs(trigger_id, executed_at DESC);
```

---

#### Milestone 3: Application Layer - Use Cases

**Objective:** Implement application services and use cases for trigger operations.

**Deliverables:**
- Configure trigger use case
- Update trigger use case
- Delete trigger use case
- Get trigger use case
- Trigger validation middleware

**Technical Approach:**
- Implement command/query separation (CQRS-lite pattern)
- Create DTOs for API request/response transformation
- Add authorization checks using dependency injection
- Implement idempotency for trigger configuration

**Files to Create:**
- `src/backend/application/workflows/use_cases/configure_trigger.py`
- `src/backend/application/workflows/use_cases/update_trigger.py`
- `src/backend/application/workflows/use_cases/delete_trigger.py`
- `src/backend/application/workflows/use_cases/get_trigger.py`
- `src/backend/application/workflows/dtos/trigger_dto.py`

---

#### Milestone 4: Presentation Layer - API Endpoints

**Objective:** Expose RESTful API endpoints for trigger management.

**Deliverables:**
- FastAPI router for trigger endpoints
- Request/response schemas with OpenAPI documentation
- Error handling and validation responses
- Rate limiting middleware

**Technical Approach:**
- Create FastAPI router with dependency injection
- Implement Pydantic schemas for request validation
- Add comprehensive OpenAPI documentation
- Implement RFC 7807 Problem Details for errors

**Files to Create:**
- `src/backend/api/v1/routes/workflow_triggers.py`
- `src/backend/api/v1/schemas/trigger_schemas.py`
- `src/backend/api/v1/dependencies/trigger_deps.py`

**API Contract:**
```python
@router.post("/{workflow_id}/trigger", status_code=201)
async def configure_trigger(
    workflow_id: UUID,
    request: ConfigureTriggerRequest,
    current_user: User = Depends(get_current_user),
    trigger_service: TriggerService = Depends(get_trigger_service)
) -> TriggerResponse:
    """Configure a trigger for a workflow."""
    ...
```

---

### Secondary Goals (Should Complete)

#### Milestone 5: Event Listening Infrastructure

**Objective:** Implement event bus integration for trigger evaluation.

**Deliverables:**
- Event bus abstraction layer
- Redis Pub/Sub implementation
- Event handlers for each trigger type
- Trigger evaluation engine

**Technical Approach:**
- Create abstract event bus interface for testability
- Implement Redis Streams for durable event processing
- Create trigger evaluator service with filter matching
- Implement async event handlers with error recovery

**Files to Create:**
- `src/backend/infrastructure/events/event_bus.py`
- `src/backend/infrastructure/events/redis_event_bus.py`
- `src/backend/infrastructure/events/handlers/trigger_handler.py`
- `src/backend/domain/workflows/services/trigger_evaluator.py`

**Event Handler Pattern:**
```python
class TriggerEventHandler:
    async def handle_contact_created(self, event: ContactCreatedEvent):
        triggers = await self.repository.find_active_by_event("contact_created")
        for trigger in triggers:
            if self.evaluator.matches(trigger.filters, event.data):
                await self.workflow_executor.enroll(
                    workflow_id=trigger.workflow_id,
                    contact_id=event.contact_id,
                    trigger_id=trigger.id
                )
```

---

#### Milestone 6: Time-Based Trigger Scheduler

**Objective:** Implement scheduling system for time-based triggers.

**Deliverables:**
- Scheduler service using Celery Beat
- Birthday/anniversary trigger jobs
- Recurring schedule trigger jobs
- Scheduled date trigger jobs

**Technical Approach:**
- Use Celery Beat for periodic task scheduling
- Implement contact query for date matching
- Add timezone-aware scheduling
- Create batch processing for large contact sets

**Files to Create:**
- `src/backend/infrastructure/scheduler/trigger_scheduler.py`
- `src/backend/infrastructure/scheduler/tasks/time_triggers.py`

---

### Final Goals (Nice to Have)

#### Milestone 7: Trigger Testing and Preview

**Objective:** Enable trigger testing and contact preview functionality.

**Deliverables:**
- Trigger test endpoint with simulation
- Contact preview query
- Estimated match count
- Test execution logging

**Technical Approach:**
- Implement dry-run mode for trigger evaluation
- Create efficient count queries with EXPLAIN ANALYZE optimization
- Add preview caching with Redis

**Files to Create:**
- `src/backend/application/workflows/use_cases/test_trigger.py`
- `src/backend/application/workflows/use_cases/preview_trigger.py`

---

### Optional Goals

#### Milestone 8: Advanced Features

**Objective:** Implement optional advanced trigger features.

**Deliverables:**
- Trigger analytics dashboard data
- Loop detection algorithm
- Trigger templates

---

## Technical Approach

### Architecture Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                      Presentation Layer                          │
│              (FastAPI Routes, Pydantic Schemas)                  │
├─────────────────────────────────────────────────────────────────┤
│                      Application Layer                           │
│              (Use Cases, DTOs, Application Services)             │
├─────────────────────────────────────────────────────────────────┤
│                        Domain Layer                              │
│          (Entities, Value Objects, Domain Services)              │
├─────────────────────────────────────────────────────────────────┤
│                     Infrastructure Layer                         │
│      (Repositories, Event Bus, External Services, Database)      │
└─────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

1. **Trigger Type Registry Pattern**
   - Use registry pattern for trigger type handlers
   - Enable easy extension for new trigger types
   - Centralize trigger-specific logic

2. **Filter Evaluation Engine**
   - JSON-based filter storage for flexibility
   - Compile filters to SQL WHERE clauses for performance
   - Support complex AND/OR logic combinations

3. **Event Sourcing for Trigger Logs**
   - Store all trigger evaluations for debugging
   - Enable replay for testing
   - Support analytics queries

4. **Multi-tenant Isolation**
   - Account ID in all queries
   - Row-level security policies
   - Event partitioning by account

### Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| API Framework | FastAPI | Latest |
| ORM | SQLAlchemy | 2.0+ |
| Validation | Pydantic | 2.9+ |
| Database | PostgreSQL (Supabase) | 16 |
| Event Bus | Redis Streams | 7+ |
| Task Queue | Celery | 5.3+ |
| Testing | pytest-asyncio | Latest |

---

## Risk Assessment

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Event bus latency | High | Medium | Implement event batching, use Redis Streams |
| Filter evaluation performance | High | Medium | Index optimization, query caching |
| Trigger loop detection complexity | Medium | Low | Implement depth-limited evaluation |

### Dependency Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| SPEC-WFL-001 not complete | Blocking | Low | Stub workflow entity if needed |
| Redis unavailability | High | Low | Implement fallback to database queuing |

---

## Quality Gates

### Code Quality

- [ ] 85%+ test coverage for trigger module
- [ ] Zero LSP errors
- [ ] All Pydantic models with complete type hints
- [ ] OpenAPI documentation complete

### Performance

- [ ] Trigger evaluation < 100ms P95
- [ ] API response time < 200ms P95
- [ ] Support 1000 events/second throughput

### Security

- [ ] Input validation on all endpoints
- [ ] SQL injection prevention verified
- [ ] Authorization checks on all operations
- [ ] Sensitive data masking in logs

---

## Traceability

| Milestone | Requirements Covered |
|-----------|---------------------|
| Milestone 1 | REQ-U-001, REQ-U-002, REQ-N-003 |
| Milestone 2 | REQ-U-003, REQ-U-004 |
| Milestone 3 | REQ-E-001 to REQ-E-026 |
| Milestone 4 | All REQ-E requirements |
| Milestone 5 | REQ-S-001, REQ-S-002, REQ-N-002 |
| Milestone 6 | REQ-E-023 to REQ-E-026, REQ-S-003 |
| Milestone 7 | REQ-O-001, REQ-O-002 |
