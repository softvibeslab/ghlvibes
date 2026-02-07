"""Use case for listing bulk enrollment jobs."""

from uuid import UUID

from src.workflows.application.bulk_enrollment_dtos import (
    BulkEnrollmentJobResponseDTO,
    ListBulkJobsRequestDTO,
    ListBulkJobsResponseDTO,
)
from src.workflows.infrastructure.bulk_enrollment_repository import IBulkEnrollmentRepository


class ListBulkJobsUseCase:
    """Use case for listing bulk enrollment jobs.

    This use case retrieves jobs with filtering and pagination.
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
        account_id: UUID,
        request_dto: ListBulkJobsRequestDTO,
    ) -> ListBulkJobsResponseDTO:
        """Execute the use case.

        Args:
            account_id: Account to list jobs for.
            request_dto: List request with filters.

        Returns:
            Paginated list of bulk enrollment jobs.
        """
        jobs, total = await self._bulk_repository.list_jobs(
            account_id=account_id,
            workflow_id=request_dto.workflow_id,
            status=request_dto.status,
            offset=request_dto.offset,
            limit=request_dto.limit,
        )

        job_dtos = [BulkEnrollmentJobResponseDTO.model_validate(job.to_dict()) for job in jobs]

        return ListBulkJobsResponseDTO(
            jobs=job_dtos,
            total=total,
            offset=request_dto.offset,
            limit=request_dto.limit,
        )
