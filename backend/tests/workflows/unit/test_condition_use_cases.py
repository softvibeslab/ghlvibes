"""Unit tests for condition use cases."""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.workflows.application.condition_dtos import (
    AddBranchRequestDTO,
    CreateConditionRequestDTO,
    EvaluateConditionRequestDTO,
    UpdateConditionRequestDTO,
)
from src.workflows.application.use_cases.add_branch import AddBranchUseCase
from src.workflows.application.use_cases.create_condition import CreateConditionUseCase
from src.workflows.application.use_cases.delete_condition import DeleteConditionUseCase
from src.workflows.application.use_cases.evaluate_condition import EvaluateConditionUseCase
from src.workflows.application.use_cases.list_conditions import ListConditionsUseCase
from src.workflows.application.use_cases.update_condition import UpdateConditionUseCase
from src.workflows.domain.condition_entities import Branch, Condition
from src.workflows.domain.condition_exceptions import ConditionValidationError
from src.workflows.domain.condition_value_objects import (
    BranchType,
    ConditionConfig,
    ConditionType,
)
from src.workflows.domain.exceptions import ConditionNotFoundError, WorkflowNotFoundError


class TestCreateConditionUseCase:
    """Test suite for CreateConditionUseCase."""

    @pytest.fixture
    def workflow_id(self) -> str:
        """Fixture for workflow ID."""
        return uuid4()

    @pytest.fixture
    def account_id(self) -> str:
        """Fixture for account ID."""
        return uuid4()

    @pytest.fixture
    def user_id(self) -> str:
        """Fixture for user ID."""
        return uuid4()

    @pytest.fixture
    def request_dto(self) -> CreateConditionRequestDTO:
        """Fixture for condition creation request."""
        return CreateConditionRequestDTO(
            node_id=uuid4(),
            condition_type="contact_field_equals",
            branch_type="if_else",
            configuration={
                "field": "email",
                "operator": "contains",
                "value": "@gmail.com",
            },
            position_x=200,
            position_y=300,
        )

    @pytest.mark.asyncio
    async def test_create_condition_success(
        self, workflow_id, account_id, user_id, request_dto
    ) -> None:
        """Test successful condition creation."""
        # Setup mocks
        mock_workflow_repo = Mock()
        mock_condition_repo = Mock()

        # Mock workflow exists
        mock_workflow = Mock()
        mock_workflow_repo.get_by_id = AsyncMock(return_value=mock_workflow)

        # Mock condition creation
        mock_condition = Mock(spec=Condition)
        mock_condition.to_dict = Mock(return_value={"id": str(uuid4()), "workflow_id": str(workflow_id)})
        mock_condition_repo.create = AsyncMock(return_value=mock_condition)

        # Create use case
        use_case = CreateConditionUseCase(mock_condition_repo, mock_workflow_repo)

        # Execute
        result = await use_case.execute(workflow_id, account_id, request_dto, user_id)

        # Verify
        assert result is not None
        mock_workflow_repo.get_by_id.assert_called_once_with(workflow_id, account_id)
        mock_condition_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_condition_workflow_not_found(
        self, workflow_id, account_id, user_id, request_dto
    ) -> None:
        """Test condition creation with non-existent workflow."""
        # Setup mocks
        mock_workflow_repo = Mock()
        mock_condition_repo = Mock()

        # Mock workflow doesn't exist
        mock_workflow_repo.get_by_id = AsyncMock(return_value=None)

        # Create use case
        use_case = CreateConditionUseCase(mock_condition_repo, mock_workflow_repo)

        # Execute and verify exception
        with pytest.raises(WorkflowNotFoundError):
            await use_case.execute(workflow_id, account_id, request_dto, user_id)

    @pytest.mark.asyncio
    async def test_create_condition_invalid_branch_type(
        self, workflow_id, account_id, user_id, request_dto
    ) -> None:
        """Test condition creation with invalid branch type."""
        # Modify request with invalid branch type
        request_dto.branch_type = "invalid_type"

        # Setup mocks
        mock_workflow_repo = Mock()
        mock_condition_repo = Mock()
        mock_workflow_repo.get_by_id = AsyncMock(return_value=Mock())

        # Create use case
        use_case = CreateConditionUseCase(mock_condition_repo, mock_workflow_repo)

        # Execute and verify exception
        with pytest.raises(ConditionValidationError, match="Invalid branch type"):
            await use_case.execute(workflow_id, account_id, request_dto, user_id)


