"""Extended pytest configuration for comprehensive testing."""

import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base, get_db
from src.main import app
from src.workflows.domain.entities import Workflow
from tests.factories import (
    WorkflowFactory,
    TriggerFactory,
    ActionFactory,
    ConditionFactory,
    GoalFactory,
)


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client with database dependency override."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_workflow_data():
    """Sample workflow creation data."""
    return {
        "name": "Test Workflow",
        "description": "Test description",
        "trigger_type": "webhook",
    }


@pytest.fixture
def sample_trigger_data():
    """Sample trigger creation data."""
    return {
        "trigger_type": "webhook",
        "config": {"webhook_url": "/webhooks/test"}
    }


@pytest.fixture
def sample_action_data():
    """Sample action creation data."""
    return {
        "action_type": "send_email",
        "config": {
            "to": "{{contact.email}}",
            "subject": "Test Email",
            "body": "Test body"
        }
    }


@pytest.fixture
def sample_condition_data():
    """Sample condition creation data."""
    return {
        "condition_type": "field_comparison",
        "operator": "equals",
        "field": "status",
        "value": "premium"
    }


@pytest.fixture
async def seeded_workflows(db_session: AsyncSession) -> list[Workflow]:
    """Seed database with test workflows."""
    workflows = [
        WorkflowFactory.build(id=uuid4()),
        WorkflowFactory.build(id=uuid4()),
        WorkflowFactory.build(id=uuid4()),
    ]

    for workflow in workflows:
        db_session.add(workflow)
    await db_session.commit()

    return workflows


@pytest.fixture
async def seeded_workflow_with_trigger(db_session: AsyncSession) -> Workflow:
    """Seed database with workflow and trigger."""
    workflow = WorkflowFactory.build(id=uuid4())
    trigger = TriggerFactory.build(workflow_id=workflow.id)

    db_session.add(workflow)
    db_session.add(trigger)
    await db_session.commit()

    return workflow


@pytest.fixture
async def seeded_workflow_with_actions(db_session: AsyncSession) -> Workflow:
    """Seed database with workflow and multiple actions."""
    workflow = WorkflowFactory.build(id=uuid4())
    actions = [
        ActionFactory.build(workflow_id=workflow.id, order=1),
        ActionFactory.build(workflow_id=workflow.id, order=2),
        ActionFactory.build(workflow_id=workflow.id, order=3),
    ]

    db_session.add(workflow)
    for action in actions:
        db_session.add(action)
    await db_session.commit()

    return workflow


# Performance testing fixtures
@pytest.fixture
def benchmark_iterations():
    """Number of iterations for benchmark tests."""
    return 1000


@pytest.fixture
def performance_thresholds():
    """Performance thresholds for tests."""
    return {
        "api_response_time_ms": 500,
        "db_query_time_ms": 100,
        "workflow_creation_time_ms": 300,
    }


# Security testing fixtures
@pytest.fixture
def sql_injection_payloads():
    """SQL injection payloads for security testing."""
    return [
        "'; DROP TABLE workflows; --",
        "1' OR '1'='1",
        "admin'--",
        "' UNION SELECT * FROM users--",
        "'; EXEC xp_cmdshell('dir'); --",
    ]


@pytest.fixture
def xss_payloads():
    """XSS payloads for security testing."""
    return [
        "<script>alert('xss')</script>",
        "<img src=x onerror=alert('xss')>",
        "<svg onload=alert('xss')>",
        "javascript:alert('xss')",
        "<iframe src='javascript:alert(xss)>",
    ]


@pytest.fixture
def path_traversal_payloads():
    """Path traversal payloads for security testing."""
    return [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
        "....//....//....//etc/passwd",
        "%2e%2e%2fetc%2fpasswd",
    ]


# Test markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "requires_redis: Tests requiring Redis")
    config.addinivalue_line("markers", "requires_postgres: Tests requiring PostgreSQL")
