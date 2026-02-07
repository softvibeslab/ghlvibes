"""FastAPI routes for bulk enrollment endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.workflows.application.bulk_enrollment_dtos import (
    BulkEnrollmentJobResponseDTO,
    BulkEnrollmentProgressDTO,
    CreateBulkJobRequestDTO,
    ListBulkJobsRequestDTO,
    ListBulkJobsResponseDTO,
)
from src.workflows.application.use_cases.cancel_bulk_job import CancelBulkJobUseCase
from src.workflows.application.use_cases.create_bulk_job import CreateBulkJobUseCase
from src.workflows.application.use_cases.get_job_status import GetJobStatusUseCase
from src.workflows.application.use_cases.list_bulk_jobs import ListBulkJobsUseCase
from src.workflows.presentation.dependencies import get_current_user_id

router = APIRouter(prefix="/api/v1/bulk-enrollment", tags=["bulk-enrollment"])


@router.post(
    "/workflows/{workflow_id}/jobs",
    response_model=BulkEnrollmentJobResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create bulk enrollment job",
    description="Initiate bulk enrollment of contacts into a workflow.",
)
async def create_bulk_job(
    workflow_id: UUID,
    request_dto: CreateBulkJobRequestDTO,
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
    current_user_id: UUID = Depends(get_current_user_id),  # noqa: B008
    create_bulk_job_uc: CreateBulkJobUseCase = Depends(CreateBulkJobUseCase),  # noqa: B008
) -> BulkEnrollmentJobResponseDTO:
    """Create a new bulk enrollment job.

    Args:
        workflow_id: Workflow to enroll contacts into.
        request_dto: Bulk enrollment job creation request.
        account_id: Account creating the job.
        current_user_id: User creating the job.
        create_bulk_job_uc: Create bulk job use case.

    Returns:
        Created bulk enrollment job.
    """
    return await create_bulk_job_uc.execute(
        workflow_id=workflow_id,
        account_id=account_id,
        request_dto=request_dto,
        created_by=current_user_id,
    )


@router.get(
    "/jobs",
    response_model=ListBulkJobsResponseDTO,
    summary="List bulk enrollment jobs",
    description="Retrieve all bulk enrollment jobs with filtering and pagination.",
)
async def list_bulk_jobs(
    workflow_id: UUID | None = None,
    status: str | None = None,
    offset: int = 0,
    limit: int = 50,
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
    list_bulk_jobs_uc: ListBulkJobsUseCase = Depends(ListBulkJobsUseCase),  # noqa: B008
) -> ListBulkJobsResponseDTO:
    """List all bulk enrollment jobs.

    Args:
        workflow_id: Filter by workflow.
        status: Filter by job status.
        offset: Pagination offset.
        limit: Maximum results to return.
        account_id: Account to list jobs for.
        list_bulk_jobs_uc: List bulk jobs use case.

    Returns:
        Paginated list of bulk enrollment jobs.
    """
    request_dto = ListBulkJobsRequestDTO(
        workflow_id=workflow_id,
        status=status,
        offset=offset,
        limit=limit,
    )
    return await list_bulk_jobs_uc.execute(
        account_id=account_id,
        request_dto=request_dto,
    )


@router.get(
    "/jobs/{job_id}",
    response_model=BulkEnrollmentJobResponseDTO,
    summary="Get bulk enrollment job details",
    description="Retrieve detailed information about a specific bulk enrollment job.",
)
async def get_bulk_job(
    job_id: UUID,
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
    get_job_status_uc: GetJobStatusUseCase = Depends(GetJobStatusUseCase),  # noqa: B008
) -> BulkEnrollmentJobResponseDTO:
    """Get a specific bulk enrollment job by ID.

    Args:
        job_id: Job ID.
        account_id: Account owning the job.
        get_job_status_uc: Get job status use case.

    Returns:
        Bulk enrollment job details.

    Raises:
        HTTPException: If job not found (404).
    """
    return await get_job_status_uc.execute(
        job_id=job_id,
        account_id=account_id,
    )


@router.get(
    "/jobs/{job_id}/progress",
    response_model=BulkEnrollmentProgressDTO,
    summary="Get job progress",
    description="Retrieve real-time progress metrics for a bulk enrollment job.",
)
async def get_job_progress(
    job_id: UUID,
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
    get_job_status_uc: GetJobStatusUseCase = Depends(GetJobStatusUseCase),  # noqa: B008
) -> BulkEnrollmentProgressDTO:
    """Get real-time progress for a bulk enrollment job.

    Args:
        job_id: Job ID.
        account_id: Account owning the job.
        get_job_status_uc: Get job status use case.

    Returns:
        Real-time progress metrics.
    """
    return await get_job_status_uc.get_progress(
        job_id=job_id,
        account_id=account_id,
    )


@router.post(
    "/jobs/{job_id}/cancel",
    response_model=BulkEnrollmentJobResponseDTO,
    summary="Cancel bulk enrollment job",
    description="Cancel an active bulk enrollment job.",
)
async def cancel_bulk_job(
    job_id: UUID,
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
    cancel_bulk_job_uc: CancelBulkJobUseCase = Depends(CancelBulkJobUseCase),  # noqa: B008
) -> BulkEnrollmentJobResponseDTO:
    """Cancel a bulk enrollment job.

    Args:
        job_id: Job to cancel.
        account_id: Account owning the job.
        cancel_bulk_job_uc: Cancel bulk job use case.

    Returns:
        Updated job with cancelled status.
    """
    return await cancel_bulk_job_uc.execute(
        job_id=job_id,
        account_id=account_id,
    )


@router.get(
    "/jobs/{job_id}/failures",
    summary="Get job failures",
    description="Retrieve detailed failure information for a bulk enrollment job.",
)
async def get_job_failures(
    job_id: UUID,
    offset: int = 0,
    limit: int = 50,
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
) -> dict:
    """Get failures for a bulk enrollment job.

    Args:
        job_id: Job ID.
        offset: Pagination offset.
        limit: Maximum results to return.
        account_id: Account owning the job.

    Returns:
        Paginated list of enrollment failures.

    Raises:
        HTTPException: If job not found (404).
    """
    # TODO: Implement GetJobFailuresUseCase
    raise NotImplementedError("GetJobFailuresUseCase not yet implemented")
