# SPEC-WFL-004: Implementation Plan

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-004 |
| **Title** | Add Condition/Branch |
| **Module** | workflows |
| **Domain** | automation |
| **Priority** | Critical |

---

## Implementation Overview

This plan outlines the phased implementation of workflow conditional branching functionality using FastAPI backend with PostgreSQL/Supabase for persistence and a modular evaluator architecture.

---

## Technical Approach

### Architecture Pattern: Strategy + Factory

The condition evaluation system uses the Strategy pattern to encapsulate different evaluation algorithms, combined with a Factory pattern for instantiation.

```
src/backend/
├── domain/
│   └── workflows/
│       ├── conditions/
│       │   ├── __init__.py
│       │   ├── models.py              # Domain models
│       │   ├── schemas.py             # Pydantic schemas
│       │   ├── service.py             # Business logic
│       │   ├── repository.py          # Data access
│       │   └── evaluators/
│       │       ├── __init__.py
│       │       ├── base.py            # Abstract evaluator
│       │       ├── factory.py         # Evaluator factory
│       │       ├── field_evaluator.py
│       │       ├── tag_evaluator.py
│       │       ├── pipeline_evaluator.py
│       │       ├── custom_field_evaluator.py
│       │       ├── engagement_evaluator.py
│       │       ├── time_evaluator.py
│       │       └── combined_evaluator.py
│       └── branches/
│           ├── __init__.py
│           ├── models.py
│           ├── schemas.py
│           ├── service.py
│           └── repository.py
├── api/
│   └── v1/
│       └── workflows/
│           └── conditions.py          # API routes
└── infrastructure/
    └── database/
        └── migrations/
            └── 004_workflow_conditions.py
```

### Key Design Decisions

1. **Evaluator Isolation**: Each condition type has its own evaluator class implementing a common interface
2. **JSONB Configuration**: Flexible condition storage using PostgreSQL JSONB
3. **Async Evaluation**: All evaluators are async-first for non-blocking execution
4. **Caching Layer**: Redis caching for frequently accessed contact data
5. **Audit Logging**: Separate logging service for condition evaluations

---

## Milestones

### Milestone 1: Database Foundation (Primary Goal)

**Objective:** Establish database schema and repository layer for conditions and branches.

**Deliverables:**
- [ ] Database migration for `workflow_conditions` table
- [ ] Database migration for `workflow_branches` table
- [ ] Database migration for `workflow_condition_logs` table
- [ ] SQLAlchemy models for all tables
- [ ] Repository classes with CRUD operations
- [ ] Database indexes for query optimization

**Components:**
```python
# models.py
class WorkflowCondition(Base):
    __tablename__ = "workflow_conditions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    workflow_id: Mapped[UUID] = mapped_column(ForeignKey("workflows.id"))
    node_id: Mapped[UUID] = mapped_column(nullable=False)
    condition_type: Mapped[str] = mapped_column(String(50), nullable=False)
    branch_type: Mapped[str] = mapped_column(String(20), nullable=False)
    configuration: Mapped[dict] = mapped_column(JSONB, nullable=False)
    position_x: Mapped[int] = mapped_column(Integer, nullable=False)
    position_y: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    branches: Mapped[list["WorkflowBranch"]] = relationship(back_populates="condition")
```

**Validation Criteria:**
- All migrations run successfully
- Repository tests pass with 100% coverage
- Query performance under 10ms for single record operations

---

### Milestone 2: Core Evaluator Framework (Primary Goal)

**Objective:** Implement base evaluator infrastructure and factory pattern.

**Deliverables:**
- [ ] Abstract base evaluator class with interface definition
- [ ] Evaluator factory with type registration
- [ ] Operator definitions and implementations
- [ ] Unit tests for base functionality

**Components:**
```python
# base.py
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseConditionEvaluator(ABC):
    """Abstract base class for condition evaluators."""

    @abstractmethod
    async def evaluate(
        self,
        contact_id: UUID,
        configuration: Dict[str, Any],
        context: EvaluationContext
    ) -> EvaluationResult:
        """Evaluate condition for a contact."""
        pass

    @abstractmethod
    def validate_configuration(
        self,
        configuration: Dict[str, Any]
    ) -> ValidationResult:
        """Validate condition configuration."""
        pass

    @abstractmethod
    def get_supported_operators(self) -> list[str]:
        """Return list of supported operators."""
        pass

# factory.py
class ConditionEvaluatorFactory:
    """Factory for creating condition evaluators."""

    _evaluators: Dict[str, Type[BaseConditionEvaluator]] = {}

    @classmethod
    def register(cls, condition_type: str):
        def decorator(evaluator_class: Type[BaseConditionEvaluator]):
            cls._evaluators[condition_type] = evaluator_class
            return evaluator_class
        return decorator

    @classmethod
    def create(cls, condition_type: str) -> BaseConditionEvaluator:
        if condition_type not in cls._evaluators:
            raise ValueError(f"Unknown condition type: {condition_type}")
        return cls._evaluators[condition_type]()
```

