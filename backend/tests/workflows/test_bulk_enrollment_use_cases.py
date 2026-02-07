"""Unit tests for bulk enrollment use cases."""

from uuid import UUID, uuid4

import pytest

from src.workflows.application.bulk_enrollment_dtos import (
    BulkEnrollmentOptionsDTO,
    CreateBulkJobRequestDTO,
    ManualSelectionDTO,
)
from src.workflows.application.use_cases.create_bulk_job import CreateBulkJobUseCase
from src.workflows.application.use_cases.cancel_bulk_job import CancelBulkJobUseCase
from src.workflows.domain.bulk_enrollment_entities import (
    BulkEnrollmentJob,
    JobStatus,
    SelectionCriteria,
    SelectionType,
)
from src.workflows.domain.exceptions import WorkflowNotFoundError


class TestCreateBulkJobUseCase:
    """Test suite for CreateBulkJobUseCase."""

    @pytest.mark.asyncio
    async def test_create_bulk_job_success(self, bulk_repository, workflow_repository):
        """Test successful bulk job creation."""
        # Arrange
        account_id = uuid4()
        workflow_id = uuid4()
        created_by = uuid4()

        # Mock workflow exists
        workflow_repository.get_by_id.return_value = mock_workflow(id=workflow_id)

        request_dto = CreateBulkJobRequestDTO(
            selection=ManualSelectionDTO(
                type="manual",
                contact_ids=[uuid4() for _ in range(100)],
            ),
            options=BulkEnrollmentOptionsDTO(
                batch_size=100,
                skip_duplicates=True,
            ),
        )
        use_case = CreateBulkJobUseCase(
            bulk_repository=bulk_repository,
            workflow_repository=workflow_repository,
        )

        # Act
        result = await use_case.execute(
            workflow_id=workflow_id,
            account_id=account_id,
            request_dto=request_dto,
            created_by=created_by,
        )

        # Assert
        assert result.workflow_id == workflow_id
        assert result.selection_type == "manual"
        assert result.total_contacts == 100
        assert result.batch_size == 100
        assert result.status == "pending"

    @pytest.mark.asyncio
    async def test_create_bulk_job_workflow_not_found(
        self, bulk_repository, workflow_repository
    ):
        """Test bulk job creation with non-existent workflow."""
        # Arrange
        account_id = uuid4()
        workflow_id = uuid4()
        created_by = uuid4()

        workflow_repository.get_by_id.return_value = None

        request_dto = CreateBulkJobRequestDTO(
            selection=ManualSelectionDTO(
                type="manual",
                contact_ids=[uuid4() for _ in range(10)],
            )
        )
        use_case = CreateBulkJobUseCase(
            bulk_repository=bulk_repository,
            workflow_repository=workflow_repository,
        )

        # Act & Assert
        with pytest.raises(WorkflowNotFoundError):
            await use_case.execute(
                workflow_id=workflow_id,
                account_id=account_id,
                request_dto=request_dto,
                created_by=created_by,
            )

    @pytest.mark.asyncio
    async def test_create_bulk_job_exceeds_limit(self, bulk_repository, workflow_repository):
        """Test bulk job creation exceeding contact limit."""
        # Arrange
        account_id = uuid4()
        workflow_id = uuid4()
        created_by = uuid4()

        workflow_repository.get_by_id.return_value = mock_workflow(id=workflow_id)

        request_dto = CreateBulkJobRequestDTO(
            selection=ManualSelectionDTO(
                type="manual",
                contact_ids=[uuid4() for _ in range(10001)],  # Exceeds 10,000 limit
            )
        )
        use_case = CreateBulkJobUseCase(
            bulk_repository=bulk_repository,
            workflow_repository=workflow_repository,
        )

        # Act & Assert
        with pytest.raises(Exception):  # ValidationError from SelectionCriteria
            await use_case.execute(
                workflow_id=workflow_id,
                account_id=account_id,
                request_dto=request_dto,
                created_by=created_by,
            )


class TestCancelBulkJobUseCase:
    """Test suite for CancelBulkJobUseCase."""

    @pytest.mark.asyncio
    async def test_cancel_job_success(self, bulk_repository):
        """Test successful job cancellation."""
        # Arrange
        account_id = uuid4()
        job_id = uuid4()

        job = BulkEnrollmentJob.create(
            account_id=account_id,
            workflow_id=uuid4(),
            selection=SelectionCriteria(
                selection_type=SelectionType.MANUAL,
                contact_ids=[uuid4() for _ in range(100)],
            ),
            total_contacts=100,
            created_by=uuid4(),
        )
        job.id = job_id
        job.start_processing()  # Move to processing state

        bulk_repository.get_job_by_id.return_value = job
        bulk_repository.update_job.return_value = job

        use_case = CancelBulkJobUseCase(bulk_repository=bulk_repository)

        # Act
        result = await use_case.execute(
            job_id=job_id,
            account_id=account_id,
        )

        # Assert
        assert result.status == "cancelled"
        assert result.is_terminal

    @pytest.mark.asyncio
    async def test_cancel_job_not_found(self, bulk_repository):
        """Test cancelling non-existent job."""
        # Arrange
        account_id = uuid4()
        job_id = uuid4()
        bulk_repository.get_job_by_id.return_value = None

        use_case = CancelBulkJobUseCase(bulk_repository=bulk_repository)

        # Act & Assert
        with pytest.raises(Exception):  # WorkflowNotFoundError
            await use_case.execute(
                job_id=job_id,
                account_id=account_id,
            )

    @pytest.mark.asyncio
    async def test_cancel_job_already_completed(self, bulk_repository):
        """Test cancelling job that's already completed."""
        # Arrange
        account_id = uuid4()
        job_id = uuid4()

        job = BulkEnrollmentJob.create(
            account_id=account_id,
            workflow_id=uuid4(),
            selection=SelectionCriteria(
                selection_type=SelectionType.MANUAL,
                contact_ids=[uuid4() for _ in range(100)],
            ),
            total_contacts=100,
            created_by=uuid4(),
        )
        job.id = job_id
        job.complete()  # Already in terminal state

        bulk_repository.get_job_by_id.return_value = job

        use_case = CancelBulkJobUseCase(bulk_repository=bulk_repository)

        # Act & Assert
        with pytest.raises(Exception):  # InvalidStatusTransitionError
            await use_case.execute(
                job_id=job_id,
                account_id=account_id,
            )


# Helper functions and fixtures


def mock_workflow(**kwargs):
    """Create a mock workflow object."""
    class MockWorkflow:
        def __init__(self, **kwargs):
            self.id = kwargs.get("id", uuid4())
            self.account_id = kwargs.get("account_id", uuid4())
            self.name = kwargs.get("name", "Test Workflow")
            self.status = kwargs.get("status", "active")

    return MockWorkflow(**kwargs)


@pytest.fixture
def bulk_repository(mocker):
    """Fixture for mocked bulk enrollment repository."""
    return mocker.AsyncMock()


@pytest.fixture
def workflow_repository(mocker):
    """Fixture for mocked workflow repository."""
    return mocker.AsyncMock()
