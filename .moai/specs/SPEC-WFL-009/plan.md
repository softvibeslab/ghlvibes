# SPEC-WFL-009: Workflow Analytics - Implementation Plan

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-009 |
| **Title** | Workflow Analytics |
| **Related SPEC** | [spec.md](./spec.md) |
| **Acceptance Criteria** | [acceptance.md](./acceptance.md) |

---

## Implementation Overview

### Scope Summary

Implement a comprehensive workflow analytics system that tracks enrollment, completion, conversion metrics, and provides funnel visualization with real-time updates and data export capabilities.

### Key Deliverables

1. **Backend Analytics Service** - FastAPI endpoints for metrics retrieval and aggregation
2. **Data Model** - PostgreSQL tables for analytics storage and time-series data
3. **Aggregation Pipeline** - Background workers for metrics calculation
4. **Real-time Updates** - Redis pub/sub with SSE for live dashboard
5. **Frontend Dashboard** - Next.js analytics page with charts and funnel visualization
6. **Export System** - CSV, PDF, and JSON export functionality

---

## Milestones

### Milestone 1: Data Foundation (Primary Goal)

**Objective:** Establish database schema and core data collection

**Tasks:**
- [ ] Create `workflow_analytics` table with daily aggregation structure
- [ ] Create `workflow_step_metrics` table for funnel data
- [ ] Create `workflow_executions` table for real-time tracking
- [ ] Implement database migrations
- [ ] Create indexes for analytics queries
- [ ] Set up partitioning for time-series data (monthly partitions)

**Validation:**
- Migrations run successfully
- Indexes improve query performance by 80%+
- Schema supports 1M+ records per workflow

### Milestone 2: Core Analytics API (Primary Goal)

**Objective:** Implement REST API endpoints for analytics retrieval

**Tasks:**
- [ ] Implement `GET /api/v1/workflows/{id}/analytics` endpoint
- [ ] Implement `GET /api/v1/workflows/{id}/analytics/funnel` endpoint
- [ ] Implement `GET /api/v1/workflows/{id}/analytics/actions` endpoint
- [ ] Add date range filtering and validation
- [ ] Add granularity options (hourly, daily, weekly)
- [ ] Implement response caching with Redis
- [ ] Add rate limiting (60 requests/minute)

**Validation:**
- All endpoints return correct data structure
- Response time < 500ms for P95
- Cache hit rate > 80% for repeated queries

### Milestone 3: Aggregation Pipeline (Secondary Goal)

**Objective:** Implement background processing for metrics calculation

**Tasks:**
- [ ] Create analytics aggregation worker using Celery
- [ ] Implement incremental aggregation (process only new events)
- [ ] Implement daily rollup job (consolidate hourly to daily)
- [ ] Implement monthly rollup job (consolidate daily to monthly)
- [ ] Add manual refresh endpoint
- [ ] Implement data retention policy (90-day detailed cleanup)

**Validation:**
- Aggregation completes within 5 minutes for 100K events
- Incremental updates process within 30 seconds
- Data retention job runs without errors

### Milestone 4: Real-time Updates (Secondary Goal)

**Objective:** Enable live dashboard updates without page refresh

**Tasks:**
- [ ] Set up Redis pub/sub channels for workflow events
- [ ] Implement SSE (Server-Sent Events) endpoint
- [ ] Add event publishing from workflow execution service
- [ ] Implement connection management (heartbeat, reconnect)
- [ ] Add incremental metric updates (delta only)
- [ ] Implement fallback polling for unsupported clients

**Validation:**
- Events appear in dashboard within 5 seconds
- SSE connections remain stable for 1+ hours
- Fallback polling works on legacy browsers

### Milestone 5: Frontend Dashboard (Secondary Goal)

**Objective:** Build analytics UI with charts and funnel visualization

**Tasks:**
- [ ] Create analytics page layout with Shadcn/UI
- [ ] Implement summary metrics cards (enrolled, active, completed, conversion)
- [ ] Implement funnel visualization component
- [ ] Implement trend charts (line/area charts for time series)
- [ ] Add action performance table
- [ ] Add date range picker with presets
- [ ] Implement responsive design for mobile

**Validation:**
- Dashboard loads within 2 seconds
- All visualizations render correctly
- Mobile layout is usable

### Milestone 6: Export Functionality (Final Goal)

