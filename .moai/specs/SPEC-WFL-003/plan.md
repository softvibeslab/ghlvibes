# SPEC-WFL-003: Add Action Step - Implementation Plan

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-003 |
| **Title** | Add Action Step |
| **Related SPEC** | [spec.md](./spec.md) |
| **Acceptance Criteria** | [acceptance.md](./acceptance.md) |

---

## Implementation Overview

This plan details the implementation approach for the workflow action step system, covering all 25+ action types across communication, CRM, timing, internal, and membership categories.

---

## Milestones

### Milestone 1: Core Action Infrastructure (Primary Goal)

**Objective:** Establish the foundational action management system and executor framework.

**Deliverables:**

| Component | Description | Files |
|-----------|-------------|-------|
| Database Schema | Action tables and indexes | `migrations/003_workflow_actions.py` |
| Base Models | Pydantic models for actions | `src/backend/domain/workflows/models/action.py` |
| Action Repository | CRUD operations | `src/backend/infrastructure/repositories/action_repository.py` |
| API Endpoints | REST endpoints for action management | `src/backend/api/v1/workflows/actions.py` |
| Executor Base | Abstract executor class | `src/backend/domain/workflows/executors/base.py` |
| Dispatcher | Action routing and execution | `src/backend/domain/workflows/executors/dispatcher.py` |

**Technical Approach:**

1. **Database Migration**
   - Create `workflow_actions` table with JSONB config storage
   - Create `workflow_action_executions` for audit trail
   - Add indexes for query optimization

2. **Domain Models**
   - Create base `ActionConfig` Pydantic model
   - Implement discriminated union for action types
   - Add validation decorators for each action type

3. **Repository Pattern**
   - Implement async SQLAlchemy repository
   - Add position management for action ordering
   - Implement soft delete with cascade handling

4. **Executor Framework**
   - Create `BaseActionExecutor` abstract class
   - Implement `ActionDispatcher` for routing
   - Add execution context management

**Dependencies:** SPEC-WFL-001 (Workflow entity must exist)

---

### Milestone 2: Communication Actions (Primary Goal)

**Objective:** Implement all communication action executors (email, SMS, voicemail, messenger, call).

**Deliverables:**

| Component | Description | Files |
|-----------|-------------|-------|
| Email Executor | SendGrid integration | `src/backend/domain/workflows/executors/email_executor.py` |
| SMS Executor | Twilio SMS with TCPA | `src/backend/domain/workflows/executors/sms_executor.py` |
| Voicemail Executor | Twilio voicemail drops | `src/backend/domain/workflows/executors/voicemail_executor.py` |
| Messenger Executor | Facebook API integration | `src/backend/domain/workflows/executors/messenger_executor.py` |
| Call Executor | Twilio outbound calls | `src/backend/domain/workflows/executors/call_executor.py` |
| Template Engine | Merge field processing | `src/backend/domain/workflows/services/template_engine.py` |

**Technical Approach:**

1. **Email Executor**
   - Integrate SendGrid SDK for email delivery
   - Implement template rendering with merge fields
   - Add tracking pixel and link rewriting for analytics
   - Handle bounce and complaint webhooks

2. **SMS Executor**
   - Integrate Twilio SMS API
   - Implement TCPA quiet hours enforcement
   - Add timezone detection for contacts
   - Support MMS with media attachments

3. **Voicemail Executor**
   - Use Twilio Programmable Voice
   - Implement AMD (Answering Machine Detection)
   - Handle call outcomes (voicemail, busy, no answer)
   - Store audio files in Supabase Storage

4. **Messenger Executor**
   - Integrate Facebook Send API
   - Support text, image, and template messages
   - Handle 24-hour messaging window rules
   - Implement fallback for opt-out users

5. **Call Executor**
   - Use Twilio Voice API for outbound calls
   - Implement call routing (user, queue, external)
   - Add call recording option
   - Track call duration and outcome

**External Dependencies:** SendGrid, Twilio, Facebook API

---

### Milestone 3: CRM Actions (Secondary Goal)

