# SPEC-WFL-007: Goal Tracking

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-007 |
| **Title** | Goal Tracking |
| **Module** | workflows |
| **Domain** | automation |
| **Priority** | Medium |
| **Status** | Planned |
| **Created** | 2026-01-26 |
| **Version** | 1.0.0 |

---

## Overview

Goal Tracking enables workflows to monitor contact behavior for specific goal completion events. When a contact achieves a defined goal (such as making a purchase or booking an appointment), the system automatically exits them from the workflow, preventing unnecessary follow-up actions and ensuring a positive customer experience.

### Business Value

- **Improved Customer Experience:** Contacts who complete desired actions are not bombarded with redundant messages
- **Resource Optimization:** System resources are freed by removing contacts who have achieved goals
- **Conversion Tracking:** Clear visibility into which workflows drive goal completion
- **Flexible Goal Definitions:** Support for multiple goal types to match various business objectives

---

## EARS Requirements

### R1: Goal Configuration (Event-Driven)

**WHEN** a user configures a workflow goal in the workflow editor
**THEN** the system shall display goal type selection with available goal options
**AND** the system shall validate that at least one goal criterion is specified
**AND** the system shall persist the goal configuration with the workflow definition

**State:** goal_configured

### R2: Goal Type Selection (Event-Driven)

**WHEN** selecting a goal type for the workflow
**THEN** the system shall provide the following goal type options:
- `tag_added` - Contact receives a specific tag
- `purchase_made` - Contact completes a purchase transaction
- `appointment_booked` - Contact books an appointment
- `form_submitted` - Contact submits a specific form
- `pipeline_stage_reached` - Contact reaches a specific pipeline stage

**State:** goal_type_selected

### R3: Tag Added Goal Monitoring (Event-Driven)

**WHEN** a contact in an active workflow receives a tag matching the configured goal tag
**THEN** the system shall mark the goal as achieved for that contact
**AND** the system shall trigger the workflow exit process
**AND** the system shall log the goal achievement with timestamp and tag details

**State:** goal_achieved

### R4: Purchase Made Goal Monitoring (Event-Driven)

**WHEN** a contact in an active workflow completes a purchase transaction
**THEN** the system shall evaluate if the purchase matches goal criteria (product, amount, or any purchase)
**AND** the system shall mark the goal as achieved if criteria are met
**AND** the system shall trigger the workflow exit process
**AND** the system shall log the goal achievement with transaction details

**State:** goal_achieved

### R5: Appointment Booked Goal Monitoring (Event-Driven)

**WHEN** a contact in an active workflow books an appointment
**THEN** the system shall evaluate if the appointment matches goal criteria (calendar, service type, or any appointment)
**AND** the system shall mark the goal as achieved if criteria are met
**AND** the system shall trigger the workflow exit process
**AND** the system shall log the goal achievement with appointment details

**State:** goal_achieved

### R6: Form Submitted Goal Monitoring (Event-Driven)

**WHEN** a contact in an active workflow submits a form
**THEN** the system shall evaluate if the form matches the configured goal form ID
**AND** the system shall mark the goal as achieved if the form matches
**AND** the system shall trigger the workflow exit process
**AND** the system shall log the goal achievement with form submission details

**State:** goal_achieved

### R7: Pipeline Stage Reached Goal Monitoring (Event-Driven)

**WHEN** a contact in an active workflow reaches a pipeline stage
**THEN** the system shall evaluate if the stage matches the configured goal stage
**AND** the system shall mark the goal as achieved if the stage matches
**AND** the system shall trigger the workflow exit process
**AND** the system shall log the goal achievement with pipeline transition details

**State:** goal_achieved

### R8: Workflow Exit on Goal Achievement (Event-Driven)

**WHEN** a goal is achieved for a contact in a workflow
**THEN** the system shall immediately halt all pending actions for that contact
**AND** the system shall cancel any scheduled wait steps
**AND** the system shall update the workflow enrollment status to "completed_goal"
**AND** the system shall emit a workflow_goal_achieved event for analytics

**State:** workflow_exited

### R9: Goal Event Listener Registration (State-Driven)

**IF** a workflow with a configured goal is activated
**THEN** the system shall register event listeners for the configured goal type
**AND** the system shall associate the listeners with the workflow ID and enrolled contacts

**State:** listeners_active

### R10: Goal Event Listener Cleanup (Event-Driven)

**WHEN** a workflow is deactivated or a contact completes/exits the workflow
**THEN** the system shall unregister the associated goal event listeners
**AND** the system shall clean up any pending goal monitoring tasks

**State:** listeners_removed

### R11: Multiple Goal Support (Optional)