**Objective:** Enable data export in multiple formats

**Tasks:**
- [ ] Implement CSV export (streaming for large datasets)
- [ ] Implement JSON export
- [ ] Implement PDF export with charts (using puppeteer or similar)
- [ ] Add export job queue for large exports
- [ ] Add download progress tracking
- [ ] Implement export access logging

**Validation:**
- CSV export handles 1M rows without timeout
- PDF includes all visualizations
- Export completes within 30 seconds for 100K records

### Milestone 7: Testing and Documentation (Final Goal)

**Objective:** Ensure quality and maintainability

**Tasks:**
- [ ] Write unit tests for analytics service (85%+ coverage)
- [ ] Write integration tests for API endpoints
- [ ] Write E2E tests for dashboard functionality
- [ ] Create characterization tests for aggregation logic
- [ ] Write API documentation (OpenAPI)
- [ ] Create user guide for analytics features

**Validation:**
- Test coverage meets 85% target
- All E2E tests pass
- Documentation is complete and accurate

---

## Technical Approach

### Architecture Design

```
+------------------------------------------+
|              Frontend Layer               |
|  (Next.js 14 + Shadcn/UI + Recharts)     |
+------------------------------------------+
                    |
                    | REST API + SSE
                    v
+------------------------------------------+
|           Application Layer               |
|     (FastAPI + Pydantic Validation)       |
+------------------------------------------+
                    |
        +-----------+-----------+
        |                       |
        v                       v
+---------------+       +---------------+
|   Domain      |       |   Domain      |
|   Service     |       |   Service     |
| (Analytics)   |       | (Aggregation) |
+---------------+       +---------------+
        |                       |
        +-----------+-----------+
                    |
                    v
+------------------------------------------+
|          Infrastructure Layer             |
|  +------------+  +--------+  +---------+ |
|  | PostgreSQL |  | Redis  |  | Celery  | |
|  | (Supabase) |  | Cache  |  | Workers | |
|  +------------+  +--------+  +---------+ |
+------------------------------------------+
```

### Backend Implementation

**Analytics Service Structure:**

```
src/backend/domain/workflows/analytics/
  __init__.py
  service.py           # Core analytics logic
  repository.py        # Database access
  models.py            # Pydantic models
  aggregation.py       # Aggregation calculations
  realtime.py          # SSE and pub/sub
  export.py            # Export generation

src/backend/api/v1/endpoints/
  workflow_analytics.py  # API routes
```

**Key Dependencies:**
- FastAPI for REST API
- SQLAlchemy 2.0 async for database
- Pydantic v2.9 for validation
- Redis for caching and pub/sub
- Celery for background jobs
- pandas for data processing

### Frontend Implementation

**Component Structure:**

```
src/frontend/app/workflows/[id]/analytics/
  page.tsx             # Main analytics page
  loading.tsx          # Loading skeleton

src/frontend/components/workflows/analytics/
  AnalyticsSummary.tsx    # Metric cards
  FunnelVisualization.tsx # Funnel chart
  TrendChart.tsx          # Time series chart
  ActionPerformance.tsx   # Action metrics table
  DateRangePicker.tsx     # Date filter
  ExportButton.tsx        # Export dropdown
```

**Key Dependencies:**
- Shadcn/UI for components
- Recharts or Tremor for charts
- TanStack Query for data fetching
- date-fns for date handling

### Database Design

**Indexing Strategy:**

```sql
-- Primary analytics queries
CREATE INDEX idx_workflow_analytics_workflow_date
  ON workflow_analytics(workflow_id, date DESC);

-- Step metrics funnel queries
CREATE INDEX idx_step_metrics_workflow_step
  ON workflow_step_metrics(workflow_id, step_id, date DESC);

-- Execution tracking queries
CREATE INDEX idx_executions_workflow_status
  ON workflow_executions(workflow_id, status, enrolled_at DESC);

-- Partial index for active executions
CREATE INDEX idx_executions_active
  ON workflow_executions(workflow_id, current_step_id)
  WHERE status = 'active';
```

**Partitioning Strategy:**

```sql
-- Monthly partitions for analytics data
CREATE TABLE workflow_analytics (
  ...
) PARTITION BY RANGE (date);

CREATE TABLE workflow_analytics_2026_01
  PARTITION OF workflow_analytics
  FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```

