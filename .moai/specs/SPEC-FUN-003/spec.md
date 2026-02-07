# SPEC-FUN-003: Orders & Payments - Payment Processing Backend

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-FUN-003 |
| **Title** | Orders & Payments - Payment Processing Backend |
| **Module** | funnels-orders |
| **Domain** | payment-processing |
| **Priority** | Critical |
| **Status** | Planned |
| **Created** | 2026-02-07 |
| **Version** | 1.0.0 |

---

## Overview

This specification defines the backend system for order management and payment processing, including Stripe integration, order bumps, upsells/downsells, and revenue tracking for funnels.

**Scope:** Complete backend API for order lifecycle management with payment gateway integration.

**Target Users:** Businesses selling products/services through funnels.

---

## Environment

### Technical Environment

**Backend Framework:**
- FastAPI 0.115+ with Python 3.13+
- Async operations for payment processing

**Payment Gateway:**
- Stripe API (latest)
- Webhook handling for payment events

**Database:**
- PostgreSQL 16+ with transaction-safe operations
- Financial data integrity

**Security:**
- PCI compliance via Stripe
- Encrypted sensitive data

---

## Assumptions

**Assumption 1:** Stripe API keys configured in environment variables.

**Confidence Level:** High

**Evidence Basis:** Standard practice for payment processing.

**Risk if Wrong:** All payment operations fail.

**Validation Method:** Verify Stripe connectivity on startup.

**Assumption 2:** Webhooks from Stripe delivered with signature verification.

**Confidence Level:** High

**Evidence Basis:** Stripe signs all webhook payloads.

**Risk if Wrong:** Fraudulent webhook events processed.

**Validation Method:** Verify webhook signature on every request.

**Assumption 3:** Order amounts stored in cents (integer) to avoid floating point issues.

**Confidence Level:** High

**Evidence Basis:** Financial industry standard.

**Risk if Wrong:** Rounding errors in calculations.

**Validation Method:** All amount fields validated as integers.

---

## EARS Requirements

### REQ-FUN-003-01: Create Order (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/orders with payment details,
**THEN** the system shall create order and process payment via Stripe,
**RESULTING IN** 201 status with order object,
**IN STATE** payment_processed.

