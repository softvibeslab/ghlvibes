# SPEC-CRM-004: Activities/Tasks

## Overview

Implement activity and task management with calendar integration, reminder system, status tracking, and completion workflows for contacts, companies, and deals.

## Requirements (EARS Format)

### 1. Activity CRUD Operations

**WHEN** an authenticated user creates an activity, **THE SYSTEM** shall store activity with required fields (activity_type, title) and optional fields (description, due_date).

**THE SYSTEM** shall support activity types: call, email, meeting, task, note, sms, other.

**THE SYSTEM** shall associate activities with optional contact, company, or deal.

**THE SYSTEM** shall track activity status: pending, in_progress, completed, cancelled.

### 2. Activity Status Management

**WHEN** an activity is created, **THE SYSTEM** shall set status to PENDING.

**WHEN** an activity is started, **THE SYSTEM** shall transition status from PENDING to IN_PROGRESS.

**WHEN** an activity is completed, **THE SYSTEM** shall set status to COMPLETED and record completed_at timestamp.

**THE SYSTEM** shall prevent completing already completed activities (idempotency).

**THE SYSTEM** shall allow cancelling pending or in_progress activities (not completed).

### 3. Calendar Integration

**WHEN** an activity has a due_date, **THE SYSTEM** shall support iCal export format.

**THE SYSTEM** shall parse and validate ISO 8601 datetime formats.

**THE SYSTEM** shall support timezone-aware datetimes (stored in UTC).

**WHEN** listing activities, **THE SYSTEM** shall support date range filtering (start_date, end_date).

### 4. Activity Reminders

**WHEN** an activity has a due_date, **THE SYSTEM** shall calculate reminder timing (15 min, 1 hour, 1 day before).

**THE SYSTEM** shall send reminder notifications via configured channels (email, push, in-app).

**THE SYSTEM** shall respect user notification preferences and timezone.

**WHEN** an activity is completed or cancelled, **THE SYSTEM** shall cancel pending reminders.

### 5. Task Completion Tracking

**WHEN** an activity type is TASK, **THE SYSTEM** shall support checklist items (JSON array of strings).

**THE SYSTEM** shall track task completion percentage based on checklist items completed.

**WHEN** all checklist items are completed, **THE SYSTEM** shall auto-mark task as completed (optional behavior).

### 6. Activity Association

**THE SYSTEM** shall support linking activities to contacts (contact_id).

**THE SYSTEM** shall support linking activities to companies (company_id).

**THE SYSTEM** shall support linking activities to deals (deal_id).

**WHEN** listing activities, **THE SYSTEM** shall support filtering by association type.

## API Endpoints

### POST /api/v1/crm/activities
Create a new activity.

**Request:**
```json
{
  "activity_type": "meeting",
  "title": "Product Demo Call",
  "description": "Demo enterprise features to CTO",
  "due_date": "2024-02-15T14:00:00Z",
  "contact_id": "uuid",
  "company_id": "uuid",
  "deal_id": "uuid"
}
```

