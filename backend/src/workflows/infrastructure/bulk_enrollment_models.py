"""SQLAlchemy models for bulk enrollment.

These models define the database schema for bulk enrollment jobs,
batches, and failure tracking.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class BulkEnrollmentJobModel(Base):
    """SQLAlchemy model for bulk enrollment jobs.

    Represents bulk operations to enroll multiple contacts into workflows.
    """

    __tablename__ = "bulk_enrollment_jobs"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    workflow_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Job status and selection
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
        index=True,
    )
    selection_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    contact_ids: Mapped[list[UUID] | None] = mapped_column(
        ARRAY(PG_UUID(as_uuid=True)),
        nullable=True,
    )
    filter_criteria: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    csv_file_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Statistics
    total_contacts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    processed_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    success_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    failure_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    skipped_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # Batching
    batch_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=100,
    )
    total_batches: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    completed_batches: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # Timing
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    estimated_completion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Audit fields
    created_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    # Indexes
    __table_args__ = (
        Index("idx_bulk_jobs_account_status", "account_id", "status"),
        Index("idx_bulk_jobs_workflow", "workflow_id"),
        Index("idx_bulk_jobs_active", "account_id", "status", postgresql_where="status IN ('pending', 'validating', 'queued', 'processing')"),
    )

    def to_domain(self) -> Any:
        """Convert model to domain entity.

        Returns:
            BulkEnrollmentJob domain entity.
        """
        from src.workflows.domain.bulk_enrollment_entities import (  # noqa: PLC0415
            BulkEnrollmentJob,
            JobStatus,
            SelectionCriteria,
            SelectionType,
        )

        # Convert selection
        selection = SelectionCriteria(
            selection_type=SelectionType(self.selection_type),
            contact_ids=self.contact_ids,
            filter_criteria=self.filter_criteria,
            csv_file_url=self.csv_file_url,
        )

        return BulkEnrollmentJob(
            id=self.id,
            account_id=self.account_id,
            workflow_id=self.workflow_id,
            status=JobStatus(self.status),
            selection=selection,
            total_contacts=self.total_contacts,
            processed_count=self.processed_count,
            success_count=self.success_count,
            failure_count=self.failure_count,
            skipped_count=self.skipped_count,
            batch_size=self.batch_size,
            total_batches=self.total_batches,
            completed_batches=self.completed_batches,
            scheduled_at=self.scheduled_at,
            started_at=self.started_at,
            completed_at=self.completed_at,
            estimated_completion=self.estimated_completion,
            created_by=self.created_by,
            created_at=self.created_at,
            updated_at=self.updated_at,
            version=self.version,
        )

    @classmethod
    def from_domain(cls, job: Any) -> "BulkEnrollmentJobModel":
        """Create model from domain entity.

        Args:
            job: BulkEnrollmentJob domain entity.

        Returns:
            BulkEnrollmentJobModel instance.
        """
        return cls(
            id=job.id,
            account_id=job.account_id,
            workflow_id=job.workflow_id,
            status=job.status.value,
            selection_type=job.selection.selection_type.value,
            contact_ids=job.selection.contact_ids,
            filter_criteria=job.selection.filter_criteria,
            csv_file_url=job.selection.csv_file_url,
            total_contacts=job.total_contacts,
            processed_count=job.processed_count,
            success_count=job.success_count,
            failure_count=job.failure_count,
            skipped_count=job.skipped_count,
            batch_size=job.batch_size,
            total_batches=job.total_batches,
            completed_batches=job.completed_batches,
            scheduled_at=job.scheduled_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            estimated_completion=job.estimated_completion,
            created_by=job.created_by,
            created_at=job.created_at,
            updated_at=job.updated_at,
            version=job.version,
        )


class BulkEnrollmentBatchModel(Base):
    """SQLAlchemy model for bulk enrollment batches.

    Represents individual batches of contacts being processed.
    """

    __tablename__ = "bulk_enrollment_batches"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign key
    job_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Batch details
    batch_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
    )
    contact_ids: Mapped[list[UUID]] = mapped_column(
        ARRAY(PG_UUID(as_uuid=True)),
        nullable=False,
    )
    success_ids: Mapped[list[UUID]] = mapped_column(
        ARRAY(PG_UUID(as_uuid=True)),
        default=list,
        nullable=False,
    )
    failure_ids: Mapped[list[UUID]] = mapped_column(
        ARRAY(PG_UUID(as_uuid=True)),
        default=list,
        nullable=False,
    )

    # Processing details
    attempt_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    # Timing
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    duration_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Indexes
    __table_args__ = (
        Index("idx_bulk_batches_job", "job_id"),
        Index("idx_bulk_batches_status", "status"),
    )

    def to_domain(self) -> Any:
        """Convert model to domain entity.

        Returns:
            BulkEnrollmentBatch domain entity.
        """
        from src.workflows.domain.bulk_enrollment_entities import (  # noqa: PLC0415
            BulkEnrollmentBatch,
            BatchStatus,
        )

        return BulkEnrollmentBatch(
            id=self.id,
            job_id=self.job_id,
            batch_number=self.batch_number,
            status=BatchStatus(self.status),
            contact_ids=self.contact_ids,
            success_ids=self.success_ids,
            failure_ids=self.failure_ids,
            attempt_count=self.attempt_count,
            error_message=self.error_message,
            started_at=self.started_at,
            completed_at=self.completed_at,
            duration_ms=self.duration_ms,
        )

    @classmethod
    def from_domain(cls, batch: Any) -> "BulkEnrollmentBatchModel":
        """Create model from domain entity.

        Args:
            batch: BulkEnrollmentBatch domain entity.

        Returns:
            BulkEnrollmentBatchModel instance.
        """
        return cls(
            id=batch.id,
            job_id=batch.job_id,
            batch_number=batch.batch_number,
            status=batch.status.value,
            contact_ids=batch.contact_ids,
            success_ids=batch.success_ids,
            failure_ids=batch.failure_ids,
            attempt_count=batch.attempt_count,
            error_message=batch.error_message,
            started_at=batch.started_at,
            completed_at=batch.completed_at,
            duration_ms=batch.duration_ms,
        )


class BulkEnrollmentFailureModel(Base):
    """SQLAlchemy model for individual enrollment failures.

    Tracks details of contacts that failed to enroll.
    """

    __tablename__ = "bulk_enrollment_failures"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys
    job_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    batch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )
    contact_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Error details
    error_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    error_message: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )
    error_details: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    # Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Indexes
    __table_args__ = (
        Index("idx_bulk_failures_job", "job_id"),
        Index("idx_bulk_failures_contact", "contact_id"),
    )

    def to_domain(self) -> Any:
        """Convert model to domain entity.

        Returns:
            EnrollmentFailure domain entity.
        """
        from src.workflows.domain.bulk_enrollment_entities import EnrollmentFailure  # noqa: PLC0415

        return EnrollmentFailure(
            id=self.id,
            job_id=self.job_id,
            batch_id=self.batch_id,
            contact_id=self.contact_id,
            error_code=self.error_code,
            error_message=self.error_message,
            error_details=self.error_details,
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(cls, failure: Any) -> "BulkEnrollmentFailureModel":
        """Create model from domain entity.

        Args:
            failure: EnrollmentFailure domain entity.

        Returns:
            BulkEnrollmentFailureModel instance.
        """
        return cls(
            id=failure.id,
            job_id=failure.job_id,
            batch_id=failure.batch_id,
            contact_id=failure.contact_id,
            error_code=failure.error_code,
            error_message=failure.error_message,
            error_details=failure.error_details,
            created_at=failure.created_at,
        )
