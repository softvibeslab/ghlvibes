"""Add workflow conditions and branches tables.

Revision ID: 20250207_add_conditions
Revises: 20250126_initial_workflow
Create Date: 2026-02-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "20250207_add_conditions"
down_revision: Union[str, None] = "20250126_initial_workflow"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create workflow_conditions, workflow_branches, and workflow_condition_logs tables."""
    # Create workflow_conditions table
    op.create_table(
        "workflow_conditions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("node_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("condition_type", sa.String(50), nullable=False),
        sa.Column("branch_type", sa.String(20), nullable=False),
        sa.Column("configuration", postgresql.JSONB, nullable=False),
        sa.Column("position_x", sa.Integer(), nullable=False),
        sa.Column("position_y", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), default=sa.text("NOW()"), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Create indexes for workflow_conditions
    op.create_index("idx_conditions_workflow", "workflow_conditions", ["workflow_id"])
    op.create_index("idx_conditions_account", "workflow_conditions", ["account_id"])
    op.create_index("idx_conditions_node", "workflow_conditions", ["node_id"])
    op.create_index("idx_conditions_workflow_active", "workflow_conditions", ["workflow_id", "is_active"])

    # Create workflow_branches table
    op.create_table(
        "workflow_branches",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("condition_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("branch_name", sa.String(100), nullable=False),
        sa.Column("branch_order", sa.Integer(), nullable=False),
        sa.Column("is_default", sa.Boolean(), default=False, nullable=False),
        sa.Column("percentage", postgresql.NUMERIC(5, 2), nullable=True),
        sa.Column("next_node_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("criteria", postgresql.JSONB, nullable=True),
    )

    # Create indexes for workflow_branches
    op.create_index("idx_branches_condition", "workflow_branches", ["condition_id"])
    op.create_index("idx_branches_order", "workflow_branches", ["condition_id", "branch_order"])

    # Create workflow_condition_logs table
    op.create_table(
        "workflow_condition_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("execution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("condition_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("evaluation_inputs", postgresql.JSONB, nullable=False),
        sa.Column("evaluation_result", sa.String(100), nullable=False),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), default=sa.text("NOW()"), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
    )

    # Create indexes for workflow_condition_logs
    op.create_index("idx_condition_logs_execution", "workflow_condition_logs", ["execution_id"])
    op.create_index("idx_condition_logs_contact", "workflow_condition_logs", ["contact_id"])
    op.create_index("idx_condition_logs_date", "workflow_condition_logs", ["evaluated_at"])
    op.create_index(
        "idx_condition_logs_workflow_contact", "workflow_condition_logs", ["condition_id", "contact_id"]
    )


def downgrade() -> None:
    """Drop workflow_conditions, workflow_branches, and workflow_condition_logs tables."""
    op.drop_table("workflow_condition_logs")
    op.drop_table("workflow_branches")
    op.drop_table("workflow_conditions")
