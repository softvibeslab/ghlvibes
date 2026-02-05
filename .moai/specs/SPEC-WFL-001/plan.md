# SPEC-WFL-001: Implementation Plan

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-001 |
| **Title** | Create Workflow |
| **Phase** | Run |

---

## Implementation Strategy

### Approach: Domain-Driven Development (DDD)

Following the ANALYZE-PRESERVE-IMPROVE cycle:

1. **ANALYZE**: Understand existing codebase structure and patterns
2. **PRESERVE**: Create characterization tests for any existing code
3. **IMPROVE**: Implement new functionality with comprehensive tests

---

## Milestones

### Primary Goal: Core Workflow Creation

**Deliverables:**
- Database schema and migrations
- Domain entities and value objects
- Repository implementation
- API endpoint with validation

**Quality Gates:**
- Unit tests for domain logic
- Integration tests for repository
- API tests for endpoint

### Secondary Goal: Security and Authorization

**Deliverables:**
- Authentication middleware integration
- Permission checking implementation
- Rate limiting middleware
- Audit logging

**Quality Gates:**
- Security tests for auth flows
- Rate limit verification tests
- Audit log verification

### Final Goal: Integration and Documentation

**Deliverables:**
- OpenAPI documentation
- Frontend integration hooks
- Error handling refinement
- Performance optimization

**Quality Gates:**
- End-to-end tests
- Performance benchmarks
- Documentation completeness

---

## Technical Approach

### Directory Structure

```
backend/
├── src/
│   └── workflows/
│       ├── __init__.py
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── entities.py          # Workflow entity
│       │   ├── value_objects.py     # WorkflowName, WorkflowStatus
│       │   └── exceptions.py        # Domain exceptions
│       ├── application/
│       │   ├── __init__.py
│       │   ├── use_cases/
│       │   │   ├── __init__.py
│       │   │   └── create_workflow.py
│       │   ├── dtos.py              # Request/Response DTOs
│       │   └── services.py          # Application services
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   ├── models.py            # SQLAlchemy models
│       │   ├── repositories.py      # Repository implementations
│       │   └── migrations/
│       │       └── versions/
│       │           └── xxxx_create_workflows_table.py
│       └── presentation/
│           ├── __init__.py
│           ├── routes.py            # FastAPI routes
│           ├── dependencies.py      # Dependency injection
│           └── middleware.py        # Rate limiting, auth
└── tests/
    └── workflows/
        ├── __init__.py
        ├── unit/
        │   ├── test_entities.py
        │   └── test_value_objects.py
        ├── integration/
        │   └── test_repositories.py
        └── e2e/
            └── test_api.py
```

### Implementation Phases

#### Phase 1: Domain Layer

**Files to Create:**
- `domain/entities.py` - Workflow aggregate root
- `domain/value_objects.py` - WorkflowName, WorkflowStatus
- `domain/exceptions.py` - WorkflowNameTooShortError, etc.

**Key Implementation:**

```python
# domain/entities.py
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from .value_objects import WorkflowName, WorkflowStatus

@dataclass
class Workflow:
    """Workflow aggregate root."""
    id: UUID
    account_id: UUID
    name: WorkflowName
    status: WorkflowStatus
    created_by: UUID
    updated_by: UUID
    description: str = ""
    trigger_type: Optional[str] = None
    trigger_config: dict = field(default_factory=dict)
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        account_id: UUID,
        name: str,
        created_by: UUID,
        description: str = "",
        trigger_type: Optional[str] = None,
        trigger_config: Optional[dict] = None,
    ) -> "Workflow":
        """Factory method for creating a new workflow."""
        return cls(
            id=uuid4(),
            account_id=account_id,
            name=WorkflowName(name),
            status=WorkflowStatus.DRAFT,
            created_by=created_by,
            updated_by=created_by,
            description=description,
            trigger_type=trigger_type,
            trigger_config=trigger_config or {},
        )
```

#### Phase 2: Infrastructure Layer

**Files to Create:**
- `infrastructure/models.py` - SQLAlchemy ORM model
- `infrastructure/repositories.py` - WorkflowRepository
- `infrastructure/migrations/versions/xxxx_create_workflows_table.py`

**Key Implementation:**

