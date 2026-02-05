# SPEC-WFL-003: Add Action Step

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-003 |
| **Title** | Add Action Step |
| **Module** | workflows |
| **Domain** | automation |
| **Priority** | Critical |
| **Status** | Planned |
| **Created** | 2026-01-26 |
| **Version** | 1.0.0 |

## Related Documents

- **Related SPECs:** SPEC-WFL-001 (Create Workflow), SPEC-WFL-002 (Configure Trigger), SPEC-WFL-004 (Add Condition/Branch), SPEC-WFL-005 (Execute Workflow)
- **Dependencies:** Workflow entity must exist (SPEC-WFL-001)
- **Plan:** [plan.md](./plan.md)
- **Acceptance Criteria:** [acceptance.md](./acceptance.md)

---

## Environment

### Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Backend | FastAPI | Latest |
| Database | PostgreSQL (Supabase) | 16 |
| ORM | SQLAlchemy | 2.0+ |
| Validation | Pydantic | v2.9+ |
| Queue | Redis/Celery | Latest |
| Language | Python | 3.12 |

### External Services

| Service | Purpose |
|---------|---------|
| Twilio | SMS, Voice, Voicemail delivery |
| SendGrid | Email delivery |
| Facebook | Messenger integration |
| Stripe | Payment and subscription actions |

---

## Assumptions

### Technical Assumptions

| ID | Assumption | Confidence | Risk if Wrong |
|----|------------|------------|---------------|
| A1 | Workflow canvas stores actions as JSON graph | High | Database schema redesign |
| A2 | Actions execute asynchronously via Celery | High | Performance bottlenecks |
| A3 | Each action type has a dedicated executor class | High | Code refactoring needed |
| A4 | Contact context available during action execution | High | Data flow redesign |

### Business Assumptions

| ID | Assumption | Confidence | Risk if Wrong |
|----|------------|------------|---------------|
| B1 | Users need all 25+ action types for MVP | Medium | Scope reduction possible |
| B2 | Actions must support dynamic content via templates | High | User experience degradation |
| B3 | Maximum 50 actions per workflow is sufficient | Medium | Performance optimization needed |

---

## Requirements

### R1: Core Action Management

#### R1.1: Add Action to Workflow (Ubiquitous)

The system shall allow adding action steps to any workflow in draft or paused state.

**EARS Pattern:** Ubiquitous

```
The system shall validate action configuration before adding to workflow sequence.
```

#### R1.2: Action Creation (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN a user selects an action type from the action palette
THEN the system shall create a new action node with default configuration
AND position the action in the workflow canvas
AND link the action to the preceding step.
```

#### R1.3: Action Configuration (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN a user configures action settings
THEN the system shall validate all required fields
AND save the configuration to the workflow definition
AND display a visual indicator of configuration status.
```

#### R1.4: Action Reordering (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN a user drags an action to a new position
THEN the system shall update the workflow sequence
AND recalculate action links
AND preserve all action configurations.
```

#### R1.5: Action Deletion (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN a user deletes an action from a workflow
THEN the system shall remove the action node
AND reconnect preceding and following steps
AND log the deletion for audit purposes.
```

---

### R2: Communication Actions

#### R2.1: Send Email Action (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN the send_email action executes
THEN the system shall render the email template with contact data
AND queue the email via SendGrid
AND track delivery status (sent, delivered, bounced, opened, clicked).
```

**Configuration Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| template_id | UUID | Yes | Email template reference |
| subject | string | Yes | Email subject with merge fields |
| from_name | string | Yes | Sender display name |
| from_email | string | Yes | Sender email address |
| reply_to | string | No | Reply-to email address |
| track_opens | boolean | No | Enable open tracking (default: true) |
| track_clicks | boolean | No | Enable click tracking (default: true) |
| attachments | array | No | File attachment references |

#### R2.2: Send SMS Action (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN the send_sms action executes
THEN the system shall validate TCPA compliance
AND check quiet hours for the contact's timezone
AND deliver SMS via Twilio
AND track delivery status.
```

**Configuration Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message | string | Yes | SMS content with merge fields (max 1600 chars) |
| from_number | string | Yes | Twilio phone number |
| media_urls | array | No | MMS media attachments |
| respect_quiet_hours | boolean | No | Honor quiet hours (default: true) |
| quiet_hours_start | time | No | Start of quiet hours (default: 21:00) |
| quiet_hours_end | time | No | End of quiet hours (default: 09:00) |

