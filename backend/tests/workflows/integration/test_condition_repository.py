"""Integration tests for condition repository.

These tests require a test database to be available.
"""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.database import Base
from src.workflows.domain.condition_entities import Branch, Condition
from src.workflows.domain.condition_value_objects import (
    BranchType,
    ConditionConfig,
    ConditionType,
)
from src.workflows.infrastructure.condition_models import (
    BranchModel,
    ConditionModel,
)
from src.workflows.infrastructure.condition_repository import (
    IConditionRepository,
    PostgresConditionRepository,
)


@pytest.fixture
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def test_session(test_engine):
    """Create test database session."""
    async_session_maker = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session


@pytest.fixture
def condition_repository(test_session: AsyncSession) -> IConditionRepository:
    """Create condition repository."""
    return PostgresConditionRepository(test_session)


@pytest.fixture
def workflow_id() -> str:
    """Fixture for workflow ID."""
    return uuid4()


@pytest.fixture
def account_id() -> str:
    """Fixture for account ID."""
    return uuid4()


@pytest.fixture
def user_id() -> str:
    """Fixture for user ID."""
    return uuid4()


class TestConditionRepository:
    """Integration tests for PostgresConditionRepository."""

    @pytest.mark.asyncio
    async def test_create_condition(
        self, condition_repository, workflow_id, account_id, user_id
    ) -> None:
        """Test creating a condition configuration."""
        # Create condition
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_FIELD_EQUALS,
            field="email",
            operator="contains",
            value="@gmail.com",
        )

        condition = Condition.create(
            workflow_id=workflow_id,
            node_id=uuid4(),
            condition_type="contact_field_equals",
            branch_type=BranchType.IF_ELSE,
            configuration=config,
            position_x=200,
            position_y=300,
            created_by=user_id,
        )

        # Save to repository
        saved_condition = await condition_repository.create(condition)

        # Verify
        assert saved_condition is not None
        assert saved_condition.id == condition.id
        assert saved_condition.workflow_id == workflow_id
        assert len(saved_condition.branches) == 2

    @pytest.mark.asyncio
    async def test_get_by_id(
        self, condition_repository, workflow_id, account_id, user_id
    ) -> None:
        """Test retrieving a condition by ID."""
        # Create condition
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_HAS_TAG,
            tags=["lead"],
        )

        condition = Condition.create(
            workflow_id=workflow_id,
            node_id=uuid4(),
            condition_type="contact_has_tag",
            branch_type=BranchType.MULTI_BRANCH,
            configuration=config,
            position_x=100,
            position_y=200,
            created_by=user_id,
        )

        saved_condition = await condition_repository.create(condition)

        # Retrieve by ID
        retrieved_condition = await condition_repository.get_by_id(
            saved_condition.id, account_id
        )

        # Verify
        assert retrieved_condition is not None
        assert retrieved_condition.id == saved_condition.id
        assert retrieved_condition.condition_type == "contact_has_tag"

    @pytest.mark.asyncio
    async def test_list_by_workflow(
        self, condition_repository, workflow_id, account_id, user_id
    ) -> None:
        """Test listing conditions by workflow."""
        # Create multiple conditions
        for i in range(3):
            config = ConditionConfig(
                condition_type=ConditionType.CONTACT_FIELD_EQUALS,
                field="email",
                operator="contains",
                value=f"@test{i}.com",
            )

            condition = Condition.create(
                workflow_id=workflow_id,
                node_id=uuid4(),
                condition_type="contact_field_equals",
                branch_type=BranchType.IF_ELSE,
                configuration=config,
                position_x=100 * i,
                position_y=200 * i,
                created_by=user_id,
            )

            await condition_repository.create(condition)

        # List conditions
        conditions = await condition_repository.list_by_workflow(
            workflow_id, account_id
        )

        # Verify
        assert len(conditions) == 3
        assert all(c.workflow_id == workflow_id for c in conditions)

    @pytest.mark.asyncio
    async def test_update_condition(
        self, condition_repository, workflow_id, account_id, user_id
    ) -> None:
        """Test updating a condition."""
        # Create condition
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_FIELD_EQUALS,
            field="email",
            operator="contains",
            value="@gmail.com",
        )

        condition = Condition.create(
            workflow_id=workflow_id,
            node_id=uuid4(),
            condition_type="contact_field_equals",
            branch_type=BranchType.IF_ELSE,
            configuration=config,
            position_x=200,
            position_y=300,
            created_by=user_id,
        )

        saved_condition = await condition_repository.create(condition)

        # Update configuration
        new_config = ConditionConfig(
            condition_type=ConditionType.CONTACT_FIELD_EQUALS,
            field="email",
            operator="contains",
            value="@yahoo.com",
        )

        saved_condition.update_configuration(new_config)
        saved_condition.position_x = 500

        # Save update
        updated_condition = await condition_repository.update(saved_condition)

        # Verify
        assert updated_condition is not None
        assert updated_condition.configuration.value == "@yahoo.com"
        assert updated_condition.position_x == 500

    @pytest.mark.asyncio
    async def test_delete_condition(
        self, condition_repository, workflow_id, account_id, user_id
    ) -> None:
        """Test deleting a condition."""
        # Create condition
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_FIELD_EQUALS,
            field="email",
            operator="contains",
            value="@gmail.com",
        )

        condition = Condition.create(
            workflow_id=workflow_id,
            node_id=uuid4(),
            condition_type="contact_field_equals",
            branch_type=BranchType.IF_ELSE,
            configuration=config,
            position_x=200,
            position_y=300,
            created_by=user_id,
        )

        saved_condition = await condition_repository.create(condition)

        # Delete condition
        result = await condition_repository.delete(
            saved_condition.id, account_id, user_id
        )

        # Verify deletion
        assert result is True

        # Verify condition no longer exists
        retrieved_condition = await condition_repository.get_by_id(
            saved_condition.id, account_id
        )
        assert retrieved_condition is None

    @pytest.mark.asyncio
    async def test_count_by_workflow(
        self, condition_repository, workflow_id, account_id, user_id
    ) -> None:
        """Test counting conditions by workflow."""
        # Initially should be 0
        count = await condition_repository.count_by_workflow(workflow_id, account_id)
        assert count == 0

        # Create 3 conditions
        for _ in range(3):
            config = ConditionConfig(
                condition_type=ConditionType.CONTACT_HAS_TAG,
                tags=["lead"],
            )

            condition = Condition.create(
                workflow_id=workflow_id,
                node_id=uuid4(),
                condition_type="contact_has_tag",
                branch_type=BranchType.MULTI_BRANCH,
                configuration=config,
                position_x=100,
                position_y=200,
                created_by=user_id,
            )

            await condition_repository.create(condition)

        # Count should be 3
        count = await condition_repository.count_by_workflow(workflow_id, account_id)
        assert count == 3
