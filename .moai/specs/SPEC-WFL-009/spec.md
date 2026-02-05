# SPEC-WFL-009: Workflow Analytics

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-009 |
| **Title** | Workflow Analytics |
| **Module** | workflows |
| **Domain** | automation |
| **Priority** | High |
| **Status** | Planned |
| **Created** | 2026-01-26 |
| **Version** | 1.0.0 |

---

## Environment

### Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Backend Framework | FastAPI | Latest |
| Database | PostgreSQL (Supabase) | 16 |
| Cache | Redis | 7 |
| Search/Analytics | Elasticsearch | 8 |
| Frontend | Next.js | 14 |
| UI Components | Shadcn/UI | Latest |
| Charting | Recharts / Tremor | Latest |

### Dependencies

- SPEC-WFL-001: Create Workflow (workflow creation provides base data)
- SPEC-WFL-005: Execute Workflow (execution events provide metrics source)
- SPEC-WFL-007: Goal Tracking (goal achievement data for conversion metrics)

### Infrastructure Requirements

- Time-series data storage for historical metrics
- Real-time event streaming for live dashboard updates
- Aggregation pipeline for metrics calculation
- CDN caching for dashboard static assets

---

## Assumptions

### Technical Assumptions

| ID | Assumption | Confidence | Risk if Wrong |
|----|------------|------------|---------------|
| A1 | Workflow execution events are reliably captured in database | High | Incomplete metrics, data loss |
| A2 | PostgreSQL can handle analytics queries at scale | Medium | May need dedicated analytics DB |
| A3 | Redis pub/sub is sufficient for real-time updates | Medium | May need WebSocket server |
| A4 | 30-day retention is acceptable for detailed metrics | Medium | Storage costs may increase |

### Business Assumptions

| ID | Assumption | Confidence | Risk if Wrong |
|----|------------|------------|---------------|
| B1 | Users need real-time metrics (< 5 second delay) | Medium | Over-engineering if not needed |
| B2 | Funnel visualization is primary use case | High | UI redesign needed |
| B3 | Export functionality is required | High | User complaints |

---

## Requirements

### EARS Format Specifications

#### REQ-WFL-009-01: Analytics Dashboard Display (Event-Driven)

**WHEN** a user views workflow performance
**THEN** the system shall display metrics on enrollment, completion, and conversions
**RESULTING IN** an analytics dashboard with funnel visualization

**Details:**
- Dashboard loads within 2 seconds for workflows with up to 100,000 enrollments
- Real-time metrics update every 5 seconds when dashboard is active
- Funnel visualization shows step-by-step drop-off rates

#### REQ-WFL-009-02: Enrollment Tracking (Ubiquitous)

**THE SYSTEM SHALL** track all workflow enrollments with timestamp, source, and contact reference

**Metrics Captured:**
- total_enrolled: Total contacts ever enrolled in workflow
- currently_active: Contacts currently progressing through workflow
- enrollment_rate: New enrollments per time period (hourly, daily, weekly)
- enrollment_source: How contacts entered workflow (trigger, bulk, API)

#### REQ-WFL-009-03: Completion Metrics (Ubiquitous)

**THE SYSTEM SHALL** track workflow completion with exit reasons and duration

**Metrics Captured:**
- completed: Total contacts who reached final step
- completion_rate: Percentage of enrolled contacts who completed
- average_duration: Mean time from enrollment to completion
- exit_reasons: Distribution of why contacts left workflow

#### REQ-WFL-009-04: Conversion Tracking (Event-Driven)

**WHEN** a contact achieves a workflow goal
**THEN** the system shall record conversion event and update conversion metrics

**Metrics Captured:**
- goals_achieved: Total goal completions
- conversion_rate: Percentage of enrolled contacts achieving goal
- time_to_conversion: Average time from enrollment to goal
- goal_breakdown: Conversions by goal type (if multiple goals)

#### REQ-WFL-009-05: Action Performance Metrics (Ubiquitous)

**THE SYSTEM SHALL** track performance metrics for each action in workflow

**Metrics Captured:**
- action_execution_count: Times each action was executed
- action_success_rate: Percentage of successful executions
- action_error_rate: Percentage of failed executions
- action_duration: Average execution time per action type