**Request Body:**
```json
{
  "funnel_id": "uuid",
  "funnel_step_id": "uuid",
  "contact_id": "uuid (required if not guest)",
  "customer": {
    "email": "string (required)",
    "name": "string",
    "phone": "string"
  },
  "billing_address": {
    "line1": "string",
    "line2": "string",
    "city": "string",
    "state": "string",
    "postal_code": "string",
    "country": "string (ISO 3166-1 alpha-2)"
  },
  "shipping_address": "object (same structure as billing)",
  "items": [
    {
      "product_id": "uuid",
      "product_name": "string",
      "quantity": "integer",
      "unit_price_cents": "integer",
      "tax_cents": "integer",
      "discount_cents": "integer (optional)"
    }
  ],
  "order_bumps": [
    {
      "product_id": "uuid",
      "quantity": "integer",
      "unit_price_cents": "integer"
    }
  ],
  "payment_method": "stripe",
  "payment_token": "string (Stripe payment intent ID)",
  "currency": "string (default: usd)",
  "subtotal_cents": "integer",
  "tax_cents": "integer",
  "shipping_cents": "integer (optional)",
  "discount_cents": "integer (optional)",
  "total_cents": "integer"
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "account_id": "uuid",
  "funnel_id": "uuid",
  "funnel_step_id": "uuid",
  "contact_id": "uuid or null",
  "order_number": "string (unique, e.g., ORD-2025-000001)",
  "customer": "object",
  "billing_address": "object",
  "shipping_address": "object or null",
  "items": ["array"],
  "order_bumps": ["array"],
  "payment": {
    "status": "pending | paid | failed | refunded | partially_refunded",
    "payment_method": "stripe",
    "stripe_payment_intent_id": "string",
    "paid_at": "ISO8601 or null",
    "failure_reason": "string or null"
  },
  "currency": "string",
  "subtotal_cents": "integer",
  "tax_cents": "integer",
  "shipping_cents": "integer",
  "discount_cents": "integer",
  "total_cents": "integer",
  "status": "pending | processing | completed | cancelled | failed",
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

**Acceptance Criteria:**
- Order number auto-generated and unique
- Payment processed via Stripe
- Order status set based on payment
- Returns 400 if validation fails
- Returns 402 if payment fails

### REQ-FUN-003-02: List Orders (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/orders with filters,
**THEN** the system shall return paginated list of orders for the account,
**RESULTING IN** 200 status with orders array,
**IN STATE** retrieved.

**Query Parameters:**
- funnel_id: uuid (optional)
- status: string (optional)
- payment_status: string (optional)
- contact_id: uuid (optional)
- date_from: ISO8601 (optional)
- date_to: ISO8601 (optional)
- min_total_cents: integer (optional)
- page, page_size, search, sort_by, sort_order

**Response 200:**
```json
{
  "items": ["array of order objects"],
  "total": "integer",
  "page": "integer",
  "page_size": "integer",
  "total_pages": "integer",
  "summary": {
    "total_revenue_cents": "integer",
    "total_orders": "integer",
    "average_order_value_cents": "integer"
  }
}
```

**Acceptance Criteria:**
- Only returns orders for account's funnels
- Summary calculated for filtered results
- Dates filtered in UTC

### REQ-FUN-003-03: Get Order Detail (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/orders/{id},
**THEN** the system shall return complete order details with payment info,
**RESULTING IN** 200 status with full order object,
**IN STATE** retrieved.

**Response 200:**
Includes all fields from create response plus:
```json
{
  "upsells": ["array of accepted upsells"],
  "downsells": ["array of accepted downsells"],
  "refunds": [
    {
      "id": "uuid",
      "amount_cents": "integer",
      "reason": "string",
      "status": "pending | completed | failed",
      "created_at": "ISO8601"
    }
  ],
  "metadata": "object",
  "affiliate": {
    "id": "uuid",
    "name": "string",
    "commission_cents": "integer"
  }
}
```

**Acceptance Criteria:**
- Returns 404 if order not found
- Returns 403 if order belongs to different account
- Includes payment timeline

### REQ-FUN-003-04: Update Order Status (Event-Driven)

**WHEN** a user submits a PATCH request to /api/v1/orders/{id}/status,
**THEN** the system shall update order status and trigger workflow,
**RESULTING IN** 200 status with updated order object,
**IN STATE** status_updated.

**Request Body:**
```json
{
  "status": "processing | completed | cancelled | failed",
  "notes": "string (optional)"
}
```

**Acceptance Criteria:**
- Status change validated
- Triggers order status workflow events
- Returns 400 if invalid status transition
- Returns 404 if not found

### REQ-FUN-003-05: Process Upsell Offer (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/orders/{id}/upsells,
**THEN** the system shall process upsell payment for additional product,
**RESULTING IN** 201 status with upsell object,
**IN STATE** upsell_processed.

**Request Body:**
```json
{
  "upsell_id": "uuid (from funnel step config)",
  "product_id": "uuid",
  "quantity": "integer",
  "unit_price_cents": "integer",
  "payment_token": "string (Stripe payment intent ID)"
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "order_id": "uuid",
  "upsell_id": "uuid",
  "product_id": "uuid",
  "product_name": "string",
  "quantity": "integer",
  "unit_price_cents": "integer",
  "total_cents": "integer",
  "status": "accepted | rejected | failed",
  "created_at": "ISO8601"
}
```

**Acceptance Criteria:**
- Payment processed for upsell amount
- Upsell linked to original order
- Returns 404 if order not found
- Returns 400 if upsell not available

### REQ-FUN-003-06: Process Downsell Offer (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/orders/{id}/downsells,
**THEN** the system shall process downsell payment for lower-priced alternative,
**RESULTING IN** 201 status with downsell object,
**IN STATE** downsell_processed.

**Request Body:** Same as upsell

**Response:** Same structure as upsell

**Acceptance Criteria:**
- Typically offered after upsell rejection
- Lower price than original/upsell
- Payment processed via Stripe

### REQ-FUN-003-07: Add Order Bump (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/orders/{id}/bumps,
**THEN** the system shall add order bump to existing order (pre-shipment),
**RESULTING IN** 201 status with updated order object,
**IN STATE** bump_added.

**Request Body:**
```json
{
  "product_id": "uuid",
  "quantity": "integer",
  "payment_token": "string"
}
```

**Acceptance Criteria:**
- Only allowed for orders not yet shipped
- Payment processed for bump amount
- Order total updated
- Returns 400 if order already shipped
- Returns 404 if bump not available

### REQ-FUN-003-08: Process Refund (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/orders/{id}/refunds,
**THEN** the system shall process refund via Stripe,
**RESULTING IN** 201 status with refund object,
**IN STATE** refund_processed.

**Request Body:**
```json
{
  "amount_cents": "integer (optional, default: full refund)",
  "reason": "string (required)",
  "refund_type": "full | partial"
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "order_id": "uuid",
  "amount_cents": "integer",
  "reason": "string",
  "status": "pending | completed | failed",
  "stripe_refund_id": "string",
  "created_at": "ISO8601",
  "completed_at": "ISO8601 or null"
}
```

**Acceptance Criteria:**
- Refund processed via Stripe API
- Order status updated to refunded
- Cannot exceed original payment amount
- Returns 400 if refund amount invalid
- Returns 403 if payment not successful

### REQ-FUN-003-09: Get Order Analytics (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/orders/analytics,
**THEN** the system shall return aggregated order statistics,
**RESULTING IN** 200 status with analytics object,
**IN STATE** analytics_retrieved.

**Query Parameters:**
- funnel_id: uuid (optional)
- date_from: ISO8601 (optional)
- date_to: ISO8601 (optional)
- granularity: string (default: day, options: hour, day, week, month)

**Response 200:**
```json
{
  "summary": {
    "total_orders": "integer",
    "total_revenue_cents": "integer",
    "average_order_value_cents": "integer",
    "conversion_rate": "decimal",
    "refund_rate": "decimal"
  },
  "by_funnel": [
    {
      "funnel_id": "uuid",
      "funnel_name": "string",
      "orders": "integer",
      "revenue_cents": "integer"
    }
  ],
  "over_time": [
    {
      "date": "ISO8601",
      "orders": "integer",
      "revenue_cents": "integer"
    }
  ],
  "top_products": [
    {
      "product_id": "uuid",
      "product_name": "string",
      "units_sold": "integer",
      "revenue_cents": "integer"
    }
  ],
  "order_bump_stats": {
    "total_offers": "integer",
    "accepted": "integer",
    "revenue_cents": "integer",
    "acceptance_rate": "decimal"
  },
  "upsell_stats": {
    "total_offers": "integer",
    "accepted": "integer",
    "revenue_cents": "integer",
    "acceptance_rate": "decimal"
  }
}
```

**Acceptance Criteria:**
- Data filtered by account
- Date ranges inclusive
- Granularity affects time grouping

### REQ-FUN-003-10: Handle Stripe Webhook (Event-Driven)

**WHEN** Stripe sends a POST request to /api/v1/webhooks/stripe,
**THEN** the system shall process webhook event and update order,
**RESULTING IN** 200 status,
**IN STATE** webhook_processed.

**Request:** Stripe webhook payload with signature in headers

**Event Types Handled:**
- payment_intent.succeeded
- payment_intent.payment_failed
- payment_intent.amount_capturable_updated
- charge.refunded
- charge.refund.updated
- charge.dispute.created

**Acceptance Criteria:**
- Webhook signature verified
- Event idempotent (duplicate events ignored)
- Order status updated based on event
- Returns 401 if signature invalid
- Returns 400 if event type unsupported

### REQ-FUN-003-11: Export Orders (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/orders/export,
**THEN** the system shall generate CSV file with filtered orders,
**RESULTING IN** 200 status with CSV file,
**IN STATE** exported.

**Request Body:**
```json
{
  "filters": "object (same as list endpoint filters)",
  "columns": ["array of field names to include"],
  "format": "csv (default) | xlsx"
}
```

**Response 200:**
Content-Type: text/csv or application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Body: File download

**Acceptance Criteria:**
- Background job for large exports (>1000 orders)
- Email notification when ready
- Returns 202 for background job
- Returns 200 with file for small exports

### REQ-FUN-003-12: Create Payment Intent (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/orders/payment-intent,
**THEN** the system shall create Stripe PaymentIntent and return client secret,
**RESULTING IN** 201 status with payment intent object,
**IN STATE** payment_intent_created.

**Request Body:**
```json
{
  "amount_cents": "integer",
  "currency": "string (default: usd)",
  "metadata": "object (optional)"
}
```

**Response 201:**
```json
{
  "payment_intent_id": "string",
  "client_secret": "string",
  "amount_cents": "integer",
  "currency": "string",
  "status": "string"
}
```

**Acceptance Criteria:**
- PaymentIntent created via Stripe API
- Client secret returned for frontend use
- Metadata stored for webhook reconciliation

---

## Technical Specifications

### Database Schema

```sql
-- Orders table
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id),
    funnel_id UUID NOT NULL REFERENCES funnels(id),
    funnel_step_id UUID NOT NULL REFERENCES funnel_steps(id),
    contact_id UUID REFERENCES contacts(id) ON DELETE SET NULL,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    customer_email VARCHAR(255) NOT NULL,
    customer_name VARCHAR(255),
    customer_phone VARCHAR(50),
    billing_address JSONB NOT NULL,
    shipping_address JSONB,
    currency VARCHAR(3) NOT NULL DEFAULT 'usd',
    subtotal_cents INTEGER NOT NULL,
    tax_cents INTEGER NOT NULL DEFAULT 0,
    shipping_cents INTEGER DEFAULT 0,
    discount_cents INTEGER DEFAULT 0,
    total_cents INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    payment_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    payment_method VARCHAR(20) NOT NULL,
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    paid_at TIMESTAMPTZ,
    failure_reason TEXT,
    metadata JSONB DEFAULT '{}',
    affiliate_id UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_orders_account_id ON orders(account_id);
