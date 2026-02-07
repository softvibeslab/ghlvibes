"""Trigger domain models for the workflow module.

This module defines all trigger-related value objects, enums, and entities
for the workflow automation system. It includes 7 trigger categories with
26 trigger events as specified in SPEC-WFL-002.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal, Self
from uuid import UUID

from src.workflows.domain.exceptions import WorkflowDomainError


class TriggerCategory(str, Enum):
    """Trigger categories representing different event sources.

    The system supports 7 trigger categories:
    - contact: Contact-related events (create, update, tag changes)
    - form: Form and survey submissions
    - pipeline: Deal/opportunity stage changes
    - appointment: Appointment lifecycle events
    - payment: Payment and subscription events
    - communication: Email, SMS, and call events
    - time: Scheduled and time-based triggers
    """

    CONTACT = "contact"
    FORM = "form"
    PIPELINE = "pipeline"
    APPOINTMENT = "appointment"
    PAYMENT = "payment"
    COMMUNICATION = "communication"
    TIME = "time"


class TriggerEvent(str, Enum):
    """Specific trigger events within each category.

    There are 26 trigger events across 7 categories as specified in SPEC-WFL-002.
    """

    # Contact triggers (5 events)
    CONTACT_CREATED = "contact_created"
    CONTACT_UPDATED = "contact_updated"
    TAG_ADDED = "tag_added"
    TAG_REMOVED = "tag_removed"
    CUSTOM_FIELD_CHANGED = "custom_field_changed"

    # Form triggers (2 events)
    FORM_SUBMITTED = "form_submitted"
    SURVEY_COMPLETED = "survey_completed"

    # Pipeline triggers (4 events)
    STAGE_CHANGED = "stage_changed"
    DEAL_CREATED = "deal_created"
    DEAL_WON = "deal_won"
    DEAL_LOST = "deal_lost"

    # Appointment triggers (4 events)
    APPOINTMENT_BOOKED = "appointment_booked"
    APPOINTMENT_CANCELLED = "appointment_cancelled"
    APPOINTMENT_COMPLETED = "appointment_completed"
    APPOINTMENT_NO_SHOW = "appointment_no_show"

    # Payment triggers (3 events)
    PAYMENT_RECEIVED = "payment_received"
    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"

    # Communication triggers (4 events)
    EMAIL_OPENED = "email_opened"
    EMAIL_CLICKED = "email_clicked"
    SMS_RECEIVED = "sms_received"
    CALL_COMPLETED = "call_completed"

    # Time triggers (4 events)
    SCHEDULED_DATE = "scheduled_date"
    RECURRING_SCHEDULE = "recurring_schedule"
    BIRTHDAY = "birthday"
    ANNIVERSARY = "anniversary"

    def get_category(self) -> TriggerCategory:
        """Get the category for this trigger event.

        Returns:
            The TriggerCategory for this event.
        """
        mapping = {
            # Contact events
            TriggerEvent.CONTACT_CREATED: TriggerCategory.CONTACT,
            TriggerEvent.CONTACT_UPDATED: TriggerCategory.CONTACT,
            TriggerEvent.TAG_ADDED: TriggerCategory.CONTACT,
            TriggerEvent.TAG_REMOVED: TriggerCategory.CONTACT,
            TriggerEvent.CUSTOM_FIELD_CHANGED: TriggerCategory.CONTACT,
            # Form events
            TriggerEvent.FORM_SUBMITTED: TriggerCategory.FORM,
            TriggerEvent.SURVEY_COMPLETED: TriggerCategory.FORM,
            # Pipeline events
            TriggerEvent.STAGE_CHANGED: TriggerCategory.PIPELINE,
            TriggerEvent.DEAL_CREATED: TriggerCategory.PIPELINE,
            TriggerEvent.DEAL_WON: TriggerCategory.PIPELINE,
            TriggerEvent.DEAL_LOST: TriggerCategory.PIPELINE,
            # Appointment events
            TriggerEvent.APPOINTMENT_BOOKED: TriggerCategory.APPOINTMENT,
            TriggerEvent.APPOINTMENT_CANCELLED: TriggerCategory.APPOINTMENT,
            TriggerEvent.APPOINTMENT_COMPLETED: TriggerCategory.APPOINTMENT,
            TriggerEvent.APPOINTMENT_NO_SHOW: TriggerCategory.APPOINTMENT,
            # Payment events
            TriggerEvent.PAYMENT_RECEIVED: TriggerCategory.PAYMENT,
            TriggerEvent.SUBSCRIPTION_CREATED: TriggerCategory.PAYMENT,
            TriggerEvent.SUBSCRIPTION_CANCELLED: TriggerCategory.PAYMENT,
            # Communication events
            TriggerEvent.EMAIL_OPENED: TriggerCategory.COMMUNICATION,
            TriggerEvent.EMAIL_CLICKED: TriggerCategory.COMMUNICATION,
            TriggerEvent.SMS_RECEIVED: TriggerCategory.COMMUNICATION,
            TriggerEvent.CALL_COMPLETED: TriggerCategory.COMMUNICATION,
            # Time events
            TriggerEvent.SCHEDULED_DATE: TriggerCategory.TIME,
            TriggerEvent.RECURRING_SCHEDULE: TriggerCategory.TIME,
            TriggerEvent.BIRTHDAY: TriggerCategory.TIME,
            TriggerEvent.ANNIVERSARY: TriggerCategory.TIME,
        }
        return mapping[self]


class FilterOperator(str, Enum):
    """Filter condition operators for trigger filters.

    These operators define how to compare field values against conditions.
    """

    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    IN = "in"
    NOT_IN = "not_in"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"


class FilterLogic(str, Enum):
    """Logic operators for combining multiple filter conditions."""

    AND = "AND"
    OR = "OR"


@dataclass(frozen=True)
class FilterCondition:
    """A single filter condition for trigger evaluation.

    Filter conditions define the criteria for matching events.

    Attributes:
        field: The field to evaluate (e.g., "tags", "status", "custom_field.email").
        operator: The comparison operator.
        value: The value to compare against (can be string, number, list, etc.).
    """

    field: str
    operator: FilterOperator
    value: Any = None

    def __post_init__(self) -> None:
        """Validate filter condition after initialization."""
        # Validate that operator doesn't require a value when none is provided
        no_value_operators = {
            FilterOperator.IS_EMPTY,
            FilterOperator.IS_NOT_EMPTY,
        }
        if self.operator in no_value_operators and self.value is not None:
            raise ValueError(f"Operator {self.operator.value} does not accept a value")

        # Validate that operator requiring a value has one
        value_operators = {
            FilterOperator.EQUALS,
            FilterOperator.NOT_EQUALS,
            FilterOperator.CONTAINS,
            FilterOperator.NOT_CONTAINS,
            FilterOperator.GREATER_THAN,
            FilterOperator.LESS_THAN,
            FilterOperator.GREATER_THAN_OR_EQUAL,
            FilterOperator.LESS_THAN_OR_EQUAL,
            FilterOperator.IN,
            FilterOperator.NOT_IN,
            FilterOperator.STARTS_WITH,
            FilterOperator.ENDS_WITH,
        }
        if self.operator in value_operators and self.value is None:
            raise ValueError(f"Operator {self.operator.value} requires a value")

    def evaluate(self, data: dict[str, Any]) -> bool:
        """Evaluate this filter condition against event data.

        Args:
            data: The event data to evaluate.

        Returns:
            True if the condition matches, False otherwise.
        """
        # Get field value from nested data using dot notation
        field_value = self._get_nested_value(data, self.field)

        # Apply operator logic
        if self.operator == FilterOperator.EQUALS:
            return field_value == self.value
        elif self.operator == FilterOperator.NOT_EQUALS:
            return field_value != self.value
        elif self.operator == FilterOperator.CONTAINS:
            return self._contains(field_value, self.value)
        elif self.operator == FilterOperator.NOT_CONTAINS:
            return not self._contains(field_value, self.value)
        elif self.operator == FilterOperator.GREATER_THAN:
            return self._compare(field_value, self.value, lambda a, b: a > b)
        elif self.operator == FilterOperator.LESS_THAN:
            return self._compare(field_value, self.value, lambda a, b: a < b)
        elif self.operator == FilterOperator.GREATER_THAN_OR_EQUAL:
            return self._compare(field_value, self.value, lambda a, b: a >= b)
        elif self.operator == FilterOperator.LESS_THAN_OR_EQUAL:
            return self._compare(field_value, self.value, lambda a, b: a <= b)
        elif self.operator == FilterOperator.IN:
            return field_value in self.value if isinstance(self.value, (list, set, tuple)) else False
        elif self.operator == FilterOperator.NOT_IN:
            return field_value not in self.value if isinstance(self.value, (list, set, tuple)) else True
        elif self.operator == FilterOperator.STARTS_WITH:
            return isinstance(field_value, str) and str(field_value).startswith(str(self.value))
        elif self.operator == FilterOperator.ENDS_WITH:
            return isinstance(field_value, str) and str(field_value).endswith(str(self.value))
        elif self.operator == FilterOperator.IS_EMPTY:
            return field_value is None or field_value == "" or (isinstance(field_value, (list, set)) and len(field_value) == 0)
        elif self.operator == FilterOperator.IS_NOT_EMPTY:
            return field_value is not None and field_value != "" and (not isinstance(field_value, (list, set)) or len(field_value) > 0)
        else:
            return False

    def _get_nested_value(self, data: dict[str, Any], field_path: str) -> Any:
        """Get value from nested dict using dot notation.

        Args:
            data: The data dictionary.
            field_path: Dot-separated field path (e.g., "contact.tags").

        Returns:
            The value at the field path, or None if not found.
        """
        keys = field_path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value

    def _contains(self, field_value: Any, target: Any) -> bool:
        """Check if field_value contains target.

        Handles strings, lists, and sets.
        """
        if isinstance(field_value, str):
            return target in field_value
        if isinstance(field_value, (list, set, tuple)):
            return target in field_value
        return False

    def _compare(self, field_value: Any, target: Any, comparator) -> bool:
        """Compare two values using the provided comparator.

        Args:
            field_value: The field value.
            target: The target value.
            comparator: Comparison function (e.g., lambda a, b: a > b).

        Returns:
            Result of comparison, or False if types are incompatible.
        """
        try:
            return comparator(field_value, target)
        except (TypeError, AttributeError):
            return False


@dataclass(frozen=True)
class TriggerFilters:
    """Trigger filter conditions with logic for combining them.

    Filters define which events should trigger workflow enrollment.
    Multiple conditions can be combined with AND/OR logic.

    Attributes:
        conditions: List of filter conditions.
        logic: How to combine conditions (AND or OR).
    """

    conditions: list[FilterCondition] = field(default_factory=list)
    logic: FilterLogic = FilterLogic.AND

    def __post_init__(self) -> None:
        """Validate trigger filters after initialization."""
        if not isinstance(self.conditions, list):
            raise ValueError("conditions must be a list")

        if not isinstance(self.logic, FilterLogic):
            raise ValueError(f"logic must be FilterLogic, got {type(self.logic)}")

        if len(self.conditions) > 20:
            raise ValueError("Maximum 20 filter conditions allowed per trigger")

    def evaluate(self, data: dict[str, Any]) -> bool:
        """Evaluate all filter conditions against event data.

        Args:
            data: The event data to evaluate.

        Returns:
            True if the filters match, False otherwise.
        """
        if not self.conditions:
            return True  # No filters means match everything

        results = [condition.evaluate(data) for condition in self.conditions]

        if self.logic == FilterLogic.AND:
            return all(results)
        else:  # OR
            return any(results)

    def to_dict(self) -> dict[str, Any]:
        """Convert filters to dictionary representation.

        Returns:
            Dictionary with conditions and logic.
        """
        return {
            "conditions": [
                {
                    "field": c.field,
                    "operator": c.operator.value,
                    "value": c.value,
                }
                for c in self.conditions
            ],
            "logic": self.logic.value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create TriggerFilters from dictionary representation.

        Args:
            data: Dictionary with conditions and logic.

        Returns:
            TriggerFilters instance.
        """
        conditions = [
            FilterCondition(
                field=c["field"],
                operator=FilterOperator(c["operator"]),
                value=c.get("value"),
            )
            for c in data.get("conditions", [])
        ]
        logic = FilterLogic(data.get("logic", "AND"))
        return cls(conditions=conditions, logic=logic)


