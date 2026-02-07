"""Unit tests for condition value objects.

These tests verify the value objects behave correctly
and enforce domain invariants.
"""

import pytest

from src.workflows.domain.condition_exceptions import BranchValidationError
from src.workflows.domain.condition_value_objects import (
    BranchCriteria,
    BranchType,
    ConditionConfig,
    ConditionType,
    CustomFieldType,
    FieldOperator,
    LogicOperator,
    TagOperator,
    TimeConditionType,
)


class TestBranchType:
    """Test suite for BranchType enum."""

    def test_branch_type_values(self) -> None:
        """Test branch type enum values."""
        assert BranchType.IF_ELSE.value == "if_else"
        assert BranchType.MULTI_BRANCH.value == "multi_branch"
        assert BranchType.SPLIT_TEST.value == "split_test"


class TestConditionType:
    """Test suite for ConditionType enum."""

    def test_condition_type_values(self) -> None:
        """Test condition type enum values."""
        assert ConditionType.CONTACT_FIELD_EQUALS.value == "contact_field_equals"
        assert ConditionType.CONTACT_HAS_TAG.value == "contact_has_tag"
        assert ConditionType.PIPELINE_STAGE_IS.value == "pipeline_stage_is"
        assert ConditionType.CUSTOM_FIELD_VALUE.value == "custom_field_value"
        assert ConditionType.EMAIL_WAS_OPENED.value == "email_was_opened"
        assert ConditionType.LINK_WAS_CLICKED.value == "link_was_clicked"
        assert ConditionType.TIME_BASED.value == "time_based"


class TestConditionConfig:
    """Test suite for ConditionConfig value object."""

    def test_create_minimal_config(self) -> None:
        """Test creating config with minimal data."""
        config = ConditionConfig(condition_type=ConditionType.CONTACT_FIELD_EQUALS)

        assert config.condition_type == ConditionType.CONTACT_FIELD_EQUALS
        assert config.field is None
        assert config.operator is None
        assert config.value is None
        assert config.logic == LogicOperator.ALL

    def test_create_full_config(self) -> None:
        """Test creating config with all fields."""
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_HAS_TAG,
            field="tags",
            operator="has_any_tag",
            value=None,
            logic=LogicOperator.ANY,
            tags=["lead", "prospect"],
        )

        assert config.condition_type == ConditionType.CONTACT_HAS_TAG
        assert config.tags == ["lead", "prospect"]
        assert config.logic == LogicOperator.ANY

    def test_config_with_string_types(self) -> None:
        """Test creating config with string enums."""
        config = ConditionConfig(
            condition_type="contact_field_equals",
            logic="ANY",
        )

        assert config.condition_type == ConditionType.CONTACT_FIELD_EQUALS
        assert config.logic == LogicOperator.ANY

    def test_config_to_dict(self) -> None:
        """Test converting config to dictionary."""
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_FIELD_EQUALS,
            field="email",
            operator="contains",
            value="@gmail.com",
        )

        result = config.to_dict()

        assert result["condition_type"] == "contact_field_equals"
        assert result["field"] == "email"
        assert result["operator"] == "contains"
        assert result["value"] == "@gmail.com"
        assert result["logic"] == "ALL"

    def test_config_from_dict(self) -> None:
        """Test creating config from dictionary."""
        data = {
            "condition_type": "contact_field_equals",
            "field": "email",
            "operator": "contains",
            "value": "@gmail.com",
            "logic": "ALL",
        }

        config = ConditionConfig.from_dict(data)

        assert config.condition_type == ConditionType.CONTACT_FIELD_EQUALS
        assert config.field == "email"
        assert config.operator == "contains"
        assert config.value == "@gmail.com"
        assert config.logic == LogicOperator.ALL

    def test_config_tags_property(self) -> None:
        """Test tags property returns copy."""
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_HAS_TAG,
            tags=["tag1", "tag2"],
        )

        tags = config.tags
        tags.append("tag3")

        assert config.tags == ["tag1", "tag2"]
        assert len(tags) == 3

    def test_config_stages_property(self) -> None:
        """Test stages property returns copy."""
        config = ConditionConfig(
            condition_type=ConditionType.PIPELINE_STAGE_IS,
            stages=["stage1", "stage2"],
        )

        stages = config.stages
        stages.append("stage3")

        assert config.stages == ["stage1", "stage2"]
        assert len(stages) == 3

    def test_config_with_custom_field_type(self) -> None:
        """Test config with custom field type."""
        config = ConditionConfig(
            condition_type=ConditionType.CUSTOM_FIELD_VALUE,
            field="age",
            operator="greater_than",
            value=18,
            custom_field_type=CustomFieldType.NUMBER,
        )

        assert config.custom_field_type == CustomFieldType.NUMBER

    def test_config_with_time_condition(self) -> None:
        """Test config with time condition."""
        config = ConditionConfig(
            condition_type=ConditionType.TIME_BASED,
            time_condition=TimeConditionType.CURRENT_DAY_OF_WEEK,
            value="Monday",
        )

        assert config.time_condition == TimeConditionType.CURRENT_DAY_OF_WEEK

    def test_config_with_days(self) -> None:
        """Test config with days value."""
        config = ConditionConfig(
            condition_type=ConditionType.TIME_BASED,
            time_condition=TimeConditionType.DAYS_SINCE_EVENT,
            days=7,
        )

        assert config.days == 7


