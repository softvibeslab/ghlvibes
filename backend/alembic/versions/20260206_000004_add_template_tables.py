"""Add workflow template tables.

Revision ID: 20260206_000004
Revises: 20260206_add_wait_step_tables
Create Date: 2026-02-06

This migration creates the workflow templates system including
template configurations and usage tracking tables.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic
revision: str = "20260206_000004"
down_revision: Union[str, None] = "20260206_add_wait_step_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create workflow template tables and indexes."""
    # Create workflow_templates table
    op.create_table(
        "workflow_templates",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1000), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column(
            "required_integrations",
            postgresql.ARRAY(sa.String()),
            server_default=sa.text("ARRAY[]::VARCHAR[]"),
            nullable=False,
        ),
        sa.Column(
            "tags",
            postgresql.ARRAY(sa.String()),
            server_default=sa.text("ARRAY[]::VARCHAR[]"),
            nullable=False,
        ),
        sa.Column("estimated_completion_rate", sa.Integer, nullable=True),
        sa.Column("is_system_template", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_shared", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("workflow_config", postgresql.JSONB(), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("usage_count", sa.Integer(), server_default="0", nullable=False),
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
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for workflow_templates
    op.create_index(
        "idx_templates_account_category",
        "workflow_templates",
        ["account_id", "category"],
    )
    op.create_index(
        "idx_templates_system",
        "workflow_templates",
        ["is_system_template"],
    )
    op.create_index(
        "idx_templates_tags",
        "workflow_templates",
        ["tags"],
        postgresql_using="gin",
    )

    # Create template_usage table
    op.create_table(
        "template_usage",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "template_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
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
            "cloned_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column("template_version", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for template_usage
    op.create_index(
        "idx_template_usage_template",
        "template_usage",
        ["template_id"],
    )
    op.create_index(
        "idx_template_usage_workflow",
        "template_usage",
        ["workflow_id"],
    )
    op.create_index(
        "idx_template_usage_account",
        "template_usage",
        ["account_id"],
    )


def downgrade() -> None:
    """Drop workflow template tables and indexes."""
    # Drop template_usage table
    op.drop_index("idx_template_usage_account", table_name="template_usage")
    op.drop_index("idx_template_usage_workflow", table_name="template_usage")
    op.drop_index("idx_template_usage_template", table_name="template_usage")
    op.drop_table("template_usage")

    # Drop workflow_templates table
    op.drop_index("idx_templates_tags", table_name="workflow_templates")
    op.drop_index("idx_templates_system", table_name="workflow_templates")
    op.drop_index("idx_templates_account_category", table_name="workflow_templates")
    op.drop_table("workflow_templates")
