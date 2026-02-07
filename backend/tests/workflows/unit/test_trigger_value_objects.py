"""Unit tests for trigger value objects and enums.

These tests verify that trigger categories, events, filters, and settings
work correctly according to SPEC-WFL-002.
"""

from typing import Any

import pytest

from src.workflows.domain.triggers import (
    FilterCondition,
    FilterLogic,
    FilterOperator,
    TriggerCategory,
    TriggerEvent,
    TriggerFilters,
    TriggerSettings,
    TriggerValidationError,
)


class TestTriggerEvent:
    """Test suite for TriggerEvent enum."""

    def test_all_26_trigger_events_defined(self) -> None:
        """Verify all 26 trigger events from SPEC are defined."""
        # Contact triggers (5 events)
        assert TriggerEvent.CONTACT_CREATED
        assert TriggerEvent.CONTACT_UPDATED
        assert TriggerEvent.TAG_ADDED
        assert TriggerEvent.TAG_REMOVED
        assert TriggerEvent.CUSTOM_FIELD_CHANGED

        # Form triggers (2 events)
        assert TriggerEvent.FORM_SUBMITTED
        assert TriggerEvent.SURVEY_COMPLETED

        # Pipeline triggers (4 events)
        assert TriggerEvent.STAGE_CHANGED
        assert TriggerEvent.DEAL_CREATED
        assert TriggerEvent.DEAL_WON
        assert TriggerEvent.DEAL_LOST

        # Appointment triggers (4 events)
        assert TriggerEvent.APPOINTMENT_BOOKED
        assert TriggerEvent.APPOINTMENT_CANCELLED
        assert TriggerEvent.APPOINTMENT_COMPLETED
        assert TriggerEvent.APPOINTMENT_NO_SHOW

        # Payment triggers (3 events)
        assert TriggerEvent.PAYMENT_RECEIVED
        assert TriggerEvent.SUBSCRIPTION_CREATED
        assert TriggerEvent.SUBSCRIPTION_CANCELLED

        # Communication triggers (4 events)
        assert TriggerEvent.EMAIL_OPENED
        assert TriggerEvent.EMAIL_CLICKED
        assert TriggerEvent.SMS_RECEIVED
        assert TriggerEvent.CALL_COMPLETED

        # Time triggers (4 events)
        assert TriggerEvent.SCHEDULED_DATE
        assert TriggerEvent.RECURRING_SCHEDULE
        assert TriggerEvent.BIRTHDAY
        assert TriggerEvent.ANNIVERSARY

    def test_get_category_for_contact_events(self) -> None:
        """Verify contact events map to CONTACT category."""
        contact_events = [
            TriggerEvent.CONTACT_CREATED,
            TriggerEvent.CONTACT_UPDATED,
            TriggerEvent.TAG_ADDED,
            TriggerEvent.TAG_REMOVED,
            TriggerEvent.CUSTOM_FIELD_CHANGED,
        ]

        for event in contact_events:
            assert event.get_category() == TriggerCategory.CONTACT

    def test_get_category_for_form_events(self) -> None:
        """Verify form events map to FORM category."""
        assert TriggerEvent.FORM_SUBMITTED.get_category() == TriggerCategory.FORM
        assert TriggerEvent.SURVEY_COMPLETED.get_category() == TriggerCategory.FORM

    def test_get_category_for_pipeline_events(self) -> None:
        """Verify pipeline events map to PIPELINE category."""
        pipeline_events = [
            TriggerEvent.STAGE_CHANGED,
            TriggerEvent.DEAL_CREATED,
            TriggerEvent.DEAL_WON,
            TriggerEvent.DEAL_LOST,
        ]

        for event in pipeline_events:
            assert event.get_category() == TriggerCategory.PIPELINE

    def test_get_category_for_appointment_events(self) -> None:
        """Verify appointment events map to APPOINTMENT category."""
        appointment_events = [
            TriggerEvent.APPOINTMENT_BOOKED,
            TriggerEvent.APPOINTMENT_CANCELLED,
            TriggerEvent.APPOINTMENT_COMPLETED,
            TriggerEvent.APPOINTMENT_NO_SHOW,
        ]

        for event in appointment_events:
            assert event.get_category() == TriggerCategory.APPOINTMENT

    def test_get_category_for_payment_events(self) -> None:
        """Verify payment events map to PAYMENT category."""
        payment_events = [
            TriggerEvent.PAYMENT_RECEIVED,
            TriggerEvent.SUBSCRIPTION_CREATED,
            TriggerEvent.SUBSCRIPTION_CANCELLED,
        ]

        for event in payment_events:
            assert event.get_category() == TriggerCategory.PAYMENT

    def test_get_category_for_communication_events(self) -> None:
        """Verify communication events map to COMMUNICATION category."""
        comm_events = [
            TriggerEvent.EMAIL_OPENED,
            TriggerEvent.EMAIL_CLICKED,
            TriggerEvent.SMS_RECEIVED,
            TriggerEvent.CALL_COMPLETED,
        ]

        for event in comm_events:
            assert event.get_category() == TriggerCategory.COMMUNICATION

    def test_get_category_for_time_events(self) -> None:
        """Verify time events map to TIME category."""
        time_events = [
            TriggerEvent.SCHEDULED_DATE,
            TriggerEvent.RECURRING_SCHEDULE,
            TriggerEvent.BIRTHDAY,
            TriggerEvent.ANNIVERSARY,
        ]

        for event in time_events:
            assert event.get_category() == TriggerCategory.TIME