#### R2.3: Send Voicemail Action (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN the send_voicemail action executes
THEN the system shall initiate a call via Twilio
AND detect voicemail or answering machine
AND play the pre-recorded audio message
AND log the delivery attempt.
```

**Configuration Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| audio_file_id | UUID | Yes | Pre-recorded audio reference |
| from_number | string | Yes | Caller ID number |
| machine_detection | boolean | No | Enable AMD (default: true) |
| retry_on_busy | boolean | No | Retry if line busy (default: false) |
| max_retries | integer | No | Maximum retry attempts (default: 1) |

#### R2.4: Send Messenger Action (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN the send_messenger action executes
THEN the system shall validate Facebook page connection
AND send message via Facebook Messenger API
AND track delivery and read receipts.
```

**Configuration Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| page_id | UUID | Yes | Facebook page reference |
| message_type | enum | Yes | text, image, template, quick_reply |
| content | object | Yes | Message content based on type |
| messaging_type | enum | No | RESPONSE, UPDATE, MESSAGE_TAG |

#### R2.5: Make Call Action (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN the make_call action executes
THEN the system shall initiate outbound call via Twilio
AND connect to configured destination (user, queue, or IVR)
AND log call duration and outcome.
```

**Configuration Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| from_number | string | Yes | Caller ID number |
| destination_type | enum | Yes | user, queue, external, ivr |
| destination_value | string | Yes | Target based on type |
| record_call | boolean | No | Enable call recording (default: false) |
| timeout_seconds | integer | No | Ring timeout (default: 30) |

---

### R3: CRM Actions

#### R3.1: Create Contact Action (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN the create_contact action executes
THEN the system shall create a new contact record
AND populate fields from workflow context or static values
AND trigger contact_created event for downstream workflows.
```

**Configuration Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| first_name | string | No | Contact first name |
| last_name | string | No | Contact last name |
| email | string | No | Contact email (unique constraint) |
| phone | string | No | Contact phone number |
| custom_fields | object | No | Custom field mappings |
| duplicate_handling | enum | No | skip, update, create_duplicate |

#### R3.2: Update Contact Action (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN the update_contact action executes
THEN the system shall update specified contact fields
AND log field changes for audit
AND trigger contact_updated event.
```

**Configuration Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| field_updates | array | Yes | Array of field-value pairs |
| update_mode | enum | No | set, append, increment |

#### R3.3: Add Tag Action (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN the add_tag action executes
THEN the system shall add the specified tag to the contact
AND create the tag if it does not exist
AND trigger tag_added event.
```

**Configuration Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| tag_name | string | Yes | Tag to add (or create) |
| tag_color | string | No | Tag color if creating new |

#### R3.4: Remove Tag Action (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN the remove_tag action executes
THEN the system shall remove the specified tag from the contact
AND trigger tag_removed event
AND continue workflow even if tag was not present.
```

#### R3.5: Add to Campaign Action (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN the add_to_campaign action executes
THEN the system shall enroll the contact in the specified campaign
AND set the starting position based on configuration
AND respect campaign enrollment limits.
```

**Configuration Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| campaign_id | UUID | Yes | Target campaign reference |
| start_position | enum | No | beginning, specific_step |
| step_id | UUID | No | Specific step if start_position is specific_step |
| skip_if_enrolled | boolean | No | Skip if already in campaign (default: true) |

#### R3.6: Remove from Campaign Action (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN the remove_from_campaign action executes
THEN the system shall unenroll the contact from the specified campaign
AND cancel any pending campaign actions
AND log the removal reason.
```

#### R3.7: Move Pipeline Stage Action (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN the move_pipeline_stage action executes
THEN the system shall move the contact's opportunity to the specified stage
AND update opportunity metadata
AND trigger stage_changed event.
```

**Configuration Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pipeline_id | UUID | Yes | Target pipeline |
| stage_id | UUID | Yes | Target stage |
| opportunity_selector | enum | No | first, latest, specific |
| opportunity_id | UUID | No | Specific opportunity if selector is specific |

#### R3.8: Assign to User Action (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN the assign_to_user action executes
THEN the system shall assign the contact to the specified user
AND optionally send assignment notification
AND update contact ownership.
```

**Configuration Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_id | UUID | Conditional | Target user (or use round_robin) |
| assignment_type | enum | Yes | specific, round_robin, least_busy |
| team_id | UUID | No | Team for round robin assignment |
| notify_assignee | boolean | No | Send notification (default: true) |

#### R3.9: Create Task Action (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN the create_task action executes
THEN the system shall create a task linked to the contact
AND assign to specified user
AND set due date based on configuration.
```

