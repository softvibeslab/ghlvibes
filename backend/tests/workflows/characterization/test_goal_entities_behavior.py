"""Characterization tests for GoalConfig entity behavior.

These tests capture the ACTUAL behavior of the GoalConfig entity
to preserve it during refactoring. They document what the code DOES,
not what it SHOULD DO.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from src.workflows.domain.exceptions import ValidationError
from src.workflows.domain.goal_entities import (
    GoalAchievement,
    GoalConfig,
    GoalCriteria,
    GoalType,
)


class TestGoalConfigBehavior:
    """Characterization tests for GoalConfig entity."""

    def test_characterize_goal_config_creation_with_tag_goal(self):
        """Document actual behavior when creating a tag_added goal."""
        # Arrange
        workflow_id = uuid4()
        account_id = uuid4()
        created_by = uuid4()
        goal_type = GoalType.TAG_ADDED
        criteria = {"tag_id": str(uuid4()), "tag_name": "Purchased"}

        # Act
        goal = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=goal_type,
            criteria=criteria,
            created_by=created_by,
        )

        # Assert - Document actual behavior
        assert isinstance(goal, GoalConfig)
        assert goal.id is not None
        assert isinstance(goal.id, UUID)
        assert goal.workflow_id == workflow_id
        assert goal.account_id == account_id
        assert goal.goal_type == GoalType.TAG_ADDED
        assert goal.is_active is True
        assert goal.version == 1
        assert isinstance(goal.created_at, datetime)
        assert isinstance(goal.updated_at, datetime)
        assert goal.created_by == created_by
        assert goal.updated_by == created_by

    def test_characterize_goal_config_with_dict_criteria(self):
        """Document actual behavior when criteria is passed as dict."""
        # Arrange
        workflow_id = uuid4()
        account_id = uuid4()
        created_by = uuid4()

        # Act
        goal = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=GoalType.PURCHASE_MADE,
            criteria={"product_id": str(uuid4()), "min_amount": 100.0},
            created_by=created_by,
        )

        # Assert - Criteria is converted to GoalCriteria
        assert isinstance(goal.criteria, GoalCriteria)
        assert goal.criteria.goal_type == GoalType.PURCHASE_MADE
        assert isinstance(goal.criteria.criteria, dict)

    def test_characterize_goal_config_update_criteria(self):
        """Document actual behavior when updating goal criteria."""
        # Arrange
        goal = GoalConfig.create(
            workflow_id=uuid4(),
            account_id=uuid4(),
            goal_type=GoalType.APPOINTMENT_BOOKED,
            criteria={"calendar_id": str(uuid4())},
            created_by=uuid4(),
        )
        original_version = goal.version
        updated_by = uuid4()

        # Act
        goal.update(
            updated_by=updated_by,
            criteria={"service_id": str(uuid4())},
        )

        # Assert
        assert goal.version == original_version + 1
        assert goal.updated_by == updated_by
        assert isinstance(goal.updated_at, datetime)

    def test_characterize_goal_config_deactivate(self):
        """Document actual behavior when deactivating a goal."""
        # Arrange
        goal = GoalConfig.create(
            workflow_id=uuid4(),
            account_id=uuid4(),
            goal_type=GoalType.FORM_SUBMITTED,
            criteria={"form_id": str(uuid4())},
            created_by=uuid4(),
        )
        updated_by = uuid4()

        # Act
        goal.deactivate(updated_by=updated_by)

        # Assert
        assert goal.is_active is False

    def test_characterize_goal_config_activate(self):
        """Document actual behavior when activating a deactivated goal."""
        # Arrange
        goal = GoalConfig.create(
            workflow_id=uuid4(),
            account_id=uuid4(),
            goal_type=GoalType.PIPELINE_STAGE_REACHED,
            criteria={"pipeline_id": str(uuid4()), "stage_id": str(uuid4())},
            created_by=uuid4(),
        )
        goal.deactivate(updated_by=uuid4())
        updated_by = uuid4()

        # Act
        goal.activate(updated_by=updated_by)

        # Assert
        assert goal.is_active is True

    def test_characterize_goal_config_to_dict(self):
        """Document actual behavior of to_dict conversion."""
        # Arrange
        workflow_id = uuid4()
        account_id = uuid4()
        created_by = uuid4()
        goal = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=GoalType.TAG_ADDED,
            criteria={"tag_id": str(uuid4())},
            created_by=created_by,
        )

        # Act
        result = goal.to_dict()

        # Assert - Document actual dict structure
        assert isinstance(result, dict)
        assert "id" in result
        assert "workflow_id" in result
        assert "account_id" in result
        assert "goal_type" in result
        assert "criteria" in result
        assert "is_active" in result
        assert "version" in result
        assert "created_at" in result
        assert "updated_at" in result
        assert "created_by" in result
        assert "updated_by" in result
        # Verify UUIDs are converted to strings
        assert isinstance(result["id"], str)
        assert isinstance(result["workflow_id"], str)
        assert isinstance(result["account_id"], str)
        assert isinstance(result["goal_type"], str)

    def test_characterize_goal_config_type_checkers(self):
        """Document actual behavior of type checker properties."""
        # Arrange & Act & Assert for each goal type
        tag_goal = GoalConfig.create(
            workflow_id=uuid4(),
            account_id=uuid4(),
            goal_type=GoalType.TAG_ADDED,
            criteria={"tag_id": str(uuid4())},
            created_by=uuid4(),
        )
        assert tag_goal.is_tag_added_goal is True
        assert tag_goal.is_purchase_made_goal is False
        assert tag_goal.is_appointment_booked_goal is False
        assert tag_goal.is_form_submitted_goal is False
        assert tag_goal.is_pipeline_stage_reached_goal is False

        purchase_goal = GoalConfig.create(
            workflow_id=uuid4(),
            account_id=uuid4(),
            goal_type=GoalType.PURCHASE_MADE,
            criteria={"any_purchase": True},
            created_by=uuid4(),
        )
        assert purchase_goal.is_purchase_made_goal is True

        appointment_goal = GoalConfig.create(
            workflow_id=uuid4(),
            account_id=uuid4(),
            goal_type=GoalType.APPOINTMENT_BOOKED,
            criteria={"any_appointment": True},
            created_by=uuid4(),
        )
        assert appointment_goal.is_appointment_booked_goal is True

        form_goal = GoalConfig.create(
            workflow_id=uuid4(),
            account_id=uuid4(),
            goal_type=GoalType.FORM_SUBMITTED,
            criteria={"form_id": str(uuid4())},
            created_by=uuid4(),
        )
        assert form_goal.is_form_submitted_goal is True

        pipeline_goal = GoalConfig.create(
            workflow_id=uuid4(),
            account_id=uuid4(),
            goal_type=GoalType.PIPELINE_STAGE_REACHED,
            criteria={"pipeline_id": str(uuid4()), "stage_id": str(uuid4())},
            created_by=uuid4(),
        )
        assert pipeline_goal.is_pipeline_stage_reached_goal is True


class TestGoalCriteriaBehavior:
    """Characterization tests for GoalCriteria value object."""

    def test_characterize_tag_goal_criteria_validation_pass(self):
        """Document actual behavior when tag goal criteria is valid."""
        # Act - Should not raise
        criteria = GoalCriteria(
            goal_type=GoalType.TAG_ADDED, criteria={"tag_id": str(uuid4())}
        )
        assert criteria.goal_type == GoalType.TAG_ADDED
        assert isinstance(criteria.criteria, dict)

    def test_characterize_tag_goal_criteria_validation_fail(self):
        """Document actual behavior when tag goal criteria is invalid."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            GoalCriteria(goal_type=GoalType.TAG_ADDED, criteria={})

        assert "tag_id" in str(exc_info.value).lower() or "tag_name" in str(
            exc_info.value
        ).lower()

    def test_characterize_purchase_goal_criteria_validation(self):
        """Document actual behavior for purchase goal criteria validation."""
        # Valid - product_id
        criteria1 = GoalCriteria(
            goal_type=GoalType.PURCHASE_MADE, criteria={"product_id": str(uuid4())}
        )
        assert criteria1.criteria["product_id"]

        # Valid - min_amount
        criteria2 = GoalCriteria(
            goal_type=GoalType.PURCHASE_MADE, criteria={"min_amount": 100.0}
        )
        assert criteria2.criteria["min_amount"] == 100.0

        # Valid - any_purchase
        criteria3 = GoalCriteria(
            goal_type=GoalType.PURCHASE_MADE, criteria={"any_purchase": True}
        )
        assert criteria3.criteria["any_purchase"] is True

        # Invalid - no criteria
        with pytest.raises(ValidationError):
            GoalCriteria(goal_type=GoalType.PURCHASE_MADE, criteria={})

    def test_characterize_appointment_goal_criteria_validation(self):
        """Document actual behavior for appointment goal criteria validation."""
        # Valid - calendar_id
        criteria1 = GoalCriteria(
            goal_type=GoalType.APPOINTMENT_BOOKED, criteria={"calendar_id": str(uuid4())}
        )
        assert criteria1.criteria["calendar_id"]

        # Valid - service_id
        criteria2 = GoalCriteria(
            goal_type=GoalType.APPOINTMENT_BOOKED, criteria={"service_id": str(uuid4())}
        )
        assert criteria2.criteria["service_id"]

        # Valid - any_appointment
        criteria3 = GoalCriteria(
            goal_type=GoalType.APPOINTMENT_BOOKED, criteria={"any_appointment": True}
        )
        assert criteria3.criteria["any_appointment"] is True

        # Invalid - no criteria
        with pytest.raises(ValidationError):
            GoalCriteria(goal_type=GoalType.APPOINTMENT_BOOKED, criteria={})

    def test_characterize_form_goal_criteria_validation(self):
        """Document actual behavior for form goal criteria validation."""
        # Valid - form_id
        criteria = GoalCriteria(
            goal_type=GoalType.FORM_SUBMITTED, criteria={"form_id": str(uuid4())}
        )
        assert criteria.criteria["form_id"]

        # Invalid - missing form_id
        with pytest.raises(ValidationError):
            GoalCriteria(goal_type=GoalType.FORM_SUBMITTED, criteria={})

    def test_characterize_pipeline_goal_criteria_validation(self):
        """Document actual behavior for pipeline goal criteria validation."""
        # Valid - both pipeline_id and stage_id
        criteria = GoalCriteria(
            goal_type=GoalType.PIPELINE_STAGE_REACHED,
            criteria={"pipeline_id": str(uuid4()), "stage_id": str(uuid4())},
        )
        assert criteria.criteria["pipeline_id"]
        assert criteria.criteria["stage_id"]

        # Invalid - missing pipeline_id
        with pytest.raises(ValidationError):
            GoalCriteria(
                goal_type=GoalType.PIPELINE_STAGE_REACHED, criteria={"stage_id": str(uuid4())}
            )

        # Invalid - missing stage_id
        with pytest.raises(ValidationError):
            GoalCriteria(
                goal_type=GoalType.PIPELINE_STAGE_REACHED,
                criteria={"pipeline_id": str(uuid4())},
            )

    def test_characterize_goal_criteria_is_frozen(self):
        """Document actual behavior - GoalCriteria should be immutable."""
        # Arrange
        criteria = GoalCriteria(
            goal_type=GoalType.TAG_ADDED, criteria={"tag_id": str(uuid4())}
        )

        # Act & Assert - Cannot modify frozen dataclass
        with pytest.raises(Exception):  # FrozenInstanceError
            criteria.criteria = {"tag_id": str(uuid4())}


