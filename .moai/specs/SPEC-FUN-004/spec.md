# SPEC-FUN-004: Funnel Analytics - Performance Tracking Backend

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-FUN-004 |
| **Title** | Funnel Analytics - Performance Tracking Backend |
| **Module** | funnels-analytics |
| **Domain** | analytics-reporting |
| **Priority** | High |
| **Status** | Planned |
| **Created** | 2026-02-07 |
| **Version** | 1.0.0 |

---

## Overview

This specification defines the backend system for funnel analytics, including conversion tracking, step-by-step analytics, revenue metrics, A/B test results, and drop-off analysis.

**Scope:** Complete backend API for funnel performance analytics with real-time tracking.

**Target Users:** Marketing teams requiring detailed funnel performance insights.

---

## Environment

### Technical Environment

**Backend Framework:**
- FastAPI 0.115+ with Python 3.13+
- Async analytics queries

**Database:**
- PostgreSQL 16+ with timescaledb for time-series data
- Materialized views for aggregations
- Partitioning for large datasets

**Caching:**
- Redis for real-time metrics caching
- Query result caching

---

## Assumptions

**Assumption 1:** Analytics events sent from frontend via tracking endpoint.

**Confidence Level:** High

**Evidence Basis:** Standard web analytics pattern.

**Risk if Wrong:** No analytics data available.

**Validation Method:** Verify tracking endpoint accessible.

**Assumption 2:** Time-series data grows significantly (millions of events).

**Confidence Level:** High

**Evidence Basis:** Analytics data high-volume.

**Risk if Wrong:** Query performance degrades.

**Validation Method:** Implement partitioning and archiving.

---

## EARS Requirements

### REQ-FUN-004-01: Track Page View (Event-Driven)

**WHEN** a frontend sends a POST request to /api/v1/analytics/track,
**THEN** the system shall record page view event,
**RESULTING IN** 202 status (accepted for processing),
**IN STATE** event_recorded.

**Request Body:**
```json
{
  "event_type": "page_view",
  "funnel_id": "uuid",
  "page_id": "uuid",
  "session_id": "string (uuid)",
  "visitor_id": "string (uuid, stored in cookie)",
  "url": "string",
  "user_agent": "string",
  "ip_address": "string",
  "referrer": "string (optional)",
  "utm_source": "string (optional)",
  "utm_medium": "string (optional)",
  "utm_campaign": "string (optional)",
  "metadata": "object (optional)"
}
```

**Acceptance Criteria:**
- Event queued for async processing
- Returns 202 immediately
- Invalid events logged but don't block
- Rate limiting: 100 events/second per IP

### REQ-FUN-004-02: Track Conversion Event (Event-Driven)

**WHEN** a frontend sends a POST request to /api/v1/analytics/track with conversion,
**THEN** the system shall record conversion event and update metrics,
**RESULTING IN** 202 status,
**IN STATE** conversion_recorded.

**Request Body:**
```json
{
  "event_type": "conversion",
  "funnel_id": "uuid",
  "page_id": "uuid",
  "session_id": "string",
  "visitor_id": "string",
  "conversion_type": "form_submit | purchase | signup | custom",
  "value_cents": "integer (optional, for purchases)",
  "conversion_goal_id": "uuid (optional)",
  "metadata": "object"
}
```

**Acceptance Criteria:**
- Conversion linked to session
- Real-time metrics updated
- Revenue tracked if value provided

### REQ-FUN-004-03: Track Funnel Step Entry (Event-Driven)

**WHEN** a visitor enters a funnel step,
**THEN** the system shall record step entry event,
**RESULTING IN** 202 status,
**IN STATE** step_entry_recorded.

**Request Body:**
```json
{
  "event_type": "step_entry",
  "funnel_id": "uuid",
  "funnel_step_id": "uuid",
  "session_id": "string",
  "visitor_id": "string",
  "previous_step_id": "uuid (optional)"
}
```

**Acceptance Criteria:**
- Records visitor progression through funnel
- Time spent in previous step calculated

### REQ-FUN-004-04: Track Funnel Step Exit (Event-Driven)

**WHEN** a visitor exits a funnel step,
**THEN** the system shall record step exit event with outcome,
**RESULTING IN** 202 status,
**IN STATE** step_exit_recorded.

**Request Body:**
```json
{
  "event_type": "step_exit",
  "funnel_id": "uuid",
  "funnel_step_id": "uuid",
  "session_id": "string",
  "visitor_id": "string",
  "exit_outcome": "forward | backward | bounce | close",
  "next_step_id": "uuid (optional, for forward exits)"
}
```

