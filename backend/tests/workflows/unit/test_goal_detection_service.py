"""Unit tests for goal detection service."""

from uuid import uuid4

import pytest

from src.workflows.application.goal_detection_service import GoalDetectionService
from src.workflows.domain.goal_entities import GoalConfig, GoalType
from src.workflows.infrastructure.goal_repository import (
    IGoalAchievementRepository,
    IGoalRepository,
)


@pytest.fixture
def mock_goal_repository():
    """Create a mock goal repository."""
    from unittest.mock import AsyncMock

    repo = AsyncMock(spec=IGoalRepository)
    return repo


@pytest.fixture
def mock_achievement_repository():
    """Create a mock achievement repository."""
    from unittest.mock import AsyncMock

    repo = AsyncMock(spec=IGoalAchievementRepository)
    return repo


class TestGoalDetectionService:
    """Tests for GoalDetectionService."""

    @pytest.mark.asyncio
    async def test_evaluate_tag_added_goal_achieved(
        self, mock_goal_repository, mock_achievement_repository
    ):
        """Test detecting tag added goal achievement."""
        # Arrange
        workflow_id = uuid4()
        contact_id = uuid4()
        account_id = uuid4()
        tag_id = uuid4()

        goal = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=GoalType.TAG_ADDED,
            criteria={"tag_id": str(tag_id)},
            created_by=uuid4(),
        )

        mock_goal_repository.list_by_workflow.return_value = [goal]
        mock_achievement_repository.check_already_achieved.return_value = False

        service = GoalDetectionService(
            goal_repository=mock_goal_repository,
            achievement_repository=mock_achievement_repository,
        )

        # Act
        result = await service.evaluate_event(
            workflow_id=workflow_id,
            contact_id=contact_id,
            account_id=account_id,
            event_type="contact.tag.added",
            event_data={"tag_id": str(tag_id), "tag_name": "Purchased"},
        )

        # Assert
        assert result.goal_achieved is True
        assert result.goal_config_id == goal.id
        assert result.goal_type == "tag_added"
        assert result.should_exit_workflow is True

    @pytest.mark.asyncio
    async def test_evaluate_tag_added_goal_not_achieved_wrong_tag(
        self, mock_goal_repository, mock_achievement_repository
    ):
        """Test tag added goal not achieved with wrong tag."""
        # Arrange
        workflow_id = uuid4()
        contact_id = uuid4()
        account_id = uuid4()

        goal = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=GoalType.TAG_ADDED,
            criteria={"tag_id": str(uuid4())},
            created_by=uuid4(),
        )

        mock_goal_repository.list_by_workflow.return_value = [goal]

        service = GoalDetectionService(
            goal_repository=mock_goal_repository,
            achievement_repository=mock_achievement_repository,
        )

        # Act
        result = await service.evaluate_event(
            workflow_id=workflow_id,
            contact_id=contact_id,
            account_id=account_id,
            event_type="contact.tag.added",
            event_data={"tag_id": str(uuid4()), "tag_name": "Other Tag"},
        )

        # Assert
        assert result.goal_achieved is False
        assert result.should_exit_workflow is False

    @pytest.mark.asyncio
    async def test_evaluate_purchase_made_goal_achieved(
        self, mock_goal_repository, mock_achievement_repository
    ):
        """Test detecting purchase made goal achievement."""
        # Arrange
        workflow_id = uuid4()
        contact_id = uuid4()
        account_id = uuid4()

        goal = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=GoalType.PURCHASE_MADE,
            criteria={"min_amount": 100.0},
            created_by=uuid4(),
        )

        mock_goal_repository.list_by_workflow.return_value = [goal]
        mock_achievement_repository.check_already_achieved.return_value = False

        service = GoalDetectionService(
            goal_repository=mock_goal_repository,
            achievement_repository=mock_achievement_repository,
        )

        # Act
        result = await service.evaluate_event(
            workflow_id=workflow_id,
            contact_id=contact_id,
            account_id=account_id,
            event_type="payment.completed",
            event_data={"amount": 150.0},
        )

        # Assert
        assert result.goal_achieved is True
        assert result.goal_type == "purchase_made"
        assert result.should_exit_workflow is True

    @pytest.mark.asyncio
    async def test_evaluate_purchase_made_goal_any_purchase(
        self, mock_goal_repository, mock_achievement_repository
    ):
        """Test purchase goal with any_purchase flag."""
        # Arrange
        workflow_id = uuid4()
        contact_id = uuid4()
        account_id = uuid4()

        goal = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=GoalType.PURCHASE_MADE,
            criteria={"any_purchase": True},
            created_by=uuid4(),
        )

        mock_goal_repository.list_by_workflow.return_value = [goal]
        mock_achievement_repository.check_already_achieved.return_value = False

        service = GoalDetectionService(
            goal_repository=mock_goal_repository,
            achievement_repository=mock_achievement_repository,
        )

        # Act
        result = await service.evaluate_event(
            workflow_id=workflow_id,
            contact_id=contact_id,
            account_id=account_id,
            event_type="payment.completed",
            event_data={"amount": 50.0},
        )

        # Assert
        assert result.goal_achieved is True

    @pytest.mark.asyncio
    async def test_evaluate_appointment_booked_goal_achieved(
        self, mock_goal_repository, mock_achievement_repository
    ):
        """Test detecting appointment booked goal achievement."""
        # Arrange
        workflow_id = uuid4()
        contact_id = uuid4()
        account_id = uuid4()
        calendar_id = uuid4()

        goal = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=GoalType.APPOINTMENT_BOOKED,
            criteria={"calendar_id": str(calendar_id)},
            created_by=uuid4(),
        )

        mock_goal_repository.list_by_workflow.return_value = [goal]
        mock_achievement_repository.check_already_achieved.return_value = False

        service = GoalDetectionService(
            goal_repository=mock_goal_repository,
            achievement_repository=mock_achievement_repository,
        )

        # Act
        result = await service.evaluate_event(
            workflow_id=workflow_id,
            contact_id=contact_id,
            account_id=account_id,
            event_type="appointment.booked",
            event_data={"calendar_id": str(calendar_id)},
        )

        # Assert
        assert result.goal_achieved is True
        assert result.goal_type == "appointment_booked"

    @pytest.mark.asyncio
    async def test_evaluate_form_submitted_goal_achieved(
        self, mock_goal_repository, mock_achievement_repository
    ):
        """Test detecting form submitted goal achievement."""
        # Arrange
        workflow_id = uuid4()
        contact_id = uuid4()
        account_id = uuid4()
        form_id = uuid4()

        goal = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=GoalType.FORM_SUBMITTED,
            criteria={"form_id": str(form_id)},
            created_by=uuid4(),
        )

        mock_goal_repository.list_by_workflow.return_value = [goal]
        mock_achievement_repository.check_already_achieved.return_value = False

        service = GoalDetectionService(
            goal_repository=mock_goal_repository,
            achievement_repository=mock_achievement_repository,
        )

        # Act
        result = await service.evaluate_event(
            workflow_id=workflow_id,
            contact_id=contact_id,
            account_id=account_id,
            event_type="form.submitted",
            event_data={"form_id": str(form_id)},
        )

        # Assert
        assert result.goal_achieved is True
        assert result.goal_type == "form_submitted"

    @pytest.mark.asyncio
    async def test_evaluate_pipeline_stage_reached_goal_achieved(
        self, mock_goal_repository, mock_achievement_repository
    ):
        """Test detecting pipeline stage reached goal achievement."""
        # Arrange
        workflow_id = uuid4()
        contact_id = uuid4()
        account_id = uuid4()
        pipeline_id = uuid4()
        stage_id = uuid4()

        goal = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=GoalType.PIPELINE_STAGE_REACHED,
            criteria={"pipeline_id": str(pipeline_id), "stage_id": str(stage_id)},
            created_by=uuid4(),
        )

        mock_goal_repository.list_by_workflow.return_value = [goal]
        mock_achievement_repository.check_already_achieved.return_value = False

        service = GoalDetectionService(
            goal_repository=mock_goal_repository,
            achievement_repository=mock_achievement_repository,
        )

        # Act
        result = await service.evaluate_event(
            workflow_id=workflow_id,
            contact_id=contact_id,
            account_id=account_id,
            event_type="pipeline.stage.changed",
            event_data={"pipeline_id": str(pipeline_id), "stage_id": str(stage_id)},
        )

        # Assert
        assert result.goal_achieved is True
        assert result.goal_type == "pipeline_stage_reached"

    @pytest.mark.asyncio
    async def test_evaluate_goal_already_achieved(
        self, mock_goal_repository, mock_achievement_repository
    ):
        """Test that already achieved goals are not re-achieved."""
        # Arrange
        workflow_id = uuid4()
        contact_id = uuid4()
        account_id = uuid4()
        tag_id = uuid4()

        goal = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=GoalType.TAG_ADDED,
            criteria={"tag_id": str(tag_id)},
            created_by=uuid4(),
        )

        mock_goal_repository.list_by_workflow.return_value = [goal]
        mock_achievement_repository.check_already_achieved.return_value = True

        service = GoalDetectionService(
            goal_repository=mock_goal_repository,
            achievement_repository=mock_achievement_repository,
        )

        # Act
        result = await service.evaluate_event(
            workflow_id=workflow_id,
            contact_id=contact_id,
            account_id=account_id,
            event_type="contact.tag.added",
            event_data={"tag_id": str(tag_id)},
        )

        # Assert
        assert result.goal_achieved is False
        assert result.should_exit_workflow is False

    @pytest.mark.asyncio
    async def test_evaluate_no_active_goals(
        self, mock_goal_repository, mock_achievement_repository
    ):
        """Test evaluation when workflow has no active goals."""
        # Arrange
        workflow_id = uuid4()
        contact_id = uuid4()
        account_id = uuid4()

        mock_goal_repository.list_by_workflow.return_value = []

        service = GoalDetectionService(
            goal_repository=mock_goal_repository,
            achievement_repository=mock_achievement_repository,
        )

        # Act
        result = await service.evaluate_event(
            workflow_id=workflow_id,
            contact_id=contact_id,
            account_id=account_id,
            event_type="contact.tag.added",
            event_data={"tag_id": str(uuid4())},
        )

        # Assert
        assert result.goal_achieved is False
        assert result.should_exit_workflow is False
