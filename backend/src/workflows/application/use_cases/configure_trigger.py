"""Use cases for trigger configuration.

This module provides use cases for creating, updating, and testing
workflow triggers as specified in SPEC-WFL-002.
"""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from src.workflows.domain.trigger_entity import Trigger
from src.workflows.domain.triggers import (
    TriggerEvent,
    TriggerFilters,
    TriggerSettings,
    TriggerValidationError,
)
from src.workflows.infrastructure.trigger_repository import TriggerRepository


class ConfigureTriggerRequest(BaseModel):
    """Request DTO for configuring a workflow trigger.

    This validates the trigger configuration data.
    """

    event: str = Field(
        ...,
        description="Trigger event (e.g., 'contact_created', 'form_submitted')",
        examples=["contact_created", "form_submitted", "tag_added"],
    )
    filters: dict[str, Any] | None = Field(
        default=None,
        description="Filter conditions for event matching",
        examples=[
            {
                "conditions": [
                    {"field": "tags", "operator": "contains", "value": "lead"}
                ],
                "logic": "AND",
            }
        ],
    )
    settings: dict[str, Any] | None = Field(
        default=None,
        description="Trigger behavior settings",
        examples=[
            {
                "enrollment_limit": "single",
                "respect_business_hours": True,
            }
        ],
    )


class TriggerResponse(BaseModel):
    """Response DTO for a trigger."""

    id: UUID = Field(description="Trigger ID")
    workflow_id: UUID = Field(description="Workflow ID")
    event: str = Field(description="Trigger event")
    category: str = Field(description="Trigger category")
    filters: dict[str, Any] = Field(description="Filter conditions")
    settings: dict[str, Any] = Field(description="Trigger settings")
    is_active: bool = Field(description="Whether trigger is active")
    created_at: str = Field(description="Creation timestamp")
    updated_at: str = Field(description="Last update timestamp")
    created_by: UUID | None = Field(description="User who created trigger")

    @classmethod
    def from_entity(cls, trigger: Trigger) -> "TriggerResponse":
        """Create response from domain entity.

        Args:
            trigger: The Trigger domain entity.

        Returns:
            TriggerResponse instance.
        """
        data = trigger.to_dict()
        return cls(
            id=trigger.id,
            workflow_id=trigger.workflow_id,
            event=trigger.event.value,
            category=trigger.event.get_category().value,
            filters=trigger.filters.to_dict(),
            settings=trigger.settings.to_dict(),
            is_active=trigger.is_active,
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            created_by=trigger.created_by,
        )


class TestTriggerRequest(BaseModel):
    """Request DTO for testing a trigger."""

    contact_id: UUID = Field(description="Contact ID to test with")
    simulate_event_data: dict[str, Any] = Field(
        ...,
        description="Simulated event data",
        examples=[
            {
                "contact_id": "uuid",
                "tags": ["lead", "prospect"],
                "status": "active",
            }
        ],
    )


class TestTriggerResult(BaseModel):
    """Result of trigger testing."""

    matched: bool = Field(description="Whether filters matched")
    would_enroll: bool = Field(description="Whether contact would be enrolled")
    filter_results: list[dict[str, Any]] = Field(
        description="Individual filter condition results"
    )


@dataclass
class ConfigureTriggerResult:
    """Result of configure trigger use case."""

    success: bool
    trigger: TriggerResponse | None = None
    error: str | None = None


class ConfigureTriggerUseCase:
    """Use case for configuring workflow triggers.

    This use case handles creating and updating triggers with proper validation.
    """

    def __init__(
        self,
        trigger_repository: TriggerRepository,
    ) -> None:
        """Initialize the use case with dependencies.

        Args:
            trigger_repository: Repository for trigger persistence.
        """
        self._trigger_repository = trigger_repository

    async def execute(
        self,
        workflow_id: UUID,
        request: ConfigureTriggerRequest,
        created_by: UUID | None = None,
    ) -> ConfigureTriggerResult:
        """Configure a trigger for a workflow.

        Args:
            workflow_id: The workflow ID.
            request: The trigger configuration request.
            created_by: User creating the trigger.

        Returns:
            ConfigureTriggerResult with the outcome.
        """
        try:
            # Create trigger entity
            trigger = Trigger.create(
                workflow_id=workflow_id,
                event=request.event,
                filters=request.filters,
                settings=request.settings,
                created_by=created_by,
            )

            # Check if trigger already exists for workflow
            existing = await self._trigger_repository.get_by_workflow_id(workflow_id)

            if existing:
                # Update existing trigger
                trigger.id = existing.id
                trigger.created_at = existing.created_at
                trigger.created_by = existing.created_by
                await self._trigger_repository.update(trigger)
            else:
                # Create new trigger
                await self._trigger_repository.create(trigger)

            return ConfigureTriggerResult(
                success=True,
                trigger=TriggerResponse.from_entity(trigger),
            )

        except TriggerValidationError as e:
            return ConfigureTriggerResult(
                success=False,
                error=e.message,
            )


