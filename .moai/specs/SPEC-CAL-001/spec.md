# SPEC-CAL-001: Calendar Management

**Module**: Calendars & Bookings
**Version**: 1.0.0
**Status**: Draft
**Created**: 2026-02-07
**Dependencies**: CRM Module (Contacts)

---

## Executive Summary

Implement comprehensive calendar management system supporting multiple calendars per organization, configurable business hours, availability rules, and time zone handling. This forms the foundation for the booking and scheduling system.

---

## Business Context

### Problem Statement
Businesses need to manage multiple calendars for different purposes (e.g., sales calls, support sessions, consultations) with specific availability rules, business hours, and time zone configurations. Without proper calendar management, booking systems cannot prevent double-booking, respect business constraints, or provide accurate availability to customers.

### Goals
- Enable multiple calendars per organization with granular control
- Support flexible business hours and scheduling rules
- Handle time zone conversions accurately
- Enable calendar sharing between team members
- Provide real-time availability status

---

## Requirements (EARS Format)

### 1. Calendar CRUD Operations

**WHEN** an authenticated user with appropriate permissions creates a calendar, the system SHALL store the calendar with provided configuration and return the calendar ID.

**WHILE** creating a calendar, the system SHALL validate that required fields (name, owner_id, timezone) are present and valid.

**WHERE** a user attempts to create more than the maximum allowed calendars (50 per organization), the system SHALL return a 403 Forbidden error with clear message.

**WHEN** a calendar owner or authorized user updates calendar settings, the system SHALL persist changes and invalidate affected availability caches.

**WHEN** a calendar is deleted, the system SHALL soft-delete the calendar and mark all associated appointments as cancelled.

**IF** a calendar has future confirmed appointments, the system SHALL prevent deletion and return error with appointment count.

### 2. Business Hours Management

**WHEN** business hours are defined for a calendar, the system SHALL store recurring weekly patterns supporting multiple time ranges per day.

**WHERE** no business hours are explicitly defined, the system SHALL default to 09:00-17:00 Monday-Friday in the calendar's timezone.

**WHILE** saving business hours, the system SHALL validate that time ranges do not overlap and end times are after start times.

**WHEN** business hours are updated, the system SHALL recalculate availability slots for all future dates.

**IF** a business day has no time ranges defined, the system SHALL treat that day as unavailable.

### 3. Availability Rules

**WHEN** availability rules are created, the system SHALL support rule types: fixed_schedule, recurring_pattern, and custom_dates.

**WHILE** evaluating availability, the system SHALL apply rules in priority order: specific dates > recurring patterns > business hours.

**WHERE** multiple availability rules conflict, the system SHALL use the most restrictive rule (fewest available slots).

**WHEN** a recurring availability rule is created, the system SHALL generate slots for the next 90 days automatically.

**IF** availability rules make a calendar completely unavailable, the system SHALL mark the calendar as inactive for booking.

### 4. Time Zone Handling

**WHEN** a calendar is created, the system SHALL require a valid IANA timezone identifier (e.g., "America/New_York").

**WHILE** displaying availability, the system SHALL convert all times to the viewer's local timezone.

**WHEN** an appointment is booked, the system SHALL store times in UTC and display them in both calendar's and customer's timezones.

**WHERE** daylight saving time transitions occur, the system SHALL handle conversions correctly using timezone database data.

**IF** an invalid timezone is provided, the system SHALL return a 400 error with list of valid timezones.

### 5. Calendar Sharing

**WHEN** a calendar owner shares a calendar, the system SHALL support permission levels: view_only, book, manage, and admin.

**WHILE** checking permissions, the system SHALL validate both explicit permissions and role-based access (organization admin, team member).

**WHEN** a shared calendar is accessed, the system SHALL log access with user, timestamp, and action performed.

**WHERE** a user has view_only permission, they SHALL NOT be able to modify calendar settings or availability.

**IF** calendar sharing is revoked, the system SHALL immediately remove access and invalidate cached permissions.

---

## Domain Entities

### Calendar

