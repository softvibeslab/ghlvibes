# SPEC-WFL-002: Configure Trigger

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-002 |
| **Title** | Configure Trigger |
| **Module** | workflows |
| **Domain** | automation |
| **Priority** | Critical |
| **Status** | Planned |
| **Created** | 2026-01-26 |
| **Author** | manager-spec |

---

## Overview

This specification defines the trigger configuration system for workflow automation. Triggers are the entry points that initiate workflow execution when specific events occur. The system supports 7 trigger categories with 25+ trigger types, enabling comprehensive automation coverage across the platform.

---

## EARS Requirements

### 1. Ubiquitous Requirements

**REQ-U-001: Trigger Validation**
The system shall validate all trigger configurations before saving to ensure required fields are complete and filter conditions are syntactically correct.

**REQ-U-002: Trigger Uniqueness**
The system shall ensure each workflow has exactly one primary trigger, though multiple filter conditions may be applied to that trigger.

**REQ-U-003: Audit Logging**
The system shall log all trigger configuration changes including creation, modification, and deletion with timestamps and user attribution.

**REQ-U-004: Multi-tenancy Isolation**
The system shall enforce tenant isolation ensuring triggers only fire for events within the same account/organization.

---

### 2. Event-Driven Requirements

#### 2.1 Contact Triggers

**REQ-E-001: Contact Created Trigger**
WHEN a new contact is created in the system,
THEN the system shall evaluate all active workflows with `contact_created` triggers and enroll matching contacts,
resulting in workflow execution initiation for qualified contacts,
in `triggered` state.

**REQ-E-002: Contact Updated Trigger**
WHEN a contact record is modified,
THEN the system shall evaluate all active workflows with `contact_updated` triggers against the changed fields,
resulting in workflow execution for contacts matching update criteria,
in `triggered` state.

**REQ-E-003: Tag Added Trigger**
WHEN a tag is added to a contact,
THEN the system shall evaluate all active workflows with `tag_added` triggers matching the specific tag,
resulting in workflow enrollment for the tagged contact,
in `triggered` state.

**REQ-E-004: Tag Removed Trigger**
WHEN a tag is removed from a contact,
THEN the system shall evaluate all active workflows with `tag_removed` triggers matching the specific tag,
resulting in workflow enrollment for the untagged contact,
in `triggered` state.

**REQ-E-005: Custom Field Changed Trigger**
WHEN a custom field value is modified on a contact,
THEN the system shall evaluate all active workflows with `custom_field_changed` triggers matching the field and value criteria,
resulting in workflow enrollment for contacts meeting the field conditions,
in `triggered` state.

#### 2.2 Form Triggers

**REQ-E-006: Form Submitted Trigger**
WHEN a form submission is received,
THEN the system shall evaluate all active workflows with `form_submitted` triggers matching the form ID,
resulting in workflow enrollment for the submitting contact,
in `triggered` state.

**REQ-E-007: Survey Completed Trigger**
WHEN a survey is completed by a contact,
THEN the system shall evaluate all active workflows with `survey_completed` triggers matching the survey ID,
resulting in workflow enrollment with survey response data available,
in `triggered` state.

#### 2.3 Pipeline Triggers

**REQ-E-008: Stage Changed Trigger**
WHEN a deal/opportunity moves to a different pipeline stage,
THEN the system shall evaluate all active workflows with `stage_changed` triggers matching the pipeline and stage criteria,
resulting in workflow enrollment for the associated contact,
in `triggered` state.

**REQ-E-009: Deal Created Trigger**
WHEN a new deal/opportunity is created,
THEN the system shall evaluate all active workflows with `deal_created` triggers matching the pipeline,
resulting in workflow enrollment for the deal's contact,
in `triggered` state.

**REQ-E-010: Deal Won Trigger**
WHEN a deal is marked as won,
THEN the system shall evaluate all active workflows with `deal_won` triggers,
resulting in workflow enrollment for the winning contact,
in `triggered` state.

**REQ-E-011: Deal Lost Trigger**
WHEN a deal is marked as lost,
THEN the system shall evaluate all active workflows with `deal_lost` triggers,
resulting in workflow enrollment for the contact with loss reason data,
in `triggered` state.

#### 2.4 Appointment Triggers

**REQ-E-012: Appointment Booked Trigger**
WHEN an appointment is scheduled,
THEN the system shall evaluate all active workflows with `appointment_booked` triggers matching the calendar/appointment type,
resulting in workflow enrollment for the booking contact,
in `triggered` state.

**REQ-E-013: Appointment Cancelled Trigger**
WHEN an appointment is cancelled,
THEN the system shall evaluate all active workflows with `appointment_cancelled` triggers,
resulting in workflow enrollment with cancellation details,
in `triggered` state.

**REQ-E-014: Appointment Completed Trigger**
WHEN an appointment is marked as completed,
THEN the system shall evaluate all active workflows with `appointment_completed` triggers,
resulting in workflow enrollment for post-appointment follow-up,
in `triggered` state.

