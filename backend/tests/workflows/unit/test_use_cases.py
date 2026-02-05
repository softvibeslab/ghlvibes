"""Unit tests for workflow use cases.

These tests verify the application layer use cases behave correctly
with mocked dependencies.
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.workflows.application.dtos import CreateWorkflowRequest
from src.workflows.application.use_cases.create_workflow import (
    CreateWorkflowUseCase,
    DeleteWorkflowUseCase,
    GetWorkflowUseCase,
    ListWorkflowsUseCase,
    UpdateWorkflowUseCase,
)
from src.workflows.domain.entities import Workflow
from src.workflows.domain.exceptions import WorkflowAlreadyExistsError
from src.workflows.domain.value_objects import WorkflowName, WorkflowStatus


class TestCreateWorkflowUseCase:
    """Test suite for CreateWorkflowUseCase."""

    @pytest.fixture
    def mock_workflow_repo(self) -> AsyncMock:
        """Create mock workflow repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_audit_repo(self) -> AsyncMock:
        """Create mock audit log repository."""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_workflow_repo, mock_audit_repo) -> CreateWorkflowUseCase:
        """Create use case with mocked dependencies."""
        return CreateWorkflowUseCase(
            workflow_repository=mock_workflow_repo,
            audit_log_repository=mock_audit_repo,
        )

    @pytest.fixture
    def account_id(self):
        """Test account ID."""
        return uuid4()

    @pytest.fixture
    def user_id(self):
        """Test user ID."""
        return uuid4()

    @pytest.fixture
    def request_data(self) -> CreateWorkflowRequest:
        """Valid request data."""
        return CreateWorkflowRequest(
            name="Test Workflow",
            description="A test workflow",
            trigger_type="contact_created",
            trigger_config={"filters": {"tags": ["lead"]}},
        )

    @pytest.mark.asyncio
    async def test_create_workflow_success(
        self,
        use_case: CreateWorkflowUseCase,
        mock_workflow_repo: AsyncMock,
        mock_audit_repo: AsyncMock,
        request_data: CreateWorkflowRequest,
        account_id,
        user_id,
    ) -> None:
        """Test successful workflow creation."""
        # Mock no existing workflow with same name
        mock_workflow_repo.get_by_name.return_value = None

        # Mock create returns workflow
        def mock_create(workflow):
            return workflow

        mock_workflow_repo.create.side_effect = mock_create

        # Execute
        result = await use_case.execute(
            request=request_data,
            account_id=account_id,
            user_id=user_id,
        )

        # Verify
        assert result.success is True
        assert result.workflow is not None
        assert result.workflow.name == "Test Workflow"
        assert result.workflow.status == WorkflowStatus.DRAFT
        assert result.error is None

        # Verify repository calls
        mock_workflow_repo.get_by_name.assert_called_once()
        mock_workflow_repo.create.assert_called_once()
        mock_audit_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_workflow_duplicate_name(
        self,
        use_case: CreateWorkflowUseCase,
        mock_workflow_repo: AsyncMock,
        request_data: CreateWorkflowRequest,
        account_id,
        user_id,
    ) -> None:
        """Test that duplicate name raises error."""
        # Mock existing workflow with same name
        existing_workflow = Workflow.create(
            account_id=account_id,
            name="Test Workflow",
            created_by=user_id,
        )
        mock_workflow_repo.get_by_name.return_value = existing_workflow

        # Execute and expect error
        with pytest.raises(WorkflowAlreadyExistsError):
            await use_case.execute(
                request=request_data,
                account_id=account_id,
                user_id=user_id,
            )

        # Verify create was not called
        mock_workflow_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_workflow_with_audit_info(
        self,
        use_case: CreateWorkflowUseCase,
        mock_workflow_repo: AsyncMock,
        mock_audit_repo: AsyncMock,
        request_data: CreateWorkflowRequest,
        account_id,
        user_id,
    ) -> None:
        """Test that audit info is recorded."""
        mock_workflow_repo.get_by_name.return_value = None
        mock_workflow_repo.create.side_effect = lambda w: w

        ip_address = "192.168.1.1"
        user_agent = "TestAgent/1.0"

        await use_case.execute(
            request=request_data,
            account_id=account_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Verify audit log was created with IP and user agent
        mock_audit_repo.create.assert_called_once()
        call_args = mock_audit_repo.create.call_args
        assert call_args.kwargs["ip_address"] == ip_address
        assert call_args.kwargs["user_agent"] == user_agent


class TestGetWorkflowUseCase:
    """Test suite for GetWorkflowUseCase."""

    @pytest.fixture
    def mock_workflow_repo(self) -> AsyncMock:
        """Create mock workflow repository."""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_workflow_repo) -> GetWorkflowUseCase:
        """Create use case with mocked dependencies."""
        return GetWorkflowUseCase(workflow_repository=mock_workflow_repo)

    @pytest.mark.asyncio
    async def test_get_existing_workflow(self, use_case, mock_workflow_repo) -> None:
        """Test getting an existing workflow."""
        account_id = uuid4()
        user_id = uuid4()
        workflow_id = uuid4()

        workflow = Workflow.create(
            account_id=account_id,
            name="Test Workflow",
            created_by=user_id,
        )
        # Override the ID
        workflow.id = workflow_id
        mock_workflow_repo.get_by_id.return_value = workflow

        result = await use_case.execute(
            workflow_id=workflow_id,
            account_id=account_id,
        )

        assert result is not None
        assert result.name == "Test Workflow"
        mock_workflow_repo.get_by_id.assert_called_once_with(
            workflow_id=workflow_id,
            account_id=account_id,
        )

    @pytest.mark.asyncio
    async def test_get_nonexistent_workflow(self, use_case, mock_workflow_repo) -> None:
        """Test getting a workflow that doesn't exist."""
        mock_workflow_repo.get_by_id.return_value = None

        result = await use_case.execute(
            workflow_id=uuid4(),
            account_id=uuid4(),
        )

        assert result is None


