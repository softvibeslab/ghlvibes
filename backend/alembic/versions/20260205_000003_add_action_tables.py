"""Add action tables

Revision ID: 20260205_000003
Revises: 20260126_000002
Create Date: 2026-02-05

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "20260205_000003"
down_revision: str | None = "20260126_000002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create workflow_actions and workflow_action_executions tables."""

    # Create workflow_actions table
    op.create_table(
        "workflow_actions",
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
        ),
        sa.Column("action_type", sa.String(50), nullable=False, comment="Action type"),
        sa.Column(
            "action_config",
            postgresql.JSONB,
            nullable=False,
            server_default="{}",
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column(
            "previous_action_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("workflow_actions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "next_action_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("workflow_actions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "branch_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
            comment="Branch ID if in conditional branch",
        ),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default="true"),
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
        sa.Column(
            "updated_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.CheckConstraint(
            "action_type IN ("
            "'send_email', 'send_sms', 'send_voicemail', 'send_messenger', 'make_call',"
            "'create_contact', 'update_contact', 'add_tag', 'remove_tag',"
            "'add_to_campaign', 'remove_from_campaign', 'move_pipeline_stage',"
            "'assign_to_user', 'create_task', 'add_note',"
            "'wait_time', 'wait_until_date', 'wait_for_event',"
            "'send_notification', 'create_opportunity', 'webhook_call', 'custom_code',"
            "'grant_course_access', 'revoke_course_access'"
            ")",
            name="ck_action_type",
        ),
        sa.CheckConstraint("position >= 0", name="ck_action_position"),
    )

    # Create indexes for workflow_actions
    op.create_index("ix_action_workflow_id", "workflow_actions", ["workflow_id"])
    op.create_index("ix_action_workflow_position", "workflow_actions", ["workflow_id", "position"])
    op.create_index("ix_action_type", "workflow_actions", ["action_type"])
    op.create_index("ix_action_enabled", "workflow_actions", ["workflow_id", "is_enabled"])
    op.create_index("ix_action_previous", "workflow_actions", ["previous_action_id"])
    op.create_index("ix_action_next", "workflow_actions", ["next_action_id"])

    # Create workflow_action_executions table
    op.create_table(
        "workflow_action_executions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "workflow_execution_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("workflow_executions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "action_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("workflow_actions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "contact_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("contacts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "execution_data",
            postgresql.JSONB,
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "result_data",
            postgresql.JSONB,
            nullable=False,
            server_default="{}",
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.CheckConstraint(
            "status IN ('pending', 'scheduled', 'running', 'completed', 'failed', 'skipped', 'waiting')",
            name="ck_execution_status",
        ),
        sa.CheckConstraint("retry_count >= 0", name="ck_execution_retry_count"),
    )

    # Create indexes for workflow_action_executions
    op.create_index(
        "ix_action_executions_workflow", "workflow_action_executions", ["workflow_execution_id"]
    )
    op.create_index("ix_action_executions_contact", "workflow_action_executions", ["contact_id"])
    op.create_index("ix_action_executions_status", "workflow_action_executions", ["status"])
    op.create_index(
        "ix_action_executions_action_status",
        "workflow_action_executions",
        ["action_id", "status"],
    )
    op.create_index(
        "ix_action_executions_scheduled",
        "workflow_action_executions",
        ["scheduled_at"],
        postgresql_where=sa.text("status = 'scheduled'"),
    )


def downgrade() -> None:
    """Drop workflow_actions and workflow_action_executions tables."""

    # Drop workflow_action_executions table
    op.drop_index("ix_action_executions_scheduled", table_name="workflow_action_executions")
    op.drop_index("ix_action_executions_action_status", table_name="workflow_action_executions")
    op.drop_index("ix_action_executions_status", table_name="workflow_action_executions")
    op.drop_index("ix_action_executions_contact", table_name="workflow_action_executions")
    op.drop_index("ix_action_executions_workflow", table_name="workflow_action_executions")
    op.drop_table("workflow_action_executions")

    # Drop workflow_actions table
    op.drop_index("ix_action_next", table_name="workflow_actions")
    op.drop_index("ix_action_previous", table_name="workflow_actions")
    op.drop_index("ix_action_enabled", table_name="workflow_actions")
    op.drop_index("ix_action_type", table_name="workflow_actions")
    op.drop_index("ix_action_workflow_position", table_name="workflow_actions")
    op.drop_index("ix_action_workflow_id", table_name="workflow_actions")
    op.drop_table("workflow_actions")
