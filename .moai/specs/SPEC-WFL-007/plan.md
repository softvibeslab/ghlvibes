# SPEC-WFL-007: Goal Tracking - Implementation Plan

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-007 |
| **Title** | Goal Tracking |
| **Module** | workflows |
| **Domain** | automation |
| **Priority** | Medium |

---

## Implementation Overview

Goal Tracking requires a robust event-driven architecture to monitor contact activities across multiple modules and trigger workflow exits when goals are achieved. The implementation follows a layered approach with clear separation between event listening, goal evaluation, and workflow control.

---

## Technical Approach

### Architecture Pattern

The implementation uses an **Event-Driven Architecture** with the following components:

1. **Goal Configuration Layer** - API and persistence for goal settings
2. **Event Listener Layer** - Event bus subscriptions for goal-related events
3. **Goal Evaluation Layer** - Logic to match events against goal criteria
4. **Workflow Control Layer** - Integration with workflow engine for exit handling

### Component Diagram

```
+------------------+     +-------------------+     +------------------+
|   Goal Config    |     |   Event Listeners |     |  Workflow Engine |
|      API         |     |    (per goal type)|     |   Integration    |
+------------------+     +-------------------+     +------------------+
        |                        |                        |
        v                        v                        v
+------------------+     +-------------------+     +------------------+
|   Goal Config    |     | Goal Evaluation   |     | Workflow Exit    |
|   Repository     |     |    Service        |     |    Service       |
+------------------+     +-------------------+     +------------------+
        |                        |                        |
        +------------------------+------------------------+
                                 |
                                 v
                    +------------------------+
                    |     PostgreSQL/Redis   |
                    |   (Persistence & Pub/Sub)|
                    +------------------------+
```

### Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| API Framework | FastAPI | Async support, OpenAPI generation |
| Database | PostgreSQL (Supabase) | Relational data, JSONB for criteria |
| Event Bus | Redis Pub/Sub | Low latency event distribution |
| Background Tasks | Celery | Reliable async processing |
| Caching | Redis | Active listener state caching |

---

## Milestones

### Primary Goal: Core Goal Configuration

**Deliverables:**
- Goal configuration data models and database schema
- CRUD API endpoints for workflow goals
- Goal configuration validation service
- Unit tests for configuration layer

**Key Tasks:**
1. Create `workflow_goals` database migration
2. Implement `GoalConfig` Pydantic models
3. Create `GoalConfigRepository` with CRUD operations
4. Implement `GoalConfigService` with business logic
5. Create FastAPI router with goal endpoints
6. Add validation for goal type and criteria
7. Write unit tests for all components

**Dependencies:** SPEC-WFL-001 (Workflow base tables)

### Secondary Goal: Event Listener Infrastructure

**Deliverables:**
- Base event listener abstract class
- Listener registration and management service
- Redis-based listener state management
- Event subscription setup for all goal types

**Key Tasks:**
1. Create abstract `GoalEventListener` base class
2. Implement `GoalListenerManager` for registration
3. Create Redis-based listener state store
4. Implement listeners for each goal type:
   - `TagAddedGoalListener`
   - `PurchaseMadeGoalListener`
   - `AppointmentBookedGoalListener`
   - `FormSubmittedGoalListener`
   - `PipelineStageGoalListener`
5. Add event bus integration with Redis Pub/Sub
6. Write integration tests for listener lifecycle

**Dependencies:** Primary Goal complete

### Tertiary Goal: Goal Evaluation and Workflow Exit

**Deliverables:**
- Goal criteria evaluation engine
- Workflow exit service integration
- Goal achievement logging and tracking
- Pending action cancellation logic

**Key Tasks:**
1. Create `GoalEvaluator` service with criteria matching
2. Implement type-specific evaluation strategies:
   - Tag matching (exact or pattern)
   - Purchase criteria (product, amount)
   - Appointment criteria (calendar, service)
   - Form ID matching
   - Pipeline stage matching
3. Create `WorkflowGoalExitService` for exit handling
4. Implement pending action cancellation
5. Add wait step cancellation integration
6. Create `goal_achievements` logging table
7. Write end-to-end tests for goal flow

**Dependencies:** Secondary Goal complete, SPEC-WFL-005, SPEC-WFL-006

### Final Goal: Analytics and Production Readiness

**Deliverables:**
- Goal analytics aggregation queries
- Goal statistics API endpoints
- Performance optimization
- Documentation and monitoring

**Key Tasks:**
1. Create analytics queries for goal metrics
2. Implement `GoalAnalyticsService`
3. Add caching for frequently accessed stats
4. Create monitoring dashboards
5. Performance test with high volume
6. Add rate limiting for analytics endpoints
7. Write API documentation
8. Create operational runbook

**Dependencies:** All previous goals complete

---

## Architecture Design

### Domain Layer