```python
class Calendar:
    id: UUID
    name: str
    description: Optional[str]
    owner_id: UUID  # User ID
    organization_id: UUID
    timezone: str  # IANA timezone
    status: CalendarStatus  # active, inactive, archived
    booking_buffer_minutes: int  # Minimum time between bookings
    cancellation_lead_time_hours: int  # Min hours before appointment
    max_bookings_per_day: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    # Relationships
    business_hours: List[BusinessHour]
    availability_rules: List[AvailabilityRule]
    appointments: List[Appointment]
    shared_with: List[CalendarShare]
```

### BusinessHour

```python
class BusinessHour:
    id: UUID
    calendar_id: UUID
    day_of_week: int  # 0=Monday, 6=Sunday
    start_time: time  # In calendar's timezone
    end_time: time  # In calendar's timezone
    is_available: bool
    created_at: datetime
    updated_at: datetime
```

### AvailabilityRule

```python
class AvailabilityRule:
    id: UUID
    calendar_id: UUID
    name: str
    rule_type: AvailabilityRuleType  # fixed_schedule, recurring_pattern, custom_dates
    priority: int  # Higher = more priority
    is_active: bool

    # Fixed schedule fields
    start_date: Optional[date]
    end_date: Optional[date]

    # Recurring pattern fields
    recurrence_pattern: Optional[str]  # JSON: RRULE format
    recurrence_until: Optional[date]

    # Time slots
    time_slots: List[TimeSlot]  # One-to-many relationship

    created_at: datetime
    updated_at: datetime
```

### TimeSlot

```python
class TimeSlot:
    id: UUID
    availability_rule_id: UUID
    start_time: time
    end_time: time
    max_bookings: int  # 0 = unlimited
    slot_duration_minutes: int
    buffer_minutes: int  # Buffer after this slot
    created_at: datetime
```

### CalendarShare

```python
class CalendarShare:
    id: UUID
    calendar_id: UUID
    shared_with_id: UUID  # User ID
    shared_by_id: UUID  # User ID
    permission_level: PermissionLevel  # view_only, book, manage, admin
    expires_at: Optional[datetime]
    created_at: datetime
    revoked_at: Optional[datetime]

    class PermissionLevel(Enum):
        VIEW_ONLY = "view_only"
        BOOK = "book"
        MANAGE = "manage"
        ADMIN = "admin"
```

---

## API Design

### Calendar Management

#### POST /api/v1/calendars
Create a new calendar.

**Request:**
```json
{
  "name": "Sales Consultations",
  "description": "Calendar for sales team calls",
  "timezone": "America/New_York",
  "booking_buffer_minutes": 15,
  "cancellation_lead_time_hours": 24,
  "max_bookings_per_day": 10,
  "business_hours": [
    {"day_of_week": 0, "start_time": "09:00", "end_time": "17:00", "is_available": true},
    {"day_of_week": 1, "start_time": "09:00", "end_time": "17:00", "is_available": true},
    {"day_of_week": 2, "start_time": "09:00", "end_time": "17:00", "is_available": true},
    {"day_of_week": 3, "start_time": "09:00", "end_time": "17:00", "is_available": true},
    {"day_of_week": 4, "start_time": "09:00", "end_time": "17:00", "is_available": true}
  ]
}
```

**Response:** 201 Created
```json
{
  "id": "uuid",
  "name": "Sales Consultations",
  "owner": {...},
  "organization": {...},
  "status": "active",
  "created_at": "2026-02-07T10:00:00Z"
}
```

#### GET /api/v1/calendars
List calendars for current user/organization.

**Query Params:**
- `include_shared`: boolean (default: false)
- `status`: filter by status
- `page`: pagination
- `limit`: results per page

**Response:** 200 OK
```json
{
  "data": [...],
  "pagination": {"total": 10, "page": 1, "limit": 20}
}
```

#### GET /api/v1/calendars/{calendar_id}
Get calendar details with all settings.

**Response:** 200 OK with full calendar object including business_hours and availability_rules.

#### PUT /api/v1/calendars/{calendar_id}
Update calendar settings.

**Request:** Partial update allowed.

**Response:** 200 OK with updated calendar.

#### DELETE /api/v1/calendars/{calendar_id}
Soft-delete a calendar.

**Response:** 204 No Content (or 409 Conflict if has future appointments).

