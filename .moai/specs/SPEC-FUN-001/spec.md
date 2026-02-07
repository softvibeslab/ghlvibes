# SPEC-FUN-001: Funnel Builder - Core Backend System

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-FUN-001 |
| **Title** | Funnel Builder - Core Backend System |
| **Module** | funnels |
| **Domain** | marketing-automation |
| **Priority** | Critical |
| **Status** | Planned |
| **Created** | 2026-02-07 |
| **Version** | 1.0.0 |

---

## Overview

This specification defines the core backend system for the Funnel Builder module, enabling users to create, manage, and clone marketing funnels with visual step management including pages, upsells, order bumps, and version control.

**Scope:** Complete backend API for funnel lifecycle management with template system and versioning.

**Target Users:** Marketing agencies, SMBs, and SaaS businesses requiring sales funnel automation.

---

## Environment

### Technical Environment

**Backend Framework:**
- FastAPI 0.115+ with Python 3.13+
- Async/await patterns throughout
- Pydantic v2.9 for validation

**Database:**
- PostgreSQL 16+ with SQLAlchemy 2.0 async
- Alembic for migrations
- Connection pooling (10-20 connections)

**Authentication:**
- JWT with account_id for multi-tenancy
- Role-based access control (RBAC)

**Documentation:**
- OpenAPI 3.1 specification
- Auto-generated via FastAPI

**Testing:**
- pytest with pytest-asyncio
- 85%+ coverage target

---

## Assumptions

### Backend Assumptions

**Assumption 1:** PostgreSQL database is available with proper connection string configured.

**Confidence Level:** High

**Evidence Basis:** Project has existing PostgreSQL for workflows module.

**Risk if Wrong:** Database connection failures prevent all operations.

**Validation Method:** Test database connectivity on startup.

**Assumption 2:** JWT authentication middleware provides account_id from token claims.

**Confidence Level:** High

**Evidence Basis:** Existing workflows module uses JWT with account_id.

**Risk if Wrong:** Multi-tenancy isolation fails causing data access violations.

**Validation Method:** Verify JWT claims include account_id in all API calls.

**Assumption 3:** Funnel storage requirements up to 100MB per funnel (JSON configurations).

**Confidence Level:** High

**Evidence Basis:** Typical funnel configurations are text-based and lightweight.

**Risk if Wrong:** Database bloat if funnels include large embedded assets.

**Validation Method:** Monitor average funnel size in production.

---

## EARS Requirements

### REQ-FUN-001-01: Create Funnel (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/funnels with valid funnel data,
**THEN** the system shall create a new funnel with unique ID,
**RESULTING IN** 201 status with funnel object in response,
**IN STATE** created.

**Request Body:**
```json
{
  "name": "string (3-100 chars)",
  "description": "string (optional, max 1000 chars)",
  "funnel_type": "lead_generation | sales | webinar | booking",
  "status": "draft | active | archived",
  "template_id": "uuid (optional)",
  "steps": [
    {
      "step_type": "page | upsell | downsell | order_bump | thank_you",
      "name": "string",
      "order": "integer",
      "page_id": "uuid (for page steps)",
      "config": "object"
    }
  ]
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "account_id": "uuid",
  "name": "string",
  "description": "string",
  "funnel_type": "string",
  "status": "string",
  "version": "integer",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "created_by": "uuid",
  "steps": ["array of step objects"]
}
```

**Acceptance Criteria:**
- Funnel ID is valid UUID v4
- Account ID extracted from JWT token
- Funnel name unique within account
- Version starts at 1
- Steps ordered by order field
- Created_at and updated_at set to current timestamp
- Returns 400 if validation fails
- Returns 409 if name already exists

### REQ-FUN-001-02: List Funnels (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/funnels with optional filters,
**THEN** the system shall return paginated list of funnels for the account,
**RESULTING IN** 200 status with funnel array and pagination metadata,
**IN STATE** retrieved.

**Query Parameters:**
- page: integer (default: 1, min: 1)
- page_size: integer (default: 20, min: 1, max: 100)
- status: string (optional, filter by status)
- funnel_type: string (optional, filter by type)
- search: string (optional, search in name/description)
- sort_by: string (default: created_at, options: name, created_at, updated_at)
- sort_order: string (default: desc, options: asc, desc)

