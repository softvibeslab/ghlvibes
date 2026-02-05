# SPEC-WFL-011: Implementation Plan

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-011 |
| **Title** | Bulk Enrollment |
| **Module** | workflows |
| **Domain** | automation |
| **Priority** | Medium |

---

## Implementation Strategy

### Development Approach

This implementation follows Domain-Driven Development (DDD) with the ANALYZE-PRESERVE-IMPROVE cycle:

1. **ANALYZE**: Understand existing workflow enrollment patterns and contact management
2. **PRESERVE**: Create characterization tests for existing enrollment handlers
3. **IMPROVE**: Implement bulk enrollment with async processing and comprehensive testing

---

## Milestones

### Milestone 1: Core Infrastructure (Primary Goal)

**Objective**: Establish bulk enrollment service foundation with database schema and job management

**Tasks**:
1. Create database migrations for bulk enrollment tables
2. Implement `BulkEnrollmentService` class with job lifecycle management
3. Create Pydantic models for request/response validation
4. Set up Redis data structures for queue and progress tracking
5. Implement job creation and validation logic

**Deliverables**:
- `/src/backend/domain/workflows/services/bulk_enrollment_service.py`
- `/src/backend/domain/workflows/models/bulk_enrollment.py`
- `/src/backend/infrastructure/database/migrations/xxx_add_bulk_enrollment_tables.py`
- `/src/backend/domain/workflows/repositories/bulk_enrollment_repo.py`
- Unit tests with 85%+ coverage

**Dependencies**: None (starting point)

### Milestone 2: Contact Selection & Validation (Primary Goal)

**Objective**: Implement multi-mode contact selection with comprehensive validation

**Tasks**:
1. Create manual contact ID selection handler
2. Implement filter-based contact resolution
3. Build CSV upload and parsing system
4. Create contact eligibility validator
5. Implement duplicate detection logic

**Deliverables**:
- `/src/backend/domain/workflows/services/contact_selector.py`
- `/src/backend/domain/workflows/services/contact_validator.py`
- `/src/backend/domain/workflows/utils/csv_parser.py`
- `/src/backend/api/v1/workflows/bulk_enrollment_validation.py`
- Integration tests for all selection modes

**Dependencies**: Milestone 1

### Milestone 3: Queue & Batch Processing (Secondary Goal)

**Objective**: Implement Redis-based queue with Celery workers for batch processing

**Tasks**:
1. Create batch queue manager with Redis
2. Implement Celery worker tasks for batch processing
3. Build batch retry mechanism with exponential backoff
4. Create worker pool management
5. Implement rate limiting per account

**Deliverables**:
- `/src/backend/domain/workflows/workers/batch_processor.py`
- `/src/backend/infrastructure/queue/bulk_enrollment_queue.py`
- `/src/backend/infrastructure/rate_limiter.py`
- `/src/backend/domain/workflows/services/batch_retry_handler.py`
- Load tests for concurrent batch processing

**Dependencies**: Milestones 1, 2

### Milestone 4: Progress Tracking & Broadcasting (Secondary Goal)

**Objective**: Implement real-time progress tracking with WebSocket broadcasting

**Tasks**:
1. Create progress tracker with Redis storage
2. Implement WebSocket endpoint for progress updates
3. Build progress calculation utilities
4. Create completion notification service
5. Implement job history and reporting

**Deliverables**:
- `/src/backend/domain/workflows/services/progress_tracker.py`
- `/src/backend/api/v1/websockets/bulk_enrollment_progress.py`
- `/src/backend/domain/workflows/services/notification_service.py`
- `/src/backend/domain/workflows/services/report_generator.py`
- WebSocket integration tests

**Dependencies**: Milestones 1, 2, 3

### Milestone 5: API Endpoints (Secondary Goal)

**Objective**: Create REST API for bulk enrollment management

**Tasks**:
1. Implement bulk enrollment CRUD endpoints
2. Create progress and status endpoints
3. Build failure listing and retry endpoints
4. Add dry-run validation endpoint
5. Implement cancellation endpoint

**Deliverables**:
- `/src/backend/api/v1/workflows/bulk_enrollment.py`
- `/src/backend/api/v1/bulk_enrollment_jobs.py`
- OpenAPI documentation updates
- API integration tests

**Dependencies**: Milestones 1, 2, 3, 4

### Milestone 6: Workflow Integration (Final Goal)

**Objective**: Integrate bulk enrollment with workflow execution engine

**Tasks**:
1. Create bulk enrollment action handler
2. Integrate with existing workflow enrollment logic
3. Add bulk enrollment to workflow analytics
4. Create UI components for bulk enrollment trigger
5. Implement end-to-end workflow tests

**Deliverables**:
- `/src/backend/domain/workflows/handlers/bulk_enrollment_handler.py`
- Updated workflow execution engine
- End-to-end integration tests
- Performance benchmarks

**Dependencies**: Milestones 1, 2, 3, 4, 5

---

## Technical Approach

### Architecture Overview