**Acceptance Criteria:**
- Drop-off identified for bounce exits
- Progression mapped for forward exits

### REQ-FUN-004-05: Get Funnel Overview Analytics (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/analytics/funnels/{id}/overview,
**THEN** the system shall return aggregated funnel performance metrics,
**RESULTING IN** 200 status with analytics object,
**IN STATE** analytics_retrieved.

**Query Parameters:**
- date_from: ISO8601 (required)
- date_to: ISO8601 (required)

**Response 200:**
```json
{
  "funnel_id": "uuid",
  "funnel_name": "string",
  "period": {
    "start": "ISO8601",
    "end": "ISO8601"
  },
  "visitors": {
    "total": "integer",
    "unique": "integer",
    "new": "integer",
    "returning": "integer"
  },
  "conversions": {
    "total": "integer",
    "rate": "decimal",
    "value_cents": "integer"
  },
  "revenue": {
    "total_cents": "integer",
    "per_visitor_cents": "integer",
    "per_conversion_cents": "integer"
  },
  "steps": [
    {
      "step_id": "uuid",
      "step_name": "string",
      "step_type": "string",
      "visitors": "integer",
      "entries": "integer",
      "exits": "integer",
      "drop_offs": "integer",
      "drop_off_rate": "decimal",
      "avg_time_seconds": "integer",
      "conversion_rate": "decimal"
    }
  ]
}
```

**Acceptance Criteria:**
- Date range limited to max 1 year
- Cached results for repeated queries
- Returns 404 if funnel not found

### REQ-FUN-004-06: Get Funnel Step Analytics (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/analytics/funnels/{id}/steps/{step_id},
**THEN** the system shall return detailed step metrics,
**RESULTING IN** 200 status with step analytics,
**IN STATE** step_analytics_retrieved.

**Query Parameters:**
- date_from: ISO8601 (required)
- date_to: ISO8601 (required)
- granularity: string (default: day, options: hour, day, week)

**Response 200:**
```json
{
  "step_id": "uuid",
  "step_name": "string",
  "period": {"start": "ISO8601", "end": "ISO8601"},
  "summary": {
    "visitors": "integer",
    "unique_visitors": "integer",
    "entries": "integer",
    "exits": "integer",
    "drop_offs": "integer",
    "drop_off_rate": "decimal",
    "avg_time_seconds": "integer",
    "median_time_seconds": "integer"
  },
  "over_time": [
    {
      "timestamp": "ISO8601",
      "visitors": "integer",
      "entries": "integer",
      "exits": "integer",
      "drop_off_rate": "decimal",
      "avg_time_seconds": "integer"
    }
  ],
  "traffic_sources": [
    {
      "source": "string",
      "visitors": "integer",
      "percentage": "decimal"
    }
  ],
  "devices": [
    {
      "device_type": "desktop | mobile | tablet",
      "visitors": "integer",
      "percentage": "decimal"
    }
  ],
  "browsers": ["array"],
  "entry_paths": [
    {
      "previous_step_id": "uuid or null (direct entry)",
      "count": "integer"
    }
  ],
  "exit_paths": [
    {
      "next_step_id": "uuid or null (exit)",
      "count": "integer"
    }
  ]
}
```

**Acceptance Criteria:**
- Time-series data grouped by granularity
- Top 10 sources/devices/browsers
- All paths shown

### REQ-FUN-004-07: Get Conversion Metrics (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/analytics/funnels/{id}/conversions,
**THEN** the system shall return conversion analytics,
**RESULTING IN** 200 status with conversion metrics,
**IN STATE** conversion_metrics_retrieved.

**Query Parameters:**
- date_from, date_to, granularity

**Response 200:**
```json
{
  "period": {"start": "ISO8601", "end": "ISO8601"},
  "summary": {
    "total_conversions": "integer",
    "conversion_rate": "decimal",
    "total_value_cents": "integer",
    "avg_value_cents": "integer"
  },
  "by_type": [
    {
      "conversion_type": "string",
      "count": "integer",
      "rate": "decimal",
      "value_cents": "integer"
    }
  ],
  "by_step": [
    {
      "step_id": "uuid",
      "step_name": "string",
      "conversions": "integer",
      "conversion_rate": "decimal"
    }
  ],
  "over_time": [
    {
      "timestamp": "ISO8601",
      "conversions": "integer",
      "rate": "decimal",
      "value_cents": "integer"
    }
  ],
  "converting_visitors": [
    {
      "visitor_id": "uuid",
      "session_id": "string",
      "conversions": "integer",
      "total_value_cents": "integer",
      "first_conversion_at": "ISO8601",
      "last_conversion_at": "ISO8601"
    }
  ]
}
```

