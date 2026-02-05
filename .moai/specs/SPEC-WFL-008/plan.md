# SPEC-WFL-008: Workflow Templates - Implementation Plan

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-008 |
| **Title** | Workflow Templates |
| **Module** | workflows |
| **Domain** | automation |
| **Priority** | Medium |
| **Status** | Planned |

---

## Implementation Overview

This plan outlines the implementation strategy for the Workflow Templates feature, following the ANALYZE-PRESERVE-IMPROVE DDD methodology and TRUST 5 quality framework.

---

## Milestones

### Milestone 1: Database Schema and Models (Primary Goal)

**Objective:** Establish the data foundation for workflow templates

**Deliverables:**

1. **Database Migration**
   - Create `workflow_templates` table with JSONB workflow configuration
   - Create `template_usage` tracking table
   - Add indexes for category filtering and full-text search
   - Implement Row-Level Security (RLS) policies

2. **SQLAlchemy Models**
   - `WorkflowTemplate` entity model
   - `TemplateUsage` tracking model
   - `TemplateCategory` enum
   - Pydantic schemas for API validation

3. **Repository Layer**
   - `WorkflowTemplateRepository` with CRUD operations
   - Template search functionality
   - Category filtering queries
   - Usage tracking methods

**Technical Approach:**
- Use SQLAlchemy 2.0 async patterns
- JSONB for flexible workflow_config storage
- GIN indexes for JSONB and array search
- Supabase RLS for multi-tenant isolation

---

### Milestone 2: Template Library API (Primary Goal)

**Objective:** Implement core template retrieval and listing endpoints

**Deliverables:**

1. **List Templates Endpoint** (`GET /api/v1/workflow-templates`)
   - Pagination with cursor-based navigation
   - Category filtering via query parameter
   - Sort by usage, rating, or date
   - Include template counts per category

2. **Get Template Details** (`GET /api/v1/workflow-templates/:id`)
   - Full template metadata
   - Workflow configuration summary
   - Required integrations list
   - Usage statistics

3. **Template Preview** (`GET /api/v1/workflow-templates/:id/preview`)
   - Complete workflow configuration
   - Step-by-step breakdown
   - Visual graph data for frontend rendering

4. **Template Search** (`GET /api/v1/workflow-templates/search`)
   - Full-text search on name and description
   - Tag-based filtering
   - Action type filtering
   - Elasticsearch integration for advanced search

**Technical Approach:**
- FastAPI router with dependency injection
- Pydantic response models with proper serialization
- Redis caching for frequently accessed templates
- Background task for search indexing

---

### Milestone 3: Template Cloning Engine (Primary Goal)

**Objective:** Implement the core template-to-workflow cloning functionality

**Deliverables:**

1. **Clone Endpoint** (`POST /api/v1/workflow-templates/:id/clone`)
   - Deep copy of workflow configuration
   - UUID generation for new workflow
   - Account association
   - Status initialization (draft)

2. **Cloning Service**
   - `TemplateCloneService` with transaction support
   - Workflow configuration transformation
   - ID regeneration for all nested entities
   - Reference validation and repair

3. **Clone Validation**
   - Integration availability check
   - Permission verification
   - Account limits validation
   - Template completeness verification

4. **Usage Tracking**
   - Record template usage on successful clone
   - Update usage statistics
   - Track template version at clone time

**Technical Approach:**
- Database transaction for atomicity
- Deep copy with ID regeneration strategy
- Event emission for analytics integration
- Optimistic locking for concurrent clones

---

### Milestone 4: Custom Template Management (Secondary Goal)

**Objective:** Enable users to create and manage their own templates

**Deliverables:**

1. **Create Custom Template** (`POST /api/v1/workflow-templates`)
   - Workflow-to-template conversion
   - Content sanitization (PII removal)
   - Category assignment
   - Validation pipeline

2. **Update Template** (`PUT /api/v1/workflow-templates/:id`)
   - Partial update support
   - Version increment
   - Validation re-run

3. **Delete Template** (`DELETE /api/v1/workflow-templates/:id`)
   - Soft delete with retention
   - Usage preservation for analytics
   - Cascade handling for shared templates

4. **Template Sharing** (`POST /api/v1/workflow-templates/:id/share`)
   - Sub-account sharing for agencies
   - Share permission management
   - Revocation support

**Technical Approach:**
- PII detection and sanitization utilities
- Versioning with semver semantics
- Event-driven sharing notifications
- Cascading soft delete pattern

---

### Milestone 5: System Template Seeding (Secondary Goal)

**Objective:** Populate the platform with high-quality pre-built templates

**Deliverables:**

1. **Lead Nurturing Templates**
   - New Lead Welcome Sequence
   - Multi-touch Follow-up Campaign
   - Lead Qualification Workflow

2. **Appointment Templates**
   - Booking Confirmation
   - Appointment Reminder Series
   - No-Show Follow-up

3. **Onboarding Templates**
   - Welcome Email Series
   - Product Feature Introduction
   - Account Setup Checklist

4. **Re-engagement Templates**
   - Win-back Campaign
   - Inactive Contact Reactivation
   - Cart Abandonment Recovery

5. **Review Request Templates**
   - Post-Service Review Request
   - Testimonial Collection
   - NPS Survey Sequence

6. **Birthday/Anniversary Templates**
   - Birthday Celebration
   - Membership Anniversary
   - Loyalty Reward Notification

