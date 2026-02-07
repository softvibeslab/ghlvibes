# Comprehensive Test Strategy - GoHighLevel Clone

## Executive Summary

This document defines the complete testing strategy for the GoHighLevel Clone marketing automation platform, covering backend, frontend, integration, E2E, performance, and security testing with a target of 2000+ tests and 85%+ code coverage.

**Test Target:** 2000+ tests
**Coverage Target:** 85%+ backend, 80%+ frontend
**Quality Gates:** TRUST 5 compliance, zero critical issues

---

## Test Pyramid Design

```
                    ┌─────────────┐
                    │   E2E: 5%   │ 100 tests
                    │  Playwright │
                    └─────────────┘
                  ┌─────────────────┐
                  │ Integration: 15%│ 300 tests
                  │  API + Database │
                  └─────────────────┘
                ┌───────────────────────┐
                │    Unit Tests: 80%    │ 1600+ tests
                │  pytest + Vitest      │
                └───────────────────────┘
```

### Test Distribution

- **Unit Tests (80%)**: 1600 tests
  - Backend: 1200 tests (pytest)
  - Frontend: 400 tests (Vitest)

- **Integration Tests (15%)**: 300 tests
  - API integration: 150 tests
  - Database integration: 100 tests
  - Backend-Frontend integration: 50 tests

- **E2E Tests (5%)**: 100 tests
  - Critical user flows: 50 tests
  - Cross-browser tests: 30 tests
  - Accessibility tests: 20 tests

---

## 1. Backend Testing Strategy

### Framework Stack

- **Unit Testing**: pytest 8.3+ with async support
- **Coverage**: pytest-cov with branch coverage
- **Mocking**: pytest-mock + unittest.mock
- **Fixtures**: pytest-asyncio with factory_boy
- **API Testing**: httpx AsyncClient
- **Database Testing**: PostgreSQL test instance

### Test Organization

```
backend/tests/
├── unit/                      # 1200 tests
│   ├── domain/               # 400 tests
│   │   ├── test_entities.py         # Workflow, Trigger, Action, Condition
│   │   ├── test_value_objects.py    # All value objects
│   │   ├── test_aggregates.py       # Workflow aggregate roots
│   │   └── test_services.py         # Domain services
│   ├── application/          # 400 tests
│   │   ├── test_use_cases/          # CRUD, execution, analytics
│   │   ├── test_commands.py         # Command handlers
│   │   └── test_queries.py          # Query handlers
│   ├── infrastructure/       # 200 tests
│   │   ├── test_repositories.py     # Repository patterns
│   │   ├── test_messaging.py        # Event bus, queues
│   │   └── test_cache.py            # Redis caching
│   └── presentation/          # 200 tests
│       ├── test_routes.py           # API endpoints
│       ├── test_middleware.py       # Auth, rate limiting
│       └── test_serializers.py      # Request/response models
├── integration/               # 150 tests
│   ├── test_api_endpoints.py        # Full API tests
│   ├── test_repositories.py         # DB integration
│   ├── test_messaging.py            # Queue integration
│   └── test_external_services.py    # Third-party integrations
├── e2e/                       # 100 tests
│   ├── test_workflows.py            # Workflow CRUD flows
│   ├── test_execution.py            # Execution flows
│   ├── test_analytics.py            # Analytics flows
│   └── test_multi_tenancy.py        # Tenant isolation
├── performance/                # 50 tests
│   ├── test_api_performance.py      # Response times
│   ├── test_db_performance.py       # Query performance
│   └── test_concurrent_load.py      # Load testing
└── security/                   # 50 tests
    ├── test_authentication.py       # Auth flows
    ├── test_authorization.py        # Permission checks
    ├── test_input_validation.py     # SQL injection, XSS
    └── test_rate_limiting.py        # DoS prevention
```

### Backend Test Coverage Targets

| Module                    | Target | Current | Gap     |
|---------------------------|--------|---------|---------|
| Domain Layer              | 95%    | 85%     | +10%    |
| Application Layer         | 90%    | 75%     | +15%    |
| Infrastructure Layer      | 85%    | 70%     | +15%    |
| Presentation Layer        | 85%    | 70%     | +15%    |
| **Overall Backend**       | **90%** | **75%** | **+15%**|

