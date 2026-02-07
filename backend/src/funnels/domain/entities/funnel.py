"""
Funnel aggregate root entity.
"""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID, uuid4

from src.funnels.domain.value_objects import FunnelStatus, FunnelType


@dataclass
class FunnelStep:
    """Funnel step value object."""
    id: UUID = field(default_factory=uuid4)
    step_type: str = ""  # page, upsell, downsell, order_bump, thank_you
    name: str = ""
    order: int = 0
    page_id: Optional[UUID] = None
    config: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Funnel:
    """
    Funnel aggregate root.

    Invariants:
    - Name must be unique within account
    - Version must increment on changes
    - Steps must be ordered sequentially starting from 1
    """
    id: UUID = field(default_factory=uuid4)
    account_id: UUID = None  # Set when created
    name: str = ""
    description: Optional[str] = None
    funnel_type: FunnelType = FunnelType.LEAD_GENERATION
    status: FunnelStatus = FunnelStatus.DRAFT
    version: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: UUID = None
    updated_by: Optional[UUID] = None
    deleted_at: Optional[datetime] = None
    steps: List[FunnelStep] = field(default_factory=list)

    def __post_init__(self):
        """Validate funnel invariants."""
        if not self.name or len(self.name) < 3 or len(self.name) > 100:
            raise ValueError("Funnel name must be between 3 and 100 characters")
        if self.version < 1:
            raise ValueError("Version must be at least 1")
        self._validate_steps()

    def _validate_steps(self):
        """Validate step invariants."""
        orders = [step.order for step in self.steps]
        if len(set(orders)) != len(orders):
            raise ValueError("Step orders must be unique")
        if self.steps and max(orders) != len(self.steps):
            raise ValueError("Step orders must be sequential starting from 1")

    def add_step(self, step: FunnelStep) -> None:
        """Add a step to the funnel."""
        step.order = len(self.steps) + 1
        self.steps.append(step)
        self.increment_version()

    def remove_step(self, step_id: UUID) -> None:
        """Remove a step and reorder remaining steps."""
        self.steps = [s for s in self.steps if s.id != step_id]
        for idx, step in enumerate(self.steps, start=1):
            step.order = idx
        self.increment_version()

    def reorder_steps(self, step_orders: dict[UUID, int]) -> None:
        """Reorder steps based on provided mapping."""
        for step in self.steps:
            if step.id in step_orders:
                step.order = step_orders[step.id]
        self.steps.sort(key=lambda s: s.order)
        self._validate_steps()
        self.increment_version()

    def increment_version(self) -> None:
        """Increment version and update timestamp."""
        self.version += 1
        self.updated_at = datetime.utcnow()

    def publish(self) -> None:
        """Publish the funnel."""
        if self.status != FunnelStatus.DRAFT:
            raise ValueError("Only draft funnels can be published")
        self.status = FunnelStatus.ACTIVE
        self.increment_version()

    def archive(self) -> None:
        """Archive the funnel."""
        self.status = FunnelStatus.ARCHIVED
        self.increment_version()

    def soft_delete(self) -> None:
        """Soft delete the funnel."""
        self.deleted_at = datetime.utcnow()

    def is_deleted(self) -> bool:
        """Check if funnel is deleted."""
        return self.deleted_at is not None

    def can_edit(self) -> bool:
        """Check if funnel can be edited."""
        return self.status == FunnelStatus.DRAFT and not self.is_deleted()

    def clone(self, new_name: str) -> "Funnel":
        """Create a copy of the funnel."""
        import copy
        cloned = copy.copy(self)
        cloned.id = uuid4()
        cloned.name = new_name
        cloned.version = 1
        cloned.created_at = datetime.utcnow()
        cloned.updated_at = datetime.utcnow()
        cloned.steps = [copy.deepcopy(step) for step in self.steps]
        for step in cloned.steps:
            step.id = uuid4()
        return cloned
