"""SQLAlchemy models for CRM module.

These models define the database schema for CRM entities.
They are separate from domain entities to maintain clean architecture.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.crm.domain.value_objects import ActivityStatus, ActivityType, DealStatus


# ============================================================================
# Tag Model (SPEC-CRM-001)
# ============================================================================

class TagModel(Base):
    """SQLAlchemy model for tags."""

    __tablename__ = "crm_tags"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)  # Hex color
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    contacts: Mapped[list["ContactModel"]] = relationship(
        "ContactTag",
        back_populates="tag",
        lazy="selectin",
    )
    companies: Mapped[list["CompanyModel"]] = relationship(
        "CompanyTag",
        back_populates="tag",
        lazy="selectin",
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint("account_id", "name", name="uq_crm_tag_account_name"),
        Index("ix_crm_tags_account_name", "account_id", "name"),
    )


# ============================================================================
# Contact Model (SPEC-CRM-001)
# ============================================================================

class ContactModel(Base):
    """SQLAlchemy model for contacts."""

    __tablename__ = "crm_contacts"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    phone_country_code: Mapped[str | None] = mapped_column(String(5), nullable=True)
    company_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("crm_companies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    custom_fields: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )
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
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    company: Mapped["CompanyModel"] = relationship(
        "CompanyModel",
        back_populates="contacts",
        lazy="selectin",
    )
    tags: Mapped[list["TagModel"]] = relationship(
        "ContactTag",
        back_populates="contact",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    activities: Mapped[list["ActivityModel"]] = relationship(
        "ActivityModel",
        back_populates="contact",
        lazy="selectin",
    )
    notes: Mapped[list["NoteModel"]] = relationship(
        "NoteModel",
        back_populates="contact",
        lazy="selectin",
    )
    deals: Mapped[list["DealModel"]] = relationship(
        "DealModel",
        back_populates="contact",
        lazy="selectin",
    )

    # Constraints
    __table_args__ = (
        Index("ix_crm_contacts_account_id", "account_id"),
        Index("ix_crm_contacts_email", "email"),
        Index("ix_crm_contacts_full_name", "first_name", "last_name"),
    )


class ContactTag(Base):
    """Association table for contact-tag many-to-many relationship."""

    __tablename__ = "crm_contact_tags"

    contact_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("crm_contacts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("crm_tags.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    contact: Mapped["ContactModel"] = relationship(
        "ContactModel",
        back_populates="tags",
    )
    tag: Mapped["TagModel"] = relationship(
        "TagModel",
        back_populates="contacts",
    )


# ============================================================================
# Company Model (SPEC-CRM-003)
# ============================================================================

class CompanyModel(Base):
    """SQLAlchemy model for companies."""

    __tablename__ = "crm_companies"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    parent_company_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("crm_companies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    size: Mapped[str | None] = mapped_column(String(50), nullable=True)
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

    # Relationships
    parent_company: Mapped["CompanyModel"] = relationship(
        "CompanyModel",
        remote_side="CompanyModel.id",
        backref="child_companies",
        lazy="selectin",
    )
    contacts: Mapped[list["ContactModel"]] = relationship(
        "ContactModel",
        back_populates="company",
        lazy="selectin",
    )
    tags: Mapped[list["TagModel"]] = relationship(
        "CompanyTag",
        back_populates="company",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    activities: Mapped[list["ActivityModel"]] = relationship(
        "ActivityModel",
        back_populates="company",
        lazy="selectin",
    )
    notes: Mapped[list["NoteModel"]] = relationship(
        "NoteModel",
        back_populates="company",
        lazy="selectin",
    )
    deals: Mapped[list["DealModel"]] = relationship(
        "DealModel",
        back_populates="company",
        lazy="selectin",
    )

    # Constraints
    __table_args__ = (
        Index("ix_crm_companies_account_id", "account_id"),
        Index("ix_crm_companies_domain", "domain"),
        Index("ix_crm_companies_name", "name"),
    )


class CompanyTag(Base):
    """Association table for company-tag many-to-many relationship."""

    __tablename__ = "crm_company_tags"

    company_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("crm_companies.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("crm_tags.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    company: Mapped["CompanyModel"] = relationship(
        "CompanyModel",
        back_populates="tags",
    )
    tag: Mapped["TagModel"] = relationship(
        "TagModel",
        back_populates="companies",
    )


# ============================================================================
# Pipeline and Stage Models (SPEC-CRM-002)
# ============================================================================

class PipelineModel(Base):
    """SQLAlchemy model for pipelines."""

    __tablename__ = "crm_pipelines"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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

    # Relationships
    stages: Mapped[list["PipelineStageModel"]] = relationship(
        "PipelineStageModel",
        back_populates="pipeline",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="PipelineStageModel.order",
    )
    deals: Mapped[list["DealModel"]] = relationship(
        "DealModel",
        back_populates="pipeline",
        lazy="selectin",
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint("account_id", "name", name="uq_crm_pipeline_account_name"),
        Index("ix_crm_pipelines_account_id", "account_id"),
    )


class PipelineStageModel(Base):
    """SQLAlchemy model for pipeline stages."""

    __tablename__ = "crm_pipeline_stages"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    pipeline_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("crm_pipelines.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    probability: Mapped[int] = mapped_column(Integer, nullable=False)
    display_color: Mapped[str | None] = mapped_column(String(7), nullable=True)

    # Relationships
    pipeline: Mapped["PipelineModel"] = relationship(
        "PipelineModel",
        back_populates="stages",
        lazy="selectin",
    )
    deals: Mapped[list["DealModel"]] = relationship(
        "DealModel",
        back_populates="stage",
        lazy="selectin",
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint("pipeline_id", "order", name="uq_crm_stage_pipeline_order"),
        UniqueConstraint("pipeline_id", "name", name="uq_crm_stage_pipeline_name"),
        CheckConstraint("probability >= 0 AND probability <= 100", name="ck_stage_probability"),
        Index("ix_crm_pipeline_stages_pipeline_order", "pipeline_id", "order"),
    )


# ============================================================================
# Deal Model (SPEC-CRM-002)
# ============================================================================

class DealModel(Base):
    """SQLAlchemy model for deals."""

    __tablename__ = "crm_deals"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    pipeline_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("crm_pipelines.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stage_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("crm_pipeline_stages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    value_amount: Mapped[int] = mapped_column(Integer, nullable=False)  # Stored as cents
    value_currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    contact_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("crm_contacts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    company_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("crm_companies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[DealStatus] = mapped_column(
        Enum(DealStatus, name="deal_status", create_constraint=True),
        default=DealStatus.OPEN,
        nullable=False,
    )
    expected_close_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    actual_close_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    probability: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    pipeline: Mapped["PipelineModel"] = relationship(
        "PipelineModel",
        back_populates="deals",
        lazy="selectin",
    )
    stage: Mapped["PipelineStageModel"] = relationship(
        "PipelineStageModel",
        back_populates="deals",
        lazy="selectin",
    )
    contact: Mapped["ContactModel"] = relationship(
        "ContactModel",
        back_populates="deals",
        lazy="selectin",
    )
    company: Mapped["CompanyModel"] = relationship(
        "CompanyModel",
        back_populates="deals",
        lazy="selectin",
    )
    activities: Mapped[list["ActivityModel"]] = relationship(
        "ActivityModel",
        back_populates="deal",
        lazy="selectin",
    )
    notes: Mapped[list["NoteModel"]] = relationship(
        "NoteModel",
        back_populates="deal",
        lazy="selectin",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("probability >= 0 AND probability <= 100", name="ck_deal_probability"),
        CheckConstraint("value_amount >= 0", name="ck_deal_value"),
        Index("ix_crm_deals_account_id", "account_id"),
        Index("ix_crm_deals_status", "status"),
        Index("ix_crm_deals_pipeline_stage", "pipeline_id", "stage_id"),
    )


# ============================================================================
# Activity Model (SPEC-CRM-004)
# ============================================================================

class ActivityModel(Base):
    """SQLAlchemy model for activities."""

    __tablename__ = "crm_activities"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    activity_type: Mapped[ActivityType] = mapped_column(
        Enum(ActivityType, name="activity_type", create_constraint=True),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ActivityStatus] = mapped_column(
        Enum(ActivityStatus, name="activity_status", create_constraint=True),
        default=ActivityStatus.PENDING,
        nullable=False,
    )
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    contact_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("crm_contacts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    company_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("crm_companies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    deal_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("crm_deals.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
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

    # Relationships
    contact: Mapped["ContactModel"] = relationship(
        "ContactModel",
        back_populates="activities",
        lazy="selectin",
    )
    company: Mapped["CompanyModel"] = relationship(
        "CompanyModel",
        back_populates="activities",
        lazy="selectin",
    )
    deal: Mapped["DealModel"] = relationship(
        "DealModel",
        back_populates="activities",
        lazy="selectin",
    )

    # Constraints
    __table_args__ = (
        Index("ix_crm_activities_account_id", "account_id"),
        Index("ix_crm_activities_due_date", "due_date"),
        Index("ix_crm_activities_status", "status"),
        Index("ix_crm_activities_type", "activity_type"),
    )


# ============================================================================
# Note Model (SPEC-CRM-005)
# ============================================================================

class NoteModel(Base):
    """SQLAlchemy model for notes."""

    __tablename__ = "crm_notes"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    note_type: Mapped[str] = mapped_column(String(50), default="note", nullable=False)
    contact_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("crm_contacts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    company_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("crm_companies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    deal_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("crm_deals.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
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

    # Relationships
    contact: Mapped["ContactModel"] = relationship(
        "ContactModel",
        back_populates="notes",
        lazy="selectin",
    )
    company: Mapped["CompanyModel"] = relationship(
        "CompanyModel",
        back_populates="notes",
        lazy="selectin",
    )
    deal: Mapped["DealModel"] = relationship(
        "DealModel",
        back_populates="notes",
        lazy="selectin",
    )

    # Constraints
    __table_args__ = (
        Index("ix_crm_notes_account_id", "account_id"),
        Index("ix_crm_notes_type", "note_type"),
    )
