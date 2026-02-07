"""
Value objects for Funnels Orders module.
"""
from enum import Enum


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class PaymentStatus(str, Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class ExitOutcome(str, Enum):
    """Step exit outcome enumeration."""
    FORWARD = "forward"
    BACKWARD = "backward"
    BOUNCE = "bounce"
    CLOSE = "close"
