# SPEC-CRM-002: Pipelines & Deals

## Overview

Implement sales pipeline and deal/opportunity management system with customizable pipelines, stage tracking, deal value forecasting, and deal movement workflows.

## Requirements (EARS Format)

### 1. Pipeline CRUD Operations

**WHEN** an authenticated user creates a pipeline, **THE SYSTEM** shall store pipeline with name, account association, and ordered stages.

**WHEN** creating a pipeline, **THE SYSTEM** shall require at least one stage with default probabilities.

**WHEN** updating a pipeline, **THE SYSTEM** shall allow name changes and stage modifications.

**THE SYSTEM** shall enforce unique pipeline names per account.

### 2. Pipeline Stage Management

**WHEN** defining pipeline stages, **THE SYSTEM** shall support stage name, order (integer), probability (0-100%), and optional display color.

**THE SYSTEM** shall ensure stage orders are unique within pipeline.

**THE SYSTEM** shall validate probability range (0-100).

**WHEN** a stage is deleted, **THE SYSTEM** shall reassign deals in that stage to a default stage or prevent deletion.

### 3. Deal/Opportunity CRUD

**WHEN** creating a deal, **THE SYSTEM** shall require pipeline_id, stage_id, name, and value (float converted to integer cents).

**THE SYSTEM** shall associate deals with optional contact and company.

**THE SYSTEM** shall track deal status (open, won, lost, abandoned) with timestamps.

**THE SYSTEM** shall store expected_close_date and actual_close_date.

### 4. Deal Stage Movement

**WHEN** a deal moves between stages, **THE SYSTEM** shall update stage_id and optionally override probability.

**THE SYSTEM** shall validate stage belongs to same pipeline.

**THE SYSTEM** shall prevent stage movement for won/lost/abandoned deals.

**THE SYSTEM** shall log stage change history for audit trail.

### 5. Deal Status Transitions

**WHEN** a deal is marked as won, **THE SYSTEM** shall set status to WON, probability to 100, and record actual_close_date.

**WHEN** a deal is marked as lost, **THE SYSTEM** shall set status to LOST, probability to 0, and record actual_close_date with optional reason.

**WHEN** a deal is abandoned, **THE SYSTEM** shall set status to ABANDONED (no longer pursuing).

**THE SYSTEM** shall prevent status changes on already won/lost deals.

### 6. Deal Forecasting

**WHEN** generating deal forecast, **THE SYSTEM** shall calculate total value, weighted value (sum of value * probability), won value, and lost value.

**THE SYSTEM** shall count open deals, won deals, and lost deals.

**THE SYSTEM** shall support filtering forecast by pipeline and date range.

**THE SYSTEM** shall return forecast summary metrics for reporting.

## API Endpoints

### POST /api/v1/crm/pipelines
Create a new pipeline.

**Request:**
```json
{
  "name": "Sales Pipeline",
  "stages": [
    {
      "name": "Prospect",
      "order": 1,
      "probability": 10,
      "display_color": "#FF5733"
    },
    {
      "name": "Qualification",
      "order": 2,
      "probability": 30,
      "display_color": "#FFC300"
    },
    {
      "name": "Proposal",
      "order": 3,
      "probability": 60,
      "display_color": "#DAF7A6"
    },
    {
      "name": "Negotiation",
      "order": 4,
      "probability": 80,
      "display_color": "#C70039"
    },
    {
      "name": "Closed Won",
      "order": 5,
      "probability": 100,
      "display_color": "#900C3F"
    }
  ]
}
```

