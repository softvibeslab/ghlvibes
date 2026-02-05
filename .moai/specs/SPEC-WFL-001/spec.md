# SPEC-WFL-001: Create Workflow

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-001 |
| **Title** | Create Workflow |
| **Module** | workflows |
| **Domain** | automation |
| **Priority** | Critical |
| **Status** | Planned |
| **Created** | 2026-01-26 |
| **Version** | 1.0.0 |

---

## Overview

This specification defines the requirements for creating a new automation workflow within the GoHighLevel Clone platform. The workflow creation feature enables users to build visual automation sequences that respond to triggers and execute actions on contacts.

---

## EARS Requirements

### REQ-WFL-001-01: Workflow Creation (Event-Driven)

**WHEN** a user creates a new automation workflow,
**THEN** the system shall initialize workflow with trigger placeholder and blank canvas,
**RESULTING IN** a new workflow ready for configuration,
**IN STATE** draft.

### REQ-WFL-001-02: Workflow Naming (Ubiquitous)

The system shall **always** validate workflow names according to the following rules:
- Name must be between 3 and 100 characters
- Name must be unique within the account
- Name must not contain special characters except hyphens and underscores

### REQ-WFL-001-03: Workflow Initialization (Event-Driven)

**WHEN** a workflow is initialized,
**THEN** the system shall create a workflow record with:
- Unique UUID v4 identifier
- Creation timestamp in UTC
- Association with the current account/tenant
- Initial status set to `draft`
- Empty trigger configuration placeholder
- Empty actions array

### REQ-WFL-001-04: Default Configuration (State-Driven)

**IF** no description is provided during workflow creation,
**THEN** the system shall set description to an empty string.

**IF** no trigger_type is specified,
**THEN** the system shall leave trigger_type as null until configured.

### REQ-WFL-001-05: Audit Logging (Ubiquitous)

The system shall **always** log workflow creation events with:
- User ID who created the workflow
- Timestamp of creation
- Workflow ID created
- Initial configuration snapshot

### REQ-WFL-001-06: Authorization Check (Event-Driven)

**WHEN** a user attempts to create a workflow,
**THEN** the system shall verify the user has the `workflows:create` permission,
**RESULTING IN** either successful creation or 403 Forbidden response.

### REQ-WFL-001-07: Rate Limiting (Unwanted)

The system shall **not** allow more than 100 workflow creations per account per hour to prevent abuse.

### REQ-WFL-001-08: Tenant Isolation (Ubiquitous)

The system shall **always** associate workflows with the authenticated user's tenant (account_id) and enforce row-level security.

---

## Configuration Schema

### Workflow Entity

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | UUID | Yes | auto-generated | Unique workflow identifier |
| `account_id` | UUID | Yes | from auth | Tenant identifier |
| `name` | string | Yes | - | Workflow display name (3-100 chars) |
| `description` | string | No | "" | Optional description |
| `trigger_type` | string | No | null | Type of trigger (configured later) |
| `trigger_config` | JSONB | No | {} | Trigger-specific configuration |
| `status` | enum | Yes | draft | One of: draft, active, paused |
| `version` | integer | Yes | 1 | Workflow version number |
| `created_at` | timestamp | Yes | now() | Creation timestamp (UTC) |
| `updated_at` | timestamp | Yes | now() | Last modification timestamp |
| `created_by` | UUID | Yes | from auth | User who created the workflow |
| `updated_by` | UUID | Yes | from auth | User who last modified |

### Status Enum Values

| Value | Description |
|-------|-------------|
| `draft` | Workflow is being configured, not active |
| `active` | Workflow is live and processing triggers |
| `paused` | Workflow is temporarily disabled |

---

## API Specification

### Endpoint: Create Workflow

```
POST /api/v1/workflows
```

#### Request Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | Yes | Bearer token from Clerk |
| `Content-Type` | Yes | Must be `application/json` |
| `X-Account-ID` | No | Override account (admin only) |

#### Request Body

```json
{
  "name": "string (required, 3-100 chars)",
  "description": "string (optional)",
  "trigger_type": "string (optional, one of trigger types)",
  "trigger_config": "object (optional, trigger-specific config)"
}
```

#### Response: 201 Created

```json
{
  "id": "uuid",
  "account_id": "uuid",
  "name": "string",
  "description": "string",
  "trigger_type": "string | null",
  "trigger_config": {},
  "status": "draft",
  "version": 1,
  "created_at": "2026-01-26T10:00:00Z",
  "updated_at": "2026-01-26T10:00:00Z",
  "created_by": "uuid",
  "updated_by": "uuid",
  "actions": [],
  "stats": {
    "total_enrolled": 0,
    "currently_active": 0,
    "completed": 0
  }
}
```

#### Error Responses

| Status | Code | Description |
|--------|------|-------------|
| 400 | `VALIDATION_ERROR` | Invalid request body |
| 401 | `UNAUTHORIZED` | Missing or invalid auth token |
| 403 | `FORBIDDEN` | User lacks `workflows:create` permission |
| 409 | `CONFLICT` | Workflow name already exists in account |
| 429 | `RATE_LIMITED` | Exceeded creation rate limit |
| 500 | `INTERNAL_ERROR` | Server error |

---

## Database Schema

### Table: workflows

