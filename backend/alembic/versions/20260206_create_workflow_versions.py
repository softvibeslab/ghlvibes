"""Create workflow versioning tables

Revision ID: 20260206_create_workflow_versions
Revises:
Create Date: 2026-02-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260206_create_workflow_versions"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create workflow versioning tables and indexes."""

    # Create workflow_versions table
    op.create_table(
        "workflow_versions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("trigger_type", sa.String(50), nullable=True),
        sa.Column(
            "trigger_config",
            postgresql.JSONB(),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("actions", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("conditions", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("change_summary", sa.String(500), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("active_executions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("workflow_id", "version_number", name="uq_workflow_version_number"),
        sa.CheckConstraint("version_number >= 1", name="ck_version_number_min"),
        sa.CheckConstraint("version_number <= 1000", name="ck_version_number_max"),
        sa.CheckConstraint(
            "status IN ('draft', 'active', 'archived')",
            name="ck_version_status",
        ),
        sa.CheckConstraint("active_executions >= 0", name="ck_active_executions"),
    )

    # Create indexes for workflow_versions
    op.create_index("ix_workflow_versions_workflow_id", "workflow_versions", ["workflow_id"])
    op.create_index("ix_workflow_versions_account_id", "workflow_versions", ["account_id"])
    op.create_index("ix_workflow_versions_status", "workflow_versions", ["status"])
    op.create_index("ix_workflow_versions_is_current", "workflow_versions", ["is_current"])
    op.create_index("ix_workflow_versions_created_at", "workflow_versions", ["created_at"])
    op.create_index(
        "ix_workflow_versions_active_executions",
        "workflow_versions",
        ["active_executions"],
    )
    op.create_index(
        "ix_workflow_versions_current_unique",
        "workflow_versions",
        ["workflow_id"],
        unique=True,
        postgresql_where=sa.text("is_current = true"),
    )

    # Create workflow_version_migrations table
    op.create_table(
        "workflow_version_migrations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("strategy", sa.String(20), nullable=False),
        sa.Column(
            "mapping_rules",
            postgresql.JSONB(),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("batch_size", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("contacts_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("contacts_migrated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("contacts_failed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_log", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.CheckConstraint(
            "strategy IN ('immediate', 'gradual', 'manual')",
            name="ck_migration_strategy",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed', 'failed', 'cancelled')",
            name="ck_migration_status",
        ),
        sa.CheckConstraint("contacts_total >= 0", name="ck_contacts_total"),
        sa.CheckConstraint("contacts_migrated >= 0", name="ck_contacts_migrated"),
        sa.CheckConstraint("contacts_failed >= 0", name="ck_contacts_failed"),
    )

    # Create indexes for workflow_version_migrations
    op.create_index(
        "ix_version_migrations_workflow_id",
        "workflow_version_migrations",
        ["workflow_id"],
    )
    op.create_index(
        "ix_version_migrations_status",
        "workflow_version_migrations",
        ["status"],
    )
    op.create_index(
        "ix_version_migrations_created_at",
        "workflow_version_migrations",
        ["created_at"],
    )

    # Create workflow_version_drafts table
    op.create_table(
        "workflow_version_drafts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("draft_data", postgresql.JSONB(), nullable=False),
        sa.Column("last_saved_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("workflow_id", "user_id", name="uq_workflow_version_draft"),
    )

    # Create indexes for workflow_version_drafts
    op.create_index("ix_version_drafts_workflow_id", "workflow_version_drafts", ["workflow_id"])
    op.create_index("ix_version_drafts_user_id", "workflow_version_drafts", ["user_id"])
    op.create_index("ix_version_drafts_last_saved_at", "workflow_version_drafts", ["last_saved_at"])

    # Create workflow_version_audit_logs table
    op.create_table(
        "workflow_version_audit_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("details", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )

    # Create indexes for workflow_version_audit_logs
    op.create_index(
        "ix_version_audit_workflow_id",
        "workflow_version_audit_logs",
        ["workflow_id"],
    )
    op.create_index(
        "ix_version_audit_version_id",
        "workflow_version_audit_logs",
        ["version_id"],
    )
    op.create_index(
        "ix_version_audit_action",
        "workflow_version_audit_logs",
        ["action"],
    )
    op.create_index(
        "ix_version_audit_created_at",
        "workflow_version_audit_logs",
        ["created_at"],
    )


def downgrade() -> None:
    """Drop workflow versioning tables and indexes."""

    # Drop tables
    op.drop_table("workflow_version_audit_logs")
    op.drop_table("workflow_version_drafts")
    op.drop_table("workflow_version_migrations")
    op.drop_table("workflow_versions")
