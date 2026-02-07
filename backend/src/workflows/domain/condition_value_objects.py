"""Domain value objects for workflow conditions.

This module defines the value objects used in condition evaluation,
including condition types, operators, and branch types.
"""

from enum import Enum
from typing import Any


class BranchType(str, Enum):
    """Type of branch node.

    - if_else: Simple true/false branching
    - multi_branch: Multiple conditional branches with priority
    - split_test: A/B or multi-variant testing with percentage distribution
    """

    IF_ELSE = "if_else"
    MULTI_BRANCH = "multi_branch"
    SPLIT_TEST = "split_test"


class ConditionType(str, Enum):
    """Type of condition to evaluate.

    Contact-based conditions:
    - contact_field_equals: Compare contact field value
    - contact_has_tag: Check contact tags

    Pipeline conditions:
    - pipeline_stage_is: Check contact's pipeline stage

    Custom field conditions:
    - custom_field_value: Compare custom field value

    Engagement conditions:
    - email_was_opened: Check email open status
    - link_was_clicked: Check link click status

    Time-based conditions:
    - time_based: Compare current time or contact dates
    """

    CONTACT_FIELD_EQUALS = "contact_field_equals"
    CONTACT_HAS_TAG = "contact_has_tag"
    PIPELINE_STAGE_IS = "pipeline_stage_is"
    CUSTOM_FIELD_VALUE = "custom_field_value"
    EMAIL_WAS_OPENED = "email_was_opened"
    LINK_WAS_CLICKED = "link_was_clicked"
    TIME_BASED = "time_based"


class FieldOperator(str, Enum):
    """Operators for contact field comparisons.

    Comparison operators:
    - equals: Exact match
    - not_equals: Not equal to
    - contains: Contains substring
    - not_contains: Does not contain substring
    - starts_with: Starts with prefix
    - ends_with: Ends with suffix
    - is_empty: Field is empty or null
    - is_not_empty: Field is not empty
    - greater_than: Numeric greater than
    - less_than: Numeric less than
    - in_list: Value in list
    - not_in_list: Value not in list
    """

    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"


class TagOperator(str, Enum):
    """Operators for tag-based conditions.

    - has_any_tag: Contact has at least one specified tag
    - has_all_tags: Contact has all specified tags
    - has_no_tags: Contact has none of the specified tags
    - has_only_tags: Contact has exactly the specified tags
    """

    HAS_ANY_TAG = "has_any_tag"
    HAS_ALL_TAGS = "has_all_tags"
    HAS_NO_TAGS = "has_no_tags"
    HAS_ONLY_TAGS = "has_only_tags"


class PipelineStageOperator(str, Enum):
    """Operators for pipeline stage conditions.

    - is_in_stage: Contact is in specified stage
    - is_not_in_stage: Contact is not in specified stage
    - is_before_stage: Contact is in earlier stage
    - is_after_stage: Contact is in later stage
    """

    IS_IN_STAGE = "is_in_stage"
    IS_NOT_IN_STAGE = "is_not_in_stage"
    IS_BEFORE_STAGE = "is_before_stage"
    IS_AFTER_STAGE = "is_after_stage"


class CustomFieldType(str, Enum):
    """Custom field types.

    - text: Text/string fields
    - number: Numeric fields
    - date: Date fields
    - dropdown: Single selection dropdown
    - checkbox: Boolean checkbox
    - multi_select: Multiple selection
    """

    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    MULTI_SELECT = "multi_select"


class TimeConditionType(str, Enum):
    """Types of time-based conditions.

    - current_day_of_week: Day of week check
    - current_time_between: Time range check
    - current_date_between: Date range check
    - contact_date_field: Compare contact's date field
    - days_since_event: Days since specific event
    """

    CURRENT_DAY_OF_WEEK = "current_day_of_week"
    CURRENT_TIME_BETWEEN = "current_time_between"
    CURRENT_DATE_BETWEEN = "current_date_between"
    CONTACT_DATE_FIELD = "contact_date_field"
    DAYS_SINCE_EVENT = "days_since_event"


class LogicOperator(str, Enum):
    """Logic operators for combining conditions.

    - ALL: All conditions must be true (AND)
    - ANY: At least one condition must be true (OR)
    """

    ALL = "ALL"
    ANY = "ANY"