```python
# Domain Entities
class GoalType(str, Enum):
    TAG_ADDED = "tag_added"
    PURCHASE_MADE = "purchase_made"
    APPOINTMENT_BOOKED = "appointment_booked"
    FORM_SUBMITTED = "form_submitted"
    PIPELINE_STAGE_REACHED = "pipeline_stage_reached"

class WorkflowGoal:
    id: UUID
    workflow_id: UUID
    tenant_id: UUID
    goal_type: GoalType
    criteria: GoalCriteria
    is_active: bool

class GoalAchievement:
    id: UUID
    workflow_id: UUID
    contact_id: UUID
    goal_config_id: UUID
    achieved_at: datetime
    trigger_event: dict
```

### Application Layer

```python
# Services
class GoalConfigService:
    async def create_goal(workflow_id, goal_data) -> WorkflowGoal
    async def update_goal(goal_id, goal_data) -> WorkflowGoal
    async def delete_goal(goal_id) -> bool
    async def get_workflow_goals(workflow_id) -> List[WorkflowGoal]

class GoalEvaluationService:
    async def evaluate_event(event_type, event_data, contact_id) -> bool
    async def get_matching_goals(contact_id, event_type) -> List[WorkflowGoal]

class WorkflowGoalExitService:
    async def exit_on_goal(enrollment_id, goal_id, trigger_event) -> bool
    async def cancel_pending_actions(enrollment_id) -> int
```

### Infrastructure Layer

```python
# Repositories
class GoalConfigRepository:
    async def create(goal: WorkflowGoal) -> WorkflowGoal
    async def get_by_id(goal_id: UUID) -> Optional[WorkflowGoal]
    async def get_by_workflow(workflow_id: UUID) -> List[WorkflowGoal]
    async def update(goal: WorkflowGoal) -> WorkflowGoal
    async def delete(goal_id: UUID) -> bool

# Event Listeners
class BaseGoalListener(ABC):
    @abstractmethod
    async def on_event(self, event_data: dict) -> None

class TagAddedGoalListener(BaseGoalListener):
    async def on_event(self, event_data: dict) -> None
```

### API Layer

```python
# FastAPI Router
router = APIRouter(prefix="/api/v1/workflows/{workflow_id}/goals")

@router.post("/", response_model=GoalResponse)
async def create_goal(workflow_id: UUID, goal: GoalCreate)

@router.get("/", response_model=GoalListResponse)
async def list_goals(workflow_id: UUID)

@router.patch("/{goal_id}", response_model=GoalResponse)
async def update_goal(workflow_id: UUID, goal_id: UUID, goal: GoalUpdate)

@router.delete("/{goal_id}")
async def delete_goal(workflow_id: UUID, goal_id: UUID)

@router.get("/stats", response_model=GoalStatsResponse)
async def get_goal_stats(workflow_id: UUID)
```

---

## Event Flow Design

### Goal Event Processing Pipeline

```
1. External Event Occurs (e.g., contact tagged)
   |
   v
2. Event Published to Redis Pub/Sub
   |
   v
3. Goal Listener Service Receives Event
   |
   v
4. Lookup Active Workflow Enrollments for Contact
   |
   v
5. Get Goal Configurations for Those Workflows
   |
   v
6. Evaluate Each Goal's Criteria Against Event
   |
   v
7. If Match Found:
   |-- Log Goal Achievement
   |-- Trigger Workflow Exit
   |-- Cancel Pending Actions
   |-- Emit Goal Achieved Event
   |
   v
8. Update Analytics Counters
```

### Event Subscription Pattern

```python
class GoalEventSubscriber:
    def __init__(self, redis_client, goal_service, exit_service):
        self.redis = redis_client
        self.goal_service = goal_service
        self.exit_service = exit_service

    async def subscribe(self):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(
            "contact.tag.added",
            "payment.completed",
            "appointment.booked",
            "form.submitted",
            "pipeline.stage.changed"
        )

        async for message in pubsub.listen():
            await self.handle_event(message)

    async def handle_event(self, message):
        event_type = message["channel"]
        event_data = json.loads(message["data"])

        contact_id = event_data["contact_id"]
        enrollments = await self.get_active_enrollments(contact_id)

        for enrollment in enrollments:
            goals = await self.goal_service.get_workflow_goals(
                enrollment.workflow_id
            )
            for goal in goals:
                if await self.evaluate_goal(goal, event_data):
                    await self.exit_service.exit_on_goal(
                        enrollment.id,
                        goal.id,
                        event_data
                    )
```

---

## Database Migration