**Configuration Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Task title with merge fields |
| description | string | No | Task description |
| due_date_offset | object | No | Offset from execution (days, hours) |
| assignee_id | UUID | No | Task assignee (default: contact owner) |
| priority | enum | No | low, medium, high |

#### R3.10: Add Note Action (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN the add_note action executes
THEN the system shall create a note on the contact record
AND include execution context metadata
AND trigger note_added event.
```

**Configuration Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| content | string | Yes | Note content with merge fields |
| note_type | enum | No | general, workflow, system |

---

### R4: Timing Actions

#### R4.1: Wait Time Action (State-Driven)

**EARS Pattern:** State-Driven

```
IF a wait_time action is reached in the workflow
THEN the system shall pause the workflow execution
AND schedule resume after the specified duration
AND store the execution state for recovery.
```

**Configuration Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| duration | integer | Yes | Wait duration value |
| unit | enum | Yes | minutes, hours, days, weeks |

#### R4.2: Wait Until Date Action (State-Driven)

**EARS Pattern:** State-Driven

```
IF a wait_until_date action is reached
THEN the system shall calculate the target datetime
AND pause execution until that time
AND respect the contact's timezone if specified.
```

**Configuration Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| date_type | enum | Yes | specific, contact_field, calculated |
| date_value | datetime | Conditional | Specific date if type is specific |
| field_name | string | Conditional | Contact field if type is contact_field |
| time_of_day | time | No | Specific time to resume |
| timezone_mode | enum | No | account, contact, utc |

#### R4.3: Wait for Event Action (State-Driven)

**EARS Pattern:** State-Driven

```
IF a wait_for_event action is reached
THEN the system shall pause execution
AND listen for the specified event type
AND resume when event occurs or timeout expires.
```

**Configuration Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| event_type | enum | Yes | email_open, email_click, sms_reply, form_submit |
| related_action_id | UUID | No | Link to triggering action |
| timeout_duration | integer | No | Timeout value |
| timeout_unit | enum | No | hours, days |
| timeout_action | enum | No | continue, branch, end |

---

### R5: Internal Actions

#### R5.1: Send Notification Action (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN the send_notification action executes
THEN the system shall send internal notification to specified users
AND deliver via configured channels (in-app, email, SMS)
AND log notification delivery.
```

**Configuration Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| recipient_type | enum | Yes | specific_user, contact_owner, team, role |
| recipient_ids | array | Conditional | User IDs if specific_user |
| channels | array | Yes | in_app, email, sms |
| title | string | Yes | Notification title |
| message | string | Yes | Notification content with merge fields |

#### R5.2: Create Opportunity Action (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN the create_opportunity action executes
THEN the system shall create an opportunity in the specified pipeline
AND link to the contact
AND set initial stage and value.
```

**Configuration Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pipeline_id | UUID | Yes | Target pipeline |
| stage_id | UUID | No | Initial stage (default: first stage) |
| name | string | Yes | Opportunity name with merge fields |
| value | number | No | Monetary value |
| currency | string | No | Currency code (default: account currency) |

#### R5.3: Webhook Call Action (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN the webhook_call action executes
THEN the system shall make HTTP request to the configured URL
AND include specified payload with contact data
AND handle response for downstream actions.
```

**Configuration Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| url | string | Yes | Webhook endpoint URL |
| method | enum | Yes | GET, POST, PUT, PATCH, DELETE |
| headers | object | No | Custom HTTP headers |
| payload | object | No | Request body (JSON) |
| auth_type | enum | No | none, basic, bearer, api_key |
| auth_config | object | Conditional | Authentication credentials |
| timeout_seconds | integer | No | Request timeout (default: 30) |
| retry_on_failure | boolean | No | Enable retry (default: true) |
| max_retries | integer | No | Maximum retries (default: 3) |
| store_response | boolean | No | Store response for later use |

#### R5.4: Custom Code Action (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN the custom_code action executes
THEN the system shall execute the user-defined JavaScript code
AND provide contact and workflow context
AND capture output for downstream actions.
```

**Configuration Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| code | string | Yes | JavaScript code to execute |
| timeout_ms | integer | No | Execution timeout (default: 5000) |
| memory_limit_mb | integer | No | Memory limit (default: 128) |
| allowed_modules | array | No | Permitted npm modules |

**Security Constraints:**

- Sandboxed execution environment (VM2 or similar)
- No filesystem access
- No network access except via fetch API
- Maximum execution time: 5 seconds
- Maximum memory: 128MB

---

### R6: Membership Actions

#### R6.1: Grant Course Access Action (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN the grant_course_access action executes
THEN the system shall grant the contact access to the specified course
AND set access parameters (duration, level)
AND trigger access_granted event.
```

