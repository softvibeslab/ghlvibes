"""Create goal tracking tables.

Revision ID: 2025_01_26_001
Create Date: 2025-01-26
Revises:
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic
revision: str = "2025_01_26_001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create goal tracking tables and indexes."""
    # Create workflow_goals table
    op.create_table(
        "workflow_goals",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "workflow_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "goal_type",
            sa.String(50),
            nullable=False,
        ),
        sa.Column(
            "criteria",
            postgresql.JSONB,
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            default=True,
            nullable=False,
        ),
        sa.Column(
            "version",
            sa.Integer(),
            default=1,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "updated_by",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["workflows.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            ondelete="CASCADE",
        ),
    )

    # Create indexes for workflow_goals
    op.create_index(
        "idx_goals_workflow_id",
        "workflow_goals",
        ["workflow_id"],
    )
    op.create_index(
        "idx_goals_account_id",
        "workflow_goals",
        ["account_id"],
    )
    op.create_index(
        "idx_goals_workflow_active",
        "workflow_goals",
        ["workflow_id", "is_active"],
    )
    op.create_index(
        "idx_goals_account_type",
        "workflow_goals",
        ["account_id", "goal_type"],
    )

    # Create workflow_goal_achievements table
    op.create_table(
        "workflow_goal_achievements",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "workflow_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "workflow_enrollment_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "contact_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "goal_config_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "goal_type",
            sa.String(50),
            nullable=False,
        ),
        sa.Column(
            "achieved_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "trigger_event",
            postgresql.JSONB,
            nullable=False,
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB,
            default=dict,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["workflows.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            ondelete="CASCADE",
        ),
    )

    # Create indexes for workflow_goal_achievements
    op.create_index(
        "idx_achievements_workflow_id",
        "workflow_goal_achievements",
        ["workflow_id"],
    )
    op.create_index(
        "idx_achievements_contact_id",
        "workflow_goal_achievements",
        ["contact_id"],
    )
    op.create_index(
        "idx_achievements_account_id",
        "workflow_goal_achievements",
        ["account_id"],
    )
    op.create_index(
        "idx_achievements_achieved_at",
        "workflow_goal_achievements",
        ["achieved_at"],
    )
    op.create_index(
        "idx_achievements_workflow_contact",
        "workflow_goal_achievements",
        ["workflow_id", "contact_id"],
    )


def downgrade() -> None:
    """Drop goal tracking tables and indexes."""
    # Drop workflow_goal_achievements table
    op.drop_index("idx_achievements_workflow_contact", table_name="workflow_goal_achievements")
    op.drop_index("idx_achievements_achieved_at", table_name="workflow_goal_achievements")
    op.drop_index("idx_achievements_account_id", table_name="workflow_goal_achievements")
    op.drop_index("idx_achievements_contact_id", table_name="workflow_goal_achievements")
    op.drop_index("idx_achievements_workflow_id", table_name="workflow_goal_achievements")
    op.drop_table("workflow_goal_achievements")

    # Drop workflow_goals table
    op.drop_index("idx_goals_account_type", table_name="workflow_goals")
    op.drop_index("idx_goals_workflow_active", table_name="workflow_goals")
    op.drop_index("idx_goals_account_id", table_name="workflow_goals")
    op.drop_index("idx_goals_workflow_id", table_name="workflow_goals")
    op.drop_table("workflow_goals")