class TestFilterCondition:
    """Test suite for FilterCondition value object."""

    def test_create_filter_condition(self) -> None:
        """Test creating a filter condition."""
        condition = FilterCondition(
            field="tags",
            operator=FilterOperator.CONTAINS,
            value="lead",
        )

        assert condition.field == "tags"
        assert condition.operator == FilterOperator.CONTAINS
        assert condition.value == "lead"

    def test_filter_condition_equality_string(self) -> None:
        """Test equals operator with string values."""
        condition = FilterCondition(
            field="status",
            operator=FilterOperator.EQUALS,
            value="active",
        )

        data = {"status": "active"}
        assert condition.evaluate(data) is True

        data = {"status": "inactive"}
        assert condition.evaluate(data) is False

    def test_filter_condition_contains_list(self) -> None:
        """Test contains operator with list values."""
        condition = FilterCondition(
            field="tags",
            operator=FilterOperator.CONTAINS,
            value="lead",
        )

        data = {"tags": ["lead", "prospect"]}
        assert condition.evaluate(data) is True

        data = {"tags": ["prospect", "customer"]}
        assert condition.evaluate(data) is False

    def test_filter_condition_contains_string(self) -> None:
        """Test contains operator with string values."""
        condition = FilterCondition(
            field="email",
            operator=FilterOperator.CONTAINS,
            value="@example.com",
        )

        data = {"email": "user@example.com"}
        assert condition.evaluate(data) is True

        data = {"email": "user@other.com"}
        assert condition.evaluate(data) is False

    def test_filter_condition_greater_than(self) -> None:
        """Test greater_than operator."""
        condition = FilterCondition(
            field="lead_score",
            operator=FilterOperator.GREATER_THAN,
            value=50,
        )

        data = {"lead_score": 75}
        assert condition.evaluate(data) is True

        data = {"lead_score": 25}
        assert condition.evaluate(data) is False

    def test_filter_condition_less_than(self) -> None:
        """Test less_than operator."""
        condition = FilterCondition(
            field="age",
            operator=FilterOperator.LESS_THAN,
            value=30,
        )

        data = {"age": 25}
        assert condition.evaluate(data) is True

        data = {"age": 35}
        assert condition.evaluate(data) is False

    def test_filter_condition_in(self) -> None:
        """Test in operator."""
        condition = FilterCondition(
            field="status",
            operator=FilterOperator.IN,
            value=["active", "pending"],
        )

        data = {"status": "active"}
        assert condition.evaluate(data) is True

        data = {"status": "inactive"}
        assert condition.evaluate(data) is False

    def test_filter_condition_nested_field(self) -> None:
        """Test filter condition with nested field path."""
        condition = FilterCondition(
            field="contact.tags",
            operator=FilterOperator.CONTAINS,
            value="vip",
        )

        data = {"contact": {"tags": ["vip", "customer"]}}
        assert condition.evaluate(data) is True

        data = {"contact": {"tags": ["customer"]}}
        assert condition.evaluate(data) is False

    def test_filter_condition_is_empty(self) -> None:
        """Test is_empty operator."""
        condition = FilterCondition(
            field="tags",
            operator=FilterOperator.IS_EMPTY,
        )

        data = {"tags": []}
        assert condition.evaluate(data) is True

        data = {"tags": None}
        assert condition.evaluate(data) is True

        data = {"tags": ["lead"]}
        assert condition.evaluate(data) is False

    def test_filter_condition_is_not_empty(self) -> None:
        """Test is_not_empty operator."""
        condition = FilterCondition(
            field="tags",
            operator=FilterOperator.IS_NOT_EMPTY,
        )

        data = {"tags": ["lead"]}
        assert condition.evaluate(data) is True

        data = {"tags": []}
        assert condition.evaluate(data) is False

        data = {"tags": None}
        assert condition.evaluate(data) is False

    def test_filter_condition_starts_with(self) -> None:
        """Test starts_with operator."""
        condition = FilterCondition(
            field="email",
            operator=FilterOperator.STARTS_WITH,
            value="admin",
        )

        data = {"email": "admin@example.com"}
        assert condition.evaluate(data) is True

        data = {"email": "user@example.com"}
        assert condition.evaluate(data) is False

    def test_filter_condition_ends_with(self) -> None:
        """Test ends_with operator."""
        condition = FilterCondition(
            field="phone",
            operator=FilterOperator.ENDS_WITH,
            value="99",
        )

        data = {"phone": "+1234567899"}
        assert condition.evaluate(data) is True

        data = {"phone": "+1234567888"}
        assert condition.evaluate(data) is False


