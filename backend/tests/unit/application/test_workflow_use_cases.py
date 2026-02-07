"""
Comprehensive unit tests for Workflow use cases.

This test suite covers the application layer use cases including
CreateWorkflow, UpdateWorkflow, DeleteWorkflow, ExecuteWorkflow, etc.
"""

import pytest
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, Mock

from src.workflows.application.use_cases.create_workflow import CreateWorkflowUseCase
from src.workflows.application.use_cases.update_workflow import UpdateWorkflowUseCase
from src.workflows.application.use_cases.delete_workflow import DeleteWorkflowUseCase
from src.workflows.application.use_cases.execute_workflow import ExecuteWorkflowUseCase
from src.workflows.application.use_cases.list_workflows import ListWorkflowsUseCase
from src.workflows.domain.entities import Workflow
from src.workflows.domain.value_objects import WorkflowName, TriggerType
from src.workflows.domain.exceptions import (
    WorkflowNotFoundError,
    InvalidWorkflowNameError,
    DuplicateWorkflowNameError,
)


class TestCreateWorkflowUseCase:
    """Test suite for CreateWorkflow use case."""

    @pytest.mark.asyncio
    async def test_create_workflow_with_valid_data(self):
        """Given valid data, when creating workflow, then workflow created."""
        # Arrange
        mock_repository = AsyncMock()
        use_case = CreateWorkflowUseCase(mock_repository)
        workflow_id = uuid4()
        account_id = uuid4()

        request = {
            "workflow_id": workflow_id,
            "account_id": account_id,
            "name": "Test Workflow",
            "description": "Test description",
            "trigger_type": "webhook",
        }

        mock_workflow = Mock(id=workflow_id, name="Test Workflow")
        mock_repository.create.return_value = mock_workflow
        mock_repository.name_exists.return_value = False

        # Act
        result = await use_case.execute(request)

        # Assert
        assert result.id == workflow_id
        mock_repository.create.assert_called_once()
        mock_repository.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_workflow_duplicate_name_rejected(self):
        """Given duplicate name, when creating, then raises exception."""
        # Arrange
        mock_repository = AsyncMock()
        use_case = CreateWorkflowUseCase(mock_repository)
        account_id = uuid4()

        request = {
            "account_id": account_id,
            "name": "Duplicate Workflow",
        }

        mock_repository.name_exists.return_value = True

        # Act & Assert
        with pytest.raises(DuplicateWorkflowNameError):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_create_workflow_invalid_name_rejected(self):
        """Given invalid name, when creating, then raises exception."""
        # Arrange
        mock_repository = AsyncMock()
        use_case = CreateWorkflowUseCase(mock_repository)
        account_id = uuid4()

        request = {
            "account_id": account_id,
            "name": "ab",  # Too short
        }

        # Act & Assert
        with pytest.raises(InvalidWorkflowNameError):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_create_workflow_with_trigger(self):
        """Given workflow with trigger, when creating, then trigger created."""
        # Arrange
        mock_repository = AsyncMock()
        mock_trigger_repository = AsyncMock()
        use_case = CreateWorkflowUseCase(mock_repository, mock_trigger_repository)
        workflow_id = uuid4()
        account_id = uuid4()

        request = {
            "workflow_id": workflow_id,
            "account_id": account_id,
            "name": "Workflow with Trigger",
            "trigger_type": "webhook",
            "trigger_config": {"webhook_url": "/webhooks/test"}
        }

        mock_workflow = Mock(id=workflow_id)
        mock_repository.create.return_value = mock_workflow
        mock_repository.name_exists.return_value = False

        # Act
        result = await use_case.execute(request)

        # Assert
        assert result.id == workflow_id
        mock_trigger_repository.create.assert_called_once()


