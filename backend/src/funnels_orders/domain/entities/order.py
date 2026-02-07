"""
Order aggregate root entity.
"""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID, uuid4

from src.funnels_orders.domain.value_objects import OrderStatus, PaymentStatus


@dataclass
class OrderItem:
    """Order item value object."""
    product_id: UUID
    product_name: str
    quantity: int
    unit_price_cents: int
    tax_cents: int = 0
    discount_cents: int = 0

    @property
    def total_cents(self) -> int:
        """Calculate total for this item."""
        return (self.unit_price_cents * self.quantity) + self.tax_cents - self.discount_cents


@dataclass
class OrderBump:
    """Order bump value object."""
    product_id: UUID
    product_name: str
    quantity: int
    unit_price_cents: int

    @property
    def total_cents(self) -> int:
        """Calculate total for this bump."""
        return self.unit_price_cents * self.quantity


@dataclass
class UpsellDownsell:
    """Upsell/Downsell value object."""
    id: UUID = field(default_factory=uuid4)
    funnel_step_id: UUID = None
    offer_type: Literal["upsell", "downsell"] = "upsell"
    product_id: UUID = None
    product_name: str = ""
    quantity: int = 1
    unit_price_cents: int = 0
    status: str = "accepted"
    stripe_payment_intent_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    responded_at: Optional[datetime] = None

    @property
    def total_cents(self) -> int:
        """Calculate total for this upsell/downsell."""
        return self.unit_price_cents * self.quantity


@dataclass
class Refund:
    """Refund value object."""
    id: UUID = field(default_factory=uuid4)
    amount_cents: int = 0
    reason: str = ""
    status: str = "pending"
    stripe_refund_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


@dataclass
class Address:
    """Address value object."""
    line1: str = ""
    line2: Optional[str] = None
    city: str = ""
    state: str = ""
    postal_code: str = ""
    country: str = "US"


@dataclass
class Customer:
    """Customer value object."""
    email: str = ""
    name: Optional[str] = None
    phone: Optional[str] = None


