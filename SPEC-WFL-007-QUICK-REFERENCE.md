# SPEC-WFL-007 Goal Tracking - Quick Reference Guide

## Quick Start

### 1. Database Migration
```bash
cd backend
alembic upgrade head
```

### 2. API Endpoints

**Create Goal:**
```bash
POST /api/v1/workflows/{workflow_id}/goals
Content-Type: application/json

{
  "goal_type": "tag_added",
  "criteria": {
    "tag_id": "uuid",
    "tag_name": "Purchased"
  }
}
```

**List Goals:**
```bash
GET /api/v1/workflows/{workflow_id}/goals?offset=0&limit=50
```

**Get Statistics:**
```bash
GET /api/v1/workflows/{workflow_id}/goals/stats
```

### 3. Goal Types

| Type | Event | Criteria Example |
|------|-------|------------------|
| `tag_added` | contact.tag.added | `{"tag_id": "uuid"}` or `{"tag_name": "Purchased"}` |
| `purchase_made` | payment.completed | `{"min_amount": 100.0}` or `{"any_purchase": true}` |
| `appointment_booked` | appointment.booked | `{"calendar_id": "uuid"}` or `{"any_appointment": true}` |
| `form_submitted` | form.submitted | `{"form_id": "uuid"}` |
| `pipeline_stage_reached` | pipeline.stage.changed | `{"pipeline_id": "uuid", "stage_id": "uuid"}` |

### 4. Service Usage

**Detect Goal Achievement:**
```python
from src.workflows.application.goal_detection_service import GoalDetectionService

service = GoalDetectionService(
    goal_repository=goal_repo,
    achievement_repository=achievement_repo,
)

result = await service.evaluate_event(
    workflow_id=workflow_id,
    contact_id=contact_id,
    account_id=account_id,
    event_type="contact.tag.added",
    event_data={"tag_id": tag_id, "tag_name": "Purchased"},
)

if result.goal_achieved and result.should_exit_workflow:
    # Exit contact from workflow
    await exit_workflow(contact_id, workflow_id)
```

**Record Achievement:**
```python
from src.workflows.application.goal_detection_service import GoalAchievementService

service = GoalAchievementService(
    achievement_repository=achievement_repo,
)

await service.record_achievement(
    workflow_id=workflow_id,
    workflow_enrollment_id=enrollment_id,
    contact_id=contact_id,
    goal_config_id=goal_config_id,
    account_id=account_id,
    goal_type=GoalType.TAG_ADDED,
    trigger_event={"tag_id": tag_id},
    metadata={"source": "webhook"},
)
```

## File Locations

### Domain Layer
- `/backend/src/workflows/domain/goal_entities.py` - GoalConfig, GoalAchievement, GoalCriteria, GoalType

### Application Layer
- `/backend/src/workflows/application/goal_dtos.py` - All DTOs
- `/backend/src/workflows/application/use_cases/create_goal.py`
- `/backend/src/workflows/application/use_cases/update_goal.py`
- `/backend/src/workflows/application/use_cases/delete_goal.py`
- `/backend/src/workflows/application/use_cases/list_goals.py`
- `/backend/src/workflows/application/use_cases/get_goal_stats.py`
- `/backend/src/workflows/application/goal_detection_service.py` - GoalDetectionService, GoalAchievementService

### Infrastructure Layer
- `/backend/src/workflows/infrastructure/goal_models.py` - GoalModel, GoalAchievementModel
- `/backend/src/workflows/infrastructure/goal_repository.py` - PostgresGoalRepository, PostgresGoalAchievementRepository
- `/backend/alembic/versions/2025_01_26_001_create_goal_tracking.py` - Database migration

### Presentation Layer
- `/backend/src/workflows/presentation/goal_routes.py` - FastAPI routes

### Tests
- `/backend/tests/workflows/characterization/test_goal_entities_behavior.py` - Characterization tests (17 tests)
- `/backend/tests/workflows/unit/test_goal_entities.py` - Domain entity tests (27 tests)
- `/backend/tests/workflows/unit/test_goal_use_cases.py` - Use case tests (10 tests)
- `/backend/tests/workflows/unit/test_goal_detection_service.py` - Service tests (10 tests)
- `/backend/tests/workflows/integration/test_goal_repositories.py` - Repository integration tests (13 tests)
- `/backend/tests/workflows/acceptance/test_ac007_goal_tracking.py` - Acceptance tests (13 tests)

## Running Tests

### All Tests
```bash
cd backend
pytest tests/workflows/ -v
```

### Unit Tests Only
```bash
pytest tests/workflows/unit/ -v
```

### Integration Tests Only
```bash
pytest tests/workflows/integration/ -v
```

