"""DTOs for condition/branch use cases.

Data Transfer Objects define the contract between the application
layer and external interfaces (API, CLI, etc.).
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CreateConditionRequestDTO(BaseModel):
    """DTO for creating a new condition node."""

    node_id: UUID = Field(..., description="Canvas node identifier")
    condition_type: str = Field(..., description="Type of condition to evaluate")
    branch_type: str = Field(..., description="Type of branching (if_else, multi_branch, split_test)")
    configuration: dict[str, Any] = Field(..., description="Condition-specific settings")
    position_x: int = Field(..., description="Canvas X position")
    position_y: int = Field(..., description="Canvas Y position")
    branches: list[dict[str, Any]] | None = Field(None, description="Optional branches")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "node_id": "uuid-of-node",
                    "condition_type": "contact_field_equals",
                    "branch_type": "if_else",
                    "configuration": {
                        "field": "email",
                        "operator": "contains",
                        "value": "@gmail.com",
                    },
                    "position_x": 200,
                    "position_y": 300,
                },
                {
                    "node_id": "uuid-of-node",
                    "condition_type": "contact_has_tag",
                    "branch_type": "multi_branch",
                    "configuration": {
                        "operator": "has_any_tag",
                        "tags": ["lead", "prospect"],
                    },
                    "position_x": 400,
                    "position_y": 500,
                },
            ]
        }
    }


class UpdateConditionRequestDTO(BaseModel):
    """DTO for updating an existing condition configuration."""

    configuration: dict[str, Any] | None = Field(None, description="New condition configuration")
    position_x: int | None = Field(None, description="New canvas X position")
    position_y: int | None = Field(None, description="New canvas Y position")
    is_active: bool | None = Field(None, description="New active state")
    branches: list[dict[str, Any]] | None = Field(None, description="Updated branches")


class BranchResponseDTO(BaseModel):
    """DTO for branch response."""

    id: UUID = Field(..., description="Branch identifier")
    condition_id: UUID = Field(..., description="Parent condition ID")
    branch_name: str = Field(..., description="Branch display name")
    branch_order: int = Field(..., description="Evaluation priority")
    is_default: bool = Field(..., description="Whether this is default/else branch")
    percentage: float | None = Field(None, description="Split test percentage")
    next_node_id: UUID | None = Field(None, description="Connected next node ID")
    criteria: dict[str, Any] | None = Field(None, description="Branch-specific criteria")

    model_config = {"from_attributes": True}


class ConditionResponseDTO(BaseModel):
    """DTO for condition configuration response."""

    id: UUID = Field(..., description="Condition identifier")
    workflow_id: UUID = Field(..., description="Associated workflow ID")
    node_id: UUID = Field(..., description="Canvas node identifier")
    condition_type: str = Field(..., description="Type of condition")
    branch_type: str = Field(..., description="Type of branching")
    configuration: dict[str, Any] = Field(..., description="Condition configuration")
    position_x: int = Field(..., description="Canvas X position")
    position_y: int = Field(..., description="Canvas Y position")
    branches: list[BranchResponseDTO] = Field(..., description="Condition branches")
    is_active: bool = Field(..., description="Whether condition is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: UUID | None = Field(None, description="Creator user ID")
    updated_by: UUID | None = Field(None, description="Last updater user ID")

    model_config = {"from_attributes": True}


class ListConditionsResponseDTO(BaseModel):
    """DTO for listing workflow conditions."""

    conditions: list[ConditionResponseDTO] = Field(..., description="List of conditions")
    total: int = Field(..., description="Total count of conditions")
    offset: int = Field(..., description="Pagination offset")
    limit: int = Field(..., description="Pagination limit")


class EvaluateConditionRequestDTO(BaseModel):
    """DTO for evaluating a condition."""

    contact_id: UUID = Field(..., description="Contact to evaluate")
    execution_id: UUID | None = Field(None, description="Workflow execution ID")
    contact_data: dict[str, Any] = Field(..., description="Contact field values")
    tags: list[str] | None = Field(None, description="Contact tags")
    pipeline_stages: dict[str, str] | None = Field(None, description="Pipeline stage data")
    custom_fields: dict[str, Any] | None = Field(None, description="Custom field values")
    email_engagement: dict[str, Any] | None = Field(None, description="Email engagement data")


class ConditionEvaluationResultDTO(BaseModel):
    """DTO for condition evaluation result."""

    result: str = Field(..., description="Branch name taken")
    branch_id: UUID | None = Field(None, description="ID of matching branch")
    next_node_id: UUID | None = Field(None, description="Next node ID in path")
    evaluation_details: dict[str, Any] = Field(..., description="Evaluation details")
    duration_ms: int = Field(..., description="Evaluation duration in milliseconds")


class AddBranchRequestDTO(BaseModel):
    """DTO for adding a branch to a condition."""

    branch_name: str = Field(..., description="Branch display name")
    branch_order: int = Field(..., description="Evaluation priority order")
    is_default: bool = Field(False, description="Whether this is default/else branch")
    percentage: float | None = Field(None, description="Split test percentage")
    next_node_id: UUID | None = Field(None, description="Connected next node ID")
    criteria: dict[str, Any] | None = Field(None, description="Branch-specific criteria")


class UpdateBranchRequestDTO(BaseModel):
    """DTO for updating a branch."""

    branch_name: str | None = Field(None, description="New branch name")
    next_node_id: UUID | None = Field(None, description="New next node ID")
    criteria: dict[str, Any] | None = Field(None, description="New criteria")
