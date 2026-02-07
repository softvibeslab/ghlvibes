"""
SQLAlchemy models for Funnels module.
"""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Integer, Text, JSON, DateTime, ForeignKey, Enum, Boolean, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from src.core.database import Base


class FunnelModel(Base):
    """Funnel SQLAlchemy model."""
    __tablename__ = "funnels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    funnel_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="draft", index=True)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    deleted_at = Column(DateTime, nullable=True, index=True)

    # Relationships
    steps = relationship("FunnelStepModel", back_populates="funnel", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_funnels_account_name_unique", "account_id", "name", "deleted_at"),
    )


class FunnelStepModel(Base):
    """Funnel step SQLAlchemy model."""
    __tablename__ = "funnel_steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    funnel_id = Column(UUID(as_uuid=True), ForeignKey("funnels.id", ondelete="CASCADE"), nullable=False)
    step_type = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    order = Column(Integer, nullable=False)
    page_id = Column(UUID(as_uuid=True), ForeignKey("pages.id", ondelete="SET NULL"))
    config = Column(JSONB, nullable=False, default={})
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    funnel = relationship("FunnelModel", back_populates="steps")

    __table_args__ = (
        Index("idx_funnel_steps_funnel_id", "funnel_id"),
        Index("idx_funnel_steps_page_id", "page_id"),
        Index("idx_funnel_steps_funnel_order_unique", "funnel_id", "order", unique=True),
    )


class FunnelTemplateModel(Base):
    """Funnel template SQLAlchemy model."""
    __tablename__ = "funnel_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    category = Column(String(50), index=True)
    funnel_type = Column(String(50), nullable=False, index=True)
    preview_image_url = Column(String(500))
    template_data = Column(JSONB, nullable=False)
    use_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_system_template = Column(Boolean, nullable=False, default=True)

    __table_args__ = (
        Index("idx_funnel_templates_category", "category"),
        Index("idx_funnel_templates_type", "funnel_type"),
    )


class FunnelVersionModel(Base):
    """Funnel version history SQLAlchemy model."""
    __tablename__ = "funnel_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    funnel_id = Column(UUID(as_uuid=True), ForeignKey("funnels.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    funnel_snapshot = Column(JSONB, nullable=False)
    change_description = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=False)

    __table_args__ = (
        Index("idx_funnel_versions_funnel_id", "funnel_id"),
        Index("idx_funnel_versions_funnel_version_unique", "funnel_id", "version", unique=True),
    )