```python
# infrastructure/repositories.py
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.entities import Workflow
from .models import WorkflowModel

class WorkflowRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, workflow: Workflow) -> Workflow:
        """Persist a workflow entity."""
        model = self._to_model(workflow)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def find_by_name(
        self,
        account_id: UUID,
        name: str
    ) -> Optional[Workflow]:
        """Find a workflow by name within an account."""
        stmt = select(WorkflowModel).where(
            WorkflowModel.account_id == account_id,
            WorkflowModel.name == name,
            WorkflowModel.deleted_at.is_(None)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
```

#### Phase 3: Application Layer

**Files to Create:**
- `application/use_cases/create_workflow.py`
- `application/dtos.py`

**Key Implementation:**

```python
# application/use_cases/create_workflow.py
from dataclasses import dataclass
from uuid import UUID

from ..dtos import CreateWorkflowRequest, WorkflowResponse
from ...domain.entities import Workflow
from ...domain.exceptions import WorkflowNameAlreadyExistsError
from ...infrastructure.repositories import WorkflowRepository, AuditLogRepository

@dataclass
class CreateWorkflowUseCase:
    workflow_repository: WorkflowRepository
    audit_repository: AuditLogRepository

    async def execute(
        self,
        request: CreateWorkflowRequest,
        account_id: UUID,
        user_id: UUID,
    ) -> WorkflowResponse:
        # Check name uniqueness
        existing = await self.workflow_repository.find_by_name(
            account_id, request.name
        )
        if existing:
            raise WorkflowNameAlreadyExistsError(request.name)

        # Create workflow
        workflow = Workflow.create(
            account_id=account_id,
            name=request.name,
            created_by=user_id,
            description=request.description,
            trigger_type=request.trigger_type,
            trigger_config=request.trigger_config,
        )

        # Persist
        saved = await self.workflow_repository.save(workflow)

        # Audit log
        await self.audit_repository.log_creation(saved, user_id)

        return WorkflowResponse.from_entity(saved)
```

#### Phase 4: Presentation Layer

**Files to Create:**
- `presentation/routes.py`
- `presentation/dependencies.py`
- `presentation/middleware.py`

**Key Implementation:**

```python
# presentation/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from ..application.dtos import CreateWorkflowRequest, WorkflowResponse
from ..application.use_cases.create_workflow import CreateWorkflowUseCase
from .dependencies import (
    get_create_workflow_use_case,
    get_current_user,
    get_current_account_id,
    require_permission,
)

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])

@router.post(
    "",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new workflow",
    description="Creates a new automation workflow in draft status.",
)
async def create_workflow(
    request: CreateWorkflowRequest,
    use_case: CreateWorkflowUseCase = Depends(get_create_workflow_use_case),
    user_id: UUID = Depends(get_current_user),
    account_id: UUID = Depends(get_current_account_id),
    _: None = Depends(require_permission("workflows:create")),
) -> WorkflowResponse:
    try:
        return await use_case.execute(request, account_id, user_id)
    except WorkflowNameAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "CONFLICT", "message": str(e)}
        )
```

---

## Risk Assessment

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Database migration conflicts | Medium | Use versioned migrations, test in staging |
| Performance bottleneck on uniqueness check | Low | Add appropriate indexes |
| Rate limiting bypass | Medium | Use Redis with atomic operations |

### Dependency Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Clerk authentication issues | High | Implement fallback, comprehensive error handling |
| Supabase connection issues | High | Connection pooling, retry logic |

---

## Quality Requirements

### Test Coverage Target: 85%

| Layer | Coverage Target | Test Types |
|-------|-----------------|------------|
| Domain | 95% | Unit tests |
| Application | 90% | Unit + Integration |
| Infrastructure | 85% | Integration tests |
| Presentation | 80% | E2E tests |

### Code Quality

- Ruff linting: Zero errors
- Pyright type checking: Strict mode, zero errors
- Code complexity: Max cyclomatic complexity 10

---

## Deployment Considerations

### Database Migration

1. Create migration file
2. Review migration in staging
3. Apply migration during maintenance window
4. Verify schema changes

### Feature Flags

- `FEATURE_WORKFLOWS_ENABLED`: Enable/disable entire module
- `FEATURE_WORKFLOW_RATE_LIMIT`: Configurable rate limit

### Rollback Plan

1. Revert API deployment
2. Keep database migration (additive only)
3. Monitor error rates

---

## Traceability Tags

- TAG:SPEC-WFL-001
- TAG:PLAN
- TAG:DDD-IMPLEMENTATION