class ConditionConfig:
    """Value object for condition configuration.

    This immutable value object contains the configuration
    for a condition evaluation.

    Attributes:
        condition_type: Type of condition to evaluate
        field: Field name for contact field conditions
        operator: Comparison operator to use
        value: Target value for comparison
        logic: Logic operator for combining conditions
        tags: List of tags for tag conditions
        stages: List of pipeline stages
        custom_field_type: Type of custom field
        time_condition: Type of time condition
        days: Days value for time conditions
    """

    __slots__ = (
        "_condition_type",
        "_field",
        "_operator",
        "_value",
        "_logic",
        "_tags",
        "_stages",
        "_custom_field_type",
        "_time_condition",
        "_days",
        "_extra",
    )

    def __init__(
        self,
        condition_type: ConditionType | str,
        field: str | None = None,
        operator: str | None = None,
        value: Any = None,
        logic: LogicOperator | str = LogicOperator.ALL,
        tags: list[str] | None = None,
        stages: list[str] | None = None,
        custom_field_type: CustomFieldType | str | None = None,
        time_condition: TimeConditionType | str | None = None,
        days: int | None = None,
        **extra: Any,
    ) -> None:
        """Initialize condition configuration.

        Args:
            condition_type: Type of condition.
            field: Field name for contact field conditions.
            operator: Comparison operator.
            value: Target value.
            logic: Logic operator for combining conditions.
            tags: Tags for tag conditions.
            stages: Pipeline stages.
            custom_field_type: Custom field type.
            time_condition: Time condition type.
            days: Days for time conditions.
            **extra: Additional configuration.
        """
        object.__setattr__(self, "_condition_type", ConditionType(condition_type))
        object.__setattr__(self, "_field", field)
        object.__setattr__(self, "_operator", operator)
        object.__setattr__(self, "_value", value)
        object.__setattr__(self, "_logic", LogicOperator(logic))
        object.__setattr__(self, "_tags", tags or [])
        object.__setattr__(self, "_stages", stages or [])
        object.__setattr__(
            self,
            "_custom_field_type",
            CustomFieldType(custom_field_type) if custom_field_type else None,
        )
        object.__setattr__(
            self,
            "_time_condition",
            TimeConditionType(time_condition) if time_condition else None,
        )
        object.__setattr__(self, "_days", days)
        object.__setattr__(self, "_extra", extra)

    @property
    def condition_type(self) -> ConditionType:
        """Get condition type."""
        return self._condition_type

    @property
    def field(self) -> str | None:
        """Get field name."""
        return self._field

    @property
    def operator(self) -> str | None:
        """Get operator."""
        return self._operator

    @property
    def value(self) -> Any:
        """Get target value."""
        return self._value

    @property
    def logic(self) -> LogicOperator:
        """Get logic operator."""
        return self._logic

    @property
    def tags(self) -> list[str]:
        """Get tags list."""
        return self._tags.copy()

    @property
    def stages(self) -> list[str]:
        """Get stages list."""
        return self._stages.copy()

    @property
    def custom_field_type(self) -> CustomFieldType | None:
        """Get custom field type."""
        return self._custom_field_type

    @property
    def time_condition(self) -> TimeConditionType | None:
        """Get time condition type."""
        return self._time_condition

    @property
    def days(self) -> int | None:
        """Get days value."""
        return self._days

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary containing all configuration.
        """
        result: dict[str, Any] = {
            "condition_type": self._condition_type.value,
            "logic": self._logic.value,
        }

        if self._field:
            result["field"] = self._field
        if self._operator:
            result["operator"] = self._operator
        if self._value is not None:
            result["value"] = self._value
        if self._tags:
            result["tags"] = self._tags
        if self._stages:
            result["stages"] = self._stages
        if self._custom_field_type:
            result["custom_field_type"] = self._custom_field_type.value
        if self._time_condition:
            result["time_condition"] = self._time_condition.value
        if self._days is not None:
            result["days"] = self._days

        result.update(self._extra)
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConditionConfig":
        """Create from dictionary.

        Args:
            data: Dictionary containing configuration.

        Returns:
            ConditionConfig instance.
        """
        return cls(
            condition_type=data.get("condition_type", "contact_field_equals"),
            field=data.get("field"),
            operator=data.get("operator"),
            value=data.get("value"),
            logic=data.get("logic", LogicOperator.ALL),
            tags=data.get("tags"),
            stages=data.get("stages"),
            custom_field_type=data.get("custom_field_type"),
            time_condition=data.get("time_condition"),
            days=data.get("days"),
        )


class BranchCriteria:
    """Value object for branch-specific criteria.

    Attributes:
        config: Condition configuration for this branch
        percentage: Percentage for split test branches
    """

    __slots__ = ("_config", "_percentage")

    def __init__(
        self,
        config: ConditionConfig | dict[str, Any] | None = None,
        percentage: float | None = None,
    ) -> None:
        """Initialize branch criteria.

        Args:
            config: Condition configuration.
            percentage: Percentage for split tests (0-100).

        Raises:
            ValueError: If percentage is not in valid range.
        """
        if config is None:
            config = ConditionConfig(condition_type=ConditionType.CONTACT_FIELD_EQUALS)
        elif isinstance(config, dict):
            config = ConditionConfig.from_dict(config)

        object.__setattr__(self, "_config", config)

        if percentage is not None:
            if not 0 <= percentage <= 100:
                raise ValueError(f"Percentage must be between 0 and 100, got {percentage}")

        object.__setattr__(self, "_percentage", percentage)

    @property
    def config(self) -> ConditionConfig:
        """Get condition configuration."""
        return self._config

    @property
    def percentage(self) -> float | None:
        """Get percentage."""
        return self._percentage

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        result: dict[str, Any] = {"config": self._config.to_dict()}
        if self._percentage is not None:
            result["percentage"] = self._percentage
        return result