**Acceptance Criteria:**
- Conversion types: form_submit, purchase, signup, custom
- Pagination for converting_visitors (page, page_size)

### REQ-FUN-004-08: Get Drop-off Analysis (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/analytics/funnels/{id}/dropoffs,
**THEN** the system shall return drop-off analysis with insights,
**RESULTING IN** 200 status with drop-off report,
**IN STATE** dropoff_analysis_retrieved.

**Response 200:**
```json
{
  "period": {"start": "ISO8601", "end": "ISO8601"},
  "overall_drop_off_rate": "decimal",
  "steps_with_drop_off": [
    {
      "step_id": "uuid",
      "step_name": "string",
      "drop_offs": "integer",
      "drop_off_rate": "decimal",
      "severity": "low | medium | high",
      "common_exit_reasons": [
        {
          "reason": "string",
          "count": "integer",
          "percentage": "decimal"
        }
      ],
      "suggestions": ["array of improvement suggestions"]
    }
  ],
  "drop_off_funnel": [
    {
      "step_id": "uuid",
      "step_name": "string",
      "visitors": "integer",
      "drop_offs": "integer",
      "cumulative_drop_off_rate": "decimal"
    }
  ]
}
```

**Acceptance Criteria:**
- Severity based on drop-off rate thresholds
- Suggestions generated algorithmically
- Cumulative rate shows total loss to that point

### REQ-FUN-004-09: Get A/B Test Results (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/analytics/funnels/{id}/ab-tests,
**THEN** the system shall return A/B test performance comparison,
**RESULTING IN** 200 status with test results,
**IN STATE** ab_test_results_retrieved.

**Query Parameters:**
- test_id: uuid (optional, specific test)
- date_from, date_to

**Response 200:**
```json
{
  "tests": [
    {
      "test_id": "uuid",
      "test_name": "string",
      "status": "running | completed | stopped",
      "started_at": "ISO8601",
      "completed_at": "ISO8601 or null",
      "variants": [
        {
          "variant_id": "uuid",
          "variant_name": "string",
          "is_control": "boolean",
          "visitors": "integer",
          "conversions": "integer",
          "conversion_rate": "decimal",
          "revenue_cents": "integer",
          "avg_revenue_per_visitor_cents": "integer",
          "improvement_vs_control": "decimal or null",
          "confidence": "decimal (statistical significance)"
        }
      ],
      "winner": {
        "variant_id": "uuid",
        "reason": "string"
      }
    }
  ]
}
```

**Acceptance Criteria:**
- Statistical significance calculated (95% confidence)
- Winner declared only if significant
- Returns empty array if no tests

### REQ-FUN-004-10: Get Revenue Metrics (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/analytics/funnels/{id}/revenue,
**THEN** the system shall return revenue analytics,
**RESULTING IN** 200 status with revenue metrics,
**IN STATE** revenue_metrics_retrieved.

**Query Parameters:**
- date_from, date_to, granularity

**Response 200:**
```json
{
  "period": {"start": "ISO8601", "end": "ISO8601"},
  "summary": {
    "total_revenue_cents": "integer",
    "revenue_per_visitor_cents": "integer",
    "revenue_per_conversion_cents": "integer",
    "refund_rate": "decimal",
    "net_revenue_cents": "integer"
  },
  "by_source": [
    {
      "source": "string",
      "revenue_cents": "integer",
      "percentage": "decimal"
    }
  ],
  "by_step": [
    {
      "step_id": "uuid",
      "step_name": "string",
      "revenue_cents": "integer",
      "orders": "integer",
      "avg_order_value_cents": "integer"
    }
  ],
  "over_time": [
    {
      "timestamp": "ISO8601",
      "revenue_cents": "integer",
      "orders": "integer",
      "avg_order_value_cents": "integer"
    }
  ],
  "top_products": [
    {
      "product_id": "uuid",
      "product_name": "string",
      "revenue_cents": "integer",
      "units_sold": "integer"
    }
  ]
}
```

**Acceptance Criteria:**
- Net revenue = total - refunds
- Top products limited to 20