@dataclass
class Order:
    """
    Order aggregate root.

    Invariants:
    - Order number must be unique
    - Total must match sum of items + bumps + tax + shipping - discounts
    - Payment status must match order status
    """
    id: UUID = field(default_factory=uuid4)
    account_id: UUID = None
    funnel_id: UUID = None
    funnel_step_id: UUID = None
    contact_id: Optional[UUID] = None
    order_number: str = ""
    customer: Customer = field(default_factory=Customer)
    billing_address: Address = field(default_factory=Address)
    shipping_address: Optional[Address] = None
    items: List[OrderItem] = field(default_factory=list)
    order_bumps: List[OrderBump] = field(default_factory=list)
    upsells: list = field(default_factory=list)
    downsells: list = field(default_factory=list)
    refunds: List[Refund] = field(default_factory=list)
    currency: str = "usd"
    subtotal_cents: int = 0
    tax_cents: int = 0
    shipping_cents: int = 0
    discount_cents: int = 0
    total_cents: int = 0
    status: OrderStatus = OrderStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.PENDING
    payment_method: str = "stripe"
    stripe_payment_intent_id: Optional[str] = None
    paid_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    affiliate_id: Optional[UUID] = None
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate order invariants."""
        if not self.customer.email:
            raise ValueError("Customer email is required")
        self._recalculate_totals()

    def _recalculate_totals(self) -> None:
        """Recalculate order totals."""
        self.subtotal_cents = sum(item.total_cents for item in self.items)
        bump_total = sum(bump.total_cents for bump in self.order_bumps)
        upsell_total = sum(u.total_cents for u in self.upsells if u.status == "accepted")
        downsell_total = sum(d.total_cents for d in self.downsells if d.status == "accepted")
        self.total_cents = (
            self.subtotal_cents
            + bump_total
            + upsell_total
            + downsell_total
            + self.tax_cents
            + self.shipping_cents
            - self.discount_cents
        )

    def add_item(self, item: OrderItem) -> None:
        """Add item to order."""
        self.items.append(item)
        self._recalculate_totals()
        self.updated_at = datetime.utcnow()

    def add_bump(self, bump: OrderBump) -> None:
        """Add order bump."""
        if self.status not in [OrderStatus.PENDING, OrderStatus.PROCESSING]:
            raise ValueError("Cannot add bumps to shipped or completed orders")
        self.order_bumps.append(bump)
        self._recalculate_totals()
        self.updated_at = datetime.utcnow()

    def add_upsell(self, upsell: UpsellDownsell) -> None:
        """Add upsell to order."""
        if self.status != OrderStatus.COMPLETED:
            raise ValueError("Upsells only available for completed orders")
        self.upsells.append(upsell)
        self._recalculate_totals()
        self.updated_at = datetime.utcnow()

    def add_downsell(self, downsell: UpsellDownsell) -> None:
        """Add downsell to order."""
        if self.status != OrderStatus.COMPLETED:
            raise ValueError("Downsells only available for completed orders")
        self.downsells.append(downsell)
        self._recalculate_totals()
        self.updated_at = datetime.utcnow()

    def mark_paid(self, payment_intent_id: str) -> None:
        """Mark order as paid."""
        if self.payment_status == PaymentStatus.PAID:
            raise ValueError("Order is already paid")
        self.payment_status = PaymentStatus.PAID
        self.status = OrderStatus.PROCESSING
        self.stripe_payment_intent_id = payment_intent_id
        self.paid_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def mark_failed(self, reason: str) -> None:
        """Mark order as failed."""
        self.payment_status = PaymentStatus.FAILED
        self.status = OrderStatus.FAILED
        self.failure_reason = reason
        self.updated_at = datetime.utcnow()

    def complete(self) -> None:
        """Mark order as completed."""
        if self.payment_status != PaymentStatus.PAID:
            raise ValueError("Cannot complete unpaid order")
        self.status = OrderStatus.COMPLETED
        self.updated_at = datetime.utcnow()

    def cancel(self) -> None:
        """Cancel the order."""
        if self.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
            raise ValueError("Cannot cancel completed or already cancelled order")
        self.status = OrderStatus.CANCELLED
        self.updated_at = datetime.utcnow()

    def process_refund(self, amount_cents: int, reason: str) -> Refund:
        """Process a refund."""
        if self.payment_status != PaymentStatus.PAID:
            raise ValueError("Cannot refund unpaid order")
        total_refunded = sum(r.amount_cents for r in self.refunds if r.status == "completed")
        if total_refunded + amount_cents > self.total_cents:
            raise ValueError("Refund amount exceeds total paid")
        refund = Refund(amount_cents=amount_cents, reason=reason)
        self.refunds.append(refund)
        if total_refunded + amount_cents >= self.total_cents:
            self.payment_status = PaymentStatus.REFUNDED
        else:
            self.payment_status = PaymentStatus.PARTIALLY_REFUNDED
        self.updated_at = datetime.utcnow()
        return refund

    def calculate_affiliate_commission(self, rate: Decimal) -> int:
        """Calculate affiliate commission."""
        if not self.affiliate_id:
            return 0
        return int(self.total_cents * Decimal(rate))

    @property
    def can_add_bumps(self) -> bool:
        """Check if order bumps can still be added."""
        return self.status in [OrderStatus.PENDING, OrderStatus.PROCESSING]

    @property
    def can_offer_upsells(self) -> bool:
        """Check if upsells can be offered."""
        return self.status == OrderStatus.COMPLETED

    @property
    def is_paid(self) -> bool:
        """Check if order is paid."""
        return self.payment_status == PaymentStatus.PAID

    @property
    def is_refunded(self) -> bool:
        """Check if order is refunded."""
        return self.payment_status in [PaymentStatus.REFUNDED, PaymentStatus.PARTIALLY_REFUNDED]