### Backend Test Templates

#### Unit Test Template

```python
# tests/unit/domain/test_workflow_entity.py

import pytest
from uuid import uuid4
from workflows.domain.entities import Workflow
from workflows.domain.value_objects import WorkflowName
from workflows.domain.exceptions import InvalidWorkflowNameError

class TestWorkflowEntity:
    """Test suite for Workflow entity."""

    def test_workflow_creation_with_valid_data(self):
        """Given valid data, when creating workflow, then entity is created."""
        # Arrange
        workflow_id = uuid4()
        account_id = uuid4()
        name = WorkflowName("Test Workflow")

        # Act
        workflow = Workflow.create(
            workflow_id=workflow_id,
            account_id=account_id,
            name=name
        )

        # Assert
        assert workflow.id == workflow_id
        assert workflow.account_id == account_id
        assert workflow.name == name
        assert workflow.status == WorkflowStatus.DRAFT
        assert workflow.version == 1

    def test_workflow_name_validation_rejects_invalid_names(self):
        """Given invalid name, when creating workflow, then raises exception."""
        # Arrange & Act & Assert
        with pytest.raises(InvalidWorkflowNameError):
            WorkflowName("ab")  # Too short

    @pytest.mark.parametrize("name,expected", [
        ("Valid Name", True),
        ("name-with-hyphens", True),
        ("name_with_underscores", True),
        ("ab", False),  # Too short
        ("a" * 101, False),  # Too long
    ])
    def test_workflow_name_validation(self, name, expected):
        """Given various names, when validating, then returns expected result."""
        # Act
        result = WorkflowName.is_valid(name)

        # Assert
        assert result == expected
```

#### Integration Test Template

```python
# tests/integration/test_workflow_api.py

import pytest
from httpx import AsyncClient

@pytest.mark.integration
class TestWorkflowAPIIntegration:
    """Test suite for Workflow API integration."""

    async def test_create_workflow_end_to_end(self, async_client: AsyncClient):
        """Given valid request, when POST /workflows, then creates workflow."""
        # Arrange
        payload = {
            "name": "Integration Test Workflow",
            "description": "Testing API end to end",
            "trigger_type": "webhook"
        }

        # Act
        response = await async_client.post("/api/v1/workflows", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert "id" in data
        assert data["status"] == "draft"

    async def test_workflow_crud_lifecycle(self, async_client: AsyncClient):
        """Given workflow, when performing CRUD, then all operations succeed."""
        # Create
        create_response = await async_client.post("/api/v1/workflows", json={
            "name": "CRUD Test Workflow"
        })
        assert create_response.status_code == 201
        workflow_id = create_response.json()["id"]

        # Read
        read_response = await async_client.get(f"/api/v1/workflows/{workflow_id}")
        assert read_response.status_code == 200
        assert read_response.json()["name"] == "CRUD Test Workflow"

        # Update
        update_response = await async_client.patch(f"/api/v1/workflows/{workflow_id}", json={
            "name": "Updated Workflow"
        })
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "Updated Workflow"

        # Delete
        delete_response = await async_client.delete(f"/api/v1/workflows/{workflow_id}")
        assert delete_response.status_code == 204
```

---

## 2. Frontend Testing Strategy

### Framework Stack

- **Unit Testing**: Vitest 1.6+
- **Component Testing**: React Testing Library 15.0+
- **E2E Testing**: Playwright 1.44+
- **Coverage**: Vitest coverage (c8)
- **Mocking**: Vitest vi + MSW
- **Visual Regression**: Storybook + Chromatic (optional)

### Test Organization

