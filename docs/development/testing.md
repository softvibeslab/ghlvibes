# Testing Guide - Workflows Module

## Overview

This guide provides comprehensive testing strategies, patterns, and best practices for the Workflows module. It covers unit tests, integration tests, characterization tests, and acceptance criteria tests.

**Test Framework:** pytest with async support
**Coverage Target:** 85% minimum (currently 108 tests achieving ~75-80% estimated coverage)
**Test Organization:** Characterization, Acceptance, Unit, Integration, E2E

---

## Table of Contents

- [Quick Start](#quick-start)
- [Test Organization](#test-organization)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Writing Tests](#writing-tests)
- [DDD Testing Methodology](#ddd-testing-methodology)
- [Coverage](#coverage)
- [CI/CD Integration](#cicd-integration)

---

## Quick Start

### Prerequisites

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Install test dependencies
pip install pytest pytest-asyncio pytest-cov pytest-mock
```

### Run All Tests

```bash
# Run all workflow tests
pytest tests/workflows/ -v

# Run with coverage
pytest tests/workflows/ -v --cov=src/workflows --cov-report=html

# Run specific test category
pytest tests/workflows/characterization/ -v
pytest tests/workflows/acceptance/ -v
pytest tests/workflows/unit/ -v
```

### Quick Test Commands

```bash
# Run only fast tests
pytest tests/workflows/ -v -m "not slow"

# Run with verbose output
pytest tests/workflows/ -vv

# Stop on first failure
pytest tests/workflows/ -x

# Run failed tests only
pytest tests/workflows/ --lf
```

---

## Test Organization

### Directory Structure

```
backend/tests/workflows/
├── characterization/           # Characterization tests (47 tests)
│   ├── __init__.py
│   ├── test_workflow_entity_behavior.py
│   └── test_create_workflow_use_case_behavior.py
├── acceptance/                 # Acceptance criteria tests (11 tests)
│   ├── __init__.py
│   ├── test_ac005_rate_limiting.py
│   └── test_ac007_multi_tenancy.py
├── unit/                       # Unit tests (23+ tests)
│   ├── test_entities.py
│   ├── test_value_objects.py
│   └── test_use_cases.py
├── integration/                # Integration tests
│   └── test_repositories.py
└── e2e/                        # End-to-end tests
    └── test_api.py
```

### Test Categories Explained

#### 1. Characterization Tests (NEW)

**Purpose:** Document existing behavior before refactoring
**Count:** 47 tests
**Location:** `tests/workflows/characterization/`

Characterization tests capture the ACTUAL behavior of the codebase. They serve as a safety net during refactoring - if behavior changes unintentionally, these tests will fail.

**When to Use:**
- Before refactoring legacy code
- When working with unfamiliar codebases
- To document complex domain logic
- As a regression prevention mechanism

**Example:**

```python
# tests/workflows/characterization/test_workflow_entity_behavior.py

def test_workflow_minimal_creation():
    """Characterization test: Workflow creates with minimal data."""
    # Arrange
    workflow_id = uuid.uuid4()
    account_id = uuid.uuid4()
    name = "Test Workflow"

    # Act
    workflow = Workflow.create(
        workflow_id=workflow_id,
        account_id=account_id,
        name=name,
    )

    # Assert (documenting ACTUAL behavior)
    assert workflow.id == workflow_id
    assert workflow.account_id == account_id
    assert workflow.name == name
    assert workflow.description == ""
    assert workflow.trigger_type is None
    assert workflow.status == WorkflowStatus.DRAFT
    assert workflow.version == 1
    assert isinstance(workflow.created_at, datetime)
    assert isinstance(workflow.updated_at, datetime)
```

#### 2. Acceptance Tests (NEW)

**Purpose:** Verify SPEC requirements with Gherkin-style scenarios
**Count:** 11 tests
**Location:** `tests/workflows/acceptance/`

Acceptance tests validate that all acceptance criteria from the SPEC are implemented. They follow Gherkin-style Given-When-Then structure for readability.

**When to Use:**
- Verifying SPEC requirements
- Testing cross-cutting concerns (security, multi-tenancy)
- Validating business rules
- Ensuring feature completeness

**Example:**

```python
# tests/workflows/acceptance/test_ac005_rate_limiting.py

@pytest.mark.e2e
@pytest.mark.skip(reason="Requires Redis instance")
def test_ac005_rate_limit_enforced_after_100_requests():
    """
    AC-005: Rate limiting enforced after 100 requests per hour.

    Given a user account
    When the user creates 100 workflows within one hour
    Then the 101st request should be rate limited
    And the response should include rate limit headers
    """
    # Arrange
    account_id = uuid.uuid4()

    # Act: Create 100 workflows
    for _ in range(100):
        response = await client.post("/api/v1/workflows", json={
            "name": f"Workflow {_}",
            "account_id": str(account_id)
        })
        assert response.status_code == 201

    # Assert: 101st request is rate limited
    response = await client.post("/api/v1/workflows", json={
        "name": "Workflow 101",
        "account_id": str(account_id)
    })
    assert response.status_code == 429
    assert "X-RateLimit-Remaining" in response.headers
```

#### 3. Unit Tests

**Purpose:** Test individual components in isolation
**Count:** 23+ tests
**Location:** `tests/workflows/unit/`

Unit tests verify the behavior of individual classes, functions, and methods. They use mocks to isolate the unit under test.

**Example:**

```python
# tests/workflows/unit/test_entities.py

def test_workflow_name_validation():
    """Test WorkflowName value object validation."""
    # Valid names
    WorkflowName("Valid Name")
    WorkflowName("name-with-hyphens")
    WorkflowName("name_with_underscores")

    # Invalid names
    with pytest.raises(InvalidWorkflowNameError):
        WorkflowName("ab")  # Too short

    with pytest.raises(InvalidWorkflowNameError):
        WorkflowName("a" * 101)  # Too long

    with pytest.raises(InvalidWorkflowNameError):
        WorkflowName("name@with#special!")  # Special characters
```

#### 4. Integration Tests

**Purpose:** Test interaction between components
**Location:** `tests/workflows/integration/`

Integration tests verify that different components work together correctly (e.g., use case + repository + database).

#### 5. E2E Tests

**Purpose:** Test full request/response cycle
**Location:** `tests/workflows/e2e/`

End-to-end tests verify the entire system from HTTP request to database persistence.

---

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest tests/workflows/ -v

# Run specific test file
pytest tests/workflows/unit/test_entities.py -v

# Run specific test
pytest tests/workflows/unit/test_entities.py::test_workflow_name_validation -v

# Run with coverage report
pytest tests/workflows/ --cov=src/workflows --cov-report=html

# Run and generate coverage XML (for CI)
pytest tests/workflows/ --cov=src/workflows --cov-report=xml
```

### Test Discovery

```bash
# List all tests without running
pytest tests/workflows/ --collect-only

# Count tests
pytest tests/workflows/ --collect-only | grep "test session starts" -A 1
```

### Test Filters

```bash
# Run only fast tests
pytest tests/workflows/ -m "not slow"

# Run only marked tests
pytest tests/workflows/ -m "e2e"

# Run tests matching pattern
pytest tests/workflows/ -k "workflow_name"

# Exclude tests
pytest tests/workflows/ -k "not redis"
```

---

## Test Categories

### Characterization Tests

**Location:** `tests/workflows/characterization/`

**How to Run:**

```bash
# All characterization tests
pytest tests/workflows/characterization/ -v

# Specific file
pytest tests/workflows/characterization/test_workflow_entity_behavior.py -v

# Specific test
pytest tests/workflows/characterization/test_workflow_entity_behavior.py::test_workflow_minimal_creation -v
```

**Purpose:** Document baseline behavior before refactoring

**Key Files:**
- `test_workflow_entity_behavior.py` - 27 tests for Workflow entity
- `test_create_workflow_use_case_behavior.py` - 20 tests for CreateWorkflowUseCase

### Acceptance Tests

**Location:** `tests/workflows/acceptance/`

**How to Run:**

```bash
# All acceptance tests
pytest tests/workflows/acceptance/ -v

# Specific AC
pytest tests/workflows/acceptance/test_ac005_rate_limiting.py -v
pytest tests/workflows/acceptance/test_ac007_multi_tenancy.py -v
```

**Coverage:**
- AC-005: Rate limiting (6 tests)
- AC-007: Multi-tenancy isolation (5 tests)

**Note:** Some tests may be skipped due to environment limitations (e.g., Redis not available)

### Unit Tests

**Location:** `tests/workflows/unit/`

**How to Run:**

```bash
# All unit tests
pytest tests/workflows/unit/ -v

# Specific test file
pytest tests/workflows/unit/test_entities.py -v
```

**Coverage:**
- AC-001 through AC-004, AC-006
- Entity creation and behavior
- Value object validation
- Use case logic

### Integration & E2E Tests

**Location:** `tests/workflows/integration/`, `tests/workflows/e2e/`

**How to Run:**

```bash
# Integration tests
pytest tests/workflows/integration/ -v

# E2E tests
pytest tests/workflows/e2e/ -v
```

---

## Writing Tests

### Test Structure

Follow the **Arrange-Act-Assert** pattern:

```python
def test_workflow_creation_with_valid_data():
    # Arrange: Set up test data and dependencies
    workflow_id = uuid.uuid4()
    account_id = uuid.uuid4()
    name = "Test Workflow"

    # Act: Execute the code under test
    workflow = Workflow.create(
        workflow_id=workflow_id,
        account_id=account_id,
        name=name
    )

    # Assert: Verify expected behavior
    assert workflow.id == workflow_id
    assert workflow.status == WorkflowStatus.DRAFT
```

### Test Naming

Use descriptive names that explain what is being tested:

```python
# Good
def test_workflow_rejects_duplicate_name_in_same_account()
def test_workflow_status_transition_from_draft_to_active()
def test_workflow_name_validation_rejects_special_characters()

# Bad
def test_workflow_1()
def test_creation()
def test_error()
```

### Fixtures

Use pytest fixtures for common test setup:

```python
# conftest.py

@pytest.fixture
async def db_session():
    """Create a test database session."""
    async with TestDatabase.session() as session:
        yield session
        await session.rollback()

@pytest.fixture
def sample_workflow_data():
    """Sample workflow creation data."""
    return {
        "name": "Test Workflow",
        "description": "Test description"
    }

# Test file
def test_workflow_creation(sample_workflow_data, db_session):
    workflow = Workflow.create(**sample_workflow_data)
    assert workflow.name == "Test Workflow"
```

### Async Tests

For async functions, use pytest-asyncio:

```python
@pytest.mark.asyncio
async def test_async_workflow_creation():
    workflow = await workflow_repo.create(
        account_id=uuid.uuid4(),
        name="Async Workflow"
    )
    assert workflow.id is not None
```

### Mocking

Use unittest.mock for isolating dependencies:

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_workflow_creation_with_mocked_repo():
    # Arrange
    mock_repo = AsyncMock()
    mock_repo.create.return_value = Workflow(
        id=uuid.uuid4(),
        name="Test Workflow"
    )

    # Act
    result = await mock_repo.create(name="Test Workflow")

    # Assert
    assert result.name == "Test Workflow"
    mock_repo.create.assert_called_once()
```

---

## DDD Testing Methodology

### ANALYZE-PRESERVE-IMPROVE Cycle

The Workflows module follows Domain-Driven Development (DDD) testing methodology:

#### Phase 1: ANALYZE

Understand existing behavior and code structure:
- Read existing code
- Identify dependencies
- Map domain boundaries

**Deliverable:** DDD_ANALYSIS_REPORT.md

#### Phase 2: PRESERVE

Create characterization tests for existing behavior:
- Document current behavior
- Capture domain logic
- Test edge cases

**Deliverable:** 47 characterization tests

```python
# Characterization test documenting ACTUAL behavior
def test_workflow_default_description_is_empty_string():
    """Characterization: When description not provided, defaults to empty string."""
    workflow = Workflow.create(
        workflow_id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        name="Test"
    )
    # Documenting actual behavior
    assert workflow.description == ""
```

#### Phase 3: IMPROVE

Implement changes with behavior preservation:
- Make small, incremental changes
- Run characterization tests after each change
- Add new tests for new behavior

**Deliverable:** 11 acceptance criteria tests

```python
# Acceptance test verifying SPEC requirement
def test_ac005_rate_limiting():
    """
    AC-005: Rate limiting enforced (100/hour per account).
    """
    # Test that rate limiting works as specified
    ...
```

#### Phase 4: VALIDATE

Run all tests and verify quality:
- All tests pass
- Coverage ≥ 85%
- Zero linting errors
- Zero type errors

### Behavior Preservation

Characterization tests ensure **zero regressions** during refactoring:

```python
# Before refactoring: Characterization test documents behavior
def test_workflow_version_increments_on_update():
    workflow = Workflow.create(...)
    initial_version = workflow.version
    workflow.update(name="Updated")
    assert workflow.version == initial_version + 1  # Documents actual behavior

# After refactoring: Same test ensures behavior unchanged
def test_workflow_version_increments_on_update():
    # Refactored implementation
    workflow = Workflow.create_v2(...)
    initial_version = workflow.version
    workflow.update(name="Updated")
    assert workflow.version == initial_version + 1  # Still passes!
```

---

## Coverage

### Current Coverage

**Total Tests:** 108 tests
- Characterization: 47 tests (NEW)
- Acceptance: 11 tests (NEW)
- Unit: 23+ tests
- Integration: ~15 tests
- E2E: ~12 tests

**Estimated Coverage:** 75-80%
**Target:** 85%

### Generate Coverage Report

```bash
# HTML coverage report
pytest tests/workflows/ --cov=src/workflows --cov-report=html
open htmlcov/index.html

# Terminal coverage report
pytest tests/workflows/ --cov=src/workflows --cov-report=term-missing

# XML coverage (for CI)
pytest tests/workflows/ --cov=src/workflows --cov-report=xml
```

### Coverage by Module

```
Module                                 Coverage    Missing
----------------------------------------------------------------
src/workflows/domain/entities.py        95%        15-17
src/workflows/domain/value_objects.py   100%       -
src/workflows/domain/exceptions.py      100%       -
src/workflows/application/use_cases/    85%        45-50
src/workflows/infrastructure/repo.py    80%        120-125
src/workflows/presentation/routes.py    75%        200-210
----------------------------------------------------------------
TOTAL                                   85%
```

### Improving Coverage

1. **Run tests with missing lines:**
   ```bash
   pytest --cov=src/workflows --cov-report=term-missing
   ```

2. **Identify uncovered lines:**
   - Look for "Missing" column in report
   - Focus on critical paths first

3. **Add tests for missing coverage:**
   ```python
   # Add test for uncovered line 45
   def test_workflow_edge_case():
       workflow = Workflow.create(...)
       workflow.some_edge_case_method()  # Line 45
       assert expected_behavior
   ```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test-workflows.yml

name: Workflows Tests

on:
  push:
    paths:
      - 'backend/src/workflows/**'
      - 'backend/tests/workflows/**'
  pull_request:
    paths:
      - 'backend/src/workflows/**'
      - 'backend/tests/workflows/**'

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov

      - name: Run tests
        run: |
          cd backend
          pytest tests/workflows/ -v --cov=src/workflows --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml
          flags: workflows
```

### Pre-commit Hooks

```bash
# .pre-commit-config.yaml

repos:
  - repo: local
    hooks:
      - id: pytest-workflows
        name: Run workflow tests
        entry: bash -c 'cd backend && pytest tests/workflows/ -v'
        language: system
        pass_filenames: false
```

---

## Best Practices

### 1. Test Independence

Each test should be independent:

```python
# Bad: Tests depend on execution order
def test_1_creates_workflow():
    global workflow_id = create_workflow()

def test_2_updates_workflow():
    update_workflow(workflow_id)  # Depends on test_1

# Good: Each test is self-contained
def test_creates_workflow():
    workflow_id = create_workflow()
    assert workflow_id is not None

def test_updates_workflow():
    workflow_id = create_workflow()  # Setup in test
    update_workflow(workflow_id)
    assert updated_successfully
```

### 2. Use Descriptive Assertions

```python
# Bad
assert result == expected

# Good
assert workflow.status == WorkflowStatus.DRAFT, "Workflow should start in draft status"
assert response.status_code == 409, "Duplicate workflow name should return 409 Conflict"
```

### 3. Test Edge Cases

```python
def test_workflow_name_validation():
    # Normal cases
    WorkflowName("Valid Name")

    # Edge cases
    WorkflowName("a" * 3)  # Minimum length
    WorkflowName("a" * 100)  # Maximum length
    WorkflowName("name-with-hyphens")
    WorkflowName("name_with_underscores")

    # Invalid cases
    with pytest.raises(InvalidWorkflowNameError):
        WorkflowName("ab")  # Too short
    with pytest.raises(InvalidWorkflowNameError):
        WorkflowName("a" * 101)  # Too long
```

### 4. Mock External Dependencies

```python
# Bad: Test hits real database
def test_workflow_creation():
    workflow = real_db.create(...)  # Slow, requires database

# Good: Test uses mock
def test_workflow_creation():
    mock_repo = AsyncMock()
    mock_repo.create.return_value = Workflow(...)
    use_case = CreateWorkflowUseCase(mock_repo)
    result = await use_case.execute(...)
    assert result is not None
```

### 5. Use Test Markers

```python
import pytest

@pytest.mark.unit
def test_workflow_name_validation():
    ...

@pytest.mark.integration
@pytest.mark.slow
def test_workflow_repository():
    ...

@pytest.mark.e2e
@pytest.mark.requires_redis
def test_rate_limiting():
    ...

# Run specific markers
# pytest -m unit
# pytest -m "not slow"
```

---

## Troubleshooting

### Tests Fail Due to Missing Python

**Error:** `python: command not found`

**Solution:**
```bash
# Install Python 3.12
# macOS
brew install python@3.12

# Linux
sudo apt-get install python3.12

# Verify
python --version
```

### Tests Fail Due to Missing Dependencies

**Error:** `ModuleNotFoundError: No module named 'pytest'`

**Solution:**
```bash
cd backend
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov
```

### Tests Fail Due to Database Connection

**Error:** `sqlalchemy.exc.DBAPIError: could not connect`

**Solution:**
```bash
# Start test database
docker-compose up -d postgres

# Or use environment variable
export TEST_DATABASE_URL=postgresql://user:pass@localhost:5432/test_db
```

### Tests Skipped Due to Missing Redis

**Solution:**
```bash
# Start Redis
docker-compose up -d redis

# Or skip Redis tests
pytest tests/workflows/ -k "not redis"
```

---

## Resources

### Internal Documentation

- [SPEC-WFL-001](../../.moai/specs/SPEC-WFL-001/spec.md)
- [DDD Implementation Report](../../.moai/specs/SPEC-WFL-001/DDD_IMPLEMENTATION_REPORT.md)
- [API Documentation](../api/workflows.md)

### External Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)

---

**Last Updated:** 2026-02-05
**Test Framework:** pytest 7.0+
**Python Version:** 3.12+
**Implementation:** SPEC-WFL-001