#### REQ-WFL-009-06: Drop-off Analysis (Event-Driven)

**WHEN** analyzing workflow funnel
**THEN** the system shall identify drop-off points between workflow steps

**Analysis Provided:**
- drop_off_points: Steps with highest exit rates
- step_conversion_rates: Conversion between consecutive steps
- bottleneck_identification: Steps causing delays
- comparison_benchmarks: Performance vs. previous periods

#### REQ-WFL-009-07: Time-Based Filtering (State-Driven)

**WHILE** viewing analytics dashboard
**THE SYSTEM SHALL** allow filtering by date range and time periods

**Filter Options:**
- Preset ranges: Today, Last 7 days, Last 30 days, Last 90 days, Custom
- Comparison mode: Compare current period to previous period
- Timezone-aware: Display times in user's local timezone

#### REQ-WFL-009-08: Data Export (Event-Driven)

**WHEN** user requests analytics export
**THEN** the system shall generate downloadable report

**Export Formats:**
- CSV: Raw metrics data
- PDF: Formatted report with visualizations
- JSON: API-compatible structured data

#### REQ-WFL-009-09: Real-time Updates (State-Driven)

**WHILE** dashboard is open and workflow is active
**THE SYSTEM SHALL** update metrics in real-time without page refresh

**Update Behavior:**
- Polling interval: 5 seconds for active workflows
- Incremental updates: Only changed metrics transmitted
- Connection recovery: Auto-reconnect on network issues

#### REQ-WFL-009-10: Data Retention (Unwanted)

**THE SYSTEM SHALL NOT** retain detailed execution logs beyond 90 days

**Retention Policy:**
- Detailed logs: 90 days
- Aggregated daily metrics: 2 years
- Monthly summaries: Indefinite

---

## Specifications

### Data Model

#### WorkflowAnalytics Entity

```
workflow_analytics:
  id: UUID (primary key)
  workflow_id: UUID (foreign key to workflows)
  date: DATE (aggregation date)

  # Enrollment metrics
  total_enrolled: INTEGER
  new_enrollments: INTEGER
  currently_active: INTEGER

  # Completion metrics
  completed: INTEGER
  completion_rate: DECIMAL(5,2)
  average_duration_seconds: INTEGER

  # Conversion metrics
  goals_achieved: INTEGER
  conversion_rate: DECIMAL(5,2)

  # Timestamps
  created_at: TIMESTAMP WITH TIME ZONE
  updated_at: TIMESTAMP WITH TIME ZONE
```

#### WorkflowStepMetrics Entity

```
workflow_step_metrics:
  id: UUID (primary key)
  workflow_id: UUID (foreign key)
  step_id: UUID (foreign key to workflow_steps)
  date: DATE

  # Step performance
  entered: INTEGER
  completed: INTEGER
  dropped_off: INTEGER
  step_conversion_rate: DECIMAL(5,2)
  average_time_in_step_seconds: INTEGER

  # Action performance (if action step)
  executions: INTEGER
  successes: INTEGER
  failures: INTEGER

  # Timestamps
  created_at: TIMESTAMP WITH TIME ZONE
  updated_at: TIMESTAMP WITH TIME ZONE
```

#### WorkflowExecution Entity (for real-time tracking)

```
workflow_executions:
  id: UUID (primary key)
  workflow_id: UUID (foreign key)
  contact_id: UUID (foreign key)

  # Status tracking
  status: ENUM('active', 'completed', 'goal_achieved', 'exited', 'error')
  current_step_id: UUID (nullable)

  # Timestamps
  enrolled_at: TIMESTAMP WITH TIME ZONE
  completed_at: TIMESTAMP WITH TIME ZONE (nullable)
  goal_achieved_at: TIMESTAMP WITH TIME ZONE (nullable)

  # Source tracking
  enrollment_source: ENUM('trigger', 'bulk', 'api', 'manual')
  exit_reason: TEXT (nullable)
```

### API Endpoints

#### GET /api/v1/workflows/{workflow_id}/analytics

**Description:** Retrieve workflow analytics summary

**Path Parameters:**
- workflow_id: UUID - Target workflow identifier

