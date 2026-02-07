"""Unit tests for Trigger entity.

These tests verify trigger creation, validation, update,
and evaluation logic according to SPEC-WFL-002.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from src.workflows.domain.trigger_entity import Trigger
from src.workflows.domain.triggers import (
    FilterCondition,
    FilterLogic,
    FilterOperator,
    TriggerEvent,
    TriggerFilters,
    TriggerSettings,
    TriggerValidationError,
)


class TestTriggerCreation:
    """Test suite for Trigger entity creation."""

    @pytest.fixture
    def workflow_id(self) -> UUID:
        """Fixture for workflow ID."""
        return uuid4()

    @pytest.fixture
    def user_id(self) -> UUID:
        """Fixture for user ID."""
        return uuid4()

    def test_create_minimal_trigger(self, workflow_id, user_id) -> None:
        """Test creating trigger with minimal data."""
        trigger = Trigger.create(
            workflow_id=workflow_id,
            event="contact_created",
            created_by=user_id,
        )

        assert trigger.workflow_id == workflow_id
        assert trigger.event == TriggerEvent.CONTACT_CREATED
        assert trigger.is_active is True
        assert trigger.created_by == user_id
        assert isinstance(trigger.id, UUID)
        assert isinstance(trigger.created_at, datetime)
        assert isinstance(trigger.updated_at, datetime)

    def test_create_trigger_with_filters(self, workflow_id, user_id) -> None:
        """Test creating trigger with filter conditions."""
        filters = TriggerFilters(
            conditions=[
                FilterCondition(
                    field="tags",
                    operator=FilterOperator.CONTAINS,
                    value="lead",
                )
            ],
            logic=FilterLogic.AND,
        )

        trigger = Trigger.create(
            workflow_id=workflow_id,
            event="contact_created",
            filters=filters,
            created_by=user_id,
        )

        assert len(trigger.filters.conditions) == 1
        assert trigger.filters.conditions[0].field == "tags"

    def test_create_trigger_with_settings(self, workflow_id, user_id) -> None:
        """Test creating trigger with custom settings."""
        settings = TriggerSettings(
            enrollment_limit="unlimited",
            respect_business_hours=True,
        )

        trigger = Trigger.create(
            workflow_id=workflow_id,
            event="form_submitted",
            settings=settings,
            created_by=user_id,
        )

        assert trigger.settings.enrollment_limit == "unlimited"
        assert trigger.settings.respect_business_hours is True

    def test_create_trigger_from_dict_filters(self, workflow_id, user_id) -> None:
        """Test creating trigger with filters from dict."""
        filters_dict = {
            "conditions": [
                {
                    "field": "tags",
                    "operator": "contains",
                    "value": "lead",
                }
            ],
            "logic": "AND",
        }

        trigger = Trigger.create(
            workflow_id=workflow_id,
            event="contact_created",
            filters=filters_dict,
            created_by=user_id,
        )

        assert len(trigger.filters.conditions) == 1

    def test_create_trigger_from_dict_settings(self, workflow_id, user_id) -> None:
        """Test creating trigger with settings from dict."""
        settings_dict = {
            "enrollment_limit": "multiple",
            "respect_business_hours": True,
        }

        trigger = Trigger.create(
            workflow_id=workflow_id,
            event="contact_created",
            settings=settings_dict,
            created_by=user_id,
        )

        assert trigger.settings.enrollment_limit == "multiple"

    def test_create_trigger_invalid_event(self, workflow_id, user_id) -> None:
        """Test creating trigger with invalid event raises error."""
        with pytest.raises(TriggerValidationError) as exc_info:
            Trigger.create(
                workflow_id=workflow_id,
                event="invalid_event",
                created_by=user_id,
            )

        assert "Invalid trigger event" in exc_info.value.message

    def test_create_trigger_event_as_enum(self, workflow_id, user_id) -> None:
        """Test creating trigger with event as enum."""
        trigger = Trigger.create(
            workflow_id=workflow_id,
            event=TriggerEvent.CONTACT_CREATED,
            created_by=user_id,
        )

        assert trigger.event == TriggerEvent.CONTACT_CREATED


class TestTriggerValidation:
    """Test suite for trigger configuration validation."""

    @pytest.fixture
    def workflow_id(self) -> UUID:
        """Fixture for workflow ID."""
        return uuid4()

    @pytest.fixture
    def user_id(self) -> UUID:
        """Fixture for user ID."""
        return uuid4()

    def test_form_submitted_requires_form_id_filter(self, workflow_id, user_id) -> None:
        """Test that form_submitted event requires form_id filter."""
        with pytest.raises(TriggerValidationError) as exc_info:
            Trigger.create(
                workflow_id=workflow_id,
                event="form_submitted",
                created_by=user_id,
            )

        assert "requires at least one filter condition" in exc_info.value.message

    def test_form_submitted_with_form_id_succeeds(self, workflow_id, user_id) -> None:
        """Test form_submitted with form_id filter succeeds."""
        filters = TriggerFilters(
            conditions=[
                FilterCondition(
                    field="form_id",
                    operator=FilterOperator.EQUALS,
                    value="form-123",
                )
            ]
        )

        trigger = Trigger.create(
            workflow_id=workflow_id,
            event="form_submitted",
            filters=filters,
            created_by=user_id,
        )

        assert trigger.event == TriggerEvent.FORM_SUBMITTED

    def test_stage_changed_requires_pipeline_and_stage(self, workflow_id, user_id) -> None:
        """Test stage_changed requires pipeline_id and stage_id."""
        with pytest.raises(TriggerValidationError) as exc_info:
            Trigger.create(
                workflow_id=workflow_id,
                event="stage_changed",
                created_by=user_id,
            )

        assert "requires at least one filter condition" in exc_info.value.message

    def test_stage_changed_with_required_fields(self, workflow_id, user_id) -> None:
        """Test stage_changed with required fields succeeds."""
        filters = TriggerFilters(
            conditions=[
                FilterCondition(
                    field="pipeline_id",
                    operator=FilterOperator.EQUALS,
                    value="pipeline-1",
                ),
                FilterCondition(
                    field="stage_id",
                    operator=FilterOperator.EQUALS,
                    value="stage-2",
                ),
            ]
        )

        trigger = Trigger.create(
            workflow_id=workflow_id,
            event="stage_changed",
            filters=filters,
            created_by=user_id,
        )

        assert trigger.event == TriggerEvent.STAGE_CHANGED

    def test_invalid_filter_field_for_event(self, workflow_id, user_id) -> None:
        """Test that invalid filter field raises error."""
        filters = TriggerFilters(
            conditions=[
                FilterCondition(
                    field="invalid_field",
                    operator=FilterOperator.EQUALS,
                    value="value",
                )
            ]
        )

        with pytest.raises(TriggerValidationError) as exc_info:
            Trigger.create(
                workflow_id=workflow_id,
                event="form_submitted",
                filters=filters,
                created_by=user_id,
            )

        assert "Invalid filter field" in exc_info.value.message


class TestTriggerEvaluation:
    """Test suite for trigger evaluation logic."""

    @pytest.fixture
    def workflow_id(self) -> UUID:
        """Fixture for workflow ID."""
        return uuid4()

    @pytest.fixture
    def user_id(self) -> UUID:
        """Fixture for user ID."""
        return uuid4()

    def test_evaluate_trigger_matches(self, workflow_id, user_id) -> None:
        """Test trigger evaluation when filters match."""
        filters = TriggerFilters(
            conditions=[
                FilterCondition(
                    field="tags",
                    operator=FilterOperator.CONTAINS,
                    value="lead",
                )
            ]
        )

        trigger = Trigger.create(
            workflow_id=workflow_id,
            event="contact_created",
            filters=filters,
            created_by=user_id,
        )

        event_data = {"tags": ["lead", "prospect"]}
        assert trigger.evaluate(event_data) is True

    def test_evaluate_trigger_no_match(self, workflow_id, user_id) -> None:
        """Test trigger evaluation when filters don't match."""
        filters = TriggerFilters(
            conditions=[
                FilterCondition(
                    field="tags",
                    operator=FilterOperator.CONTAINS,
                    value="vip",
                )
            ]
        )

        trigger = Trigger.create(
            workflow_id=workflow_id,
            event="contact_created",
            filters=filters,
            created_by=user_id,
        )

        event_data = {"tags": ["lead", "prospect"]}
        assert trigger.evaluate(event_data) is False

    def test_evaluate_inactive_trigger_no_match(self, workflow_id, user_id) -> None:
        """Test inactive trigger doesn't match even with valid data."""
        filters = TriggerFilters(
            conditions=[
                FilterCondition(
                    field="tags",
                    operator=FilterOperator.CONTAINS,
                    value="lead",
                )
            ]
        )

        trigger = Trigger.create(
            workflow_id=workflow_id,
            event="contact_created",
            filters=filters,
            created_by=user_id,
        )
        trigger.deactivate()

        event_data = {"tags": ["lead"]}
        assert trigger.evaluate(event_data) is False

    def test_evaluate_no_filters_matches_all(self, workflow_id, user_id) -> None:
        """Test trigger with no filters matches everything."""
        trigger = Trigger.create(
            workflow_id=workflow_id,
            event="contact_created",
            created_by=user_id,
        )

        assert trigger.evaluate({"any": "data"}) is True
        assert trigger.evaluate({}) is True

    def test_evaluate_multiple_filters_and(self, workflow_id, user_id) -> None:
        """Test multiple filters with AND logic."""
        filters = TriggerFilters(
            conditions=[
                FilterCondition(
                    field="tags",
                    operator=FilterOperator.CONTAINS,
                    value="lead",
                ),
                FilterCondition(
                    field="status",
                    operator=FilterOperator.EQUALS,
                    value="active",
                ),
            ],
            logic=FilterLogic.AND,
        )

        trigger = Trigger.create(
            workflow_id=workflow_id,
            event="contact_created",
            filters=filters,
            created_by=user_id,
        )

        # Both match
        event_data = {"tags": ["lead"], "status": "active"}
        assert trigger.evaluate(event_data) is True

        # Only one matches
        event_data = {"tags": ["lead"], "status": "inactive"}
        assert trigger.evaluate(event_data) is False