**Response:** 201 Created
```json
{
  "id": "uuid",
  "account_id": "uuid",
  "name": "Sales Pipeline",
  "is_active": true,
  "stages": [...],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### GET /api/v1/crm/pipelines/{pipeline_id}
Get pipeline with stages.

### GET /api/v1/crm/pipelines
List all pipelines for account.

### POST /api/v1/crm/deals
Create a new deal.

**Request:**
```json
{
  "pipeline_id": "uuid",
  "stage_id": "uuid",
  "name": "Enterprise Software License",
  "value": 50000.00,
  "contact_id": "uuid",
  "company_id": "uuid",
  "expected_close_date": "2024-03-31T00:00:00Z",
  "probability": 60,
  "notes": "Decision maker: CTO John Smith"
}
```

**Response:** 201 Created
```json
{
  "id": "uuid",
  "account_id": "uuid",
  "pipeline_id": "uuid",
  "stage_id": "uuid",
  "name": "Enterprise Software License",
  "value_amount": 5000000,
  "value_currency": "USD",
  "contact_id": "uuid",
  "company_id": "uuid",
  "status": "open",
  "expected_close_date": "2024-03-31T00:00:00Z",
  "actual_close_date": null,
  "probability": 60,
  "notes": "Decision maker: CTO John Smith",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "created_by": "uuid"
}
```

### PATCH /api/v1/crm/deals/{deal_id}
Update deal details.

**Request:**
```json
{
  "name": "Enterprise Software License (Renewal)",
  "value": 55000.00,
  "stage_id": "uuid",
  "expected_close_date": "2024-04-15T00:00:00Z",
  "probability": 75,
  "notes": "Increased scope, updated pricing"
}
```

### POST /api/v1/crm/deals/{deal_id}/move
Move deal to new stage.

**Query Parameters:**
- stage_id: UUID (required)
- probability: int 0-100 (optional override)

**Response:** 200 OK with updated deal

### POST /api/v1/crm/deals/{deal_id}/win
Mark deal as won.

**Response:** 200 OK with status=WON, probability=100, actual_close_date set

### POST /api/v1/crm/deals/{deal_id}/lose
Mark deal as lost.

**Response:** 200 OK with status=LOST, probability=0, actual_close_date set

### GET /api/v1/crm/deals/forecast
Get deal forecast summary.

**Query Parameters:**
- pipeline_id: UUID (optional filter)

**Response:** 200 OK
```json
{
  "total_value": 525000.00,
  "weighted_value": 278500.00,
  "won_value": 125000.00,
  "lost_value": 45000.00,
  "open_deals": 15,
  "won_deals": 5,
  "lost_deals": 3
}
```

## Database Schema

### crm_pipelines table

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| account_id | UUID | FK, NOT NULL, indexed |
| name | VARCHAR(100) | NOT NULL, unique per account |
| is_active | BOOLEAN | default true |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

### crm_pipeline_stages table

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| pipeline_id | UUID | FK, NOT NULL, indexed |
| name | VARCHAR(100) | NOT NULL |
| order | INTEGER | NOT NULL, unique per pipeline |
| probability | INTEGER | NOT NULL, 0-100 |
| display_color | VARCHAR(7) | nullable (hex) |

**Indexes:**
- uq_crm_stage_pipeline_order (pipeline_id, order)
- ck_stage_probability (CHECK probability >= 0 AND probability <= 100)

### crm_deals table

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| account_id | UUID | FK, NOT NULL, indexed |
| pipeline_id | UUID | FK, NOT NULL, indexed |
| stage_id | UUID | FK, NOT NULL, indexed |
| name | VARCHAR(255) | NOT NULL |
| value_amount | INTEGER | NOT NULL (cents) |
| value_currency | VARCHAR(3) | NOT NULL, default "USD" |
| contact_id | UUID | FK to crm_contacts |
| company_id | UUID | FK to crm_companies |
| status | ENUM | NOT NULL, default "open" |
| expected_close_date | TIMESTAMPTZ | nullable |
| actual_close_date | TIMESTAMPTZ | nullable |
| probability | INTEGER | NOT NULL, default 50, 0-100 |
| notes | TEXT | nullable |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |
| created_by | UUID | FK to users |

**Indexes:**
- ck_deal_probability (CHECK probability >= 0 AND probability <= 100)
- ck_deal_value (CHECK value_amount >= 0)
- ix_crm_deals_status
- ix_crm_deals_pipeline_stage (pipeline_id, stage_id)

## Acceptance Criteria

**AC1:** User can create pipeline with custom name and stages.

**AC2:** Pipeline stages have unique orders and valid probabilities (0-100).

**AC3:** Deal creation requires pipeline_id, stage_id, name, and value.

**AC4:** Deal value is stored as integer cents for precision (50000.00 -> 5000000).

**AC5:** Moving deal between stages updates stage_id and optionally probability.

**AC6:** Won deals cannot be moved or status-changed (immutable).

**AC7:** Lost deals record actual_close_date and set probability to 0.

**AC8:** Forecast calculates weighted value (sum of value * probability / 100).

**AC9:** Filter deals by pipeline, stage, status, contact, company.

**AC10:** Account isolation enforced in all pipeline and deal queries.

## Testing Strategy

**Unit Tests:**
- Deal entity creation and validation
- Money value object decimal/cents conversion
- Stage transition validation

**Integration Tests:**
- Pipeline and deal CRUD with database
- Deal stage movement with history tracking
- Forecast calculation accuracy

**E2E Tests:**
- Create pipeline via API
- Create deal and move through stages
- Mark deal as won/lost
- Generate forecast report

**Test Coverage Target:** 85%+

## Dependencies

**Dependencies:**
- SPEC-CRM-001 (Contacts - deals linked to contacts)
- SPEC-CRM-003 (Companies - deals linked to companies)

**Dependent Modules:**
- SPEC-CRM-004 (Activities/Tasks - activities linked to deals)
- SPEC-CRM-005 (Notes - notes linked to deals)

## Technical Notes

**Performance Considerations:**
- Index (pipeline_id, stage_id) for deal filtering
- Cache forecast calculations for 5 minutes
- Use database aggregation for forecast queries

**Business Logic:**
- Weighted value formula: SUM(value_amount * probability / 100.0)
- Default probability from stage when deal created
- Prevent closing deals in first stage (validation rule)

**Future Enhancements:**
- Deal split/merge functionality
- Stage duration analytics
- AI-powered win probability prediction
- Competitor tracking on deals
