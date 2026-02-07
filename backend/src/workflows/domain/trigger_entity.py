"""Trigger entity for workflow automation.

This module defines the Trigger entity which represents the entry point
for workflow execution. Each workflow has exactly one primary trigger.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from src.workflows.domain.triggers import (
    FilterCondition,
    TriggerEvent,
    TriggerFilters,
    TriggerSettings,
    TriggerValidationError,
)


@dataclass
class Trigger:
    """Trigger entity representing workflow entry point.

    The Trigger entity defines when and how a workflow is initiated.
    It includes the event type, filter conditions, and configuration settings.

    Attributes:
        id: Unique trigger identifier.
        workflow_id: ID of the workflow this trigger belongs to.
        event: The specific event that fires this trigger.
        filters: Filter conditions for event matching.
        settings: Trigger behavior settings.
        is_active: Whether the trigger is enabled.
        created_at: Timestamp when trigger was created.
        updated_at: Timestamp of last update.
        created_by: User who created the trigger.
    """

    id: UUID
    workflow_id: UUID
    event: TriggerEvent
    filters: TriggerFilters
    settings: TriggerSettings
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: UUID | None = None

    @classmethod
    def create(
        cls,
        workflow_id: UUID,
        event: TriggerEvent | str,
        filters: TriggerFilters | dict[str, Any] | None = None,
        settings: TriggerSettings | dict[str, Any] | None = None,
        created_by: UUID | None = None,
    ) -> "Trigger":
        """Factory method to create a new Trigger.

        Args:
            workflow_id: ID of the workflow this trigger belongs to.
            event: The trigger event (enum or string).
            filters: Filter conditions (TriggerFilters object or dict).
            settings: Trigger settings (TriggerSettings object or dict).
            created_by: User creating the trigger.

        Returns:
            A new Trigger instance.

        Raises:
            TriggerValidationError: If trigger configuration is invalid.
        """
        # Convert event to enum if string
        if isinstance(event, str):
            try:
                event = TriggerEvent(event)
            except ValueError as e:
                raise TriggerValidationError(
                    [f"Invalid trigger event: {event}. Must be one of {[e.value for e in TriggerEvent]}"]
                ) from e

        # Convert filters to object if dict
        if filters is None:
            filters = TriggerFilters()
        elif isinstance(filters, dict):
            filters = TriggerFilters.from_dict(filters)

        # Convert settings to object if dict
        if settings is None:
            settings = TriggerSettings()
        elif isinstance(settings, dict):
            settings = TriggerSettings.from_dict(settings)

        # Validate trigger configuration
        errors = cls._validate_configuration(event, filters, settings)
        if errors:
            raise TriggerValidationError(errors)

        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            workflow_id=workflow_id,
            event=event,
            filters=filters,
            settings=settings,
            is_active=True,
            created_at=now,
            updated_at=now,
            created_by=created_by,
        )

    @staticmethod
    def _validate_configuration(
        event: TriggerEvent,
        filters: TriggerFilters,
        settings: TriggerSettings,
    ) -> list[str]:
        """Validate trigger configuration.

        Args:
            event: The trigger event.
            filters: Filter conditions.
            settings: Trigger settings.

        Returns:
            List of validation error messages (empty if valid).
        """
        errors: list[str] = []

        # Validate filters are appropriate for the event type
        required_fields = Trigger._get_required_fields_for_event(event)
        if required_fields and not filters.conditions:
            errors.append(f"Event '{event.value}' requires at least one filter condition")

        # Check that filter fields are valid for this event type
        valid_fields = Trigger._get_valid_fields_for_event(event)
        for condition in filters.conditions:
            if valid_fields and condition.field not in valid_fields:
                errors.append(
                    f"Invalid filter field '{condition.field}' for event '{event.value}'. "
                    f"Valid fields: {valid_fields}"
                )

        return errors

    @staticmethod
    def _get_required_fields_for_event(event: TriggerEvent) -> list[str] | None:
        """Get required filter fields for a specific event.

        Args:
            event: The trigger event.

        Returns:
            List of required field names, or None if no required fields.
        """
        required_fields = {
            TriggerEvent.FORM_SUBMITTED: ["form_id"],
            TriggerEvent.SURVEY_COMPLETED: ["survey_id"],
            TriggerEvent.STAGE_CHANGED: ["pipeline_id", "stage_id"],
            TriggerEvent.DEAL_CREATED: ["pipeline_id"],
            TriggerEvent.APPOINTMENT_BOOKED: ["calendar_id"],
            TriggerEvent.EMAIL_OPENED: ["campaign_id", "email_id"],
            TriggerEvent.EMAIL_CLICKED: ["campaign_id"],
            TriggerEvent.SCHEDULED_DATE: ["date_field"],
            TriggerEvent.RECURRING_SCHEDULE: ["schedule_interval"],
        }
        return required_fields.get(event)

    @staticmethod
    def _get_valid_fields_for_event(event: TriggerEvent) -> list[str] | None:
        """Get valid filter fields for a specific event.

        Args:
            event: The trigger event.

        Returns:
            List of valid field names, or None if all fields are valid.
        """
        # Common fields available for all contact events
        contact_fields = [
            "tags",
            "status",
            "source",
            "lead_score",
            "custom_field.*",
            "email",
            "phone",
        ]

        # Event-specific fields
        valid_fields = {
            TriggerEvent.CONTACT_CREATED: contact_fields,
            TriggerEvent.CONTACT_UPDATED: contact_fields + ["changed_fields"],
            TriggerEvent.TAG_ADDED: ["tag"],
            TriggerEvent.TAG_REMOVED: ["tag"],
            TriggerEvent.CUSTOM_FIELD_CHANGED: ["field_name", "field_value"],
            TriggerEvent.FORM_SUBMITTED: ["form_id", "form_data.*"],
            TriggerEvent.SURVEY_COMPLETED: ["survey_id", "survey_data.*"],
            TriggerEvent.STAGE_CHANGED: ["pipeline_id", "stage_id", "previous_stage"],
            TriggerEvent.DEAL_CREATED: ["pipeline_id", "deal_value"],
            TriggerEvent.DEAL_WON: ["pipeline_id", "deal_value"],
            TriggerEvent.DEAL_LOST: ["pipeline_id", "loss_reason"],
            TriggerEvent.APPOINTMENT_BOOKED: ["calendar_id", "appointment_type"],
            TriggerEvent.APPOINTMENT_CANCELLED: ["calendar_id", "cancellation_reason"],
            TriggerEvent.APPOINTMENT_COMPLETED: ["calendar_id", "appointment_type"],
            TriggerEvent.APPOINTMENT_NO_SHOW: ["calendar_id"],
            TriggerEvent.PAYMENT_RECEIVED: ["amount", "product_id", "payment_method"],
            TriggerEvent.SUBSCRIPTION_CREATED: ["plan_id", "billing_interval"],
            TriggerEvent.SUBSCRIPTION_CANCELLED: ["plan_id", "cancellation_reason"],
            TriggerEvent.EMAIL_OPENED: ["campaign_id", "email_id", "contact_email"],
            TriggerEvent.EMAIL_CLICKED: ["campaign_id", "link_url", "contact_email"],
            TriggerEvent.SMS_RECEIVED: ["phone_number", "keyword", "message_content"],
            TriggerEvent.CALL_COMPLETED: ["phone_number", "disposition", "duration"],
            TriggerEvent.SCHEDULED_DATE: ["date_field", "date_value"],
            TriggerEvent.RECURRING_SCHEDULE: ["schedule_interval", "days_of_week"],
            TriggerEvent.BIRTHDAY: ["contact_birthday"],
            TriggerEvent.ANNIVERSARY: ["anniversary_field", "anniversary_date"],
        }

        return valid_fields.get(event)

    def evaluate(self, event_data: dict[str, Any]) -> bool:
        """Evaluate whether this trigger should fire for the given event data.

        Args:
            event_data: The event payload to evaluate.

        Returns:
            True if the trigger should fire, False otherwise.
        """
        # Check if trigger is active
        if not self.is_active:
            return False

        # Evaluate filters
        return self.filters.evaluate(event_data)

    def activate(self) -> None:
        """Activate the trigger."""
        self.is_active = True
        self._touch()

    def deactivate(self) -> None:
        """Deactivate the trigger."""
        self.is_active = False
        self._touch()

    def update(
        self,
        event: TriggerEvent | str | None = None,
        filters: TriggerFilters | dict[str, Any] | None = None,
        settings: TriggerSettings | dict[str, Any] | None = None,
        is_active: bool | None = None,
    ) -> None:
        """Update trigger properties.

        Args:
            event: New trigger event (optional).
            filters: New filter conditions (optional).
            settings: New trigger settings (optional).
            is_active: New active state (optional).
        """
        if event is not None:
            if isinstance(event, str):
                event = TriggerEvent(event)
            self.event = event

        if filters is not None:
            if isinstance(filters, dict):
                filters = TriggerFilters.from_dict(filters)
            self.filters = filters

        if settings is not None:
            if isinstance(settings, dict):
                settings = TriggerSettings.from_dict(settings)
            self.settings = settings

        if is_active is not None:
            self.is_active = is_active

        self._touch()

    def _touch(self) -> None:
        """Update the timestamp."""
        self.updated_at = datetime.now(UTC)

    def to_dict(self) -> dict[str, Any]:
        """Convert trigger to dictionary representation.

        Returns:
            Dictionary containing all trigger attributes.
        """
        return {
            "id": str(self.id),
            "workflow_id": str(self.workflow_id),
            "event": self.event.value,
            "category": self.event.get_category().value,
            "filters": self.filters.to_dict(),
            "settings": self.settings.to_dict(),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": str(self.created_by) if self.created_by else None,
        }
