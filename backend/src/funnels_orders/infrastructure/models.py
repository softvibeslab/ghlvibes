"""
SQLAlchemy models for Funnels Orders module.
"""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Numeric, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from src.core.database import Base


class OrderModel(Base):
    """Order SQLAlchemy model."""
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    funnel_id = Column(UUID(as_uuid=True), ForeignKey("funnels.id"), nullable=False)
    funnel_step_id = Column(UUID(as_uuid=True), ForeignKey("funnel_steps.id"), nullable=False)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=True)
    order_number = Column(String(50), nullable=False, unique=True)
    customer_email = Column(String(255), nullable=False)
    customer_name = Column(String(255))
    customer_phone = Column(String(50))
    billing_address = Column(JSONB, nullable=False)
    shipping_address = Column(JSONB)
    currency = Column(String(3), nullable=False, default="usd")
    subtotal_cents = Column(Integer, nullable=False)
    tax_cents = Column(Integer, nullable=False, default=0)
    shipping_cents = Column(Integer, nullable=True)
    discount_cents = Column(Integer, nullable=True, default=0)
    total_cents = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="pending", index=True)
    payment_status = Column(String(20), nullable=False, default="pending", index=True)
    payment_method = Column(String(20), nullable=False)
    stripe_payment_intent_id = Column(String(255), unique=True)
    paid_at = Column(DateTime)
    failure_reason = Column(Text)
    metadata = Column(JSONB, default={})
    affiliate_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = relationship("OrderItemModel", back_populates="order", cascade="all, delete-orphan")
    order_bumps = relationship("OrderBumpModel", back_populates="order", cascade="all, delete-orphan")
    upsells = relationship("OrderUpsellModel", back_populates="order", cascade="all, delete-orphan")
    refunds = relationship("RefundModel", back_populates="order", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_orders_account_id", "account_id"),
        Index("idx_orders_funnel_id", "funnel_id"),
        Index("idx_orders_contact_id", "contact_id"),
        Index("idx_orders_status", "status"),
        Index("idx_orders_payment_status", "payment_status"),
        Index("idx_orders_created_at", "created_at"),
        Index("idx_orders_order_number", "order_number"),
    )


class OrderItemModel(Base):
    """Order item SQLAlchemy model."""
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price_cents = Column(Integer, nullable=False)
    tax_cents = Column(Integer, nullable=False, default=0)
    discount_cents = Column(Integer, nullable=True, default=0)
    total_cents = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    order = relationship("OrderModel", back_populates="items")

    __table_args__ = (
        Index("idx_order_items_order_id", "order_id"),
        Index("idx_order_items_product_id", "product_id"),
    )


class OrderBumpModel(Base):
    """Order bump SQLAlchemy model."""
    __tablename__ = "order_bumps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price_cents = Column(Integer, nullable=False)
    total_cents = Column(Integer, nullable=False)
    accepted_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    order = relationship("OrderModel", back_populates="order_bumps")

    __table_args__ = (
        Index("idx_order_bumps_order_id", "order_id"),
    )


class OrderUpsellModel(Base):
    """Upsell/Downsell SQLAlchemy model."""
    __tablename__ = "order_upsells"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    funnel_step_id = Column(UUID(as_uuid=True), ForeignKey("funnel_steps.id"), nullable=False)
    offer_type = Column(String(10), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price_cents = Column(Integer, nullable=False)
    total_cents = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="accepted")
    stripe_payment_intent_id = Column(String(255), unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    responded_at = Column(DateTime)

    # Relationships
    order = relationship("OrderModel", back_populates="upsells")

    __table_args__ = (
        Index("idx_order_upsells_order_id", "order_id"),
    )


class RefundModel(Base):
    """Refund SQLAlchemy model."""
    __tablename__ = "refunds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    amount_cents = Column(Integer, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    stripe_refund_id = Column(String(255), unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime)

    # Relationships
    order = relationship("OrderModel", back_populates="refunds")

    __table_args__ = (
        Index("idx_refunds_order_id", "order_id"),
        Index("idx_refunds_status", "status"),
    )
