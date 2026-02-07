"""Pytest fixtures for workflow tests.

This module provides reusable fixtures for workflow testing.
"""

from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.database import get_db, Base


@pytest.fixture
async def test_account_id() -> str:
    """Provide a test account ID."""
    from uuid import uuid4
    return str(uuid4())


@pytest.fixture
async def test_user_id() -> str:
    """Provide a test user ID."""
    from uuid import uuid4
    return str(uuid4())


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a test database session.

    This fixture creates a new database session for each test
    and handles cleanup after the test completes.
    """
    # Create test database engine
    # In production, this would use a separate test database
    from src.core.config import settings

    engine = create_async_engine(
        settings.database_url,
        echo=False,
        future=True,
    )

    async_session_maker = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session

    await engine.dispose()