**Response 200:**
```json
{
  "items": ["array of funnel objects"],
  "total": "integer",
  "page": "integer",
  "page_size": "integer",
  "total_pages": "integer"
}
```

**Acceptance Criteria:**
- Only returns funnels for account_id from JWT
- Filters applied server-side
- Pagination metadata accurate
- Returns 400 for invalid query parameters
- Returns 401 if authentication fails

### REQ-FUN-001-03: Get Funnel Detail (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/funnels/{id},
**THEN** the system shall return complete funnel details including all steps,
**RESULTING IN** 200 status with full funnel object,
**IN STATE** retrieved.

**Response 200:**
```json
{
  "id": "uuid",
  "account_id": "uuid",
  "name": "string",
  "description": "string",
  "funnel_type": "string",
  "status": "string",
  "version": "integer",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "created_by": "uuid",
  "updated_by": "uuid",
  "steps": [
    {
      "id": "uuid",
      "step_type": "string",
      "name": "string",
      "order": "integer",
      "page_id": "uuid or null",
      "config": "object",
      "created_at": "ISO8601"
    }
  ],
  "stats": {
    "total_visits": "integer",
    "conversions": "integer",
    "revenue": "decimal"
  }
}
```

**Acceptance Criteria:**
- Returns 404 if funnel not found
- Returns 403 if funnel belongs to different account
- Includes all steps with page details
- Includes basic stats

### REQ-FUN-001-04: Update Funnel (Event-Driven)

**WHEN** a user submits a PATCH request to /api/v1/funnels/{id} with partial data,
**THEN** the system shall update specified fields and increment version,
**RESULTING IN** 200 status with updated funnel object,
**IN STATE** updated.

**Request Body (all fields optional):**
```json
{
  "name": "string",
  "description": "string",
  "status": "string",
  "steps": ["array of step objects"]
}
```

**Acceptance Criteria:**
- Version incremented automatically
- Updated_at set to current timestamp
- Updated_by set to current user
- Steps can be fully replaced
- Returns 404 if funnel not found
- Returns 403 if different account
- Returns 400 if validation fails

### REQ-FUN-001-05: Delete Funnel (Event-Driven)

**WHEN** a user submits a DELETE request to /api/v1/funnels/{id},
**THEN** the system shall soft delete the funnel (set deleted_at),
**RESULTING IN** 204 status with no body,
**IN STATE** deleted.

**Acceptance Criteria:**
- Soft delete (set deleted_at, not hard delete)
- Returns 404 if funnel not found
- Returns 403 if different account
- Returns 204 on success
- Cascade soft delete to steps

### REQ-FUN-001-06: Clone Funnel (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/funnels/{id}/clone,
**THEN** the system shall create a copy with new ID and "- Copy" suffix,
**RESULTING IN** 201 status with cloned funnel object,
**IN STATE** cloned.

**Request Body:**
```json
{
  "name": "string (optional, defaults to 'Original Name - Copy')"
}
```

**Acceptance Criteria:**
- New funnel with new UUID
- Name suffixed with "- Copy" unless provided
- All steps cloned with new IDs
- Version reset to 1
- Created_by set to current user
- Returns 404 if original not found
- Returns 403 if different account

### REQ-FUN-001-07: Add Step to Funnel (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/funnels/{id}/steps,
**THEN** the system shall add a new step to the funnel,
**RESULTING IN** 201 status with created step object,
**IN STATE** step_added.

**Request Body:**
```json
{
  "step_type": "page | upsell | downsell | order_bump | thank_you",
  "name": "string (3-100 chars)",
  "order": "integer",
  "page_id": "uuid (required for page steps)",
  "config": "object (optional)"
}
```

**Acceptance Criteria:**
- Step ID is new UUID
- Funnel updated_at timestamp updated
- Funnel version incremented
- Order unique within funnel
- Returns 400 if step_type invalid
- Returns 400 if page_id missing for page step
- Returns 404 if funnel not found

### REQ-FUN-001-08: Update Funnel Step (Event-Driven)

**WHEN** a user submits a PATCH request to /api/v1/funnels/{id}/steps/{step_id},
**THEN** the system shall update the step and increment funnel version,
**RESULTING IN** 200 status with updated step object,
**IN STATE** step_updated.