class TestUpdateConditionUseCase:
    """Test suite for UpdateConditionUseCase."""

    @pytest.fixture
    def condition_id(self) -> str:
        """Fixture for condition ID."""
        return uuid4()

    @pytest.fixture
    def account_id(self) -> str:
        """Fixture for account ID."""
        return uuid4()

    @pytest.fixture
    def user_id(self) -> str:
        """Fixture for user ID."""
        return uuid4()

    @pytest.fixture
    def request_dto(self) -> UpdateConditionRequestDTO:
        """Fixture for condition update request."""
        return UpdateConditionRequestDTO(
            configuration={
                "field": "email",
                "operator": "contains",
                "value": "@yahoo.com",
            },
            position_x=300,
            position_y=400,
            is_active=True,
        )

    @pytest.mark.asyncio
    async def test_update_condition_success(
        self, condition_id, account_id, user_id, request_dto
    ) -> None:
        """Test successful condition update."""
        # Setup mocks
        mock_condition_repo = Mock()

        # Mock condition exists
        mock_condition = Mock(spec=Condition)
        mock_condition.update_configuration = Mock()
        mock_condition.to_dict = Mock(return_value={"id": str(condition_id)})
        mock_condition_repo.get_by_id = AsyncMock(return_value=mock_condition)
        mock_condition_repo.update = AsyncMock(return_value=mock_condition)

        # Create use case
        use_case = UpdateConditionUseCase(mock_condition_repo)

        # Execute
        result = await use_case.execute(condition_id, account_id, request_dto, user_id)

        # Verify
        assert result is not None
        mock_condition_repo.get_by_id.assert_called_once_with(condition_id, account_id)
        mock_condition.update_configuration.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_condition_not_found(
        self, condition_id, account_id, user_id, request_dto
    ) -> None:
        """Test updating non-existent condition."""
        # Setup mocks
        mock_condition_repo = Mock()
        mock_condition_repo.get_by_id = AsyncMock(return_value=None)

        # Create use case
        use_case = UpdateConditionUseCase(mock_condition_repo)

        # Execute and verify exception
        with pytest.raises(ConditionNotFoundError):
            await use_case.execute(condition_id, account_id, request_dto, user_id)


class TestDeleteConditionUseCase:
    """Test suite for DeleteConditionUseCase."""

    @pytest.fixture
    def condition_id(self) -> str:
        """Fixture for condition ID."""
        return uuid4()

    @pytest.fixture
    def account_id(self) -> str:
        """Fixture for account ID."""
        return uuid4()

    @pytest.fixture
    def user_id(self) -> str:
        """Fixture for user ID."""
        return uuid4()

    @pytest.mark.asyncio
    async def test_delete_condition_success(self, condition_id, account_id, user_id) -> None:
        """Test successful condition deletion."""
        # Setup mocks
        mock_condition_repo = Mock()
        mock_condition = Mock(spec=Condition)
        mock_condition_repo.get_by_id = AsyncMock(return_value=mock_condition)
        mock_condition_repo.delete = AsyncMock(return_value=True)

        # Create use case
        use_case = DeleteConditionUseCase(mock_condition_repo)

        # Execute
        await use_case.execute(condition_id, account_id, user_id)

        # Verify
        mock_condition_repo.get_by_id.assert_called_once_with(condition_id, account_id)
        mock_condition_repo.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_condition_not_found(self, condition_id, account_id, user_id) -> None:
        """Test deleting non-existent condition."""
        # Setup mocks
        mock_condition_repo = Mock()
        mock_condition_repo.get_by_id = AsyncMock(return_value=None)

        # Create use case
        use_case = DeleteConditionUseCase(mock_condition_repo)

        # Execute and verify exception
        with pytest.raises(ConditionNotFoundError):
            await use_case.execute(condition_id, account_id, user_id)


class TestEvaluateConditionUseCase:
    """Test suite for EvaluateConditionUseCase."""

    @pytest.fixture
    def condition_id(self) -> str:
        """Fixture for condition ID."""
        return uuid4()

    @pytest.fixture
    def account_id(self) -> str:
        """Fixture for account ID."""
        return uuid4()

    @pytest.fixture
    def request_dto(self) -> EvaluateConditionRequestDTO:
        """Fixture for evaluation request."""
        return EvaluateConditionRequestDTO(
            contact_id=uuid4(),
            contact_data={"email": "test@gmail.com", "name": "Test User"},
            tags=["lead"],
        )

    @pytest.mark.asyncio
    async def test_evaluate_condition_success(
        self, condition_id, account_id, request_dto
    ) -> None:
        """Test successful condition evaluation."""
        # Setup mocks
        mock_condition_repo = Mock()

        # Mock condition with if/else branches
        true_branch = Mock(spec=Branch)
        true_branch.id = uuid4()
        true_branch.is_default = False
        true_branch.branch_name = "True"
        true_branch.next_node_id = uuid4()

        false_branch = Mock(spec=Branch)
        false_branch.id = uuid4()
        false_branch.is_default = True
        false_branch.branch_name = "False"
        false_branch.next_node_id = uuid4()

        mock_condition = Mock(spec=Condition)
        mock_condition.condition_type = "contact_field_equals"
        mock_condition.configuration = Mock()
        mock_condition.configuration.to_dict = Mock(return_value={})
        mock_condition.branches = [true_branch, false_branch]

        mock_condition_repo.get_by_id = AsyncMock(return_value=mock_condition)

        # Create use case
        use_case = EvaluateConditionUseCase(mock_condition_repo)

        # Execute
        result = await use_case.execute(condition_id, account_id, request_dto)

        # Verify
        assert result is not None
        assert "result" in result.model_fields_set or hasattr(result, "result")
        assert result.duration_ms >= 0
        mock_condition_repo.get_by_id.assert_called_once()

    @pytest.mark.asyncio
    async def test_evaluate_condition_not_found(
        self, condition_id, account_id, request_dto
    ) -> None:
        """Test evaluating non-existent condition."""
        # Setup mocks
        mock_condition_repo = Mock()
        mock_condition_repo.get_by_id = AsyncMock(return_value=None)

        # Create use case
        use_case = EvaluateConditionUseCase(mock_condition_repo)

        # Execute and verify exception
        with pytest.raises(ConditionNotFoundError):
            await use_case.execute(condition_id, account_id, request_dto)


