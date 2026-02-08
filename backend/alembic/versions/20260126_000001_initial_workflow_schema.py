"""Initial workflow schema.

Revision ID: 001_initial
Revises:
Create Date: 2026-01-26 00:00:01

This migration creates the initial database schema for workflows including:
- accounts table (stub)
- users table (stub)
- workflows table
- workflow_audit_logs table
- Row Level Security policies
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# Revision identifiers
revision: str = "001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create initial schema."""
    # Create workflow_status enum type
    workflow_status = postgresql.ENUM(
        "draft",
        "active",
        "paused",
        name="workflow_status",
        create_type=True,
    )
    workflow_status.create(op.get_bind(), checkfirst=True)

    # Create accounts table (stub for foreign key)
    op.create_table(
        "accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create users table (stub for foreign key)
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    # Create workflows table
    op.create_table(
        "workflows",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("trigger_type", sa.String(50), nullable=True),
        sa.Column(
            "trigger_config",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "status",
            workflow_status,
            nullable=False,
            server_default="draft",
        ),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "length(name) >= 3 AND length(name) <= 100",
            name="ck_workflow_name_length",
        ),
    )

    # Create indexes for workflows table
    op.create_index(
        "ix_workflow_account_id",
        "workflows",
        ["account_id"],
    )
    op.create_index(
        "ix_workflow_account_status",
        "workflows",
        ["account_id", "status"],
    )
    op.create_index(
        "ix_workflow_created_at",
        "workflows",
        ["created_at"],
    )
    op.create_index(
        "ix_workflow_trigger_type",
        "workflows",
        ["trigger_type"],
    )

    # Create partial unique index for name within account (excluding deleted)
    op.execute(
        """
        CREATE UNIQUE INDEX uq_workflow_account_name
        ON workflows (account_id, name)
        WHERE deleted_at IS NULL
        """
    )

    # Create partial index for active workflows
    op.execute(
        """
        CREATE INDEX ix_workflow_active
        ON workflows (account_id)
        WHERE status = 'active' AND deleted_at IS NULL
        """
    )

    # Create workflow_audit_logs table
    op.create_table(
        "workflow_audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "workflow_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("workflows.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column(
            "old_values",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "new_values",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "changed_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for audit logs
    op.create_index(
        "ix_audit_workflow_id",
        "workflow_audit_logs",
        ["workflow_id"],
    )
    op.create_index(
        "ix_audit_workflow_changed_at",
        "workflow_audit_logs",
        ["workflow_id", "changed_at"],
    )
    op.create_index(
        "ix_audit_action",
        "workflow_audit_logs",
        ["action"],
    )

    # Create Row Level Security policies (for Supabase compatibility)
    # Note: These require superuser privileges and are optional
    op.execute(
        """
        -- Enable RLS on workflows table
        ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;

        -- Policy: Users can only see workflows in their account
        CREATE POLICY workflows_account_isolation ON workflows
        FOR ALL
        USING (
            account_id = current_setting('app.current_account_id', true)::uuid
        );

        -- Enable RLS on audit logs
        ALTER TABLE workflow_audit_logs ENABLE ROW LEVEL SECURITY;

        -- Policy: Users can only see audit logs for their workflows
        CREATE POLICY audit_logs_account_isolation ON workflow_audit_logs
        FOR ALL
        USING (
            workflow_id IN (
                SELECT id FROM workflows
                WHERE account_id = current_setting('app.current_account_id', true)::uuid
            )
        );
        """
    )


def downgrade() -> None:
    """Drop all tables and types."""
    # Drop RLS policies first
    op.execute("DROP POLICY IF EXISTS workflows_account_isolation ON workflows")
    op.execute("DROP POLICY IF EXISTS audit_logs_account_isolation ON workflow_audit_logs")

    # Drop tables
    op.drop_table("workflow_audit_logs")
    op.drop_table("workflows")
    op.drop_table("users")
    op.drop_table("accounts")

    # Drop enum type
    op.execute("DROP TYPE IF EXISTS workflow_status")
