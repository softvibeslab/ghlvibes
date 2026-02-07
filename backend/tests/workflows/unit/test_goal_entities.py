"""Unit tests for goal tracking domain entities."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.workflows.domain.exceptions import ValidationError
from src.workflows.domain.goal_entities import (
    GoalAchievement,
    GoalConfig,
    GoalCriteria,
    GoalType,
)


class TestGoalType:
    """Tests for GoalType enum."""

    def test_goal_type_values(self):
        """Test that all required goal types are defined."""
        assert GoalType.TAG_ADDED.value == "tag_added"
        assert GoalType.PURCHASE_MADE.value == "purchase_made"
        assert GoalType.APPOINTMENT_BOOKED.value == "appointment_booked"
        assert GoalType.FORM_SUBMITTED.value == "form_submitted"
        assert GoalType.PIPELINE_STAGE_REACHED.value == "pipeline_stage_reached"


class TestGoalCriteria:
    """Tests for GoalCriteria value object."""

    def test_tag_goal_criteria_with_tag_id(self):
        """Test valid tag goal criteria with tag_id."""
        criteria = GoalCriteria(
            goal_type=GoalType.TAG_ADDED,
            criteria={"tag_id": str(uuid4())},
        )
        assert criteria.goal_type == GoalType.TAG_ADDED
        assert "tag_id" in criteria.criteria

    def test_tag_goal_criteria_with_tag_name(self):
        """Test valid tag goal criteria with tag_name."""
        criteria = GoalCriteria(
            goal_type=GoalType.TAG_ADDED,
            criteria={"tag_name": "Purchased"},
        )
        assert criteria.goal_type == GoalType.TAG_ADDED
        assert criteria.criteria["tag_name"] == "Purchased"

    def test_tag_goal_criteria_validation_fails_without_tag_fields(self):
        """Test that tag goal validation fails without tag_id or tag_name."""
        with pytest.raises(ValidationError) as exc_info:
            GoalCriteria(goal_type=GoalType.TAG_ADDED, criteria={})
        assert "tag_id" in str(exc_info.value).lower() or "tag_name" in str(
            exc_info.value
        ).lower()

    def test_purchase_goal_criteria_with_product_id(self):
        """Test valid purchase goal criteria with product_id."""
        product_id = uuid4()
        criteria = GoalCriteria(
            goal_type=GoalType.PURCHASE_MADE,
            criteria={"product_id": str(product_id)},
        )
        assert criteria.goal_type == GoalType.PURCHASE_MADE
        assert str(criteria.criteria["product_id"]) == str(product_id)

    def test_purchase_goal_criteria_with_min_amount(self):
        """Test valid purchase goal criteria with min_amount."""
        criteria = GoalCriteria(
            goal_type=GoalType.PURCHASE_MADE,
            criteria={"min_amount": 100.0},
        )
        assert criteria.goal_type == GoalType.PURCHASE_MADE
        assert criteria.criteria["min_amount"] == 100.0

    def test_purchase_goal_criteria_with_any_purchase(self):
        """Test valid purchase goal criteria with any_purchase flag."""
        criteria = GoalCriteria(
            goal_type=GoalType.PURCHASE_MADE,
            criteria={"any_purchase": True},
        )
        assert criteria.goal_type == GoalType.PURCHASE_MADE
        assert criteria.criteria["any_purchase"] is True

    def test_purchase_goal_criteria_validation_fails_without_criteria(self):
        """Test that purchase goal validation fails without any criteria."""
        with pytest.raises(ValidationError):
            GoalCriteria(goal_type=GoalType.PURCHASE_MADE, criteria={})

    def test_appointment_goal_criteria_with_calendar_id(self):
        """Test valid appointment goal criteria with calendar_id."""
        criteria = GoalCriteria(
            goal_type=GoalType.APPOINTMENT_BOOKED,
            criteria={"calendar_id": str(uuid4())},
        )
        assert criteria.goal_type == GoalType.APPOINTMENT_BOOKED

    def test_appointment_goal_criteria_with_service_id(self):
        """Test valid appointment goal criteria with service_id."""
        criteria = GoalCriteria(
            goal_type=GoalType.APPOINTMENT_BOOKED,
            criteria={"service_id": str(uuid4())},
        )
        assert criteria.goal_type == GoalType.APPOINTMENT_BOOKED

    def test_appointment_goal_criteria_with_any_appointment(self):
        """Test valid appointment goal criteria with any_appointment flag."""
        criteria = GoalCriteria(
            goal_type=GoalType.APPOINTMENT_BOOKED,
            criteria={"any_appointment": True},
        )
        assert criteria.goal_type == GoalType.APPOINTMENT_BOOKED
        assert criteria.criteria["any_appointment"] is True

    def test_form_goal_criteria_validation(self):
        """Test form goal criteria validation."""
        # Valid with form_id
        criteria = GoalCriteria(
            goal_type=GoalType.FORM_SUBMITTED,
            criteria={"form_id": str(uuid4())},
        )
        assert criteria.goal_type == GoalType.FORM_SUBMITTED

        # Invalid without form_id
        with pytest.raises(ValidationError) as exc_info:
            GoalCriteria(goal_type=GoalType.FORM_SUBMITTED, criteria={})
        assert "form_id" in str(exc_info.value).lower()

    def test_pipeline_goal_criteria_validation(self):
        """Test pipeline goal criteria validation."""
        # Valid with both pipeline_id and stage_id
        criteria = GoalCriteria(
            goal_type=GoalType.PIPELINE_STAGE_REACHED,
            criteria={"pipeline_id": str(uuid4()), "stage_id": str(uuid4())},
        )
        assert criteria.goal_type == GoalType.PIPELINE_STAGE_REACHED

        # Invalid without pipeline_id
        with pytest.raises(ValidationError):
            GoalCriteria(
                goal_type=GoalType.PIPELINE_STAGE_REACHED,
                criteria={"stage_id": str(uuid4())},
            )

        # Invalid without stage_id
        with pytest.raises(ValidationError):
            GoalCriteria(
                goal_type=GoalType.PIPELINE_STAGE_REACHED,
                criteria={"pipeline_id": str(uuid4())},
            )


class TestGoalConfig:
    """Tests for GoalConfig entity."""

    def test_create_goal_config(self):
        """Test creating a goal configuration."""
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

        assert goal.id is not None
        assert goal.workflow_id == workflow_id
        assert goal.account_id == account_id
        assert goal.goal_type == GoalType.TAG_ADDED
        assert goal.is_active is True
        assert goal.version == 1
        assert goal.created_by == created_by
        assert goal.updated_by == created_by
        assert isinstance(goal.created_at, datetime)
        assert isinstance(goal.updated_at, datetime)

    def test_create_goal_converts_dict_to_goal_criteria(self):
        """Test that dict criteria is converted to GoalCriteria."""
        workflow_id = uuid4()
        account_id = uuid4()
        created_by = uuid4()

        goal = GoalConfig.create(
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=GoalType.PURCHASE_MADE,
            criteria={"min_amount": 100.0},
            created_by=created_by,
        )

        assert isinstance(goal.criteria, GoalCriteria)
        assert goal.criteria.criteria["min_amount"] == 100.0

    def test_goal_update_criteria(self):
        """Test updating goal criteria."""
        goal = GoalConfig.create(
            workflow_id=uuid4(),
            account_id=uuid4(),
            goal_type=GoalType.APPOINTMENT_BOOKED,
            criteria={"calendar_id": str(uuid4())},
            created_by=uuid4(),
        )
        original_version = goal.version
        updated_by = uuid4()

        goal.update(
            updated_by=updated_by,
            criteria={"service_id": str(uuid4())},
        )

        assert goal.version == original_version + 1
        assert goal.updated_by == updated_by

    def test_goal_deactivate(self):
        """Test deactivating a goal."""
        goal = GoalConfig.create(
            workflow_id=uuid4(),
            account_id=uuid4(),
            goal_type=GoalType.FORM_SUBMITTED,
            criteria={"form_id": str(uuid4())},
            created_by=uuid4(),
        )
        updated_by = uuid4()

        goal.deactivate(updated_by=updated_by)

        assert goal.is_active is False
        assert goal.updated_by == updated_by

    def test_goal_activate(self):
        """Test activating a deactivated goal."""
        goal = GoalConfig.create(
            workflow_id=uuid4(),
            account_id=uuid4(),
            goal_type=GoalType.PIPELINE_STAGE_REACHED,
            criteria={"pipeline_id": str(uuid4()), "stage_id": str(uuid4())},
            created_by=uuid4(),
        )
        goal.deactivate(updated_by=uuid4())
        updated_by = uuid4()

        goal.activate(updated_by=updated_by)

        assert goal.is_active is True

    def test_goal_to_dict(self):
        """Test converting goal to dictionary."""
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

        result = goal.to_dict()

        assert isinstance(result, dict)
        assert result["workflow_id"] == str(workflow_id)
        assert result["account_id"] == str(account_id)
        assert result["goal_type"] == "tag_added"
        assert result["is_active"] is True
        assert result["version"] == 1

    def test_goal_type_checkers(self):
        """Test goal type checker properties."""
        tag_goal = GoalConfig.create(
            workflow_id=uuid4(),
            account_id=uuid4(),
            goal_type=GoalType.TAG_ADDED,
            criteria={"tag_id": str(uuid4())},
            created_by=uuid4(),
        )
        assert tag_goal.is_tag_added_goal is True
        assert tag_goal.is_purchase_made_goal is False

        purchase_goal = GoalConfig.create(
            workflow_id=uuid4(),
            account_id=uuid4(),
            goal_type=GoalType.PURCHASE_MADE,
            criteria={"any_purchase": True},
            created_by=uuid4(),
        )
        assert purchase_goal.is_purchase_made_goal is True


class TestGoalAchievement:
    """Tests for GoalAchievement entity."""

    def test_create_goal_achievement(self):
        """Test creating a goal achievement record."""
        workflow_id = uuid4()
        enrollment_id = uuid4()
        contact_id = uuid4()
        goal_config_id = uuid4()
        account_id = uuid4()

        achievement = GoalAchievement.create(
            workflow_id=workflow_id,
            workflow_enrollment_id=enrollment_id,
            contact_id=contact_id,
            goal_config_id=goal_config_id,
            account_id=account_id,
            goal_type=GoalType.TAG_ADDED,
            trigger_event={"tag_id": str(uuid4()), "tag_name": "Purchased"},
        )

        assert achievement.id is not None
        assert achievement.workflow_id == workflow_id
        assert achievement.workflow_enrollment_id == enrollment_id
        assert achievement.contact_id == contact_id
        assert achievement.goal_config_id == goal_config_id
        assert achievement.account_id == account_id
        assert achievement.goal_type == GoalType.TAG_ADDED
        assert isinstance(achievement.achieved_at, datetime)

    def test_goal_achievement_with_metadata(self):
        """Test creating achievement with metadata."""
        achievement = GoalAchievement.create(
            workflow_id=uuid4(),
            workflow_enrollment_id=uuid4(),
            contact_id=uuid4(),
            goal_config_id=uuid4(),
            account_id=uuid4(),
            goal_type=GoalType.PURCHASE_MADE,
            trigger_event={"amount": 100.0},
            metadata={"source": "webhook"},
        )

        assert achievement.metadata == {"source": "webhook"}

    def test_goal_achievement_default_metadata(self):
        """Test that achievement defaults to empty dict for metadata."""
        achievement = GoalAchievement.create(
            workflow_id=uuid4(),
            workflow_enrollment_id=uuid4(),
            contact_id=uuid4(),
            goal_config_id=uuid4(),
            account_id=uuid4(),
            goal_type=GoalType.APPOINTMENT_BOOKED,
            trigger_event={"calendar_id": str(uuid4())},
            metadata=None,
        )

        assert achievement.metadata == {}

    def test_goal_achievement_to_dict(self):
        """Test converting achievement to dictionary."""
        workflow_id = uuid4()
        achievement = GoalAchievement.create(
            workflow_id=workflow_id,
            workflow_enrollment_id=uuid4(),
            contact_id=uuid4(),
            goal_config_id=uuid4(),
            account_id=uuid4(),
            goal_type=GoalType.FORM_SUBMITTED,
            trigger_event={"form_id": str(uuid4())},
        )

        result = achievement.to_dict()

        assert isinstance(result, dict)
        assert result["workflow_id"] == str(workflow_id)
        assert result["goal_type"] == "form_submitted"
        assert isinstance(result["achieved_at"], str)
