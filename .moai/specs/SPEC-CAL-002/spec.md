# SPEC-CAL-002: Appointments

**Module**: Calendars & Bookings
**Version**: 1.0.0
**Status**: Draft
**Created**: 2026-02-07
**Dependencies**: SPEC-CAL-001 (Calendar Management), CRM Module (Contacts)

---

## Executive Summary

Implement comprehensive appointment booking and management system supporting appointment lifecycle management, confirmation emails, reminder notifications, cancellation handling, and rescheduling capabilities.

---

## Business Context

### Problem Statement
Businesses need a complete appointment management system to handle bookings, send confirmations and reminders, manage cancellations and rescheduling, and maintain appointment history. Manual appointment management leads to missed appointments, scheduling conflicts, and poor customer experience.

### Goals
- Enable seamless appointment booking workflow
- Automate confirmation and reminder communications
- Handle appointment lifecycle changes (cancel, reschedule, no-show)
- Prevent double-booking and scheduling conflicts
- Provide comprehensive appointment history and analytics

---

## Requirements (EARS Format)

### 1. Appointment Booking

**WHEN** a customer books an available slot, the system SHALL create an appointment and reserve the time slot.

**WHILE** booking, the system SHALL validate that the slot is still available (handle race conditions).

**WHERE** the selected time slot is within the cancellation lead time window, the system SHALL prevent booking and return alternative available slots.

**WHEN** an appointment is successfully booked, the system SHALL:
- Send confirmation email to customer
- Send notification to calendar owner
- Update slot availability
- Create appointment record with status "confirmed"

**IF** booking fails due to slot becoming unavailable, the system SHALL return 409 Conflict with available alternatives.

### 2. Appointment Confirmation