**Request Body (partial):**
```json
{
  "name": "string",
  "order": "integer",
  "config": "object"
}
```

**Acceptance Criteria:**
- Funnel version incremented
- Funnel updated_at set to now
- Returns 404 if step not found
- Returns 403 if different account

### REQ-FUN-001-09: Delete Step from Funnel (Event-Driven)

**WHEN** a user submits a DELETE request to /api/v1/funnels/{id}/steps/{step_id},
**THEN** the system shall remove the step and reorder remaining steps,
**RESULTING IN** 204 status with no body,
**IN STATE** step_deleted.

**Acceptance Criteria:**
- Step hard deleted from database
- Remaining steps reordered (order field updated)
- Funnel version incremented
- Returns 404 if step not found
- Returns 403 if different account
- Returns 204 on success

### REQ-FUN-001-10: Reorder Funnel Steps (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/funnels/{id}/steps/reorder,
**THEN** the system shall reorder all steps according to provided order,
**RESULTING IN** 200 status with updated steps array,
**IN STATE** steps_reordered.

**Request Body:**
```json
{
  "step_orders": [
    {"step_id": "uuid", "order": "integer"},
    {"step_id": "uuid", "order": "integer"}
  ]
}
```

**Acceptance Criteria:**
- All steps updated atomically
- Funnel version incremented
- Order values sequential starting from 1
- Returns 400 if duplicate orders
- Returns 404 if any step not found
- Returns 403 if different account

### REQ-FUN-001-11: List Funnel Templates (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/funnels/templates,
**THEN** the system shall return list of available funnel templates,
**RESULTING IN** 200 status with templates array,
**IN STATE** templates_retrieved.

**Query Parameters:**
- category: string (optional)
- funnel_type: string (optional)

**Response 200:**
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "string",
      "description": "string",
      "category": "string",
      "funnel_type": "string",
      "preview_image_url": "string",
      "use_count": "integer",
      "steps": ["array of step definitions"]
    }
  ]
}
```

**Acceptance Criteria:**
- Returns system-defined templates
- Templates include step structure
- use_count reflects how many times used

### REQ-FUN-001-12: Create Funnel from Template (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/funnels/templates/{template_id}/instantiate,
**THEN** the system shall create a new funnel from template structure,
**RESULTING IN** 201 status with created funnel object,
**IN STATE** funnel_created_from_template.

**Request Body:**
```json
{
  "name": "string (3-100 chars, required)"
}
```

**Acceptance Criteria:**
- New funnel created with template steps
- Template use_count incremented
- Pages created as copies (not references)
- Returns 404 if template not found
- Returns 400 if name invalid

### REQ-FUN-001-13: Get Funnel Versions (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/funnels/{id}/versions,
**THEN** the system shall return list of all versions for the funnel,
**RESULTING IN** 200 status with versions array,
**IN STATE** versions_retrieved.

**Response 200:**
```json
{
  "items": [
    {
      "version": "integer",
      "created_at": "ISO8601",
      "created_by": "uuid",
      "change_description": "string"
    }
  ]
}
```

**Acceptance Criteria:**
- Ordered by version descending
- Shows all version changes
- Returns 404 if funnel not found

### REQ-FUN-001-14: Restore Funnel Version (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/funnels/{id}/versions/{version}/restore,
**THEN** the system shall restore funnel to specified version,
**RESULTING IN** 200 status with restored funnel object,
**IN STATE** version_restored.

**Acceptance Criteria:**
- Creates new version with restored state
- Original version preserved
- Returns 404 if version not found
- Returns 403 if different account
- Returns 400 if funnel is active

---

## Technical Specifications

### Database Schema

**Tables:**

```sql
-- Funnels table
CREATE TABLE funnels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    funnel_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    deleted_at TIMESTAMPTZ,
    CONSTRAINT funnels_account_name_unique UNIQUE (account_id, name, deleted_at)
);

CREATE INDEX idx_funnels_account_id ON funnels(account_id);
CREATE INDEX idx_funnels_status ON funnels(status);
CREATE INDEX idx_funnels_type ON funnels(funnel_type);
CREATE INDEX idx_funnels_deleted_at ON funnels(deleted_at);

