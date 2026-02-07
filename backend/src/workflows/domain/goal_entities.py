"""Goal tracking domain entities for the workflow module.

Entities represent objects with identity that persist over time.
The GoalConfig entity is the aggregate root for goal tracking.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Self
from uuid import UUID, uuid4

from src.workflows.domain.exceptions import ValidationError


class GoalType(str, Enum):
    """Types of goals that can be configured for workflows.

    Each goal type represents a different business event that can trigger
    workflow exit when achieved by a contact.
    """

    TAG_ADDED = "tag_added"
    PURCHASE_MADE = "purchase_made"
    APPOINTMENT_BOOKED = "appointment_booked"
    FORM_SUBMITTED = "form_submitted"
    PIPELINE_STAGE_REACHED = "pipeline_stage_reached"


@dataclass(frozen=True)
class GoalCriteria:
    """Value object for goal-specific criteria.

    Different goal types have different criteria requirements.
    This value object uses type validation to ensure only
    appropriate criteria are provided for each goal type.
    """

    goal_type: GoalType
    criteria: dict[str, Any]

    def __post_init__(self) -> None:
        """Validate criteria based on goal type."""
        goal_type = self.goal_type
        criteria = self.criteria

        if goal_type == GoalType.TAG_ADDED:
            if "tag_id" not in criteria and "tag_name" not in criteria:
                raise ValidationError(
                    "Tag goal requires either tag_id or tag_name in criteria"
                )
        elif goal_type == GoalType.PURCHASE_MADE:
            if not any(
                k in criteria
                for k in ["product_id", "min_amount", "any_purchase"]
            ):
                raise ValidationError(
                    "Purchase goal requires product_id, min_amount, or any_purchase in criteria"
                )
        elif goal_type == GoalType.APPOINTMENT_BOOKED:
            if not any(
                k in criteria
                for k in ["calendar_id", "service_id", "any_appointment"]
            ):
                raise ValidationError(
                    "Appointment goal requires calendar_id, service_id, or any_appointment in criteria"
                )
        elif goal_type == GoalType.FORM_SUBMITTED:
            if "form_id" not in criteria:
                raise ValidationError("Form goal requires form_id in criteria")
        elif goal_type == GoalType.PIPELINE_STAGE_REACHED:
            if "pipeline_id" not in criteria or "stage_id" not in criteria:
                raise ValidationError(
                    "Pipeline stage goal requires both pipeline_id and stage_id in criteria"
                )


@dataclass
class GoalConfig:
    """Goal configuration aggregate root entity.

    Represents a goal configured for a workflow. When contacts achieve
    this goal, they are automatically exited from the workflow.

    Attributes:
        id: Unique identifier for the goal configuration.
        workflow_id: Workflow this goal is associated with.
        account_id: Account/tenant this goal belongs to.
        goal_type: Type of goal to track.
        criteria: Goal-specific criteria for achievement.
        is_active: Whether goal tracking is active.
        version: Optimistic locking version.
        created_at: Timestamp when goal was created.
        updated_at: Timestamp of last update.
        created_by: User who created the goal.
        updated_by: User who last updated the goal.
    """

    id: UUID
    workflow_id: UUID
    account_id: UUID
    goal_type: GoalType
    criteria: GoalCriteria
    is_active: bool = True
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: UUID | None = None
    updated_by: UUID | None = None

    def __post_init__(self) -> None:
        """Validate entity state after initialization."""
        # Ensure criteria is a GoalCriteria instance
        if isinstance(self.criteria, dict):
            object.__setattr__(
                self, "criteria", GoalCriteria(goal_type=self.goal_type, criteria=self.criteria)
            )

        # Validate workflow_id and account_id match criteria context
        # (additional business rules can be added here)

    @classmethod
    def create(
        cls,
        workflow_id: UUID,
        account_id: UUID,
        goal_type: GoalType,
        criteria: dict[str, Any] | GoalCriteria,
        created_by: UUID,
    ) -> Self:
        """Factory method to create a new goal configuration.

        Args:
            workflow_id: Workflow to associate goal with.
            account_id: Account/tenant this goal belongs to.
            goal_type: Type of goal to configure.
            criteria: Goal-specific criteria (dict or GoalCriteria).
            created_by: User creating the goal.

        Returns:
            A new GoalConfig instance.
        """
        goal_criteria = (
            criteria
            if isinstance(criteria, GoalCriteria)
            else GoalCriteria(goal_type=goal_type, criteria=criteria)
        )
        now = datetime.now(UTC)

        return cls(
            id=uuid4(),
            workflow_id=workflow_id,
            account_id=account_id,
            goal_type=goal_type,
            criteria=goal_criteria,
            is_active=True,
            version=1,
            created_at=now,
            updated_at=now,
            created_by=created_by,
            updated_by=created_by,
        )

    def update(
        self,
        updated_by: UUID,
        criteria: dict[str, Any] | GoalCriteria | None = None,
        is_active: bool | None = None,
    ) -> None:
        """Update goal configuration.

        Args:
            updated_by: User making the update.
            criteria: New criteria (optional).
            is_active: New active state (optional).
        """
        if criteria is not None:
            new_criteria = (
                criteria
                if isinstance(criteria, GoalCriteria)
                else GoalCriteria(goal_type=self.goal_type, criteria=criteria)
            )
            self.criteria = new_criteria
        if is_active is not None:
            self.is_active = is_active

        self._touch(updated_by)

    def deactivate(self, updated_by: UUID) -> None:
        """Deactivate the goal configuration.

        Args:
            updated_by: User deactivating the goal.
        """
        self.is_active = False
        self._touch(updated_by)

    def activate(self, updated_by: UUID) -> None:
        """Activate the goal configuration.

        Args:
            updated_by: User activating the goal.
        """
        self.is_active = True
        self._touch(updated_by)

    def _touch(self, updated_by: UUID) -> None:
        """Update timestamp and version.

        Args:
            updated_by: User making the change.
        """
        self.updated_at = datetime.now(UTC)
        self.updated_by = updated_by
        self.version += 1

    @property
    def is_tag_added_goal(self) -> bool:
        """Check if this is a tag_added goal."""
        return self.goal_type == GoalType.TAG_ADDED

    @property
    def is_purchase_made_goal(self) -> bool:
        """Check if this is a purchase_made goal."""
        return self.goal_type == GoalType.PURCHASE_MADE

    @property
    def is_appointment_booked_goal(self) -> bool:
        """Check if this is an appointment_booked goal."""
        return self.goal_type == GoalType.APPOINTMENT_BOOKED

    @property
    def is_form_submitted_goal(self) -> bool:
        """Check if this is a form_submitted goal."""
        return self.goal_type == GoalType.FORM_SUBMITTED

    @property
    def is_pipeline_stage_reached_goal(self) -> bool:
        """Check if this is a pipeline_stage_reached goal."""
        return self.goal_type == GoalType.PIPELINE_STAGE_REACHED

    def to_dict(self) -> dict[str, Any]:
        """Convert goal config to dictionary representation.

        Returns:
            Dictionary containing all goal attributes.
        """
        return {
            "id": str(self.id),
            "workflow_id": str(self.workflow_id),
            "account_id": str(self.account_id),
            "goal_type": self.goal_type.value,
            "criteria": self.criteria.criteria,
            "is_active": self.is_active,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": str(self.created_by) if self.created_by else None,
            "updated_by": str(self.updated_by) if self.updated_by else None,
        }


@dataclass
class GoalAchievement:
    """Goal achievement entity.

    Records when a contact achieves a configured goal, including
    the event data that triggered the achievement.

    Attributes:
        id: Unique identifier for the achievement record.
        workflow_id: Workflow where goal was achieved.
        workflow_enrollment_id: Enrollment that achieved the goal.
        contact_id: Contact who achieved the goal.
        goal_config_id: Goal configuration that was achieved.
        account_id: Account/tenant this belongs to.
        goal_type: Type of goal achieved.
        achieved_at: Timestamp when goal was achieved.
        trigger_event: Event data that triggered goal achievement.
        metadata: Additional context about the achievement.
    """

    id: UUID
    workflow_id: UUID
    workflow_enrollment_id: UUID
    contact_id: UUID
    goal_config_id: UUID
    account_id: UUID
    goal_type: GoalType
    achieved_at: datetime
    trigger_event: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        workflow_id: UUID,
        workflow_enrollment_id: UUID,
        contact_id: UUID,
        goal_config_id: UUID,
        account_id: UUID,
        goal_type: GoalType,
        trigger_event: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> Self:
        """Factory method to create a goal achievement record.

        Args:
            workflow_id: Workflow where goal was achieved.
            workflow_enrollment_id: Enrollment that achieved the goal.
            contact_id: Contact who achieved the goal.
            goal_config_id: Goal configuration that was achieved.
            account_id: Account/tenant this belongs to.
            goal_type: Type of goal achieved.
            trigger_event: Event data that triggered achievement.
            metadata: Additional context (optional).

        Returns:
            A new GoalAchievement instance.
        """
        return cls(
            id=uuid4(),
            workflow_id=workflow_id,
            workflow_enrollment_id=workflow_enrollment_id,
            contact_id=contact_id,
            goal_config_id=goal_config_id,
            account_id=account_id,
            goal_type=goal_type,
            achieved_at=datetime.now(UTC),
            trigger_event=trigger_event,
            metadata=metadata or {},
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert goal achievement to dictionary representation.

        Returns:
            Dictionary containing all achievement attributes.
        """
        return {
            "id": str(self.id),
            "workflow_id": str(self.workflow_id),
            "workflow_enrollment_id": str(self.workflow_enrollment_id),
            "contact_id": str(self.contact_id),
            "goal_config_id": str(self.goal_config_id),
            "account_id": str(self.account_id),
            "goal_type": self.goal_type.value,
            "achieved_at": self.achieved_at.isoformat(),
            "trigger_event": self.trigger_event,
            "metadata": self.metadata,
        }