### Caching Strategy

| Data Type | Cache Key Pattern | TTL | Invalidation |
|-----------|-------------------|-----|--------------|
| Summary metrics | `analytics:{workflow_id}:{date_range}:summary` | 5 min | On new event |
| Funnel data | `analytics:{workflow_id}:{date_range}:funnel` | 5 min | On new event |
| Action metrics | `analytics:{workflow_id}:{date_range}:actions` | 5 min | On new event |
| User preferences | `analytics:user:{user_id}:prefs` | 24 hours | On update |

### Real-time Implementation

**Redis Pub/Sub Channels:**

```
workflow_analytics:{workflow_id}  # Workflow-specific updates
workflow_analytics:broadcast      # Global announcements
```

**SSE Event Format:**

```json
{
  "event": "metrics_update",
  "data": {
    "workflow_id": "uuid",
    "timestamp": "2026-01-26T10:30:00Z",
    "changes": {
      "currently_active": 1201,
      "new_enrollments_delta": 1
    }
  }
}
```

---

## Risk Assessment

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Query performance degradation at scale | Medium | High | Pre-aggregation, partitioning, query optimization |
| SSE connection stability issues | Medium | Medium | Fallback polling, connection pooling |
| Export timeout for large datasets | Medium | Medium | Streaming exports, job queue with progress |
| Aggregation job failures | Low | High | Idempotent operations, retry logic, alerting |

### Mitigation Strategies

1. **Performance:** Implement query explain analysis during development; add performance tests
2. **Reliability:** Circuit breaker for external dependencies; graceful degradation
3. **Scalability:** Design for horizontal scaling; stateless services

---

## Quality Gates

### TRUST 5 Compliance

| Pillar | Requirement | Validation |
|--------|-------------|------------|
| **Tested** | 85% code coverage | pytest-cov report |
| **Readable** | Docstrings on all public methods | pylint checks |
| **Unified** | Consistent API response format | OpenAPI validation |
| **Secured** | Authorization on all endpoints | Security tests |
| **Trackable** | Structured logging | Log analysis |

### Definition of Done

- [ ] All acceptance criteria in acceptance.md pass
- [ ] Unit test coverage >= 85%
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] API documentation updated
- [ ] Performance benchmarks met
- [ ] Security review completed
- [ ] Code reviewed and approved

---

## Dependencies and Blockers

### Prerequisites

| Dependency | Status | Blocker |
|------------|--------|---------|
| SPEC-WFL-001: Create Workflow | Required | Provides workflow data structure |
| SPEC-WFL-005: Execute Workflow | Required | Provides execution events |
| SPEC-WFL-007: Goal Tracking | Required | Provides goal achievement data |
| Redis infrastructure | Required | Caching and pub/sub |
| Celery workers | Required | Background processing |

### External Dependencies

| Service | Purpose | Fallback |
|---------|---------|----------|
| Supabase PostgreSQL | Primary data store | N/A (critical) |
| Redis | Caching, pub/sub | Direct DB queries (degraded) |
| Elasticsearch | Advanced analytics | PostgreSQL full-text search |

---

## Resource Requirements

### Development Resources

| Role | Allocation | Duration |
|------|------------|----------|
| Backend Developer | 1 FTE | Milestones 1-4, 6 |
| Frontend Developer | 1 FTE | Milestone 5 |
| QA Engineer | 0.5 FTE | Milestone 7 |

### Infrastructure Resources

| Resource | Specification |
|----------|---------------|
| Database | PostgreSQL 16 with 100GB+ storage |
| Cache | Redis 7 with 1GB+ memory |
| Workers | 2+ Celery workers |
| Compute | 2+ API instances |

---

## Traceability

| Milestone | Requirements Covered |
|-----------|---------------------|
| Milestone 1 | REQ-WFL-009-02, REQ-WFL-009-10 |
| Milestone 2 | REQ-WFL-009-01, REQ-WFL-009-07 |
| Milestone 3 | REQ-WFL-009-02, REQ-WFL-009-03, REQ-WFL-009-04, REQ-WFL-009-05 |
| Milestone 4 | REQ-WFL-009-09 |
| Milestone 5 | REQ-WFL-009-01, REQ-WFL-009-06 |
| Milestone 6 | REQ-WFL-009-08 |
| Milestone 7 | All requirements (validation) |
