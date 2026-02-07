"""Bulk enrollment domain entities for the workflow module.

Entities represent objects with identity that persist over time.
The BulkEnrollmentJob entity is the aggregate root for bulk operations.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Self
from uuid import UUID, uuid4

from src.workflows.domain.exceptions import ValidationError, InvalidStatusTransitionError


class JobStatus(str, Enum):
    """Status of a bulk enrollment job.

    Tracks the lifecycle of a bulk enrollment job through validation,
    queuing, processing, and completion.
    """

    PENDING = "pending"
    VALIDATING = "validating"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    CANCELLED = "cancelled"
    FAILED = "failed"

    def can_transition_to(self, new_status: "JobStatus") -> bool:
        """Check if transition to new status is allowed.

        Args:
            new_status: Desired new status.

        Returns:
            True if transition is allowed, False otherwise.
        """
        valid_transitions = {
            JobStatus.PENDING: [
                JobStatus.VALIDATING,
                JobStatus.CANCELLED,
                JobStatus.FAILED,
            ],
            JobStatus.VALIDATING: [
                JobStatus.QUEUED,
                JobStatus.FAILED,
                JobStatus.CANCELLED,
            ],
            JobStatus.QUEUED: [
                JobStatus.PROCESSING,
                JobStatus.CANCELLED,
                JobStatus.FAILED,
            ],
            JobStatus.PROCESSING: [
                JobStatus.COMPLETED,
                JobStatus.COMPLETED_WITH_ERRORS,
                JobStatus.CANCELLED,
                JobStatus.FAILED,
            ],
            JobStatus.COMPLETED: [],  # Terminal state
            JobStatus.COMPLETED_WITH_ERRORS: [],  # Terminal state
            JobStatus.CANCELLED: [],  # Terminal state
            JobStatus.FAILED: [],  # Terminal state
        }

        return new_status in valid_transitions.get(self, [])


class SelectionType(str, Enum):
    """Type of contact selection for bulk enrollment."""

    MANUAL = "manual"
    FILTER = "filter"
    CSV = "csv"


class BatchStatus(str, Enum):
    """Status of a batch within a bulk enrollment job."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class SelectionCriteria:
    """Value object for contact selection criteria.

    Supports different selection methods: manual IDs, filter-based, or CSV upload.
    """

    selection_type: SelectionType
    contact_ids: list[UUID] | None = None
    filter_criteria: dict[str, Any] | None = None
    csv_file_url: str | None = None
    identifier_column: str = "email"

    def __post_init__(self) -> None:
        """Validate selection criteria based on type."""
        if self.selection_type == SelectionType.MANUAL:
            if not self.contact_ids:
                raise ValidationError("Manual selection requires contact_ids")
            if len(self.contact_ids) > 10000:
                raise ValidationError(
                    f"Cannot exceed 10,000 contacts, got {len(self.contact_ids)}"
                )
        elif self.selection_type == SelectionType.FILTER:
            if not self.filter_criteria:
                raise ValidationError("Filter selection requires filter_criteria")
        elif self.selection_type == SelectionType.CSV:
            if not self.csv_file_url:
                raise ValidationError("CSV selection requires csv_file_url")
            if self.identifier_column not in ["email", "contact_id"]:
                raise ValidationError(
                    f"identifier_column must be 'email' or 'contact_id', got {self.identifier_column}"
                )


