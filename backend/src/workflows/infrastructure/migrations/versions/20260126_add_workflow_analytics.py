"""Add workflow analytics tables.

Revision ID: 20260126_add_workflow_analytics
Create Date: 2026-01-26

This migration creates tables for workflow analytics including:
- workflow_analytics: Daily aggregated metrics
- workflow_step_metrics: Step-level funnel metrics
- workflow_executions: Individual execution tracking
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import (
    JSON,
    Column,
    Computed,
    Date,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID

from src.workflows.infrastructure.analytics_models import (
    WorkflowAnalyticsModel,
    WorkflowExecutionModel,
    WorkflowStepMetricsModel,
)

# revision identifiers, used by Alembic.
revision: str = "20260126_add_workflow_analytics"
down_revision: Union[str, None] = "20260125_add_workflow_executions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create workflow analytics tables."""

    # Create workflow_analytics table
    op.create_table(
        "workflow_analytics",
        Column("id", UUID, primary_key=True),
        Column("workflow_id", UUID, nullable=False, index=True, comment="Reference to workflow"),
        Column("account_id", UUID, nullable=False, index=True, comment="Account/tenant identifier"),
        Column("date", Date, nullable=False, index=True, comment="Aggregation date"),
        Column("total_enrolled", Integer, nullable=False, default=0, comment="Total enrollments at snapshot time"),
        Column("new_enrollments", Integer, nullable=False, default=0, comment="New enrollments on this date"),
        Column("currently_active", Integer, nullable=False, default=0, comment="Contacts currently in workflow"),
        Column("enrollment_sources", JSON, nullable=False, default=dict, comment="Breakdown of enrollments by source"),
        Column("completed", Integer, nullable=False, default=0, comment="Total completions at snapshot time"),
        Column("completion_rate", Numeric(5, 2), nullable=False, default=0, comment="Completion percentage"),
        Column("average_duration_seconds", Integer, nullable=True, comment="Average time from enrollment to completion"),
        Column("exit_reasons", JSON, nullable=False, default=dict, comment="Distribution of exit reasons"),
        Column("goals_achieved", Integer, nullable=False, default=0, comment="Total goal achievements at snapshot time"),
        Column("conversion_rate", Numeric(5, 2), nullable=False, default=0, comment="Conversion percentage"),
        Column("created_at", DateTime(timezone=True), nullable=False, comment="Record creation time"),
        Column("updated_at", DateTime(timezone=True), nullable=False, comment="Last update time"),
        comment="Daily aggregated workflow analytics",
    )

    # Create unique constraint on workflow_id and date
    op.create_unique_constraint(
        "uq_workflow_analytics_workflow_date",
        "workflow_analytics",
        ["workflow_id", "date"],
    )

    # Create composite index for workflow_id and date
    op.create_index(
        "ix_workflow_analytics_workflow_date",
        "workflow_analytics",
        ["workflow_id", "date"],
    )

    # Create workflow_step_metrics table
    op.create_table(
        "workflow_step_metrics",
        Column("id", UUID, primary_key=True),
        Column("workflow_id", UUID, nullable=False, index=True, comment="Reference to workflow"),
        Column("step_id", UUID, nullable=False, index=True, comment="Reference to workflow step"),
        Column("step_name", String(255), nullable=False, comment="Human-readable step name"),
        Column("step_order", Integer, nullable=False, comment="Position in workflow sequence"),
        Column("date", Date, nullable=False, index=True, comment="Aggregation date"),
        Column("entered", Integer, nullable=False, default=0, comment="Contacts who entered this step"),
        Column("completed", Integer, nullable=False, default=0, comment="Contacts who completed this step"),
        Column("dropped_off", Integer, nullable=False, default=0, comment="Contacts who exited at this step"),
        Column("step_conversion_rate", Numeric(5, 2), nullable=False, default=0, comment="Step conversion percentage"),
        Column("average_time_in_step_seconds", Integer, nullable=True, comment="Average time spent in step"),
        Column("executions", Integer, nullable=False, default=0, comment="Number of action executions"),
        Column("successes", Integer, nullable=False, default=0, comment="Successful executions"),
        Column("failures", Integer, nullable=False, default=0, comment="Failed executions"),
        Column("created_at", DateTime(timezone=True), nullable=False, comment="Record creation time"),
        Column("updated_at", DateTime(timezone=True), nullable=False, comment="Last update time"),
        comment="Workflow step performance metrics",
    )

    # Create unique constraint on workflow_id, step_id, and date
    op.create_unique_constraint(
        "uq_workflow_step_metrics_workflow_step_date",
        "workflow_step_metrics",
        ["workflow_id", "step_id", "date"],
    )

    # Create composite index for workflow_id and date
    op.create_index(
        "ix_workflow_step_metrics_workflow_date",
        "workflow_step_metrics",
        ["workflow_id", "date"],
    )

    # Create composite index for workflow_id and step_order
    op.create_index(
        "ix_workflow_step_metrics_workflow_order",
        "workflow_step_metrics",
        ["workflow_id", "step_order"],
    )

    # Create workflow_executions table
    op.create_table(
        "workflow_executions",
        Column("id", UUID, primary_key=True),
        Column("workflow_id", UUID, nullable=False, index=True, comment="Reference to workflow"),
        Column("contact_id", UUID, nullable=False, index=True, comment="Contact identifier"),
        Column("account_id", UUID, nullable=False, index=True, comment="Account/tenant identifier"),
        Column("status", String(50), nullable=False, index=True, comment="Execution status"),
        Column("current_step_id", UUID, nullable=True, comment="Current step in workflow"),
        Column("enrolled_at", DateTime(timezone=True), nullable=False, index=True, comment="When contact entered workflow"),
        Column("completed_at", DateTime(timezone=True), nullable=True, comment="When workflow was completed"),
        Column("goal_achieved_at", DateTime(timezone=True), nullable=True, comment="When goal was achieved"),
        Column("enrollment_source", String(50), nullable=False, comment="How contact entered workflow"),
        Column("exit_reason", Text, nullable=True, comment="Reason for workflow exit"),
        Column("metadata", JSON, nullable=True, comment="Additional execution metadata"),
        Column("created_at", DateTime(timezone=True), nullable=False, comment="Record creation time"),
        Column("updated_at", DateTime(timezone=True), nullable=False, comment="Last update time"),
        comment="Individual workflow execution tracking",
    )

    # Create composite index for workflow_id and enrolled_at
    op.create_index(
        "ix_workflow_executions_workflow_enrolled",
        "workflow_executions",
        ["workflow_id", "enrolled_at"],
    )

    # Create composite index for workflow_id and status
    op.create_index(
        "ix_workflow_executions_workflow_status",
        "workflow_executions",
        ["workflow_id", "status"],
    )

    # Create composite index for contact_id and workflow_id
    op.create_index(
        "ix_workflow_executions_contact_workflow",
        "workflow_executions",
        ["contact_id", "workflow_id"],
    )


def downgrade() -> None:
    """Drop workflow analytics tables."""

    # Drop tables in reverse order of creation
    op.drop_table("workflow_executions")
    op.drop_table("workflow_step_metrics")
    op.drop_table("workflow_analytics")