class TestGoalAchievementBehavior:
    """Characterization tests for GoalAchievement entity."""

    def test_characterize_goal_achievement_creation(self):
        """Document actual behavior when creating a goal achievement."""
        # Arrange
        workflow_id = uuid4()
        enrollment_id = uuid4()
        contact_id = uuid4()
        goal_config_id = uuid4()
        account_id = uuid4()
        goal_type = GoalType.TAG_ADDED
        trigger_event = {"tag_id": str(uuid4()), "tag_name": "Purchased"}
        metadata = {"source": "webhook"}

        # Act
        achievement = GoalAchievement.create(
            workflow_id=workflow_id,
            workflow_enrollment_id=enrollment_id,
            contact_id=contact_id,
            goal_config_id=goal_config_id,
            account_id=account_id,
            goal_type=goal_type,
            trigger_event=trigger_event,
            metadata=metadata,
        )

        # Assert
        assert isinstance(achievement, GoalAchievement)
        assert achievement.id is not None
        assert isinstance(achievement.id, UUID)
        assert achievement.workflow_id == workflow_id
        assert achievement.workflow_enrollment_id == enrollment_id
        assert achievement.contact_id == contact_id
        assert achievement.goal_config_id == goal_config_id
        assert achievement.account_id == account_id
        assert achievement.goal_type == goal_type
        assert isinstance(achievement.achieved_at, datetime)
        assert achievement.trigger_event == trigger_event
        assert achievement.metadata == metadata

    def test_characterize_goal_achievement_without_metadata(self):
        """Document actual behavior when metadata is not provided."""
        # Arrange
        workflow_id = uuid4()

        # Act
        achievement = GoalAchievement.create(
            workflow_id=workflow_id,
            workflow_enrollment_id=uuid4(),
            contact_id=uuid4(),
            goal_config_id=uuid4(),
            account_id=uuid4(),
            goal_type=GoalType.PURCHASE_MADE,
            trigger_event={"amount": 100.0},
            metadata=None,
        )

        # Assert - Default empty dict
        assert achievement.metadata == {}

    def test_characterize_goal_achievement_to_dict(self):
        """Document actual behavior of to_dict conversion."""
        # Arrange
        workflow_id = uuid4()
        achievement = GoalAchievement.create(
            workflow_id=workflow_id,
            workflow_enrollment_id=uuid4(),
            contact_id=uuid4(),
            goal_config_id=uuid4(),
            account_id=uuid4(),
            goal_type=GoalType.APPOINTMENT_BOOKED,
            trigger_event={"calendar_id": str(uuid4())},
        )

        # Act
        result = achievement.to_dict()

        # Assert
        assert isinstance(result, dict)
        assert "id" in result
        assert "workflow_id" in result
        assert "workflow_enrollment_id" in result
        assert "contact_id" in result
        assert "goal_config_id" in result
        assert "account_id" in result
        assert "goal_type" in result
        assert "achieved_at" in result
        assert "trigger_event" in result
        assert "metadata" in result
        # Verify UUIDs are converted to strings
        assert isinstance(result["id"], str)
        assert isinstance(result["workflow_id"], str)
        assert isinstance(result["goal_type"], str)
        assert isinstance(result["achieved_at"], str)  # ISO format
