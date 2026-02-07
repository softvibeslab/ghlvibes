"""Domain entities for CRM module.

Entities are objects with identity that persists over time.
Each entity represents a core business concept in the CRM domain.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from src.crm.domain.value_objects import (
    ActivityStatus,
    ActivityType,
    DealStatus,
    Email,
    Money,
    PhoneNumber,
)
from src.crm.domain.exceptions import (
    ActivityValidationError,
    CompanyValidationError,
    ContactValidationError,
    DealValidationError,
    InvalidStageTransitionError,
    NoteValidationError,
    PipelineValidationError,
)


# ============================================================================
# Tag Entity (SPEC-CRM-001)
# ============================================================================

@dataclass
class Tag:
    """Tag entity for categorizing contacts and companies.

    Tags are flexible labels used for organizing and filtering contacts.
    """

    id: UUID
    account_id: UUID
    name: str
    color: str | None = None  # Hex color code
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Validate tag state."""
        if not self.name or len(self.name.strip()) == 0:
            raise TagValidationError("Tag name is required")

        if len(self.name) > 50:
            raise TagValidationError("Tag name must be 50 characters or less")

    @classmethod
    def create(cls, account_id: UUID, name: str, color: str | None = None) -> "Tag":
        """Factory method to create a new tag.

        Args:
            account_id: Account ID.
            name: Tag name.
            color: Optional hex color code.

        Returns:
            Tag instance.
        """
        return cls(
            id=uuid4(),
            account_id=account_id,
            name=name.strip(),
            color=color,
        )


# ============================================================================
# Contact Entity (SPEC-CRM-001)
# ============================================================================