class TestListWorkflowsUseCase:
    """Test suite for ListWorkflowsUseCase."""

    @pytest.fixture
    def mock_workflow_repo(self) -> AsyncMock:
        """Create mock workflow repository."""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_workflow_repo) -> ListWorkflowsUseCase:
        """Create use case with mocked dependencies."""
        return ListWorkflowsUseCase(workflow_repository=mock_workflow_repo)

    @pytest.mark.asyncio
    async def test_list_workflows(self, use_case, mock_workflow_repo) -> None:
        """Test listing workflows."""
        account_id = uuid4()
        user_id = uuid4()

        workflows = [
            Workflow.create(account_id=account_id, name=f"Workflow {i}", created_by=user_id)
            for i in range(3)
        ]

        mock_workflow_repo.list_by_account.return_value = workflows
        mock_workflow_repo.count_by_account.return_value = 3

        result, total = await use_case.execute(
            account_id=account_id,
            offset=0,
            limit=50,
        )

        assert len(result) == 3
        assert total == 3
        mock_workflow_repo.list_by_account.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_workflows_with_status_filter(
        self, use_case, mock_workflow_repo
    ) -> None:
        """Test listing workflows with status filter."""
        account_id = uuid4()

        mock_workflow_repo.list_by_account.return_value = []
        mock_workflow_repo.count_by_account.return_value = 0

        await use_case.execute(
            account_id=account_id,
            status="active",
        )

        call_args = mock_workflow_repo.list_by_account.call_args
        assert call_args.kwargs["status"] == WorkflowStatus.ACTIVE


class TestUpdateWorkflowUseCase:
    """Test suite for UpdateWorkflowUseCase."""

    @pytest.fixture
    def mock_workflow_repo(self) -> AsyncMock:
        """Create mock workflow repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_audit_repo(self) -> AsyncMock:
        """Create mock audit log repository."""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_workflow_repo, mock_audit_repo) -> UpdateWorkflowUseCase:
        """Create use case with mocked dependencies."""
        return UpdateWorkflowUseCase(
            workflow_repository=mock_workflow_repo,
            audit_log_repository=mock_audit_repo,
        )

    @pytest.mark.asyncio
    async def test_update_workflow_name(
        self, use_case, mock_workflow_repo, mock_audit_repo
    ) -> None:
        """Test updating workflow name."""
        account_id = uuid4()
        user_id = uuid4()
        workflow_id = uuid4()

        workflow = Workflow.create(
            account_id=account_id,
            name="Original Name",
            created_by=user_id,
        )
        workflow.id = workflow_id

        mock_workflow_repo.get_by_id.return_value = workflow
        mock_workflow_repo.get_by_name.return_value = None
        mock_workflow_repo.update.side_effect = lambda w: w

        result = await use_case.execute(
            workflow_id=workflow_id,
            account_id=account_id,
            user_id=user_id,
            name="Updated Name",
        )

        assert result is not None
        assert result.name == "Updated Name"
        mock_audit_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_nonexistent_workflow(
        self, use_case, mock_workflow_repo
    ) -> None:
        """Test updating a workflow that doesn't exist."""
        mock_workflow_repo.get_by_id.return_value = None

        result = await use_case.execute(
            workflow_id=uuid4(),
            account_id=uuid4(),
            user_id=uuid4(),
            name="New Name",
        )

        assert result is None


class TestDeleteWorkflowUseCase:
    """Test suite for DeleteWorkflowUseCase."""

    @pytest.fixture
    def mock_workflow_repo(self) -> AsyncMock:
        """Create mock workflow repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_audit_repo(self) -> AsyncMock:
        """Create mock audit log repository."""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_workflow_repo, mock_audit_repo) -> DeleteWorkflowUseCase:
        """Create use case with mocked dependencies."""
        return DeleteWorkflowUseCase(
            workflow_repository=mock_workflow_repo,
            audit_log_repository=mock_audit_repo,
        )

    @pytest.mark.asyncio
    async def test_delete_workflow_success(
        self, use_case, mock_workflow_repo, mock_audit_repo
    ) -> None:
        """Test successful workflow deletion."""
        account_id = uuid4()
        user_id = uuid4()
        workflow_id = uuid4()

        workflow = Workflow.create(
            account_id=account_id,
            name="To Delete",
            created_by=user_id,
        )
        workflow.id = workflow_id

        mock_workflow_repo.get_by_id.return_value = workflow
        mock_workflow_repo.delete.return_value = True

        result = await use_case.execute(
            workflow_id=workflow_id,
            account_id=account_id,
            user_id=user_id,
        )

        assert result is True
        mock_workflow_repo.delete.assert_called_once()
        mock_audit_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_nonexistent_workflow(
        self, use_case, mock_workflow_repo
    ) -> None:
        """Test deleting a workflow that doesn't exist."""
        mock_workflow_repo.get_by_id.return_value = None

        result = await use_case.execute(
            workflow_id=uuid4(),
            account_id=uuid4(),
            user_id=uuid4(),
        )

        assert result is False
