"""Integration tests for goal tracking repositories.

These tests use a test database to verify repository implementations.
"""

import pytest
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.database import Base
from src.workflows.domain.goal_entities import GoalAchievement, GoalConfig, GoalType
from src.workflows.infrastructure.goal_models import GoalAchievementModel, GoalModel
from src.workflows.infrastructure.goal_repository import (
    PostgresGoalAchievementRepository,
    PostgresGoalRepository,
)


@pytest.fixture
async def test_engine():
    """Create a test database engine."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(test_engine):
    """Create a test database session."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session


@pytest.fixture
def goal_repository(db_session):
    """Create a goal repository with test session."""
    return PostgresGoalRepository(session=db_session)


@pytest.fixture
def achievement_repository(db_session):
    """Create an achievement repository with test session."""
    return PostgresGoalAchievementRepository(session=db_session)


class TestPostgresGoalRepository:
    """Integration tests for PostgresGoalRepository."""

    @pytest.mark.asyncio
    async def test_create_goal(self, goal_repository):
        """Test creating a goal configuration."""
        # Arrange
        workflow_id = uuid4()
        account_id = uuid4()
        created_by = uuid4()

        goal = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=GoalType.TAG_ADDED,
            criteria={"tag_id": str(uuid4())},
            created_by=created_by,
        )

        # Act
        result = await goal_repository.create(goal)

        # Assert
        assert result.id is not None
        assert result.workflow_id == workflow_id
        assert result.goal_type == GoalType.TAG_ADDED

    @pytest.mark.asyncio
    async def test_get_by_id(self, goal_repository):
        """Test retrieving a goal by ID."""
        # Arrange
        workflow_id = uuid4()
        account_id = uuid4()
        created_by = uuid4()

        goal = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=GoalType.PURCHASE_MADE,
            criteria={"any_purchase": True},
            created_by=created_by,
        )
        created_goal = await goal_repository.create(goal)

        # Act
        result = await goal_repository.get_by_id(created_goal.id, account_id)

        # Assert
        assert result is not None
        assert result.id == created_goal.id
        assert result.goal_type == GoalType.PURCHASE_MADE

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, goal_repository):
        """Test retrieving a non-existent goal."""
        # Act
        result = await goal_repository.get_by_id(uuid4(), uuid4())

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_list_by_workflow(self, goal_repository):
        """Test listing goals by workflow."""
        # Arrange
        workflow_id = uuid4()
        account_id = uuid4()
        created_by = uuid4()

        goal1 = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=GoalType.TAG_ADDED,
            criteria={"tag_id": str(uuid4())},
            created_by=created_by,
        )
        goal2 = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=GoalType.PURCHASE_MADE,
            criteria={"min_amount": 100.0},
            created_by=created_by,
        )

        await goal_repository.create(goal1)
        await goal_repository.create(goal2)

        # Act
        results = await goal_repository.list_by_workflow(
            workflow_id=workflow_id,
            account_id=account_id,
            offset=0,
            limit=10,
        )

        # Assert
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_update_goal(self, goal_repository):
        """Test updating a goal configuration."""
        # Arrange
        workflow_id = uuid4()
        account_id = uuid4()
        created_by = uuid4()

        goal = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=GoalType.APPOINTMENT_BOOKED,
            criteria={"calendar_id": str(uuid4())},
            created_by=created_by,
        )
        created_goal = await goal_repository.create(goal)

        # Act
        updated_by = uuid4()
        created_goal.update(
            updated_by=updated_by,
            criteria={"service_id": str(uuid4())},
        )
        result = await goal_repository.update(created_goal)

        # Assert
        assert result.version == 2
        assert result.updated_by == updated_by

    @pytest.mark.asyncio
    async def test_delete_goal(self, goal_repository):
        """Test deleting a goal configuration."""
        # Arrange
        workflow_id = uuid4()
        account_id = uuid4()
        created_by = uuid4()

        goal = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=GoalType.FORM_SUBMITTED,
            criteria={"form_id": str(uuid4())},
            created_by=created_by,
        )
        created_goal = await goal_repository.create(goal)

        # Act
        result = await goal_repository.delete(created_goal.id, account_id, created_by)

        # Assert
        assert result is True

        # Verify deleted
        deleted_goal = await goal_repository.get_by_id(created_goal.id, account_id)
        assert deleted_goal is None

    @pytest.mark.asyncio
    async def test_count_by_workflow(self, goal_repository):
        """Test counting goals by workflow."""
        # Arrange
        workflow_id = uuid4()
        account_id = uuid4()
        created_by = uuid4()

        goal1 = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=GoalType.TAG_ADDED,
            criteria={"tag_id": str(uuid4())},
            created_by=created_by,
        )
        goal2 = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=GoalType.PURCHASE_MADE,
            criteria={"any_purchase": True},
            created_by=created_by,
        )

        await goal_repository.create(goal1)
        await goal_repository.create(goal2)

        # Act
        count = await goal_repository.count_by_workflow(workflow_id, account_id)

        # Assert
        assert count == 2