CREATE INDEX idx_orders_funnel_id ON orders(funnel_id);
CREATE INDEX idx_orders_contact_id ON orders(contact_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_payment_status ON orders(payment_status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_order_number ON orders(order_number);

-- Order items table
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id),
    product_name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price_cents INTEGER NOT NULL,
    tax_cents INTEGER NOT NULL DEFAULT 0,
    discount_cents INTEGER DEFAULT 0,
    total_cents INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

-- Order bumps table
CREATE TABLE order_bumps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id),
    product_name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price_cents INTEGER NOT NULL,
    total_cents INTEGER NOT NULL,
    accepted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_order_bumps_order_id ON order_bumps(order_id);

-- Upsells/Downsells table
CREATE TABLE order_upsells (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    funnel_step_id UUID NOT NULL REFERENCES funnel_steps(id),
    offer_type VARCHAR(10) NOT NULL,
    product_id UUID NOT NULL REFERENCES products(id),
    product_name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price_cents INTEGER NOT NULL,
    total_cents INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'accepted',
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    responded_at TIMESTAMPTZ
);

CREATE INDEX idx_order_upsells_order_id ON order_upsells(order_id);

-- Refunds table
CREATE TABLE refunds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    amount_cents INTEGER NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    stripe_refund_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_refunds_order_id ON refunds(order_id);
CREATE INDEX idx_refunds_status ON refunds(status);
```

### API Endpoints Summary

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/orders | Create order & process payment |
| GET | /api/v1/orders | List orders (paginated) |
| GET | /api/v1/orders/{id} | Get order detail |
| PATCH | /api/v1/orders/{id}/status | Update order status |
| POST | /api/v1/orders/{id}/upsells | Process upsell |
| POST | /api/v1/orders/{id}/downsells | Process downsell |
| POST | /api/v1/orders/{id}/bumps | Add order bump |
| POST | /api/v1/orders/{id}/refunds | Process refund |
| GET | /api/v1/orders/analytics | Get order analytics |
| POST | /api/v1/webhooks/stripe | Handle Stripe webhook |
| POST | /api/v1/orders/export | Export orders |
| POST | /api/v1/orders/payment-intent | Create PaymentIntent |

**Total Endpoints: 12**

---

## Constraints

### Technical Constraints

- All amounts in cents (integer)
- Payment processing via Stripe only
- Webhook signature verification required
- Idempotent operations for retries

### Business Constraints

- Maximum refund: original payment amount
- Order bumps: only before shipping
- Upsells: only for completed orders
- Refund window: 30 days (configurable)

### Financial Constraints

- Minimum order amount: 50 cents
- Maximum order amount: $999,999.99
- Precision: 2 decimal places (cents)

---

## Dependencies

### Internal Dependencies

| Module | Dependency Type | Description |
|--------|-----------------|-------------|
| Funnels Module | Hard | Orders belong to funnels |
| Contacts Module | Soft | Link orders to contacts |
| Products Module | Hard | Order items reference products |
| Users Module | Soft | Affiliate tracking |

### External Dependencies

| Service | Purpose |
|---------|---------|
| Stripe API | Payment processing |
| Stripe Webhooks | Payment events |

---

## Related SPECs

| SPEC ID | Title | Relationship |
|---------|-------|--------------|
| SPEC-FUN-001 | Funnel Builder | Order steps in funnels |
| SPEC-FUN-002 | Pages & Elements | Checkout page forms |
| SPEC-FUN-004 | Funnel Analytics | Revenue metrics |

---

## Traceability Tags

- TAG:SPEC-FUN-003
- TAG:MODULE-FUNNELS-ORDERS
- TAG:DOMAIN-PAYMENT-PROCESSING
- TAG:PRIORITY-CRITICAL
- TAG:API-REST
- TAG:STRIPE-INTEGRATION
- TAG:DDD-IMPLEMENTATION
