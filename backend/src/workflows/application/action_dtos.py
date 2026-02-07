"""Data Transfer Objects for workflow actions.

DTOs define the structure of data exchanged between the API layer
and the application layer for action management.
"""

from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateActionRequest(BaseModel):
    """Request DTO for creating a new action.

    Validates input data for action creation.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    action_type: Annotated[
        str,
        Field(
            description="Type of action to create",
            examples=["send_email", "wait_time", "add_tag"],
        ),
    ]
    action_config: Annotated[
        dict[str, Any],
        Field(
            description="Configuration for the action (schema depends on action_type)",
            examples=[
                {
                    "template_id": "550e8400-e29b-41d4-a716-446655440000",
                    "subject": "Welcome {{contact.first_name}}!",
                    "from_name": "Support Team",
                    "from_email": "support@example.com",
                }
            ],
        ),
    ]
    position: Annotated[
        int | None,
        Field(
            default=None,
            ge=0,
            description="Position in workflow sequence (auto-assigned if not provided)",
        ),
    ]
    previous_action_id: Annotated[
        UUID | None,
        Field(
            default=None,
            description="ID of previous action for linking",
        ),
    ]


class UpdateActionRequest(BaseModel):
    """Request DTO for updating an action.

    Allows partial updates to action configuration.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    action_config: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="New action configuration",
        ),
    ]
    is_enabled: Annotated[
        bool | None,
        Field(
            default=None,
            description="Enable or disable the action",
        ),
    ]
    position: Annotated[
        int | None,
        Field(
            default=None,
            ge=0,
            description="New position in workflow sequence",
        ),
    ]


class ReorderActionsRequest(BaseModel):
    """Request DTO for reordering actions in a workflow."""

    action_positions: Annotated[
        dict[str, int],
        Field(
            description="Dictionary mapping action IDs to their new positions",
            examples=[
                {
                    "550e8400-e29b-41d4-a716-446655440000": 0,
                    "660e8400-e29b-41d4-a716-446655440000": 1,
                }
            ],
        ),
    ]

    @field_validator("action_positions")
    @classmethod
    def validate_action_positions(cls, v: dict[str, int]) -> dict[str, int]:
        """Validate that all positions are non-negative."""
        for action_id, position in v.items():
            if position < 0:
                raise ValueError(f"Position for action {action_id} must be >= 0")
        return v


class ActionResponse(BaseModel):
    """Response DTO for action data."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workflow_id: UUID
    action_type: str
    action_config: dict[str, Any]
    position: int
    previous_action_id: UUID | None
    next_action_id: UUID | None
    branch_id: UUID | None
    is_enabled: bool
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None
    updated_by: UUID | None

    @classmethod
    def from_entity(cls, entity: Any) -> "ActionResponse":
        """Create response from domain entity.

        Args:
            entity: Action domain entity or model.

        Returns:
            ActionResponse instance.
        """
        # Check if entity has to_dict method
        if hasattr(entity, "to_dict"):
            data = entity.to_dict()
            return cls(**data)
        # Otherwise use attributes directly
        return cls.model_validate(entity)


class ActionExecutionResponse(BaseModel):
    """Response DTO for action execution data."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workflow_execution_id: UUID
    action_id: UUID
    contact_id: UUID
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    execution_data: dict[str, Any]
    result_data: dict[str, Any]
    error_message: str | None
    retry_count: int
    scheduled_at: datetime | None
    duration_seconds: float | None

    @classmethod
    def from_entity(cls, entity: Any) -> "ActionExecutionResponse":
        """Create response from domain entity.

        Args:
            entity: ActionExecution domain entity or model.

        Returns:
            ActionExecutionResponse instance.
        """
        if hasattr(entity, "to_dict"):
            data = entity.to_dict()
            return cls(**data)
        return cls.model_validate(entity)


class ListActionsResponse(BaseModel):
    """Response DTO for listing actions."""

    items: list[ActionResponse]
    total: int
    workflow_id: UUID


class ErrorResponse(BaseModel):
    """Standard error response DTO."""

    error: Annotated[
        str,
        Field(
            description="Error code",
            examples=["invalid_action_type", "configuration_error"],
        ),
    ]
    message: Annotated[
        str,
        Field(
            description="Human-readable error message",
        ),
    ]
    details: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="Additional error details",
        ),
    ]