@dataclass
class Contact:
    """Contact aggregate root entity.

    Represents a person (lead, customer, etc.) in the CRM system.
    Supports custom fields, tags, and multiple contact methods.
    """

    id: UUID
    account_id: UUID
    email: Email | None
    first_name: str
    last_name: str
    phone: PhoneNumber | None = None
    company_id: UUID | None = None
    tags: list[Tag] = field(default_factory=list)
    custom_fields: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: UUID | None = None

    def __post_init__(self) -> None:
        """Validate contact state."""
        if not self.first_name or len(self.first_name.strip()) == 0:
            raise ContactValidationError("First name is required")

        if len(self.first_name) > 100:
            raise ContactValidationError("First name must be 100 characters or less")

        if self.last_name and len(self.last_name) > 100:
            raise ContactValidationError("Last name must be 100 characters or less")

    @property
    def full_name(self) -> str:
        """Return full name."""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    @classmethod
    def create(
        cls,
        account_id: UUID,
        first_name: str,
        last_name: str,
        email: str | None = None,
        phone: str | None = None,
        company_id: UUID | None = None,
        created_by: UUID | None = None,
    ) -> "Contact":
        """Factory method to create a new contact.

        Args:
            account_id: Account ID.
            first_name: First name.
            last_name: Last name.
            email: Optional email address.
            phone: Optional phone number.
            company_id: Optional associated company.
            created_by: User ID who created the contact.

        Returns:
            Contact instance.
        """
        email_obj = Email(email) if email else None
        phone_obj = PhoneNumber(phone) if phone else None

        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            account_id=account_id,
            email=email_obj,
            first_name=first_name.strip(),
            last_name=last_name.strip() if last_name else "",
            phone=phone_obj,
            company_id=company_id,
            created_at=now,
            updated_at=now,
            created_by=created_by,
        )

    def update(
        self,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        company_id: UUID | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> None:
        """Update contact details.

        Args:
            first_name: New first name.
            last_name: New last name.
            email: New email.
            phone: New phone.
            company_id: New company association.
            custom_fields: Updated custom field values.
        """
        if first_name is not None:
            self.first_name = first_name.strip()

        if last_name is not None:
            self.last_name = last_name.strip()

        if email is not None:
            self.email = Email(email) if email else None

        if phone is not None:
            self.phone = PhoneNumber(phone) if phone else None

        if company_id is not None:
            self.company_id = company_id

        if custom_fields is not None:
            self.custom_fields.update(custom_fields)

        self.updated_at = datetime.now(UTC)

    def add_tag(self, tag: Tag) -> None:
        """Add a tag to the contact.

        Args:
            tag: Tag to add.
        """
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now(UTC)

    def remove_tag(self, tag_id: UUID) -> None:
        """Remove a tag from the contact.

        Args:
            tag_id: Tag ID to remove.
        """
        self.tags = [t for t in self.tags if t.id != tag_id]
        self.updated_at = datetime.now(UTC)


# ============================================================================
# Company Entity (SPEC-CRM-003)
# ============================================================================

@dataclass
class Company:
    """Company aggregate root entity.

    Represents a business organization in the CRM system.
    Supports hierarchies (parent companies) and domains.
    """

    id: UUID
    account_id: UUID
    name: str
    domain: str | None = None  # e.g., "example.com"
    website: str | None = None  # Full URL
    parent_company_id: UUID | None = None
    industry: str | None = None
    size: str | None = None  # e.g., "1-10", "11-50", "51-200", etc.
    tags: list[Tag] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Validate company state."""
        if not self.name or len(self.name.strip()) == 0:
            raise CompanyValidationError("Company name is required")

        if len(self.name) > 255:
            raise CompanyValidationError("Company name must be 255 characters or less")

        if self.domain and len(self.domain) > 255:
            raise CompanyValidationError("Domain must be 255 characters or less")

    @classmethod
    def create(
        cls,
        account_id: UUID,
        name: str,
        domain: str | None = None,
        website: str | None = None,
        parent_company_id: UUID | None = None,
        industry: str | None = None,
        size: str | None = None,
    ) -> "Company":
        """Factory method to create a new company.

        Args:
            account_id: Account ID.
            name: Company name.
            domain: Company domain.
            website: Company website URL.
            parent_company_id: Parent company ID for hierarchies.
            industry: Industry classification.
            size: Company size category.

        Returns:
            Company instance.
        """
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            account_id=account_id,
            name=name.strip(),
            domain=domain.strip().lower() if domain else None,
            website=website.strip() if website else None,
            parent_company_id=parent_company_id,
            industry=industry,
            size=size,
            created_at=now,
            updated_at=now,
        )

    def update(
        self,
        name: str | None = None,
        domain: str | None = None,
        website: str | None = None,
        parent_company_id: UUID | None = None,
        industry: str | None = None,
        size: str | None = None,
    ) -> None:
        """Update company details."""
        if name is not None:
            self.name = name.strip()

        if domain is not None:
            self.domain = domain.strip().lower() if domain else None

        if website is not None:
            self.website = website.strip() if website else None

        if parent_company_id is not None:
            self.parent_company_id = parent_company_id

        if industry is not None:
            self.industry = industry

        if size is not None:
            self.size = size

        self.updated_at = datetime.now(UTC)


# ============================================================================
# Pipeline and Stage Entities (SPEC-CRM-002)
# ============================================================================

@dataclass
class PipelineStage:
    """Pipeline stage value object.

    Represents a stage in a sales pipeline with probability.
    """

    id: UUID
    pipeline_id: UUID
    name: str
    order: int
    probability: int  # 0-100, likelihood of deal winning
    display_color: str | None = None  # Hex color

    def __post_init__(self) -> None:
        """Validate stage state."""
        if not self.name or len(self.name.strip()) == 0:
            raise PipelineValidationError("Stage name is required")

        if self.probability < 0 or self.probability > 100:
            raise PipelineValidationError("Probability must be between 0 and 100")

    @property
    def formatted_probability(self) -> str:
        """Return formatted probability string."""
        return f"{self.probability}%"


@dataclass
class Pipeline:
    """Pipeline aggregate root entity.

    Represents a sales pipeline with multiple stages.
    Pipelines define the sales process for different types of deals.
    """

    id: UUID
    account_id: UUID
    name: str
    stages: list[PipelineStage] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Validate pipeline state."""
        if not self.name or len(self.name.strip()) == 0:
            raise PipelineValidationError("Pipeline name is required")

        if len(self.name) > 100:
            raise PipelineValidationError("Pipeline name must be 100 characters or less")

    @classmethod
    def create(
        cls,
        account_id: UUID,
        name: str,
        stages: list[PipelineStage] | None = None,
    ) -> "Pipeline":
        """Factory method to create a new pipeline.

        Args:
            account_id: Account ID.
            name: Pipeline name.
            stages: Optional list of stages.

        Returns:
            Pipeline instance.
        """
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            account_id=account_id,
            name=name.strip(),
            stages=stages or [],
            created_at=now,
            updated_at=now,
        )

    def add_stage(self, stage: PipelineStage) -> None:
        """Add a stage to the pipeline.

        Args:
            stage: Stage to add.
        """
        if stage.pipeline_id != self.id:
            raise PipelineValidationError("Stage does not belong to this pipeline")

        if stage.id in [s.id for s in self.stages]:
            raise PipelineValidationError("Stage already exists in pipeline")

        self.stages.append(stage)
        self.stages.sort(key=lambda s: s.order)
        self.updated_at = datetime.now(UTC)

    def remove_stage(self, stage_id: UUID) -> None:
        """Remove a stage from the pipeline.

        Args:
            stage_id: Stage ID to remove.
        """
        self.stages = [s for s in self.stages if s.id != stage_id]
        self.updated_at = datetime.now(UTC)

    def get_stage(self, stage_id: UUID) -> PipelineStage | None:
        """Get a stage by ID.

        Args:
            stage_id: Stage ID.

        Returns:
            PipelineStage or None if not found.
        """
        return next((s for s in self.stages if s.id == stage_id), None)


