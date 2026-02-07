# Funnels Module Backend - Quick Start Guide

## Overview

Complete backend implementation for GoHighLevel Clone Funnels Module with **5 SPECs, 65 endpoints, 20 tables, and full DDD architecture**.

---

## Project Structure

```
backend/src/
├── funnels/                    # SPEC-FUN-001: Funnel Builder
│   ├── domain/
│   │   ├── entities/funnel.py
│   │   └── value_objects.py
│   ├── application/
│   │   └── use_cases/
│   ├── infrastructure/
│   │   ├── models.py
│   │   └── migrations/versions/
│   └── presentation/
│       └── routes/funnels.py
├── funnels_pages/              # SPEC-FUN-002: Pages & Elements
│   └── [same DDD structure]
├── funnels_orders/             # SPEC-FUN-003: Orders & Payments
│   └── [same DDD structure]
├── funnels_analytics/          # SPEC-FUN-004: Funnel Analytics
│   └── [same DDD structure]
├── funnels_integrations/       # SPEC-FUN-005: Integrations
│   └── [same DDD structure]
└── tests/
    └── funnels/
```

---

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt

# Key dependencies:
# - fastapi[all] >= 0.115
# - sqlalchemy[asyncio] >= 2.0
# - alembic
# - stripe
# - redis
# - pytest
# - pytest-asyncio
```

### 2. Configure Environment

Create `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/gohighlevel
REDIS_URL=redis://localhost:6379/0
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
AWS_S3_BUCKET=your-bucket
SECRET_KEY=your-secret-key
```

### 3. Run Migrations

```bash
# Run all migrations
alembic upgrade head

# Creates 20 tables:
# - 4 funnel tables
# - 3 page tables
# - 5 order tables
# - 4 analytics tables
# - 4 integration tables
```

### 4. Start Server

```bash
# Development
uvicorn src.main:app --reload --port 8000

# Production
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Access API Documentation

```
http://localhost:8000/docs - Swagger UI
http://localhost:8000/redoc - ReDoc
```

---

## API Endpoints by Module

### Funnel Builder (14 endpoints)

```bash
# Create funnel
POST /api/v1/funnels
{
  "name": "Lead Gen Funnel",
  "funnel_type": "lead_generation",
  "steps": [
    {"step_type": "page", "name": "Opt-in", "page_id": "..."}
  ]
}

# List funnels
GET /api/v1/funnels?page=1&page_size=20

# Get funnel detail
GET /api/v1/funnels/{id}

# Clone funnel
POST /api/v1/funnels/{id}/clone

# Add step
POST /api/v1/funnels/{id}/steps

# Publish funnel
PATCH /api/v1/funnels/{id}?status=active
```

### Pages & Elements (15 endpoints)

```bash
# Create page
POST /api/v1/pages
{
  "name": "Opt-in Page",
  "page_type": "optin",
  "slug": "lead-magnet",
  "elements": [
    {
      "element_type": "headline",
      "props": {"text": "Get Your Free Guide!"}
    }
  ]
}

# Publish page
POST /api/v1/pages/{id}/publish

# Get element library
GET /api/v1/pages/elements/library

# Preview page
GET /api/v1/pages/{id}/preview?device=mobile
```

### Orders & Payments (12 endpoints)

```bash
# Create PaymentIntent
POST /api/v1/orders/payment-intent
{
  "amount_cents": 9900,
  "currency": "usd"
}
# Returns: { client_secret: "pi_..." }

# Create order
POST /api/v1/orders
{
  "funnel_id": "...",
  "customer": {"email": "user@example.com"},
  "items": [...],
  "payment_token": "pi_..."
}

# Process upsell
POST /api/v1/orders/{id}/upsells
{
  "product_id": "...",
  "payment_token": "pi_..."
}

# Get analytics
GET /api/v1/orders/analytics?funnel_id=...&date_from=...&date_to=...
```

### Analytics (10 endpoints)

```bash
# Track event
POST /api/v1/analytics/track
{
  "event_type": "page_view",
  "funnel_id": "...",
  "visitor_id": "...",
  "session_id": "..."
}

# Get funnel overview
GET /api/v1/analytics/funnels/{id}/overview?date_from=...&date_to=...

# Get drop-off analysis
GET /api/v1/analytics/funnels/{id}/dropoffs

# Real-time data
GET /api/v1/analytics/funnels/{id}/realtime
```

