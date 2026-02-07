# Calendars Module - Master SPEC Index

**Module**: Calendars & Bookings
**Total SPECs**: 5
**Entities**: 17
**API Endpoints**: 35+
**Status**: Ready for Implementation
**Created**: 2026-02-07

---

## Module Overview

The Calendars Module provides comprehensive booking and scheduling capabilities for the GoHighLevel clone platform. It enables businesses to manage multiple calendars, accept appointments, configure availability rules, embed booking widgets, and integrate with external calendar services.

---

## SPEC Documents

### 1. SPEC-CAL-001: Calendar Management
**File**: `.moai/specs/SPEC-CAL-001/spec.md`

**Scope**: Core calendar infrastructure
- Multiple calendars per organization
- Business hours management
- Availability rules (recurring, fixed, custom)
- Time zone handling with full IANA support
- Calendar sharing with permission levels

**Entities (5)**:
- Calendar
- BusinessHour
- AvailabilityRule
- TimeSlot
- CalendarShare

**API Endpoints (10)**:
- POST /api/v1/calendars
- GET /api/v1/calendars
- GET /api/v1/calendars/{id}
- PUT /api/v1/calendars/{id}
- DELETE /api/v1/calendars/{id}
- PUT /api/v1/calendars/{id}/business-hours
- POST /api/v1/calendars/{id}/availability-rules
- GET /api/v1/calendars/{id}/availability-rules
- PUT /api/v1/calendars/{id}/availability-rules/{rule_id}
- DELETE /api/v1/calendars/{id}/availability-rules/{rule_id}
- POST /api/v1/calendars/{id}/shares
- GET /api/v1/calendars/{id}/shares
- DELETE /api/v1/calendars/{id}/shares/{share_id}

**Dependencies**: CRM Module (Contacts)

---

### 2. SPEC-CAL-002: Appointments
**File**: `.moai/specs/SPEC-CAL-002/spec.md`

**Scope**: Appointment lifecycle management
- Appointment booking with race condition prevention
- Confirmation emails with "Add to Calendar" links
- Multi-channel reminders (email, SMS, push)
- Cancellation with policy enforcement
- Rescheduling workflow
- Status management (pending, confirmed, cancelled, completed, no-show)
- Appointment analytics and reporting

**Entities (5)**:
- Appointment
- AppointmentReminder
- AppointmentCancellation
- AppointmentCheckIn

**API Endpoints (8)**:
- POST /api/v1/appointments
- GET /api/v1/appointments
- GET /api/v1/appointments/{id}
- POST /api/v1/appointments/{id}/cancel
- POST /api/v1/appointments/{id}/reschedule
- PUT /api/v1/appointments/{id}/reschedule/confirm
- PATCH /api/v1/appointments/{id}/status
- POST /api/v1/appointments/{id}/check-in
- GET /api/v1/appointments/analytics

**Dependencies**: SPEC-CAL-001, CRM Module (Contacts)

---

### 3. SPEC-CAL-003: Availability Management
**File**: `.moai/specs/SPEC-CAL-003/spec.md`

**Scope**: Advanced availability and slot generation
- Dynamic slot generation with multi-layer rules
- Buffer time management (before/after/between appointments)
- Break time scheduling (fixed, recurring, one-time)
- Blackout dates for holidays/vacations
- Recurring availability patterns (RRULE support)
- Availability caching with Redis
- Real-time availability updates via WebSocket

**Entities (5)**:
- AvailabilitySlot
- BufferTime
- BreakTime
- BlackoutDate
- SlotGenerationCache

**API Endpoints (11)**:
- GET /api/v1/calendars/{id}/availability
- POST /api/v1/calendars/{id}/buffer-times
- GET /api/v1/calendars/{id}/buffer-times
- PUT /api/v1/calendars/{id}/buffer-times/{buffer_id}
- DELETE /api/v1/calendars/{id}/buffer-times/{buffer_id}
- POST /api/v1/calendars/{id}/break-times
- POST /api/v1/calendars/{id}/break-times/recurring
- GET /api/v1/calendars/{id}/break-times
- PUT /api/v1/calendars/{id}/break-times/{break_id}
- DELETE /api/v1/calendars/{id}/break-times/{break_id}
- POST /api/v1/calendars/{id}/blackout-dates
- GET /api/v1/calendars/{id}/blackout-dates
- PUT /api/v1/calendars/{id}/blackout-dates/{blackout_id}
- DELETE /api/v1/calendars/{id}/blackout-dates/{blackout_id}
- POST /api/v1/calendars/{id}/availability/regenerate