### Acceptance Tests Only
```bash
pytest tests/workflows/acceptance/ -v
```

### With Coverage
```bash
pytest tests/workflows/ --cov=src/workflows --cov-report=html
```

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│  Presentation Layer (FastAPI)           │
│  goal_routes.py (5 endpoints)           │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  Application Layer                      │
│  - Use Cases (5)                        │
│  - DTOs (8)                             │
│  - GoalDetectionService                 │
│  - GoalAchievementService               │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  Domain Layer                           │
│  - GoalConfig (Aggregate Root)          │
│  - GoalAchievement                      │
│  - GoalCriteria (Value Object)          │
│  - GoalType (Enum)                      │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  Infrastructure Layer                   │
│  - GoalModel, GoalAchievementModel      │
│  - PostgresGoalRepository               │
│  - PostgresGoalAchievementRepository    │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  PostgreSQL Database                    │
│  - workflow_goals table                 │
│  - workflow_goal_achievements table     │
└─────────────────────────────────────────┘
```

## Data Models

### GoalConfig (Domain Entity)
```python
@dataclass
class GoalConfig:
    id: UUID
    workflow_id: UUID
    account_id: UUID
    goal_type: GoalType
    criteria: GoalCriteria
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None
    updated_by: UUID | None
```

### GoalAchievement (Domain Entity)
```python
@dataclass
class GoalAchievement:
    id: UUID
    workflow_id: UUID
    workflow_enrollment_id: UUID
    contact_id: UUID
    goal_config_id: UUID
    account_id: UUID
    goal_type: GoalType
    achieved_at: datetime
    trigger_event: dict
    metadata: dict
```

### GoalCriteria (Value Object)
```python
@dataclass(frozen=True)
class GoalCriteria:
    goal_type: GoalType
    criteria: dict[str, Any]
    # Validates criteria based on goal_type
```

## Key Features

✅ **5 Goal Types:** tag_added, purchase_made, appointment_booked, form_submitted, pipeline_stage_reached
✅ **Event Detection:** Real-time goal achievement detection from events
✅ **Duplicate Prevention:** Prevents recording same goal multiple times
✅ **Multi-tenancy:** Full tenant isolation at database and domain levels
✅ **Audit Trail:** Created/updated timestamps and user tracking
✅ **Optimistic Locking:** Version field prevents concurrent modification conflicts
✅ **Statistics:** Conversion rates, time to goal, breakdown by goal type
✅ **Validation:** Domain-level validation for goal criteria
✅ **Async/Await:** Full async support for scalability
✅ **RESTful API:** Clean REST API with OpenAPI documentation

## TRUST 5 Compliance

✅ **Tested:** 90 tests, 85%+ coverage
✅ **Readable:** Clear naming, English comments
✅ **Unified:** Consistent patterns, ruff formatting
✅ **Secured:** Tenant isolation, input validation
✅ **Trackable:** Audit trail, version tracking

## Integration Checklist

- [x] Domain entities implemented
- [x] Application layer (use cases, DTOs, services)
- [x] Infrastructure layer (models, repositories)
- [x] Presentation layer (FastAPI routes)
- [x] Database migration created
- [x] Unit tests (47 tests)
- [x] Integration tests (13 tests)
- [x] Acceptance tests (13 tests)
- [x] Characterization tests (17 tests)
- [ ] Apply migration to database
- [ ] Register routes with FastAPI app
- [ ] Integrate with workflow engine (exit on goal)
- [ ] Implement event listener registration
- [ ] Add external event webhooks
- [ ] Performance testing
- [ ] Load testing

## Dependencies

**Internal:**
- Workflow Engine (SPEC-WFL-005)
- Contact Management (SPEC-CRM-001)
- Appointment System (SPEC-BKG-001)
- Form System (SPEC-FNL-002)
- Pipeline System (SPEC-CRM-005)
- Payment System (SPEC-PAY-001)

**External:**
- PostgreSQL 14+
- Redis (for event pub/sub)
- SQLAlchemy 2.0+
- FastAPI 0.115+
- Pydantic 2.10+

## Support

For questions or issues:
1. Check implementation report: `SPEC-WFL-007-IMPLEMENTATION-REPORT.md`
2. Review acceptance tests: `tests/workflows/acceptance/test_ac007_goal_tracking.py`
3. See API docs: `/docs` (Swagger UI) when running

## Version

**SPEC Version:** 1.0.0
**Implementation Date:** 2026-02-06
**DDD Cycle:** ANALYZE ✅ → PRESERVE ✅ → IMPROVE ✅
**Status:** ✅ **READY FOR INTEGRATION**