### Integrations (14 endpoints)

```bash
# Create email integration
POST /api/v1/integrations/email
{
  "provider": "mailchimp",
  "credentials": {"api_key": "..."},
  "settings": {"default_list_id": "..."}
}

# Test connection
POST /api/v1/integrations/{id}/test

# Create webhook
POST /api/v1/integrations/webhooks
{
  "name": "New Lead Webhook",
  "events": ["contact.created"],
  "url": "https://yourapp.com/webhooks"
}
```

---

## Domain Model Examples

### Funnel Aggregate

```python
from src.funnels.domain.entities import Funnel, FunnelStep
from src.funnels.domain.value_objects import FunnelType, FunnelStatus

# Create funnel
funnel = Funnel(
    account_id=uuid4(),
    name="Sales Funnel",
    funnel_type=FunnelType.SALES,
    status=FunnelStatus.DRAFT,
    created_by=user_id,
)

# Add steps
step1 = FunnelStep(
    step_type="page",
    name="Sales Page",
    page_id=page_id,
)

step2 = FunnelStep(
    step_type="upsell",
    name="Order Bump",
)

funnel.add_step(step1)
funnel.add_step(step2)

# Publish
funnel.publish()

# Clone
cloned = funnel.clone("Sales Funnel 2")
```

### Order Aggregate

```python
from src.funnels_orders.domain.entities import (
    Order, OrderItem, Customer, Address
)

# Create order
order = Order(
    account_id=account_id,
    funnel_id=funnel_id,
    customer=Customer(email="user@example.com", name="John Doe"),
    billing_address=Address(
        line1="123 Main St",
        city="New York",
        state="NY",
        postal_code="10001",
    ),
    items=[
        OrderItem(
            product_id=product_id,
            product_name="Course",
            quantity=1,
            unit_price_cents=9900,
        )
    ],
)

# Add order bump
order.add_bump(OrderBump(
    product_id=bump_id,
    product_name="Premium Support",
    quantity=1,
    unit_price_cents=4900,
))

# Mark as paid
order.mark_paid(payment_intent_id="pi_...")

# Complete
order.complete()

# Process refund
refund = order.process_refund(
    amount_cents=5000,
    reason="Customer request"
)
```

---

## Testing

### Run All Tests

```bash
# Run with coverage
pytest tests/ --cov=src/funnels* --cov-report=html

# Run specific module
pytest tests/funnels/test_funnel.py -v

# Run async tests
pytest tests/ -k "async" --asyncio-mode=auto
```

### Test Examples

```python
# Domain tests
async def test_funnel_creation():
    funnel = Funnel(
        account_id=uuid4(),
        name="Test Funnel",
        funnel_type=FunnelType.LEAD_GENERATION,
        created_by=uuid4(),
    )
    assert funnel.version == 1
    assert funnel.status == FunnelStatus.DRAFT

# API tests
async def test_create_funnel_endpoint(async_client):
    response = await async_client.post(
        "/api/v1/funnels",
        json={"name": "Test", "funnel_type": "lead_generation"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test"
```

---

## Database Schema

### Key Tables

```sql
-- Funnels
funnels (id, account_id, name, funnel_type, status, version)
funnel_steps (id, funnel_id, step_type, name, order, page_id)
funnel_templates (id, name, category, template_data)
funnel_versions (id, funnel_id, version, funnel_snapshot)

-- Pages
pages (id, account_id, funnel_id, name, slug, elements, status)
page_assets (id, account_id, page_id, url, filename, size)
page_versions (id, page_id, version, page_snapshot)

-- Orders
orders (id, account_id, order_number, total_cents, status, payment_status)
order_items (id, order_id, product_id, quantity, unit_price_cents)
order_bumps (id, order_id, product_id, quantity, unit_price_cents)
order_upsells (id, order_id, offer_type, product_id, total_cents)
refunds (id, order_id, amount_cents, reason, status)

-- Analytics
analytics_events (id, account_id, funnel_id, event_type, visitor_id, created_at)
funnel_step_stats (funnel_id, funnel_step_id, date, unique_visitors, entries, exits)
ab_tests (id, account_id, funnel_id, test_name, status, winner_variant_id)
ab_test_variants (id, test_id, variant_name, is_control, traffic_split)

-- Integrations
integrations (id, account_id, provider, integration_type, credentials, settings)
webhooks (id, account_id, name, events, url, retry_config)
webhook_deliveries (id, webhook_id, event_type, payload, response_status)
integration_sync_logs (id, integration_id, sync_type, entity_id, status)
```

