"""Use case for cancelling bulk enrollment jobs."""

from uuid import UUID

from src.workflows.application.bulk_enrollment_dtos import BulkEnrollmentJobResponseDTO
from src.workflows.domain.exceptions import InvalidStatusTransitionError, WorkflowNotFoundError
from src.workflows.infrastructure.bulk_enrollment_repository import IBulkEnrollmentRepository


class CancelBulkJobUseCase:
    """Use case for cancelling a bulk enrollment job.

    This use case marks an active job for cancellation and stops
    processing of remaining batches.
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
            job_id: Job to cancel.
            account_id: Account owning the job.

        Returns:
            Updated job with cancelled status.

        Raises:
            WorkflowNotFoundError: If job doesn't exist.
            InvalidStatusTransitionError: If job cannot be cancelled.
        """
        # Get job
        job = await self._bulk_repository.get_job_by_id(job_id, account_id)
        if job is None:
            raise WorkflowNotFoundError(f"Bulk enrollment job not found: {job_id}")

        # Check if job can be cancelled
        if job.is_terminal:
            raise InvalidStatusTransitionError(
                job.status.value,
                "cancelled",
                "Job is already in a terminal state",
            )

        # Cancel job
        job.cancel()

        # Persist changes
        updated_job = await self._bulk_repository.update_job(job)

        return BulkEnrollmentJobResponseDTO.model_validate(updated_job.to_dict())