**Objective:** Implement all CRM-related action executors.

**Deliverables:**

| Component | Description | Files |
|-----------|-------------|-------|
| Contact Executor | Create/update contacts | `src/backend/domain/workflows/executors/contact_executor.py` |
| Tag Executor | Add/remove tags | `src/backend/domain/workflows/executors/tag_executor.py` |
| Campaign Executor | Campaign enrollment | `src/backend/domain/workflows/executors/campaign_executor.py` |
| Pipeline Executor | Stage management | `src/backend/domain/workflows/executors/pipeline_executor.py` |
| Assignment Executor | User assignment | `src/backend/domain/workflows/executors/assignment_executor.py` |
| Task Executor | Task creation | `src/backend/domain/workflows/executors/task_executor.py` |
| Note Executor | Note creation | `src/backend/domain/workflows/executors/note_executor.py` |

**Technical Approach:**

1. **Contact Operations**
   - Implement create with duplicate detection
   - Support field update with merge modes (set, append, increment)
   - Handle custom field mappings
   - Emit events for downstream workflows

2. **Tag Management**
   - Create tags dynamically if not exist
   - Implement idempotent add/remove
   - Support tag color customization

3. **Campaign Enrollment**
   - Validate campaign exists and is active
   - Support starting position configuration
   - Implement enrollment limit checking
   - Handle duplicate enrollment prevention

4. **Pipeline Stage Movement**
   - Validate pipeline and stage existence
   - Support multiple opportunity selection
   - Log stage transition history
   - Emit stage_changed events

5. **User Assignment**
   - Implement round-robin algorithm
   - Support least-busy assignment
   - Send assignment notifications
   - Update contact ownership

**Dependencies:** CRM module entities (SPEC-CRM-*)

---

### Milestone 4: Timing and Wait Actions (Secondary Goal)

**Objective:** Implement timing control actions with proper scheduling.

**Deliverables:**

| Component | Description | Files |
|-----------|-------------|-------|
| Wait Time Executor | Fixed duration wait | `src/backend/domain/workflows/executors/wait_time_executor.py` |
| Wait Date Executor | Date-based wait | `src/backend/domain/workflows/executors/wait_date_executor.py` |
| Wait Event Executor | Event-based wait | `src/backend/domain/workflows/executors/wait_event_executor.py` |
| Scheduler Service | Job scheduling | `src/backend/domain/workflows/services/scheduler_service.py` |
| Event Listener | Event monitoring | `src/backend/domain/workflows/services/event_listener.py` |

**Technical Approach:**

1. **Wait Time Processing**
   - Store scheduled resume time in database
   - Use Celery beat for periodic checking
   - Handle timezone conversions
   - Support unit conversion (minutes, hours, days, weeks)

2. **Wait Until Date**
   - Calculate target datetime from configuration
   - Support contact field date sources
   - Implement time-of-day scheduling
   - Handle past dates gracefully

3. **Wait for Event**
   - Create event listener registration
   - Implement timeout handling
   - Support multiple event types
   - Link to triggering actions for context

4. **Scheduler Service**
   - Use Redis for scheduled job storage
   - Implement distributed locking
   - Handle missed schedules (catch-up)
   - Support schedule cancellation

**Dependencies:** Redis, Celery Beat

---

### Milestone 5: Internal and Membership Actions (Final Goal)

**Objective:** Implement internal system actions and membership management.

**Deliverables:**

| Component | Description | Files |
|-----------|-------------|-------|
| Notification Executor | Internal notifications | `src/backend/domain/workflows/executors/notification_executor.py` |
| Opportunity Executor | Opportunity creation | `src/backend/domain/workflows/executors/opportunity_executor.py` |
| Webhook Executor | HTTP calls | `src/backend/domain/workflows/executors/webhook_executor.py` |
| Custom Code Executor | JS execution | `src/backend/domain/workflows/executors/custom_code_executor.py` |
| Course Access Executor | Membership access | `src/backend/domain/workflows/executors/course_access_executor.py` |

**Technical Approach:**

