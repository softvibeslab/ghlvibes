"""Data Transfer Objects for the workflow module.

DTOs define the structure of data exchanged between the API layer
and the application layer. They handle validation and serialization.
"""

from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.workflows.domain.value_objects import WorkflowStatus


class CreateWorkflowRequest(BaseModel):
    """Request DTO for creating a new workflow.

    Validates input data for workflow creation.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    name: Annotated[
        str,
        Field(
            min_length=3,
            max_length=100,
            description="Workflow name (3-100 characters)",
            examples=["Lead Nurturing Sequence", "Welcome Email Campaign"],
        ),
    ]
    description: Annotated[
        str | None,
        Field(
            default=None,
            max_length=1000,
            description="Optional workflow description",
            examples=["Nurtures new leads through a 7-day email sequence"],
        ),
    ]
    trigger_type: Annotated[
        str | None,
        Field(
            default=None,
            max_length=50,
            description="Type of trigger that starts the workflow",
            examples=["contact_created", "form_submitted", "tag_added"],
        ),
    ]
    trigger_config: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="Configuration for the trigger",
            examples=[{"filters": {"tags": ["new-lead"]}}],
        ),
    ]

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate workflow name format.

        Args:
            v: The name value to validate.

        Returns:
            The validated name.

        Raises:
            ValueError: If name format is invalid.
        """
        if not v or v.isspace():
            raise ValueError("Name cannot be empty or whitespace only")

        # Check for valid characters (alphanumeric, spaces, hyphens, underscores)
        import re

        if len(v) > 2 and not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9\s\-_]*[a-zA-Z0-9]$", v):
            raise ValueError(
                "Name must start and end with alphanumeric characters and "
                "contain only alphanumeric characters, spaces, hyphens, or underscores"
            )
        elif len(v) <= 2 and not v.isalnum():
            raise ValueError("Short names must contain only alphanumeric characters")

        return v


class UpdateWorkflowRequest(BaseModel):
    """Request DTO for updating an existing workflow.

    All fields are optional - only provided fields will be updated.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    name: Annotated[
        str | None,
        Field(
            default=None,
            min_length=3,
            max_length=100,
            description="New workflow name",
        ),
    ]
    description: Annotated[
        str | None,
        Field(
            default=None,
            max_length=1000,
            description="New description",
        ),
    ]
    trigger_type: Annotated[
        str | None,
        Field(
            default=None,
            max_length=50,
            description="New trigger type",
        ),
    ]
    trigger_config: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="New trigger configuration",
        ),
    ]

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Validate workflow name format if provided."""
        if v is None:
            return v

        if not v or v.isspace():
            raise ValueError("Name cannot be empty or whitespace only")

        import re

        if len(v) > 2 and not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9\s\-_]*[a-zA-Z0-9]$", v):
            raise ValueError(
                "Name must start and end with alphanumeric characters and "
                "contain only alphanumeric characters, spaces, hyphens, or underscores"
            )
        elif len(v) <= 2 and not v.isalnum():
            raise ValueError("Short names must contain only alphanumeric characters")

        return v


class WorkflowResponse(BaseModel):
    """Response DTO for a single workflow.

    Serializes workflow data for API responses.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="Unique workflow identifier")
    account_id: UUID = Field(description="Account the workflow belongs to")
    name: str = Field(description="Workflow name")
    description: str | None = Field(description="Workflow description")
    trigger_type: str | None = Field(description="Trigger type")
    trigger_config: dict[str, Any] = Field(description="Trigger configuration")
    status: WorkflowStatus = Field(description="Current workflow status")
    version: int = Field(description="Version number for optimistic locking")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    created_by: UUID | None = Field(description="User who created the workflow")
    updated_by: UUID | None = Field(description="User who last updated the workflow")

    @classmethod
    def from_entity(cls, workflow: "Workflow") -> "WorkflowResponse":  # type: ignore[name-defined]
        """Create response from domain entity.

        Args:
            workflow: The domain Workflow entity.

        Returns:
            WorkflowResponse instance.
        """
        return cls(
            id=workflow.id,
            account_id=workflow.account_id,
            name=str(workflow.name),
            description=workflow.description,
            trigger_type=workflow.trigger_type,
            trigger_config=workflow.trigger_config,
            status=workflow.status,
            version=workflow.version,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at,
            created_by=workflow.created_by,
            updated_by=workflow.updated_by,
        )


class PaginatedWorkflowResponse(BaseModel):
    """Response DTO for paginated workflow lists."""

    model_config = ConfigDict(from_attributes=True)

    items: list[WorkflowResponse] = Field(description="List of workflows")
    total: int = Field(description="Total number of workflows")
    offset: int = Field(description="Current offset")
    limit: int = Field(description="Maximum items per page")
    has_more: bool = Field(description="Whether more items exist")


class WorkflowStatusUpdateRequest(BaseModel):
    """Request DTO for updating workflow status."""

    status: WorkflowStatus = Field(description="New workflow status")


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: str = Field(description="Error type")
    message: str = Field(description="Human-readable error message")
    details: dict[str, Any] | None = Field(
        default=None,
        description="Additional error details",
    )


class ValidationErrorResponse(BaseModel):
    """Validation error response format."""

    error: str = Field(default="validation_error")
    message: str = Field(default="Validation failed")
    details: list[dict[str, Any]] = Field(description="List of validation errors")
