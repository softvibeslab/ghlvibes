"""Workflow template domain entities for the workflow module.

Entities represent objects with identity that persist over time.
The WorkflowTemplate entity is the aggregate root for template management.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Self
from uuid import UUID, uuid4

from src.workflows.domain.exceptions import ValidationError


class TemplateCategory(str, Enum):
    """Categories for organizing workflow templates.

    Each category represents a specific business use case for automation.
    """

    LEAD_NURTURING = "lead_nurturing"
    APPOINTMENT_REMINDER = "appointment_reminder"
    ONBOARDING = "onboarding"
    RE_ENGAGEMENT = "re_engagement"
    REVIEW_REQUEST = "review_request"
    BIRTHDAY_CELEBRATION = "birthday_celebration"
    CUSTOM = "custom"


@dataclass(frozen=True)
class TemplateMetadata:
    """Value object for template metadata.

    Tracks information about the template source and usage.
    """

    category: TemplateCategory
    required_integrations: list[str]
    tags: list[str]
    estimated_completion_rate: float | None = None
    is_system_template: bool = False
    is_shared: bool = False

    def __post_init__(self) -> None:
        """Validate metadata fields."""
        # Validate completion rate is between 0 and 100
        if self.estimated_completion_rate is not None:
            if not 0.0 <= self.estimated_completion_rate <= 100.0:
                raise ValidationError(
                    f"Completion rate must be between 0 and 100, got {self.estimated_completion_rate}"
                )

        # Validate required_integrations is not None
        if self.required_integrations is None:
            object.__setattr__(self, "required_integrations", [])

        # Validate tags is not None
        if self.tags is None:
            object.__setattr__(self, "tags", [])


@dataclass
class WorkflowTemplate:
    """Workflow template aggregate root entity.

    Represents a reusable workflow template that can be cloned to create
    new workflow instances. Templates can be system-provided or user-created.

    Attributes:
        id: Unique identifier for the template.
        account_id: Account that owns the template (None for system templates).
        name: Template name.
        description: Template description.
        category: Template category for organization.
        metadata: Template metadata including integrations and tags.
        workflow_config: Complete workflow configuration (JSON).
        version: Template version number.
        usage_count: Number of times this template has been cloned.
        created_at: Timestamp when template was created.
        updated_at: Timestamp of last update.
        created_by: User who created the template.
    """

    id: UUID
    account_id: UUID | None
    name: str
    description: str
    category: TemplateCategory
    metadata: TemplateMetadata
    workflow_config: dict[str, Any]
    version: int = 1
    usage_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: UUID | None = None

    def __post_init__(self) -> None:
        """Validate entity state after initialization."""
        # Ensure metadata is a TemplateMetadata instance
        if isinstance(self.metadata, dict):
            object.__setattr__(self, "metadata", TemplateMetadata(**self.metadata))

        # Validate workflow_config is not empty
        if not self.workflow_config or not isinstance(self.workflow_config, dict):
            raise ValidationError("Workflow configuration must be a non-empty dictionary")

        # Validate workflow_config has at least trigger and actions
        if "trigger" not in self.workflow_config:
            raise ValidationError("Workflow configuration must include a trigger")

        if "actions" not in self.workflow_config or not self.workflow_config["actions"]:
            raise ValidationError("Workflow configuration must include at least one action")

        # System templates cannot have an account_id
        if self.metadata.is_system_template and self.account_id is not None:
            raise ValidationError("System templates cannot have an account_id")

        # Custom templates must have an account_id
        if not self.metadata.is_system_template and self.account_id is None:
            raise ValidationError("Custom templates must have an account_id")

    @classmethod
    def create(
        cls,
        account_id: UUID | None,
        name: str,
        description: str,
        category: TemplateCategory,
        workflow_config: dict[str, Any],
        created_by: UUID | None = None,
        required_integrations: list[str] | None = None,
        tags: list[str] | None = None,
        estimated_completion_rate: float | None = None,
        is_system_template: bool = False,
        is_shared: bool = False,
    ) -> Self:
        """Factory method to create a new workflow template.

        Args:
            account_id: Account owning the template (None for system templates).
            name: Template name.
            description: Template description.
            category: Template category.
            workflow_config: Complete workflow configuration.
            created_by: User creating the template.
            required_integrations: List of required integrations.
            tags: Template tags for search.
            estimated_completion_rate: Expected completion rate (0-100).
            is_system_template: Whether this is a system template.
            is_shared: Whether template is shared with sub-accounts.

        Returns:
            A new WorkflowTemplate instance.
        """
        now = datetime.now(UTC)
        metadata = TemplateMetadata(
            category=category,
            required_integrations=required_integrations or [],
            tags=tags or [],
            estimated_completion_rate=estimated_completion_rate,
            is_system_template=is_system_template,
            is_shared=is_shared,
        )

        return cls(
            id=uuid4(),
            account_id=account_id,
            name=name,
            description=description,
            category=category,
            metadata=metadata,
            workflow_config=workflow_config,
            version=1,
            usage_count=0,
            created_at=now,
            updated_at=now,
            created_by=created_by,
        )

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        workflow_config: dict[str, Any] | None = None,
        category: TemplateCategory | None = None,
        tags: list[str] | None = None,
        required_integrations: list[str] | None = None,
        estimated_completion_rate: float | None = None,
        is_shared: bool | None = None,
    ) -> None:
        """Update template properties.

        Args:
            name: New name (optional).
            description: New description (optional).
            workflow_config: New workflow configuration (optional).
            category: New category (optional).
            tags: New tags (optional).
            required_integrations: New required integrations (optional).
            estimated_completion_rate: New completion rate (optional).
            is_shared: New shared status (optional).
        """
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if workflow_config is not None:
            self.workflow_config = workflow_config
        if category is not None:
            self.category = category
        if is_shared is not None:
            # Update metadata with new shared status
            self.metadata = TemplateMetadata(
                category=self.metadata.category,
                required_integrations=self.metadata.required_integrations,
                tags=self.metadata.tags,
                estimated_completion_rate=self.metadata.estimated_completion_rate,
                is_system_template=self.metadata.is_system_template,
                is_shared=is_shared,
            )
        if tags is not None or required_integrations is not None or estimated_completion_rate is not None:
            # Update metadata with new values
            self.metadata = TemplateMetadata(
                category=self.category,
                required_integrations=required_integrations or self.metadata.required_integrations,
                tags=tags or self.metadata.tags,
                estimated_completion_rate=estimated_completion_rate
                or self.metadata.estimated_completion_rate,
                is_system_template=self.metadata.is_system_template,
                is_shared=self.metadata.is_shared,
            )

        self._touch()

    def increment_usage_count(self) -> None:
        """Increment the usage counter when template is cloned."""
        self.usage_count += 1
        self._touch()

    def _touch(self) -> None:
        """Update timestamp and version."""
        self.updated_at = datetime.now(UTC)
        self.version += 1

    @property
    def is_system_template(self) -> bool:
        """Check if this is a system template."""
        return self.metadata.is_system_template

    @property
    def is_custom_template(self) -> bool:
        """Check if this is a custom (user-created) template."""
        return not self.metadata.is_system_template

    @property
    def is_shared(self) -> bool:
        """Check if this template is shared."""
        return self.metadata.is_shared

    def validate_for_cloning(self, available_integrations: list[str]) -> list[str]:
        """Validate template can be cloned with available integrations.

        Args:
            available_integrations: List of integrations available in the account.

        Returns:
            List of missing required integrations (empty if valid).

        Raises:
            ValidationError: If template configuration is invalid.
        """
        # Check if all required integrations are available
        missing_integrations = []
        for integration in self.metadata.required_integrations:
            if integration not in available_integrations:
                missing_integrations.append(integration)

        return missing_integrations

    def to_dict(self) -> dict[str, Any]:
        """Convert template to dictionary representation.

        Returns:
            Dictionary containing all template attributes.
        """
        return {
            "id": str(self.id),
            "account_id": str(self.account_id) if self.account_id else None,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "metadata": {
                "required_integrations": self.metadata.required_integrations,
                "tags": self.metadata.tags,
                "estimated_completion_rate": self.metadata.estimated_completion_rate,
                "is_system_template": self.metadata.is_system_template,
                "is_shared": self.metadata.is_shared,
            },
            "version": self.version,
            "usage_count": self.usage_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": str(self.created_by) if self.created_by else None,
        }


@dataclass
class TemplateUsage:
    """Template usage tracking entity.

    Records when a template is cloned to create a new workflow.

    Attributes:
        id: Unique identifier for the usage record.
        template_id: Template that was cloned.
        workflow_id: Workflow created from the template.
        account_id: Account that cloned the template.
        cloned_at: Timestamp when template was cloned.
        template_version: Version of template that was cloned.
    """

    id: UUID
    template_id: UUID
    workflow_id: UUID
    account_id: UUID
    cloned_at: datetime
    template_version: int

    @classmethod
    def create(
        cls,
        template_id: UUID,
        workflow_id: UUID,
        account_id: UUID,
        template_version: int,
    ) -> Self:
        """Factory method to create a template usage record.

        Args:
            template_id: Template that was cloned.
            workflow_id: Workflow created from template.
            account_id: Account that cloned the template.
            template_version: Version of template that was cloned.

        Returns:
            A new TemplateUsage instance.
        """
        return cls(
            id=uuid4(),
            template_id=template_id,
            workflow_id=workflow_id,
            account_id=account_id,
            cloned_at=datetime.now(UTC),
            template_version=template_version,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert template usage to dictionary representation.

        Returns:
            Dictionary containing all usage attributes.
        """
        return {
            "id": str(self.id),
            "template_id": str(self.template_id),
            "workflow_id": str(self.workflow_id),
            "account_id": str(self.account_id),
            "cloned_at": self.cloned_at.isoformat(),
            "template_version": self.template_version,
        }