```
frontend/
├── src/
│   ├── __tests__/          # 400 tests
│   │   ├── unit/           # 250 tests
│   │   │   ├── lib/        # Utilities, helpers
│   │   │   ├── stores/     # Zustand stores
│   │   │   └── hooks/      # Custom hooks
│   │   └── components/     # 150 tests
│   │       ├── ui/         # UI components
│   │       └── workflows/  # Workflow components
│   ├── e2e/                # 100 tests
│   │   ├── workflows/      # Workflow flows
│   │   ├── auth/           # Authentication
│   │   └── navigation/     # Navigation flows
│   └── __mocks__/          # Mock data
├── vitest.config.ts        # Vitest configuration
├── playwright.config.ts    # Playwright configuration
└── tsconfig.json           # TypeScript configuration
```

### Frontend Test Coverage Targets

| Area              | Target | Current | Gap     |
|-------------------|--------|---------|---------|
| Components        | 85%    | 0%      | +85%    |
| Hooks/Stores      | 90%    | 0%      | +90%    |
| Utilities         | 95%    | 0%      | +95%    |
| **Overall Frontend** | **80%** | **0%** | **+80%** |

### Frontend Test Templates

#### Component Test Template

```typescript
// src/components/workflows/__tests__/WorkflowBuilder.test.tsx

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { WorkflowBuilder } from '../WorkflowBuilder'

describe('WorkflowBuilder', () => {
  it('renders workflow canvas with initial state', () => {
    // Arrange
    const mockWorkflow = {
      id: '123',
      name: 'Test Workflow',
      steps: []
    }

    // Act
    render(<WorkflowBuilder workflow={mockWorkflow} />)

    // Assert
    expect(screen.getByText('Test Workflow')).toBeInTheDocument()
    expect(screen.getByTestId('workflow-canvas')).toBeInTheDocument()
  })

  it('adds new step when clicking add step button', async () => {
    // Arrange
    const onAddStep = vi.fn()
    render(<WorkflowBuilder workflow={mockWorkflow} onAddStep={onAddStep} />)

    // Act
    fireEvent.click(screen.getByText('Add Step'))

    // Assert
    await waitFor(() => {
      expect(onAddStep).toHaveBeenCalledOnce()
    })
  })

  it('displays validation error for invalid workflow name', () => {
    // Arrange
    render(<WorkflowBuilder workflow={{...mockWorkflow, name: ''}} />)

    // Act
    fireEvent.click(screen.getByText('Save'))

    // Assert
    expect(screen.getByText('Workflow name is required')).toBeInTheDocument()
  })
})
```

#### E2E Test Template

```typescript
// e2e/workflows/workflow-creation.spec.ts

import { test, expect } from '@playwright/test'

test.describe('Workflow Creation', () => {
  test('creates new workflow from scratch', async ({ page }) => {
    // Arrange
    await page.goto('/workflows')
    await page.click('text=Create Workflow')

    // Act
    await page.fill('[data-testid="workflow-name"]', 'E2E Test Workflow')
    await page.fill('[data-testid="workflow-description"]', 'Testing workflow creation')
    await page.selectOption('[data-testid="trigger-type"]', 'webhook')
    await page.click('text=Create')

    // Assert
    await expect(page).toHaveURL(/\/workflows\/[a-f0-9-]+$/)
    await expect(page.locator('text=E2E Test Workflow')).toBeVisible()
    await expect(page.locator('text=Draft')).toBeVisible()
  })

  test('adds action step to workflow', async ({ page }) => {
    // Arrange
    await page.goto('/workflows/test-workflow-id/builder')

    // Act
    await page.click('[data-testid="add-step-button"]')
    await page.click('text=Send Email')
    await page.fill('[data-testid="email-subject"]', 'Test Email')
    await page.fill('[data-testid="email-body"]', 'Test body')
    await page.click('text=Save Step')

    // Assert
    await expect(page.locator('text=Send Email')).toBeVisible()
    await expect(page.locator('[data-testid="step-count"]')).toContainText('1')
  })
})
```

---

## 3. E2E Testing Strategy

### Critical User Flows (50 tests)

#### Authentication Flows (10 tests)
- User login with valid credentials
- User login with invalid credentials
- Password reset flow
- User logout
- Session timeout
- Multi-factor authentication
- Social login (Google, OAuth)
- Account creation
- Email verification
- Password change