@dataclass(frozen=True)
class TriggerSettings:
    """Trigger configuration settings.

    Settings control trigger behavior such as enrollment limits,
    business hours, and retry logic.

    Attributes:
        enrollment_limit: How many times a contact can enroll ("single", "multiple", "unlimited").
        respect_business_hours: Only trigger during business hours.
        retry_on_failure: Retry workflow execution on failure.
        max_retries: Maximum number of retry attempts.
    """

    enrollment_limit: Literal["single", "multiple", "unlimited"] = "single"
    respect_business_hours: bool = False
    retry_on_failure: bool = False
    max_retries: int = 3

    def __post_init__(self) -> None:
        """Validate trigger settings after initialization."""
        if self.enrollment_limit not in ("single", "multiple", "unlimited"):
            raise ValueError(f"Invalid enrollment_limit: {self.enrollment_limit}")

        if self.max_retries < 0 or self.max_retries > 10:
            raise ValueError("max_retries must be between 0 and 10")

    def to_dict(self) -> dict[str, Any]:
        """Convert settings to dictionary representation."""
        return {
            "enrollment_limit": self.enrollment_limit,
            "respect_business_hours": self.respect_business_hours,
            "retry_on_failure": self.retry_on_failure,
            "max_retries": self.max_retries,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create TriggerSettings from dictionary representation."""
        return cls(
            enrollment_limit=data.get("enrollment_limit", "single"),
            respect_business_hours=data.get("respect_business_hours", False),
            retry_on_failure=data.get("retry_on_failure", False),
            max_retries=data.get("max_retries", 3),
        )


class TriggerValidationError(WorkflowDomainError):
    """Raised when trigger configuration fails validation."""

    def __init__(self, errors: list[str]) -> None:
        """Initialize with validation errors.

        Args:
            errors: List of validation error messages.
        """
        message = f"Trigger validation failed: {'; '.join(errors)}"
        super().__init__(message)
        self.errors = errors
