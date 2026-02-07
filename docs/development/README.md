# Development Guide

Complete guide for contributing to and developing the GoHighLevel Clone platform.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Backend Development](#backend-development)
- [Frontend Development](#frontend-development)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [DDD Methodology](#ddd-methodology)

## Getting Started

### Prerequisites

- **Python**: 3.12 or higher
- **Node.js**: 20.x or higher
- **Docker**: Latest version
- **Git**: Latest version
- **Editor**: VS Code (recommended) with extensions

### VS Code Extensions

```
- Python (Microsoft)
- Pylance (Microsoft)
- Python Test Explorer (LittleFoxTeam)
- ESLint (Microsoft)
- Prettier (Prettier)
- Tailwind CSS IntelliSense (Tailwind Labs)
- GitLens (GitKraken)
- Thunder Client (for API testing)
```

### Clone Repository

```bash
git clone https://github.com/your-org/gohighlevel-clone.git
cd gohighlevel-clone
```

### Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e '.[dev]'

# Setup pre-commit hooks
pre-commit install

# Run database migrations
alembic upgrade head

# Start development server
uvicorn src.main:app --reload
```

### Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Development Workflow

### SPEC-First DDD Methodology

This project follows MoAI-ADK SPEC-First development:

```bash
# 1. Plan: Create specification
/moai:1-plan "Implement contact management with custom fields"

# 2. Run: Implement with DDD
/moai:2-run SPEC-CNT-001

# 3. Sync: Document and deploy
/moai:3-sync SPEC-CNT-001
```

### Git Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/contact-management
   ```

2. **Make Changes**
   - Write code following TRUST 5 standards
   - Add tests for new functionality
   - Update documentation

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add contact custom fields"
   ```

4. **Push and Create PR**
   ```bash
   git push origin feature/contact-management
   # Create PR on GitHub
   ```

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(workflows): add webhook trigger type
fix(auth): resolve JWT refresh token issue
docs(api): update workflow endpoint documentation
test(contacts): add integration tests for contact CRUD
```

## Backend Development

### Project Structure (Backend)

```
backend/
├── src/
│   ├── core/                    # Core utilities
│   │   ├── config.py            # Settings
│   │   ├── database.py          # DB session
│   │   └── dependencies.py      # FastAPI deps
│   ├── workflows/               # Workflow module
│   │   ├── domain/              # Business logic
│   │   │   ├── entities.py
│   │   │   ├── value_objects.py
│   │   │   └── exceptions.py
│   │   ├── application/         # Use cases
│   │   │   ├── commands/
│   │   │   └── queries/
│   │   ├── infrastructure/      # Data access
│   │   │   ├── models.py
│   │   │   └── repositories/
│   │   └── presentation/        # API layer
│   │       ├── routes.py
│   │       └── schemas.py
│   └── main.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── alembic/
```

### Clean Architecture Pattern

**Domain Layer** (Business Logic)
```python
# src/workflows/domain/entities.py
class Workflow:
    def __init__(self, name: str, account_id: UUID):
        self.id = uuid4()
        self.name = name
        self.account_id = account_id
        self.status = WorkflowStatus.DRAFT

    def activate(self) -> None:
        if self.status != WorkflowStatus.DRAFT:
            raise InvalidWorkflowStatusTransitionError(
                current_status=self.status,
                target_status=WorkflowStatus.ACTIVE
            )
        self.status = WorkflowStatus.ACTIVE
```

**Application Layer** (Use Cases)
```python
# src/workflows/application/commands/create_workflow.py
class CreateWorkflowUseCase:
    def __init__(self, repository: WorkflowRepository):
        self.repository = repository

    async def execute(self, request: CreateWorkflowRequest) -> Workflow:
        workflow = Workflow(
            name=request.name,
            account_id=request.account_id
        )
        await self.repository.save(workflow)
        return workflow
```

**Infrastructure Layer** (Data Access)
```python
# src/workflows/infrastructure/repositories/sqlalchemy_workflow_repository.py
class SQLAlchemyWorkflowRepository(WorkflowRepository):
    async def save(self, workflow: Workflow) -> None:
        async with self.session:
            model = WorkflowModel.from_entity(workflow)
            self.session.add(model)
            await self.session.commit()
```

**Presentation Layer** (API)
```python
# src/workflows/presentation/routes.py
@router.post("", response_model=WorkflowResponse)
async def create_workflow(
    body: CreateWorkflowRequest,
    use_case: CreateWorkflowUseCaseDep,
) -> WorkflowResponse:
    result = await use_case.execute(request=body)
    return WorkflowResponse.from_entity(result)
```

### Adding a New Feature

1. **Define Domain Entity**
2. **Create Value Objects**
3. **Define Domain Exceptions**
4. **Implement Use Case**
5. **Create Repository Interface**
6. **Implement Repository**
7. **Add API Route**
8. **Write Tests**
9. **Update Documentation**

### Code Quality Standards

**TRUST 5 Framework:**

- **Tested**: 85%+ test coverage
- **Readable**: Clear naming, English comments
- **Unified**: Consistent patterns
- **Secured**: OWASP compliance
- **Trackable**: Audit logs

**Python Style:**
- Follow PEP 8
- Use ruff for linting
- Use mypy for type checking
- Maximum line length: 100 characters

**Example:**
```python
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def get_workflow(
    workflow_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    repo: Annotated[WorkflowRepository, Depends(get_workflow_repo)],
) -> Workflow:
    """Get workflow by ID.

    Args:
        workflow_id: Workflow UUID
        session: Database session
        repo: Workflow repository

    Returns:
        Workflow entity

    Raises:
        WorkflowNotFoundError: If workflow not found
    """
    workflow = await repo.get_by_id(workflow_id)
    if not workflow:
        raise WorkflowNotFoundError(workflow_id=workflow_id)
    return workflow
```

## Frontend Development

### Project Structure (Frontend)

```
frontend/
├── src/
│   ├── app/                     # Next.js App Router
│   │   ├── workflows/
│   │   │   ├── page.tsx
│   │   │   └── [id]/
│   │   │       └── page.tsx
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── ui/                  # Shadcn components
│   │   ├── workflows/
│   │   └── contacts/
│   ├── lib/
│   │   ├── api.ts               # API client
│   │   ├── query.ts             # TanStack Query
│   │   └── utils.ts
│   └── styles/
├── public/
└── package.json
```

### Component Example

```typescript
// src/components/workflows/workflow-list.tsx
"use client"

import { useQuery } from "@tanstack/react-query"
import { Workflow } from "@/types"

export function WorkflowList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["workflows"],
    queryFn: async () => {
      const response = await fetch("/api/v1/workflows")
      if (!response.ok) throw new Error("Failed to fetch")
      return response.json()
    },
  })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error loading workflows</div>

  return (
    <div className="grid gap-4">
      {data?.items?.map((workflow: Workflow) => (
        <WorkflowCard key={workflow.id} workflow={workflow} />
      ))}
    </div>
  )
}
```

### State Management with Zustand

```typescript
// src/lib/store/workflow-store.ts
import { create } from "zustand"

interface WorkflowStore {
  selectedWorkflow: Workflow | null
  setSelectedWorkflow: (workflow: Workflow | null) => void
}

export const useWorkflowStore = create<WorkflowStore>((set) => ({
  selectedWorkflow: null,
  setSelectedWorkflow: (workflow) => set({ selectedWorkflow: workflow }),
}))
```

### API Client with TanStack Query

```typescript
// src/lib/api/workflows.ts
import { useMutation, useQuery } from "@tanstack/react-query"

export function useCreateWorkflow() {
  return useMutation({
    mutationFn: async (data: CreateWorkflowRequest) => {
      const response = await fetch("/api/v1/workflows", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      })
      if (!response.ok) throw new Error("Failed to create workflow")
      return response.json()
    },
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ["workflows"] })
    },
  })
}
```

## Testing

### Backend Testing

**Unit Tests**
```python
# tests/workflows/domain/test_workflow.py
import pytest
from src.workflows.domain.entities import Workflow
from src.workflows.domain.exceptions import InvalidWorkflowStatusTransitionError

def test_workflow_activate_from_draft():
    workflow = Workflow(name="Test", account_id=uuid4())
    workflow.activate()
    assert workflow.status == WorkflowStatus.ACTIVE

def test_workflow_activate_from_active_fails():
    workflow = Workflow(name="Test", account_id=uuid4())
    workflow.status = WorkflowStatus.ACTIVE
    with pytest.raises(InvalidWorkflowStatusTransitionError):
        workflow.activate()
```

**Integration Tests**
```python
# tests/workflows/integration/test_create_workflow_endpoint.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_workflow_endpoint(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/workflows",
        json={"name": "Test Workflow"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Workflow"
```

**Run Tests**
```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific test file
pytest tests/workflows/domain/test_workflow.py -v
```

### Frontend Testing

**Unit Tests (Vitest)**
```typescript
// src/components/workflows/__tests__/workflow-card.test.tsx
import { render, screen } from "@testing-library/react"
import { WorkflowCard } from "../workflow-card"

describe("WorkflowCard", () => {
  it("renders workflow name", () => {
    render(<WorkflowCard workflow={{ id: "1", name: "Test" }} />)
    expect(screen.getByText("Test")).toBeInTheDocument()
  })
})
```

**E2E Tests (Playwright)**
```typescript
// tests/e2e/workflows.spec.ts
import { test, expect } from "@playwright/test"

test("create workflow", async ({ page }) => {
  await page.goto("/workflows")
  await page.click("text=Create Workflow")
  await page.fill('[name="name"]', "Test Workflow")
  await page.click("text=Create")
  await expect(page.locator("text=Test Workflow")).toBeVisible()
})
```

**Run Tests**
```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Type checking
npm run type-check
```

## Code Quality

### Backend Linting and Formatting

```bash
# Check linting
ruff check src/

# Fix linting issues
ruff check src/ --fix

# Format code
ruff format src/

# Type checking
mypy src/
```

### Frontend Linting and Formatting

```bash
# Lint
npm run lint

# Fix linting
npm run lint -- --fix

# Format
npm run format

# Type check
npm run type-check
```

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit:

```bash
# .git/hooks/pre-commit
ruff check src/ --fix
ruff format src/
mypy src/
pytest tests/ --cov=src --cov-fail-under=85
```

## DDD Methodology

### ANALYZE Phase

Understand existing behavior and code structure.

```python
# Read existing code
# Identify dependencies
# Map domain boundaries
```

### PRESERVE Phase

Create characterization tests for existing behavior.

```python
def test_existing_workflow_behavior():
    # Capture current behavior
    workflow = Workflow(name="Test", account_id=uuid4())
    assert workflow.status == WorkflowStatus.DRAFT
    assert workflow.id is not None
```

### IMPROVE Phase

Make small, incremental changes.

```python
# Add new feature
# Run characterization tests
# Verify behavior preservation
```

### VALIDATE Phase

Ensure quality standards.

```bash
pytest tests/ --cov=src --cov-fail-under=85
ruff check src/
mypy src/
```

## Common Patterns

### Repository Pattern

```python
from abc import ABC, abstractmethod

class WorkflowRepository(ABC):
    @abstractmethod
    async def get_by_id(self, workflow_id: UUID) -> Workflow | None:
        pass

    @abstractmethod
    async def save(self, workflow: Workflow) -> None:
        pass
```

### Dependency Injection

```python
from fastapi import Depends

def get_workflow_repository(
    session: AsyncSession = Depends(get_db)
) -> WorkflowRepository:
    return SQLAlchemyWorkflowRepository(session)
```

### Error Handling

```python
from src.workflows.domain.exceptions import WorkflowNotFoundError

@router.get("/{workflow_id}")
async def get_workflow(
    workflow_id: UUID,
    repo: WorkflowRepository = Depends(get_workflow_repository)
):
    try:
        workflow = await repo.get_by_id(workflow_id)
        if not workflow:
            raise WorkflowNotFoundError(workflow_id=workflow_id)
        return WorkflowResponse.from_entity(workflow)
    except WorkflowNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
```

## Related Documentation

- [Testing Guide](./testing.md)
- [DDD Methodology](./ddd.md)
- [Architecture](../architecture/system.md)
- [API Reference](../api/README.md)