1. **Internal Notifications**
   - Implement multi-channel delivery (in-app, email, SMS)
   - Support recipient type resolution
   - Use WebSocket for real-time in-app notifications
   - Respect notification preferences

2. **Opportunity Creation**
   - Create opportunity with pipeline linkage
   - Set initial stage and value
   - Support currency conversion
   - Emit opportunity_created event

3. **Webhook Calls**
   - Implement configurable HTTP client
   - Support authentication methods
   - Add retry with exponential backoff
   - Store response for later use
   - Implement circuit breaker pattern

4. **Custom Code Execution**
   - Use VM2 or isolated-vm for sandboxing
   - Inject contact and workflow context
   - Implement strict timeout enforcement
   - Capture console output for debugging
   - Whitelist allowed modules

5. **Course Access Management**
   - Grant/revoke course membership
   - Set access duration
   - Configure content dripping
   - Send welcome/revocation emails

**Security Considerations:**
- Custom code runs in isolated environment
- Network access restricted
- Memory and CPU limits enforced
- No filesystem access

---

### Milestone 6: Error Handling and Testing (Final Goal)

**Objective:** Implement comprehensive error handling and test coverage.

**Deliverables:**

| Component | Description | Files |
|-----------|-------------|-------|
| Error Handler | Centralized error handling | `src/backend/domain/workflows/services/error_handler.py` |
| Retry Service | Retry logic | `src/backend/domain/workflows/services/retry_service.py` |
| Unit Tests | Action unit tests | `src/backend/tests/unit/workflows/test_actions.py` |
| Integration Tests | E2E action tests | `src/backend/tests/integration/workflows/test_action_execution.py` |
| Fixtures | Test data factories | `src/backend/tests/fixtures/workflow_fixtures.py` |

**Technical Approach:**

1. **Error Classification**
   - Define retryable vs non-retryable errors
   - Implement error code system
   - Create error response schemas
   - Add error localization

2. **Retry Logic**
   - Implement exponential backoff
   - Support linear backoff for rate limits
   - Add jitter to prevent thundering herd
   - Track retry attempts in execution log

3. **Circuit Breaker**
   - Monitor failure rates per service
   - Implement half-open state testing
   - Configure thresholds per integration
   - Alert on circuit open

4. **Testing Strategy**
   - Unit tests for each executor (mocked dependencies)
   - Integration tests with real database
   - Contract tests for external APIs
   - Load tests for throughput validation

---

## Technical Approach

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         API Layer                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │ Action Router   │  │ Validation      │  │ Authorization   │     │
│  │ (FastAPI)       │  │ (Pydantic)      │  │ (RBAC)          │     │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘     │
└───────────┼─────────────────────┼─────────────────────┼─────────────┘
            │                     │                     │
┌───────────▼─────────────────────▼─────────────────────▼─────────────┐
│                       Application Layer                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Action Service                            │   │
│  │  - CRUD operations                                           │   │
│  │  - Position management                                       │   │
│  │  - Configuration validation                                  │   │
│  └─────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────┐
│                         Domain Layer                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │ Action Models   │  │ Executor        │  │ Template        │     │
│  │                 │  │ Framework       │  │ Engine          │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                    Action Executors                           │ │
│  │  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐          │ │
│  │  │ Email │ │  SMS  │ │  CRM  │ │Webhook│ │Custom │   ...    │ │
│  │  └───────┘ └───────┘ └───────┘ └───────┘ └───────┘          │ │
│  └───────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────┐
│                     Infrastructure Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │ Action Repo     │  │ External APIs   │  │ Message Queue   │     │
│  │ (SQLAlchemy)    │  │ (Twilio, etc)   │  │ (Celery/Redis)  │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

#### 1. Action Configuration Storage

**Decision:** Store action configurations as JSONB in PostgreSQL.

**Rationale:**
- Flexible schema for different action types
- Native JSON querying capabilities
- Version-agnostic storage
- Easy migration for config changes

**Trade-off:** Less strict type enforcement at database level (mitigated by Pydantic validation).

#### 2. Executor Pattern