**Validation Criteria:**
- Factory correctly instantiates all evaluator types
- Base class enforces interface contract
- 95%+ test coverage on framework code

---

### Milestone 3: Condition Type Evaluators (Primary Goal)

**Objective:** Implement all seven condition type evaluators.

**Deliverables:**
- [ ] FieldConditionEvaluator (contact_field_equals)
- [ ] TagConditionEvaluator (contact_has_tag)
- [ ] PipelineConditionEvaluator (pipeline_stage_is)
- [ ] CustomFieldEvaluator (custom_field_value)
- [ ] EngagementConditionEvaluator (email_was_opened, link_was_clicked)
- [ ] TimeConditionEvaluator (time_based)
- [ ] CombinedConditionEvaluator (AND/OR logic)

**Components per Evaluator:**
```python
# field_evaluator.py
@ConditionEvaluatorFactory.register("contact_field_equals")
class FieldConditionEvaluator(BaseConditionEvaluator):

    SUPPORTED_OPERATORS = [
        "equals", "not_equals", "contains", "not_contains",
        "starts_with", "ends_with", "is_empty", "is_not_empty",
        "greater_than", "less_than", "in_list", "not_in_list"
    ]

    async def evaluate(
        self,
        contact_id: UUID,
        configuration: Dict[str, Any],
        context: EvaluationContext
    ) -> EvaluationResult:
        field_name = configuration["field"]
        operator = configuration["operator"]
        target_value = configuration.get("value")

        contact = await context.contact_service.get_contact(contact_id)
        field_value = getattr(contact, field_name, None)

        result = self._apply_operator(field_value, operator, target_value)

        return EvaluationResult(
            matched=result,
            inputs={"field_value": field_value},
            details={"operator": operator, "target": target_value}
        )

    def _apply_operator(self, value: Any, operator: str, target: Any) -> bool:
        match operator:
            case "equals":
                return value == target
            case "not_equals":
                return value != target
            case "contains":
                return target.lower() in str(value).lower()
            case "starts_with":
                return str(value).lower().startswith(target.lower())
            case "is_empty":
                return value is None or value == ""
            # ... additional operators
```

**Validation Criteria:**
- Each evaluator handles all its supported operators
- Edge cases (null values, type mismatches) handled gracefully
- 100% operator coverage in tests

---

### Milestone 4: API Layer (Secondary Goal)

**Objective:** Implement REST API endpoints for condition management.

**Deliverables:**
- [ ] POST endpoint for creating conditions
- [ ] GET endpoint for retrieving conditions
- [ ] PATCH endpoint for updating conditions
- [ ] DELETE endpoint for removing conditions
- [ ] Pydantic request/response schemas
- [ ] API documentation (OpenAPI)

**Components:**
```python
# conditions.py (API routes)
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

router = APIRouter(prefix="/workflows/{workflow_id}/conditions", tags=["Workflow Conditions"])

@router.post("/", response_model=ConditionResponse, status_code=status.HTTP_201_CREATED)
async def create_condition(
    workflow_id: UUID,
    request: CreateConditionRequest,
    condition_service: ConditionService = Depends(get_condition_service),
    current_user: User = Depends(get_current_user)
) -> ConditionResponse:
    """Create a new condition node in the workflow."""
    # Verify workflow access
    await verify_workflow_access(workflow_id, current_user, "conditions.create")

    # Validate condition configuration
    validation = await condition_service.validate_configuration(
        request.condition_type,
        request.configuration
    )
    if not validation.is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=validation.errors
        )

    # Create condition
    condition = await condition_service.create_condition(
        workflow_id=workflow_id,
        node_id=request.node_id,
        condition_type=request.condition_type,
        branch_type=request.branch_type,
        configuration=request.configuration,
        position=request.position,
        created_by=current_user.id
    )

    return ConditionResponse.from_orm(condition)
```

**Validation Criteria:**
- All endpoints return appropriate status codes
- Request validation with clear error messages
- OpenAPI documentation auto-generated

---

### Milestone 5: Branch Management (Secondary Goal)

**Objective:** Implement branch creation, routing, and split test logic.

**Deliverables:**
- [ ] Branch service for CRUD operations
- [ ] Branch connection management (linking to next nodes)
- [ ] Split test percentage validation
- [ ] Random distribution algorithm for split tests
- [ ] Branch ordering/priority management