**REQ-E-015: Appointment No-Show Trigger**
WHEN an appointment is marked as no-show,
THEN the system shall evaluate all active workflows with `appointment_no_show` triggers,
resulting in workflow enrollment for no-show handling,
in `triggered` state.

#### 2.5 Payment Triggers

**REQ-E-016: Payment Received Trigger**
WHEN a payment is successfully processed,
THEN the system shall evaluate all active workflows with `payment_received` triggers matching amount or product criteria,
resulting in workflow enrollment with payment details,
in `triggered` state.

**REQ-E-017: Subscription Created Trigger**
WHEN a new subscription is established,
THEN the system shall evaluate all active workflows with `subscription_created` triggers matching the plan,
resulting in workflow enrollment for onboarding,
in `triggered` state.

**REQ-E-018: Subscription Cancelled Trigger**
WHEN a subscription is cancelled,
THEN the system shall evaluate all active workflows with `subscription_cancelled` triggers,
resulting in workflow enrollment for retention/offboarding,
in `triggered` state.

#### 2.6 Communication Triggers

**REQ-E-019: Email Opened Trigger**
WHEN an email is opened by a contact,
THEN the system shall evaluate all active workflows with `email_opened` triggers matching the campaign/email ID,
resulting in workflow enrollment for engaged contacts,
in `triggered` state.

**REQ-E-020: Email Clicked Trigger**
WHEN a link in an email is clicked,
THEN the system shall evaluate all active workflows with `email_clicked` triggers matching the link or campaign,
resulting in workflow enrollment with click data,
in `triggered` state.

**REQ-E-021: SMS Received Trigger**
WHEN an inbound SMS is received,
THEN the system shall evaluate all active workflows with `sms_received` triggers matching keyword or sender criteria,
resulting in workflow enrollment with message content,
in `triggered` state.

**REQ-E-022: Call Completed Trigger**
WHEN a phone call is completed,
THEN the system shall evaluate all active workflows with `call_completed` triggers matching call disposition,
resulting in workflow enrollment with call details,
in `triggered` state.

#### 2.7 Time Triggers

**REQ-E-023: Scheduled Date Trigger**
WHEN a contact's date field matches a scheduled condition,
THEN the system shall evaluate all active workflows with `scheduled_date` triggers,
resulting in workflow enrollment at the specified time,
in `triggered` state.

**REQ-E-024: Recurring Schedule Trigger**
WHEN a recurring schedule interval is reached,
THEN the system shall evaluate all active workflows with `recurring_schedule` triggers matching the schedule,
resulting in batch workflow enrollment for matching contacts,
in `triggered` state.

**REQ-E-025: Birthday Trigger**
WHEN a contact's birthday matches the current date,
THEN the system shall evaluate all active workflows with `birthday` triggers,
resulting in workflow enrollment for birthday automation,
in `triggered` state.

**REQ-E-026: Anniversary Trigger**
WHEN a contact's anniversary date matches the current date,
THEN the system shall evaluate all active workflows with `anniversary` triggers,
resulting in workflow enrollment for anniversary automation,
in `triggered` state.

---

### 3. State-Driven Requirements

**REQ-S-001: Workflow Status Check**
WHILE a workflow is in `paused` or `draft` status,
THEN the system shall not evaluate or fire any triggers for that workflow,
resulting in no new enrollments,
in `inactive` state.

**REQ-S-002: Contact Enrollment Limit**
WHILE a contact is already enrolled in a workflow with `single_enrollment` setting,
THEN the system shall not re-enroll the contact even if the trigger fires again,
resulting in duplicate prevention,
in `blocked` state.

**REQ-S-003: Business Hours Enforcement**
WHILE outside configured business hours,
THEN time-based triggers shall queue for execution at the next available business hour,
resulting in delayed trigger processing,
in `queued` state.

---

### 4. Unwanted Behavior Requirements

**REQ-N-001: No Trigger Without Validation**
The system shall NOT save a trigger configuration that fails validation rules.

**REQ-N-002: No Cross-Tenant Triggering**
The system shall NOT fire triggers for events occurring in different tenant accounts.

**REQ-N-003: No Circular Trigger Loops**
The system shall NOT allow trigger configurations that would create infinite loops (e.g., tag_added trigger adds the same tag).

**REQ-N-004: No Trigger on Deleted Contacts**
The system shall NOT fire triggers for contacts marked as deleted (soft delete).

---

### 5. Optional Requirements

**REQ-O-001: Trigger Preview**
WHERE possible, the system shall provide a preview showing estimated contacts matching the trigger criteria before activation.

**REQ-O-002: Trigger Testing**
WHERE possible, the system shall allow manual trigger testing with a selected contact without requiring the actual event.

---

## Technical Specifications

### Database Schema