**Decision:** Use Strategy pattern with factory for action execution.

**Rationale:**
- Each action type has dedicated executor
- Easy to add new action types
- Testable in isolation
- Clear separation of concerns

**Implementation:**
```python
class ActionExecutorFactory:
    _executors: Dict[str, Type[BaseActionExecutor]] = {}

    @classmethod
    def register(cls, action_type: str):
        def decorator(executor_cls):
            cls._executors[action_type] = executor_cls
            return executor_cls
        return decorator

    @classmethod
    def get_executor(cls, action_type: str) -> BaseActionExecutor:
        return cls._executors[action_type]()
```

#### 3. Async Execution Model

**Decision:** Execute actions asynchronously via Celery task queue.

**Rationale:**
- Non-blocking API responses
- Horizontal scalability
- Retry and failure handling
- Rate limiting support

**Trade-off:** Added complexity for debugging execution flow.

#### 4. Template Engine

**Decision:** Use Jinja2 with custom filters for merge field processing.

**Rationale:**
- Industry standard template engine
- Rich filter and function support
- Secure sandboxed execution
- Extensible for custom functions

**Merge Field Syntax:**
```
{{contact.first_name}}
{{contact.custom_fields.company_name}}
{{workflow.execution_date | date_format('YYYY-MM-DD')}}
```

### File Structure

```
src/backend/
├── api/
│   └── v1/
│       └── workflows/
│           ├── __init__.py
│           ├── actions.py          # Action endpoints
│           └── schemas.py          # Request/Response schemas
├── domain/
│   └── workflows/
│       ├── models/
│       │   ├── __init__.py
│       │   ├── action.py           # Action domain models
│       │   └── execution.py        # Execution models
│       ├── executors/
│       │   ├── __init__.py
│       │   ├── base.py             # Base executor class
│       │   ├── dispatcher.py       # Action dispatcher
│       │   ├── email_executor.py
│       │   ├── sms_executor.py
│       │   ├── voicemail_executor.py
│       │   ├── messenger_executor.py
│       │   ├── call_executor.py
│       │   ├── contact_executor.py
│       │   ├── tag_executor.py
│       │   ├── campaign_executor.py
│       │   ├── pipeline_executor.py
│       │   ├── assignment_executor.py
│       │   ├── task_executor.py
│       │   ├── note_executor.py
│       │   ├── wait_time_executor.py
│       │   ├── wait_date_executor.py
│       │   ├── wait_event_executor.py
│       │   ├── notification_executor.py
│       │   ├── opportunity_executor.py
│       │   ├── webhook_executor.py
│       │   ├── custom_code_executor.py
│       │   └── course_access_executor.py
│       └── services/
│           ├── __init__.py
│           ├── action_service.py   # Action business logic
│           ├── template_engine.py  # Merge field processing
│           ├── scheduler_service.py # Wait scheduling
│           ├── error_handler.py    # Error management
│           └── retry_service.py    # Retry logic
├── infrastructure/
│   └── repositories/
│       ├── __init__.py
│       └── action_repository.py    # Database operations
└── tests/
    ├── unit/
    │   └── workflows/
    │       ├── test_actions.py
    │       ├── test_executors.py
    │       └── test_template_engine.py
    ├── integration/
    │   └── workflows/
    │       └── test_action_execution.py
    └── fixtures/
        └── workflow_fixtures.py
```

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| External API rate limits | High | Medium | Implement rate limiting and queueing |
| Action execution timeouts | Medium | Medium | Set conservative timeouts, async processing |
| Custom code security | Low | Critical | Strict sandboxing, code review |
| Data consistency | Medium | High | Transactional operations, idempotency |
| Performance bottleneck | Medium | High | Horizontal scaling, caching |

---

## Definition of Done

- [ ] All action types implemented and tested
- [ ] 85%+ code coverage for action module
- [ ] API documentation generated (OpenAPI)
- [ ] Error handling comprehensive
- [ ] Performance targets met
- [ ] Security review completed
- [ ] Integration tests passing
- [ ] Code review approved
