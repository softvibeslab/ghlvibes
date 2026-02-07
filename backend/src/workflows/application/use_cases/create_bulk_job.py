"""Use case for creating bulk enrollment jobs."""

from uuid import UUID

from src.workflows.application.bulk_enrollment_dtos import (
    BulkEnrollmentJobResponseDTO,
    CreateBulkJobRequestDTO,
)
from src.workflows.domain.bulk_enrollment_entities import (
    BulkEnrollmentJob,
    SelectionCriteria,
    SelectionType,
)
from src.workflows.domain.exceptions import ValidationError, WorkflowNotFoundError
from src.workflows.infrastructure.bulk_enrollment_repository import IBulkEnrollmentRepository
from src.workflows.infrastructure.repositories import IWorkflowRepository


class CreateBulkJobUseCase:
    """Use case for creating a new bulk enrollment job.

    This use case validates the workflow exists, validates contact selection,
    and creates a bulk enrollment job for asynchronous processing.
    """

    def __init__(
        self,
        bulk_repository: IBulkEnrollmentRepository,
        workflow_repository: IWorkflowRepository,
    ) -> None:
        """Initialize the use case.

        Args:
            bulk_repository: Repository for bulk enrollment jobs.
            workflow_repository: Repository for workflows.
        """
        self._bulk_repository = bulk_repository
        self._workflow_repository = workflow_repository

    async def execute(
        self,
        workflow_id: UUID,
        account_id: UUID,
        request_dto: CreateBulkJobRequestDTO,
        created_by: UUID,
    ) -> BulkEnrollmentJobResponseDTO:
        """Execute the use case.

        Args:
            workflow_id: Workflow to enroll contacts into.
            account_id: Account creating the job.
            request_dto: Bulk enrollment job creation request.
            created_by: User creating the job.

        Returns:
            Created bulk enrollment job.

        Raises:
            WorkflowNotFoundError: If workflow doesn't exist.
            ValidationError: If request is invalid.
        """
        # Verify workflow exists
        workflow = await self._workflow_repository.get_by_id(workflow_id, account_id)
        if workflow is None:
            raise WorkflowNotFoundError(str(workflow_id))

        # Convert selection DTO to domain
        selection_data = request_dto.selection.model_dump()

        # Determine selection type
        if request_dto.selection.type == "manual":
            selection_type = SelectionType.MANUAL
            contact_ids = selection_data.get("contact_ids", [])
            total_contacts = len(contact_ids)
            selection = SelectionCriteria(
                selection_type=selection_type,
                contact_ids=contact_ids,
            )
        elif request_dto.selection.type == "filter":
            selection_type = SelectionType.FILTER
            # TODO: Resolve filter to contact IDs
            # For now, we'll need to query contacts matching the filter
            total_contacts = 0  # Will be updated after validation
            selection = SelectionCriteria(
                selection_type=selection_type,
                filter_criteria=selection_data.get("filter"),
            )
        else:  # csv
            selection_type = SelectionType.CSV
            # TODO: Parse CSV file to get contact IDs
            total_contacts = 0  # Will be updated after parsing
            selection = SelectionCriteria(
                selection_type=selection_type,
                csv_file_url=selection_data.get("file_key"),
                identifier_column=selection_data.get("identifier_column", "email"),
            )

        # Get options
        options = request_dto.options
        batch_size = options.batch_size if options else 100
        scheduled_at = options.scheduled_at if options else None

        # Create job
        job = BulkEnrollmentJob.create(
            account_id=account_id,
            workflow_id=workflow_id,
            selection=selection,
            total_contacts=total_contacts,
            created_by=created_by,
            batch_size=batch_size,
            scheduled_at=scheduled_at,
        )

        # Persist job
        saved_job = await self._bulk_repository.create_job(job)

        return BulkEnrollmentJobResponseDTO.model_validate(saved_job.to_dict())