### REQ-FUN-004-11: Get Real-Time Analytics (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/analytics/funnels/{id}/realtime,
**THEN** the system shall return current active visitors and events,
**RESULTING IN** 200 status with real-time data,
**IN STATE** realtime_data_retrieved.

**Response 200:**
```json
{
  "funnel_id": "uuid",
  "timestamp": "ISO8601",
  "active_visitors": {
    "total": "integer",
    "by_step": [
      {
        "step_id": "uuid",
        "step_name": "string",
        "visitors": "integer"
      }
    ]
  },
  "recent_events": [
    {
      "event_type": "string",
      "step_id": "uuid or null",
      "timestamp": "ISO8601",
      "session_id": "string"
    }
  ],
  "conversions_last_5min": {
    "count": "integer",
    "value_cents": "integer"
  }
}
```

**Acceptance Criteria:**
- Active visitors: last 30 minutes
- Recent events: last 50 events
- Data cached in Redis (5-second TTL)

### REQ-FUN-004-12: Export Analytics Data (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/analytics/export,
**THEN** the system shall generate export file with analytics data,
**RESULTING IN** 202 for background job or 200 with file,
**IN STATE** export_initiated.

**Request Body:**
```json
{
  "funnel_id": "uuid",
  "report_type": "overview | conversions | dropoffs | revenue",
  "date_from": "ISO8601",
  "date_to": "ISO8601",
  "format": "csv | xlsx | pdf",
  "include_charts": "boolean (for pdf)"
}
```