# ============================================================================
# Deal Entity (SPEC-CRM-002)
# ============================================================================

@dataclass
class Deal:
    """Deal aggregate root entity.

    Represents a sales opportunity in a pipeline stage.
    Deals track potential revenue through the sales process.
    """

    id: UUID
    account_id: UUID
    pipeline_id: UUID
    stage_id: UUID
    name: str
    value: Money
    contact_id: UUID | None = None
    company_id: UUID | None = None
    status: DealStatus = DealStatus.OPEN
    expected_close_date: datetime | None = None
    actual_close_date: datetime | None = None
    probability: int = 50  # Override stage probability
    notes: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: UUID | None = None

    def __post_init__(self) -> None:
        """Validate deal state."""
        if not self.name or len(self.name.strip()) == 0:
            raise DealValidationError("Deal name is required")

        if len(self.name) > 255:
            raise DealValidationError("Deal name must be 255 characters or less")

        if self.probability < 0 or self.probability > 100:
            raise DealValidationError("Probability must be between 0 and 100")

    @classmethod
    def create(
        cls,
        account_id: UUID,
        pipeline_id: UUID,
        stage_id: UUID,
        name: str,
        value: float | Money,
        contact_id: UUID | None = None,
        company_id: UUID | None = None,
        created_by: UUID | None = None,
    ) -> "Deal":
        """Factory method to create a new deal.

        Args:
            account_id: Account ID.
            pipeline_id: Pipeline ID.
            stage_id: Initial stage ID.
            name: Deal name.
            value: Deal value (float or Money).
            contact_id: Associated contact.
            company_id: Associated company.
            created_by: User ID who created the deal.

        Returns:
            Deal instance.
        """
        if isinstance(value, float):
            value_obj = Money.from_decimal(value)
        else:
            value_obj = value

        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            account_id=account_id,
            pipeline_id=pipeline_id,
            stage_id=stage_id,
            name=name.strip(),
            value=value_obj,
            contact_id=contact_id,
            company_id=company_id,
            status=DealStatus.OPEN,
            created_at=now,
            updated_at=now,
            created_by=created_by,
        )

    def move_to_stage(self, new_stage_id: UUID, new_probability: int | None = None) -> None:
        """Move deal to a new stage.

        Args:
            new_stage_id: New stage ID.
            new_probability: Optional probability override.

        Raises:
            InvalidStageTransitionError: If deal is already won/lost.
        """
        if self.status in [DealStatus.WON, DealStatus.LOST, DealStatus.ABANDONED]:
            raise InvalidStageTransitionError(
                f"Cannot move deal with status {self.status.value}"
            )

        self.stage_id = new_stage_id
        if new_probability is not None:
            self.probability = new_probability

        self.updated_at = datetime.now(UTC)

    def win(self, close_date: datetime | None = None) -> None:
        """Mark deal as won.

        Args:
            close_date: Optional custom close date (defaults to now).
        """
        self.status = DealStatus.WON
        self.actual_close_date = close_date or datetime.now(UTC)
        self.updated_at = datetime.now(UTC)

    def lose(self, close_date: datetime | None = None) -> None:
        """Mark deal as lost.

        Args:
            close_date: Optional custom close date (defaults to now).
        """
        self.status = DealStatus.LOST
        self.actual_close_date = close_date or datetime.now(UTC)
        self.updated_at = datetime.now(UTC)

    def abandon(self) -> None:
        """Mark deal as abandoned (no longer pursued)."""
        self.status = DealStatus.ABANDONED
        self.updated_at = datetime.now(UTC)


# ============================================================================
# Activity Entity (SPEC-CRM-004)
# ============================================================================