**Query Parameters:**
- start_date: DATE - Start of date range (required)
- end_date: DATE - End of date range (required)
- granularity: ENUM('hourly', 'daily', 'weekly') - Aggregation level (default: 'daily')

**Response Schema:**
```json
{
  "workflow_id": "uuid",
  "period": {
    "start_date": "2026-01-01",
    "end_date": "2026-01-31"
  },
  "summary": {
    "total_enrolled": 5000,
    "currently_active": 1200,
    "completed": 2800,
    "completion_rate": 56.0,
    "goals_achieved": 1400,
    "conversion_rate": 28.0,
    "average_duration_hours": 72.5
  },
  "trends": [
    {
      "date": "2026-01-01",
      "new_enrollments": 150,
      "completions": 80,
      "conversions": 40
    }
  ]
}
```

**Status Codes:**
- 200: Success
- 400: Invalid date range
- 404: Workflow not found
- 403: Unauthorized access

#### GET /api/v1/workflows/{workflow_id}/analytics/funnel

**Description:** Retrieve funnel visualization data

**Path Parameters:**
- workflow_id: UUID - Target workflow identifier

**Query Parameters:**
- start_date: DATE - Start of date range (required)
- end_date: DATE - End of date range (required)

**Response Schema:**
```json
{
  "workflow_id": "uuid",
  "funnel_steps": [
    {
      "step_id": "uuid",
      "step_name": "Send Welcome Email",
      "step_order": 1,
      "entered": 5000,
      "completed": 4800,
      "dropped_off": 200,
      "conversion_rate": 96.0,
      "average_time_seconds": 5
    },
    {
      "step_id": "uuid",
      "step_name": "Wait 1 Day",
      "step_order": 2,
      "entered": 4800,
      "completed": 4500,
      "dropped_off": 300,
      "conversion_rate": 93.75,
      "average_time_seconds": 86400
    }
  ],
  "overall_conversion": 56.0,
  "bottleneck_step": "step_id"
}
```

#### GET /api/v1/workflows/{workflow_id}/analytics/actions

**Description:** Retrieve action performance metrics

**Path Parameters:**
- workflow_id: UUID - Target workflow identifier

**Query Parameters:**
- start_date: DATE - Start of date range (required)
- end_date: DATE - End of date range (required)

**Response Schema:**
```json
{
  "workflow_id": "uuid",
  "actions": [
    {
      "action_id": "uuid",
      "action_type": "send_email",
      "action_name": "Welcome Email",
      "executions": 4800,
      "successes": 4750,
      "failures": 50,
      "success_rate": 98.96,
      "average_duration_ms": 250
    }
  ]
}
```

#### GET /api/v1/workflows/{workflow_id}/analytics/export

**Description:** Export analytics data

**Path Parameters:**
- workflow_id: UUID - Target workflow identifier

**Query Parameters:**
- start_date: DATE - Start of date range (required)
- end_date: DATE - End of date range (required)
- format: ENUM('csv', 'pdf', 'json') - Export format (default: 'csv')

**Response:**
- Content-Type: application/octet-stream (CSV/PDF) or application/json
- Content-Disposition: attachment; filename="workflow-analytics-{id}-{date}.{ext}"

#### POST /api/v1/workflows/{workflow_id}/analytics/refresh

**Description:** Trigger manual refresh of aggregated metrics

**Path Parameters:**
- workflow_id: UUID - Target workflow identifier

**Response Schema:**
```json
{
  "status": "queued",
  "job_id": "uuid",
  "estimated_completion_seconds": 30
}
```

### Funnel Visualization Data Structure

```typescript
interface FunnelData {
  steps: FunnelStep[];
  metadata: FunnelMetadata;
}

interface FunnelStep {
  id: string;
  name: string;
  order: number;
  type: 'trigger' | 'action' | 'condition' | 'wait' | 'goal';

  // Metrics
  entered: number;
  completed: number;
  droppedOff: number;
  conversionRate: number;

  // Visual properties
  color: string;
  width: number; // Proportional to entered count
}

interface FunnelMetadata {
  totalEnrolled: number;
  finalConverted: number;
  overallConversionRate: number;
  bottleneckStepId: string | null;
  averageDuration: number;
}
```

### Analytics Calculation Logic

#### Conversion Rate Calculation

