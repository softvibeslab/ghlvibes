"""Repository implementations for goal tracking."""

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.workflows.domain.goal_entities import GoalAchievement, GoalConfig
from src.workflows.infrastructure.goal_models import GoalAchievementModel, GoalModel


class IGoalRepository(ABC):
    """Abstract interface for goal configuration repository."""

    @abstractmethod
    async def create(self, goal: GoalConfig) -> GoalConfig:
        """Create a new goal configuration."""
        pass

    @abstractmethod
    async def get_by_id(self, goal_id: UUID, account_id: UUID) -> GoalConfig | None:
        """Get a goal configuration by ID."""
        pass

    @abstractmethod
    async def list_by_workflow(
        self,
        workflow_id: UUID,
        account_id: UUID,
        offset: int = 0,
        limit: int = 50,
    ) -> list[GoalConfig]:
        """List goal configurations for a workflow."""
        pass

    @abstractmethod
    async def update(self, goal: GoalConfig) -> GoalConfig:
        """Update an existing goal configuration."""
        pass

    @abstractmethod
    async def delete(self, goal_id: UUID, account_id: UUID, deleted_by: UUID) -> bool:
        """Delete a goal configuration."""
        pass

    @abstractmethod
    async def count_by_workflow(self, workflow_id: UUID, account_id: UUID) -> int:
        """Count goal configurations for a workflow."""
        pass

    @abstractmethod
    async def get_statistics(
        self, workflow_id: UUID, account_id: UUID
    ) -> dict[str, Any]:
        """Get goal achievement statistics."""
        pass


class IGoalAchievementRepository(ABC):
    """Abstract interface for goal achievement repository."""

    @abstractmethod
    async def create(self, achievement: GoalAchievement) -> GoalAchievement:
        """Create a new goal achievement record."""
        pass

    @abstractmethod
    async def get_by_contact_and_workflow(
        self, contact_id: UUID, workflow_id: UUID, account_id: UUID
    ) -> list[GoalAchievement]:
        """Get all achievements for a contact in a workflow."""
        pass

    @abstractmethod
    async def list_by_workflow(
        self,
        workflow_id: UUID,
        account_id: UUID,
        offset: int = 0,
        limit: int = 50,
    ) -> list[GoalAchievement]:
        """List goal achievements for a workflow."""
        pass

    @abstractmethod
    async def check_already_achieved(
        self, contact_id: UUID, goal_config_id: UUID, account_id: UUID
    ) -> bool:
        """Check if contact has already achieved a specific goal."""
        pass


