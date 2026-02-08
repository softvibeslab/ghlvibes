"""Add bulk enrollment tables.

Revision ID: 20260206_000005
Revises: 20260206_000004
Create Date: 2026-02-06

This migration creates the bulk enrollment system including
jobs, batches, and failure tracking tables.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic
revision: str = "20260206_000005"
down_revision: str | None = "20260206_000004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create bulk enrollment tables and indexes."""
    # Create bulk_enrollment_jobs table
    op.create_table(
        "bulk_enrollment_jobs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(30), server_default="pending", nullable=False),
        sa.Column("selection_type", sa.String(20), nullable=False),
        sa.Column("contact_ids", postgresql.ARRAY(postgresql.UUID()), nullable=True),
        sa.Column("filter_criteria", postgresql.JSONB(), nullable=True),
        sa.Column("csv_file_url", sa.String(500), nullable=True),
        sa.Column("total_contacts", sa.Integer(), server_default="0", nullable=False),
        sa.Column("processed_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("success_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("failure_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("skipped_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("batch_size", sa.Integer(), server_default="100", nullable=False),
        sa.Column("total_batches", sa.Integer(), server_default="0", nullable=False),
        sa.Column("completed_batches", sa.Integer(), server_default="0", nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("estimated_completion", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
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
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for bulk_enrollment_jobs
    op.create_index(
        "idx_bulk_jobs_account_status",
        "bulk_enrollment_jobs",
        ["account_id", "status"],
    )
    op.create_index(
        "idx_bulk_jobs_workflow",
        "bulk_enrollment_jobs",
        ["workflow_id"],
    )
    op.create_index(
        "idx_bulk_jobs_active",
        "bulk_enrollment_jobs",
        ["account_id", "status"],
        postgresql_where="status IN ('pending', 'validating', 'queued', 'processing')",
    )

    # Create bulk_enrollment_batches table
    op.create_table(
        "bulk_enrollment_batches",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("batch_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("contact_ids", postgresql.ARRAY(postgresql.UUID()), nullable=False),
        sa.Column(
            "success_ids",
            postgresql.ARRAY(postgresql.UUID()),
            server_default=sa.text("ARRAY[]::UUID[]"),
            nullable=False,
        ),
        sa.Column(
            "failure_ids",
            postgresql.ARRAY(postgresql.UUID()),
            server_default=sa.text("ARRAY[]::UUID[]"),
            nullable=False,
        ),
        sa.Column("attempt_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_message", sa.String(1000), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for bulk_enrollment_batches
    op.create_index(
        "idx_bulk_batches_job",
        "bulk_enrollment_batches",
        ["job_id"],
    )
    op.create_index(
        "idx_bulk_batches_status",
        "bulk_enrollment_batches",
        ["status"],
    )

    # Create bulk_enrollment_failures table
    op.create_table(
        "bulk_enrollment_failures",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("batch_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("error_code", sa.String(50), nullable=False),
        sa.Column("error_message", sa.String(1000), nullable=False),
        sa.Column("error_details", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for bulk_enrollment_failures
    op.create_index(
        "idx_bulk_failures_job",
        "bulk_enrollment_failures",
        ["job_id"],
    )
    op.create_index(
        "idx_bulk_failures_contact",
        "bulk_enrollment_failures",
        ["contact_id"],
    )


def downgrade() -> None:
    """Drop bulk enrollment tables and indexes."""
    # Drop bulk_enrollment_failures table
    op.drop_index("idx_bulk_failures_contact", table_name="bulk_enrollment_failures")
    op.drop_index("idx_bulk_failures_job", table_name="bulk_enrollment_failures")
    op.drop_table("bulk_enrollment_failures")

    # Drop bulk_enrollment_batches table
    op.drop_index("idx_bulk_batches_status", table_name="bulk_enrollment_batches")
    op.drop_index("idx_bulk_batches_job", table_name="bulk_enrollment_batches")
    op.drop_table("bulk_enrollment_batches")

    # Drop bulk_enrollment_jobs table
    op.drop_index("idx_bulk_jobs_active", table_name="bulk_enrollment_jobs")
    op.drop_index("idx_bulk_jobs_workflow", table_name="bulk_enrollment_jobs")
    op.drop_index("idx_bulk_jobs_account_status", table_name="bulk_enrollment_jobs")
    op.drop_table("bulk_enrollment_jobs")