```sql
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT '',
    trigger_type VARCHAR(50),
    trigger_config JSONB DEFAULT '{}',
    status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'paused')),
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    updated_by UUID NOT NULL REFERENCES users(id),
    deleted_at TIMESTAMPTZ,

    CONSTRAINT workflows_name_account_unique UNIQUE (account_id, name) WHERE deleted_at IS NULL
);

-- Indexes
CREATE INDEX idx_workflows_account_id ON workflows(account_id);
CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflows_created_at ON workflows(created_at);
CREATE INDEX idx_workflows_trigger_type ON workflows(trigger_type) WHERE trigger_type IS NOT NULL;

-- Row Level Security
ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;

CREATE POLICY workflows_tenant_isolation ON workflows
    FOR ALL
    USING (account_id = current_setting('app.current_account_id')::uuid);

-- Audit trigger
CREATE TRIGGER workflows_updated_at
    BEFORE UPDATE ON workflows
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Table: workflow_audit_logs

```sql
CREATE TABLE workflow_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts(id),
    action VARCHAR(50) NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id),
    changes JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_workflow_audit_workflow_id ON workflow_audit_logs(workflow_id);
CREATE INDEX idx_workflow_audit_created_at ON workflow_audit_logs(created_at);
```

---

## Technical Approach

### Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   FastAPI    │────▶│  PostgreSQL  │
│  (Next.js)   │     │   Backend    │     │  (Supabase)  │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │    Redis     │
                     │ (Rate Limit) │
                     └──────────────┘
```

### Implementation Layers

1. **Presentation Layer (FastAPI Routes)**
   - Request validation with Pydantic
   - Authentication middleware (Clerk JWT)
   - Rate limiting middleware
   - Error handling

2. **Application Layer (Use Cases)**
   - CreateWorkflowUseCase
   - Orchestrates validation, creation, and audit logging
   - Transaction management

3. **Domain Layer (Entities)**
   - Workflow entity with business rules
   - WorkflowName value object with validation
   - WorkflowStatus enum

4. **Infrastructure Layer (Repositories)**
   - WorkflowRepository (SQLAlchemy async)
   - AuditLogRepository
   - Redis rate limit client

### Key Implementation Details

#### Pydantic Request Model

```python
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
import re

class CreateWorkflowRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(default="", max_length=1000)
    trigger_type: Optional[str] = Field(default=None)
    trigger_config: Optional[dict] = Field(default_factory=dict)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', v):
            raise ValueError('Name can only contain alphanumeric characters, spaces, hyphens, and underscores')
        return v
```

#### SQLAlchemy Model

```python
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone

class Workflow(Base):
    __tablename__ = 'workflows'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String, default='')
    trigger_type = Column(String(50), nullable=True)
    trigger_config = Column(JSONB, default=dict)
    status = Column(String(20), nullable=False, default='draft')
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("status IN ('draft', 'active', 'paused')", name='workflow_status_check'),
    )
```

---

## Dependencies

### Internal Dependencies

| Module | Dependency Type | Description |
|--------|-----------------|-------------|
| CRM | Soft | Workflows reference contacts |
| Marketing | Soft | Workflows can trigger campaigns |
| Authentication | Hard | Requires Clerk authentication |
| Multi-tenancy | Hard | Requires account isolation |

### External Dependencies

| Service | Purpose | Required |
|---------|---------|----------|
| Supabase PostgreSQL | Primary data storage | Yes |
| Clerk | Authentication and authorization | Yes |
| Redis | Rate limiting | Yes |

---

## Security Considerations

### Authentication

- All endpoints require valid JWT from Clerk
- JWT must contain `account_id` claim for tenant isolation

### Authorization

- User must have `workflows:create` permission
- Permission checked via Clerk metadata or custom RBAC

### Data Protection

- All workflow data encrypted at rest (Supabase default)
- TLS 1.3 for all API communications
- Audit logging for compliance

### Input Validation

- Name: Alphanumeric, hyphens, underscores only
- Description: HTML sanitized
- trigger_config: Schema validated based on trigger_type

---

## Performance Requirements

| Metric | Target |
|--------|--------|
| API Response Time (p95) | < 200ms |
| Database Query Time (p95) | < 50ms |
| Throughput | 100 requests/second |
| Rate Limit | 100 creations/account/hour |

---

## Constraints

### Technical Constraints

- Must use FastAPI async patterns
- Must use SQLAlchemy 2.0 async with Supabase
- Must integrate with existing Clerk authentication
- Must follow Clean Architecture patterns

### Business Constraints

- Workflows are account-scoped (multi-tenant)
- Maximum 500 workflows per account
- Soft delete with 90-day retention

---

## Related SPECs

| SPEC ID | Title | Relationship |
|---------|-------|--------------|
| SPEC-WFL-002 | Configure Trigger | Next step after creation |
| SPEC-WFL-003 | Add Action Step | Configures workflow actions |
| SPEC-WFL-005 | Execute Workflow | Runs completed workflows |
| SPEC-WFL-012 | Workflow Versioning | Version management |

---

## Traceability Tags

- TAG:SPEC-WFL-001
- TAG:MODULE-WORKFLOWS
- TAG:DOMAIN-AUTOMATION
- TAG:PRIORITY-CRITICAL