**Components:**
```python
# branch_service.py
class BranchService:

    async def create_branches_for_condition(
        self,
        condition: WorkflowCondition
    ) -> list[WorkflowBranch]:
        """Create default branches based on branch type."""
        match condition.branch_type:
            case "if_else":
                return await self._create_if_else_branches(condition)
            case "multi_branch":
                return await self._create_multi_branches(condition)
            case "split_test":
                return await self._create_split_test_branches(condition)

    async def route_to_branch(
        self,
        condition_id: UUID,
        evaluation_result: EvaluationResult
    ) -> WorkflowBranch:
        """Determine which branch to route based on evaluation."""
        branches = await self.repository.get_branches(condition_id)

        # For split tests, use random distribution
        condition = await self.condition_repo.get(condition_id)
        if condition.branch_type == "split_test":
            return self._random_split_selection(branches)

        # For if_else and multi_branch, find matching branch
        for branch in sorted(branches, key=lambda b: b.branch_order):
            if branch.is_default:
                continue
            if self._matches_branch_criteria(evaluation_result, branch):
                return branch

        # Return default branch
        return next(b for b in branches if b.is_default)

    def _random_split_selection(
        self,
        branches: list[WorkflowBranch]
    ) -> WorkflowBranch:
        """Select branch based on percentage distribution."""
        rand_value = random.random() * 100
        cumulative = 0.0

        for branch in sorted(branches, key=lambda b: b.branch_order):
            cumulative += branch.percentage
            if rand_value <= cumulative:
                return branch

        return branches[-1]  # Fallback to last branch
```

**Validation Criteria:**
- Split test distribution matches configured percentages (within statistical tolerance)
- Branch priority ordering is respected
- Default branch always exists as fallback

---

### Milestone 6: Execution Integration (Secondary Goal)

**Objective:** Integrate condition evaluation with workflow execution engine.

**Deliverables:**
- [ ] Condition evaluation hook in execution flow
- [ ] Execution context management
- [ ] Result caching for repeated evaluations
- [ ] Error handling and recovery

**Components:**
```python
# execution_integration.py
class WorkflowConditionExecutor:
    """Integrates condition evaluation with workflow execution."""

    def __init__(
        self,
        condition_service: ConditionService,
        branch_service: BranchService,
        log_service: ConditionLogService,
        cache: Redis
    ):
        self.condition_service = condition_service
        self.branch_service = branch_service
        self.log_service = log_service
        self.cache = cache

    async def execute_condition_node(
        self,
        execution_id: UUID,
        condition_id: UUID,
        contact_id: UUID
    ) -> ExecutionResult:
        """Execute a condition node and determine next path."""
        start_time = time.monotonic()

        try:
            # Get condition configuration
            condition = await self.condition_service.get_condition(condition_id)

            # Create evaluation context with cached data
            context = await self._create_evaluation_context(contact_id)

            # Evaluate condition
            evaluation = await self.condition_service.evaluate(
                condition_id=condition_id,
                contact_id=contact_id,
                context=context
            )

            # Route to appropriate branch
            branch = await self.branch_service.route_to_branch(
                condition_id=condition_id,
                evaluation_result=evaluation
            )

            # Log evaluation
            duration_ms = int((time.monotonic() - start_time) * 1000)
            await self.log_service.log_evaluation(
                execution_id=execution_id,
                condition_id=condition_id,
                contact_id=contact_id,
                inputs=evaluation.inputs,
                result=branch.branch_name,
                duration_ms=duration_ms
            )

            return ExecutionResult(
                success=True,
                next_node_id=branch.next_node_id,
                branch_taken=branch.branch_name
            )

        except Exception as e:
            await self._handle_evaluation_error(
                execution_id, condition_id, contact_id, e
            )
            # Route to error/default branch
            return await self._get_fallback_result(condition_id)
```

**Validation Criteria:**
- Seamless integration with existing execution engine
- Error handling prevents workflow stalls
- Performance within 50ms target

---

### Milestone 7: Logging and Analytics (Final Goal)

**Objective:** Implement comprehensive logging and analytics for conditions.

**Deliverables:**
- [ ] Condition evaluation logging service
- [ ] Log query API endpoints
- [ ] Analytics aggregation for branch performance
- [ ] Log retention and cleanup job

**Components:**
```python
# log_service.py
class ConditionLogService:
    """Service for logging and querying condition evaluations."""

    async def log_evaluation(
        self,
        execution_id: UUID,
        condition_id: UUID,
        contact_id: UUID,
        inputs: dict,
        result: str,
        duration_ms: int
    ) -> WorkflowConditionLog:
        """Log a condition evaluation."""
        log_entry = WorkflowConditionLog(
            execution_id=execution_id,
            condition_id=condition_id,
            contact_id=contact_id,
            evaluation_inputs=self._mask_pii(inputs),
            evaluation_result=result,
            duration_ms=duration_ms
        )
        return await self.repository.create(log_entry)

    async def get_branch_analytics(
        self,
        condition_id: UUID,
        date_range: DateRange
    ) -> BranchAnalytics:
        """Get analytics for branch distribution."""
        logs = await self.repository.get_logs_for_condition(
            condition_id=condition_id,
            start_date=date_range.start,
            end_date=date_range.end
        )

        branch_counts = Counter(log.evaluation_result for log in logs)
        total = sum(branch_counts.values())

        return BranchAnalytics(
            total_evaluations=total,
            branch_distribution={
                branch: count / total * 100
                for branch, count in branch_counts.items()
            },
            avg_duration_ms=sum(log.duration_ms for log in logs) / len(logs)
        )
```