#### Workflow Flows (20 tests)
- Create workflow from scratch
- Create workflow from template
- Add trigger (webhook, manual, scheduled)
- Add action (send email, update contact)
- Add condition (branch logic)
- Configure wait step
- Add goal tracking
- Activate workflow
- Pause active workflow
- Edit draft workflow
- Version active workflow
- Rollback to previous version
- Delete draft workflow
- Archive workflow
- Duplicate workflow
- Export workflow
- Import workflow
- Test workflow execution
- View workflow analytics
- Clone workflow to another account

#### Contact Management Flows (10 tests)
- Create contact manually
- Import contacts via CSV
- Add contact to workflow
- Remove contact from workflow
- Update contact information
- Merge duplicate contacts
- Delete contact
- View contact timeline
- Tag contact
- Search contacts

#### Analytics & Reporting (10 tests)
- View workflow execution metrics
- View goal completion rates
- Generate workflow report
- Export analytics data
- View real-time execution log
- Compare workflow versions
- View account-wide dashboard
- Filter by date range
- Drill down into specific execution
- Share analytics report

### Cross-Browser Testing (30 tests)

- Chrome: 100% of E2E tests
- Firefox: 50% of critical flows
- Safari: 30% of critical flows
- Edge: 30% of critical flows
- Mobile (iOS Safari): 20% of critical flows
- Mobile (Chrome Android): 20% of critical flows

### Accessibility Testing (20 tests)

- WCAG 2.1 AA compliance
- Keyboard navigation
- Screen reader compatibility (NVDA, JAWS)
- Color contrast validation
- Focus management
- ARIA label validation
- Form error accessibility
- Dynamic content announcements

---

## 4. Performance Testing Strategy

### Load Testing (k6)

```javascript
// load-tests/workflow-creation.js

import http from 'k6/http'
import { check, sleep } from 'k6'

export const options = {
  stages: [
    { duration: '1m', target: 10 },   // Ramp up to 10 users
    { duration: '3m', target: 50 },   // Ramp up to 50 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests < 500ms
    http_req_failed: ['rate<0.01'],   // Error rate < 1%
  },
}

export default function () {
  const payload = JSON.stringify({
    name: `Load Test Workflow ${__VU}`,
    description: 'Performance testing',
  })

  const params = {
    headers: { 'Content-Type': 'application/json' },
  }

  const res = http.post('http://localhost:8000/api/v1/workflows', payload, params)

  check(res, {
    'status is 201': (r) => r.status === 201,
    'response time < 500ms': (r) => r.timings.duration < 500,
  })

  sleep(1)
}
```

### Performance Benchmarks

| Endpoint                | Target  | Acceptable | Critical |
|-------------------------|---------|------------|----------|
| GET /workflows          | < 200ms | < 500ms    | > 1s     |
| POST /workflows         | < 300ms | < 700ms    | > 1.5s   |
| GET /workflows/:id      | < 150ms | < 300ms    | > 500ms  |
| PATCH /workflows/:id    | < 250ms | < 600ms    | > 1s     |
| DELETE /workflows/:id   | < 200ms | < 400ms    | > 800ms  |
| POST /workflows/execute | < 500ms | < 1s       | > 2s     |

---

## 5. Security Testing Strategy

### OWASP Top 10 Coverage

1. **Injection Attacks** (SQL, NoSQL, LDAP)
   - Test all input sanitization
   - Verify parameterized queries
   - Test ORM query safety

2. **Broken Authentication**
   - Test session management
   - Verify password hashing (bcrypt, Argon2)
   - Test JWT token validation
   - Verify rate limiting on auth endpoints

3. **XSS (Cross-Site Scripting)**
   - Test all user input fields
   - Verify output encoding
   - Test CSP headers

4. **CSRF (Cross-Site Request Forgery)**
   - Verify CSRF token validation
   - Test SameSite cookie attributes

5. **Security Misconfiguration**
   - Test default credentials
   - Verify security headers
   - Test debug mode disabled

6. **SSRF (Server-Side Request Forgery)**
   - Test webhook URL validation
   - Verify URL whitelist/blacklist

### Security Test Templates

