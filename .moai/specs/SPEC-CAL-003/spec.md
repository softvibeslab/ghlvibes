# SPEC-CAL-003: Availability Management

**Module**: Calendars & Bookings
**Version**: 1.0.0
**Status**: Draft
**Created**: 2026-02-07
**Dependencies**: SPEC-CAL-001 (Calendar Management), SPEC-CAL-002 (Appointments)

---

## Executive Summary

Implement advanced availability management system supporting dynamic slot generation, recurring availability patterns, buffer times between appointments, break time scheduling, and blackout date management. This ensures customers see accurate, up-to-date availability when booking.

---

## Business Context

### Problem Statement
Basic availability rules are insufficient for complex scheduling needs. Businesses need to configure buffer times between appointments, schedule breaks, block out dates for holidays or vacations, and define recurring availability patterns that change seasonally. Without advanced availability management, booking systems cannot accurately represent real-world scheduling constraints.

### Goals
- Enable dynamic slot generation based on complex availability rules
- Support configurable buffer times to prevent back-to-back bookings
- Allow break time scheduling within available periods
- Implement blackout dates for holidays, vacations, or events
- Optimize slot generation for performance with caching

---

## Requirements (EARS Format)

### 1. Slot Generation

**WHEN** availability is queried for a calendar, the system SHALL generate available slots based on:
- Business hours (base availability)
- Recurring availability patterns (exceptions to business hours)
- Specific date rules (one-time overrides)
- Existing appointments (subtract booked slots)

**WHILE** generating slots, the system SHALL apply all configured rules in priority order:
1. Specific date rules (highest priority)
2. Recurring patterns (medium priority)
3. Business hours (base priority)

**WHERE** multiple rules would create overlapping slots, the system SHALL merge them into single continuous availability periods.

**WHEN** slot generation is requested, the system SHALL support date ranges up to 90 days in the future.

**IF** no availability is found for the requested period, the system SHALL return empty result with message indicating next available date.

### 2. Buffer Time Management

**WHEN** appointments are booked, the system SHALL reserve the appointment slot plus buffer time before and/or after.

**WHILE** calculating availability, the system SHALL ensure that buffer times do not overlap with adjacent slots.

**WHERE** buffer times are configured, the system SHALL:
- Treat buffer time as unavailable for new bookings
- Include buffer time in appointment duration
- Display buffer time in calendar views (distinct from appointments)

**WHEN** buffer times are defined globally versus per-slot, the system SHALL use per-slot configuration if available, otherwise fall back to global setting.

**IF** a slot's buffer time would extend beyond business hours, the system SHALL truncate the slot to fit within available time.

### 3. Break Time Scheduling

**WHEN** a calendar owner defines break times, the system SHALL remove those periods from generated availability slots.

**WHILE** processing breaks, the system SHALL support:
- Fixed daily breaks (e.g., lunch hour 12-1pm)
- Recurring breaks (e.g., every Monday for team meeting)
- One-time breaks (e.g., dentist appointment)

**WHERE** breaks overlap with appointments, the system SHALL allow existing appointments but prevent new bookings during break times.

**WHEN** break times are updated, the system SHALL regenerate affected availability slots.

**IF** break times render a day completely unavailable, the system SHALL exclude that day from availability results.

### 4. Blackout Dates

**WHEN** a calendar owner creates blackout dates, the system SHALL mark entire days or date ranges as unavailable.

**WHILE** processing blackout dates, the system SHALL support:
- Single-day blackout (e.g., public holiday)
- Date range blackout (e.g., vacation week)
- Recurring annual blackout (e.g., Christmas week every year)

**WHERE** blackout dates conflict with existing appointments, the system SHALL:
- Keep existing appointments unchanged
- Prevent new bookings during blackout period
- Display blackout reason in calendar view

**WHEN** blackout dates are created, the system SHALL invalidate cached availability for affected period.

**IF** a blackout date is deleted, the system SHALL immediately make those dates available for booking (subject to other rules).

### 5. Recurring Availability Patterns

**WHEN** creating recurring availability, the system SHALL support RRULE (RFC 5545) format for defining patterns:
- Daily, weekly, monthly, yearly recurrence
- Complex patterns (e.g., "every Monday and Wednesday")
- Recurrence end dates or count limits