-- Funnel steps table
CREATE TABLE funnel_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    funnel_id UUID NOT NULL REFERENCES funnels(id) ON DELETE CASCADE,
    step_type VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    "order" INTEGER NOT NULL,
    page_id UUID REFERENCES pages(id) ON DELETE SET NULL,
    config JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT funnel_steps_funnel_order_unique UNIQUE (funnel_id, "order")
);

CREATE INDEX idx_funnel_steps_funnel_id ON funnel_steps(funnel_id);
CREATE INDEX idx_funnel_steps_page_id ON funnel_steps(page_id);

-- Funnel templates table
CREATE TABLE funnel_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(50),
    funnel_type VARCHAR(50) NOT NULL,
    preview_image_url VARCHAR(500),
    template_data JSONB NOT NULL,
    use_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_system_template BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX idx_funnel_templates_category ON funnel_templates(category);
CREATE INDEX idx_funnel_templates_type ON funnel_templates(funnel_type);

-- Funnel version history table
CREATE TABLE funnel_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    funnel_id UUID NOT NULL REFERENCES funnels(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    funnel_snapshot JSONB NOT NULL,
    change_description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    CONSTRAINT funnel_versions_funnel_version_unique UNIQUE (funnel_id, version)
);

CREATE INDEX idx_funnel_versions_funnel_id ON funnel_versions(funnel_id);
```

### API Endpoints Summary

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/funnels | Create funnel |
| GET | /api/v1/funnels | List funnels (paginated) |
| GET | /api/v1/funnels/{id} | Get funnel detail |
| PATCH | /api/v1/funnels/{id} | Update funnel |
| DELETE | /api/v1/funnels/{id} | Delete funnel (soft) |
| POST | /api/v1/funnels/{id}/clone | Clone funnel |
| POST | /api/v1/funnels/{id}/steps | Add step |
| PATCH | /api/v1/funnels/{id}/steps/{step_id} | Update step |
| DELETE | /api/v1/funnels/{id}/steps/{step_id} | Delete step |
| POST | /api/v1/funnels/{id}/steps/reorder | Reorder steps |
| GET | /api/v1/funnels/templates | List templates |
| POST | /api/v1/funnels/templates/{template_id}/instantiate | Create from template |
| GET | /api/v1/funnels/{id}/versions | List versions |
| POST | /api/v1/funnels/{id}/versions/{version}/restore | Restore version |

**Total Endpoints: 14**

---

## Constraints

### Technical Constraints

- Must use FastAPI 0.115+ with async/await
- Must use PostgreSQL 16+ with SQLAlchemy 2.0 async
- Must implement soft delete for funnels
- Must implement version tracking
- Must validate with Pydantic v2.9

### Business Constraints

- Maximum 500 funnels per account
- Maximum 50 steps per funnel
- Funnel name: 3-100 characters
- Step name: 3-100 characters
- Version history limited to last 50 versions

### Performance Constraints

- List endpoint: < 500ms response time
- Get detail: < 200ms response time
- Create/update: < 1000ms response time
- Support 100 concurrent requests per account

---

## Dependencies

### Internal Dependencies

| Module | Dependency Type | Description |
|--------|-----------------|-------------|
| Pages Module | Hard | Steps reference pages |
| Accounts Module | Hard | Multi-tenancy account_id |
| Users Module | Hard | Created_by/updated_by references |

### External Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| FastAPI | 0.115+ | Web framework |
| SQLAlchemy | 2.0+ | ORM |
| Alembic | Latest | Migrations |
| Pydantic | 2.9+ | Validation |
| pytest | Latest | Testing |

---

## Related SPECs

| SPEC ID | Title | Relationship |
|---------|-------|--------------|
| SPEC-FUN-002 | Pages & Elements | Steps contain pages |
| SPEC-FUN-003 | Orders & Payments | Funnels process orders |
| SPEC-FUN-004 | Funnel Analytics | Track funnel performance |
| SPEC-FUN-005 | Integrations | External integrations |

---

## Traceability Tags

- TAG:SPEC-FUN-001
- TAG:MODULE-FUNNELS
- TAG:DOMAIN-MARKETING-AUTOMATION
- TAG:PRIORITY-CRITICAL
- TAG:API-REST
- TAG:DDD-IMPLEMENTATION
