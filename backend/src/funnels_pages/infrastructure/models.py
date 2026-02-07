"""
SQLAlchemy models for Funnels Pages module.
"""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from src.core.database import Base


class PageModel(Base):
    """Page SQLAlchemy model."""
    __tablename__ = "pages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    funnel_id = Column(UUID(as_uuid=True), ForeignKey("funnels.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(100), nullable=False)
    page_type = Column(String(20), nullable=False)
    slug = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default="draft", index=True)
    seo_title = Column(String(60))
    seo_description = Column(String(160))
    og_title = Column(String(100))
    og_description = Column(String(200))
    og_image = Column(String(500))
    canonical_url = Column(String(500))
    elements = Column(JSONB, nullable=False, default=[])
    responsive_settings = Column(JSONB, nullable=False, default={})
    tracking_scripts = Column(JSONB, nullable=False, default=[])
    custom_head = Column(Text)
    custom_body = Column(Text)
    published_url = Column(String(500))
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)
    last_published_at = Column(DateTime)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    deleted_at = Column(DateTime, nullable=True, index=True)

    __table_args__ = (
        Index("idx_pages_account_id", "account_id"),
        Index("idx_pages_funnel_id", "funnel_id"),
        Index("idx_pages_status", "status"),
        Index("idx_pages_deleted_at", "deleted_at"),
        Index("idx_pages_account_slug_unique", "account_id", "slug", "deleted_at", unique=True),
    )


class PageAssetModel(Base):
    """Page asset SQLAlchemy model."""
    __tablename__ = "page_assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    page_id = Column(UUID(as_uuid=True), ForeignKey("pages.id", ondelete="SET NULL"), nullable=True)
    filename = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    size = Column(Integer, nullable=False)
    content_type = Column(String(100), nullable=False)
    width = Column(Integer)
    height = Column(Integer)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    uploaded_by = Column(UUID(as_uuid=True), nullable=False)

    __table_args__ = (
        Index("idx_page_assets_account_id", "account_id"),
        Index("idx_page_assets_page_id", "page_id"),
    )


class PageVersionModel(Base):
    """Page version history SQLAlchemy model."""
    __tablename__ = "page_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    page_id = Column(UUID(as_uuid=True), ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    page_snapshot = Column(JSONB, nullable=False)
    change_summary = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=False)

    __table_args__ = (
        Index("idx_page_versions_page_id", "page_id"),
        Index("idx_page_versions_page_version_unique", "page_id", "version", unique=True),
    )