**Response:** 201 Created
```json
{
  "id": "uuid",
  "account_id": "uuid",
  "activity_type": "meeting",
  "title": "Product Demo Call",
  "description": "Demo enterprise features to CTO",
  "status": "pending",
  "due_date": "2024-02-15T14:00:00Z",
  "completed_at": null,
  "contact_id": "uuid",
  "company_id": "uuid",
  "deal_id": "uuid",
  "created_by": "uuid",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### GET /api/v1/crm/activities/{activity_id}
Get activity by ID.

### GET /api/v1/crm/activities
List activities with filters.

**Query Parameters:**
- page: int (default: 1)
- page_size: int (default: 20, max: 100)
- activity_type: enum (optional)
- status: enum (optional)
- contact_id: UUID (optional)
- company_id: UUID (optional)
- deal_id: UUID (optional)

**Response:** 200 OK with paginated activities

### PATCH /api/v1/crm/activities/{activity_id}
Update activity details.

**Request:**
```json
{
  "title": "Updated: Product Demo Call",
  "description": "New agenda",
  "due_date": "2024-02-16T15:00:00Z",
  "status": "in_progress"
}
```

### DELETE /api/v1/crm/activities/{activity_id}
Delete activity.

**Response:** 204 No Content

### POST /api/v1/crm/activities/{activity_id}/complete
Mark activity as completed.

**Response:** 200 OK with status=completed, completed_at set

### POST /api/v1/crm/activities/{activity_id}/start
Mark activity as in progress (only from pending status).

**Response:** 200 OK with status=in_progress

### POST /api/v1/crm/activities/{activity_id}/cancel
Cancel activity (only from pending or in_progress status).

**Response:** 200 OK with status=cancelled

## Database Schema

### crm_activities table

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| account_id | UUID | FK, NOT NULL, indexed |
| activity_type | ENUM | NOT NULL (call, email, meeting, task, note, sms, other) |
| title | VARCHAR(255) | NOT NULL |
| description | TEXT | nullable |
| status | ENUM | NOT NULL, default "pending" |
| due_date | TIMESTAMPTZ | nullable, indexed |
| completed_at | TIMESTAMPTZ | nullable |
| contact_id | UUID | FK to crm_contacts |
| company_id | UUID | FK to crm_companies |
| deal_id | UUID | FK to crm_deals |
| created_by | UUID | FK to users |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

**Indexes:**
- ix_crm_activities_account_id
- ix_crm_activities_due_date
- ix_crm_activities_status
- ix_crm_activities_type

**Relationships:**
- contact: Many-to-one to crm_contacts
- company: Many-to-one to crm_companies
- deal: Many-to-one to crm_deals

## Acceptance Criteria

**AC1:** User can create activity with required type and title.

**AC2:** Activity status transitions follow state machine (pending -> in_progress -> completed OR pending -> cancelled).

**AC3:** Completed activities cannot be status-changed (immutable).

**AC4:** Due dates support timezone-aware ISO 8601 format.

**AC5:** Activities can be linked to contact, company, or deal.

**AC6:** Filter activities by type, status, and association.

**AC7:** Complete activity sets completed_at timestamp.

**AC8:** Cancel activity prevents completion and sets status to cancelled.

**AC9:** List activities supports date range filtering.

**AC10:** Account isolation enforced in all activity queries.

## Testing Strategy

**Unit Tests:**
- Activity entity creation and validation
- Status transition validation
- Activity type enum validation

**Integration Tests:**
- Activity CRUD with database
- Status transitions with state tracking
- Association with contacts/companies/deals

**E2E Tests:**
- Create activity via API
- Start and complete activity
- Cancel pending activity
- Filter activities by type/status

**Test Coverage Target:** 85%+

## Dependencies

**Dependencies:**
- SPEC-CRM-001 (Contacts - activities linked to contacts)
- SPEC-CRM-002 (Pipelines & Deals - activities linked to deals)
- SPEC-CRM-003 (Companies - activities linked to companies)

**Dependent Modules:**
- SPEC-CRM-005 (Notes - activities can create notes)

## Technical Notes

**Performance Considerations:**
- Index due_date for date range queries
- Index status for filtering pending activities
- Use database aggregations for activity counts

**State Machine:**
```
PENDING -> IN_PROGRESS -> COMPLETED
    |
    v
CANCELLED
```

**Calendar Integration:**
- Generate iCal (ICS) format: `BEGIN:VCALENDAR...`
- Include UID, DTSTAMP, DTSTART, SUMMARY, DESCRIPTION
- Support webcal:// protocol for calendar subscriptions

**Reminder System:**
- Calculate reminder times: due_date - interval
- Queue reminder jobs in background task system
- Support multiple reminder intervals per activity

**Future Enhancements:**
- Recurring activities (daily, weekly, monthly)
- Activity templates for common tasks
- Activity duration tracking
- Activity reporting and analytics
- Google Calendar/Outlook integration