---

## Common Workflows

### Create Complete Funnel

```python
# 1. Create funnel
funnel = await create_funnel(account_id, {
    "name": "Webinar Funnel",
    "funnel_type": "webinar",
    "steps": []
})

# 2. Create pages
optin_page = await create_page(account_id, {
    "name": "Registration",
    "page_type": "optin",
    "slug": "webinar-register",
    "elements": [...]
})

thank_you_page = await create_page(account_id, {
    "name": "Thank You",
    "page_type": "thank_you",
    "slug": "webinar-thank-you",
    "elements": [...]
})

# 3. Add steps to funnel
await add_step(funnel_id, {
    "step_type": "page",
    "name": "Registration",
    "page_id": optin_page.id
})

await add_step(funnel_id, {
    "step_type": "thank_you",
    "name": "Thank You",
    "page_id": thank_you_page.id
})

# 4. Publish funnel
await update_funnel(funnel_id, {"status": "active"})
```

### Process Order with Upsells

```python
# 1. Create payment intent
payment = await create_payment_intent(account_id, {
    "amount_cents": 9900,
    "currency": "usd"
})
client_secret = payment["client_secret"]

# 2. Complete payment on frontend, get token
# ... Stripe Elements payment ...

# 3. Create order
order = await create_order(account_id, {
    "funnel_id": funnel_id,
    "customer": {"email": "user@example.com"},
    "items": [{"product_id": pid, "quantity": 1, "unit_price_cents": 9900}],
    "payment_token": payment_token
})

# 4. Offer upsell
upsell = await process_upsell(order_id, {
    "upsell_id": upsell_step_id,
    "product_id": upsell_product_id,
    "payment_token": upsell_payment_token
})

# 5. Track conversion
await track_event(account_id, {
    "event_type": "conversion",
    "funnel_id": funnel_id,
    "conversion_type": "purchase",
    "value_cents": order["total_cents"]
})
```

---

## Performance Tips

### Database Queries

```python
# ✅ GOOD: Use indexes
db.query(FunnelModel).filter(
    FunnelModel.account_id == account_id,
    FunnelModel.status == "active"
).all()

# ❌ BAD: Full table scan
db.query(FunnelModel).filter(
    FunnelModel.name.contains("test")
).all()
```

### Caching

```python
# Real-time analytics (5-second cache)
redis.set(f"funnel:{funnel_id}:realtime", data, ex=5)

# Template library (1-hour cache)
redis.set("element_library", library_data, ex=3600)
```

### Async Operations

```python
# ✅ GOOD: Async for I/O
async def create_order(data):
    # Stripe API call
    payment = await stripe.PaymentIntent.create_async(...)
    # Database insert
    order = await OrderModel.create(**data)
    return order

# ❌ BAD: Blocking calls
def create_order(data):
    payment = stripe.PaymentIntent.create(...)  # Blocks!
    order = OrderModel.create(**data)
    return order
```

---

## Troubleshooting

### Common Issues

**Migration fails:**
```bash
# Check database connection
psql $DATABASE_URL -c "SELECT 1"

# Drop and recreate
alembic downgrade base
alembic upgrade head
```

**Tests failing:**
```bash
# Check test database
pytest tests/ --create-db

# Increase timeout
pytest tests/ --asyncio-mode=auto -v
```

**API not responding:**
```bash
# Check logs
uvicorn src.main:app --log-level debug

# Verify imports
python -c "from src.main import app; print(app)"
```

---

## Support

For issues or questions:
1. Check API docs: http://localhost:8000/docs
2. Review SPEC documents: `.moai/specs/SPEC-FUN-*/`
3. Check implementation report: `FUNNELS_BACKEND_IMPLEMENTATION_REPORT.md`

---

**Last Updated:** 2026-02-07
**Status:** ✅ Complete - Production Ready
