"""
Orders API routes - SPEC-FUN-003.
12 endpoints for order and payment management.
"""
from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from src.core.dependencies import get_db, get_current_account
from src.funnels_orders.application.use_cases import (
    CreateOrderUseCase,
    ListOrdersUseCase,
    GetOrderUseCase,
    UpdateOrderStatusUseCase,
    ProcessUpsellUseCase,
    ProcessDownsellUseCase,
    AddOrderBumpUseCase,
    ProcessRefundUseCase,
    GetOrderAnalyticsUseCase,
    HandleStripeWebhookUseCase,
    ExportOrdersUseCase,
    CreatePaymentIntentUseCase,
)

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])


class OrderCreate(BaseModel):
    funnel_id: UUID
    funnel_step_id: UUID
    contact_id: UUID | None = None
    customer: dict
    billing_address: dict
    shipping_address: dict | None = None
    items: List[dict]
    order_bumps: List[dict] = []
    payment_method: str = "stripe"
    payment_token: str
    currency: str = "usd"
    subtotal_cents: int
    tax_cents: int
    shipping_cents: int | None = None
    discount_cents: int | None = None
    total_cents: int


class OrderResponse(BaseModel):
    id: UUID
    order_number: str
    status: str
    payment_status: str
    total_cents: int
    created_at: str

    class Config:
        from_attributes = True


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Create order and process payment."""
    use_case = CreateOrderUseCase(db)
    order = await use_case.execute(account_id, data.dict())
    if not order:
        raise HTTPException(status_code=402, detail="Payment failed")
    return OrderResponse(**order.to_dict())


@router.get("")
async def list_orders(
    funnel_id: UUID | None = None,
    status: str | None = None,
    payment_status: str | None = None,
    contact_id: UUID | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """List orders with filters."""
    use_case = ListOrdersUseCase(db)
    result = await use_case.execute(account_id, {
        "funnel_id": funnel_id,
        "status": status,
        "payment_status": payment_status,
        "contact_id": contact_id,
        "date_from": date_from,
        "date_to": date_to,
        "page": page,
        "page_size": page_size,
    })
    return result


@router.get("/{order_id}")
async def get_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Get order details."""
    use_case = GetOrderUseCase(db)
    order = await use_case.execute(order_id, account_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order.to_dict()


@router.patch("/{order_id}/status")
async def update_order_status(
    order_id: UUID,
    status: str,
    notes: str | None = None,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Update order status."""
    use_case = UpdateOrderStatusUseCase(db)
    order = await use_case.execute(order_id, account_id, status, notes)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order.to_dict()


@router.post("/{order_id}/upsells")
async def process_upsell(
    order_id: UUID,
    upsell_id: UUID,
    product_id: UUID,
    quantity: int = 1,
    unit_price_cents: int = 0,
    payment_token: str = "",
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Process upsell offer."""
    use_case = ProcessUpsellUseCase(db)
    upsell = await use_case.execute(order_id, account_id, {
        "upsell_id": upsell_id,
        "product_id": product_id,
        "quantity": quantity,
        "unit_price_cents": unit_price_cents,
        "payment_token": payment_token,
    })
    if not upsell:
        raise HTTPException(status_code=400, detail="Upsell not available")
    return upsell


@router.post("/{order_id}/downsells")
async def process_downsell(
    order_id: UUID,
    downsell_data: dict,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Process downsell offer."""
    use_case = ProcessDownsellUseCase(db)
    downsell = await use_case.execute(order_id, account_id, downsell_data)
    if not downsell:
        raise HTTPException(status_code=400, detail="Downsell not available")
    return downsell


@router.post("/{order_id}/bumps")
async def add_order_bump(
    order_id: UUID,
    product_id: UUID,
    quantity: int = 1,
    payment_token: str = "",
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Add order bump to existing order."""
    use_case = AddOrderBumpUseCase(db)
    result = await use_case.execute(order_id, account_id, {
        "product_id": product_id,
        "quantity": quantity,
        "payment_token": payment_token,
    })
    if not result:
        raise HTTPException(status_code=400, detail="Cannot add bumps to this order")
    return result


@router.post("/{order_id}/refunds")
async def process_refund(
    order_id: UUID,
    amount_cents: int | None = None,
    reason: str = "",
    refund_type: str = "full",
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Process refund."""
    use_case = ProcessRefundUseCase(db)
    refund = await use_case.execute(order_id, account_id, {
        "amount_cents": amount_cents,
        "reason": reason,
        "refund_type": refund_type,
    })
    if not refund:
        raise HTTPException(status_code=403, detail="Cannot refund this order")
    return refund


@router.get("/analytics")
async def get_order_analytics(
    funnel_id: UUID | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    granularity: str = "day",
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Get order analytics."""
    use_case = GetOrderAnalyticsUseCase(db)
    return await use_case.execute(account_id, {
        "funnel_id": funnel_id,
        "date_from": date_from,
        "date_to": date_to,
        "granularity": granularity,
    })


@router.post("/webhooks/stripe")
async def handle_stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle Stripe webhook events."""
    use_case = HandleStripeWebhookUseCase(db)
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    await use_case.execute(payload, sig_header)
    return {"status": "ok"}


@router.post("/export")
async def export_orders(
    filters: dict,
    columns: List[str],
    format: str = "csv",
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Export orders to file."""
    use_case = ExportOrdersUseCase(db)
    result = await use_case.execute(account_id, filters, columns, format)
    return result


@router.post("/payment-intent")
async def create_payment_intent(
    amount_cents: int,
    currency: str = "usd",
    metadata: dict | None = None,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Create Stripe PaymentIntent."""
    use_case = CreatePaymentIntentUseCase(db)
    intent = await use_case.execute(account_id, amount_cents, currency, metadata)
    return intent