class TestTriggerFilters:
    """Test suite for TriggerFilters value object."""

    def test_create_empty_filters(self) -> None:
        """Test creating filters with no conditions."""
        filters = TriggerFilters()

        assert filters.conditions == []
        assert filters.logic == FilterLogic.AND

    def test_create_filters_with_conditions(self) -> None:
        """Test creating filters with conditions."""
        conditions = [
            FilterCondition(field="tags", operator=FilterOperator.CONTAINS, value="lead"),
            FilterCondition(field="status", operator=FilterOperator.EQUALS, value="active"),
        ]
        filters = TriggerFilters(conditions=conditions, logic=FilterLogic.AND)

        assert len(filters.conditions) == 2
        assert filters.logic == FilterLogic.AND

    def test_filters_max_20_conditions(self) -> None:
        """Test that more than 20 conditions raises error."""
        conditions = [
            FilterCondition(field=f"field_{i}", operator=FilterOperator.EQUALS, value=i)
            for i in range(21)
        ]

        with pytest.raises(ValueError, match="Maximum 20 filter conditions"):
            TriggerFilters(conditions=conditions)

    def test_filters_evaluate_and_logic(self) -> None:
        """Test AND logic - all conditions must match."""
        conditions = [
            FilterCondition(field="tags", operator=FilterOperator.CONTAINS, value="lead"),
            FilterCondition(field="status", operator=FilterOperator.EQUALS, value="active"),
        ]
        filters = TriggerFilters(conditions=conditions, logic=FilterLogic.AND)

        # Both match
        data = {"tags": ["lead", "prospect"], "status": "active"}
        assert filters.evaluate(data) is True

        # Only one matches
        data = {"tags": ["lead"], "status": "inactive"}
        assert filters.evaluate(data) is False

    def test_filters_evaluate_or_logic(self) -> None:
        """Test OR logic - at least one condition must match."""
        conditions = [
            FilterCondition(field="tags", operator=FilterOperator.CONTAINS, value="lead"),
            FilterCondition(field="tags", operator=FilterOperator.CONTAINS, value="vip"),
        ]
        filters = TriggerFilters(conditions=conditions, logic=FilterLogic.OR)

        # Both match
        data = {"tags": ["lead", "vip"]}
        assert filters.evaluate(data) is True

        # One matches
        data = {"tags": ["lead"]}
        assert filters.evaluate(data) is True

        # None match
        data = {"tags": ["customer"]}
        assert filters.evaluate(data) is False

    def test_filters_no_conditions_match_all(self) -> None:
        """Test that empty filters match everything."""
        filters = TriggerFilters()

        data = {"any": "data"}
        assert filters.evaluate(data) is True

        assert filters.evaluate({}) is True

    def test_filters_to_dict(self) -> None:
        """Test converting filters to dictionary."""
        conditions = [
            FilterCondition(field="tags", operator=FilterOperator.CONTAINS, value="lead"),
        ]
        filters = TriggerFilters(conditions=conditions, logic=FilterLogic.AND)

        result = filters.to_dict()

        assert result == {
            "conditions": [
                {
                    "field": "tags",
                    "operator": "contains",
                    "value": "lead",
                }
            ],
            "logic": "AND",
        }

    def test_filters_from_dict(self) -> None:
        """Test creating filters from dictionary."""
        data = {
            "conditions": [
                {
                    "field": "tags",
                    "operator": "contains",
                    "value": "lead",
                }
            ],
            "logic": "OR",
        }

        filters = TriggerFilters.from_dict(data)

        assert len(filters.conditions) == 1
        assert filters.conditions[0].field == "tags"
        assert filters.conditions[0].operator == FilterOperator.CONTAINS
        assert filters.conditions[0].value == "lead"
        assert filters.logic == FilterLogic.OR