**WHERE** advanced goal tracking is enabled
**THEN** the system shall allow configuration of multiple goals per workflow
**AND** the system shall support "any goal" or "all goals" completion logic

**State:** multi_goal_configured

### R12: Goal Analytics Tracking (Ubiquitous)

The system shall track and store goal achievement metrics including:
- Total contacts who achieved the goal
- Time from enrollment to goal achievement
- Goal conversion rate per workflow
- Goal achievement by goal type

**State:** analytics_active

### R13: Goal Configuration Validation (Unwanted)

The system shall NOT allow workflow activation if:
- Goal type is selected but no goal criteria are specified
- Goal references non-existent entities (tags, forms, pipelines)
- Goal configuration contains invalid data types

**State:** validation_error

---

## Constraints

### Technical Constraints

| Constraint | Specification |
|------------|---------------|
| Event Processing Latency | Goal events must be processed within 5 seconds of occurrence |
| Listener Scalability | Support up to 100,000 concurrent goal listeners |
| Data Retention | Goal achievement logs retained for 2 years |
| API Response Time | Goal configuration API responses under 200ms |

### Business Constraints

| Constraint | Specification |
|------------|---------------|
| Goal Types | Limited to 5 predefined goal types in v1.0 |
| Multiple Goals | Maximum 3 goals per workflow |
| Retroactive Goals | Goals are not evaluated retroactively for contacts already in workflow |

### Security Constraints

| Constraint | Specification |
|------------|---------------|
| Tenant Isolation | Goal events must be tenant-scoped to prevent cross-tenant data access |
| Audit Logging | All goal achievements and configuration changes must be audit logged |
| Authorization | Only users with workflow edit permissions can configure goals |

---

## Dependencies

### Internal Dependencies

| Dependency | Purpose |
|------------|---------|
| Workflow Engine (SPEC-WFL-005) | Workflow execution and contact enrollment |
| Contact Management (SPEC-CRM-001) | Contact data and tag management |
| Appointment System (SPEC-BKG-001) | Appointment booking events |
| Form System (SPEC-FNL-002) | Form submission events |
| Pipeline System (SPEC-CRM-005) | Pipeline stage change events |
| Payment System (SPEC-PAY-001) | Purchase transaction events |

### External Dependencies

| Dependency | Purpose |
|------------|---------|
| Redis | Event pub/sub and listener state management |
| PostgreSQL/Supabase | Goal configuration and achievement persistence |
| Celery/Background Workers | Asynchronous event processing |

---

## Data Model

### Goal Configuration Schema

```python
class GoalType(str, Enum):
    TAG_ADDED = "tag_added"
    PURCHASE_MADE = "purchase_made"
    APPOINTMENT_BOOKED = "appointment_booked"
    FORM_SUBMITTED = "form_submitted"
    PIPELINE_STAGE_REACHED = "pipeline_stage_reached"

class GoalConfig(BaseModel):
    id: UUID
    workflow_id: UUID
    goal_type: GoalType
    criteria: dict  # Type-specific criteria
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class GoalCriteria:
    # tag_added
    tag_id: Optional[UUID]
    tag_name: Optional[str]

    # purchase_made
    product_id: Optional[UUID]
    min_amount: Optional[Decimal]
    any_purchase: bool = False

    # appointment_booked
    calendar_id: Optional[UUID]
    service_id: Optional[UUID]
    any_appointment: bool = False

    # form_submitted
    form_id: UUID

    # pipeline_stage_reached
    pipeline_id: UUID
    stage_id: UUID
```

### Goal Achievement Schema

```python
class GoalAchievement(BaseModel):
    id: UUID
    workflow_id: UUID
    workflow_enrollment_id: UUID
    contact_id: UUID
    goal_config_id: UUID
    goal_type: GoalType
    achieved_at: datetime
    trigger_event: dict  # Event data that triggered goal
    metadata: dict  # Additional context
```

### Database Tables

```sql
-- Goal Configuration Table
CREATE TABLE workflow_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    goal_type VARCHAR(50) NOT NULL,
    criteria JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    UNIQUE(workflow_id, goal_type, criteria)
);

-- Goal Achievement Log Table
CREATE TABLE workflow_goal_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id),
    workflow_enrollment_id UUID NOT NULL REFERENCES workflow_enrollments(id),
    contact_id UUID NOT NULL REFERENCES contacts(id),
    goal_config_id UUID NOT NULL REFERENCES workflow_goals(id),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    goal_type VARCHAR(50) NOT NULL,
    achieved_at TIMESTAMPTZ DEFAULT NOW(),
    trigger_event JSONB,
    metadata JSONB,
    INDEX idx_achievements_workflow (workflow_id),
    INDEX idx_achievements_contact (contact_id),
    INDEX idx_achievements_date (achieved_at)
);
```