**Response 202:**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "estimated_completion": "ISO8601"
}
```

**Acceptance Criteria:**
- Background job for all exports
- Email notification when ready
- Download link valid for 24 hours
- Returns 400 if invalid report type

### REQ-FUN-004-13: Get Visitor Journey (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/analytics/visitors/{visitor_id}/journey,
**THEN** the system shall return complete visitor session history,
**RESULTING IN** 200 status with journey data,
**IN STATE** journey_retrieved.

**Query Parameters:**
- funnel_id: uuid (optional, filter by funnel)

**Response 200:**
```json
{
  "visitor_id": "uuid",
  "first_seen_at": "ISO8601",
  "last_seen_at": "ISO8601",
  "total_sessions": "integer",
  "total_page_views": "integer",
  "total_conversions": "integer",
  "sessions": [
    {
      "session_id": "string",
      "started_at": "ISO8601",
      "ended_at": "ISO8601 or null",
      "funnel_id": "uuid",
      "entry_page": "string",
      "exit_page": "string or null",
      "page_views": "integer",
      "time_spent_seconds": "integer",
      "conversions": "integer",
      "events": [
        {
          "event_type": "string",
          "page_id": "uuid or null",
          "step_id": "uuid or null",
          "timestamp": "ISO8601",
          "metadata": "object"
        }
      ]
    }
  ]
}
```

**Acceptance Criteria:**
- GDPR compliance: anonymize after consent withdrawn
- Returns 404 if visitor not found

---

## Technical Specifications

### Database Schema

```sql
-- Analytics events table (time-series, partitioned)
CREATE TABLE analytics_events (
    id UUID DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL,
    funnel_id UUID NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    visitor_id UUID NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    page_id UUID,
    funnel_step_id UUID,
    conversion_type VARCHAR(50),
    value_cents INTEGER,
    conversion_goal_id UUID,
    url TEXT,
    user_agent TEXT,
    ip_address INET,
    referrer TEXT,
    utm_source VARCHAR(255),
    utm_medium VARCHAR(255),
    utm_campaign VARCHAR(255),
    exit_outcome VARCHAR(20),
    next_step_id UUID,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Create partitions for each month
CREATE TABLE analytics_events_2025_01 PARTITION OF analytics_events
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE INDEX idx_analytics_events_account_funnel ON analytics_events(account_id, funnel_id);
CREATE INDEX idx_analytics_events_visitor_id ON analytics_events(visitor_id);
CREATE INDEX idx_analytics_events_session_id ON analytics_events(session_id);
CREATE INDEX idx_analytics_events_created_at ON analytics_events(created_at);
CREATE INDEX idx_analytics_events_type ON analytics_events(event_type);

-- Aggregate materialized views for performance
CREATE MATERIALIZED VIEW funnel_step_stats AS
SELECT
    funnel_id,
    funnel_step_id,
    DATE_TRUNC('day', created_at) as date,
    COUNT(DISTINCT visitor_id) as unique_visitors,
    COUNT(*) FILTER (WHERE event_type = 'step_entry') as entries,
    COUNT(*) FILTER (WHERE event_type = 'step_exit') as exits,
    COUNT(*) FILTER (WHERE event_type = 'step_exit' AND exit_outcome = 'bounce') as drop_offs,
    AVG(EXTRACT(EPOCH FROM (LEAD(created_at) OVER (PARTITION BY session_id ORDER BY created_at) - created_at))) as avg_time_seconds
FROM analytics_events
WHERE event_type IN ('step_entry', 'step_exit')
GROUP BY funnel_id, funnel_step_id, DATE_TRUNC('day', created_at);

CREATE UNIQUE INDEX idx_funnel_step_stats_lookup ON funnel_step_stats(funnel_id, funnel_step_id, date);
CREATE INDEX idx_funnel_step_stats_date ON funnel_step_stats(date);

-- Refresh materialized view
CREATE OR REPLACE FUNCTION refresh_step_stats()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY funnel_step_stats;
END;
$$ LANGUAGE plpgsql;

-- A/B test variants table
CREATE TABLE ab_test_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_id UUID NOT NULL REFERENCES ab_tests(id) ON DELETE CASCADE,
    variant_name VARCHAR(100) NOT NULL,
    is_control BOOLEAN NOT NULL DEFAULT FALSE,
    page_id UUID REFERENCES pages(id),
    config JSONB NOT NULL DEFAULT '{}',
    traffic_split INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ab_test_variants_test_id ON ab_test_variants(test_id);

-- A/B tests table
CREATE TABLE ab_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id),
    funnel_id UUID NOT NULL REFERENCES funnels(id),
    test_name VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'running',
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    winner_variant_id UUID REFERENCES ab_test_variants(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ab_tests_account_id ON ab_tests(account_id);
CREATE INDEX idx_ab_tests_funnel_id ON ab_tests(funnel_id);
```

### API Endpoints Summary

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/analytics/track | Track analytics event |
| GET | /api/v1/analytics/funnels/{id}/overview | Funnel overview |
| GET | /api/v1/analytics/funnels/{id}/steps/{step_id} | Step analytics |
| GET | /api/v1/analytics/funnels/{id}/conversions | Conversion metrics |
| GET | /api/v1/analytics/funnels/{id}/dropoffs | Drop-off analysis |
| GET | /api/v1/analytics/funnels/{id}/ab-tests | A/B test results |
| GET | /api/v1/analytics/funnels/{id}/revenue | Revenue metrics |
| GET | /api/v1/analytics/funnels/{id}/realtime | Real-time data |
| POST | /api/v1/analytics/export | Export analytics |
| GET | /api/v1/analytics/visitors/{visitor_id}/journey | Visitor journey |

**Total Endpoints: 10**

---

## Constraints

### Technical Constraints

- Event tracking: Async processing with queue
- Materialized views refreshed every 5 minutes
- Real-time data cached in Redis (5-second TTL)
- Partition retention: 13 months rolling

### Business Constraints

- Date range max: 1 year for reports
- Real-time window: last 30 minutes
- Export retention: 24 hours

### Performance Constraints

- Tracking endpoint: < 100ms (async response)
- Overview query: < 2000ms for 1-year range
- Real-time query: < 500ms (cached)
- Export generation: < 5 minutes for 1-year data

---

## Dependencies

### Internal Dependencies

| Module | Dependency Type | Description |
|--------|-----------------|-------------|
| Funnels Module | Hard | Analytics for funnels |
| Pages Module | Hard | Page view tracking |
| Orders Module | Soft | Revenue/conversion tracking |

### External Dependencies

| Service | Purpose |
|---------|---------|
| Redis | Real-time caching |
| TimescaleDB | Time-series optimization |

---

## Related SPECs

| SPEC ID | Title | Relationship |
|---------|-------|--------------|
| SPEC-FUN-001 | Funnel Builder | Analytics for funnels |
| SPEC-FUN-002 | Pages & Elements | Page analytics |
| SPEC-FUN-003 | Orders & Payments | Revenue tracking |

---

## Traceability Tags

- TAG:SPEC-FUN-004
- TAG:MODULE-FUNNELS-ANALYTICS
- TAG:DOMAIN-ANALYTICS-REPORTING
- TAG:PRIORITY-HIGH
- TAG:API-REST
- TAG:TIME-SERIES-DATA
- TAG:DDD-IMPLEMENTATION
