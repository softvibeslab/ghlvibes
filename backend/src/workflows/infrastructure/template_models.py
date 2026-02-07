"""SQLAlchemy models for workflow templates.

These models define the database schema for workflow templates
and template usage tracking.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class TemplateModel(Base):
    """SQLAlchemy model for workflow templates.

    Represents reusable workflow templates that can be cloned
    to create new workflow instances.
    """

    __tablename__ = "workflow_templates"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign key
    account_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        index=True,
    )

    # Template details
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    # Metadata (as JSONB columns for simplicity)
    required_integrations: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        default=list,
        nullable=False,
    )
    tags: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        default=list,
        nullable=False,
    )
    estimated_completion_rate: Mapped[float | None] = mapped_column(
        Integer,
        nullable=True,
    )
    is_system_template: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
    is_shared: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    # Workflow configuration
    workflow_config: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )

    # Versioning and usage
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    usage_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    created_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )

    # Indexes
    __table_args__ = (
        Index("idx_templates_account_category", "account_id", "category"),
        Index("idx_templates_system", "is_system_template"),
        Index("idx_templates_tags", "tags", postgresql_using="gin"),
    )

    def to_domain(self) -> Any:
        """Convert model to domain entity.

        Returns:
            WorkflowTemplate domain entity.
        """
        from src.workflows.domain.template_entities import (  # noqa: PLC0415
            TemplateCategory,
            TemplateMetadata,
            WorkflowTemplate,
        )

        metadata = TemplateMetadata(
            category=TemplateCategory(self.category),
            required_integrations=self.required_integrations,
            tags=self.tags,
            estimated_completion_rate=self.estimated_completion_rate,
            is_system_template=self.is_system_template,
            is_shared=self.is_shared,
        )

        return WorkflowTemplate(
            id=self.id,
            account_id=self.account_id,
            name=self.name,
            description=self.description,
            category=TemplateCategory(self.category),
            metadata=metadata,
            workflow_config=self.workflow_config,
            version=self.version,
            usage_count=self.usage_count,
            created_at=self.created_at,
            updated_at=self.updated_at,
            created_by=self.created_by,
        )

    @classmethod
    def from_domain(cls, template: Any) -> "TemplateModel":
        """Create model from domain entity.

        Args:
            template: WorkflowTemplate domain entity.

        Returns:
            TemplateModel instance.
        """
        return cls(
            id=template.id,
            account_id=template.account_id,
            name=template.name,
            description=template.description,
            category=template.category.value,
            required_integrations=template.metadata.required_integrations,
            tags=template.metadata.tags,
            estimated_completion_rate=template.metadata.estimated_completion_rate,
            is_system_template=template.metadata.is_system_template,
            is_shared=template.metadata.is_shared,
            workflow_config=template.workflow_config,
            version=template.version,
            usage_count=template.usage_count,
            created_at=template.created_at,
            updated_at=template.updated_at,
            created_by=template.created_by,
        )


class TemplateUsageModel(Base):
    """SQLAlchemy model for template usage tracking.

    Records when templates are cloned to create new workflows.
    """

    __tablename__ = "template_usage"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys
    template_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    workflow_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Usage details
    cloned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    template_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Indexes
    __table_args__ = (
        Index("idx_template_usage_template", "template_id"),
        Index("idx_template_usage_workflow", "workflow_id"),
        Index("idx_template_usage_account", "account_id"),
    )

    def to_domain(self) -> Any:
        """Convert model to domain entity.

        Returns:
            TemplateUsage domain entity.
        """
        from src.workflows.domain.template_entities import TemplateUsage  # noqa: PLC0415

        return TemplateUsage(
            id=self.id,
            template_id=self.template_id,
            workflow_id=self.workflow_id,
            account_id=self.account_id,
            cloned_at=self.cloned_at,
            template_version=self.template_version,
        )

    @classmethod
    def from_domain(cls, usage: Any) -> "TemplateUsageModel":
        """Create model from domain entity.

        Args:
            usage: TemplateUsage domain entity.

        Returns:
            TemplateUsageModel instance.
        """
        return cls(
            id=usage.id,
            template_id=usage.template_id,
            workflow_id=usage.workflow_id,
            account_id=usage.account_id,
            cloned_at=usage.cloned_at,
            template_version=usage.template_version,
        )