### Business Hours

#### PUT /api/v1/calendars/{calendar_id}/business-hours
Set business hours for a calendar.

**Request:**
```json
{
  "business_hours": [
    {"day_of_week": 0, "start_time": "09:00", "end_time": "17:00"},
    ...
  ]
}
```

**Response:** 200 OK with updated business hours.

### Availability Rules

#### POST /api/v1/calendars/{calendar_id}/availability-rules
Create availability rule.

**Request:**
```json
{
  "name": "Summer Hours",
  "rule_type": "recurring_pattern",
  "priority": 10,
  "start_date": "2026-06-01",
  "end_date": "2026-08-31",
  "recurrence_pattern": "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR",
  "time_slots": [
    {
      "start_time": "08:00",
      "end_time": "15:00",
      "max_bookings": 5,
      "slot_duration_minutes": 30
    }
  ]
}
```

**Response:** 201 Created with rule details.

#### GET /api/v1/calendars/{calendar_id}/availability-rules
List availability rules.

#### PUT /api/v1/calendars/{calendar_id}/availability-rules/{rule_id}
Update availability rule.

#### DELETE /api/v1/calendars/{calendar_id}/availability-rules/{rule_id}
Delete availability rule.

### Calendar Sharing

#### POST /api/v1/calendars/{calendar_id}/shares
Share calendar with user.

**Request:**
```json
{
  "shared_with_id": "user-uuid",
  "permission_level": "book",
  "expires_at": "2026-12-31T23:59:59Z"
}
```

**Response:** 201 Created

#### GET /api/v1/calendars/{calendar_id}/shares
List calendar shares.

#### DELETE /api/v1/calendars/{calendar_id}/shares/{share_id}
Revoke calendar share.

---

## Database Schema

```sql
-- Calendars table
CREATE TABLE calendars (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id UUID NOT NULL REFERENCES users(id),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    timezone VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    booking_buffer_minutes INT NOT NULL DEFAULT 0,
    cancellation_lead_time_hours INT NOT NULL DEFAULT 24,
    max_bookings_per_day INT NOT NULL DEFAULT 10,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,

    CONSTRAINT valid_timezone CHECK (timezone ~* '^[A-Z]+/[A-Z_]+$')
);

CREATE INDEX idx_calendars_owner ON calendars(owner_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_calendars_organization ON calendars(organization_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_calendars_status ON calendars(status) WHERE deleted_at IS NULL;

-- Business hours
CREATE TABLE business_hours (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    calendar_id UUID NOT NULL REFERENCES calendars(id) ON DELETE CASCADE,
    day_of_week INT NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_time_range CHECK (end_time > start_time),
    UNIQUE(calendar_id, day_of_week)
);

CREATE INDEX idx_business_hours_calendar ON business_hours(calendar_id);

-- Availability rules
CREATE TABLE availability_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    calendar_id UUID NOT NULL REFERENCES calendars(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    rule_type VARCHAR(50) NOT NULL,
    priority INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    start_date DATE,
    end_date DATE,
    recurrence_pattern TEXT,
    recurrence_until DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_rule_type CHECK (rule_type IN ('fixed_schedule', 'recurring_pattern', 'custom_dates')),
    CONSTRAINT valid_dates CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE INDEX idx_availability_rules_calendar ON availability_rules(calendar_id);
CREATE INDEX idx_availability_rules_active ON availability_rules(is_active) WHERE is_active = true;

-- Time slots
CREATE TABLE time_slots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    availability_rule_id UUID NOT NULL REFERENCES availability_rules(id) ON DELETE CASCADE,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    max_bookings INT NOT NULL DEFAULT 0,
    slot_duration_minutes INT NOT NULL,
    buffer_minutes INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_slot_range CHECK (end_time > start_time),
    CONSTRAINT positive_duration CHECK (slot_duration_minutes > 0)
);

CREATE INDEX idx_time_slots_rule ON time_slots(availability_rule_id);

-- Calendar shares
CREATE TABLE calendar_shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    calendar_id UUID NOT NULL REFERENCES calendars(id) ON DELETE CASCADE,
    shared_with_id UUID NOT NULL REFERENCES users(id),
    shared_by_id UUID NOT NULL REFERENCES users(id),
    permission_level VARCHAR(20) NOT NULL,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at TIMESTAMPTZ,

    CONSTRAINT valid_permission CHECK (permission_level IN ('view_only', 'book', 'manage', 'admin')),
    UNIQUE(calendar_id, shared_with_id) WHERE revoked_at IS NULL
);

CREATE INDEX idx_calendar_shares_calendar ON calendar_shares(calendar_id) WHERE revoked_at IS NULL;
CREATE INDEX idx_calendar_shares_user ON calendar_shares(shared_with_id) WHERE revoked_at IS NULL;
```