**WHILE** evaluating recurring patterns, the system SHALL expand patterns for the query date range (up to 90 days).

**WHERE** recurring patterns overlap with business hours, the system SHALL use the more restrictive rule.

**WHEN** a recurring pattern is edited, the system SHALL:
- Update future occurrences
- Option to apply changes to past occurrences (with confirmation)
- Invalidate affected cached slots

**IF** a recurring pattern has no end date, the system SHALL apply it indefinitely when generating slots.

### 6. Availability Caching

**WHEN** availability slots are generated for a calendar and date range, the system SHALL cache results in Redis.

**WHILE** caching, the system SHALL use cache key format: `availability:{calendar_id}:{start_date}:{end_date}`.

**WHERE** calendar settings change (business hours, rules, appointments), the system SHALL invalidate relevant cache entries.

**WHEN** cache hit occurs, the system SHALL return cached results without regenerating slots.

**IF** cache is stale due to setting changes, the system SHALL detect and regenerate fresh slots.

### 7. Real-Time Availability Updates

**WHEN** an appointment is booked, cancelled, or rescheduled, the system SHALL immediately update availability for affected dates.

**WHILE** updating availability, the system SHALL use WebSocket connections to push updates to connected clients viewing availability.

**WHERE** multiple clients are viewing same calendar, the system SHALL broadcast availability change to all subscribers.

**WHEN** appointment booking occurs, the system SHALL:
- Remove booked slot from availability
- Push updated availability to all viewers
- Update cache for affected date range

**IF** real-time updates fail, the system SHALL fall back to periodic refresh (client-side polling every 30 seconds).

---

## Domain Entities

### AvailabilitySlot

```python
class AvailabilitySlot:
    id: UUID
    calendar_id: UUID
    start_time: datetime  # UTC
    end_time: datetime  # UTC
    duration_minutes: int
    is_available: bool

    # Buffer times
    buffer_before_minutes: int
    buffer_after_minutes: int

    # Capacity
    max_bookings: int  # 0 = unlimited
    current_bookings: int

    # Scheduling rules that created this slot
    source_rule_id: Optional[UUID]  # AvailabilityRule that generated this
    source_type: SlotSourceType  # business_hours, recurring_pattern, specific_date

    # Metadata
    date: date  # Local date in calendar's timezone
    created_at: datetime
    expires_at: datetime  # When this slot data should be refreshed

    class SlotSourceType(Enum):
        BUSINESS_HOURS = "business_hours"
        RECURRING_PATTERN = "recurring_pattern"
        SPECIFIC_DATE = "specific_date"
```

### BufferTime

```python
class BufferTime:
    id: UUID
    calendar_id: UUID
    buffer_type: BufferType  # before, after, both
    duration_minutes: int
    applies_to: List[str]  # Appointment types this applies to (empty = all)
    priority: int  # For overlapping rules
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class BufferType(Enum):
        BEFORE = "before"
        AFTER = "after"
        BOTH = "both"
```

### BreakTime

```python
class BreakTime:
    id: UUID
    calendar_id: UUID
    name: str
    break_type: BreakType  # fixed_daily, recurring, one_time

    # Timing
    start_time: time  # For daily/recurring
    end_time: time
    day_of_week: Optional[int]  # For recurring breaks

    # Date range
    start_date: Optional[date]
    end_date: Optional[date]

    # Recurrence
    recurrence_pattern: Optional[str]  # RRULE format

    is_active: bool
    created_at: datetime
    updated_at: datetime

    class BreakType(Enum):
        FIXED_DAILY = "fixed_daily"
        RECURRING = "recurring"
        ONE_TIME = "one_time"
```

### BlackoutDate

```python
class BlackoutDate:
    id: UUID
    calendar_id: UUID
    name: str
    start_date: date
    end_date: date  # Same as start_date for single day
    recurrence: Optional[str]  # RRULE for recurring annual blackout
    reason: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

### SlotGenerationCache

```python
class SlotGenerationCache:
    calendar_id: UUID
    start_date: date
    end_date: date
    cache_key: str
    slot_count: int
    generated_at: datetime
    expires_at: datetime
    version: int  # Incremented when settings change
