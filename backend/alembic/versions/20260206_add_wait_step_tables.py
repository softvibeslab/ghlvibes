"""Add wait step tables for workflow automation.

Revision ID: 20260206_add_wait_step_tables
Revises: <previous_revision>
Create Date: 2026-02-06

This migration adds tables for wait step execution tracking
and event listener registration in workflow automation.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "20260206_add_wait_step_tables"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create wait step execution tables."""
    # Create enum types
    wait_type_enum = postgresql.ENUM(
        "fixed_time",
        "until_date",
        "until_time",
        "for_event",
        name="wait_type",
        create_type=True,
    )
    wait_type_enum.create(op.get_bind())

    wait_execution_status_enum = postgresql.ENUM(
        "waiting",
        "scheduled",
        "resumed",
        "timeout",
        "cancelled",
        "error",
        name="wait_execution_status",
        create_type=True,
    )
    wait_execution_status_enum.create(op.get_bind())

    event_type_enum = postgresql.ENUM(
        "email_open",
        "email_click",
        "sms_reply",
        "form_submit",
        "page_visit",
        "appointment_booked",
        name="event_type",
        create_type=True,
    )
    event_type_enum.create(op.get_bind())

    listener_event_type_enum = postgresql.ENUM(
        "email_open",
        "email_click",
        "sms_reply",
        "form_submit",
        "page_visit",
        "appointment_booked",
        name="listener_event_type",
        create_type=True,
    )
    listener_event_type_enum.create(op.get_bind())

    # Create workflow_wait_executions table
    op.create_table(
        "workflow_wait_executions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "workflow_execution_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("workflow_executions.id", ondelete="CASCADE"),
            nullable=False,
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
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("step_id", sa.String(100), nullable=False),
        sa.Column("wait_type", wait_type_enum, nullable=False),
        sa.Column("wait_config", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("timezone", sa.String(100), nullable=False, server_default="UTC"),
        sa.Column("event_type", event_type_enum, nullable=True),
        sa.Column("event_correlation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_timeout_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", wait_execution_status_enum, nullable=False, server_default="waiting"),
        sa.Column("resumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resumed_by", sa.String(50), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )

    # Create indexes for workflow_wait_executions
    op.create_index(
        "ix_wait_executions_scheduled",
        "workflow_wait_executions",
        ["scheduled_at"],
        postgresql_where=sa.text("status = 'scheduled'"),
    )
    op.create_index(
        "ix_wait_executions_event",
        "workflow_wait_executions",
        ["event_type", "event_correlation_id"],
        postgresql_where=sa.text("status = 'waiting'"),
    )
    op.create_index(
        "uq_wait_execution_step",
        "workflow_wait_executions",
        ["workflow_execution_id", "step_id"],
        unique=True,
    )

    # Create workflow_event_listeners table
    op.create_table(
        "workflow_event_listeners",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "wait_execution_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("workflow_wait_executions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_type", listener_event_type_enum, nullable=False),
        sa.Column("correlation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "contact_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("contacts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "workflow_execution_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("workflow_executions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("match_criteria", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("matched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("matched_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )

    # Create indexes for workflow_event_listeners
    op.create_index(
        "ix_event_listeners_lookup",
        "workflow_event_listeners",
        ["event_type", "contact_id"],
        postgresql_where=sa.text("status = 'active'"),
    )
    op.create_index(
        "ix_event_listeners_expires",
        "workflow_event_listeners",
        ["expires_at"],
        postgresql_where=sa.text("status = 'active'"),
    )
    op.create_index(
        "uq_event_listener",
        "workflow_event_listeners",
        ["wait_execution_id", "event_type"],
        unique=True,
    )


def downgrade() -> None:
    """Drop wait step execution tables."""
    op.drop_table("workflow_event_listeners")
    op.drop_table("workflow_wait_executions")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS listener_event_type")
    op.execute("DROP TYPE IF EXISTS event_type")
    op.execute("DROP TYPE IF EXISTS wait_execution_status")
    op.execute("DROP TYPE IF EXISTS wait_type")