```python
# tests/security/test_sql_injection.py

import pytest

class TestSQLInjection:
    """Test suite for SQL injection prevention."""

    @pytest.mark.security
    async def test_workflow_name_sql_injection(self, async_client: AsyncClient):
        """Given SQL injection payload, when creating workflow, then sanitized."""
        # Arrange
        malicious_payloads = [
            "'; DROP TABLE workflows; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--",
        ]

        for payload in malicious_payloads:
            # Act
            response = await async_client.post("/api/v1/workflows", json={
                "name": payload
            })

            # Assert - Should either reject or sanitize, not execute SQL
            assert response.status_code in [400, 422]
            # Verify database still intact
            workflows_response = await async_client.get("/api/v1/workflows")
            assert workflows_response.status_code == 200
```

```python
# tests/security/test_authentication.py

class TestAuthenticationSecurity:
    """Test suite for authentication security."""

    async def test_jwt_token_expiration(self, async_client: AsyncClient):
        """Given expired token, when accessing API, then returns 401."""
        # Arrange
        expired_token = generate_expired_jwt_token()

        # Act
        response = await async_client.get(
            "/api/v1/workflows",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        # Assert
        assert response.status_code == 401

    async def test_password_hashing_bcrypt(self, db_session):
        """Given user password, when stored, then hashed with bcrypt."""
        # Arrange
        password = "plain_text_password"

        # Act
        user = User.create(email="test@example.com", password=password)
        await user_repo.save(user)

        # Assert
        assert user.password != password
        assert user.password.startswith("$2b$")  # bcrypt prefix
```

---

## 6. CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test-suite.yml

name: Complete Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  backend-tests:
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

      - name: Run unit tests
        run: |
          cd backend
          pytest tests/unit/ -v --cov=src --cov-report=xml

      - name: Run integration tests
        run: |
          cd backend
          pytest tests/integration/ -v

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml
          flags: backend

  frontend-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run unit tests
        run: |
          cd frontend
          npm run test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./frontend/coverage/coverage-final.json
          flags: frontend

  e2e-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci
          npx playwright install --with-deps

      - name: Install backend
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Start services
        run: |
          docker-compose up -d postgres redis
          cd backend && python -m uvicorn src.main:app &
          cd frontend && npm run dev &

      - name: Run E2E tests
        run: |
          cd frontend
          npm run test:e2e

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

---

## 7. Test Data Management

### Fixtures and Factories

```python
# tests/factories/workflow_factory.py

import factory
from uuid import uuid4
from workflows.domain.entities import Workflow
from workflows.domain.value_objects import WorkflowName, WorkflowDescription

class WorkflowFactory(factory.Factory):
    """Factory for creating Workflow entities in tests."""

    class Meta:
        model = Workflow

    id = factory.LazyFunction(uuid4)
    account_id = factory.LazyFunction(uuid4)
    name = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('text')
    status = WorkflowStatus.DRAFT
    version = 1
    trigger_type = None

    class Params:
        """Factory parameters for common test scenarios."""

        active = factory.Trait(
            status=WorkflowStatus.ACTIVE,
            trigger_type='webhook'
        )

        with_webhook_trigger = factory.Trait(
            trigger_type='webhook',
            trigger_config={'webhook_url': '/webhooks/test'}
        )

        minimal = factory.Trait(
            name='Minimal Workflow',
            description=''
        )
```

### Test Data Seeding

```python
# tests/conftest.py

import pytest
from tests.factories import WorkflowFactory, ContactFactory

@pytest.fixture(scope="function")
async def seeded_database(db_session):
    """Seed database with test data."""
    # Create 10 workflows
    workflows = [WorkflowFactory() for _ in range(10)]
    for workflow in workflows:
        await db_session.add(workflow)
    await db_session.commit()

    # Create 50 contacts
    contacts = [ContactFactory() for _ in range(50)]
    for contact in contacts:
        await db_session.add(contact)
    await db_session.commit()

    return {
        "workflows": workflows,
        "contacts": contacts
    }
```

---

## 8. Quality Gates

### Pre-Commit Quality Checks