@dataclass
class BulkEnrollmentJob:
    """Bulk enrollment job aggregate root entity.

    Represents a bulk operation to enroll multiple contacts into a workflow.
    Contacts are processed in batches asynchronously.

    Attributes:
        id: Unique identifier for the job.
        account_id: Account that initiated the job.
        workflow_id: Workflow to enroll contacts into.
        status: Current job status.
        selection: Contact selection criteria.
        total_contacts: Total number of contacts to process.
        processed_count: Number of contacts processed.
        success_count: Number of successful enrollments.
        failure_count: Number of failed enrollments.
        skipped_count: Number of skipped contacts (duplicates, blocked, etc.).
        batch_size: Number of contacts per batch.
        total_batches: Total number of batches.
        completed_batches: Number of completed batches.
        scheduled_at: When the job is scheduled to run (optional).
        started_at: When job processing started.
        completed_at: When job processing completed.
        estimated_completion: Estimated completion time.
        created_by: User who created the job.
        created_at: Timestamp when job was created.
        updated_at: Timestamp of last update.
        version: Optimistic locking version.
    """

    id: UUID
    account_id: UUID
    workflow_id: UUID
    status: JobStatus
    selection: SelectionCriteria
    total_contacts: int
    processed_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    skipped_count: int = 0
    batch_size: int = 100
    total_batches: int = 0
    completed_batches: int = 0
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    estimated_completion: datetime | None = None
    created_by: UUID | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    version: int = 1

    def __post_init__(self) -> None:
        """Validate entity state after initialization."""
        # Ensure selection is a SelectionCriteria instance
        if isinstance(self.selection, dict):
            object.__setattr__(
                self, "selection", SelectionCriteria(**self.selection)
            )

        # Validate counts don't exceed total
        if self.processed_count > self.total_contacts:
            raise ValidationError(
                f"processed_count ({self.processed_count}) cannot exceed total_contacts ({self.total_contacts})"
            )
        if self.success_count + self.failure_count + self.skipped_count > self.total_contacts:
            raise ValidationError("Sum of success/failure/skipped counts exceeds total")

        # Validate batch_size
        if not 10 <= self.batch_size <= 500:
            raise ValidationError(f"batch_size must be between 10 and 500, got {self.batch_size}")

    @classmethod
    def create(
        cls,
        account_id: UUID,
        workflow_id: UUID,
        selection: dict[str, Any] | SelectionCriteria,
        total_contacts: int,
        created_by: UUID,
        batch_size: int = 100,
        scheduled_at: datetime | None = None,
    ) -> Self:
        """Factory method to create a new bulk enrollment job.

        Args:
            account_id: Account initiating the job.
            workflow_id: Workflow to enroll contacts into.
            selection: Contact selection criteria (dict or SelectionCriteria).
            total_contacts: Total number of contacts to process.
            created_by: User creating the job.
            batch_size: Contacts per batch (default 100).
            scheduled_at: Optional scheduled execution time.

        Returns:
            A new BulkEnrollmentJob instance.
        """
        selection_criteria = (
            selection
            if isinstance(selection, SelectionCriteria)
            else SelectionCriteria(**selection)
        )

        # Calculate total batches
        total_batches = (total_contacts + batch_size - 1) // batch_size  # Ceiling division

        now = datetime.now(UTC)

        return cls(
            id=uuid4(),
            account_id=account_id,
            workflow_id=workflow_id,
            status=JobStatus.PENDING,
            selection=selection_criteria,
            total_contacts=total_contacts,
            batch_size=batch_size,
            total_batches=total_batches,
            created_by=created_by,
            created_at=now,
            updated_at=now,
            scheduled_at=scheduled_at,
        )

    def start_validating(self) -> None:
        """Transition job to validating status."""
        self._transition_to(JobStatus.VALIDATING)

    def start_processing(self) -> None:
        """Transition job to processing status."""
        self._transition_to(JobStatus.PROCESSING)
        if self.started_at is None:
            self.started_at = datetime.now(UTC)

    def complete(self, with_errors: bool = False) -> None:
        """Transition job to completed status.

        Args:
            with_errors: Whether there were errors during processing.
        """
        new_status = JobStatus.COMPLETED_WITH_ERRORS if with_errors else JobStatus.COMPLETED
        self._transition_to(new_status)
        self.completed_at = datetime.now(UTC)

    def fail(self) -> None:
        """Transition job to failed status."""
        self._transition_to(JobStatus.FAILED)
        self.completed_at = datetime.now(UTC)

    def cancel(self) -> None:
        """Transition job to cancelled status."""
        self._transition_to(JobStatus.CANCELLED)
        self.completed_at = datetime.now(UTC)

    def _transition_to(self, new_status: JobStatus) -> None:
        """Transition to new status with validation.

        Args:
            new_status: Desired new status.

        Raises:
            InvalidStatusTransitionError: If transition is not allowed.
        """
        if not self.status.can_transition_to(new_status):
            raise InvalidStatusTransitionError(
                self.status.value,
                new_status.value,
            )
        self.status = new_status
        self._touch()

    def update_progress(
        self,
        processed_delta: int = 0,
        success_delta: int = 0,
        failure_delta: int = 0,
        skipped_delta: int = 0,
        batch_delta: int = 0,
    ) -> None:
        """Update job progress counters.

        Args:
            processed_delta: Increment to processed count.
            success_delta: Increment to success count.
            failure_delta: Increment to failure count.
            skipped_delta: Increment to skipped count.
            batch_delta: Increment to completed batches count.
        """
        self.processed_count += processed_delta
        self.success_count += success_delta
        self.failure_count += failure_delta
        self.skipped_count += skipped_delta
        self.completed_batches += batch_delta
        self._touch()

    def _touch(self) -> None:
        """Update timestamp and version."""
        self.updated_at = datetime.now(UTC)
        self.version += 1

    @property
    def progress_percentage(self) -> float:
        """Calculate job completion percentage.

        Returns:
            Completion percentage (0-100).
        """
        if self.total_contacts == 0:
            return 100.0
        return (self.processed_count / self.total_contacts) * 100

    @property
    def is_pending(self) -> bool:
        """Check if job is pending."""
        return self.status == JobStatus.PENDING

    @property
    def is_processing(self) -> bool:
        """Check if job is currently processing."""
        return self.status == JobStatus.PROCESSING

    @property
    def is_completed(self) -> bool:
        """Check if job completed successfully."""
        return self.status == JobStatus.COMPLETED

    @property
    def is_terminal(self) -> bool:
        """Check if job is in a terminal state."""
        return self.status in [
            JobStatus.COMPLETED,
            JobStatus.COMPLETED_WITH_ERRORS,
            JobStatus.CANCELLED,
            JobStatus.FAILED,
        ]

    def to_dict(self) -> dict[str, Any]:
        """Convert job to dictionary representation.

        Returns:
            Dictionary containing all job attributes.
        """
        return {
            "id": str(self.id),
            "account_id": str(self.account_id),
            "workflow_id": str(self.workflow_id),
            "status": self.status.value,
            "selection_type": self.selection.selection_type.value,
            "total_contacts": self.total_contacts,
            "processed_count": self.processed_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "skipped_count": self.skipped_count,
            "progress_percentage": round(self.progress_percentage, 2),
            "batch_size": self.batch_size,
            "total_batches": self.total_batches,
            "completed_batches": self.completed_batches,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "estimated_completion": (
                self.estimated_completion.isoformat() if self.estimated_completion else None
            ),
            "created_by": str(self.created_by) if self.created_by else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
        }


