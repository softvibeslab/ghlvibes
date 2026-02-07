"""
Analytics event entities.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any
from uuid import UUID, uuid4


@dataclass
class AnalyticsEvent:
    """
    Analytics event base entity.

    Invariants:
    - Event must have valid event type
    - Visitor ID and Session ID required
    """
    id: UUID = field(default_factory=uuid4)
    account_id: UUID = None
    funnel_id: UUID = None
    event_type: str = ""
    visitor_id: UUID = None
    session_id: str = ""
    page_id: Optional[UUID] = None
    funnel_step_id: Optional[UUID] = None
    conversion_type: Optional[str] = None
    value_cents: Optional[int] = None
    conversion_goal_id: Optional[UUID] = None
    url: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    referrer: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    exit_outcome: Optional[str] = None
    next_step_id: Optional[UUID] = None
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate event invariants."""
        valid_types = ["page_view", "conversion", "step_entry", "step_exit"]
        if self.event_type not in valid_types:
            raise ValueError(f"Invalid event type. Must be one of: {valid_types}")
        if not self.visitor_id:
            raise ValueError("Visitor ID is required")
        if not self.session_id:
            raise ValueError("Session ID is required")


@dataclass
class FunnelStepStats:
    """Funnel step statistics value object."""
    funnel_id: UUID = None
    funnel_step_id: UUID = None
    date: datetime = None
    unique_visitors: int = 0
    entries: int = 0
    exits: int = 0
    drop_offs: int = 0
    avg_time_seconds: float = 0.0

    @property
    def drop_off_rate(self) -> float:
        """Calculate drop-off rate."""
        if self.entries == 0:
            return 0.0
        return self.drop_offs / self.entries


@dataclass
class ABTest:
    """A/B test aggregate root."""
    id: UUID = field(default_factory=uuid4)
    account_id: UUID = None
    funnel_id: UUID = None
    test_name: str = ""
    status: str = "running"
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    winner_variant_id: Optional[UUID] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def complete(self, winner_id: UUID) -> None:
        """Mark test as complete."""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        self.winner_variant_id = winner_id


@dataclass
class ABTestVariant:
    """A/B test variant value object."""
    id: UUID = field(default_factory=uuid4)
    test_id: UUID = None
    variant_name: str = ""
    is_control: bool = False
    page_id: Optional[UUID] = None
    config: dict = field(default_factory=dict)
    traffic_split: int = 50

    @property
    def is_valid_split(self) -> bool:
        """Validate traffic split percentage."""
        return 0 <= self.traffic_split <= 100