**Configuration Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| course_id | UUID | Yes | Target course |
| access_level | enum | No | full, preview, limited |
| duration_days | integer | No | Access duration (null for lifetime) |
| drip_content | boolean | No | Enable content dripping (default: true) |
| send_welcome | boolean | No | Send welcome email (default: true) |

#### R6.2: Revoke Course Access Action (Event-Driven)

**EARS Pattern:** Event-Driven

```
WHEN the revoke_course_access action executes
THEN the system shall revoke the contact's access to the specified course
AND optionally retain progress data
AND trigger access_revoked event.
```

**Configuration Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| course_id | UUID | Yes | Target course |
| retain_progress | boolean | No | Keep progress data (default: true) |
| revocation_reason | string | No | Reason for revocation |

---

### R7: Error Handling and Recovery

#### R7.1: Action Failure Handling (Unwanted)

**EARS Pattern:** Unwanted

```
The system shall NOT continue workflow execution when an action fails critically
UNLESS a fallback action is configured
OR the error is marked as non-blocking.
```

#### R7.2: Retry Logic (State-Driven)

**EARS Pattern:** State-Driven

```
IF an action fails with a retryable error
THEN the system shall retry the action using exponential backoff
AND log each retry attempt
AND mark as failed after maximum retries exceeded.
```

**Retry Configuration:**

| Error Type | Retryable | Max Retries | Backoff |
|------------|-----------|-------------|---------|
| Network timeout | Yes | 3 | Exponential |
| Rate limit | Yes | 5 | Linear with delay |
| Invalid config | No | 0 | N/A |
| Service unavailable | Yes | 3 | Exponential |
| Authentication | No | 0 | N/A |

#### R7.3: Execution Logging (Ubiquitous)

**EARS Pattern:** Ubiquitous

```
The system shall log all action executions with:
- Timestamp
- Contact ID
- Action type and configuration
- Execution duration
- Result status
- Error details if failed
```

---

## Specifications

### Database Schema

#### workflow_actions Table

```sql
CREATE TABLE workflow_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    action_type VARCHAR(50) NOT NULL,
    action_config JSONB NOT NULL DEFAULT '{}',
    position INTEGER NOT NULL,
    previous_action_id UUID REFERENCES workflow_actions(id),
    next_action_id UUID REFERENCES workflow_actions(id),
    branch_id UUID REFERENCES workflow_branches(id),
    is_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id),

    CONSTRAINT valid_action_type CHECK (
        action_type IN (
            'send_email', 'send_sms', 'send_voicemail', 'send_messenger', 'make_call',
            'create_contact', 'update_contact', 'add_tag', 'remove_tag',
            'add_to_campaign', 'remove_from_campaign', 'move_pipeline_stage',
            'assign_to_user', 'create_task', 'add_note',
            'wait_time', 'wait_until_date', 'wait_for_event',
            'send_notification', 'create_opportunity', 'webhook_call', 'custom_code',
            'grant_course_access', 'revoke_course_access'
        )
    )
);

CREATE INDEX idx_workflow_actions_workflow ON workflow_actions(workflow_id);
CREATE INDEX idx_workflow_actions_type ON workflow_actions(action_type);
CREATE INDEX idx_workflow_actions_position ON workflow_actions(workflow_id, position);
```

#### workflow_action_executions Table

```sql
CREATE TABLE workflow_action_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_execution_id UUID NOT NULL REFERENCES workflow_executions(id),
    action_id UUID NOT NULL REFERENCES workflow_actions(id),
    contact_id UUID NOT NULL REFERENCES contacts(id),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    execution_data JSONB DEFAULT '{}',
    result_data JSONB DEFAULT '{}',
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    scheduled_at TIMESTAMPTZ,

    CONSTRAINT valid_execution_status CHECK (
        status IN ('pending', 'scheduled', 'running', 'completed', 'failed', 'skipped', 'waiting')
    )
);

CREATE INDEX idx_action_executions_workflow ON workflow_action_executions(workflow_execution_id);
CREATE INDEX idx_action_executions_contact ON workflow_action_executions(contact_id);
CREATE INDEX idx_action_executions_status ON workflow_action_executions(status);
CREATE INDEX idx_action_executions_scheduled ON workflow_action_executions(scheduled_at)
    WHERE status = 'scheduled';
```

### API Endpoints