**Validation Criteria:**
- All evaluations logged with full context
- Log queries performant (< 100ms for 1000 records)
- PII masking applied correctly

---

### Milestone 8: Testing and Documentation (Final Goal)

**Objective:** Comprehensive test coverage and documentation.

**Deliverables:**
- [ ] Unit tests for all evaluators (100% coverage)
- [ ] Integration tests for API endpoints
- [ ] End-to-end tests for workflow execution with conditions
- [ ] Performance benchmarks
- [ ] API documentation updates
- [ ] Developer guide for adding new condition types

**Test Categories:**
```python
# test_field_evaluator.py
class TestFieldConditionEvaluator:

    @pytest.mark.asyncio
    async def test_equals_operator_match(self):
        """Test equals operator returns true on match."""
        evaluator = FieldConditionEvaluator()
        result = await evaluator.evaluate(
            contact_id=uuid4(),
            configuration={
                "field": "email",
                "operator": "equals",
                "value": "test@example.com"
            },
            context=mock_context(email="test@example.com")
        )
        assert result.matched is True

    @pytest.mark.asyncio
    async def test_contains_operator_case_insensitive(self):
        """Test contains operator is case insensitive."""
        evaluator = FieldConditionEvaluator()
        result = await evaluator.evaluate(
            contact_id=uuid4(),
            configuration={
                "field": "email",
                "operator": "contains",
                "value": "@GMAIL"
            },
            context=mock_context(email="user@gmail.com")
        )
        assert result.matched is True

    @pytest.mark.asyncio
    async def test_null_field_handling(self):
        """Test graceful handling of null field values."""
        evaluator = FieldConditionEvaluator()
        result = await evaluator.evaluate(
            contact_id=uuid4(),
            configuration={
                "field": "phone",
                "operator": "is_empty",
                "value": None
            },
            context=mock_context(phone=None)
        )
        assert result.matched is True
```

**Validation Criteria:**
- 95%+ code coverage
- All edge cases documented and tested
- Performance benchmarks meet targets

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Complex condition evaluation timeout | Medium | High | Implement evaluation timeout with fallback |
| Split test distribution skew | Low | Medium | Statistical validation in tests |
| Database query performance | Medium | High | Proper indexing, query optimization |
| PII exposure in logs | Low | High | PII masking, log access controls |
| Condition configuration breaking changes | Medium | Medium | Schema versioning, migration scripts |

---

## Technical Dependencies

### Libraries
- SQLAlchemy 2.0+ (async ORM)
- Pydantic 2.x (validation)
- FastAPI 0.115+ (API framework)
- Redis (caching)
- pytest-asyncio (testing)

### Infrastructure
- PostgreSQL 16+ with JSONB support
- Redis 7+ for caching
- Supabase for managed database

### Internal Services
- Contact Service (field access)
- Tag Service (tag queries)
- Pipeline Service (stage queries)
- Email Tracking Service (engagement data)
- Workflow Execution Engine (integration point)

---

## Quality Gates

| Gate | Requirement | Validation |
|------|-------------|------------|
| Unit Test Coverage | >= 95% | pytest-cov report |
| Integration Test Pass | 100% | CI pipeline |
| API Response Time | < 100ms P95 | Load testing |
| Condition Evaluation | < 50ms P95 | Benchmark tests |
| Security Scan | 0 critical | Bandit/Semgrep |
| Documentation | Complete | Review checklist |

---

## Traceability Matrix

| SPEC Requirement | Milestone | Component |
|------------------|-----------|-----------|
| REQ-001 | M1, M2 | ConditionService, BranchService |
| REQ-002 | M1, M5 | BranchService |
| REQ-003 | M5 | SplitTestBranchService |
| REQ-004 | M3 | FieldConditionEvaluator |
| REQ-005 | M3 | TagConditionEvaluator |
| REQ-006 | M3 | PipelineConditionEvaluator |
| REQ-007 | M3 | CustomFieldEvaluator |
| REQ-008 | M3 | EngagementConditionEvaluator |
| REQ-009 | M3 | TimeConditionEvaluator |
| REQ-010 | M3 | CombinedConditionEvaluator |
| REQ-011 | M2, M4 | ConditionValidator |
| REQ-012 | M7 | ConditionLogService |
| REQ-013 | M6 | WorkflowConditionExecutor |
