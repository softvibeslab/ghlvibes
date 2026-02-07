"""DTOs for goal tracking use cases.

Data Transfer Objects define the contract between the application
layer and external interfaces (API, CLI, etc.).
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CreateGoalRequestDTO(BaseModel):
    """DTO for creating a new goal configuration."""

    goal_type: str = Field(..., description="Type of goal to configure")
    criteria: dict[str, Any] = Field(..., description="Goal-specific criteria")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "goal_type": "tag_added",
                    "criteria": {"tag_id": "uuid-of-tag", "tag_name": "Purchased"},
                },
                {
                    "goal_type": "purchase_made",
                    "criteria": {"min_amount": 100.0},
                },
            ]
        }
    }


class UpdateGoalRequestDTO(BaseModel):
    """DTO for updating an existing goal configuration."""

    criteria: dict[str, Any] | None = Field(None, description="New goal criteria")
    is_active: bool | None = Field(None, description="New active state")


class GoalResponseDTO(BaseModel):
    """DTO for goal configuration response."""

    id: UUID = Field(..., description="Goal configuration ID")
    workflow_id: UUID = Field(..., description="Associated workflow ID")
    account_id: UUID = Field(..., description="Account/tenant ID")
    goal_type: str = Field(..., description="Type of goal")
    criteria: dict[str, Any] = Field(..., description="Goal criteria")
    is_active: bool = Field(..., description="Whether goal is active")
    version: int = Field(..., description="Optimistic locking version")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: UUID | None = Field(None, description="Creator user ID")
    updated_by: UUID | None = Field(None, description="Last updater user ID")

    model_config = {"from_attributes": True}


class ListGoalsResponseDTO(BaseModel):
    """DTO for listing workflow goals."""

    goals: list[GoalResponseDTO] = Field(..., description="List of goal configurations")
    total: int = Field(..., description="Total count of goals")
    offset: int = Field(..., description="Pagination offset")
    limit: int = Field(..., description="Pagination limit")


class GoalAchievementResponseDTO(BaseModel):
    """DTO for goal achievement response."""

    id: UUID = Field(..., description="Achievement record ID")
    workflow_id: UUID = Field(..., description="Workflow ID")
    workflow_enrollment_id: UUID = Field(..., description="Enrollment ID")
    contact_id: UUID = Field(..., description="Contact who achieved goal")
    goal_config_id: UUID = Field(..., description="Goal configuration ID")
    account_id: UUID = Field(..., description="Account/tenant ID")
    goal_type: str = Field(..., description="Type of goal achieved")
    achieved_at: datetime = Field(..., description="When goal was achieved")
    trigger_event: dict[str, Any] = Field(..., description="Event that triggered achievement")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional context")

    model_config = {"from_attributes": True}


class GoalStatsResponseDTO(BaseModel):
    """DTO for goal statistics response."""

    workflow_id: UUID = Field(..., description="Workflow ID")
    total_enrolled: int = Field(..., description="Total contacts enrolled")
    goals_achieved: int = Field(..., description="Total goals achieved")
    conversion_rate: float = Field(..., description="Conversion rate percentage")
    avg_time_to_goal_hours: float | None = Field(
        None, description="Average time to goal achievement"
    )
    by_goal_type: dict[str, dict[str, Any]] = Field(
        default_factory=dict, description="Breakdown by goal type"
    )


class GoalEvaluationRequestDTO(BaseModel):
    """DTO for goal evaluation request."""

    contact_id: UUID = Field(..., description="Contact to evaluate")
    workflow_id: UUID = Field(..., description="Workflow to check")
    event_type: str = Field(..., description="Type of event that occurred")
    event_data: dict[str, Any] = Field(..., description="Event data")


class GoalEvaluationResultDTO(BaseModel):
    """DTO for goal evaluation result."""

    goal_achieved: bool = Field(..., description="Whether a goal was achieved")
    goal_config_id: UUID | None = Field(None, description="Achieved goal configuration ID")
    goal_type: str | None = Field(None, description="Type of goal achieved")
    should_exit_workflow: bool = Field(
        ...,
        description="Whether contact should be exited from workflow",
    )
