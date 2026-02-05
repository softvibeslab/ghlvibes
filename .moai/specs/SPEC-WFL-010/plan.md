# SPEC-WFL-010: Implementation Plan

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-010 |
| **Title** | Webhook Integration |
| **Module** | workflows |
| **Domain** | automation |
| **Priority** | High |

---

## Implementation Strategy

### Development Approach

This implementation follows Domain-Driven Development (DDD) with the ANALYZE-PRESERVE-IMPROVE cycle:

1. **ANALYZE**: Understand existing workflow action architecture
2. **PRESERVE**: Create characterization tests for existing action handlers
3. **IMPROVE**: Implement webhook action with full test coverage

---

## Milestones

### Milestone 1: Core Infrastructure (Primary Goal)

**Objective**: Establish webhook service foundation with HTTP client pool

**Tasks**:
1. Create `WebhookService` class with async HTTP client
2. Implement HTTP client connection pooling with httpx
3. Create webhook configuration Pydantic models
4. Set up database migrations for webhook tables
5. Implement URL validation and security checks

**Deliverables**:
- `/src/backend/domain/workflows/services/webhook_service.py`
- `/src/backend/domain/workflows/models/webhook.py`
- `/src/backend/infrastructure/database/migrations/xxx_add_webhook_tables.py`
- Unit tests with 85%+ coverage

**Dependencies**: None (starting point)

### Milestone 2: Authentication & Security (Primary Goal)

**Objective**: Implement secure authentication handling for webhooks

**Tasks**:
1. Implement authentication type handlers (none, basic, bearer, api_key)
2. Create credential encryption/decryption utilities
3. Implement private IP blocking and URL sanitization
4. Add merge field interpolation with XSS prevention
5. Create SSL/TLS verification handling

**Deliverables**:
- `/src/backend/domain/workflows/services/webhook_auth.py`
- `/src/backend/core/security/credential_manager.py`
- `/src/backend/domain/workflows/utils/url_validator.py`
- Integration tests for all auth types

**Dependencies**: Milestone 1

### Milestone 3: Retry & Error Handling (Secondary Goal)

**Objective**: Implement resilient retry mechanism with circuit breaker

**Tasks**:
1. Create retry handler with exponential backoff
2. Implement circuit breaker pattern for failing endpoints
3. Build error classification system
4. Create webhook execution logging
5. Implement rate limiting per account/endpoint

**Deliverables**:
- `/src/backend/domain/workflows/services/webhook_retry.py`
- `/src/backend/infrastructure/circuit_breaker.py`
- `/src/backend/domain/workflows/repositories/webhook_execution_repo.py`
- Stress tests for retry scenarios

**Dependencies**: Milestones 1, 2

### Milestone 4: API Endpoints (Secondary Goal)

**Objective**: Create REST API for webhook configuration and monitoring

**Tasks**:
1. Implement webhook CRUD endpoints
2. Create webhook test endpoint
3. Build execution log listing with pagination
4. Add OpenAPI documentation
5. Implement request/response validation

**Deliverables**:
- `/src/backend/api/v1/workflows/webhooks.py`
- `/src/backend/api/v1/webhook_executions.py`
- API integration tests
- OpenAPI schema updates

**Dependencies**: Milestones 1, 2, 3

### Milestone 5: Workflow Integration (Final Goal)

**Objective**: Integrate webhook action into workflow execution engine

**Tasks**:
1. Create webhook action handler for workflow engine
2. Implement response data mapping to contact fields
3. Add webhook action to workflow builder UI actions
4. Create workflow execution context integration
5. Build analytics and monitoring dashboards

**Deliverables**:
- `/src/backend/domain/workflows/handlers/webhook_action_handler.py`
- `/src/backend/domain/workflows/services/response_mapper.py`
- End-to-end integration tests
- Performance benchmarks

**Dependencies**: Milestones 1, 2, 3, 4

---

## Technical Approach

### Architecture Overview

