"""Characterization tests for CreateWorkflowUseCase behavior.

These tests document the CURRENT ACTUAL BEHAVIOR of the CreateWorkflowUseCase.
They serve as a safety net during refactoring.

IMPORTANT: These tests capture what the code DOES, not what it SHOULD DO.
If a test fails, either:
1. You broke existing behavior (bad)
2. Behavior changed intentionally (update test to document new behavior)

Generated during DDD PRESERVE phase for SPEC-WFL-001.
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.workflows.application.dtos import CreateWorkflowRequest
from src.workflows.application.use_cases.create_workflow import (
    CreateWorkflowResult,
    CreateWorkflowUseCase,
)
from src.workflows.domain.entities import Workflow
from src.workflows.domain.exceptions import WorkflowAlreadyExistsError
from src.workflows.domain.value_objects import WorkflowStatus


class TestCharacterizeCreateWorkflowUseCaseSuccessPath:
    """Characterize successful workflow creation behavior."""

    @pytest.mark.asyncio
    async def test_characterize_successful_workflow_creation_flow(self) -> None:
        """Document: Successful creation follows exact sequence of operations."""
        # Arrange
        account_id = uuid4()
        user_id = uuid4()
        request = CreateWorkflowRequest(
            name="Test Workflow",
            description="Test description",
            trigger_type="contact_created",
            trigger_config={"filters": {"tags": ["lead"]}},
        )

        mock_workflow_repo = AsyncMock()
        mock_audit_repo = AsyncMock()

        # Document: Repository behavior expectations
        mock_workflow_repo.get_by_name.return_value = None  # No duplicate

        # Document: Create returns the workflow unchanged
        def mock_create(workflow: Workflow) -> Workflow:
            return workflow

        mock_workflow_repo.create.side_effect = mock_create

        use_case = CreateWorkflowUseCase(
            workflow_repository=mock_workflow_repo,
            audit_log_repository=mock_audit_repo,
        )

        # Act
        result = await use_case.execute(
            request=request,
            account_id=account_id,
            user_id=user_id,
        )

        # Assert: Result structure
        assert isinstance(result, CreateWorkflowResult)
        assert result.success is True
        assert result.workflow is not None
        assert result.error is None

        # Assert: Workflow data in result
        assert result.workflow.name == "Test Workflow"
        assert result.workflow.description == "Test description"
        assert result.workflow.trigger_type == "contact_created"
        assert result.workflow.trigger_config == {"filters": {"tags": ["lead"]}}
        assert result.workflow.status == WorkflowStatus.DRAFT
        assert result.workflow.version == 1

        # Assert: Repository call sequence
        mock_workflow_repo.get_by_name.assert_called_once()
        call_args = mock_workflow_repo.get_by_name.call_args
        assert call_args.kwargs["name"] == "Test Workflow"
        assert call_args.kwargs["account_id"] == account_id

        mock_workflow_repo.create.assert_called_once()
        created_workflow = mock_workflow_repo.create.call_args.args[0]
        assert isinstance(created_workflow, Workflow)
        assert str(created_workflow.name) == "Test Workflow"

        # Assert: Audit log was created
        mock_audit_repo.create.assert_called_once()
        audit_call = mock_audit_repo.create.call_args
        assert audit_call.kwargs["workflow_id"] == result.workflow.id
        assert audit_call.kwargs["action"] == "created"
        assert audit_call.kwargs["changed_by"] == user_id
        assert audit_call.kwargs["new_values"] is not None

    @pytest.mark.asyncio
    async def test_characterize_minimal_workflow_creation(self) -> None:
        """Document: Creation with minimal required fields works correctly."""
        account_id = uuid4()
        user_id = uuid4()
        request = CreateWorkflowRequest(name="Minimal Workflow")

        mock_workflow_repo = AsyncMock()
        mock_audit_repo = AsyncMock()
        mock_workflow_repo.get_by_name.return_value = None
        mock_workflow_repo.create.side_effect = lambda w: w

        use_case = CreateWorkflowUseCase(
            workflow_repository=mock_workflow_repo,
            audit_log_repository=mock_audit_repo,
        )

        result = await use_case.execute(
            request=request,
            account_id=account_id,
            user_id=user_id,
        )

        # Assert: Minimal data creates valid workflow
        assert result.success is True
        assert result.workflow.name == "Minimal Workflow"
        assert result.workflow.description is None
        assert result.workflow.trigger_type is None
        assert result.workflow.trigger_config == {}


class TestCharacterizeCreateWorkflowUseCaseDuplicateHandling:
    """Characterize duplicate name detection behavior."""

    @pytest.mark.asyncio
    async def test_characterize_duplicate_name_raises_error(self) -> None:
        """Document: Duplicate name raises WorkflowAlreadyExistsError."""
        account_id = uuid4()
        user_id = uuid4()
        request = CreateWorkflowRequest(name="Duplicate Name")

        existing_workflow = Workflow.create(
            account_id=account_id,
            name="Duplicate Name",
            created_by=user_id,
        )

        mock_workflow_repo = AsyncMock()
        mock_audit_repo = AsyncMock()

        # Document: Repository returns existing workflow
        mock_workflow_repo.get_by_name.return_value = existing_workflow

        use_case = CreateWorkflowUseCase(
            workflow_repository=mock_workflow_repo,
            audit_log_repository=mock_audit_repo,
        )

        # Act & Assert
        with pytest.raises(WorkflowAlreadyExistsError) as exc_info:
            await use_case.execute(
                request=request,
                account_id=account_id,
                user_id=user_id,
            )

        # Assert: Error contains relevant information
        assert "Duplicate Name" in str(exc_info.value)
        assert str(account_id) in str(exc_info.value)

        # Assert: Create was never called
        mock_workflow_repo.create.assert_not_called()

        # Assert: Audit log was not created
        mock_audit_repo.create.assert_not_called()


class TestCharacterizeCreateWorkflowUseCaseAuditLogging:
    """Characterize audit logging behavior."""

    @pytest.mark.asyncio
    async def test_characterize_audit_log_includes_metadata(self) -> None:
        """Document: Audit log includes IP address and user agent when provided."""
        account_id = uuid4()
        user_id = uuid4()
        request = CreateWorkflowRequest(name="Audit Test")

        mock_workflow_repo = AsyncMock()
        mock_audit_repo = AsyncMock()
        mock_workflow_repo.get_by_name.return_value = None
        mock_workflow_repo.create.side_effect = lambda w: w

        use_case = CreateWorkflowUseCase(
            workflow_repository=mock_workflow_repo,
            audit_log_repository=mock_audit_repo,
        )

        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0 Test Browser"

        await use_case.execute(
            request=request,
            account_id=account_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Assert: Audit log includes metadata
        audit_call = mock_audit_repo.create.call_args
        assert audit_call.kwargs["ip_address"] == ip_address
        assert audit_call.kwargs["user_agent"] == user_agent

    @pytest.mark.asyncio
    async def test_characterize_audit_log_without_metadata(self) -> None:
        """Document: Audit log works without IP and user agent."""
        account_id = uuid4()
        user_id = uuid4()
        request = CreateWorkflowRequest(name="No Metadata Test")

        mock_workflow_repo = AsyncMock()
        mock_audit_repo = AsyncMock()
        mock_workflow_repo.get_by_name.return_value = None
        mock_workflow_repo.create.side_effect = lambda w: w

        use_case = CreateWorkflowUseCase(
            workflow_repository=mock_workflow_repo,
            audit_log_repository=mock_audit_repo,
        )

        await use_case.execute(
            request=request,
            account_id=account_id,
            user_id=user_id,
        )

        # Assert: Audit log created even without metadata
        mock_audit_repo.create.assert_called_once()
        audit_call = mock_audit_repo.create.call_args
        assert audit_call.kwargs["ip_address"] is None
        assert audit_call.kwargs["user_agent"] is None

    @pytest.mark.asyncio
    async def test_characterize_audit_log_contains_workflow_snapshot(self) -> None:
        """Document: Audit log contains full workflow state in new_values."""
        account_id = uuid4()
        user_id = uuid4()
        request = CreateWorkflowRequest(
            name="Snapshot Test",
            description="Full workflow",
            trigger_type="test",
            trigger_config={"key": "value"},
        )

        mock_workflow_repo = AsyncMock()
        mock_audit_repo = AsyncMock()
        mock_workflow_repo.get_by_name.return_value = None
        mock_workflow_repo.create.side_effect = lambda w: w

        use_case = CreateWorkflowUseCase(
            workflow_repository=mock_workflow_repo,
            audit_log_repository=mock_audit_repo,
        )

        await use_case.execute(
            request=request,
            account_id=account_id,
            user_id=user_id,
        )

        # Assert: new_values contains complete workflow state
        audit_call = mock_audit_repo.create.call_args
        new_values = audit_call.kwargs["new_values"]
        assert isinstance(new_values, dict)
        assert "id" in new_values
        assert "name" in new_values
        assert new_values["name"] == "Snapshot Test"
        assert new_values["description"] == "Full workflow"
        assert new_values["trigger_type"] == "test"
        assert new_values["trigger_config"] == {"key": "value"}
        assert new_values["status"] == "draft"
        assert "created_at" in new_values
        assert "updated_at" in new_values


class TestCharacterizeCreateWorkflowUseCaseErrorHandling:
    """Characterize error handling behavior."""

    @pytest.mark.asyncio
    async def test_characterize_domain_exception_propagates(self) -> None:
        """Document: Domain exceptions propagate without modification."""
        from src.workflows.domain.exceptions import InvalidWorkflowNameError

        account_id = uuid4()
        user_id = uuid4()

        # Invalid name will raise domain exception during entity creation
        request = CreateWorkflowRequest(name="ab")  # Too short

        mock_workflow_repo = AsyncMock()
        mock_audit_repo = AsyncMock()
        mock_workflow_repo.get_by_name.return_value = None

        use_case = CreateWorkflowUseCase(
            workflow_repository=mock_workflow_repo,
            audit_log_repository=mock_audit_repo,
        )

        # Act & Assert: Exception propagates
        with pytest.raises(InvalidWorkflowNameError):
            await use_case.execute(
                request=request,
                account_id=account_id,
                user_id=user_id,
            )

        # Assert: No audit log created for failed attempt
        mock_audit_repo.create.assert_not_called()


class TestCharacterizeCreateWorkflowUseCaseRepositoryInteraction:
    """Characterize repository interaction patterns."""

    @pytest.mark.asyncio
    async def test_characterize_duplicate_check_called_before_create(self) -> None:
        """Document: Duplicate check always happens before create."""
        account_id = uuid4()
        user_id = uuid4()
        request = CreateWorkflowRequest(name="Order Test")

        call_order = []

        mock_workflow_repo = AsyncMock()

        async def mock_get_by_name(*args, **kwargs):
            call_order.append("get_by_name")
            return None

        async def mock_create(*args, **kwargs):
            call_order.append("create")
            return args[0]

        mock_workflow_repo.get_by_name.side_effect = mock_get_by_name
        mock_workflow_repo.create.side_effect = mock_create

        mock_audit_repo = AsyncMock()

        use_case = CreateWorkflowUseCase(
            workflow_repository=mock_workflow_repo,
            audit_log_repository=mock_audit_repo,
        )

        await use_case.execute(
            request=request,
            account_id=account_id,
            user_id=user_id,
        )

        # Assert: get_by_name called before create
        assert call_order == ["get_by_name", "create"]

    @pytest.mark.asyncio
    async def test_characterize_workflow_passed_to_repository(self) -> None:
        """Document: Workflow entity is passed to repository, not DTO."""
        account_id = uuid4()
        user_id = uuid4()
        request = CreateWorkflowRequest(name="Entity Test")

        mock_workflow_repo = AsyncMock()
        mock_audit_repo = AsyncMock()
        mock_workflow_repo.get_by_name.return_value = None

        captured_workflow = None

        async def capture_workflow(workflow):
            nonlocal captured_workflow
            captured_workflow = workflow
            return workflow

        mock_workflow_repo.create.side_effect = capture_workflow

        use_case = CreateWorkflowUseCase(
            workflow_repository=mock_workflow_repo,
            audit_log_repository=mock_audit_repo,
        )

        await use_case.execute(
            request=request,
            account_id=account_id,
            user_id=user_id,
        )

        # Assert: Workflow entity, not DTO, passed to repository
        assert isinstance(captured_workflow, Workflow)
        assert not isinstance(captured_workflow, CreateWorkflowRequest)
        assert str(captured_workflow.name) == "Entity Test"