class PostgresGoalRepository(IGoalRepository):
    """PostgreSQL implementation of goal repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.
        Args:
            session: Async database session.
        """
        self._session = session

    async def create(self, goal: GoalConfig) -> GoalConfig:
        """Create a new goal configuration.
        Args:
            goal: Goal configuration entity.
        Returns:
            Created goal with generated ID.
        """
        model = GoalModel.from_domain(goal)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model.to_domain()

    async def get_by_id(self, goal_id: UUID, account_id: UUID) -> GoalConfig | None:
        """Get a goal configuration by ID.
        Args:
            goal_id: Goal configuration ID.
            account_id: Account/tenant ID.
        Returns:
            Goal configuration if found, None otherwise.
        """
        result = await self._session.execute(
            select(GoalModel).where(
                and_(GoalModel.id == goal_id, GoalModel.account_id == account_id)
            )
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def list_by_workflow(
        self,
        workflow_id: UUID,
        account_id: UUID,
        offset: int = 0,
        limit: int = 50,
    ) -> list[GoalConfig]:
        """List goal configurations for a workflow.
        Args:
            workflow_id: Workflow ID.
            account_id: Account/tenant ID.
            offset: Pagination offset.
            limit: Maximum results.
        Returns:
            List of goal configurations.
        """
        result = await self._session.execute(
            select(GoalModel)
            .where(
                and_(
                    GoalModel.workflow_id == workflow_id,
                    GoalModel.account_id == account_id,
                )
            )
            .order_by(GoalModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        models = result.scalars().all()
        return [model.to_domain() for model in models]

    async def update(self, goal: GoalConfig) -> GoalConfig:
        """Update an existing goal configuration.
        Args:
            goal: Goal configuration with updated values.
        Returns:
            Updated goal configuration.
        """
        result = await self._session.execute(
            select(GoalModel).where(
                and_(GoalModel.id == goal.id, GoalModel.account_id == goal.account_id)
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None

        # Update fields
        model.criteria = goal.criteria.criteria
        model.is_active = goal.is_active
        model.version = goal.version
        model.updated_at = goal.updated_at
        model.updated_by = goal.updated_by

        await self._session.flush()
        await self._session.refresh(model)
        return model.to_domain()

    async def delete(self, goal_id: UUID, account_id: UUID, deleted_by: UUID) -> bool:
        """Delete a goal configuration.
        Args:
            goal_id: Goal configuration ID.
            account_id: Account/tenant ID.
            deleted_by: User performing deletion.
        Returns:
            True if deleted, False if not found.
        """
        result = await self._session.execute(
            select(GoalModel).where(
                and_(GoalModel.id == goal_id, GoalModel.account_id == account_id)
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            return False

        await self._session.delete(model)
        await self._session.flush()
        return True

    async def count_by_workflow(self, workflow_id: UUID, account_id: UUID) -> int:
        """Count goal configurations for a workflow.
        Args:
            workflow_id: Workflow ID.
            account_id: Account/tenant ID.
        Returns:
            Count of goal configurations.
        """
        result = await self._session.execute(
            select(func.count())
            .select_from(GoalModel)
            .where(
                and_(
                    GoalModel.workflow_id == workflow_id,
                    GoalModel.account_id == account_id,
                )
            )
        )
        return result.scalar() or 0

    async def get_statistics(
        self, workflow_id: UUID, account_id: UUID
    ) -> dict[str, Any]:
        """Get goal achievement statistics.
        Args:
            workflow_id: Workflow ID.
            account_id: Account/tenant ID.
        Returns:
            Statistics dictionary with metrics.
        """
        # Get total achievements
        achievements_result = await self._session.execute(
            select(func.count())
            .select_from(GoalAchievementModel)
            .where(
                and_(
                    GoalAchievementModel.workflow_id == workflow_id,
                    GoalAchievementModel.account_id == account_id,
                )
            )
        )
        goals_achieved = achievements_result.scalar() or 0

        # Get breakdown by goal type
        by_type_result = await self._session.execute(
            select(
                GoalAchievementModel.goal_type,
                func.count().label("count"),
            )
            .where(
                and_(
                    GoalAchievementModel.workflow_id == workflow_id,
                    GoalAchievementModel.account_id == account_id,
                )
            )
            .group_by(GoalAchievementModel.goal_type)
        )
        by_goal_type = {row.goal_type: {"achieved": row.count} for row in by_type_result}

        # Calculate average time to goal (in hours)
        avg_time_result = await self._session.execute(
            select(
                func.avg(
                    func.extract(
                        "epoch",
                        GoalAchievementModel.achieved_at,
                    )
                )
            ).where(
                and_(
                    GoalAchievementModel.workflow_id == workflow_id,
                    GoalAchievementModel.account_id == account_id,
                )
            )
        )
        avg_time_seconds = avg_time_result.scalar()
        avg_time_to_goal_hours = (
            float(avg_time_seconds / 3600) if avg_time_seconds else None
        )

        # TODO: Get total enrolled count from enrollment repository
        # For now, return 0
        total_enrolled = 0

        conversion_rate = (
            (goals_achieved / total_enrolled * 100) if total_enrolled > 0 else 0.0
        )

        return {
            "total_enrolled": total_enrolled,
            "goals_achieved": goals_achieved,
            "conversion_rate": conversion_rate,
            "avg_time_to_goal_hours": avg_time_to_goal_hours,
            "by_goal_type": by_goal_type,
        }


class PostgresGoalAchievementRepository(IGoalAchievementRepository):
    """PostgreSQL implementation of goal achievement repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.
        Args:
            session: Async database session.
        """
        self._session = session

    async def create(self, achievement: GoalAchievement) -> GoalAchievement:
        """Create a new goal achievement record.
        Args:
            achievement: Goal achievement entity.
        Returns:
            Created achievement record.
        """
        model = GoalAchievementModel.from_domain(achievement)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model.to_domain()

    async def get_by_contact_and_workflow(
        self, contact_id: UUID, workflow_id: UUID, account_id: UUID
    ) -> list[GoalAchievement]:
        """Get all achievements for a contact in a workflow.
        Args:
            contact_id: Contact ID.
            workflow_id: Workflow ID.
            account_id: Account/tenant ID.
        Returns:
            List of goal achievements.
        """
        result = await self._session.execute(
            select(GoalAchievementModel)
            .where(
                and_(
                    GoalAchievementModel.contact_id == contact_id,
                    GoalAchievementModel.workflow_id == workflow_id,
                    GoalAchievementModel.account_id == account_id,
                )
            )
            .order_by(GoalAchievementModel.achieved_at.desc())
        )
        models = result.scalars().all()
        return [model.to_domain() for model in models]

    async def list_by_workflow(
        self,
        workflow_id: UUID,
        account_id: UUID,
        offset: int = 0,
        limit: int = 50,
    ) -> list[GoalAchievement]:
        """List goal achievements for a workflow.
        Args:
            workflow_id: Workflow ID.
            account_id: Account/tenant ID.
            offset: Pagination offset.
            limit: Maximum results.
        Returns:
            List of goal achievements.
        """
        result = await self._session.execute(
            select(GoalAchievementModel)
            .where(
                and_(
                    GoalAchievementModel.workflow_id == workflow_id,
                    GoalAchievementModel.account_id == account_id,
                )
            )
            .order_by(GoalAchievementModel.achieved_at.desc())
            .offset(offset)
            .limit(limit)
        )
        models = result.scalars().all()
        return [model.to_domain() for model in models]

    async def check_already_achieved(
        self, contact_id: UUID, goal_config_id: UUID, account_id: UUID
    ) -> bool:
        """Check if contact has already achieved a specific goal.
        Args:
            contact_id: Contact ID.
            goal_config_id: Goal configuration ID.
            account_id: Account/tenant ID.
        Returns:
            True if already achieved, False otherwise.
        """
        result = await self._session.execute(
            select(func.count())
            .select_from(GoalAchievementModel)
            .where(
                and_(
                    GoalAchievementModel.contact_id == contact_id,
                    GoalAchievementModel.goal_config_id == goal_config_id,
                    GoalAchievementModel.account_id == account_id,
                )
            )
        )
        count = result.scalar() or 0
        return count > 0