class TestListConditionsUseCase:
    """Test suite for ListConditionsUseCase."""

    @pytest.fixture
    def workflow_id(self) -> str:
        """Fixture for workflow ID."""
        return uuid4()

    @pytest.fixture
    def account_id(self) -> str:
        """Fixture for account ID."""
        return uuid4()

    @pytest.mark.asyncio
    async def test_list_conditions_success(self, workflow_id, account_id) -> None:
        """Test successful conditions listing."""
        # Setup mocks
        mock_condition_repo = Mock()

        # Mock conditions list
        mock_condition1 = Mock(spec=Condition)
        mock_condition1.to_dict = Mock(return_value={"id": str(uuid4()), "node_id": str(uuid4())})

        mock_condition2 = Mock(spec=Condition)
        mock_condition2.to_dict = Mock(return_value={"id": str(uuid4()), "node_id": str(uuid4())})

        mock_condition_repo.list_by_workflow = AsyncMock(return_value=[mock_condition1, mock_condition2])
        mock_condition_repo.count_by_workflow = AsyncMock(return_value=2)

        # Create use case
        use_case = ListConditionsUseCase(mock_condition_repo)

        # Execute
        result = await use_case.execute(workflow_id, account_id, offset=0, limit=50)

        # Verify
        assert result is not None
        assert len(result.conditions) == 2
        assert result.total == 2
        mock_condition_repo.list_by_workflow.assert_called_once()
        mock_condition_repo.count_by_workflow.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_conditions_empty(self, workflow_id, account_id) -> None:
        """Test listing conditions with no results."""
        # Setup mocks
        mock_condition_repo = Mock()
        mock_condition_repo.list_by_workflow = AsyncMock(return_value=[])
        mock_condition_repo.count_by_workflow = AsyncMock(return_value=0)

        # Create use case
        use_case = ListConditionsUseCase(mock_condition_repo)

        # Execute
        result = await use_case.execute(workflow_id, account_id)

        # Verify
        assert result is not None
        assert len(result.conditions) == 0
        assert result.total == 0


class TestAddBranchUseCase:
    """Test suite for AddBranchUseCase."""

    @pytest.fixture
    def condition_id(self) -> str:
        """Fixture for condition ID."""
        return uuid4()

    @pytest.fixture
    def account_id(self) -> str:
        """Fixture for account ID."""
        return uuid4()

    @pytest.mark.asyncio
    async def test_add_branch_success(self, condition_id, account_id) -> None:
        """Test successful branch addition."""
        # Setup mocks
        mock_condition_repo = Mock()

        # Mock condition
        mock_condition = Mock(spec=Condition)
        mock_condition.add_branch = Mock()

        mock_condition_repo.get_by_id = AsyncMock(return_value=mock_condition)
        mock_condition_repo.update = AsyncMock(return_value=mock_condition)

        # Create use case
        use_case = AddBranchUseCase(mock_condition_repo)

        # Execute
        result = await use_case.execute(
            condition_id=condition_id,
            account_id=account_id,
            branch_name="New Branch",
            branch_order=2,
            is_default=False,
        )

        # Verify
        assert result is not None
        mock_condition.add_branch.assert_called_once()
        mock_condition_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_branch_condition_not_found(self, condition_id, account_id) -> None:
        """Test adding branch to non-existent condition."""
        # Setup mocks
        mock_condition_repo = Mock()
        mock_condition_repo.get_by_id = AsyncMock(return_value=None)

        # Create use case
        use_case = AddBranchUseCase(mock_condition_repo)

        # Execute and verify exception
        with pytest.raises(ConditionNotFoundError):
            await use_case.execute(
                condition_id=condition_id,
                account_id=account_id,
                branch_name="New Branch",
                branch_order=1,
            )
