"""
Database migration: Create workflow analytics tables.

Alembic migration for creating analytics schema.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    """Create analytics tables."""
    # Create workflow_analytics table
    op.create_table(
        "workflow_analytics",
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
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("total_enrolled", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("new_enrollments", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("currently_active", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completion_rate", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("average_duration_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("goals_achieved", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("conversion_rate", sa.Numeric(5, 2), nullable=False, server_default="0"),
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
    )

    # Create indexes for workflow_analytics
    op.create_index(
        "ix_workflow_analytics_workflow_date",
        "workflow_analytics",
        ["workflow_id", "date"],
    )
    op.create_index("ix_workflow_analytics_date", "workflow_analytics", ["date"])

    # Create workflow_step_metrics table
    op.create_table(
        "workflow_step_metrics",
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
        sa.Column("step_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("entered", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("dropped_off", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "step_conversion_rate",
            sa.Numeric(5, 2),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "average_time_in_step_seconds",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("executions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("successes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failures", sa.Integer(), nullable=False, server_default="0"),
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
    )

    # Create indexes for workflow_step_metrics
    op.create_index(
        "ix_workflow_step_metrics_workflow_date",
        "workflow_step_metrics",
        ["workflow_id", "date"],
    )
    op.create_index("ix_workflow_step_metrics_step_date", "workflow_step_metrics", ["step_id", "date"])

    # Create workflow_executions table
    op.create_table(
        "workflow_executions",
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
        sa.Column(
            "contact_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("contacts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "active",
                "completed",
                "goal_achieved",
                "exited",
                "error",
                name="execution_status",
            ),
            nullable=False,
            server_default="active",
        ),
        sa.Column("current_step_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "enrolled_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("goal_achieved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "enrollment_source",
            sa.Enum("trigger", "bulk", "api", "manual", name="enrollment_source"),
            nullable=False,
            server_default="manual",
        ),
        sa.Column("exit_reason", sa.String(255), nullable=True),
        sa.Column("steps_entered", postgresql.JSON(), nullable=False, server_default="[]"),
        sa.Column("steps_completed", postgresql.JSON(), nullable=False, server_default="[]"),
        sa.Column("step_times", postgresql.JSON(), nullable=False, server_default="{}"),
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
    )

    # Create indexes for workflow_executions
    op.create_index(
        "ix_workflow_executions_workflow_enrolled",
        "workflow_executions",
        ["workflow_id", "enrolled_at"],
    )
    op.create_index(
        "ix_workflow_executions_contact_workflow",
        "workflow_executions",
        ["contact_id", "workflow_id"],
    )
    op.create_index("ix_workflow_executions_status", "workflow_executions", ["status"])


def downgrade():
    """Drop analytics tables."""
    op.drop_table("workflow_executions")
    op.drop_table("workflow_step_metrics")
    op.drop_table("workflow_analytics")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS execution_status")
    op.execute("DROP TYPE IF EXISTS enrollment_source")