**Dependencies**: SPEC-CAL-001, SPEC-CAL-002

---

### 4. SPEC-CAL-004: Booking Widgets
**File**: `.moai/specs/SPEC-CAL-004/spec.md`

**Scope**: Embeddable booking widgets
- Three widget types: inline, popup, full-page
- Full customization (colors, fonts, branding)
- Multi-step booking flow with validation
- Responsive design (mobile, tablet, desktop)
- Performance optimization (< 2s load on 3G)
- Privacy protection (HTTPS, no data exposure)
- Analytics and conversion tracking

**Entities (3)**:
- BookingWidget
- WidgetAnalytics
- WidgetEmbed

**API Endpoints (9)**:
- POST /api/v1/widgets
- GET /api/v1/widgets
- GET /api/v1/widgets/{id}
- PUT /api/v1/widgets/{id}
- DELETE /api/v1/widgets/{id}
- GET /api/v1/public/widgets/{public_api_key}
- GET /api/v1/public/widgets/{public_api_key}/availability
- POST /api/v1/public/widgets/{public_api_key}/book
- GET /api/v1/widgets/{id}/analytics
- GET /api/v1/widgets/{id}/embeds

**Dependencies**: SPEC-CAL-001, SPEC-CAL-002, SPEC-CAL-003

---

### 5. SPEC-CAL-005: Calendar Integrations
**File**: `.moai/specs/SPEC-CAL-005/spec.md`

**Scope**: External calendar and video conferencing integration
- Google Calendar two-way sync (OAuth 2.0)
- Outlook/Office 365 sync (Microsoft Graph API)
- iCloud CalDAV sync
- Video conferencing: Zoom, Google Meet, Microsoft Teams
- Automatic video meeting creation
- Sync conflict detection and resolution
- Webhook-based real-time sync
- Token management and refresh

**Entities (4)**:
- CalendarIntegration
- SyncEvent
- SyncConflict
- VideoMeeting

**API Endpoints (10)**:
- POST /api/v1/calendar-integrations
- GET /api/v1/calendar-integrations
- GET /api/v1/calendar-integrations/{id}
- PUT /api/v1/calendar-integrations/{id}
- DELETE /api/v1/calendar-integrations/{id}
- POST /api/v1/calendar-integrations/{id}/sync
- GET /api/v1/calendar-integrations/{id}/sync-status
- GET /api/v1/calendar-integrations/{id}/conflicts
- POST /api/v1/calendar-integrations/{id}/conflicts/{conflict_id}/resolve
- POST /api/v1/video-meetings
- PUT /api/v1/video-meetings/{id}
- DELETE /api/v1/video-meetings/{id}

**Dependencies**: SPEC-CAL-001, SPEC-CAL-002

---

## Entity Summary (17 Total)

| Entity | SPEC | Purpose |
|--------|-----|---------|
| Calendar | CAL-001 | Core calendar entity |
| BusinessHour | CAL-001 | Weekly business hours |
| AvailabilityRule | CAL-001 | Availability patterns |
| TimeSlot | CAL-001 | Time slot definitions |
| CalendarShare | CAL-001 | Calendar sharing |
| Appointment | CAL-002 | Booked appointments |
| AppointmentReminder | CAL-002 | Reminder scheduling |
| AppointmentCancellation | CAL-002 | Cancellation records |
| AppointmentCheckIn | CAL-002 | Check-in tracking |
| AvailabilitySlot | CAL-003 | Generated available slots |
| BufferTime | CAL-003 | Buffer time rules |
| BreakTime | CAL-003 | Break periods |
| BlackoutDate | CAL-003 | Unavailable dates |
| SlotGenerationCache | CAL-003 | Cached slot data |
| BookingWidget | CAL-004 | Embeddable widgets |
| WidgetAnalytics | CAL-004 | Widget usage data |
| WidgetEmbed | CAL-004 | Embed tracking |
| CalendarIntegration | CAL-005 | External connections |
| SyncEvent | CAL-005 | Sync operations |
| SyncConflict | CAL-005 | Conflict records |
| VideoMeeting | CAL-005 | Video meetings |