@dataclass
class Activity:
    """Activity aggregate root entity.

    Represents a scheduled or completed activity (call, meeting, task, etc.).
    Activities are interactions with contacts and companies.
    """

    id: UUID
    account_id: UUID
    activity_type: ActivityType
    title: str
    description: str | None = None
    status: ActivityStatus = ActivityStatus.PENDING
    due_date: datetime | None = None
    completed_at: datetime | None = None
    contact_id: UUID | None = None
    company_id: UUID | None = None
    deal_id: UUID | None = None
    created_by: UUID | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Validate activity state."""
        if not self.title or len(self.title.strip()) == 0:
            raise ActivityValidationError("Activity title is required")

        if len(self.title) > 255:
            raise ActivityValidationError("Activity title must be 255 characters or less")

    @classmethod
    def create(
        cls,
        account_id: UUID,
        activity_type: ActivityType,
        title: str,
        description: str | None = None,
        due_date: datetime | None = None,
        contact_id: UUID | None = None,
        company_id: UUID | None = None,
        deal_id: UUID | None = None,
        created_by: UUID | None = None,
    ) -> "Activity":
        """Factory method to create a new activity.

        Args:
            account_id: Account ID.
            activity_type: Type of activity.
            title: Activity title.
            description: Optional description.
            due_date: Optional due date.
            contact_id: Associated contact.
            company_id: Associated company.
            deal_id: Associated deal.
            created_by: User ID who created the activity.

        Returns:
            Activity instance.
        """
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            account_id=account_id,
            activity_type=activity_type,
            title=title.strip(),
            description=description,
            status=ActivityStatus.PENDING,
            due_date=due_date,
            contact_id=contact_id,
            company_id=company_id,
            deal_id=deal_id,
            created_by=created_by,
            created_at=now,
            updated_at=now,
        )

    def start(self) -> None:
        """Mark activity as in progress."""
        if self.status != ActivityStatus.PENDING:
            raise ActivityValidationError("Can only start pending activities")

        self.status = ActivityStatus.IN_PROGRESS
        self.updated_at = datetime.now(UTC)

    def complete(self) -> None:
        """Mark activity as completed."""
        if self.status == ActivityStatus.COMPLETED:
            raise ActivityValidationError("Activity is already completed")

        if self.status == ActivityStatus.CANCELLED:
            raise ActivityValidationError("Cannot complete cancelled activities")

        self.status = ActivityStatus.COMPLETED
        self.completed_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)

    def cancel(self) -> None:
        """Cancel the activity."""
        if self.status == ActivityStatus.COMPLETED:
            raise ActivityValidationError("Cannot cancel completed activities")

        self.status = ActivityStatus.CANCELLED
        self.updated_at = datetime.now(UTC)


# ============================================================================
# Note Entity (SPEC-CRM-005)
# ============================================================================

@dataclass
class Note:
    """Note aggregate root entity.

    Represents a note or communication log associated with contacts/companies.
    Notes include email, call, SMS logs and general notes.
    """

    id: UUID
    account_id: UUID
    content: str
    note_type: str = "note"  # note, email, call, sms
    contact_id: UUID | None = None
    company_id: UUID | None = None
    deal_id: UUID | None = None
    created_by: UUID | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Validate note state."""
        if not self.content or len(self.content.strip()) == 0:
            raise NoteValidationError("Note content is required")

        if len(self.content) > 10000:
            raise NoteValidationError("Note content must be 10,000 characters or less")

    @classmethod
    def create(
        cls,
        account_id: UUID,
        content: str,
        note_type: str = "note",
        contact_id: UUID | None = None,
        company_id: UUID | None = None,
        deal_id: UUID | None = None,
        created_by: UUID | None = None,
    ) -> "Note":
        """Factory method to create a new note.

        Args:
            account_id: Account ID.
            content: Note content.
            note_type: Type of note (note, email, call, sms).
            contact_id: Associated contact.
            company_id: Associated company.
            deal_id: Associated deal.
            created_by: User ID who created the note.

        Returns:
            Note instance.
        """
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            account_id=account_id,
            content=content.strip(),
            note_type=note_type,
            contact_id=contact_id,
            company_id=company_id,
            deal_id=deal_id,
            created_by=created_by,
            created_at=now,
            updated_at=now,
        )

    def update(self, content: str) -> None:
        """Update note content.

        Args:
            content: New content.
        """
        self.content = content.strip()
        self.updated_at = datetime.now(UTC)
