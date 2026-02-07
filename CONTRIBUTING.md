# Contributing Guide

Thank you for your interest in contributing to GoHighLevel Clone! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Standards](#documentation-standards)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and considerate in all interactions.

### Standards

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

### Reporting Issues

If you encounter or witness any violations of this code of conduct, please contact us at conduct@gohighlevel-clone.com.

## Getting Started

### Fork and Clone

```bash
# Fork the repository on GitHub
git clone https://github.com/YOUR_USERNAME/gohighlevel-clone.git
cd gohighlevel-clone
git remote add upstream https://github.com/original-org/gohighlevel-clone.git
```

### Setup Development Environment

See [Development Guide](docs/development/README.md) for detailed setup instructions.

### Choose an Issue

1. Check [Good First Issues](https://github.com/your-org/gohighlevel-clone/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
2. Comment on the issue you want to work on
3. Wait for assignment

## Development Workflow

### 1. Create Branch

```bash
git fetch upstream
git checkout upstream/main -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or changes

### 2. Make Changes

Follow the [SPEC-First DDD Methodology](docs/development/README.md#ddd-methodology):

```bash
# Plan: Create specification
/moai:1-plan "Implement your feature description"

# Run: Implement with DDD
/moai:2-run SPEC-XXX

# Sync: Document and prepare PR
/moai:3-sync SPEC-XXX
```

### 3. Write Tests

Ensure all tests pass and coverage remains above 85%:

```bash
# Backend
cd backend
pytest tests/ -v --cov=src --cov-report=html

# Frontend
cd frontend
npm run test
npm run type-check
```

### 4. Update Documentation

- Update API documentation for API changes
- Update user-facing docs for feature changes
- Update README if needed
- Add examples for new features

### 5. Commit Changes

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git add .
git commit -m "feat(workflows): add webhook trigger type

- Add webhook_received trigger type
- Support custom webhook URL configuration
- Add authentication options
- Include integration tests

Closes #123"
```

Commit types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### 6. Sync and Push

```bash
git fetch upstream
git rebase upstream/main
git push origin feature/your-feature-name
```

## Pull Request Process

### 1. Create Pull Request

- Go to the repository on GitHub
- Click "New Pull Request"
- Select your feature branch
- Fill in the PR template

### 2. PR Title

Use the same format as commit messages:

```
feat(workflows): add webhook trigger type
fix(auth): resolve JWT refresh token issue
docs(api): update workflow endpoint documentation
```

### 3. PR Description

Answer these questions:

- **What does this PR do?**
- **Why is it needed?**
- **How was it tested?**
- **Are there breaking changes?**
- **Screenshots (if applicable)**

### 4. PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] E2E tests added/updated
- [ ] All tests passing

## Checklist
- [ ] Code follows TRUST 5 standards
- [ ] 85%+ test coverage maintained
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Commit messages follow conventions

## Related Issues
Fixes #123
Related to #456
```

### 5. Code Review

- Address all review comments
- Update tests as needed
- Keep PRs focused and small (< 500 lines)
- Large PRs should be split into multiple smaller PRs

### 6. Approval and Merge

- At least one approval required
- All CI checks must pass
- No merge conflicts
- Maintainer will merge

## Coding Standards

### Python (Backend)

**Style Guide**: PEP 8

**Tools**:
- `ruff` - Linting and formatting
- `mypy` - Type checking
- `pytest` - Testing

**Standards**:
```python
# Good
from typing import Annotated
from uuid import UUID

from fastapi import Depends


async def get_workflow(
    workflow_id: UUID,
    repo: Annotated[WorkflowRepository, Depends(get_workflow_repo)],
) -> Workflow:
    """Get workflow by ID.

    Args:
        workflow_id: Workflow UUID
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

**Rules**:
- Use type hints for all functions
- Maximum line length: 100 characters
- Use docstrings for all public functions
- Follow snake_case naming
- Import order: stdlib, third-party, local

### TypeScript (Frontend)

**Style Guide**: Airbnb Style Guide

**Tools**:
- `ESLint` - Linting
- `Prettier` - Formatting
- `Vitest` - Testing

**Standards**:
```typescript
// Good
import { useQuery } from "@tanstack/react-query"

interface WorkflowProps {
  workflowId: string
}

export function Workflow({ workflowId }: WorkflowProps) {
  const { data, isLoading } = useQuery({
    queryKey: ["workflow", workflowId],
    queryFn: () => fetchWorkflow(workflowId),
  })

  if (isLoading) return <div>Loading...</div>
  return <div>{data?.name}</div>
}
```

**Rules**:
- Use TypeScript strict mode
- Prefer function components
- Use hooks for state and side effects
- Follow PascalCase for components
- Follow camelCase for variables and functions

### TRUST 5 Quality Framework

All code must meet TRUST 5 standards:

**Tested** (T):
- 85%+ test coverage
- Unit, integration, and E2E tests
- Characterization tests for refactoring

**Readable** (R):
- Clear naming conventions
- Comprehensive documentation
- Code comments for complex logic
- Consistent patterns

**Unified** (U):
- Single source of truth
- Consistent coding style
- Shared type definitions
- DRY principles

**Secured** (S):
- OWASP compliance
- Input validation
- Authentication and authorization
- Audit logging

**Trackable** (T):
- Semantic versioning
- Git history
- CHANGELOG updates
- Audit trails

## Testing Guidelines

### Test Coverage

- **Minimum Coverage**: 85%
- **Target Coverage**: 90%+
- **Critical Paths**: 100%

### Test Types

**Unit Tests**:
- Test individual functions/classes
- No external dependencies (mocked)
- Fast execution (< 1ms per test)

**Integration Tests**:
- Test component interactions
- Real database (test instance)
- Medium execution (< 100ms per test)

**E2E Tests**:
- Test complete user flows
- Real browser and API
- Slower execution (< 5s per test)

### Writing Tests

**Good Test**:
```python
def test_workflow_activate_from_draft():
    # Arrange
    workflow = Workflow(name="Test", account_id=uuid4())

    # Act
    workflow.activate()

    # Assert
    assert workflow.status == WorkflowStatus.ACTIVE
```

**Test Structure**:
- Arrange: Setup test data
- Act: Execute behavior
- Assert: Verify results

### Test Naming

Use descriptive names:
```python
# Good
def test_workflow_activate_from_draft()
def test_workflow_activate_from_active_raises_error()

# Bad
def test_workflow()
def test_activate()
```

## Documentation Standards

### Code Documentation

**Python Docstrings** (Google Style):
```python
def create_workflow(name: str, account_id: UUID) -> Workflow:
    """Create a new workflow.

    Args:
        name: Workflow name (3-100 characters)
        account_id: Account UUID

    Returns:
        Created workflow entity

    Raises:
        InvalidWorkflowNameError: If name validation fails
        WorkflowAlreadyExistsError: If workflow name already exists

    Examples:
        >>> workflow = create_workflow("Welcome", account_id)
        >>> print(workflow.status)
        draft
    """
```

**TypeScript JSDoc**:
```typescript
/**
 * Creates a new workflow
 *
 * @param name - Workflow name (3-100 characters)
 * @param accountId - Account UUID
 * @returns Created workflow
 * @throws {InvalidWorkflowNameError} If name validation fails
 *
 * @example
 * ```typescript
 * const workflow = await createWorkflow("Welcome", accountId)
 * console.log(workflow.status)
 * ```
 */
async function createWorkflow(
  name: string,
  accountId: string
): Promise<Workflow>
```

### API Documentation

- Update OpenAPI/Swagger docs for API changes
- Provide examples for all endpoints
- Document error responses
- Include authentication requirements

### User Documentation

- Update user manual for new features
- Provide screenshots for UI changes
- Include step-by-step tutorials
- Add troubleshooting sections

### README Updates

Update README.md for:
- New features
- Configuration changes
- Breaking changes
- New dependencies

## Issue Reporting

### Bug Reports

Include:
- Clear title
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details
- Screenshots/logs if applicable

**Bug Report Template**:
```markdown
## Description
Clear description of the bug

## Steps to Reproduce
1. Go to...
2. Click on...
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS:
- Browser:
- Version:

## Screenshots/Logs
```

### Feature Requests

Include:
- Clear description of the feature
- Use case/motivation
- Proposed solution
- Alternative approaches considered

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project website

### Becoming a Maintainer

Active contributors may be invited to become maintainers:
- Consistent quality contributions
- Helpful in code reviews
- Active in discussions
- Understanding of project goals

## Questions?

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/gohighlevel-clone/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/gohighlevel-clone/discussions)
- **Email**: contributors@gohighlevel-clone.com

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

Thank you for contributing to GoHighLevel Clone! Your contributions make this project better for everyone.