---

## API Endpoint Summary (48+ Endpoints)

### Calendar Management (13 endpoints)
- Calendar CRUD operations
- Business hours management
- Availability rules management
- Calendar sharing

### Appointments (9 endpoints)
- Appointment booking
- Cancellation and rescheduling
- Check-in management
- Analytics

### Availability (15 endpoints)
- Availability querying
- Buffer time management
- Break time management
- Blackout date management
- Slot regeneration

### Booking Widgets (10 endpoints)
- Widget management
- Public API (no-auth)
- Analytics

### Calendar Integrations (12 endpoints)
- Integration management
- OAuth callbacks
- Sync operations
- Conflict resolution
- Video meetings

---

## Database Schema Summary

**Total Tables**: 23

**By SPEC**:
- SPEC-CAL-001: 5 tables (calendars, business_hours, availability_rules, time_slots, calendar_shares)
- SPEC-CAL-002: 4 tables (appointments, appointment_reminders, appointment_cancellations, appointment_check_ins)
- SPEC-CAL-003: 4 tables (availability_slots, buffer_times, break_times, blackout_dates)
- SPEC-CAL-004: 3 tables (booking_widgets, widget_analytics, widget_embeds)
- SPEC-CAL-005: 4 tables (calendar_integrations, sync_events, sync_conflicts, video_meetings)
- Plus 3 junction tables for many-to-many relationships

**Key Features**:
- UUID primary keys throughout
- Comprehensive indexes for performance
- Foreign key constraints for data integrity
- Soft delete support (deleted_at columns)
- Enum constraints for valid values
- JSONB columns for flexible metadata

---

## Implementation Phases

### Phase 1: Foundation (SPEC-CAL-001)
**Duration**: Week 1-2
- Calendar entities and repositories
- Business hours management
- Basic availability rules
- Calendar sharing with permissions
- Database migrations
- Unit tests (85%+ coverage)

**Deliverables**:
- 5 domain entities
- 5 repository classes
- 3 service classes
- 13 API endpoints
- Database migration scripts
- Comprehensive test suite

### Phase 2: Appointments (SPEC-CAL-002)
**Duration**: Week 3-4
- Appointment lifecycle management
- Booking workflow with race condition prevention
- Email confirmation system
- Reminder scheduling (Celery)
- Cancellation and rescheduling
- Appointment analytics

**Deliverables**:
- 4 domain entities
- AppointmentService with booking logic
- NotificationService for emails/reminders
- 9 API endpoints
- Email templates
- Celery tasks for reminders

### Phase 3: Availability (SPEC-CAL-003)
**Duration**: Week 5-6
- Advanced slot generation algorithm
- Buffer and break time management
- Blackout dates
- Redis caching layer
- WebSocket for real-time updates
- RRULE parsing for recurring patterns

**Deliverables**:
- 5 domain entities
- SlotGenerationService
- CacheService with Redis
- WebSocket integration
- 15 API endpoints
- Performance optimization

### Phase 4: Booking Widgets (SPEC-CAL-004)
**Duration**: Week 7-8
- Embeddable JavaScript widget
- React component library
- Widget customization engine
- Booking flow with validation
- Analytics tracking
- Responsive design

**Deliverables**:
- 3 domain entities
- JavaScript widget bundle
- React component library
- Widget customization UI
- Public API endpoints
- Analytics dashboard

### Phase 5: Calendar Integrations (SPEC-CAL-005)
**Duration**: Week 9-10
- OAuth 2.0 flows (Google, Microsoft)
- CalDAV integration for iCloud
- Two-way sync algorithms
- Video meeting APIs (Zoom, Google Meet, Teams)
- Sync conflict resolution
- Webhook handlers