class GetTriggerUseCase:
    """Use case for retrieving a workflow trigger."""

    def __init__(self, trigger_repository: TriggerRepository) -> None:
        """Initialize with repository."""
        self._trigger_repository = trigger_repository

    async def execute(self, workflow_id: UUID) -> TriggerResponse | None:
        """Get trigger by workflow ID.

        Args:
            workflow_id: The workflow ID.

        Returns:
            TriggerResponse if found, None otherwise.
        """
        trigger = await self._trigger_repository.get_by_workflow_id(workflow_id)
        return TriggerResponse.from_entity(trigger) if trigger else None


class UpdateTriggerUseCase:
    """Use case for updating a workflow trigger."""

    def __init__(self, trigger_repository: TriggerRepository) -> None:
        """Initialize with repository."""
        self._trigger_repository = trigger_repository

    async def execute(
        self,
        workflow_id: UUID,
        event: str | None = None,
        filters: dict[str, Any] | None = None,
        settings: dict[str, Any] | None = None,
        is_active: bool | None = None,
    ) -> TriggerResponse | None:
        """Update a workflow trigger.

        Args:
            workflow_id: The workflow ID.
            event: New trigger event (optional).
            filters: New filter conditions (optional).
            settings: New trigger settings (optional).
            is_active: New active state (optional).

        Returns:
            Updated TriggerResponse if successful, None if not found.
        """
        trigger = await self._trigger_repository.get_by_workflow_id(workflow_id)
        if not trigger:
            return None

        # Update trigger entity
        trigger.update(
            event=event,
            filters=filters,
            settings=settings,
            is_active=is_active,
        )

        # Persist changes
        await self._trigger_repository.update(trigger)

        return TriggerResponse.from_entity(trigger)


class DeleteTriggerUseCase:
    """Use case for deleting a workflow trigger."""

    def __init__(self, trigger_repository: TriggerRepository) -> None:
        """Initialize with repository."""
        self._trigger_repository = trigger_repository

    async def execute(self, workflow_id: UUID) -> bool:
        """Delete a workflow trigger.

        Args:
            workflow_id: The workflow ID.

        Returns:
            True if deleted, False if not found.
        """
        trigger = await self._trigger_repository.get_by_workflow_id(workflow_id)
        if not trigger:
            return False

        return await self._trigger_repository.delete(trigger.id)


class TestTriggerUseCase:
    """Use case for testing a trigger configuration."""

    def __init__(self, trigger_repository: TriggerRepository) -> None:
        """Initialize with repository."""
        self._trigger_repository = trigger_repository

    async def execute(
        self,
        workflow_id: UUID,
        request: TestTriggerRequest,
    ) -> TestTriggerResult | None:
        """Test a trigger with simulated event data.

        Args:
            workflow_id: The workflow ID.
            request: Test request with contact and event data.

        Returns:
            TestTriggerResult if trigger found, None otherwise.
        """
        trigger = await self._trigger_repository.get_by_workflow_id(workflow_id)
        if not trigger:
            return None

        # Evaluate trigger
        matched = trigger.evaluate(request.simulate_event_data)

        # Check if would enroll based on settings
        would_enroll = matched  # Simplified - full logic checks enrollment history

        # Get individual filter results
        filter_results = []
        for condition in trigger.filters.conditions:
            result = condition.evaluate(request.simulate_event_data)
            filter_results.append(
                {
                    "field": condition.field,
                    "operator": condition.operator.value,
                    "value": condition.value,
                    "matched": result,
                }
            )

        return TestTriggerResult(
            matched=matched,
            would_enroll=would_enroll,
            filter_results=filter_results,
        )