@dataclass
class BulkEnrollmentBatch:
    """Bulk enrollment batch entity.

    Represents a single batch of contacts being processed as part of a bulk job.

    Attributes:
        id: Unique identifier for the batch.
        job_id: Parent bulk enrollment job.
        batch_number: Batch sequence number (1-based).
        status: Current batch status.
        contact_ids: Contact IDs in this batch.
        success_ids: IDs of successfully enrolled contacts.
        failure_ids: IDs of contacts that failed to enroll.
        attempt_count: Number of processing attempts.
        error_message: Error message if batch failed.
        started_at: When batch processing started.
        completed_at: When batch processing completed.
        duration_ms: Processing duration in milliseconds.
    """

    id: UUID
    job_id: UUID
    batch_number: int
    status: BatchStatus
    contact_ids: list[UUID]
    success_ids: list[UUID] = field(default_factory=list)
    failure_ids: list[UUID] = field(default_factory=list)
    attempt_count: int = 0
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: int | None = None

    @classmethod
    def create(cls, job_id: UUID, batch_number: int, contact_ids: list[UUID]) -> Self:
        """Factory method to create a new batch.

        Args:
            job_id: Parent bulk enrollment job.
            batch_number: Batch sequence number.
            contact_ids: Contact IDs in this batch.

        Returns:
            A new BulkEnrollmentBatch instance.
        """
        return cls(
            id=uuid4(),
            job_id=job_id,
            batch_number=batch_number,
            status=BatchStatus.PENDING,
            contact_ids=contact_ids,
        )

    def start_processing(self) -> None:
        """Mark batch as processing."""
        self.status = BatchStatus.PROCESSING
        self.attempt_count += 1
        self.started_at = datetime.now(UTC)

    def complete(self, success_ids: list[UUID], failure_ids: list[UUID]) -> None:
        """Mark batch as completed with results.

        Args:
            success_ids: Successfully enrolled contact IDs.
            failure_ids: Failed contact IDs.
        """
        self.status = BatchStatus.COMPLETED
        self.success_ids = success_ids
        self.failure_ids = failure_ids
        self.completed_at = datetime.now(UTC)

        if self.started_at:
            delta = self.completed_at - self.started_at
            self.duration_ms = int(delta.total_seconds() * 1000)

    def fail(self, error_message: str) -> None:
        """Mark batch as failed.

        Args:
            error_message: Error describing the failure.
        """
        self.status = BatchStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.now(UTC)

    def skip(self) -> None:
        """Mark batch as skipped."""
        self.status = BatchStatus.SKIPPED
        self.completed_at = datetime.now(UTC)

    def to_dict(self) -> dict[str, Any]:
        """Convert batch to dictionary representation.

        Returns:
            Dictionary containing all batch attributes.
        """
        return {
            "id": str(self.id),
            "job_id": str(self.job_id),
            "batch_number": self.batch_number,
            "status": self.status.value,
            "contact_count": len(self.contact_ids),
            "success_count": len(self.success_ids),
            "failure_count": len(self.failure_ids),
            "attempt_count": self.attempt_count,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms,
        }