```bash
# .pre-commit-config.yaml

repos:
  - repo: local
    hooks:
      - id: backend-unit-tests
        name: Backend unit tests
        entry: bash -c 'cd backend && pytest tests/unit/ -v'
        language: system
        pass_filenames: false

      - id: backend-lint
        name: Backend linting
        entry: bash -c 'cd backend && ruff check src tests'
        language: system
        pass_filenames: false

      - id: backend-type-check
        name: Backend type check
        entry: bash -c 'cd backend && mypy src'
        language: system
        pass_filenames: false

      - id: frontend-unit-tests
        name: Frontend unit tests
        entry: bash -c 'cd frontend && npm run test'
        language: system
        pass_filenames: false

      - id: frontend-lint
        name: Frontend linting
        entry: bash -c 'cd frontend && npm run lint'
        language: system
        pass_filenames: false

      - id: frontend-type-check
        name: Frontend type check
        entry: bash -c 'cd frontend && npm run type-check'
        language: system
        pass_filenames: false
```

### Quality Gate Thresholds

| Metric                     | Pass Criteria | Block PR? |
|----------------------------|---------------|-----------|
| Backend Coverage           | ≥ 85%         | Yes       |
| Frontend Coverage          | ≥ 80%         | Yes       |
| Backend Lint Errors        | 0             | Yes       |
| Frontend Lint Errors       | 0             | Yes       |
| Backend Type Errors        | 0             | Yes       |
| Frontend Type Errors       | 0             | Yes       |
| Unit Test Pass Rate        | 100%          | Yes       |
| Integration Test Pass Rate | 100%          | Yes       |
| E2E Test Pass Rate         | ≥ 95%         | No*       |
| Security Scan              | 0 critical    | Yes       |
| Performance Benchmarks     | All pass      | Yes       |

*E2E tests may be flaky; 95% threshold allows for occasional failures.

---

## 9. Test Execution Strategy

### Local Development

```bash
# Backend
cd backend
pytest tests/unit/ -v                          # Fast unit tests
pytest tests/integration/ -v                   # Integration tests
pytest tests/ -v --cov=src --cov-report=html   # Full suite with coverage

# Frontend
cd frontend
npm run test                                   # Unit tests with watch mode
npm run test:ui                                # Vitest UI
npm run test:e2e                               # Playwright E2E tests
```

### Pre-Commit

```bash
# Run fast tests only (< 2 minutes)
pytest tests/unit/ -m "not slow" -v
npm run test
```

### Pre-Push

```bash
# Run full test suite
pytest tests/ -v
npm run test
npm run test:e2e
```

### CI/CD Pipeline

```bash
# Parallel execution for speed
pytest tests/unit/ -v -n auto                   # Parallel unit tests
pytest tests/integration/ -v -n auto            # Parallel integration tests
npm run test -- --reporter=verbose --threads    # Parallel frontend tests
npm run test:e2e --workers=4                    # Parallel E2E tests
```

---

## 10. Mock Strategy

### Backend Mocking

```python
# tests/unit/mocks/mock_external_service.py

from unittest.mock import AsyncMock
from workflows.infrastructure.external_email_service import EmailService

class MockEmailService:
    """Mock for EmailService with predefined responses."""

    def __init__(self):
        self.send_email = AsyncMock(return_value={
            "success": True,
            "message_id": "mock-message-id"
        })
        self.bulk_send = AsyncMock(return_value={
            "success": True,
            "sent_count": 10,
            "failed_count": 0
        })

@pytest.fixture
def mock_email_service():
    """Fixture providing mocked email service."""
    return MockEmailService()
```

### Frontend Mocking

```typescript
// src/__mocks__/msw/handlers.ts

import { http, HttpResponse } from 'msw'

export const handlers = [
  // Mock workflow API
  http.get('/api/v1/workflows', () => {
    return HttpResponse.json({
      workflows: [
        { id: '1', name: 'Mock Workflow 1', status: 'active' },
        { id: '2', name: 'Mock Workflow 2', status: 'draft' },
      ]
    })
  }),

  http.post('/api/v1/workflows', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({
      id: 'mock-id',
      ...body,
      status: 'draft',
      created_at: new Date().toISOString()
    }, { status: 201 })
  }),
]
```