```sql
-- Migration: 20260126_create_workflow_goals.sql

-- Create goal type enum
CREATE TYPE goal_type AS ENUM (
    'tag_added',
    'purchase_made',
    'appointment_booked',
    'form_submitted',
    'pipeline_stage_reached'
);

-- Workflow Goals Configuration Table
CREATE TABLE workflow_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    goal_type goal_type NOT NULL,
    criteria JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),

    CONSTRAINT uq_workflow_goal UNIQUE (workflow_id, goal_type, criteria)
);

-- Indexes for efficient querying
CREATE INDEX idx_workflow_goals_workflow ON workflow_goals(workflow_id);
CREATE INDEX idx_workflow_goals_tenant ON workflow_goals(tenant_id);
CREATE INDEX idx_workflow_goals_active ON workflow_goals(is_active) WHERE is_active = true;

-- Goal Achievements Log Table
CREATE TABLE workflow_goal_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id),
    workflow_enrollment_id UUID NOT NULL REFERENCES workflow_enrollments(id),
    contact_id UUID NOT NULL REFERENCES contacts(id),
    goal_config_id UUID NOT NULL REFERENCES workflow_goals(id),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    goal_type goal_type NOT NULL,
    achieved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    trigger_event JSONB,
    metadata JSONB DEFAULT '{}',

    CONSTRAINT uq_achievement UNIQUE (workflow_enrollment_id, goal_config_id)
);

-- Indexes for analytics and lookups
CREATE INDEX idx_achievements_workflow ON workflow_goal_achievements(workflow_id);
CREATE INDEX idx_achievements_contact ON workflow_goal_achievements(contact_id);
CREATE INDEX idx_achievements_date ON workflow_goal_achievements(achieved_at);
CREATE INDEX idx_achievements_tenant ON workflow_goal_achievements(tenant_id);

-- Trigger for updated_at
CREATE TRIGGER update_workflow_goals_updated_at
    BEFORE UPDATE ON workflow_goals
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security
ALTER TABLE workflow_goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_goal_achievements ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_goals ON workflow_goals
    FOR ALL USING (tenant_id = current_setting('app.tenant_id')::uuid);

CREATE POLICY tenant_isolation_achievements ON workflow_goal_achievements
    FOR ALL USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

---

## Risks and Mitigations

### Risk 1: Event Processing Latency

**Risk:** High event volume causing delays in goal detection

**Mitigation:**
- Implement event batching for high-volume periods
- Use Redis Streams for reliable event delivery
- Add horizontal scaling for listener workers
- Implement circuit breaker for downstream dependencies

### Risk 2: Duplicate Goal Achievements

**Risk:** Same goal achieved multiple times due to race conditions

**Mitigation:**
- Use database unique constraint on (enrollment_id, goal_config_id)
- Implement idempotent goal achievement processing
- Add Redis-based distributed locking for concurrent events

### Risk 3: Orphaned Event Listeners

**Risk:** Listeners remain active after workflow deactivation

**Mitigation:**
- Implement listener lifecycle management
- Add periodic cleanup job for stale listeners
- Use TTL-based listener expiration in Redis
- Add monitoring for listener count per workflow

### Risk 4: Cross-Tenant Data Leakage

**Risk:** Goal events processed for wrong tenant

**Mitigation:**
- Enforce tenant_id in all queries via RLS
- Validate tenant context in event handlers
- Add tenant ID to all event payloads
- Implement audit logging for cross-tenant operations

---

## Testing Strategy

### Unit Tests

- Goal configuration CRUD operations
- Goal criteria validation
- Goal type-specific evaluation logic
- Workflow exit service logic

### Integration Tests

- End-to-end goal configuration flow
- Event listener registration and cleanup
- Goal achievement with workflow exit
- Analytics aggregation accuracy

### Performance Tests

- Event processing throughput (target: 10,000 events/sec)
- Goal evaluation latency (target: <100ms)
- Listener scalability (target: 100,000 concurrent)

---

## Monitoring and Observability

### Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `goal.events.received` | Counter | Events received by goal service |
| `goal.evaluations.total` | Counter | Goal evaluations performed |
| `goal.achievements.total` | Counter | Goals achieved |
| `goal.evaluation.latency` | Histogram | Time to evaluate goal |
| `goal.listeners.active` | Gauge | Active goal listeners |

### Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| High Goal Evaluation Latency | p95 > 500ms | Warning |
| Goal Processing Backlog | Queue > 10,000 | Critical |
| Listener Registration Failures | Error rate > 1% | Warning |

---

## Implementation Notes

### File Structure

```
backend/
  app/
    modules/
      workflows/
        goals/
          __init__.py
          models.py          # Pydantic models
          entities.py        # Domain entities
          repository.py      # Database operations
          service.py         # Business logic
          router.py          # API endpoints
          validators.py      # Validation logic
          listeners/
            __init__.py
            base.py          # Abstract listener
            tag_added.py
            purchase_made.py
            appointment_booked.py
            form_submitted.py
            pipeline_stage.py
          evaluators/
            __init__.py
            base.py          # Abstract evaluator
            criteria.py      # Criteria matching
          exit/
            __init__.py
            service.py       # Exit handling
          analytics/
            __init__.py
            service.py       # Analytics queries
```

### Configuration

```python
# config/goals.py
class GoalConfig:
    # Event processing
    EVENT_BATCH_SIZE: int = 100
    EVENT_PROCESSING_TIMEOUT_MS: int = 5000

    # Listener management
    LISTENER_TTL_SECONDS: int = 86400  # 24 hours
    LISTENER_CLEANUP_INTERVAL_SECONDS: int = 3600

    # Analytics
    STATS_CACHE_TTL_SECONDS: int = 300  # 5 minutes
```
