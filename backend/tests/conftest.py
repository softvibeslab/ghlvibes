"""Pytest configuration and shared fixtures.

This module provides fixtures for testing including:
- Async database sessions with test database
- HTTP client for API testing
- Mock authentication
- Sample data factories
"""

import asyncio
from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from jose import jwt
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.database import Base, get_db


# Test database URL - uses the same database with test_ prefix
TEST_DATABASE_URL = settings.database_url.replace(
    f"/{settings.database_name}",
    f"/{settings.database_name}_test",
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests.

    This fixture creates a single event loop for the entire test session.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine.

    Creates an async engine connected to the test database.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional database session for tests.

    Each test gets its own session that rolls back after the test,
    ensuring test isolation.
    """
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session() as session:
        # Start a savepoint for rollback
        async with session.begin():
            yield session
            # Rollback is automatic when exiting the context


@pytest.fixture(scope="function")
def override_get_db(db_session: AsyncSession):
    """Override the get_db dependency to use the test session."""

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    return _override_get_db


@pytest.fixture(scope="function")
async def app(override_get_db) -> FastAPI:
    """Create FastAPI application with test dependencies."""
    from src.main import create_app

    application = create_app()
    application.dependency_overrides[get_db] = override_get_db
    return application


@pytest.fixture(scope="function")
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for API testing."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# Test data fixtures


@pytest.fixture
def test_account_id() -> UUID:
    """Provide a consistent test account ID."""
    return UUID("12345678-1234-5678-1234-567812345678")


@pytest.fixture
def test_user_id() -> UUID:
    """Provide a consistent test user ID."""
    return UUID("87654321-4321-8765-4321-876543218765")


@pytest.fixture
def auth_token(test_user_id: UUID, test_account_id: UUID) -> str:
    """Generate a valid JWT token for testing.

    Args:
        test_user_id: The user ID to embed in the token.
        test_account_id: The account ID to embed in the token.

    Returns:
        A valid JWT token string.
    """
    payload = {
        "sub": str(test_user_id),
        "account_id": str(test_account_id),
        "email": "test@example.com",
        "roles": ["admin", "user"],
        "exp": datetime.now(UTC) + timedelta(hours=1),
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


@pytest.fixture
def auth_headers(auth_token: str) -> dict[str, str]:
    """Provide authorization headers with test token."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def non_admin_token(test_user_id: UUID, test_account_id: UUID) -> str:
    """Generate a token without admin role."""
    payload = {
        "sub": str(test_user_id),
        "account_id": str(test_account_id),
        "email": "user@example.com",
        "roles": ["user"],
        "exp": datetime.now(UTC) + timedelta(hours=1),
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


@pytest.fixture
def non_admin_headers(non_admin_token: str) -> dict[str, str]:
    """Provide authorization headers without admin role."""
    return {"Authorization": f"Bearer {non_admin_token}"}


# Sample workflow data


@pytest.fixture
def sample_workflow_data() -> dict[str, Any]:
    """Provide sample workflow creation data."""
    return {
        "name": "Test Workflow",
        "description": "A test workflow for automated testing",
        "trigger_type": "contact_created",
        "trigger_config": {"filters": {"tags": ["new-lead"]}},
    }


@pytest.fixture
def minimal_workflow_data() -> dict[str, Any]:
    """Provide minimal valid workflow data."""
    return {"name": "Minimal Workflow"}


@pytest.fixture
def invalid_workflow_data() -> dict[str, Any]:
    """Provide invalid workflow data for error testing."""
    return {"name": "ab"}  # Too short, minimum is 3 characters
