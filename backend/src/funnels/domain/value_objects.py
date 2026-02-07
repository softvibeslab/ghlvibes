"""
Value objects for Funnels module.
"""
from enum import Enum
from typing import Literal


class FunnelStatus(str, Enum):
    """Funnel status enumeration."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class FunnelType(str, Enum):
    """Funnel type enumeration."""
    LEAD_GENERATION = "lead_generation"
    SALES = "sales"
    WEBINAR = "webinar"
    BOOKING = "booking"


class StepType(str, Enum):
    """Funnel step type enumeration."""
    PAGE = "page"
    UPSELL = "upsell"
    DOWNSELL = "downsell"
    ORDER_BUMP = "order_bump"
    THANK_YOU = "thank_you"


class PageType(str, Enum):
    """Page type enumeration."""
    OPTIN = "optin"
    SALES = "sales"
    CHECKOUT = "checkout"
    THANK_YOU = "thank_you"
    WEBINAR = "webinar"
    ORDER_FORM = "order_form"


class PageStatus(str, Enum):
    """Page status enumeration."""
    DRAFT = "draft"
    PUBLISHED = "published"


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


class ConversionType(str, Enum):
    """Conversion type enumeration."""
    FORM_SUBMIT = "form_submit"
    PURCHASE = "purchase"
    SIGNUP = "signup"
    CUSTOM = "custom"


class EventType(str, Enum):
    """Analytics event type enumeration."""
    PAGE_VIEW = "page_view"
    CONVERSION = "conversion"
    STEP_ENTRY = "step_entry"
    STEP_EXIT = "step_exit"