**Technical Approach:**
- YAML/JSON template definitions
- Database seeding scripts
- Versioned template files in repository
- Idempotent seeding for deployments

---

### Milestone 6: Frontend Integration (Final Goal)

**Objective:** Build the user interface for template management

**Deliverables:**

1. **Template Library Component**
   - Grid/list view with template cards
   - Category tabs/filters
   - Search input with debounced API calls
   - Infinite scroll pagination

2. **Template Preview Modal**
   - Read-only workflow visualization
   - Step details sidebar
   - "Use Template" CTA button

3. **Clone Workflow Flow**
   - Template selection confirmation
   - Workflow naming dialog
   - Redirect to workflow editor
   - Success notification

4. **Custom Template Creator**
   - "Save as Template" button in workflow editor
   - Template metadata form
   - Category selection
   - Sharing options (agency accounts)

**Technical Approach:**
- Next.js 14 with App Router
- Server Components for initial data
- Client Components for interactivity
- Shadcn/UI component library
- React Query for data fetching

---

### Milestone 7: Performance Optimization (Optional Goal)

**Objective:** Ensure template operations meet performance targets

**Deliverables:**

1. **Caching Layer**
   - Redis caching for template library
   - Cache invalidation strategy
   - Template preview caching

2. **Search Optimization**
   - Elasticsearch index optimization
   - Search result caching
   - Autocomplete suggestions

3. **Clone Performance**
   - Async processing for large templates
   - Progress tracking for bulk operations
   - Connection pooling optimization

**Technical Approach:**
- Redis with TTL-based invalidation
- Elasticsearch with dedicated template index
- Background job queue for heavy operations

---

## Technical Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │ Template     │ │ Preview      │ │ Custom Template      │ │
│  │ Library      │ │ Modal        │ │ Creator              │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
└────────────────────────────┬────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │ Template     │ │ Clone        │ │ Custom Template      │ │
│  │ Router       │ │ Service      │ │ Service              │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │ Template     │ │ Search       │ │ Validation           │ │
│  │ Repository   │ │ Service      │ │ Service              │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
└───────┬─────────────────┬─────────────────┬─────────────────┘
        │                 │                 │
┌───────▼───────┐ ┌───────▼───────┐ ┌───────▼───────┐
│  PostgreSQL   │ │    Redis      │ │ Elasticsearch │
│  (Supabase)   │ │   (Cache)     │ │   (Search)    │
└───────────────┘ └───────────────┘ └───────────────┘
```

### Directory Structure

```
backend/
├── app/
│   ├── workflows/
│   │   ├── templates/
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   ├── models.py
│   │   │   ├── repository.py
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── template_service.py
│   │   │   │   ├── clone_service.py
│   │   │   │   ├── search_service.py
│   │   │   │   └── validation_service.py
│   │   │   └── seed/
│   │   │       ├── __init__.py
│   │   │       ├── lead_nurturing.yaml
│   │   │       ├── appointment_reminder.yaml
│   │   │       ├── onboarding.yaml
│   │   │       ├── re_engagement.yaml
│   │   │       ├── review_request.yaml
│   │   │       └── birthday_celebration.yaml
│   │   └── ...

frontend/
├── app/
│   ├── workflows/
│   │   ├── templates/
│   │   │   ├── page.tsx
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx
│   │   │   └── components/
│   │   │       ├── template-card.tsx
│   │   │       ├── template-grid.tsx
│   │   │       ├── template-preview.tsx
│   │   │       ├── template-search.tsx
│   │   │       ├── category-filter.tsx
│   │   │       └── clone-dialog.tsx
│   │   └── ...
```

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Complex workflow config may fail deep copy | High | Medium | Comprehensive unit tests for all action types |
| Search performance degradation | Medium | Low | Elasticsearch with proper indexing |
| Template versioning conflicts | Medium | Low | Optimistic locking, version tracking |
| PII leakage in custom templates | High | Medium | Automated sanitization, review process |
| Integration availability at clone time | Medium | Medium | Pre-clone validation, clear error messages |

---

## Quality Gates

### TRUST 5 Compliance

| Pillar | Requirement | Validation |
|--------|-------------|------------|
| **Tested** | 85%+ code coverage | pytest with coverage report |
| **Readable** | Documentation for all public APIs | OpenAPI spec, docstrings |
| **Unified** | Single source of truth for templates | Repository pattern |
| **Secured** | RLS policies, input validation | Security tests, OWASP compliance |
| **Trackable** | Audit logging for template operations | Structured logging |

### LSP Quality Gates

| Phase | Requirement |
|-------|-------------|
| **Run** | Zero type errors, zero lint errors |
| **Sync** | Zero errors, max 10 warnings |

---

## Dependencies

### Required Before Implementation

- SPEC-WFL-001 (Create Workflow) - Base workflow CRUD operations
- SPEC-WFL-002 (Configure Trigger) - Trigger configuration system
- SPEC-WFL-003 (Add Action Step) - Action step management

### Can Be Implemented In Parallel

- SPEC-WFL-009 (Workflow Analytics) - Template usage analytics

---

## Traceability

| Artifact | Reference |
|----------|-----------|
| Specification | spec.md |
| Acceptance Criteria | acceptance.md |
| Product Requirement | Workflows Module - Pre-built workflow templates |
| Technical Stack | FastAPI, PostgreSQL/Supabase, Redis, Elasticsearch |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-26 | SPEC Builder | Initial implementation plan |
