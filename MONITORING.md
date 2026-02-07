# Monitoring and Logging Setup

Comprehensive monitoring and logging configuration for GoHighLevel Clone production deployment.

## Table of Contents

- [Overview](#overview)
- [Health Check System](#health-check-system)
- [Application Logging](#application-logging)
- [Performance Monitoring](#performance-monitoring)
- [Error Tracking](#error-tracking)
- [Alerting](#alerting)
- [Log Aggregation](#log-aggregation)
- [Metrics Collection](#metrics-collection)

## Overview

The monitoring system provides:

- **Health Checks**: Real-time service health monitoring
- **Structured Logging**: JSON-formatted logs for easy parsing
- **Performance Metrics**: Response times, throughput, resource usage
- **Error Tracking**: Automatic error capture and notification
- **Alerting**: Proactive notification of issues

## Health Check System

### Health Check Endpoints

**Primary Health Check**: `GET /health`

Returns comprehensive health status:

```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2026-02-07T12:00:00Z"
}
```

**Liveness Probe**: `GET /health/live`

Basic liveness check (always returns 200 if API is running):

```json
{
  "status": "alive"
}
```

**Readiness Probe**: `GET /health/ready`

Checks if all dependencies are ready:

```json
{
  "status": "ready"
}
```

### Platform-Specific Health Checks

**Railway (Backend)**:
- Configured in `railway.toml`
- Health check path: `/health`
- Check interval: 30 seconds
- Timeout: 30 seconds
- Restart policy: ON_FAILURE

**Vercel (Frontend)**:
- Automatic health checks
- Edge function monitoring
- Deployment health verification

### Monitoring Health Checks

**Manual Check**:
```bash
# Check backend health
curl https://api.gohighlevel-clone.railway.app/health

# Check with timing
curl -w "@curl-format.txt" https://api.gohighlevel-clone.railway.app/health
```

**Automated Monitoring**:
- Uptime monitoring (UptimeRobot, Pingdom)
- Synthetic transactions
- API endpoint monitoring

**Create curl-format.txt**:
```txt
time_namelookup: %{time_namelookup}\n
time_connect: %{time_connect}\n
time_appconnect: %{time_appconnect}\n
time_pretransfer: %{time_pretransfer}\n
time_starttransfer: %{time_starttransfer}\n
time_total: %{time_total}\n
http_code: %{http_code}\n
```

## Application Logging

### Logging Configuration

**Structured JSON Logging** (recommended for production):

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if present
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        return json.dumps(log_data)

# Configure logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Log Levels

**DEBUG**: Detailed diagnostic information
```python
logger.debug("Database query executed", extra={
    "query": "SELECT * FROM users",
    "duration_ms": 15
})
```

**INFO**: General informational messages
```python
logger.info("User logged in", extra={
    "user_id": 123,
    "ip_address": "192.168.1.1"
})
```

**WARNING**: Warning conditions
```python
logger.warning("High memory usage", extra={
    "usage_percent": 85,
    "threshold": 80
})
```

**ERROR**: Error events
```python
logger.error("Database connection failed", extra={
    "error": str(e),
    "retry_attempt": 3
})
```

**CRITICAL**: Critical failures
```python
logger.critical("Service unavailable", extra={
    "error": "Database connection pool exhausted",
    "impact": "All requests failing"
})
```

### Logging Best Practices

**DO**:
- Use structured logging with extra fields
- Include request_id for traceability
- Log user_id for auditing
- Use appropriate log levels
- Log security-relevant events

**DON'T**:
- Log sensitive data (passwords, tokens)
- Log excessive DEBUG in production
- Log in hot loops (high-frequency)
- Use print() statements

## Performance Monitoring

### Key Metrics

**API Performance**:
- Response time (P50, P95, P99)
- Request rate (requests/second)
- Error rate (percentage)
- Throughput (requests/minute)

**Database Performance**:
- Query execution time
- Connection pool usage
- Slow query log
- Transaction rate

**Cache Performance**:
- Cache hit rate
- Cache miss rate
- Response time
- Memory usage

**Resource Usage**:
- CPU utilization
- Memory utilization
- Disk I/O
- Network I/O

### Monitoring Tools

**Railway Metrics**:
- Built-in metrics dashboard
- CPU, memory usage
- Request/response metrics
- Deployment history

**Vercel Analytics**:
- Web Vitals (LCP, FID, CLS)
- Page views
- Top pages
- Geographic distribution

### Custom Metrics (Optional)

**Using Prometheus**:
```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

active_connections = Gauge(
    'active_connections',
    'Active database connections'
)

# Use in code
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response
```

## Error Tracking

### Sentry Integration (Optional)

**Backend Setup**:
```bash
pip install sentry-sdk
```

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1,
)
```

**Frontend Setup**:
```bash
npm install @sentry/nextjs
```

```javascript
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: "your-sentry-dsn",
  tracesSampleRate: 0.1,
});
```

### Error Categories

**Application Errors**:
- Unhandled exceptions
- Validation errors
- Business logic errors

**Infrastructure Errors**:
- Database connection failures
- Redis connection failures
- Network timeouts

**Integration Errors**:
- Third-party API failures
- Webhook failures
- Email sending failures

## Alerting

### Alert Conditions

**Critical Alerts** (immediate notification):
- API error rate > 10%
- Database connection failures
- Service downtime > 5 minutes
- Security incidents

**Warning Alerts** (hourly digest):
- API error rate > 5%
- Response time P95 > 1s
- High memory usage > 80%
- High CPU usage > 80%

**Info Alerts** (daily digest):
- Deployment completed
- SSL certificate expiry warning
- Cost spike detection

### Alert Channels

**Email**:
- On-call engineering team
- Platform-specific alerts

**Slack** (optional):
```yaml
# GitHub Actions workflow
- name: Slack Notification
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}
  if: failure()
```

**PagerDuty** (optional):
- Critical alerts only
- Escalation policies
- On-call rotation

## Log Aggregation

### Current Setup

**Platform Logs**:
- Railway: Built-in log viewer
- Vercel: Built-in log viewer
- GitHub Actions: Workflow logs

### External Log Aggregation (Optional)

**ELK Stack** (Elasticsearch, Logstash, Kibana):
- Centralized log storage
- Powerful search and filtering
- Custom dashboards

**Datadog**:
- Unified monitoring
- APM integration
- Infrastructure monitoring

**CloudWatch** (AWS):
- Log aggregation
- Metrics and alarms
- Lambda integration

### Log Retention

**Current**:
- Development: 7 days
- Staging: 30 days
- Production: 90 days

**Archive Strategy**:
- Compress logs older than 30 days
- Move to S3/Glacier for long-term storage
- Keep security logs for 1 year

## Metrics Collection

### Application Metrics

**Custom Middleware**:
```python
import time
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware to collect request metrics."""
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time
    duration_ms = int(duration * 1000)

    # Log metrics
    logger.info(
        "Request processed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        }
    )

    # Add response header
    response.headers["X-Response-Time"] = f"{duration_ms}ms"

    return response
```

### Database Metrics

**Slow Query Logging**:
```python
# In SQLAlchemy setup
event.listen(
    engine,
    "before_cursor_execute",
    receive_before_cursor_execute
)

def receive_before_cursor_execute(
    conn, cursor, statement, params, context, executemany
):
    context._query_start_time = time.time()

def receive_after_cursor_execute(
    conn, cursor, statement, params, context, executemany
):
    total = time.time() - context._query_start_time
    if total > 0.5:  # Log queries taking > 500ms
        logger.warning(
            "Slow query detected",
            extra={
                "query": statement,
                "duration_ms": int(total * 1000),
            }
        )
```

### Frontend Metrics

**Web Vitals** (automatic with Vercel):
- LCP (Largest Contentful Paint): < 2.5s
- FID (First Input Delay): < 100ms
- CLS (Cumulative Layout Shift): < 0.1

**Custom Metrics**:
```javascript
// Track custom performance events
export function trackEvent(name, properties) {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', name, properties);
  }
}

// Usage
trackEvent('workflow_created', {
  workflow_id: workflow.id,
  user_id: user.id
});
```

## Monitoring Dashboard

### Recommended Dashboards

**System Health Dashboard**:
- CPU usage
- Memory usage
- Disk I/O
- Network I/O
- Uptime status

**Application Dashboard**:
- Request rate
- Response times (P50, P95, P99)
- Error rate
- Active connections
- Cache hit rate

**Business Metrics Dashboard**:
- Active users
- Workflows created
- Actions executed
- Bulk enrollments processed

## Troubleshooting Guide

### High Response Times

**Check**:
1. Database query performance
2. Network latency
3. Resource utilization
4. Cache hit rate

**Solutions**:
1. Optimize slow queries
2. Add database indexes
3. Increase cache TTL
4. Scale horizontally

### High Error Rate

**Check**:
1. Recent deployments
2. Third-party API status
3. Database connectivity
4. Resource exhaustion

**Solutions**:
1. Rollback deployment
2. Restart affected services
3. Scale resources
4. Implement circuit breakers

### Memory Leaks

**Check**:
1. Memory usage trends
2. Connection pools
3. Caching strategies
4. Background tasks

**Solutions**:
1. Restart services
2. Reduce cache size
3. Optimize connection pooling
4. Profile memory usage

## Best Practices

1. **Monitor Everything**: If you can't measure it, you can't improve it
2. **Set Up Alerts**: Proactive notification beats reactive debugging
3. **Use Structured Logging**: JSON logs are easier to parse and analyze
4. **Correlate Logs**: Use request_id to trace requests across services
5. **Review Metrics Regularly**: Weekly reviews catch issues early
6. **Test Monitoring**: Verify alerts work before you need them
7. **Document Incidents**: Learn from failures and improve

## Additional Resources

- [Railway Monitoring](https://docs.railway.app/guides/monitoring)
- [Vercel Analytics](https://vercel.com/docs/analytics)
- [Sentry Documentation](https://docs.sentry.io)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)

---

Last Updated: 2026-02-07