```
src/backend/
├── api/v1/
│   ├── workflows/
│   │   └── webhooks.py          # Webhook CRUD endpoints
│   └── webhook_executions.py     # Execution log endpoints
├── domain/workflows/
│   ├── models/
│   │   └── webhook.py           # Pydantic models
│   ├── services/
│   │   ├── webhook_service.py   # Core webhook execution
│   │   ├── webhook_auth.py      # Authentication handlers
│   │   └── webhook_retry.py     # Retry logic
│   ├── handlers/
│   │   └── webhook_action_handler.py  # Workflow integration
│   ├── repositories/
│   │   └── webhook_repo.py      # Database operations
│   └── utils/
│       └── url_validator.py     # URL security validation
├── infrastructure/
│   ├── http_client.py           # Async HTTP client pool
│   └── circuit_breaker.py       # Circuit breaker implementation
└── core/security/
    └── credential_manager.py    # Encrypted credential handling
```

### Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| HTTP Client | httpx | Async support, connection pooling, HTTP/2 |
| Validation | Pydantic v2 | Type safety, JSON schema generation |
| Database | PostgreSQL/Supabase | JSONB support for flexible configs |
| Caching | Redis | Rate limiting, circuit breaker state |
| Queue | Celery/Redis | Async retry processing |
| Encryption | cryptography | AES-256 credential encryption |

### Key Design Decisions

1. **Async-First Architecture**
   - All webhook calls use async/await
   - Connection pooling reduces latency
   - Non-blocking execution preserves workflow throughput

2. **Circuit Breaker Pattern**
   - Prevents cascading failures from bad endpoints
   - Automatic recovery when endpoint stabilizes
   - Per-endpoint tracking with Redis

3. **Credential Isolation**
   - Per-account encryption keys
   - Credentials never in logs or error messages
   - Secure memory handling for sensitive data

4. **Merge Field Security**
   - HTML/script escaping by default
   - URL encoding for path/query parameters
   - JSON escaping for payload values

---

## Risk Assessment

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Webhook endpoint unavailable | High | Medium | Retry mechanism with exponential backoff |
| Memory exhaustion from large responses | Medium | High | Response size limits, streaming for large payloads |
| Credential exposure | Low | Critical | Encryption at rest, secure logging |
| Rate limiting by external services | Medium | Medium | Per-endpoint rate limiting, backoff on 429 |

### Operational Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Database migration failure | Low | High | Staged rollout, rollback plan |
| Performance degradation under load | Medium | Medium | Load testing, circuit breakers |
| Third-party API changes | Medium | Low | Abstraction layer, versioned integrations |

---

## Quality Gates

### Code Quality

- [ ] 85%+ test coverage for all new code
- [ ] Zero Pyright type errors
- [ ] Zero Ruff linting errors
- [ ] All endpoints documented in OpenAPI
- [ ] Security review completed

### Performance Benchmarks

- [ ] Webhook execution < 100ms to start
- [ ] Support 100 concurrent requests per account
- [ ] Database queries < 50ms (p95)
- [ ] Memory usage stable under load

### Integration Criteria

- [ ] All acceptance tests passing
- [ ] End-to-end workflow execution works
- [ ] Retry mechanism validated
- [ ] Authentication types verified

---

## Definition of Done

1. All EARS requirements implemented and tested
2. Acceptance criteria verified (see acceptance.md)
3. Code reviewed and approved
4. Documentation complete (API, architecture)
5. Performance benchmarks met
6. Security review passed
7. Deployed to staging environment
8. Product owner sign-off

---

## Traceability

| Tag | Reference |
|-----|-----------|
| SPEC-WFL-010 | Parent specification |
| PLAN-WFL-010-M1 | Milestone 1 |
| PLAN-WFL-010-M2 | Milestone 2 |
| PLAN-WFL-010-M3 | Milestone 3 |
| PLAN-WFL-010-M4 | Milestone 4 |
| PLAN-WFL-010-M5 | Milestone 5 |