class TestPostgresGoalAchievementRepository:
    """Integration tests for PostgresGoalAchievementRepository."""

    @pytest.mark.asyncio
    async def test_create_achievement(self, achievement_repository):
        """Test creating a goal achievement."""
        # Arrange
        workflow_id = uuid4()
        enrollment_id = uuid4()
        contact_id = uuid4()
        goal_config_id = uuid4()
        account_id = uuid4()

        achievement = GoalAchievement.create(
            workflow_id=workflow_id,
            workflow_enrollment_id=enrollment_id,
            contact_id=contact_id,
            goal_config_id=goal_config_id,
            account_id=account_id,
            goal_type=GoalType.TAG_ADDED,
            trigger_event={"tag_id": str(uuid4())},
        )

        # Act
        result = await achievement_repository.create(achievement)

        # Assert
        assert result.id is not None
        assert result.contact_id == contact_id
        assert result.goal_type == GoalType.TAG_ADDED

    @pytest.mark.asyncio
    async def test_get_by_contact_and_workflow(self, achievement_repository):
        """Test retrieving achievements by contact and workflow."""
        # Arrange
        workflow_id = uuid4()
        contact_id = uuid4()
        account_id = uuid4()
        goal_config_id = uuid4()

        achievement1 = GoalAchievement.create(
            workflow_id=workflow_id,
            workflow_enrollment_id=uuid4(),
            contact_id=contact_id,
            goal_config_id=goal_config_id,
            account_id=account_id,
            goal_type=GoalType.TAG_ADDED,
            trigger_event={"tag_id": str(uuid4())},
        )
        await achievement_repository.create(achievement1)

        # Act
        results = await achievement_repository.get_by_contact_and_workflow(
            contact_id=contact_id,
            workflow_id=workflow_id,
            account_id=account_id,
        )

        # Assert
        assert len(results) == 1
        assert results[0].contact_id == contact_id

    @pytest.mark.asyncio
    async def test_check_already_achieved(self, achievement_repository):
        """Test checking if goal was already achieved."""
        # Arrange
        contact_id = uuid4()
        goal_config_id = uuid4()
        account_id = uuid4()

        achievement = GoalAchievement.create(
            workflow_id=uuid4(),
            workflow_enrollment_id=uuid4(),
            contact_id=contact_id,
            goal_config_id=goal_config_id,
            account_id=account_id,
            goal_type=GoalType.PURCHASE_MADE,
            trigger_event={"amount": 100.0},
        )
        await achievement_repository.create(achievement)

        # Act
        result = await achievement_repository.check_already_achieved(
            contact_id=contact_id,
            goal_config_id=goal_config_id,
            account_id=account_id,
        )

        # Assert
        assert result is True

        # Test not achieved
        result2 = await achievement_repository.check_already_achieved(
            contact_id=uuid4(),  # Different contact
            goal_config_id=goal_config_id,
            account_id=account_id,
        )
        assert result2 is False