class TestTriggerUpdate:
    """Test suite for trigger update operations."""

    @pytest.fixture
    def workflow_id(self) -> UUID:
        """Fixture for workflow ID."""
        return uuid4()

    @pytest.fixture
    def user_id(self) -> UUID:
        """Fixture for user ID."""
        return uuid4()

    def test_update_trigger_event(self, workflow_id, user_id) -> None:
        """Test updating trigger event."""
        trigger = Trigger.create(
            workflow_id=workflow_id,
            event="contact_created",
            created_by=user_id,
        )

        trigger.update(event="form_submitted")

        assert trigger.event == TriggerEvent.FORM_SUBMITTED
        assert trigger.updated_at > trigger.created_at

    def test_update_trigger_filters(self, workflow_id, user_id) -> None:
        """Test updating trigger filters."""
        trigger = Trigger.create(
            workflow_id=workflow_id,
            event="contact_created",
            created_by=user_id,
        )

        new_filters = TriggerFilters(
            conditions=[
                FilterCondition(
                    field="status",
                    operator=FilterOperator.EQUALS,
                    value="active",
                )
            ]
        )

        trigger.update(filters=new_filters)

        assert len(trigger.filters.conditions) == 1
        assert trigger.filters.conditions[0].field == "status"

    def test_update_trigger_settings(self, workflow_id, user_id) -> None:
        """Test updating trigger settings."""
        trigger = Trigger.create(
            workflow_id=workflow_id,
            event="contact_created",
            created_by=user_id,
        )

        new_settings = TriggerSettings(enrollment_limit="unlimited")
        trigger.update(settings=new_settings)

        assert trigger.settings.enrollment_limit == "unlimited"

    def test_activate_trigger(self, workflow_id, user_id) -> None:
        """Test activating a trigger."""
        trigger = Trigger.create(
            workflow_id=workflow_id,
            event="contact_created",
            created_by=user_id,
        )
        trigger.deactivate()

        trigger.activate()

        assert trigger.is_active is True

    def test_deactivate_trigger(self, workflow_id, user_id) -> None:
        """Test deactivating a trigger."""
        trigger = Trigger.create(
            workflow_id=workflow_id,
            event="contact_created",
            created_by=user_id,
        )

        trigger.deactivate()

        assert trigger.is_active is False


