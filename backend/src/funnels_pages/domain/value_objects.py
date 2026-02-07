"""
Value objects for Funnels Pages module.
"""
from enum import Enum


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


class ElementType(str, Enum):
    """Element type enumeration."""
    HEADLINE = "headline"
    SUBHEADLINE = "subheadline"
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    BUTTON = "button"
    FORM = "form"
    COUNTDOWN_TIMER = "countdown_timer"
    COUNTDOWN_EVERGREEN = "countdown_evergreen"
    PROGRESS_BAR = "progressBar"
    SOCIAL_PROOF = "social_proof"
    TESTIMONIAL = "testimonial"
    PRICING_TABLE = "pricing_table"
    FAQ = "faq"
    CUSTOM_HTML = "custom_html"
    CUSTOM_CSS = "custom_css"
    DIVIDER = "divider"
    SPACER = "spacer"
    COLUMNS = "columns"