class TestUpdateWorkflowUseCase:
    """Test suite for UpdateWorkflow use case."""

    @pytest.mark.asyncio
    async def test_update_workflow_name(self):
        """Given workflow, when updating name, then name updated."""
        # Arrange
        mock_repository = AsyncMock()
        use_case = UpdateWorkflowUseCase(mock_repository)
        workflow_id = uuid4()

        existing_workflow = Mock(id=workflow_id, name="Old Name")
        mock_repository.get_by_id.return_value = existing_workflow
        mock_repository.name_exists.return_value = False

        request = {
            "workflow_id": workflow_id,
            "name": "New Name",
        }

        # Act
        result = await use_case.execute(request)

        # Assert
        assert result.name == "New Name"
        mock_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_workflow_not_found(self):
        """Given non-existent workflow, when updating, then raises exception."""
        # Arrange
        mock_repository = AsyncMock()
        use_case = UpdateWorkflowUseCase(mock_repository)
        workflow_id = uuid4()

        mock_repository.get_by_id.return_value = None

        request = {
            "workflow_id": workflow_id,
            "name": "Updated Name",
        }

        # Act & Assert
        with pytest.raises(WorkflowNotFoundError):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_update_active_workflow_increments_version(self):
        """Given active workflow, when updating, then version increments."""
        # Arrange
        mock_repository = AsyncMock()
        use_case = UpdateWorkflowUseCase(mock_repository)
        workflow_id = uuid4()

        existing_workflow = Mock(
            id=workflow_id,
            name="Old Name",
            status="active",
            version=1
        )
        mock_repository.get_by_id.return_value = existing_workflow
        mock_repository.name_exists.return_value = False

        request = {
            "workflow_id": workflow_id,
            "name": "New Name",
        }

        # Act
        result = await use_case.execute(request)

        # Assert
        assert result.version == 2


class TestDeleteWorkflowUseCase:
    """Test suite for DeleteWorkflow use case."""

    @pytest.mark.asyncio
    async def test_delete_workflow_success(self):
        """Given draft workflow, when deleting, then workflow deleted."""
        # Arrange
        mock_repository = AsyncMock()
        use_case = DeleteWorkflowUseCase(mock_repository)
        workflow_id = uuid4()

        existing_workflow = Mock(
            id=workflow_id,
            status="draft"
        )
        mock_repository.get_by_id.return_value = existing_workflow

        request = {
            "workflow_id": workflow_id,
        }

        # Act
        await use_case.execute(request)

        # Assert
        mock_repository.delete.assert_called_once_with(workflow_id)

    @pytest.mark.asyncio
    async def test_delete_active_workflow_rejected(self):
        """Given active workflow, when deleting, then raises exception."""
        # Arrange
        mock_repository = AsyncMock()
        use_case = DeleteWorkflowUseCase(mock_repository)
        workflow_id = uuid4()

        existing_workflow = Mock(
            id=workflow_id,
            status="active"
        )
        mock_repository.get_by_id.return_value = existing_workflow

        request = {
            "workflow_id": workflow_id,
        }

        # Act & Assert
        with pytest.raises(InvalidWorkflowStatusError):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_delete_workflow_not_found(self):
        """Given non-existent workflow, when deleting, then raises exception."""
        # Arrange
        mock_repository = AsyncMock()
        use_case = DeleteWorkflowUseCase(mock_repository)
        workflow_id = uuid4()

        mock_repository.get_by_id.return_value = None

        request = {
            "workflow_id": workflow_id,
        }

        # Act & Assert
        with pytest.raises(WorkflowNotFoundError):
            await use_case.execute(request)