class TestTriggerSettings:
    """Test suite for TriggerSettings value object."""

    def test_create_default_settings(self) -> None:
        """Test creating settings with defaults."""
        settings = TriggerSettings()

        assert settings.enrollment_limit == "single"
        assert settings.respect_business_hours is False
        assert settings.retry_on_failure is False
        assert settings.max_retries == 3

    def test_create_custom_settings(self) -> None:
        """Test creating custom settings."""
        settings = TriggerSettings(
            enrollment_limit="unlimited",
            respect_business_hours=True,
            retry_on_failure=True,
            max_retries=5,
        )

        assert settings.enrollment_limit == "unlimited"
        assert settings.respect_business_hours is True
        assert settings.retry_on_failure is True
        assert settings.max_retries == 5

    def test_settings_invalid_enrollment_limit(self) -> None:
        """Test invalid enrollment limit raises error."""
        with pytest.raises(ValueError, match="Invalid enrollment_limit"):
            TriggerSettings(enrollment_limit="invalid")  # type: ignore

    def test_settings_max_retries_bounds(self) -> None:
        """Test max_retries must be between 0 and 10."""
        with pytest.raises(ValueError, match="max_retries must be between 0 and 10"):
            TriggerSettings(max_retries=11)

        with pytest.raises(ValueError, match="max_retries must be between 0 and 10"):
            TriggerSettings(max_retries=-1)

    def test_settings_to_dict(self) -> None:
        """Test converting settings to dictionary."""
        settings = TriggerSettings(
            enrollment_limit="multiple",
            respect_business_hours=True,
        )

        result = settings.to_dict()

        assert result == {
            "enrollment_limit": "multiple",
            "respect_business_hours": True,
            "retry_on_failure": False,
            "max_retries": 3,
        }

    def test_settings_from_dict(self) -> None:
        """Test creating settings from dictionary."""
        data = {
            "enrollment_limit": "unlimited",
            "respect_business_hours": True,
            "retry_on_failure": True,
            "max_retries": 5,
        }

        settings = TriggerSettings.from_dict(data)

        assert settings.enrollment_limit == "unlimited"
        assert settings.respect_business_hours is True
        assert settings.retry_on_failure is True
        assert settings.max_retries == 5