class TestBranchCriteria:
    """Test suite for BranchCriteria value object."""

    def test_create_minimal_criteria(self) -> None:
        """Test creating minimal criteria."""
        criteria = BranchCriteria()

        assert criteria.config.condition_type == ConditionType.CONTACT_FIELD_EQUALS
        assert criteria.percentage is None

    def test_create_with_config(self) -> None:
        """Test creating criteria with config."""
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_FIELD_EQUALS,
            field="email",
            operator="contains",
            value="@gmail.com",
        )
        criteria = BranchCriteria(config=config)

        assert criteria.config.condition_type == ConditionType.CONTACT_FIELD_EQUALS
        assert criteria.config.field == "email"

    def test_create_with_dict_config(self) -> None:
        """Test creating criteria with dict config."""
        config_dict = {
            "condition_type": "contact_field_equals",
            "field": "email",
            "operator": "contains",
            "value": "@gmail.com",
        }
        criteria = BranchCriteria(config=config_dict)

        assert criteria.config.condition_type == ConditionType.CONTACT_FIELD_EQUALS
        assert criteria.config.field == "email"

    def test_create_with_valid_percentage(self) -> None:
        """Test creating criteria with valid percentage."""
        criteria = BranchCriteria(percentage=50.0)

        assert criteria.percentage == 50.0

    def test_create_with_invalid_percentage_low(self) -> None:
        """Test creating criteria with percentage too low."""
        with pytest.raises(ValueError, match="Percentage must be between 0 and 100"):
            BranchCriteria(percentage=-1.0)

    def test_create_with_invalid_percentage_high(self) -> None:
        """Test creating criteria with percentage too high."""
        with pytest.raises(ValueError, match="Percentage must be between 0 and 100"):
            BranchCriteria(percentage=101.0)

    def test_criteria_to_dict(self) -> None:
        """Test converting criteria to dictionary."""
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_FIELD_EQUALS,
            field="email",
            operator="contains",
            value="@gmail.com",
        )
        criteria = BranchCriteria(config=config, percentage=50.0)

        result = criteria.to_dict()

        assert "config" in result
        assert result["config"]["field"] == "email"
        assert result["percentage"] == 50.0

    def test_criteria_to_dict_without_percentage(self) -> None:
        """Test converting criteria to dict without percentage."""
        criteria = BranchCriteria()

        result = criteria.to_dict()

        assert "config" in result
        assert "percentage" not in result


class TestFieldOperator:
    """Test suite for FieldOperator enum."""

    def test_operator_values(self) -> None:
        """Test field operator enum values."""
        assert FieldOperator.EQUALS.value == "equals"
        assert FieldOperator.CONTAINS.value == "contains"
        assert FieldOperator.GREATER_THAN.value == "greater_than"
        assert FieldOperator.IN_LIST.value == "in_list"


class TestTagOperator:
    """Test suite for TagOperator enum."""

    def test_operator_values(self) -> None:
        """Test tag operator enum values."""
        assert TagOperator.HAS_ANY_TAG.value == "has_any_tag"
        assert TagOperator.HAS_ALL_TAGS.value == "has_all_tags"
        assert TagOperator.HAS_NO_TAGS.value == "has_no_tags"
        assert TagOperator.HAS_ONLY_TAGS.value == "has_only_tags"


class TestCustomFieldType:
    """Test suite for CustomFieldType enum."""

    def test_type_values(self) -> None:
        """Test custom field type enum values."""
        assert CustomFieldType.TEXT.value == "text"
        assert CustomFieldType.NUMBER.value == "number"
        assert CustomFieldType.DATE.value == "date"
        assert CustomFieldType.DROPDOWN.value == "dropdown"
        assert CustomFieldType.CHECKBOX.value == "checkbox"
        assert CustomFieldType.MULTI_SELECT.value == "multi_select"


class TestTimeConditionType:
    """Test suite for TimeConditionType enum."""

    def test_type_values(self) -> None:
        """Test time condition type enum values."""
        assert TimeConditionType.CURRENT_DAY_OF_WEEK.value == "current_day_of_week"
        assert TimeConditionType.CURRENT_TIME_BETWEEN.value == "current_time_between"
        assert TimeConditionType.CURRENT_DATE_BETWEEN.value == "current_date_between"
        assert TimeConditionType.CONTACT_DATE_FIELD.value == "contact_date_field"
        assert TimeConditionType.DAYS_SINCE_EVENT.value == "days_since_event"


class TestLogicOperator:
    """Test suite for LogicOperator enum."""

    def test_operator_values(self) -> None:
        """Test logic operator enum values."""
        assert LogicOperator.ALL.value == "ALL"
        assert LogicOperator.ANY.value == "ANY"
