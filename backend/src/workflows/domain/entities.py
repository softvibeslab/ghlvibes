"""Domain entities for the workflow module.

Entities are objects with identity that persists over time.
The Workflow entity is the aggregate root for the workflow domain.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Self
from uuid import UUID, uuid4

from src.workflows.domain.exceptions import InvalidWorkflowStatusTransitionError
from src.workflows.domain.value_objects import WorkflowName, WorkflowStatus


@dataclass
class Workflow:
    """Workflow aggregate root entity.

    The Workflow entity represents an automation workflow in the system.
    It is the aggregate root for the workflow domain, meaning all
    modifications to workflow data should go through this entity.

    Attributes:
        id: Unique identifier for the workflow.
        account_id: The account/tenant this workflow belongs to.
        name: Workflow name (validated value object).
        description: Optional description of the workflow.
        trigger_type: Type of trigger that starts the workflow.
        trigger_config: Configuration for the trigger (JSON).
        status: Current lifecycle status.
        version: Version number for optimistic locking.
        created_at: Timestamp when the workflow was created.
        updated_at: Timestamp of the last update.
        created_by: ID of the user who created the workflow.
        updated_by: ID of the user who last updated the workflow.
    """

    id: UUID
    account_id: UUID
    name: WorkflowName
    status: WorkflowStatus = WorkflowStatus.DRAFT
    description: str | None = None
    trigger_type: str | None = None
    trigger_config: dict[str, Any] = field(default_factory=dict)
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: UUID | None = None
    updated_by: UUID | None = None

    def __post_init__(self) -> None:
        """Validate entity state after initialization."""
        # Ensure name is a WorkflowName instance
        if isinstance(self.name, str):
            object.__setattr__(self, "name", WorkflowName(self.name))

    @classmethod
    def create(
        cls,
        account_id: UUID,
        name: str | WorkflowName,
        created_by: UUID,
        description: str | None = None,
        trigger_type: str | None = None,
        trigger_config: dict[str, Any] | None = None,
    ) -> Self:
        """Factory method to create a new Workflow.

        Args:
            account_id: The account this workflow belongs to.
            name: The workflow name (string or WorkflowName).
            created_by: ID of the user creating the workflow.
            description: Optional description.
            trigger_type: Optional trigger type.
            trigger_config: Optional trigger configuration.

        Returns:
            A new Workflow instance in draft status.
        """
        workflow_name = name if isinstance(name, WorkflowName) else WorkflowName(name)
        now = datetime.now(UTC)

        return cls(
            id=uuid4(),
            account_id=account_id,
            name=workflow_name,
            description=description,
            trigger_type=trigger_type,
            trigger_config=trigger_config or {},
            status=WorkflowStatus.DRAFT,
            version=1,
            created_at=now,
            updated_at=now,
            created_by=created_by,
            updated_by=created_by,
        )

    def activate(self, updated_by: UUID) -> None:
        """Activate the workflow.

        Transitions the workflow from draft or paused to active status.

        Args:
            updated_by: ID of the user activating the workflow.

        Raises:
            InvalidWorkflowStatusTransitionError: If transition is not allowed.
        """
        if not self.status.can_transition_to(WorkflowStatus.ACTIVE):
            raise InvalidWorkflowStatusTransitionError(
                self.status.value,
                WorkflowStatus.ACTIVE.value,
            )
        self.status = WorkflowStatus.ACTIVE
        self._touch(updated_by)

    def pause(self, updated_by: UUID) -> None:
        """Pause the workflow.

        Transitions the workflow from active to paused status.

        Args:
            updated_by: ID of the user pausing the workflow.

        Raises:
            InvalidWorkflowStatusTransitionError: If transition is not allowed.
        """
        if not self.status.can_transition_to(WorkflowStatus.PAUSED):
            raise InvalidWorkflowStatusTransitionError(
                self.status.value,
                WorkflowStatus.PAUSED.value,
            )
        self.status = WorkflowStatus.PAUSED
        self._touch(updated_by)

    def deactivate(self, updated_by: UUID) -> None:
        """Deactivate the workflow.

        Transitions the workflow from active or paused to draft status.

        Args:
            updated_by: ID of the user deactivating the workflow.

        Raises:
            InvalidWorkflowStatusTransitionError: If transition is not allowed.
        """
        if not self.status.can_transition_to(WorkflowStatus.DRAFT):
            raise InvalidWorkflowStatusTransitionError(
                self.status.value,
                WorkflowStatus.DRAFT.value,
            )
        self.status = WorkflowStatus.DRAFT
        self._touch(updated_by)

    def update(
        self,
        updated_by: UUID,
        name: str | WorkflowName | None = None,
        description: str | None = None,
        trigger_type: str | None = None,
        trigger_config: dict[str, Any] | None = None,
    ) -> None:
        """Update workflow properties.

        Args:
            updated_by: ID of the user updating the workflow.
            name: New name (optional).
            description: New description (optional).
            trigger_type: New trigger type (optional).
            trigger_config: New trigger configuration (optional).
        """
        if name is not None:
            self.name = name if isinstance(name, WorkflowName) else WorkflowName(name)
        if description is not None:
            self.description = description
        if trigger_type is not None:
            self.trigger_type = trigger_type
        if trigger_config is not None:
            self.trigger_config = trigger_config
        self._touch(updated_by)

    def _touch(self, updated_by: UUID) -> None:
        """Update timestamp and version.

        Args:
            updated_by: ID of the user making the change.
        """
        self.updated_at = datetime.now(UTC)
        self.updated_by = updated_by
        self.version += 1

    @property
    def is_active(self) -> bool:
        """Check if workflow is active."""
        return self.status == WorkflowStatus.ACTIVE

    @property
    def is_draft(self) -> bool:
        """Check if workflow is in draft status."""
        return self.status == WorkflowStatus.DRAFT

    @property
    def is_paused(self) -> bool:
        """Check if workflow is paused."""
        return self.status == WorkflowStatus.PAUSED

    @property
    def name_value(self) -> str:
        """Get the workflow name as a string."""
        return str(self.name)

    def to_dict(self) -> dict[str, Any]:
        """Convert workflow to dictionary representation.

        Returns:
            Dictionary containing all workflow attributes.
        """
        return {
            "id": str(self.id),
            "account_id": str(self.account_id),
            "name": str(self.name),
            "description": self.description,
            "trigger_type": self.trigger_type,
            "trigger_config": self.trigger_config,
            "status": self.status.value,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": str(self.created_by) if self.created_by else None,
            "updated_by": str(self.updated_by) if self.updated_by else None,
        }