---

## API Specification

### Endpoints

#### Configure Workflow Goal

```
POST /api/v1/workflows/{workflow_id}/goals
```

**Request Body:**
```json
{
    "goal_type": "tag_added",
    "criteria": {
        "tag_id": "uuid-of-tag",
        "tag_name": "Purchased"
    }
}
```

**Response (201 Created):**
```json
{
    "id": "uuid-of-goal-config",
    "workflow_id": "uuid-of-workflow",
    "goal_type": "tag_added",
    "criteria": {
        "tag_id": "uuid-of-tag",
        "tag_name": "Purchased"
    },
    "is_active": true,
    "created_at": "2026-01-26T10:00:00Z"
}
```

#### List Workflow Goals

```
GET /api/v1/workflows/{workflow_id}/goals
```

**Response (200 OK):**
```json
{
    "goals": [
        {
            "id": "uuid-of-goal-config",
            "goal_type": "tag_added",
            "criteria": {...},
            "is_active": true
        }
    ],
    "total": 1
}
```

#### Update Workflow Goal

```
PATCH /api/v1/workflows/{workflow_id}/goals/{goal_id}
```

#### Delete Workflow Goal

```
DELETE /api/v1/workflows/{workflow_id}/goals/{goal_id}
```

#### Get Goal Achievement Stats

```
GET /api/v1/workflows/{workflow_id}/goals/stats
```

**Response (200 OK):**
```json
{
    "workflow_id": "uuid-of-workflow",
    "total_enrolled": 1500,
    "goals_achieved": 450,
    "conversion_rate": 30.0,
    "avg_time_to_goal_hours": 72.5,
    "by_goal_type": {
        "tag_added": {
            "achieved": 200,
            "conversion_rate": 13.3
        },
        "purchase_made": {
            "achieved": 250,
            "conversion_rate": 16.7
        }
    }
}
```

---

## Event Architecture

### Event Flow

```
[Goal Event Source] --> [Event Bus] --> [Goal Listener Service]
                                               |
                                               v
                                    [Check Active Enrollments]
                                               |
                                               v
                                    [Evaluate Goal Criteria]
                                               |
                                               v
                              [Yes: Trigger Workflow Exit]
                              [No: Continue Workflow]
```

### Events Published

| Event | Payload | Trigger |
|-------|---------|---------|
| `workflow.goal.configured` | GoalConfig | Goal added to workflow |
| `workflow.goal.achieved` | GoalAchievement | Contact achieves goal |
| `workflow.exit.goal` | EnrollmentExit | Contact exits due to goal |

### Events Consumed

| Event | Source | Action |
|-------|--------|--------|
| `contact.tag.added` | CRM Module | Check tag_added goals |
| `payment.completed` | Payment Module | Check purchase_made goals |
| `appointment.booked` | Booking Module | Check appointment_booked goals |
| `form.submitted` | Funnel Module | Check form_submitted goals |
| `pipeline.stage.changed` | CRM Module | Check pipeline_stage_reached goals |

---

## Traceability

| Requirement | Test | Implementation |
|-------------|------|----------------|
| R1 | test_goal_configuration | GoalConfigService.create_goal() |
| R2 | test_goal_type_selection | GoalType enum, validation |
| R3 | test_tag_goal_achievement | TagGoalListener.on_tag_added() |
| R4 | test_purchase_goal_achievement | PurchaseGoalListener.on_payment() |
| R5 | test_appointment_goal_achievement | AppointmentGoalListener.on_booking() |
| R6 | test_form_goal_achievement | FormGoalListener.on_submission() |
| R7 | test_pipeline_goal_achievement | PipelineGoalListener.on_stage_change() |
| R8 | test_workflow_exit | WorkflowExitService.exit_on_goal() |
| R9 | test_listener_registration | GoalListenerManager.register() |
| R10 | test_listener_cleanup | GoalListenerManager.unregister() |
| R11 | test_multiple_goals | MultiGoalEvaluator.evaluate() |
| R12 | test_goal_analytics | GoalAnalyticsService.get_stats() |
| R13 | test_validation_errors | GoalConfigValidator.validate() |

---

## Related SPECs

- **SPEC-WFL-005:** Execute Workflow - Core workflow execution engine
- **SPEC-WFL-006:** Wait Step Processing - Wait step cancellation on goal exit
- **SPEC-WFL-009:** Workflow Analytics - Goal metrics integration
- **SPEC-CRM-001:** Contact Management - Tag operations
- **SPEC-BKG-001:** Appointment Booking - Booking event source
- **SPEC-FNL-002:** Form Submissions - Form event source
- **SPEC-PAY-001:** Payment Processing - Purchase event source
