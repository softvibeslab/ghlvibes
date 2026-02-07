"""
Integration entities.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Literal
from uuid import UUID, uuid4


@dataclass
class Integration:
    """
    Integration aggregate root.

    Invariants:
    - Credentials must be encrypted at rest
    - Name must be unique within account
    """
    id: UUID = field(default_factory=uuid4)
    account_id: UUID = None
    provider: str = ""
    integration_type: str = ""  # email, sms, webhook, tracking
    name: str = ""
    description: Optional[str] = None
    credentials: str = ""  # Encrypted
    settings: dict = field(default_factory=dict)
    mappings: list = field(default_factory=list)
    status: str = "active"
    last_verified_at: Optional[datetime] = None
    health_status: str = "unknown"
    last_health_check_at: Optional[datetime] = None
    health_error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate integration invariants."""
        if not self.name or len(self.name) < 3 or len(self.name) > 100:
            raise ValueError("Integration name must be between 3 and 100 characters")

    def verify_connection(self, success: bool, details: Optional[dict] = None) -> None:
        """Update connection verification status."""
        self.last_verified_at = datetime.utcnow()
        self.health_status = "healthy" if success else "error"
        self.last_health_check_at = datetime.utcnow()
        if not success and details:
            self.health_error_message = details.get("error", "Connection failed")

    def deactivate(self) -> None:
        """Deactivate the integration."""
        self.status = "inactive"
        self.updated_at = datetime.utcnow()


@dataclass
class Webhook:
    """Webhook aggregate root."""
    id: UUID = field(default_factory=uuid4)
    account_id: UUID = None
    name: str = ""
    description: Optional[str] = None
    events: List[str] = field(default_factory=list)
    url: str = ""
    method: Literal["POST", "PUT"] = "POST"
    headers: List[dict] = field(default_factory=list)
    retry_config: dict = field(default_factory=lambda: {
        "enabled": True,
        "max_retries": 3,
        "retry_after_seconds": 60
    })
    secret: Optional[str] = None
    status: str = "active"
    last_triggered_at: Optional[datetime] = None
    trigger_count: int = 0
    failure_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate webhook invariants."""
        if not self.url or not self.url.startswith("https://"):
            raise ValueError("Webhook URL must use HTTPS")

    def trigger(self) -> None:
        """Record webhook trigger."""
        self.last_triggered_at = datetime.utcnow()
        self.trigger_count += 1
        self.updated_at = datetime.utcnow()

    def record_failure(self) -> None:
        """Record webhook delivery failure."""
        self.failure_count += 1
        self.updated_at = datetime.utcnow()

    def record_success(self) -> None:
        """Record successful webhook delivery."""
        self.failure_count = max(0, self.failure_count - 1)
        self.updated_at = datetime.utcnow()


@dataclass
class WebhookDelivery:
    """Webhook delivery value object."""
    id: UUID = field(default_factory=uuid4)
    webhook_id: UUID = None
    event_type: str = ""
    payload: dict = field(default_factory=dict)
    response_status: Optional[int] = None
    response_body: Optional[str] = None
    attempt_number: int = 1
    delivered_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def is_successful(self) -> bool:
        """Check if delivery was successful."""
        return self.response_status is not None and 200 <= self.response_status < 300

    @property
    def can_retry(self) -> bool:
        """Check if delivery can be retried."""
        return not self.is_successful and self.attempt_number < 3


@dataclass
class FieldMapping:
    """Field mapping value object."""
    funnel_field: str = ""
    provider_field: str = ""
    transform: Optional[str] = None  # Optional transformation function