#### `workflow_triggers` Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique trigger identifier |
| `workflow_id` | UUID | FOREIGN KEY, NOT NULL | Reference to parent workflow |
| `trigger_type` | VARCHAR(50) | NOT NULL | Trigger category (contact, form, etc.) |
| `trigger_event` | VARCHAR(50) | NOT NULL | Specific event (contact_created, etc.) |
| `filters` | JSONB | DEFAULT '{}' | Filter conditions as JSON |
| `settings` | JSONB | DEFAULT '{}' | Trigger-specific settings |
| `is_active` | BOOLEAN | DEFAULT true | Trigger enabled status |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Last modification timestamp |
| `created_by` | UUID | FOREIGN KEY | User who created trigger |

#### `trigger_filters` Schema (JSONB)

```json
{
  "conditions": [
    {
      "field": "string",
      "operator": "equals|not_equals|contains|greater_than|less_than|in|not_in",
      "value": "any"
    }
  ],
  "logic": "AND|OR"
}
```

#### `trigger_execution_logs` Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Log entry identifier |
| `trigger_id` | UUID | FOREIGN KEY | Reference to trigger |
| `contact_id` | UUID | FOREIGN KEY | Contact that triggered |
| `event_data` | JSONB | NOT NULL | Event payload |
| `matched` | BOOLEAN | NOT NULL | Whether filters matched |
| `enrolled` | BOOLEAN | NOT NULL | Whether contact was enrolled |
| `failure_reason` | TEXT | NULLABLE | Reason if enrollment failed |
| `executed_at` | TIMESTAMPTZ | DEFAULT NOW() | Execution timestamp |

---

### API Endpoints

#### Configure Trigger

```
POST /api/v1/workflows/{workflow_id}/trigger
```

**Request Body:**
```json
{
  "trigger_type": "contact",
  "trigger_event": "contact_created",
  "filters": {
    "conditions": [
      {
        "field": "tags",
        "operator": "contains",
        "value": "lead"
      }
    ],
    "logic": "AND"
  },
  "settings": {
    "enrollment_limit": "single",
    "respect_business_hours": true
  }
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "workflow_id": "uuid",
  "trigger_type": "contact",
  "trigger_event": "contact_created",
  "filters": {...},
  "settings": {...},
  "is_active": true,
  "created_at": "2026-01-26T10:00:00Z"
}
```

#### Update Trigger

```
PUT /api/v1/workflows/{workflow_id}/trigger/{trigger_id}
```

#### Get Trigger

```
GET /api/v1/workflows/{workflow_id}/trigger
```

#### Delete Trigger

```
DELETE /api/v1/workflows/{workflow_id}/trigger/{trigger_id}
```

#### Test Trigger

```
POST /api/v1/workflows/{workflow_id}/trigger/{trigger_id}/test
```

**Request Body:**
```json
{
  "contact_id": "uuid",
  "simulate_event_data": {...}
}
```

---

### Event Listening Architecture

#### Event Bus Integration

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Event Source   │────▶│   Event Bus      │────▶│  Trigger Engine  │
│  (CRM, Forms,    │     │  (Redis Pub/Sub) │     │  (FastAPI Worker)│
│   Payments...)   │     │                  │     │                  │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                                                          │
                                                          ▼
                              ┌──────────────────────────────────────┐
                              │         Workflow Executor            │
                              │  (Queue contact for workflow run)    │
                              └──────────────────────────────────────┘
```

#### Event Payload Structure

```json
{
  "event_id": "uuid",
  "event_type": "contact.created",
  "account_id": "uuid",
  "timestamp": "ISO8601",
  "data": {
    "contact_id": "uuid",
    "previous_state": {...},
    "current_state": {...}
  }
}
```

---

## Constraints

### Performance Requirements

| Metric | Target |
|--------|--------|
| Trigger evaluation latency | < 100ms |
| Event processing throughput | 1000 events/second |
| Filter matching accuracy | 100% |
| Maximum filters per trigger | 20 conditions |

### Security Requirements

- All trigger configurations require authenticated API access
- Trigger modifications require `workflow:edit` permission
- Event data is encrypted in transit (TLS 1.3)
- Sensitive filter values (emails, phone numbers) are masked in logs

### Scalability Requirements

- Support 10,000+ active triggers per account
- Support 100,000+ trigger evaluations per hour
- Horizontal scaling through event partitioning by account_id

---

## Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| SPEC-WFL-001 | Prerequisite | Workflow must exist before trigger configuration |
| SPEC-WFL-005 | Downstream | Trigger fires workflow execution |
| Redis | Infrastructure | Event bus for trigger event distribution |
| PostgreSQL | Infrastructure | Trigger configuration storage |

---

## Traceability

| Requirement | Test Case | Acceptance Criteria |
|-------------|-----------|---------------------|
| REQ-E-001 | test_contact_trigger | AC-001 |
| REQ-E-006 | test_form_trigger | AC-002 |
| REQ-E-023 | test_time_trigger | AC-003 |
| REQ-S-002 | test_trigger_filters | AC-004 |

---

## References

- [GoHighLevel Clone - Product Overview](/config/workspace/gohighlevel-clone/.moai/project/product.md)
- [Technology Stack](/config/workspace/gohighlevel-clone/.moai/project/tech.md)
- [Workflows Module Plan](/config/workspace/gohighlevel-clone/specs/workflows/plan.md)