class TestTriggerToDict:
    """Test suite for trigger serialization."""

    @pytest.fixture
    def workflow_id(self) -> UUID:
        """Fixture for workflow ID."""
        return uuid4()

    @pytest.fixture
    def user_id(self) -> UUID:
        """Fixture for user ID."""
        return uuid4()

    def test_to_dict_includes_all_fields(self, workflow_id, user_id) -> None:
        """Test to_dict includes all trigger fields."""
        filters = TriggerFilters(
            conditions=[
                FilterCondition(
                    field="tags",
                    operator=FilterOperator.CONTAINS,
                    value="lead",
                )
            ]
        )

        trigger = Trigger.create(
            workflow_id=workflow_id,
            event="contact_created",
            filters=filters,
            created_by=user_id,
        )

        result = trigger.to_dict()

        assert "id" in result
        assert "workflow_id" in result
        assert "event" in result
        assert "category" in result
        assert "filters" in result
        assert "settings" in result
        assert "is_active" in result
        assert "created_at" in result
        assert "updated_at" in result
        assert "created_by" in result

    def test_to_dict_category_is_correct(self, workflow_id, user_id) -> None:
        """Test to_dict includes correct category."""
        trigger = Trigger.create(
            workflow_id=workflow_id,
            event="contact_created",
            created_by=user_id,
        )

        result = trigger.to_dict()

        assert result["category"] == "contact"
        assert result["event"] == "contact_created"
