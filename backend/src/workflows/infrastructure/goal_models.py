"""SQLAlchemy models for goal tracking.

These models define the database schema for goal configurations
and achievement tracking.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class GoalModel(Base):
    """SQLAlchemy model for goal configurations.

    Represents goal configurations that track contact behavior
    for workflow automation.
    """

    __tablename__ = "workflow_goals"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys
    workflow_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Goal configuration
    goal_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    criteria: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )

    # State
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    # Audit fields
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    created_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )
    updated_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )

    # Indexes
    __table_args__ = (
        Index("idx_goals_workflow_active", "workflow_id", "is_active"),
        Index("idx_goals_account_type", "account_id", "goal_type"),
    )

    def to_domain(self) -> Any:
        """Convert model to domain entity.
        Returns:
            GoalConfig domain entity.
        """
        from src.workflows.domain.goal_entities import (  # noqa: PLC0415
            GoalConfig,
            GoalCriteria,
            GoalType,
        )

        return GoalConfig(
            id=self.id,
            workflow_id=self.workflow_id,
            account_id=self.account_id,
            goal_type=GoalType(self.goal_type),
            criteria=GoalCriteria(
                goal_type=GoalType(self.goal_type),
                criteria=self.criteria,
            ),
            is_active=self.is_active,
            version=self.version,
            created_at=self.created_at,
            updated_at=self.updated_at,
            created_by=self.created_by,
            updated_by=self.updated_by,
        )

    @classmethod
    def from_domain(cls, goal_config: Any) -> "GoalModel":
        """Create model from domain entity.
        Args:
            goal_config: GoalConfig domain entity.
        Returns:
            GoalModel instance.
        """
        return cls(
            id=goal_config.id,
            workflow_id=goal_config.workflow_id,
            account_id=goal_config.account_id,
            goal_type=goal_config.goal_type.value,
            criteria=goal_config.criteria.criteria,
            is_active=goal_config.is_active,
            version=goal_config.version,
            created_at=goal_config.created_at,
            updated_at=goal_config.updated_at,
            created_by=goal_config.created_by,
            updated_by=goal_config.updated_by,
        )


class GoalAchievementModel(Base):
    """SQLAlchemy model for goal achievement records.

    Records when contacts achieve configured goals, including
    event data that triggered the achievement.
    """

    __tablename__ = "workflow_goal_achievements"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys
    workflow_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    workflow_enrollment_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )
    contact_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    goal_config_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Achievement details
    goal_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    achieved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    trigger_event: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )
    additional_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",  # Keep "metadata" as column name in DB
        JSONB,
        default=dict,
        nullable=False,
    )

    # Indexes
    __table_args__ = (
        Index("idx_achievements_workflow", "workflow_id"),
        Index("idx_achievements_contact", "contact_id"),
        Index("idx_achievements_date", "achieved_at"),
        Index("idx_achievements_workflow_contact", "workflow_id", "contact_id"),
    )

    def to_domain(self) -> Any:
        """Convert model to domain entity.
        Returns:
            GoalAchievement domain entity.
        """
        from src.workflows.domain.goal_entities import (  # noqa: PLC0415
            GoalAchievement,
            GoalType,
        )

        return GoalAchievement(
            id=self.id,
            workflow_id=self.workflow_id,
            workflow_enrollment_id=self.workflow_enrollment_id,
            contact_id=self.contact_id,
            goal_config_id=self.goal_config_id,
            account_id=self.account_id,
            goal_type=GoalType(self.goal_type),
            achieved_at=self.achieved_at,
            trigger_event=self.trigger_event,
            metadata=self.additional_metadata,
        )

    @classmethod
    def from_domain(cls, achievement: Any) -> "GoalAchievementModel":
        """Create model from domain entity.
        Args:
            achievement: GoalAchievement domain entity.
        Returns:
            GoalAchievementModel instance.
        """
        return cls(
            id=achievement.id,
            workflow_id=achievement.workflow_id,
            workflow_enrollment_id=achievement.workflow_enrollment_id,
            contact_id=achievement.contact_id,
            goal_config_id=achievement.goal_config_id,
            account_id=achievement.account_id,
            goal_type=achievement.goal_type.value,
            achieved_at=achievement.achieved_at,
            trigger_event=achievement.trigger_event,
            additional_metadata=achievement.metadata,
        )