---

## 11. Flaky Test Prevention

### Retry Logic

```python
# tests/conftest.py

@pytest.fixture
def stable_api_client():
    """API client with retry logic for flaky network tests."""
    client = AsyncClient(app=app, base_url="http://test")
    max_retries = 3

    async def request_with_retry(method, url, **kwargs):
        for attempt in range(max_retries):
            try:
                response = await client.request(method, url, **kwargs)
                if response.status_code not in [502, 503, 504]:
                    return response
            except (httpx.TimeoutException, httpx.ConnectError):
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(0.5 * (attempt + 1))
        return response

    return request_with_retry
```

### Test Isolation

```python
# Each test gets fresh database state
@pytest.fixture(scope="function")
async def isolated_db_session():
    """Create isolated database session for each test."""
    async with TestDatabase.session() as session:
        yield session
        await session.rollback()
        await session.close()
```

---

## 12. Reporting and Metrics

### Coverage Reports

- HTML reports: `htmlcov/index.html` (backend), `coverage/index.html` (frontend)
- XML reports: For CI/CD integration
- JSON reports: For trend analysis
- Console summary: For quick feedback

### Test Metrics Dashboard

Track the following metrics:

- Total test count
- Pass rate (target: 100% for unit/integration, ≥ 95% for E2E)
- Execution time (target: < 5 min for unit, < 15 min for full suite)
- Coverage percentage (backend ≥ 85%, frontend ≥ 80%)
- Flake rate (target: < 1%)
- Test failure distribution by module

---

## 13. Implementation Timeline

### Phase 1: Backend Unit Tests (Week 1-2)
- [ ] Create 1200 backend unit tests
- [ ] Set up pytest infrastructure
- [ ] Create test fixtures and factories
- [ ] Achieve 90% backend coverage

### Phase 2: Frontend Unit Tests (Week 2-3)
- [ ] Create 400 frontend unit tests
- [ ] Set up Vitest infrastructure
- [ ] Create component test templates
- [ ] Achieve 80% frontend coverage

### Phase 3: Integration Tests (Week 3-4)
- [ ] Create 300 integration tests
- [ ] Set up test databases and services
- [ ] Test API endpoints end-to-end
- [ ] Verify data persistence

### Phase 4: E2E Tests (Week 4-5)
- [ ] Create 100 E2E tests with Playwright
- [ ] Cover critical user flows
- [ ] Set up cross-browser testing
- [ ] Add accessibility tests

### Phase 5: Performance & Security Tests (Week 5-6)
- [ ] Create 50 performance tests
- [ ] Create 50 security tests
- [ ] Set up load testing infrastructure
- [ ] Verify OWASP compliance

### Phase 6: CI/CD Integration (Week 6-7)
- [ ] Configure GitHub Actions workflows
- [ ] Set up quality gates
- [ ] Configure coverage reporting
- [ ] Set up performance benchmarking

---

## 14. Success Criteria

The testing suite will be considered complete when:

1. **Test Count**: 2000+ tests across all categories
   - Unit tests: 1600+ tests
   - Integration tests: 300+ tests
   - E2E tests: 100+ tests
   - Performance tests: 50+ tests
   - Security tests: 50+ tests

2. **Coverage**: Minimum targets met
   - Backend: ≥ 90% coverage
   - Frontend: ≥ 80% coverage

3. **Quality Gates**: All TRUST 5 principles met
   - Tested: All code paths exercised
   - Readable: Clear test documentation
   - Unified: Consistent test patterns
   - Secured: Security tests passing
   - Trackable: All changes testable

4. **CI/CD**: Automated testing pipeline
   - Tests run on every commit
   - Coverage gates enforced
   - Performance benchmarks validated
   - Security scans integrated

5. **Execution Time**: Fast feedback loop
   - Unit tests: < 2 minutes
   - Integration tests: < 5 minutes
   - E2E tests: < 15 minutes
   - Full suite: < 20 minutes

---

**Document Version:** 1.0.0
**Last Updated:** 2026-02-07
**Status:** Active
**Implementation:** In Progress