#### Action Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/workflows/{workflow_id}/actions` | Add action to workflow |
| GET | `/api/v1/workflows/{workflow_id}/actions` | List workflow actions |
| GET | `/api/v1/workflows/{workflow_id}/actions/{action_id}` | Get action details |
| PUT | `/api/v1/workflows/{workflow_id}/actions/{action_id}` | Update action config |
| DELETE | `/api/v1/workflows/{workflow_id}/actions/{action_id}` | Delete action |
| POST | `/api/v1/workflows/{workflow_id}/actions/reorder` | Reorder actions |

#### Request/Response Examples

**POST /api/v1/workflows/{workflow_id}/actions**

Request:
```json
{
    "action_type": "send_email",
    "action_config": {
        "template_id": "550e8400-e29b-41d4-a716-446655440000",
        "subject": "Welcome {{contact.first_name}}!",
        "from_name": "Support Team",
        "from_email": "support@example.com",
        "track_opens": true,
        "track_clicks": true
    },
    "position": 1,
    "previous_action_id": "660e8400-e29b-41d4-a716-446655440000"
}
```

Response:
```json
{
    "id": "770e8400-e29b-41d4-a716-446655440000",
    "workflow_id": "880e8400-e29b-41d4-a716-446655440000",
    "action_type": "send_email",
    "action_config": { ... },
    "position": 1,
    "is_enabled": true,
    "created_at": "2026-01-26T10:00:00Z"
}
```

### Action Executor Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Workflow Engine                           │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                Action Dispatcher                         │ │
│  └────────────────────────┬────────────────────────────────┘ │
│                           │                                  │
│  ┌────────────────────────▼────────────────────────────────┐ │
│  │              Action Executor Factory                     │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │ │
│  │  │  Email  │ │   SMS   │ │   CRM   │ │ Webhook │  ...  │ │
│  │  │Executor │ │Executor │ │Executor │ │Executor │       │ │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘       │ │
│  └───────┼──────────────┼──────────────┼──────────┼────────┘ │
│          │              │              │          │          │
└──────────┼──────────────┼──────────────┼──────────┼──────────┘
           │              │              │          │
    ┌──────▼─────┐ ┌──────▼─────┐ ┌──────▼────┐ ┌──▼─────────┐
    │  SendGrid  │ │   Twilio   │ │ Database  │ │  HTTP      │
    │    API     │ │    API     │ │           │ │  Client    │
    └────────────┘ └────────────┘ └───────────┘ └────────────┘
```

### Traceability

| Requirement | Test Case | Acceptance Criteria |
|-------------|-----------|---------------------|
| R1.1 | test_add_action_to_workflow | AC-001 |
| R1.2 | test_action_creation | AC-002 |
| R1.3 | test_action_configuration | AC-003 |
| R2.1 | test_send_email_action | AC-010 |
| R2.2 | test_send_sms_action | AC-011 |
| R3.1 | test_create_contact_action | AC-020 |
| R4.1 | test_wait_time_action | AC-030 |
| R5.3 | test_webhook_action | AC-040 |
| R6.1 | test_grant_course_access | AC-050 |
| R7.1 | test_action_failure_handling | AC-060 |

---

## Constraints

### Performance Requirements

| Metric | Target |
|--------|--------|
| Action creation response time | < 200ms |
| Action execution throughput | 1000 actions/second |
| Maximum actions per workflow | 50 |
| Maximum concurrent executions | 10,000 |

### Security Requirements

| Requirement | Implementation |
|-------------|----------------|
| Input validation | Pydantic schemas for all action configs |
| Authorization | RBAC with workflow edit permission |
| Audit logging | All action CRUD operations logged |
| Sandbox execution | Custom code runs in isolated VM |

### Compliance Requirements

| Regulation | Requirement |
|------------|-------------|
| TCPA | SMS quiet hours enforcement |
| CAN-SPAM | Email unsubscribe handling |
| GDPR | Contact data processing consent |

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| External service downtime | Medium | High | Retry logic with circuit breaker |
| Action execution bottleneck | Low | High | Horizontal scaling with Celery workers |
| Complex action dependencies | Medium | Medium | Graph validation before save |
| Custom code security | Low | Critical | Sandboxed VM with strict limits |

---

## Out of Scope

- Visual workflow canvas UI (handled by frontend SPEC)
- Workflow scheduling (handled by SPEC-WFL-005)
- Action analytics dashboards (handled by SPEC-WFL-009)
- Import/export of workflow templates (handled by SPEC-WFL-008)