@dataclass
class EnrollmentFailure:
    """Individual enrollment failure record.

    Tracks details of contacts that failed to enroll for debugging and retry.

    Attributes:
        id: Unique identifier for the failure record.
        job_id: Parent bulk enrollment job.
        batch_id: Batch that contained this contact.
        contact_id: Contact that failed to enroll.
        error_code: Machine-readable error code.
        error_message: Human-readable error message.
        error_details: Additional error details (JSON).
        created_at: Timestamp when failure was recorded.
    """

    id: UUID
    job_id: UUID
    batch_id: UUID | None
    contact_id: UUID
    error_code: str
    error_message: str
    error_details: dict[str, Any] | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        job_id: UUID,
        contact_id: UUID,
        error_code: str,
        error_message: str,
        batch_id: UUID | None = None,
        error_details: dict[str, Any] | None = None,
    ) -> Self:
        """Factory method to create a failure record.

        Args:
            job_id: Parent bulk enrollment job.
            contact_id: Contact that failed.
            error_code: Machine-readable error code.
            error_message: Human-readable error message.
            batch_id: Batch that contained the contact (optional).
            error_details: Additional error details (optional).

        Returns:
            A new EnrollmentFailure instance.
        """
        return cls(
            id=uuid4(),
            job_id=job_id,
            batch_id=batch_id,
            contact_id=contact_id,
            error_code=error_code,
            error_message=error_message,
            error_details=error_details,
            created_at=datetime.now(UTC),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert failure to dictionary representation.

        Returns:
            Dictionary containing all failure attributes.
        """
        return {
            "id": str(self.id),
            "job_id": str(self.job_id),
            "batch_id": str(self.batch_id) if self.batch_id else None,
            "contact_id": str(self.contact_id),
            "error_code": self.error_code,
            "error_message": self.error_message,
            "error_details": self.error_details,
            "created_at": self.created_at.isoformat(),
        }
