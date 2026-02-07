"""Add workflow triggers and execution logs tables.

Revision ID: 20260126_000002
Revises: 20260126_000001
Create Date: 2026-01-26

This migration adds the workflow_triggers and trigger_execution_logs tables
as specified in SPEC-WFL-002.

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "20260126_000002"
down_revision: Union[str, None] = "20260126_000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create workflow_triggers and trigger_execution_logs tables."""

    # Create workflow_triggers table
    op.create_table(
        "workflow_triggers",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "workflow_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("workflows.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("event", sa.String(50), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column(
            "filters",
            postgresql.JSONB,
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "settings",
            postgresql.JSONB,
            nullable=False,
            server_default="{}",
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    # Create indexes for workflow_triggers
    op.create_index(
        "ix_trigger_workflow_id",
        "workflow_triggers",
        ["workflow_id"],
    )
    op.create_index(
        "ix_trigger_event",
        "workflow_triggers",
        ["event"],
    )
    op.create_index(
        "ix_trigger_category",
        "workflow_triggers",
        ["category"],
    )
    op.create_index(
        "ix_trigger_is_active",
        "workflow_triggers",
        ["is_active"],
    )
    op.create_index(
        "ix_trigger_active_event",
        "workflow_triggers",
        ["category", "event"],
        postgresql_where=sa.text("is_active = TRUE"),
    )
    op.create_index(
        "ix_trigger_workflow_active",
        "workflow_triggers",
        ["workflow_id", "is_active"],
    )

    # Create trigger_execution_logs table
    op.create_table(
        "trigger_execution_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "trigger_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("workflow_triggers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "contact_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "event_data",
            postgresql.JSONB,
            nullable=False,
        ),
        sa.Column("matched", sa.Boolean(), nullable=False),
        sa.Column("enrolled", sa.Boolean(), nullable=False),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column(
            "executed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )

    # Create indexes for trigger_execution_logs
    op.create_index(
        "ix_trigger_log_trigger_id",
        "trigger_execution_logs",
        ["trigger_id"],
    )
    op.create_index(
        "ix_trigger_log_contact_id",
        "trigger_execution_logs",
        ["contact_id"],
    )
    op.create_index(
        "ix_trigger_log_executed_at",
        "trigger_execution_logs",
        ["executed_at"],
    )
    op.create_index(
        "ix_trigger_log_matched",
        "trigger_execution_logs",
        ["matched"],
    )
    op.create_index(
        "ix_trigger_log_enrolled",
        "trigger_execution_logs",
        ["enrolled"],
    )
    op.create_index(
        "ix_trigger_log_trigger_executed_at",
        "trigger_execution_logs",
        ["trigger_id", "executed_at"],
    )
    op.create_index(
        "ix_trigger_log_enrolled_success",
        "trigger_execution_logs",
        ["trigger_id", "enrolled"],
        postgresql_where=sa.text("enrolled = TRUE"),
    )
    op.create_index(
        "ix_trigger_log_failed_match",
        "trigger_execution_logs",
        ["trigger_id", "matched"],
        postgresql_where=sa.text("matched = FALSE"),
    )
    op.create_index(
        "ix_trigger_log_contact_executed",
        "trigger_execution_logs",
        ["contact_id", "executed_at"],
    )


def downgrade() -> None:
    """Drop workflow_triggers and trigger_execution_logs tables."""

    # Drop indexes first
    op.drop_index("ix_trigger_log_contact_executed", table_name="trigger_execution_logs")
    op.drop_index("ix_trigger_log_failed_match", table_name="trigger_execution_logs")
    op.drop_index("ix_trigger_log_enrolled_success", table_name="trigger_execution_logs")
    op.drop_index("ix_trigger_log_trigger_executed_at", table_name="trigger_execution_logs")
    op.drop_index("ix_trigger_log_enrolled", table_name="trigger_execution_logs")
    op.drop_index("ix_trigger_log_matched", table_name="trigger_execution_logs")
    op.drop_index("ix_trigger_log_executed_at", table_name="trigger_execution_logs")
    op.drop_index("ix_trigger_log_contact_id", table_name="trigger_execution_logs")
    op.drop_index("ix_trigger_log_trigger_id", table_name="trigger_execution_logs")

    # Drop trigger_execution_logs table
    op.drop_table("trigger_execution_logs")

    # Drop indexes
    op.drop_index("ix_trigger_workflow_active", table_name="workflow_triggers")
    op.drop_index("ix_trigger_active_event", table_name="workflow_triggers")
    op.drop_index("ix_trigger_is_active", table_name="workflow_triggers")
    op.drop_index("ix_trigger_category", table_name="workflow_triggers")
    op.drop_index("ix_trigger_event", table_name="workflow_triggers")
    op.drop_index("ix_trigger_workflow_id", table_name="workflow_triggers")

    # Drop workflow_triggers table
    op.drop_table("workflow_triggers")