```
src/backend/
├── api/v1/
│   ├── workflows/
│   │   ├── bulk_enrollment.py        # Job management endpoints
│   │   └── bulk_enrollment_validation.py  # Validation endpoints
│   ├── bulk_enrollment_jobs.py       # Job listing and details
│   └── websockets/
│       └── bulk_enrollment_progress.py  # Real-time progress
├── domain/workflows/
│   ├── models/
│   │   └── bulk_enrollment.py        # Pydantic models
│   ├── services/
│   │   ├── bulk_enrollment_service.py   # Core service
│   │   ├── contact_selector.py       # Contact selection logic
│   │   ├── contact_validator.py      # Eligibility validation
│   │   ├── progress_tracker.py       # Progress management
│   │   ├── batch_retry_handler.py    # Retry logic
│   │   └── notification_service.py   # Completion notifications
│   ├── workers/
│   │   └── batch_processor.py        # Celery worker tasks
│   ├── handlers/
│   │   └── bulk_enrollment_handler.py   # Workflow integration
│   ├── repositories/
│   │   └── bulk_enrollment_repo.py   # Database operations
│   └── utils/
│       └── csv_parser.py             # CSV processing
├── infrastructure/
│   ├── queue/
│   │   └── bulk_enrollment_queue.py  # Redis queue management
│   └── rate_limiter.py               # Rate limiting
└── core/
    └── websocket_manager.py          # WebSocket broadcast
```

### Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Task Queue | Celery + Redis | Reliable async processing, retry support |
| Progress Storage | Redis | Low-latency real-time updates |
| Database | PostgreSQL/Supabase | ACID compliance, JSONB flexibility |
| WebSocket | FastAPI WebSockets | Native async support, integrated auth |
| File Processing | pandas | Efficient CSV parsing for large files |
| Rate Limiting | Redis + Lua | Atomic operations, sliding window |

### Key Design Decisions

1. **Asynchronous Job Processing**
   - Jobs created immediately, processing deferred to workers
   - Non-blocking API responses for large enrollments
   - Scalable worker pool for parallel processing

2. **Batch-Based Processing**
   - Fixed batch size (100) for predictable processing time
   - Independent batch retries without full job restart
   - Progress tracked at batch level for granular updates

3. **Redis for Real-Time State**
   - Progress stored in Redis for sub-100ms reads
   - WebSocket broadcasts triggered on Redis pub/sub
   - Rate limiting with atomic Lua scripts

4. **Graceful Failure Handling**
   - Individual failures do not stop batch processing
   - Batch failures trigger automatic retry
   - Job continues with partial success

5. **Separation of Concerns**
   - Selection, validation, and enrollment are independent services
   - Each service has dedicated tests and error handling
   - Enables future enhancements (new selection modes)

---

## Risk Assessment

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Database deadlocks during high concurrency | Medium | High | Row-level locking, batch isolation |
| Memory exhaustion with large CSV files | Medium | High | Streaming CSV parser, file size limits |
| Redis connection failures | Low | High | Connection pooling, fallback to DB |
| Worker starvation under load | Medium | Medium | Dynamic worker scaling, monitoring |

### Operational Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Runaway bulk jobs consuming resources | Medium | High | Per-account limits, admin controls |
| Data inconsistency on partial failures | Low | High | Transaction boundaries, reconciliation jobs |
| WebSocket connection overload | Low | Medium | Connection limits, message batching |

---

## Quality Gates

### Code Quality

- [ ] 85%+ test coverage for all new code
- [ ] Zero Pyright type errors
- [ ] Zero Ruff linting errors
- [ ] All endpoints documented in OpenAPI
- [ ] Security review completed

### Performance Benchmarks

- [ ] 10,000 contact job completes in < 15 minutes
- [ ] Progress updates delivered in < 100ms
- [ ] API response time < 500ms for job creation
- [ ] Database queries < 50ms (p95)
- [ ] System stable with 5 concurrent bulk jobs

### Integration Criteria

- [ ] All acceptance tests passing
- [ ] End-to-end workflow enrollment works
- [ ] Retry mechanism validated
- [ ] WebSocket progress updates verified
- [ ] Rate limiting enforced correctly

---

## Definition of Done

1. All EARS requirements implemented and tested
2. Acceptance criteria verified (see acceptance.md)
3. Code reviewed and approved
4. Documentation complete (API, architecture)
5. Performance benchmarks met
6. Security review passed
7. Load testing completed successfully
8. Deployed to staging environment
9. Product owner sign-off

---

## Traceability

| Tag | Reference |
|-----|-----------|
| SPEC-WFL-011 | Parent specification |
| PLAN-WFL-011-M1 | Milestone 1: Core Infrastructure |
| PLAN-WFL-011-M2 | Milestone 2: Contact Selection |
| PLAN-WFL-011-M3 | Milestone 3: Queue Processing |
| PLAN-WFL-011-M4 | Milestone 4: Progress Tracking |
| PLAN-WFL-011-M5 | Milestone 5: API Endpoints |
| PLAN-WFL-011-M6 | Milestone 6: Workflow Integration |
