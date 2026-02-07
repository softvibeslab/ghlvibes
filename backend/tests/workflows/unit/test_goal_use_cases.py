"""Unit tests for goal tracking use cases."""

from uuid import uuid4

import pytest

from src.workflows.application.goal_dtos import CreateGoalRequestDTO
from src.workflows.application.use_cases.create_goal import CreateGoalUseCase
from src.workflows.application.use_cases.delete_goal import DeleteGoalUseCase
from src.workflows.application.use_cases.list_goals import ListGoalsUseCase
from src.workflows.application.use_cases.update_goal import UpdateGoalUseCase
from src.workflows.domain.exceptions import GoalConfigNotFoundError, WorkflowNotFoundError
from src.workflows.domain.goal_entities import GoalConfig, GoalType
from src.workflows.infrastructure.goal_repository import IGoalRepository
from src.workflows.infrastructure.repositories import IWorkflowRepository


@pytest.fixture
def mock_goal_repository():
    """Create a mock goal repository."""
    from unittest.mock import AsyncMock

    repo = AsyncMock(spec=IGoalRepository)
    return repo


@pytest.fixture
def mock_workflow_repository():
    """Create a mock workflow repository."""
    from unittest.mock import AsyncMock

    repo = AsyncMock(spec=IWorkflowRepository)
    return repo


@pytest.fixture
def sample_goal():
    """Create a sample goal configuration."""
    return GoalConfig.create(
        workflow_id=uuid4(),
        account_id=uuid4(),
        goal_type=GoalType.TAG_ADDED,
        criteria={"tag_id": str(uuid4()), "tag_name": "Purchased"},
        created_by=uuid4(),
    )