**WHEN** an appointment is created, the system SHALL immediately send confirmation email containing:
- Appointment date and time (in customer's timezone)
- Calendar/business name
- Location or meeting link
- Contact information
- Cancellation policy
- Add to calendar links (Google, Outlook, iCal)

**WHILE** sending confirmation, the system SHALL support multiple email templates based on appointment type.

**WHERE** email sending fails, the system SHALL retry 3 times with exponential backoff and log the failure.

**IF** confirmation email cannot be delivered after retries, the system SHALL mark appointment as "confirmation_failed" and notify support.

### 3. Appointment Reminders

**WHEN** an appointment is booked, the system SHALL schedule reminder notifications based on calendar settings.

**WHILE** scheduling reminders, the system SHALL support:
- Email reminders (default: 24 hours and 1 hour before)
- SMS reminders (if enabled)
- Push notifications (for web/app users)

**WHERE** multiple reminders are configured, the system SHALL send each at the specified interval.

**WHEN** appointment is cancelled or rescheduled, the system SHALL cancel pending reminders.

**IF** reminder sending fails, the system SHALL log the error and continue with subsequent reminders.

### 4. Appointment Cancellation

**WHEN** a customer cancels an appointment, the system SHALL:
- Update appointment status to "cancelled"
- Release the reserved time slot
- Send cancellation confirmation email
- Refund payment if applicable
- Log cancellation reason

**WHILE** processing cancellation, the system SHALL check cancellation policy:
- Within allowed window → Allow cancellation with possible refund
- Outside allowed window → Block cancellation or apply penalty

**WHERE** calendar owner cancels, the system SHALL notify customer immediately and offer to reschedule.

**IF** cancellation occurs within minimum notice period, the system MAY apply cancellation fee and mark as "late_cancel".

### 5. Appointment Rescheduling

**WHEN** a customer requests to reschedule, the system SHALL:
- Check cancellation policy for current appointment
- Show available alternative slots
- Hold current slot while customer selects new time
- Release current slot when new appointment is confirmed

**WHILE** rescheduling, the system SHALL validate that:
- New time is available
- New time respects booking buffer
- New time is within allowed rescheduling window

**WHERE** rescheduling is initiated by calendar owner, the system SHALL notify customer of change and require confirmation.

**IF** new slot cannot be found, the system SHALL offer closest available alternatives.

### 6. Appointment Status Management

**WHEN** appointment lifecycle events occur, the system SHALL update status accordingly:
- "pending" → Initial state (if payment required)
- "confirmed" → Booking confirmed
- "cancelled" → Cancelled by any party
- "completed" → Appointment time passed
- "no_show" → Customer did not attend
- "late_cancel" → Cancelled within notice period

**WHILE** updating status, the system SHALL trigger appropriate notifications and workflows.

**WHERE** appointment time passes without completion, the system SHALL auto-mark as "completed" or "no_show" based on check-in data.

**IF** status change requires notification, the system SHALL send relevant emails to all parties.

### 7. Appointment History and Analytics

**WHEN** retrieving appointments, the system SHALL support filtering by:
- Date range
- Status
- Calendar
- Customer
- Appointment type

**WHILE** generating analytics, the system SHALL calculate:
- Total appointments by period
- Cancellation rate
- No-show rate
- Average booking lead time
- Revenue per appointment type

**WHERE** pagination is required, the system SHALL use cursor-based pagination for performance.

---

## Domain Entities

### Appointment

```python
class Appointment:
    id: UUID
    calendar_id: UUID
    slot_id: UUID  # Reference to reserved slot
    customer_id: UUID  # Contact from CRM
    customer_email: str
    customer_phone: Optional[str]
    customer_name: str

    # Timing
    start_time: datetime  # UTC
    end_time: datetime  # UTC
    duration_minutes: int
    timezone: str  # Customer's timezone

    # Status and lifecycle
    status: AppointmentStatus
    cancellation_reason: Optional[str]
    cancelled_by: Optional[UUID]  # User ID
    cancelled_at: Optional[datetime]

    # Rescheduling
    rescheduled_from_id: Optional[UUID]  # Previous appointment ID
    rescheduled_to_id: Optional[UUID]  # New appointment ID

    # Metadata
    appointment_type: str  # e.g., "consultation", "support", "demo"
    notes: Optional[str]
    location_type: LocationType  # in_person, virtual, phone
    location_address: Optional[str]
    meeting_link: Optional[str]
    meeting_provider: Optional[str]  # zoom, google_meet, teams

    # Payment (optional)
    payment_required: bool
    payment_amount: Optional[Decimal]
    payment_status: Optional[PaymentStatus]
    payment_id: Optional[str]

    # Reminders
    reminders_sent: List[datetime]

    # Audit
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime]
    completed_at: Optional[datetime]

    class AppointmentStatus(Enum):
        PENDING = "pending"
        CONFIRMED = "confirmed"
        CANCELLED = "cancelled"
        COMPLETED = "completed"
        NO_SHOW = "no_show"
        LATE_CANCEL = "late_cancel"

    class LocationType(Enum):
        IN_PERSON = "in_person"
        VIRTUAL = "virtual"
        PHONE = "phone"
```

### AppointmentReminder

```python
class AppointmentReminder:
    id: UUID
    appointment_id: UUID
    reminder_type: ReminderType  # email, sms, push
    scheduled_for: datetime  # When to send
    sent_at: Optional[datetime]
    status: ReminderStatus  # pending, sent, failed

    class ReminderType(Enum):
        EMAIL = "email"
        SMS = "sms"
        PUSH = "push"

    class ReminderStatus(Enum):
        PENDING = "pending"
        SENT = "sent"
        FAILED = "failed"
        CANCELLED = "cancelled"
```

### AppointmentCancellation

```python
class AppointmentCancellation:
    id: UUID
    appointment_id: UUID
    cancelled_by_id: UUID
    reason: str
    cancellation_type: CancellationType  # customer, owner, system
    refund_amount: Optional[Decimal]
    refund_status: Optional[str]
    created_at: datetime

    class CancellationType(Enum):
        CUSTOMER = "customer"
        OWNER = "owner"
        SYSTEM = "system"  # Duplicate, conflict, etc.
```

### AppointmentCheckIn

```python
class AppointmentCheckIn:
    id: UUID
    appointment_id: UUID
    checked_in_by: UUID  # Customer or staff
    checked_in_at: datetime
    check_in_method: str  # qr_code, manual, link
    notes: Optional[str]
```

---

## API Design

### Appointment Booking

#### POST /api/v1/appointments
Book a new appointment.

**Request:**
```json
{
  "calendar_id": "uuid",
  "slot_id": "uuid",
  "customer_id": "uuid",
  "customer_email": "customer@example.com",
  "customer_name": "John Doe",
  "customer_phone": "+1234567890",
  "start_time": "2026-02-15T14:00:00Z",
  "end_time": "2026-02-15T14:30:00Z",
  "timezone": "America/New_York",
  "appointment_type": "consultation",
  "notes": "Discuss project requirements",
  "location_type": "virtual"
}
```

**Response:** 201 Created
```json
{
  "id": "uuid",
  "status": "confirmed",
  "start_time": "2026-02-15T14:00:00Z",
  "end_time": "2026-02-15T14:30:00Z",
  "meeting_link": "https://zoom.us/j/123456",
  "confirmed_at": "2026-02-07T10:00:00Z",
  "customer": {...},
  "calendar": {...}
}
```

**Error Response:** 409 Conflict (slot unavailable)
```json
{
  "error": "slot_unavailable",
  "message": "Selected time slot is no longer available",
  "available_slots": [
    {"start_time": "2026-02-15T14:30:00Z", "end_time": "2026-02-15T15:00:00Z"}
  ]
}
```

#### GET /api/v1/appointments
List appointments with filtering.

**Query Params:**
- `calendar_id`: filter by calendar
- `customer_id`: filter by customer
- `status`: filter by status
- `start_date`: filter start date (ISO 8601)
- `end_date`: filter end date
- `page`: pagination
- `limit`: results per page

**Response:** 200 OK with paginated results.

#### GET /api/v1/appointments/{appointment_id}
Get appointment details.

**Response:** 200 OK with full appointment object.

### Appointment Cancellation

#### POST /api/v1/appointments/{appointment_id}/cancel
Cancel an appointment.

**Request:**
```json
{
  "reason": "Customer request - schedule conflict",
  "cancelled_by": "customer"
}
```

**Response:** 200 OK
```json
{
  "id": "uuid",
  "status": "cancelled",
  "cancelled_at": "2026-02-07T11:00:00Z",
  "refund_amount": 50.00,
  "refund_status": "processed"
}
```

**Error Response:** 403 Forbidden (outside cancellation window)
```json
{
  "error": "cancellation_not_allowed",
  "message": "Appointments must be cancelled at least 24 hours in advance",
  "cancellation_policy": {
    "lead_time_hours": 24,
    "hours_until_appointment": 4
  }
}
```

### Appointment Rescheduling

#### POST /api/v1/appointments/{appointment_id}/reschedule
Initiate rescheduling.

**Request:**
```json
{
  "reason": "Customer request"
}
```

**Response:** 200 OK
```json
{
  "appointment_id": "uuid",
  "reschedule_token": "temporary_token",
  "available_slots": [
    {
      "start_time": "2026-02-15T15:00:00Z",
      "end_time": "2026-02-15T15:30:00Z",
      "calendar_id": "uuid"
    }
  ],
  "expires_at": "2026-02-07T11:30:00Z"
}
```

#### PUT /api/v1/appointments/{appointment_id}/reschedule/confirm
Confirm rescheduling to new slot.

**Request:**
```json
{
  "new_slot_id": "uuid",
  "new_start_time": "2026-02-15T15:00:00Z",
  "new_end_time": "2026-02-15T15:30:00Z",
  "reschedule_token": "temporary_token"
}
```

**Response:** 200 OK with updated appointment details.

### Appointment Status Updates

#### PATCH /api/v1/appointments/{appointment_id}/status
Update appointment status (for staff/admin).

**Request:**
```json
{
  "status": "completed",
  "notes": "Consultation completed successfully"
}
```

**Response:** 200 OK

### Appointment Check-In

#### POST /api/v1/appointments/{appointment_id}/check-in
Check in to appointment.

**Request:**
```json
{
  "method": "qr_code",
  "notes": "Customer arrived on time"
}
```

**Response:** 201 Created

### Appointment Analytics

#### GET /api/v1/appointments/analytics
Get appointment analytics.

**Query Params:**
- `calendar_id`: filter by calendar
- `start_date`: start date range
- `end_date`: end date range
- `group_by`: day, week, month

**Response:** 200 OK
```json
{
  "total_appointments": 150,
  "confirmed": 120,
  "cancelled": 20,
  "completed": 100,
  "no_show": 10,
  "cancellation_rate": 0.13,
  "no_show_rate": 0.08,
  "average_lead_time_hours": 48,
  "by_type": {
    "consultation": {"count": 80, "revenue": 8000},
    "support": {"count": 40, "revenue": 2000}
  },
  "by_day": [
    {"date": "2026-02-01", "count": 12, "completed": 10, "cancelled": 2}
  ]
}
```

---

## Database Schema

```sql
-- Appointments table
CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    calendar_id UUID NOT NULL REFERENCES calendars(id),
    slot_id UUID NOT NULL,
    customer_id UUID NOT NULL REFERENCES contacts(id),
    customer_email VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(50),
    customer_name VARCHAR(255) NOT NULL,

    -- Timing
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    duration_minutes INT NOT NULL,
    timezone VARCHAR(100) NOT NULL,

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    cancellation_reason TEXT,
    cancelled_by UUID REFERENCES users(id),
    cancelled_at TIMESTAMPTZ,

    -- Rescheduling
    rescheduled_from_id UUID REFERENCES appointments(id),
    rescheduled_to_id UUID REFERENCES appointments(id),

    -- Metadata
    appointment_type VARCHAR(100) NOT NULL,
    notes TEXT,
    location_type VARCHAR(20) NOT NULL,
    location_address TEXT,
    meeting_link TEXT,
    meeting_provider VARCHAR(50),

    -- Payment
    payment_required BOOLEAN NOT NULL DEFAULT false,
    payment_amount DECIMAL(10, 2),
    payment_status VARCHAR(20),
    payment_id VARCHAR(255),

    -- Audit
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    confirmed_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    CONSTRAINT valid_status CHECK (status IN ('pending', 'confirmed', 'cancelled', 'completed', 'no_show', 'late_cancel')),
    CONSTRAINT valid_location_type CHECK (location_type IN ('in_person', 'virtual', 'phone')),
    CONSTRAINT valid_time_range CHECK (end_time > start_time),
    CONSTRAINT no_self_reschedule CHECK (rescheduled_from_id IS DISTINCT FROM id),
    UNIQUE(calendar_id, start_time, end_time)  -- Prevent double booking
);

CREATE INDEX idx_appointments_calendar ON appointments(calendar_id);
CREATE INDEX idx_appointments_customer ON appointments(customer_id);
CREATE INDEX idx_appointments_status ON appointments(status);
CREATE INDEX idx_appointments_start_time ON appointments(start_time);
CREATE INDEX idx_appointments_reschedule_from ON appointments(rescheduled_from_id);
CREATE INDEX idx_appointments_reschedule_to ON appointments(rescheduled_to_id);

-- Appointment reminders
CREATE TABLE appointment_reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    appointment_id UUID NOT NULL REFERENCES appointments(id) ON DELETE CASCADE,
    reminder_type VARCHAR(20) NOT NULL,
    scheduled_for TIMESTAMPTZ NOT NULL,
    sent_at TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',

    CONSTRAINT valid_reminder_type CHECK (reminder_type IN ('email', 'sms', 'push')),
    CONSTRAINT valid_reminder_status CHECK (status IN ('pending', 'sent', 'failed', 'cancelled'))
);

CREATE INDEX idx_reminders_appointment ON appointment_reminders(appointment_id);
CREATE INDEX idx_reminders_scheduled ON appointment_reminders(scheduled_for) WHERE status = 'pending';
CREATE INDEX idx_reminders_status ON appointment_reminders(status);

-- Appointment cancellations
CREATE TABLE appointment_cancellations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    appointment_id UUID NOT NULL REFERENCES appointments(id),
    cancelled_by_id UUID NOT NULL REFERENCES users(id),
    reason TEXT NOT NULL,
    cancellation_type VARCHAR(20) NOT NULL,
    refund_amount DECIMAL(10, 2),
    refund_status VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_cancellation_type CHECK (cancellation_type IN ('customer', 'owner', 'system'))
);

CREATE INDEX idx_cancellations_appointment ON appointment_cancellations(appointment_id);

-- Appointment check-ins
CREATE TABLE appointment_check_ins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    appointment_id UUID NOT NULL REFERENCES appointments(id),
    checked_in_by UUID NOT NULL REFERENCES users(id),
    checked_in_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    check_in_method VARCHAR(50) NOT NULL,
    notes TEXT,

    UNIQUE(appointment_id)  -- One check-in per appointment
);

CREATE INDEX idx_check_ins_appointment ON appointment_check_ins(appointment_id);
```

---

## Acceptance Criteria

### AC1: Successful Booking
- GIVEN an available time slot
- WHEN customer books appointment
- THEN appointment is created with "confirmed" status
- AND confirmation email is sent to customer
- AND notification is sent to calendar owner
- AND slot is marked as unavailable

### AC2: Race Condition Handling
- GIVEN two customers attempt to book same slot simultaneously
- WHEN both requests are processed
- THEN only one booking succeeds
- AND other receives 409 Conflict with available alternatives
- AND no double-booking occurs

### AC3: Confirmation Email
- GIVEN a newly created appointment
- WHEN confirmation email is sent
- THEN email contains all appointment details
- AND includes "Add to Calendar" links
- AND includes cancellation policy
- AND email is delivered within 10 seconds

### AC4: Reminder Delivery
- GIVEN an appointment scheduled for tomorrow
- WHEN reminder is due (24 hours before)
- THEN reminder email is sent automatically
- AND reminder status is updated to "sent"
- AND failed reminders are logged for retry

### AC5: Cancellation Policy
- GIVEN appointment with 24-hour cancellation policy
- WHEN customer tries to cancel 4 hours before
- THEN cancellation is blocked with 403 error
- AND error message explains policy
- AND customer is offered rescheduling instead

### AC6: Rescheduling Flow
- GIVEN customer wants to reschedule appointment
- WHEN rescheduling is initiated
- THEN current slot is held with expiration
- AND available alternative slots are shown
- AND new appointment is created upon confirmation
- AND old appointment is cancelled automatically

### AC7: No-Show Detection
- GIVEN appointment time has passed
- WHEN no check-in occurred
- THEN appointment status is auto-updated to "no_show"
- AND customer is sent follow-up email
- AND calendar owner is notified

### AC8: Analytics Accuracy
- GIVEN multiple appointments with various statuses
- WHEN analytics are requested
- THEN counts are accurate for each status
- AND cancellation rate is calculated correctly
- AND revenue totals match payment records

---

## Technical Approach

### Technology Stack
- **Backend**: FastAPI with async/await
- **Email**: SendGrid with templates
- **SMS**: Twilio
- **Task Queue**: Celery with Redis for reminder scheduling
- **Caching**: Redis for slot availability locks
- **Database**: PostgreSQL with row-level locking

### Architecture Pattern
- **Service Layer**: AppointmentService, ReminderService, NotificationService
- **Repository Pattern**: Async repositories for data access
- **Event-Driven**: Pub/Sub for appointment lifecycle events
- **Locking**: Redis distributed locks for slot booking

### Key Implementation Points

1. **Race Condition Prevention**:
   - Use Redis distributed locks with 30-second timeout
   - Implement optimistic locking with version checks
   - Use SELECT FOR UPDATE on appointments table

2. **Reminder Scheduling**:
   - Celery tasks scheduled based on appointment creation
   - Store tasks in Celery Beat schedule
   - Cancel tasks on appointment cancellation/rescheduling

3. **Email Templates**:
   - Dynamic templates with Jinja2
   - Multi-language support
   - A/B testing capability

4. **Rescheduling Transaction**:
   - Use database transaction for atomic operation
   - Hold current slot with temporary lock
   - Release lock if new booking fails

---

## Testing Strategy

### Unit Tests
- Booking validation logic
- Cancellation policy checks
- Status transition logic
- Reminder scheduling calculations
- Rescheduling transaction flow

### Integration Tests
- API endpoint with race conditions
- Email sending with SendGrid mock
- Celery task execution
- Database locking behavior
- Analytics query accuracy

### E2E Tests
- Complete booking flow from slot selection to confirmation
- Cancellation with policy enforcement
- Rescheduling from initiation to confirmation
- Reminder delivery for upcoming appointments
- No-show auto-detection workflow

---

## Success Metrics

- Booking success rate > 99%
- Confirmation email delivery > 99.5%
- Reminder delivery > 99%
- Zero double-booking incidents
- Cancellation rate < 15%
- No-show rate < 10%
- 85%+ test coverage achieved

---

**Next SPEC**: SPEC-CAL-003 (Availability)
