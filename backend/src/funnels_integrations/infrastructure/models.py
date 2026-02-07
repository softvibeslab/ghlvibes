"""
SQLAlchemy models for Funnels Integrations module.
"""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Boolean, ARRAY, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB

from src.core.database import Base


class IntegrationModel(Base):
    """Integration SQLAlchemy model."""
    __tablename__ = "integrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    provider = Column(String(50), nullable=False)
    integration_type = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    credentials = Column(Text, nullable=False)  # Encrypted
    settings = Column(JSONB, nullable=False, default={})
    mappings = Column(JSONB, nullable=False, default=[])
    status = Column(String(20), nullable=False, default="active")
    last_verified_at = Column(DateTime)
    health_status = Column(String(20), nullable=False, default="unknown")
    last_health_check_at = Column(DateTime)
    health_error_message = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_integrations_account_id", "account_id"),
        Index("idx_integrations_provider", "provider"),
        Index("idx_integrations_type", "integration_type"),
        Index("idx_integrations_status", "status"),
    )


class WebhookModel(Base):
    """Webhook SQLAlchemy model."""
    __tablename__ = "webhooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    events = Column(ARRAY(String), nullable=False)
    url = Column(String(500), nullable=False)
    method = Column(String(10), nullable=False, default="POST")
    headers = Column(JSONB, nullable=False, default=[])
    retry_config = Column(JSONB, nullable=False, default={"enabled": True, "max_retries": 3, "retry_after_seconds": 60})
    secret = Column(String(255))
    status = Column(String(20), nullable=False, default="active")
    last_triggered_at = Column(DateTime)
    trigger_count = Column(Integer, nullable=False, default=0)
    failure_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_webhooks_account_id", "account_id"),
        Index("idx_webhooks_status", "status"),
    )


class WebhookDeliveryModel(Base):
    """Webhook delivery SQLAlchemy model."""
    __tablename__ = "webhook_deliveries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    webhook_id = Column(UUID(as_uuid=True), ForeignKey("webhooks.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(100), nullable=False)
    payload = Column(JSONB, nullable=False)
    response_status = Column(Integer)
    response_body = Column(Text)
    attempt_number = Column(Integer, nullable=False, default=1)
    delivered_at = Column(DateTime)
    failed_at = Column(DateTime)
    error_message = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_webhook_deliveries_webhook_id", "webhook_id"),
        Index("idx_webhook_deliveries_created_at", "created_at"),
    )


class IntegrationSyncLogModel(Base):
    """Integration sync log SQLAlchemy model."""
    __tablename__ = "integration_sync_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    integration_id = Column(UUID(as_uuid=True), ForeignKey("integrations.id", ondelete="CASCADE"), nullable=False)
    sync_type = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String(20), nullable=False)
    request_payload = Column(JSONB)
    response_payload = Column(JSONB)
    error_message = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_integration_sync_logs_integration_id", "integration_id"),
        Index("idx_integration_sync_logs_created_at", "created_at"),
    )