class TestCreateGoalUseCase:
    """Tests for CreateGoalUseCase."""

    @pytest.mark.asyncio
    async def test_create_goal_success(self, mock_goal_repository, mock_workflow_repository):
        """Test successful goal creation."""
        # Arrange
        workflow_id = uuid4()
        account_id = uuid4()
        created_by = uuid4()
        request_dto = CreateGoalRequestDTO(
            goal_type="tag_added",
            criteria={"tag_id": str(uuid4()), "tag_name": "Purchased"},
        )

        mock_workflow = type(
            "Workflow",
            (),
            {"id": workflow_id, "account_id": account_id},
        )()
        mock_workflow_repository.get_by_id.return_value = mock_workflow

        goal = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=GoalType.TAG_ADDED,
            criteria=request_dto.criteria,
            created_by=created_by,
        )
        mock_goal_repository.create.return_value = goal

        use_case = CreateGoalUseCase(
            goal_repository=mock_goal_repository,
            workflow_repository=mock_workflow_repository,
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
        assert result.goal_type == "tag_added"
        mock_workflow_repository.get_by_id.assert_called_once_with(workflow_id, account_id)
        mock_goal_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_goal_workflow_not_found(
        self, mock_goal_repository, mock_workflow_repository
    ):
        """Test goal creation when workflow doesn't exist."""
        # Arrange
        workflow_id = uuid4()
        account_id = uuid4()
        request_dto = CreateGoalRequestDTO(
            goal_type="tag_added",
            criteria={"tag_id": str(uuid4())},
        )
        mock_workflow_repository.get_by_id.return_value = None

        use_case = CreateGoalUseCase(
            goal_repository=mock_goal_repository,
            workflow_repository=mock_workflow_repository,
        )

        # Act & Assert
        with pytest.raises(WorkflowNotFoundError):
            await use_case.execute(
                workflow_id=workflow_id,
                account_id=account_id,
                request_dto=request_dto,
                created_by=uuid4(),
            )

    @pytest.mark.asyncio
    async def test_create_goal_invalid_goal_type(
        self, mock_goal_repository, mock_workflow_repository
    ):
        """Test goal creation with invalid goal type."""
        # Arrange
        workflow_id = uuid4()
        account_id = uuid4()
        request_dto = CreateGoalRequestDTO(
            goal_type="invalid_goal_type",
            criteria={"tag_id": str(uuid4())},
        )

        mock_workflow = type("Workflow", (), {"id": workflow_id})()
        mock_workflow_repository.get_by_id.return_value = mock_workflow

        use_case = CreateGoalUseCase(
            goal_repository=mock_goal_repository,
            workflow_repository=mock_workflow_repository,
        )

        # Act & Assert
        with pytest.raises(Exception):  # GoalValidationError
            await use_case.execute(
                workflow_id=workflow_id,
                account_id=account_id,
                request_dto=request_dto,
                created_by=uuid4(),
            )


class TestUpdateGoalUseCase:
    """Tests for UpdateGoalUseCase."""

    @pytest.mark.asyncio
    async def test_update_goal_success(self, mock_goal_repository, sample_goal):
        """Test successful goal update."""
        # Arrange
        account_id = sample_goal.account_id
        updated_by = uuid4()

        mock_goal_repository.get_by_id.return_value = sample_goal
        mock_goal_repository.update.return_value = sample_goal

        from src.workflows.application.goal_dtos import UpdateGoalRequestDTO

        request_dto = UpdateGoalRequestDTO(
            criteria={"tag_name": "VIP Customer"},
            is_active=False,
        )

        use_case = UpdateGoalUseCase(goal_repository=mock_goal_repository)

        # Act
        result = await use_case.execute(
            goal_id=sample_goal.id,
            account_id=account_id,
            request_dto=request_dto,
            updated_by=updated_by,
        )

        # Assert
        assert result.id == sample_goal.id
        mock_goal_repository.get_by_id.assert_called_once()
        mock_goal_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_goal_not_found(self, mock_goal_repository):
        """Test updating a goal that doesn't exist."""
        # Arrange
        goal_id = uuid4()
        account_id = uuid4()
        mock_goal_repository.get_by_id.return_value = None

        from src.workflows.application.goal_dtos import UpdateGoalRequestDTO

        request_dto = UpdateGoalRequestDTO(is_active=False)

        use_case = UpdateGoalUseCase(goal_repository=mock_goal_repository)

        # Act & Assert
        with pytest.raises(GoalConfigNotFoundError):
            await use_case.execute(
                goal_id=goal_id,
                account_id=account_id,
                request_dto=request_dto,
                updated_by=uuid4(),
            )


class TestDeleteGoalUseCase:
    """Tests for DeleteGoalUseCase."""

    @pytest.mark.asyncio
    async def test_delete_goal_success(self, mock_goal_repository, sample_goal):
        """Test successful goal deletion."""
        # Arrange
        mock_goal_repository.get_by_id.return_value = sample_goal
        mock_goal_repository.delete.return_value = True

        use_case = DeleteGoalUseCase(goal_repository=mock_goal_repository)

        # Act
        result = await use_case.execute(
            goal_id=sample_goal.id,
            account_id=sample_goal.account_id,
            deleted_by=uuid4(),
        )

        # Assert
        assert result is True
        mock_goal_repository.get_by_id.assert_called_once()
        mock_goal_repository.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_goal_not_found(self, mock_goal_repository):
        """Test deleting a goal that doesn't exist."""
        # Arrange
        goal_id = uuid4()
        account_id = uuid4()
        mock_goal_repository.get_by_id.return_value = None

        use_case = DeleteGoalUseCase(goal_repository=mock_goal_repository)

        # Act & Assert
        with pytest.raises(GoalConfigNotFoundError):
            await use_case.execute(
                goal_id=goal_id,
                account_id=account_id,
                deleted_by=uuid4(),
            )


class TestListGoalsUseCase:
    """Tests for ListGoalsUseCase."""

    @pytest.mark.asyncio
    async def test_list_goals_success(self, mock_goal_repository):
        """Test successful goal listing."""
        # Arrange
        workflow_id = uuid4()
        account_id = uuid4()

        goal1 = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=GoalType.TAG_ADDED,
            criteria={"tag_id": str(uuid4())},
            created_by=uuid4(),
        )
        goal2 = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=GoalType.PURCHASE_MADE,
            criteria={"any_purchase": True},
            created_by=uuid4(),
        )

        mock_goal_repository.list_by_workflow.return_value = [goal1, goal2]
        mock_goal_repository.count_by_workflow.return_value = 2

        use_case = ListGoalsUseCase(goal_repository=mock_goal_repository)

        # Act
        result = await use_case.execute(
            workflow_id=workflow_id,
            account_id=account_id,
            offset=0,
            limit=50,
        )

        # Assert
        assert len(result.goals) == 2
        assert result.total == 2
        assert result.offset == 0
        assert result.limit == 50
        mock_goal_repository.list_by_workflow.assert_called_once()
        mock_goal_repository.count_by_workflow.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_goals_empty(self, mock_goal_repository):
        """Test listing goals when none exist."""
        # Arrange
        workflow_id = uuid4()
        account_id = uuid4()

        mock_goal_repository.list_by_workflow.return_value = []
        mock_goal_repository.count_by_workflow.return_value = 0

        use_case = ListGoalsUseCase(goal_repository=mock_goal_repository)

        # Act
        result = await use_case.execute(
            workflow_id=workflow_id,
            account_id=account_id,
        )

        # Assert
        assert len(result.goals) == 0
        assert result.total == 0