**Deliverables**:
- 4 domain entities
- OAuth flows for 3 providers
- Sync services for each provider
- Video meeting service
- 12 API endpoints
- Integration management UI

---

## Testing Strategy

### Unit Tests
- Entity models and validation
- Repository methods
- Service layer business logic
- Utility functions (timezone, RRULE parsing)
- Mock external dependencies

**Target**: 85%+ code coverage

### Integration Tests
- API endpoint testing
- Database operations
- Redis caching
- WebSocket connections
- Email sending (mocked)
- Celery task execution

### E2E Tests (Playwright)
- Complete booking flow
- Calendar management
- Appointment lifecycle
- Widget embedding and booking
- Calendar sync workflow

---

## Performance Targets

- API response time: p95 < 200ms
- Slot generation: < 500ms for 90-day range
- Widget load time: < 2s on 3G
- Email delivery: < 10s (95%)
- Sync latency: < 30s (webhook) or < 5min (polling)
- Cache hit rate: > 80%
- Database query time: < 100ms (p95)

---

## Security Requirements

- OWASP Top 10 compliance
- SQL injection prevention (parameterized queries)
- XSS protection (input sanitization)
- CSRF protection (state validation)
- Encrypted OAuth tokens at rest
- Rate limiting on public endpoints
- HTTPS only
- Row-level security for multi-tenancy
- Audit logging for all operations

---

## Dependencies

### Internal Modules
- CRM Module (Contacts entity referenced)
- Auth Module (User authentication)
- Notifications Module (Email, SMS, push)

### External Services
- SendGrid (Email)
- Twilio (SMS)
- Firebase (Push notifications)
- Google Calendar API
- Microsoft Graph API
- Zoom API
- Redis (Caching)
- PostgreSQL (Database)

---

## Technology Stack

### Backend
- **Framework**: FastAPI 0.115+
- **Language**: Python 3.12+
- **ORM**: SQLAlchemy 2.0 (async)
- **Validation**: Pydantic v2.9
- **Testing**: pytest-asyncio
- **Task Queue**: Celery with Redis
- **Real-Time**: WebSockets (FastAPI WebSocket)
- **OAuth**: Authlib

### Frontend (Widgets)
- **Framework**: React 18
- **Build**: Vite
- **Styling**: Tailwind CSS
- **Testing**: React Testing Library, Playwright

### Infrastructure
- **Database**: PostgreSQL 16 with Supabase
- **Cache**: Redis 7
- **Hosting**: AWS (S3, CloudFront for widgets)

---

## Success Criteria

✅ All 5 SPECs implemented with complete functionality
✅ 17 domain entities with proper relationships
✅ 48+ API endpoints with comprehensive testing
✅ 85%+ test coverage achieved
✅ Performance targets met (API, caching, sync)
✅ Security requirements satisfied (OWASP compliance)
✅ Documentation complete (API docs, deployment guides)
✅ Integration tests passing
✅ E2E tests passing for critical flows
✅ Widget successfully embeddable on external sites
✅ Calendar sync working with Google, Outlook, iCloud
✅ Video meeting creation functional

---

## Next Steps

1. ✅ **SPEC Creation**: All 5 SPEC documents created
2. **Backend Implementation**: Begin DDD implementation starting with SPEC-CAL-001
3. **Database Migrations**: Create Alembic migrations for all tables
4. **Testing**: Write comprehensive tests for each SPEC
5. **Documentation**: Generate OpenAPI/Swagger documentation
6. **Frontend**: Build booking widgets (Phase 4)
7. **Integrations**: Implement calendar sync (Phase 5)
8. **Deployment**: Deploy to staging environment
9. **E2E Testing**: Run full end-to-end test suite
10. **Production Launch**: Deploy to production

---

**Module Status**: Ready for DDD Implementation
**Last Updated**: 2026-02-07
**Generated By**: MoAI-ADK Alfred Orchestrator