class TestExecuteWorkflowUseCase:
    """Test suite for ExecuteWorkflow use case."""

    @pytest.mark.asyncio
    async def test_execute_workflow_success(self):
        """Given active workflow, when executing, then workflow executed."""
        # Arrange
        mock_repository = AsyncMock()
        mock_executor = AsyncMock()
        use_case = ExecuteWorkflowUseCase(mock_repository, mock_executor)
        workflow_id = uuid4()
        contact_id = uuid4()

        workflow = Mock(
            id=workflow_id,
            status="active",
            trigger_type=TriggerType.MANUAL
        )
        mock_repository.get_by_id.return_value = workflow

        request = {
            "workflow_id": workflow_id,
            "contact_id": contact_id,
            "trigger_data": {},
        }

        mock_executor.execute.return_value = Mock(
            execution_id=uuid4(),
            status="completed"
        )

        # Act
        result = await use_case.execute(request)

        # Assert
        assert result.status == "completed"
        mock_executor.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_draft_workflow_rejected(self):
        """Given draft workflow, when executing, then raises exception."""
        # Arrange
        mock_repository = AsyncMock()
        mock_executor = AsyncMock()
        use_case = ExecuteWorkflowUseCase(mock_repository, mock_executor)
        workflow_id = uuid4()

        workflow = Mock(
            id=workflow_id,
            status="draft"
        )
        mock_repository.get_by_id.return_value = workflow

        request = {
            "workflow_id": workflow_id,
            "contact_id": uuid4(),
        }

        # Act & Assert
        with pytest.raises(InvalidWorkflowStatusError):
            await use_case.execute(request)


class TestListWorkflowsUseCase:
    """Test suite for ListWorkflows use case."""

    @pytest.mark.asyncio
    async def test_list_workflows_default_pagination(self):
        """Given account with workflows, when listing, then returns paginated results."""
        # Arrange
        mock_repository = AsyncMock()
        use_case = ListWorkflowsUseCase(mock_repository)
        account_id = uuid4()

        workflows = [
            Mock(id=uuid4(), name=f"Workflow {i}"),
            Mock(id=uuid4(), name=f"Workflow {i}"),
            Mock(id=uuid4(), name=f"Workflow {i}"),
        ]
        mock_repository.list.return_value = workflows
        mock_repository.count.return_value = 3

        request = {
            "account_id": account_id,
        }

        # Act
        result = await use_case.execute(request)

        # Assert
        assert len(result.workflows) == 3
        assert result.total_count == 3
        mock_repository.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_workflows_with_filters(self):
        """Given filter criteria, when listing, then returns filtered results."""
        # Arrange
        mock_repository = AsyncMock()
        use_case = ListWorkflowsUseCase(mock_repository)
        account_id = uuid4()

        workflows = [Mock(id=uuid4(), status="active")]
        mock_repository.list.return_value = workflows
        mock_repository.count.return_value = 1

        request = {
            "account_id": account_id,
            "status": "active",
            "trigger_type": "webhook",
        }

        # Act
        result = await use_case.execute(request)

        # Assert
        assert len(result.workflows) == 1
        assert result.workflows[0].status == "active"

    @pytest.mark.asyncio
    async def test_list_workflows_custom_pagination(self):
        """Given custom pagination, when listing, then applies pagination."""
        # Arrange
        mock_repository = AsyncMock()
        use_case = ListWorkflowsUseCase(mock_repository)
        account_id = uuid4()

        workflows = [Mock(id=uuid4())]
        mock_repository.list.return_value = workflows
        mock_repository.count.return_value = 1

        request = {
            "account_id": account_id,
            "page": 2,
            "page_size": 50,
        }

        # Act
        result = await use_case.execute(request)

        # Assert
        assert len(result.workflows) == 1
        mock_repository.list.assert_called_once_with(
            account_id=account_id,
            offset=50,
            limit=50
        )


class TestWorkflowUseCaseIntegration:
    """Integration tests for workflow use cases."""

    @pytest.mark.asyncio
    async def test_create_and_execute_workflow_flow(self):
        """Given use cases, when creating then executing, then flow succeeds."""
        # This would be an integration test with real repositories
        # Placeholder for demonstrating use case composition
        pass

    @pytest.mark.asyncio
    async def test_update_and_activate_workflow_flow(self):
        """Given use cases, when updating then activating, then flow succeeds."""
        # Placeholder for demonstrating use case composition
        pass


# Import missing exceptions
from src.workflows.domain.exceptions import InvalidWorkflowStatusError