```

---

## API Design

### Availability Query

#### GET /api/v1/calendars/{calendar_id}/availability
Query available slots for booking.

**Query Params:**
- `start_date`: Start of date range (ISO 8601 date, required)
- `end_date`: End of date range (ISO 8601 date, required)
- `timezone`: Timezone for display (default: calendar's timezone)
- `duration_minutes`: Filter slots by minimum duration (optional)
- `include_buffer`: Include buffer times in response (default: false)

**Response:** 200 OK
```json
{
  "calendar_id": "uuid",
  "start_date": "2026-02-15",
  "end_date": "2026-02-21",
  "timezone": "America/New_York",
  "slots": [
    {
      "id": "uuid",
      "start_time": "2026-02-15T09:00:00-05:00",
      "end_time": "2026-02-15T09:30:00-05:00",
      "duration_minutes": 30,
      "is_available": true,
      "buffer_before_minutes": 0,
      "buffer_after_minutes": 15,
      "max_bookings": 1,
      "current_bookings": 0
    },
    {
      "id": "uuid",
      "start_time": "2026-02-15T09:45:00-05:00",
      "end_time": "2026-02-15T10:15:00-05:00",
      "duration_minutes": 30,
      "is_available": true,
      "buffer_before_minutes": 15,
      "buffer_after_minutes": 15,
      "max_bookings": 1,
      "current_bookings": 0
    }
  ],
  "unavailable_dates": ["2026-02-18", "2026-02-19"],
  "next_available_date": "2026-02-20",
  "generated_at": "2026-02-07T10:00:00Z",
  "cached": true
}
```

**Error Response:** 400 Bad Request (invalid date range)
```json
{
  "error": "invalid_date_range",
  "message": "Date range cannot exceed 90 days",
  "max_days": 90
}
```

### Buffer Time Management

#### POST /api/v1/calendars/{calendar_id}/buffer-times
Create buffer time rule.

**Request:**
```json
{
  "buffer_type": "after",
  "duration_minutes": 15,
  "applies_to": ["consultation", "demo"],
  "priority": 10
}
```

**Response:** 201 Created

#### GET /api/v1/calendars/{calendar_id}/buffer-times
List buffer time rules.

#### PUT /api/v1/calendars/{calendar_id}/buffer-times/{buffer_id}
Update buffer time rule.

#### DELETE /api/v1/calendars/{calendar_id}/buffer-times/{buffer_id}
Delete buffer time rule.

### Break Time Management

#### POST /api/v1/calendars/{calendar_id}/break-times
Create break time.

**Request:**
```json
{
  "name": "Lunch Break",
  "break_type": "fixed_daily",
  "start_time": "12:00",
  "end_time": "13:00",
  "is_active": true
}
```

**Response:** 201 Created

#### POST /api/v1/calendars/{calendar_id}/break-times/recurring
Create recurring break time.

**Request:**
```json
{
  "name": "Team Meeting",
  "break_type": "recurring",
  "day_of_week": 0,  // Monday
  "start_time": "10:00",
  "end_time": "11:00",
  "start_date": "2026-02-01",
  "end_date": "2026-06-30",
  "is_active": true
}
```

**Response:** 201 Created

#### GET /api/v1/calendars/{calendar_id}/break-times
List break times.

#### PUT /api/v1/calendars/{calendar_id}/break-times/{break_id}
Update break time.

#### DELETE /api/v1/calendars/{calendar_id}/break-times/{break_id}
Delete break time.

### Blackout Date Management

#### POST /api/v1/calendars/{calendar_id}/blackout-dates
Create blackout date.

**Request:**
```json
{
  "name": "Office Closed for Holidays",
  "start_date": "2026-12-24",
  "end_date": "2026-12-26",
  "reason": "Holiday closure",
  "recurrence": "FREQ=YEARLY"
}
```

**Response:** 201 Created

#### GET /api/v1/calendars/{calendar_id}/blackout-dates
List blackout dates.

**Query Params:**
- `start_date`: Filter start date
- `end_date`: Filter end date
- `include_recurring`: Include recurring blackouts

#### PUT /api/v1/calendars/{calendar_id}/blackout-dates/{blackout_id}
Update blackout date.

#### DELETE /api/v1/calendars/{calendar_id}/blackout-dates/{blackout_id}
Delete blackout date.

### Slot Regeneration

#### POST /api/v1/calendars/{calendar_id}/availability/regenerate
Force regeneration of availability slots (invalidates cache).

**Request:**
```json
{
  "start_date": "2026-02-15",
  "end_date": "2026-02-21"
}
```

**Response:** 202 Accepted
```json
{
  "message": "Slot regeneration initiated",
  "job_id": "uuid"
}
```

---

## Database Schema

```sql
-- Availability slots (generated, not manually created)
CREATE TABLE availability_slots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    calendar_id UUID NOT NULL REFERENCES calendars(id),
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    duration_minutes INT NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT true,

    -- Buffer times
    buffer_before_minutes INT NOT NULL DEFAULT 0,
    buffer_after_minutes INT NOT NULL DEFAULT 0,

    -- Capacity
    max_bookings INT NOT NULL DEFAULT 1,
    current_bookings INT NOT NULL DEFAULT 0,

    -- Source
    source_rule_id UUID REFERENCES availability_rules(id),
    source_type VARCHAR(50) NOT NULL,

    -- Metadata
    date DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,

    CONSTRAINT valid_source_type CHECK (source_type IN ('business_hours', 'recurring_pattern', 'specific_date')),
    CONSTRAINT positive_duration CHECK (duration_minutes > 0),
    CONSTRAINT valid_time_range CHECK (end_time > start_time)
);