---

## Acceptance Criteria

### AC1: Calendar Creation
- GIVEN an authenticated user
- WHEN they create a calendar with valid data
- THEN the calendar is created with unique ID
- AND business hours are stored
- AND response includes full calendar details
- AND 201 status code is returned

### AC2: Business Hours Validation
- GIVEN a calendar with existing business hours
- WHEN user updates with overlapping time ranges
- THEN 400 error is returned
- AND error message indicates the conflict
- AND no changes are persisted

### AC3: Timezone Handling
- GIVEN a calendar in "America/Los_Angeles" timezone
- WHEN a user in "Europe/London" views availability
- THEN all times are displayed in London timezone
- AND bookings are stored in UTC
- AND daylight saving transitions are handled correctly

### AC4: Calendar Sharing
- GIVEN a calendar owner
- WHEN they share calendar with view_only permission
- THEN the shared user can view but not modify
- AND access attempts to modify return 403 Forbidden
- AND access logs are created

### AC5: Availability Priority
- GIVEN multiple availability rules
- WHEN evaluating availability for a specific date
- THEN rules are applied in priority order
- AND specific date rules override recurring patterns
- AND recurring patterns override business hours

### AC6: Soft Delete Prevention
- GIVEN a calendar with confirmed future appointments
- WHEN owner attempts to delete
- THEN 409 Conflict is returned
- AND response includes count of future appointments
- AND calendar remains active

---

## Technical Approach

### Technology Stack
- **Backend**: FastAPI 0.115+ with async/await
- **Database**: PostgreSQL 16 with Supabase
- **ORM**: SQLAlchemy 2.0 async
- **Validation**: Pydantic v2.9
- **Timezone**: pytz/zoneinfo for timezone handling
- **Testing**: pytest-asyncio with 85%+ coverage

### Architecture Pattern
- **Repository Pattern**: Separate business logic from data access
- **Service Layer**: CalendarService, AvailabilityService, ShareService
- **Dependency Injection**: FastAPI Depends for session injection
- **Caching**: Redis for availability slot caching (TTL: 1 hour)

### Key Implementation Points

1. **Timezone Handling**:
   - Store all datetimes in UTC
   - Use zoneinfo for Python 3.12+ timezone support
   - Convert to user's timezone on read

2. **Availability Calculation**:
   - Pre-calculate slots for 90 days
   - Cache results in Redis
   - Invalidate cache on rules/business hours update

3. **Permission System**:
   - Check permissions on every access
   - Cache permissions in Redis (short TTL)
   - Log all access for audit trail

4. **Validation**:
   - Pydantic models for request validation
   - Custom validators for business rules
   - Database constraints for data integrity

---

## Testing Strategy

### Unit Tests
- Calendar CRUD operations
- Business hours validation logic
- Availability rule priority sorting
- Timezone conversion functions
- Permission checking logic

### Integration Tests
- API endpoint testing with test database
- Business hours update triggers availability recalculation
- Calendar sharing flow with permissions
- Soft delete with appointment conflict detection

### E2E Tests
- User creates calendar and books first appointment
- Calendar sharing and permission enforcement
- Timezone conversion across multiple regions
- Availability calculation with complex rules

---

## Success Metrics

- All API endpoints return < 200ms (p95)
- Availability calculation completes < 100ms
- Timezone conversions are 100% accurate
- 85%+ test coverage achieved
- Zero data integrity violations in production

---

**Next SPEC**: SPEC-CAL-002 (Appointments)