```
conversion_rate = (goals_achieved / total_enrolled) * 100

Where:
- goals_achieved: Count of workflow_executions where status = 'goal_achieved'
- total_enrolled: Count of all workflow_executions for the workflow
```

#### Completion Rate Calculation

```
completion_rate = (completed / total_enrolled) * 100

Where:
- completed: Count where status IN ('completed', 'goal_achieved')
- total_enrolled: Count of all workflow_executions
```

#### Step Drop-off Calculation

```
step_drop_off_rate = ((entered - completed) / entered) * 100

drop_off_points = ORDER BY step_drop_off_rate DESC LIMIT 3
```

#### Average Duration Calculation

```
average_duration = AVG(completed_at - enrolled_at)

WHERE status IN ('completed', 'goal_achieved')
AND completed_at IS NOT NULL
```

### Real-time Update Architecture

```
+------------------+     +-----------------+     +------------------+
|  Workflow        |     |     Redis       |     |   Frontend       |
|  Execution       |---->|   Pub/Sub       |---->|   Dashboard      |
|  Service         |     |   Channel       |     |   (SSE/WS)       |
+------------------+     +-----------------+     +------------------+
        |                        ^
        |                        |
        v                        |
+------------------+     +-----------------+
|  PostgreSQL      |     |  Aggregation    |
|  (Events)        |---->|  Worker         |
+------------------+     +-----------------+
```

**Event Flow:**
1. Workflow execution creates event in PostgreSQL
2. Database trigger or application event publishes to Redis
3. Aggregation worker processes events incrementally
4. Updated metrics broadcast via Redis pub/sub
5. Frontend receives update via Server-Sent Events (SSE)

---

## Constraints

### Performance Constraints

| Constraint | Target | Measurement |
|------------|--------|-------------|
| Dashboard load time | < 2 seconds | P95 latency |
| Real-time update delay | < 5 seconds | Event to display |
| Export generation | < 30 seconds | For 100K records |
| Query response time | < 500ms | P95 latency |

### Scalability Constraints

| Constraint | Target |
|------------|--------|
| Max enrollments per workflow | 1,000,000 |
| Max concurrent dashboard users | 1,000 |
| Historical data retention | 90 days detailed, 2 years aggregated |
| Max export size | 1,000,000 rows |

### Security Constraints

- Analytics data restricted to workflow owner and account admins
- Export requires explicit user action (no automated downloads)
- Audit logging for all analytics access
- Rate limiting: 60 requests/minute per user

---

## Traceability

| Requirement | Test | Acceptance Criteria |
|-------------|------|---------------------|
| REQ-WFL-009-01 | test_dashboard_display | AC-WFL-009-01 |
| REQ-WFL-009-02 | test_enrollment_tracking | AC-WFL-009-02 |
| REQ-WFL-009-03 | test_completion_metrics | AC-WFL-009-03 |
| REQ-WFL-009-04 | test_conversion_tracking | AC-WFL-009-04 |
| REQ-WFL-009-05 | test_action_performance | AC-WFL-009-05 |
| REQ-WFL-009-06 | test_dropoff_analysis | AC-WFL-009-06 |
| REQ-WFL-009-07 | test_time_filtering | AC-WFL-009-07 |
| REQ-WFL-009-08 | test_data_export | AC-WFL-009-08 |
| REQ-WFL-009-09 | test_realtime_updates | AC-WFL-009-09 |
| REQ-WFL-009-10 | test_data_retention | AC-WFL-009-10 |

---

## Related SPECs

| SPEC ID | Relationship | Description |
|---------|--------------|-------------|
| SPEC-WFL-001 | Dependency | Provides workflow structure data |
| SPEC-WFL-005 | Dependency | Provides execution events |
| SPEC-WFL-007 | Dependency | Provides goal achievement data |
| SPEC-WFL-011 | Related | Bulk enrollment tracking integration |

---

## References

- [EARS Specification](https://www.iaria.org/conferences2009/filesICCGI09/ICCGI-2009%20EARS%20paper.pdf)
- [Time Series Analytics Best Practices](https://www.timescale.com/blog/time-series-data-why-and-how-to-use-a-relational-database-instead-of-nosql/)
- [Funnel Analysis Patterns](https://amplitude.com/blog/funnel-analysis)