CREATE INDEX idx_slots_calendar_date ON availability_slots(calendar_id, date);
CREATE INDEX idx_slots_time_range ON availability_slots(start_time, end_time);
CREATE INDEX idx_slots_available ON availability_slots(is_available) WHERE is_available = true;
CREATE INDEX idx_slots_expires ON availability_slots(expires_at);

-- Buffer times
CREATE TABLE buffer_times (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    calendar_id UUID NOT NULL REFERENCES calendars(id) ON DELETE CASCADE,
    buffer_type VARCHAR(20) NOT NULL,
    duration_minutes INT NOT NULL,
    applies_to JSONB,  -- Array of appointment types
    priority INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_buffer_type CHECK (buffer_type IN ('before', 'after', 'both')),
    CONSTRAINT positive_buffer CHECK (duration_minutes >= 0)
);

CREATE INDEX idx_buffer_calendar ON buffer_times(calendar_id) WHERE is_active = true;

-- Break times
CREATE TABLE break_times (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    calendar_id UUID NOT NULL REFERENCES calendars(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    break_type VARCHAR(20) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    day_of_week INT CHECK (day_of_week BETWEEN 0 AND 6),
    start_date DATE,
    end_date DATE,
    recurrence_pattern TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_break_type CHECK (break_type IN ('fixed_daily', 'recurring', 'one_time')),
    CONSTRAINT valid_break_time CHECK (end_time > start_time),
    CONSTRAINT valid_dates CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE INDEX idx_breaks_calendar ON break_times(calendar_id) WHERE is_active = true;
CREATE INDEX idx_breaks_type_day ON break_times(calendar_id, day_of_week) WHERE is_active = true AND break_type = 'recurring';
CREATE INDEX idx_breaks_date_range ON break_times(calendar_id, start_date, end_date) WHERE is_active = true;

-- Blackout dates
CREATE TABLE blackout_dates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    calendar_id UUID NOT NULL REFERENCES calendars(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    recurrence TEXT,  -- RRULE for recurring blackouts
    reason TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_date_range CHECK (end_date >= start_date)
);

CREATE INDEX idx_blackout_calendar ON blackout_dates(calendar_id) WHERE is_active = true;
CREATE INDEX idx_blackout_date_range ON blackout_dates(start_date, end_date) WHERE is_active = true;
```

---

## Acceptance Criteria

### AC1: Slot Generation Accuracy
- GIVEN a calendar with business hours 9-5 Mon-Fri
- WHEN availability is queried for next week
- THEN slots are generated for each day 9-5
- AND slots respect buffer times
- AND weekend days are excluded
- AND duration matches configured slot duration

### AC2: Buffer Time Application
- GIVEN calendar with 15-minute buffer after appointments
- WHEN appointment is booked at 9:00-9:30
- THEN next available slot starts at 9:45 (9:30 + 15min buffer)
- AND 9:30-9:45 period is marked as unavailable

### AC3: Break Time Exclusion
- GIVEN calendar with lunch break 12-1pm daily
- WHEN availability is generated
- THEN no slots overlap with 12-1pm
- AND morning slots end by 12:00
- AND afternoon slots start at 13:00

### AC4: Blackout Date Effect
- GIVEN blackout date for December 25
- WHEN availability includes that date
- THEN December 25 shows as unavailable
- AND reason "Holiday closure" is displayed
- AND no slots are generated for that day

### AC5: Recurring Pattern Expansion
- GIVEN recurring availability every Monday and Wednesday
- WHEN slots are generated for 90 days
- THEN slots appear on all Mondays and Wednesdays
- AND no slots on other days (unless business hours apply)
- AND pattern respects end date if configured

### AC6: Cache Invalidation
- GIVEN cached availability for February 15-21
- WHEN business hours are updated for that period
- THEN cache is invalidated
- AND subsequent queries regenerate slots
- AND new slots reflect updated business hours

### AC7: Real-Time Update
- GIVEN two users viewing availability calendar
- WHEN one user books an appointment
- THEN other user's view updates immediately
- AND booked slot disappears from availability
- AND notification shows "1 slot just booked"

### AC8: Performance with Caching
- GIVEN 1000 slots cached for calendar
- WHEN availability query matches cached range
- THEN response returns in < 50ms
- AND cache hit is logged
- AND slots are not regenerated

---

## Technical Approach

### Technology Stack
- **Backend**: FastAPI with async/await
- **Caching**: Redis with TTL-based expiration
- **Real-Time**: WebSocket connections for live updates
- **Task Queue**: Background tasks for slot generation
- **Date/Time**: Python zoneinfo for timezone handling
- **Recurrence**: dateutil library for RRULE parsing

### Architecture Pattern
- **Service Layer**: AvailabilityService, SlotGenerationService, CacheService
- **Strategy Pattern**: Different slot generation strategies per source type
- **Observer Pattern**: WebSocket subscribers receive availability updates
- **Cache-Aside**: Generate slots, cache, then serve from cache

### Key Implementation Points

1. **Slot Generation Algorithm**:
   - Start with business hours (base availability)
   - Apply recurring patterns (add/override)
   - Apply specific date rules (highest priority)
   - Subtract break times
   - Subtract blackout dates
   - Subtract existing appointments
   - Apply buffer times to remaining slots
   - Split continuous availability into discrete slots

2. **Cache Management**:
   - Cache key: `availability:{calendar_id}:{start_date}:{end_date}:{version}`
   - Version increments on settings change
   - TTL: 1 hour for volatile calendars, 24 hours for static
   - Invalidation on appointment create/update/delete

3. **Real-Time Updates**:
   - WebSocket connection per calendar view
   - Broadcast on appointment lifecycle events
   - Optimistic updates with rollback on failure
   - Fallback to 30-second polling if WebSocket fails

4. **Performance Optimization**:
   - Pre-generate slots for next 90 days
   - Use database indexes for date range queries
   - Batch slot generation (1 week at a time)
   - Lazy load slots beyond 90 days

---

## Testing Strategy

### Unit Tests
- Slot generation algorithm with various rule combinations
- Buffer time calculation logic
- Break time subtraction logic
- Blackout date application
- Recurring pattern expansion (RRULE parsing)
- Cache key generation and validation

### Integration Tests
- Availability API with database queries
- Cache read/write with Redis
- WebSocket connection and message broadcasting
- Slot regeneration background tasks
- Real-time update flow

### E2E Tests
- User queries availability, books appointment, sees real-time update
- Admin updates business hours, availability regenerates
- Blackout date created, slots disappear for that period
- Break time added, slots adjust around break
- Recurring pattern created, slots appear on specified days

---

## Success Metrics

- Slot generation completes < 500ms for 90-day range
- Cache hit rate > 80%
- Real-time updates delivered < 1 second
- Zero inaccurate availability shown to customers
- 85%+ test coverage achieved
- Availability API p95 latency < 200ms

---

**Next SPEC**: SPEC-CAL-004 (Booking Widgets)
