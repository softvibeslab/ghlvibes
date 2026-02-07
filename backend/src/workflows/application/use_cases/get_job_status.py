"""Use case for retrieving bulk enrollment job status."""

from uuid import UUID

from src.workflows.application.bulk_enrollment_dtos import (
    BulkEnrollmentJobResponseDTO,
    BulkEnrollmentProgressDTO,
)
from src.workflows.domain.exceptions import WorkflowNotFoundError
from src.workflows.infrastructure.bulk_enrollment_repository import IBulkEnrollmentRepository


class GetJobStatusUseCase:
    """Use case for retrieving bulk enrollment job status and progress.

    This use case returns current job status and real-time progress metrics.
    """

    def __init__(
        self,
        bulk_repository: IBulkEnrollmentRepository,
    ) -> None:
        """Initialize the use case.

        Args:
            bulk_repository: Repository for bulk enrollment jobs.
        """
        self._bulk_repository = bulk_repository

    async def execute(
        self,
        job_id: UUID,
        account_id: UUID,
    ) -> BulkEnrollmentJobResponseDTO:
        """Execute the use case.

        Args:
            job_id: Job to retrieve.
            account_id: Account owning the job.

        Returns:
            Job status and details.

        Raises:
            WorkflowNotFoundError: If job doesn't exist.
        """
        job = await self._bulk_repository.get_job_by_id(job_id, account_id)
        if job is None:
            raise WorkflowNotFoundError(f"Bulk enrollment job not found: {job_id}")

        return BulkEnrollmentJobResponseDTO.model_validate(job.to_dict())

    async def get_progress(
        self,
        job_id: UUID,
        account_id: UUID,
    ) -> BulkEnrollmentProgressDTO:
        """Get real-time progress for a job.

        Args:
            job_id: Job to get progress for.
            account_id: Account owning the job.

        Returns:
            Real-time progress metrics.

        Raises:
            WorkflowNotFoundError: If job doesn't exist.
        """
        job = await self._bulk_repository.get_job_by_id(job_id, account_id)
        if job is None:
            raise WorkflowNotFoundError(f"Bulk enrollment job not found: {job_id}")

        # Calculate rate (contacts per second)
        rate = 0.0
        if job.started_at and job.processed_count > 0:
            elapsed_seconds = (job.updated_at - job.started_at).total_seconds()
            if elapsed_seconds > 0:
                rate = job.processed_count / elapsed_seconds

        # Estimate time remaining
        estimated_time_remaining = None
        if rate > 0 and (job.total_contacts - job.processed_count) > 0:
            remaining_contacts = job.total_contacts - job.processed_count
            estimated_time_remaining = int(remaining_contacts / rate)

        return BulkEnrollmentProgressDTO(
            job_id=job.id,
            status=job.status.value,
            total_contacts=job.total_contacts,
            processed=job.processed_count,
            success=job.success_count,
            failed=job.failure_count,
            skipped=job.skipped_count,
            current_batch=job.completed_batches + 1,
            total_batches=job.total_batches,
            progress_percentage=job.progress_percentage,
            rate=rate,
            estimated_time_remaining_seconds=estimated_time_remaining,
        )
