"""SQLAlchemy models for workflow conditions.

These models define the database schema for condition configurations
and branch paths.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Index, Integer, String, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ConditionModel(Base):
    """SQLAlchemy model for condition configurations.

    Represents conditional branching logic in workflows.
    """

    __tablename__ = "workflow_conditions"

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

    # Node configuration
    node_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    condition_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    branch_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # Condition configuration (JSONB for flexible storage)
    configuration: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )

    # Canvas position
    position_x: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    position_y: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # State
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    # Audit fields
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
        Index("idx_conditions_workflow", "workflow_id"),
        Index("idx_conditions_account", "account_id"),
        Index("idx_conditions_node", "node_id"),
        Index("idx_conditions_workflow_active", "workflow_id", "is_active"),
    )

    def to_domain(self) -> Any:
        """Convert model to domain entity.

        Returns:
            Condition domain entity with branches loaded.
        """
        from src.workflows.domain.condition_entities import (  # noqa: PLC0415
            Branch,
            Condition,
        )
        from src.workflows.domain.condition_value_objects import (  # noqa: PLC0415
            BranchType,
            ConditionConfig,
        )

        # Load branches from relationship
        branch_models = getattr(self, "branches", [])
        branches = [
            Branch(
                id=b.id,
                condition_id=b.condition_id,
                branch_name=b.branch_name,
                branch_order=b.branch_order,
                is_default=b.is_default,
                percentage=b.percentage,
                next_node_id=b.next_node_id,
                criteria=None,  # Will be set in __post_init__
            )
            for b in branch_models
        ]

        # Set criteria for each branch
        for b, b_model in zip(branches, branch_models):
            if b_model.criteria:
                from src.workflows.domain.condition_value_objects import (  # noqa: PLC0415
                    BranchCriteria,
                )

                b.criteria = BranchCriteria.from_dict(b_model.criteria)

        return Condition(
            id=self.id,
            workflow_id=self.workflow_id,
            node_id=self.node_id,
            condition_type=self.condition_type,
            branch_type=BranchType(self.branch_type),
            configuration=ConditionConfig.from_dict(self.configuration),
            position_x=self.position_x,
            position_y=self.position_y,
            branches=branches,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
            created_by=self.created_by,
            updated_by=self.updated_by,
        )

    @classmethod
    def from_domain(cls, condition: Any) -> "ConditionModel":
        """Create model from domain entity.

        Args:
            condition: Condition domain entity.

        Returns:
            ConditionModel instance.
        """
        return cls(
            id=condition.id,
            workflow_id=condition.workflow_id,
            account_id=UUID("00000000-0000-0000-0000-000000000000"),  # Placeholder
            node_id=condition.node_id,
            condition_type=condition.condition_type,
            branch_type=condition.branch_type.value,
            configuration=condition.configuration.to_dict(),
            position_x=condition.position_x,
            position_y=condition.position_y,
            is_active=condition.is_active,
            created_at=condition.created_at,
            updated_at=condition.updated_at,
            created_by=condition.created_by,
            updated_by=condition.updated_by,
        )


class BranchModel(Base):
    """SQLAlchemy model for condition branches.

    Represents individual branch paths in conditional logic.
    """

    __tablename__ = "workflow_branches"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign key
    condition_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Branch configuration
    branch_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    branch_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    is_default: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    # Split test distribution
    percentage: Mapped[float | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    # Next node in path
    next_node_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )

    # Branch-specific criteria (JSONB)
    criteria: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    # Indexes
    __table_args__ = (
        Index("idx_branches_condition", "condition_id"),
        Index("idx_branches_order", "condition_id", "branch_order"),
    )


class ConditionLogModel(Base):
    """SQLAlchemy model for condition evaluation logs.

    Records all condition evaluations for audit trails and debugging.
    """

    __tablename__ = "workflow_condition_logs"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys
    execution_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    condition_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    contact_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Evaluation data
    evaluation_inputs: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )
    evaluation_result: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    duration_ms: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Indexes
    __table_args__ = (
        Index("idx_condition_logs_execution", "execution_id"),
        Index("idx_condition_logs_contact", "contact_id"),
        Index("idx_condition_logs_date", "evaluated_at"),
        Index("idx_condition_logs_workflow_contact", "condition_id", "contact_id"),
    )
