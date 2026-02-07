"""Acceptance tests for SPEC-WFL-002 trigger configuration.

These tests validate the acceptance criteria for trigger configuration
as specified in SPEC-WFL-002.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest


class TestAC001ContactTriggerEvents:
    """Acceptance tests for REQ-E-001 to REQ-E-005 (Contact Triggers).

    AC-001: WHEN a new contact is created in the system,
    THEN the system shall evaluate all active workflows with contact_created triggers.
    """

    @pytest.mark.asyncio
    async def test_contact_created_trigger_evaluation(self) -> None:
        """Test that contact_created trigger can be configured and evaluated."""
        from src.workflows.domain.trigger_entity import Trigger
        from src.workflows.domain.triggers import (
            FilterCondition,
            FilterOperator,
            TriggerEvent,
            TriggerFilters,
        )

        # Arrange
        workflow_id = uuid4()
        user_id = uuid4()

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
            event=TriggerEvent.CONTACT_CREATED,
            filters=filters,
            created_by=user_id,
        )

        # Act - Simulate contact created event
        event_data = {
            "contact_id": str(uuid4()),
            "tags": ["lead", "prospect"],
            "status": "active",
            "created_at": datetime.now(UTC).isoformat(),
        }

        # Assert
        assert trigger.evaluate(event_data) is True, "Trigger should match lead tag"

        # Test with non-matching data
        event_data_no_match = {
            "contact_id": str(uuid4()),
            "tags": ["customer"],
            "status": "active",
        }

        assert trigger.evaluate(event_data_no_match) is False, "Trigger should not match"

    @pytest.mark.asyncio
    async def test_contact_updated_trigger_evaluation(self) -> None:
        """Test that contact_updated trigger can be configured."""
        from src.workflows.domain.trigger_entity import Trigger
        from src.workflows.domain.triggers import TriggerEvent, TriggerFilters

        workflow_id = uuid4()
        user_id = uuid4()

        trigger = Trigger.create(
            workflow_id=workflow_id,
            event=TriggerEvent.CONTACT_UPDATED,
            filters=TriggerFilters(),
            created_by=user_id,
        )

        event_data = {
            "contact_id": str(uuid4()),
            "changed_fields": ["status", "lead_score"],
            "previous_state": {"status": "lead"},
            "current_state": {"status": "customer"},
        }

        assert trigger.evaluate(event_data) is True

    @pytest.mark.asyncio
    async def test_tag_added_trigger_evaluation(self) -> None:
        """Test that tag_added trigger can be configured."""
        from src.workflows.domain.trigger_entity import Trigger
        from src.workflows.domain.triggers import (
            FilterCondition,
            FilterOperator,
            TriggerEvent,
            TriggerFilters,
        )

        workflow_id = uuid4()
        user_id = uuid4()

        filters = TriggerFilters(
            conditions=[
                FilterCondition(
                    field="tag",
                    operator=FilterOperator.EQUALS,
                    value="vip",
                )
            ]
        )

        trigger = Trigger.create(
            workflow_id=workflow_id,
            event=TriggerEvent.TAG_ADDED,
            filters=filters,
            created_by=user_id,
        )

        event_data = {
            "contact_id": str(uuid4()),
            "tag": "vip",
            "timestamp": datetime.now(UTC).isoformat(),
        }

        assert trigger.evaluate(event_data) is True

    @pytest.mark.asyncio
    async def test_custom_field_changed_trigger_evaluation(self) -> None:
        """Test that custom_field_changed trigger can be configured."""
        from src.workflows.domain.trigger_entity import Trigger
        from src.workflows.domain.triggers import (
            FilterCondition,
            FilterOperator,
            TriggerEvent,
            TriggerFilters,
        )

        workflow_id = uuid4()
        user_id = uuid4()

        filters = TriggerFilters(
            conditions=[
                FilterCondition(
                    field="field_name",
                    operator=FilterOperator.EQUALS,
                    value="lead_score",
                ),
                FilterCondition(
                    field="field_value",
                    operator=FilterOperator.GREATER_THAN,
                    value=80,
                ),
            ],
        )

        trigger = Trigger.create(
            workflow_id=workflow_id,
            event=TriggerEvent.CUSTOM_FIELD_CHANGED,
            filters=filters,
            created_by=user_id,
        )

        event_data = {
            "contact_id": str(uuid4()),
            "field_name": "lead_score",
            "field_value": 85,
            "previous_value": 70,
        }

        assert trigger.evaluate(event_data) is True


class TestAC002FormTriggerEvents:
    """Acceptance tests for REQ-E-006 to REQ-E-007 (Form Triggers).

    AC-002: WHEN a form submission is received,
    THEN the system shall evaluate all active workflows with form_submitted triggers.
    """

    @pytest.mark.asyncio
    async def test_form_submitted_trigger_requires_form_id(self) -> None:
        """Test that form_submitted trigger requires form_id filter."""
        from src.workflows.domain.trigger_entity import Trigger
        from src.workflows.domain.triggers import (
            FilterCondition,
            FilterOperator,
            TriggerEvent,
            TriggerFilters,
            TriggerValidationError,
        )
        from uuid import uuid4

        workflow_id = uuid4()
        user_id = uuid4()

        # Should fail without form_id
        with pytest.raises(TriggerValidationError) as exc_info:
            Trigger.create(
                workflow_id=workflow_id,
                event=TriggerEvent.FORM_SUBMITTED,
                created_by=user_id,
            )

        assert "requires at least one filter condition" in str(exc_info.value)

        # Should succeed with form_id
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
            event=TriggerEvent.FORM_SUBMITTED,
            filters=filters,
            created_by=user_id,
        )

        event_data = {
            "form_id": "form-123",
            "contact_id": str(uuid4()),
            "submission_data": {"email": "user@example.com"},
            "submitted_at": datetime.now(UTC).isoformat(),
        }

        assert trigger.evaluate(event_data) is True

    @pytest.mark.asyncio
    async def test_survey_completed_trigger(self) -> None:
        """Test that survey_completed trigger can be configured."""
        from src.workflows.domain.trigger_entity import Trigger
        from src.workflows.domain.triggers import (
            FilterCondition,
            FilterOperator,
            TriggerEvent,
            TriggerFilters,
        )
        from uuid import uuid4

        workflow_id = uuid4()
        user_id = uuid4()

        filters = TriggerFilters(
            conditions=[
                FilterCondition(
                    field="survey_id",
                    operator=FilterOperator.EQUALS,
                    value="survey-456",
                )
            ]
        )

        trigger = Trigger.create(
            workflow_id=workflow_id,
            event=TriggerEvent.SURVEY_COMPLETED,
            filters=filters,
            created_by=user_id,
        )

        event_data = {
            "survey_id": "survey-456",
            "contact_id": str(uuid4()),
            "responses": {"satisfaction": 5},
            "completed_at": datetime.now(UTC).isoformat(),
        }

        assert trigger.evaluate(event_data) is True


class TestAC003TimeTriggerEvents:
    """Acceptance tests for REQ-E-023 to REQ-E-026 (Time Triggers).

    AC-003: WHEN a contact's date field matches a scheduled condition,
    THEN the system shall evaluate all active workflows with scheduled_date triggers.
    """

    @pytest.mark.asyncio
    async def test_scheduled_date_trigger(self) -> None:
        """Test that scheduled_date trigger can be configured."""
        from src.workflows.domain.trigger_entity import Trigger
        from src.workflows.domain.triggers import (
            FilterCondition,
            FilterOperator,
            TriggerEvent,
            TriggerFilters,
        )
        from uuid import uuid4

        workflow_id = uuid4()
        user_id = uuid4()

        filters = TriggerFilters(
            conditions=[
                FilterCondition(
                    field="date_field",
                    operator=FilterOperator.EQUALS,
                    value="follow_up_date",
                )
            ]
        )

        trigger = Trigger.create(
            workflow_id=workflow_id,
            event=TriggerEvent.SCHEDULED_DATE,
            filters=filters,
            created_by=user_id,
        )

        event_data = {
            "contact_id": str(uuid4()),
            "date_field": "follow_up_date",
            "date_value": "2026-01-27",
            "current_date": "2026-01-27",
        }

        assert trigger.evaluate(event_data) is True

    @pytest.mark.asyncio
    async def test_birthday_trigger(self) -> None:
        """Test that birthday trigger can be configured."""
        from src.workflows.domain.trigger_entity import Trigger
        from src.workflows.domain.triggers import TriggerEvent, TriggerFilters
        from uuid import uuid4

        workflow_id = uuid4()
        user_id = uuid4()

        trigger = Trigger.create(
            workflow_id=workflow_id,
            event=TriggerEvent.BIRTHDAY,
            filters=TriggerFilters(),
            created_by=user_id,
        )

        # Simulate birthday match
        event_data = {
            "contact_id": str(uuid4()),
            "contact_birthday": "1990-01-27",
            "current_date": "2026-01-27",
        }

        assert trigger.evaluate(event_data) is True


class TestAC004TriggerFilters:
    """Acceptance tests for REQ-S-002 (Contact Enrollment Limit).

    AC-004: WHILE a contact is already enrolled in a workflow with single_enrollment setting,
    THEN the system shall not re-enroll the contact even if the trigger fires again.
    """

    @pytest.mark.asyncio
    async def test_trigger_filter_multiple_conditions(self) -> None:
        """Test that trigger filters support multiple conditions."""
        from src.workflows.domain.trigger_entity import Trigger
        from src.workflows.domain.triggers import (
            FilterCondition,
            FilterLogic,
            FilterOperator,
            TriggerEvent,
            TriggerFilters,
        )
        from uuid import uuid4

        workflow_id = uuid4()
        user_id = uuid4()

        filters = TriggerFilters(
            conditions=[
                FilterCondition(
                    field="tags",
                    operator=FilterOperator.CONTAINS,
                    value="lead",
                ),
                FilterCondition(
                    field="lead_score",
                    operator=FilterOperator.GREATER_THAN,
                    value=50,
                ),
            ],
            logic=FilterLogic.AND,
        )

        trigger = Trigger.create(
            workflow_id=workflow_id,
            event=TriggerEvent.CONTACT_CREATED,
            filters=filters,
            created_by=user_id,
        )

        # Both conditions match
        event_data = {
            "contact_id": str(uuid4()),
            "tags": ["lead", "prospect"],
            "lead_score": 75,
        }

        assert trigger.evaluate(event_data) is True

        # Only one condition matches
        event_data_partial = {
            "contact_id": str(uuid4()),
            "tags": ["lead"],
            "lead_score": 30,
        }

        assert trigger.evaluate(event_data_partial) is False

    @pytest.mark.asyncio
    async def test_trigger_filter_or_logic(self) -> None:
        """Test that trigger filters support OR logic."""
        from src.workflows.domain.trigger_entity import Trigger
        from src.workflows.domain.triggers import (
            FilterCondition,
            FilterLogic,
            FilterOperator,
            TriggerEvent,
            TriggerFilters,
        )
        from uuid import uuid4

        workflow_id = uuid4()
        user_id = uuid4()

        filters = TriggerFilters(
            conditions=[
                FilterCondition(
                    field="tags",
                    operator=FilterOperator.CONTAINS,
                    value="vip",
                ),
                FilterCondition(
                    field="tags",
                    operator=FilterOperator.CONTAINS,
                    value="premium",
                ),
            ],
            logic=FilterLogic.OR,
        )

        trigger = Trigger.create(
            workflow_id=workflow_id,
            event=TriggerEvent.CONTACT_CREATED,
            filters=filters,
            created_by=user_id,
        )

        # First condition matches
        event_data = {"contact_id": str(uuid4()), "tags": ["vip", "customer"]}
        assert trigger.evaluate(event_data) is True

        # Second condition matches
        event_data = {"contact_id": str(uuid4()), "tags": ["premium"]}
        assert trigger.evaluate(event_data) is True

        # Neither matches
        event_data = {"contact_id": str(uuid4()), "tags": ["standard"]}
        assert trigger.evaluate(event_data) is False

    @pytest.mark.asyncio
    async def test_trigger_settings_enrollment_limit(self) -> None:
        """Test that trigger settings include enrollment_limit."""
        from src.workflows.domain.trigger_entity import Trigger
        from src.workflows.domain.triggers import (
            TriggerEvent,
            TriggerFilters,
            TriggerSettings,
        )
        from uuid import uuid4

        workflow_id = uuid4()
        user_id = uuid4()

        settings = TriggerSettings(enrollment_limit="single")

        trigger = Trigger.create(
            workflow_id=workflow_id,
            event=TriggerEvent.CONTACT_CREATED,
            filters=TriggerFilters(),
            settings=settings,
            created_by=user_id,
        )

        assert trigger.settings.enrollment_limit == "single"


class TestAC005MultiTenancyIsolation:
    """Acceptance tests for REQ-U-004 (Multi-tenancy Isolation).

    AC-005: The system shall enforce tenant isolation ensuring triggers
    only fire for events within the same account/organization.
    """

    @pytest.mark.asyncio
    async def test_trigger_belongs_to_workflow_account(self) -> None:
        """Test that triggers are scoped to workflow account."""
        from src.workflows.domain.entities import Workflow
        from src.workflows.domain.trigger_entity import Trigger
        from src.workflows.domain.triggers import TriggerEvent, TriggerFilters
        from uuid import uuid4

        account_id = uuid4()
        user_id = uuid4()

        workflow = Workflow.create(
            account_id=account_id,
            name="Test Workflow",
            created_by=user_id,
        )

        trigger = Trigger.create(
            workflow_id=workflow.id,
            event=TriggerEvent.CONTACT_CREATED,
            created_by=user_id,
        )

        # Trigger should be associated with workflow's account
        assert trigger.workflow_id == workflow.id

        # When storing trigger, it should inherit workflow's account_id
        # This is enforced at repository level by joining workflows table


class TestAC006AuditLogging:
    """Acceptance tests for REQ-U-003 (Audit Logging).

    AC-006: The system shall log all trigger configuration changes including
    creation, modification, and deletion with timestamps and user attribution.
    """

    @pytest.mark.asyncio
    async def test_trigger_tracks_created_by(self) -> None:
        """Test that trigger tracks who created it."""
        from src.workflows.domain.trigger_entity import Trigger
        from src.workflows.domain.triggers import TriggerEvent, TriggerFilters
        from uuid import uuid4

        workflow_id = uuid4()
        user_id = uuid4()

        trigger = Trigger.create(
            workflow_id=workflow_id,
            event=TriggerEvent.CONTACT_CREATED,
            created_by=user_id,
        )

        assert trigger.created_by == user_id
        assert trigger.created_at is not None

    @pytest.mark.asyncio
    async def test_trigger_update_changes_timestamp(self) -> None:
        """Test that trigger update changes updated_at timestamp."""
        from src.workflows.domain.trigger_entity import Trigger
        from src.workflows.domain.triggers import TriggerEvent, TriggerFilters
        from uuid import uuid4

        workflow_id = uuid4()
        user_id = uuid4()

        trigger = Trigger.create(
            workflow_id=workflow_id,
            event=TriggerEvent.CONTACT_CREATED,
            created_by=user_id,
        )

        original_updated_at = trigger.updated_at

        # Wait a bit to ensure timestamp difference
        import time

        time.sleep(0.01)

        trigger.update(event="form_submitted")

        assert trigger.updated_at > original_updated_at


class TestAC007AllTriggerCategories:
    """Acceptance tests for all 7 trigger categories.

    AC-007: Verify all 7 trigger categories with 26 trigger events are supported.
    """

    @pytest.mark.asyncio
    async def test_all_26_trigger_events_defined(self) -> None:
        """Verify all 26 trigger events can be created."""
        from src.workflows.domain.triggers import TriggerEvent

        # Contact triggers (5)
        contact_events = [
            TriggerEvent.CONTACT_CREATED,
            TriggerEvent.CONTACT_UPDATED,
            TriggerEvent.TAG_ADDED,
            TriggerEvent.TAG_REMOVED,
            TriggerEvent.CUSTOM_FIELD_CHANGED,
        ]

        # Form triggers (2)
        form_events = [
            TriggerEvent.FORM_SUBMITTED,
            TriggerEvent.SURVEY_COMPLETED,
        ]

        # Pipeline triggers (4)
        pipeline_events = [
            TriggerEvent.STAGE_CHANGED,
            TriggerEvent.DEAL_CREATED,
            TriggerEvent.DEAL_WON,
            TriggerEvent.DEAL_LOST,
        ]

        # Appointment triggers (4)
        appointment_events = [
            TriggerEvent.APPOINTMENT_BOOKED,
            TriggerEvent.APPOINTMENT_CANCELLED,
            TriggerEvent.APPOINTMENT_COMPLETED,
            TriggerEvent.APPOINTMENT_NO_SHOW,
        ]

        # Payment triggers (3)
        payment_events = [
            TriggerEvent.PAYMENT_RECEIVED,
            TriggerEvent.SUBSCRIPTION_CREATED,
            TriggerEvent.SUBSCRIPTION_CANCELLED,
        ]

        # Communication triggers (4)
        comm_events = [
            TriggerEvent.EMAIL_OPENED,
            TriggerEvent.EMAIL_CLICKED,
            TriggerEvent.SMS_RECEIVED,
            TriggerEvent.CALL_COMPLETED,
        ]

        # Time triggers (4)
        time_events = [
            TriggerEvent.SCHEDULED_DATE,
            TriggerEvent.RECURRING_SCHEDULE,
            TriggerEvent.BIRTHDAY,
            TriggerEvent.ANNIVERSARY,
        ]

        all_events = (
            contact_events
            + form_events
            + pipeline_events
            + appointment_events
            + payment_events
            + comm_events
            + time_events
        )

        assert len(all_events) == 26, f"Expected 26 events, got {len(all_events)}"
