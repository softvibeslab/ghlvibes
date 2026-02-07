"""Domain entities for Calendars module.

Entities are objects with identity that persist over time.
Each entity represents a core business concept in the calendars domain.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime, date, time
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from src.calendars.domain.exceptions import (
    CalendarValidationError,
    InvalidBufferTimeError,
    InvalidTimezoneError,
    InvalidAppointmentStatusTransitionError,
    WidgetValidationError,
)
from src.calendars.domain.value_objects import (
    AppointmentStatus,
    AppointmentTime,
    AvailabilityRuleType,
    BreakType,
    BufferType,
    CalendarStatus,
    ConflictResolution,
    LocationType,
    PermissionLevel,
    RecurrencePattern,
    ReminderStatus,
    ReminderType,
    ReminderType as AppointmentReminderType,
    ReminderStatus as AppointmentReminderStatus,
    SlotSourceType,
    SyncDirection,
    SyncEventStatus,
    SyncEventType,
    SyncStatus,
    TimeRange,
    VideoPlatform,
    WidgetBranding,
    WidgetStatus,
    WidgetType,
    CalendarProvider,
    BreakType as BreakTimeBreakType,
    BufferType as BufferTimeBufferType,
    SlotSourceType as AvailabilitySlotSlotSourceType,
)


# ============================================================================
# SPEC-CAL-001: Calendar Management Entities
# ============================================================================


@dataclass
class Calendar:
    """Calendar aggregate root entity (SPEC-CAL-001).

    Represents a booking calendar with availability rules,
    business hours, and sharing capabilities.
    """

    id: UUID
    owner_id: UUID
    organization_id: UUID
    name: str
    timezone: str  # IANA timezone identifier
    status: CalendarStatus = CalendarStatus.ACTIVE
    description: str | None = None
    booking_buffer_minutes: int = 0
    cancellation_lead_time_hours: int = 24
    max_bookings_per_day: int = 10
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    deleted_at: datetime | None = None

    # Relationships (managed by repositories)
    business_hours: list = field(default_factory=list)
    availability_rules: list = field(default_factory=list)
    shared_with: list = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate calendar state."""
        if not self.name or len(self.name.strip()) == 0:
            raise CalendarValidationError("Calendar name is required", field="name")

        if len(self.name) > 255:
            raise CalendarValidationError("Calendar name must be 255 characters or less", field="name")

        # Validate timezone
        if not self.timezone or not self._is_valid_timezone(self.timezone):
            raise InvalidTimezoneError(self.timezone)

        if self.booking_buffer_minutes < 0:
            raise CalendarValidationError("Booking buffer cannot be negative", field="booking_buffer_minutes")

        if self.cancellation_lead_time_hours < 0:
            raise CalendarValidationError("Cancellation lead time cannot be negative", field="cancellation_lead_time_hours")

        if self.max_bookings_per_day < 1:
            raise CalendarValidationError("Max bookings per day must be at least 1", field="max_bookings_per_day")

    @staticmethod
    def _is_valid_timezone(timezone_str: str) -> bool:
        """Basic timezone validation (should use zoneinfo in production)."""
        # In production, use: zoneinfo.available_timezones()
        valid_prefixes = ["America/", "Europe/", "Asia/", "Australia/", "Pacific/", "Africa/", "UTC"]
        return any(timezone_str.startswith(prefix) for prefix in valid_prefixes) or timezone_str == "UTC"

    def is_active(self) -> bool:
        """Check if calendar is active."""
        return self.status == CalendarStatus.ACTIVE and self.deleted_at is None

    def is_deleted(self) -> bool:
        """Check if calendar is soft-deleted."""
        return self.deleted_at is not None

    def mark_deleted(self) -> None:
        """Mark calendar as deleted (soft delete)."""
        self.deleted_at = datetime.now(UTC)
        self.status = CalendarStatus.ARCHIVED

    @classmethod
    def create(
        cls,
        owner_id: UUID,
        organization_id: UUID,
        name: str,
        timezone: str,
        description: str | None = None,
        **kwargs: Any,
    ) -> "Calendar":
        """Factory method to create a new calendar."""
        return cls(
            id=uuid4(),
            owner_id=owner_id,
            organization_id=organization_id,
            name=name.strip(),
            timezone=timezone,
            description=description,
            **kwargs,
        )


@dataclass
class BusinessHour:
    """Business hours entity (SPEC-CAL-001).

    Defines weekly business hours for a calendar.
    """

    id: UUID
    calendar_id: UUID
    day_of_week: int  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time
    is_available: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Validate business hour."""
        if not 0 <= self.day_of_week <= 6:
            raise CalendarValidationError("Day of week must be 0-6", field="day_of_week")

        if self.end_time <= self.start_time:
            raise CalendarValidationError("End time must be after start time", field="end_time")

    @classmethod
    def create(
        cls,
        calendar_id: UUID,
        day_of_week: int,
        start_time: str,  # HH:MM format
        end_time: str,  # HH:MM format
        is_available: bool = True,
    ) -> "BusinessHour":
        """Factory method to create business hours."""
        # Parse time strings to time objects
        start_h, start_m = map(int, start_time.split(":"))
        end_h, end_m = map(int, end_time.split(":"))

        return cls(
            id=uuid4(),
            calendar_id=calendar_id,
            day_of_week=day_of_week,
            start_time=time(start_h, start_m),
            end_time=time(end_h, end_m),
            is_available=is_available,
        )


@dataclass
class AvailabilityRule:
    """Availability rule entity (SPEC-CAL-001, SPEC-CAL-003).

    Defines complex availability patterns beyond business hours.
    """

    id: UUID
    calendar_id: UUID
    name: str
    rule_type: AvailabilityRuleType
    priority: int = 0  # Higher = more priority
    is_active: bool = True
    start_date: date | None = None
    end_date: date | None = None
    recurrence_pattern: str | None = None  # RRULE format
    recurrence_until: date | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Time slots (managed by repository)
    time_slots: list = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate availability rule."""
        if not self.name or len(self.name.strip()) == 0:
            raise CalendarValidationError("Rule name is required", field="name")

        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise CalendarValidationError("End date cannot be before start date", field="end_date")

        if self.recurrence_until and self.start_date and self.recurrence_until < self.start_date:
            raise CalendarValidationError("Recurrence until cannot be before start date", field="recurrence_until")

    @classmethod
    def create(
        cls,
        calendar_id: UUID,
        name: str,
        rule_type: AvailabilityRuleType,
        priority: int = 0,
        **kwargs: Any,
    ) -> "AvailabilityRule":
        """Factory method to create availability rule."""
        return cls(
            id=uuid4(),
            calendar_id=calendar_id,
            name=name.strip(),
            rule_type=rule_type,
            priority=priority,
            **kwargs,
        )


@dataclass
class TimeSlot:
    """Time slot entity (SPEC-CAL-001).

    Defines discrete time slots within availability rules.
    """

    id: UUID
    availability_rule_id: UUID
    start_time: time
    end_time: time
    max_bookings: int = 1  # 0 = unlimited
    slot_duration_minutes: int = 30
    buffer_minutes: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Validate time slot."""
        if self.end_time <= self.start_time:
            raise CalendarValidationError("End time must be after start time", field="end_time")

        if self.slot_duration_minutes <= 0:
            raise CalendarValidationError("Slot duration must be positive", field="slot_duration_minutes")

        if self.max_bookings < 0:
            raise CalendarValidationError("Max bookings cannot be negative", field="max_bookings")

        if self.buffer_minutes < 0:
            raise InvalidBufferTimeError("Buffer minutes cannot be negative")

    @classmethod
    def create(
        cls,
        availability_rule_id: UUID,
        start_time: str,  # HH:MM format
        end_time: str,  # HH:MM format
        slot_duration_minutes: int = 30,
        max_bookings: int = 1,
        buffer_minutes: int = 0,
    ) -> "TimeSlot":
        """Factory method to create time slot."""
        start_h, start_m = map(int, start_time.split(":"))
        end_h, end_m = map(int, end_time.split(":"))

        return cls(
            id=uuid4(),
            availability_rule_id=availability_rule_id,
            start_time=time(start_h, start_m),
            end_time=time(end_h, end_m),
            slot_duration_minutes=slot_duration_minutes,
            max_bookings=max_bookings,
            buffer_minutes=buffer_minutes,
        )


@dataclass
class CalendarShare:
    """Calendar sharing entity (SPEC-CAL-001).

    Manages calendar sharing with other users.
    """

    id: UUID
    calendar_id: UUID
    shared_with_id: UUID  # User ID
    shared_by_id: UUID  # User ID
    permission_level: PermissionLevel
    expires_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    revoked_at: datetime | None = None

    def is_active(self) -> bool:
        """Check if share is active."""
        if self.revoked_at is not None:
            return False
        if self.expires_at and datetime.now(UTC) > self.expires_at:
            return False
        return True

    def revoke(self) -> None:
        """Revoke calendar share."""
        self.revoked_at = datetime.now(UTC)

    @classmethod
    def create(
        cls,
        calendar_id: UUID,
        shared_with_id: UUID,
        shared_by_id: UUID,
        permission_level: PermissionLevel,
        expires_at: datetime | None = None,
    ) -> "CalendarShare":
        """Factory method to create calendar share."""
        return cls(
            id=uuid4(),
            calendar_id=calendar_id,
            shared_with_id=shared_with_id,
            shared_by_id=shared_by_id,
            permission_level=permission_level,
            expires_at=expires_at,
        )


# ============================================================================
# SPEC-CAL-002: Appointments Entities
# ============================================================================


@dataclass
class Appointment:
    """Appointment aggregate root entity (SPEC-CAL-002).

    Represents a booked appointment with all lifecycle management.
    """

    id: UUID
    calendar_id: UUID
    slot_id: UUID
    customer_id: UUID  # Contact from CRM
    customer_email: str
    customer_name: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    timezone: str  # Customer's timezone
    status: AppointmentStatus = AppointmentStatus.PENDING

    # Optional fields
    customer_phone: str | None = None
    cancellation_reason: str | None = None
    cancelled_by: UUID | None = None
    cancelled_at: datetime | None = None

    # Rescheduling
    rescheduled_from_id: UUID | None = None
    rescheduled_to_id: UUID | None = None

    # Metadata
    appointment_type: str = "consultation"
    notes: str | None = None
    location_type: LocationType = LocationType.VIRTUAL
    location_address: str | None = None
    meeting_link: str | None = None
    meeting_provider: str | None = None

    # Payment (optional)
    payment_required: bool = False
    payment_amount: Decimal | None = None
    payment_status: str | None = None
    payment_id: str | None = None

    # Reminders
    reminders_sent: list[datetime] = field(default_factory=list)

    # Audit
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    confirmed_at: datetime | None = None
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate appointment."""
        if not self.customer_email or "@" not in self.customer_email:
            raise CalendarValidationError("Valid customer email is required", field="customer_email")

        if not self.customer_name or len(self.customer_name.strip()) == 0:
            raise CalendarValidationError("Customer name is required", field="customer_name")

        if self.end_time <= self.start_time:
            raise CalendarValidationError("End time must be after start time", field="end_time")

        if self.duration_minutes <= 0:
            raise CalendarValidationError("Duration must be positive", field="duration_minutes")

    def confirm(self) -> None:
        """Confirm appointment."""
        if self.status != AppointmentStatus.PENDING:
            raise InvalidAppointmentStatusTransitionError(self.status, AppointmentStatus.CONFIRMED)

        self.status = AppointmentStatus.CONFIRMED
        self.confirmed_at = datetime.now(UTC)

    def cancel(self, reason: str, cancelled_by: UUID) -> None:
        """Cancel appointment."""
        if self.status in [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED]:
            raise InvalidAppointmentStatusTransitionError(self.status, AppointmentStatus.CANCELLED)

        self.status = AppointmentStatus.CANCELLED
        self.cancellation_reason = reason
        self.cancelled_by = cancelled_by
        self.cancelled_at = datetime.now(UTC)

    def complete(self) -> None:
        """Mark appointment as completed."""
        if self.status != AppointmentStatus.CONFIRMED:
            raise InvalidAppointmentStatusTransitionError(self.status, AppointmentStatus.COMPLETED)

        self.status = AppointmentStatus.COMPLETED
        self.completed_at = datetime.now(UTC)

    def mark_no_show(self) -> None:
        """Mark appointment as no-show."""
        if self.status != AppointmentStatus.CONFIRMED:
            raise InvalidAppointmentStatusTransitionError(self.status, AppointmentStatus.NO_SHOW)

        self.status = AppointmentStatus.NO_SHOW
        self.completed_at = datetime.now(UTC)

    @classmethod
    def create(
        cls,
        calendar_id: UUID,
        slot_id: UUID,
        customer_id: UUID,
        customer_email: str,
        customer_name: str,
        start_time: datetime,
        end_time: datetime,
        timezone: str,
        **kwargs: Any,
    ) -> "Appointment":
        """Factory method to create appointment."""
        duration_minutes = int((end_time - start_time).total_seconds() / 60)

        return cls(
            id=uuid4(),
            calendar_id=calendar_id,
            slot_id=slot_id,
            customer_id=customer_id,
            customer_email=customer_email,
            customer_name=customer_name,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration_minutes,
            timezone=timezone,
            **kwargs,
        )


@dataclass
class AppointmentReminder:
    """Appointment reminder entity (SPEC-CAL-002).

    Tracks reminder notifications for appointments.
    """

    id: UUID
    appointment_id: UUID
    reminder_type: AppointmentReminderType
    scheduled_for: datetime
    sent_at: datetime | None = None
    status: AppointmentReminderStatus = AppointmentReminderStatus.PENDING

    def send(self) -> None:
        """Mark reminder as sent."""
        if self.status != AppointmentReminderStatus.PENDING:
            return
        self.status = AppointmentReminderStatus.SENT
        self.sent_at = datetime.now(UTC)

    def fail(self) -> None:
        """Mark reminder as failed."""
        self.status = AppointmentReminderStatus.FAILED

    def cancel(self) -> None:
        """Cancel reminder."""
        self.status = AppointmentReminderStatus.CANCELLED

    @classmethod
    def create(
        cls,
        appointment_id: UUID,
        reminder_type: AppointmentReminderType,
        scheduled_for: datetime,
    ) -> "AppointmentReminder":
        """Factory method to create reminder."""
        return cls(
            id=uuid4(),
            appointment_id=appointment_id,
            reminder_type=reminder_type,
            scheduled_for=scheduled_for,
        )


@dataclass
class AppointmentCancellation:
    """Appointment cancellation record entity (SPEC-CAL-002).

    Records cancellation details for analytics and reporting.
    """

    id: UUID
    appointment_id: UUID
    cancelled_by_id: UUID
    reason: str
    cancellation_type: str  # customer, owner, system
    refund_amount: Decimal | None = None
    refund_status: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        appointment_id: UUID,
        cancelled_by_id: UUID,
        reason: str,
        cancellation_type: str,
        refund_amount: Decimal | None = None,
    ) -> "AppointmentCancellation":
        """Factory method to create cancellation record."""
        return cls(
            id=uuid4(),
            appointment_id=appointment_id,
            cancelled_by_id=cancelled_by_id,
            reason=reason,
            cancellation_type=cancellation_type,
            refund_amount=refund_amount,
        )


@dataclass
class AppointmentCheckIn:
    """Appointment check-in entity (SPEC-CAL-002).

    Tracks customer check-ins for appointments.
    """

    id: UUID
    appointment_id: UUID
    checked_in_by: UUID  # Customer or staff
    checked_in_at: datetime
    check_in_method: str  # qr_code, manual, link
    notes: str | None = None

    @classmethod
    def create(
        cls,
        appointment_id: UUID,
        checked_in_by: UUID,
        check_in_method: str,
        notes: str | None = None,
    ) -> "AppointmentCheckIn":
        """Factory method to create check-in."""
        return cls(
            id=uuid4(),
            appointment_id=appointment_id,
            checked_in_by=checked_in_by,
            checked_in_at=datetime.now(UTC),
            check_in_method=check_in_method,
            notes=notes,
        )


# ============================================================================
# SPEC-CAL-003: Availability Management Entities
# ============================================================================


@dataclass
class AvailabilitySlot:
    """Generated availability slot entity (SPEC-CAL-003).

    Represents a bookable time slot generated by availability rules.
    """

    id: UUID
    calendar_id: UUID
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    is_available: bool = True
    buffer_before_minutes: int = 0
    buffer_after_minutes: int = 0
    max_bookings: int = 1
    current_bookings: int = 0
    source_rule_id: UUID | None = None
    source_type: SlotSourceType = SlotSourceType.BUSINESS_HOURS
    date: date | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None

    def book(self) -> bool:
        """Attempt to book the slot."""
        if not self.is_available:
            return False
        if self.max_bookings > 0 and self.current_bookings >= self.max_bookings:
            return False

        self.current_bookings += 1
        if self.max_bookings > 0 and self.current_bookings >= self.max_bookings:
            self.is_available = False
        return True

    def release(self) -> None:
        """Release a booking from the slot."""
        if self.current_bookings > 0:
            self.current_bookings -= 1
            self.is_available = True


@dataclass
class BufferTime:
    """Buffer time configuration entity (SPEC-CAL-003).

    Defines buffer times before/after appointments.
    """

    id: UUID
    calendar_id: UUID
    buffer_type: BufferTimeBufferType
    duration_minutes: int
    applies_to: list[str] = field(default_factory=list)  # Appointment types
    priority: int = 0
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Validate buffer time."""
        if self.duration_minutes < 0:
            raise InvalidBufferTimeError("Buffer duration cannot be negative")


@dataclass
class BreakTime:
    """Break time entity (SPEC-CAL-003).

    Defines break periods that block availability.
    """

    id: UUID
    calendar_id: UUID
    name: str
    break_type: BreakTimeBreakType
    start_time: time
    end_time: time
    day_of_week: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    recurrence_pattern: str | None = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Validate break time."""
        if self.end_time <= self.start_time:
            raise CalendarValidationError("Break end time must be after start time")

        if self.day_of_week is not None and not 0 <= self.day_of_week <= 6:
            raise CalendarValidationError("Day of week must be 0-6")


@dataclass
class BlackoutDate:
    """Blackout date entity (SPEC-CAL-003).

    Blocks entire dates or date ranges from availability.
    """

    id: UUID
    calendar_id: UUID
    name: str
    start_date: date
    end_date: date
    recurrence: str | None = None  # RRULE for recurring blackouts
    reason: str | None = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Validate blackout date."""
        if self.end_date < self.start_date:
            raise CalendarValidationError("End date cannot be before start date", field="end_date")

    def affects_date(self, target_date: date) -> bool:
        """Check if blackout affects a specific date."""
        return self.start_date <= target_date <= self.end_date


# ============================================================================
# SPEC-CAL-004: Booking Widget Entities
# ============================================================================


@dataclass
class BookingWidget:
    """Booking widget entity (SPEC-CAL-004).

    Represents an embeddable booking widget.
    """

    id: UUID
    calendar_id: UUID
    name: str
    widget_type: WidgetType
    status: WidgetStatus = WidgetStatus.ACTIVE

    # Customization
    primary_color: str = "#3B82F6"
    secondary_color: str = "#1E40AF"
    background_color: str = "#FFFFFF"
    text_color: str = "#000000"
    font_family: str = "system-ui"
    border_radius: int = 8
    logo_url: str | None = None
    background_image_url: str | None = None
    welcome_message: str = "Book your appointment"

    # Behavior
    require_payment: bool = False
    collect_customer_address: bool = False
    collect_customer_notes: bool = True
    allow_rescheduling: bool = True
    show_calendar_owner_photo: bool = False

    # Integration
    allowed_domains: list[str] = field(default_factory=list)
    redirect_url: str | None = None
    webhook_url: str | None = None

    # Analytics
    track_conversions: bool = True
    tracking_id: str | None = None

    # Authentication
    public_api_key: str | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Validate widget."""
        if not self.name or len(self.name.strip()) == 0:
            raise WidgetValidationError("Widget name is required", field="name")

        # Validate hex colors
        for color_field in ["primary_color", "secondary_color", "background_color", "text_color"]:
            color = getattr(self, color_field)
            if not color.startswith("#") or len(color) != 7:
                raise WidgetValidationError(f"Invalid hex color for {color_field}", field=color_field)

    def is_active(self) -> bool:
        """Check if widget is active."""
        return self.status == WidgetStatus.ACTIVE

    def is_domain_allowed(self, domain: str) -> bool:
        """Check if domain is allowed for embedding."""
        if not self.allowed_domains:
            return True
        return domain in self.allowed_domains

    @classmethod
    def create(
        cls,
        calendar_id: UUID,
        name: str,
        widget_type: WidgetType,
        **kwargs: Any,
    ) -> "BookingWidget":
        """Factory method to create widget."""
        widget = cls(
            id=uuid4(),
            calendar_id=calendar_id,
            name=name.strip(),
            widget_type=widget_type,
            **kwargs,
        )
        # Generate public API key
        import secrets

        widget.public_api_key = f"pk_{secrets.token_urlsafe(32)}"
        return widget


@dataclass
class WidgetAnalytics:
    """Widget analytics event entity (SPEC-CAL-004).

    Tracks widget usage and conversion events.
    """

    id: UUID
    widget_id: UUID
    event_type: str  # view, step_start, step_complete, booking, error
    timestamp: datetime
    referrer_url: str | None = None
    user_agent: str | None = None
    device_type: str | None = None  # mobile, tablet, desktop
    browser: str | None = None
    step_name: str | None = None
    time_spent_seconds: int | None = None
    error_message: str | None = None
    appointment_id: UUID | None = None
    booking_value: Decimal | None = None

    @classmethod
    def create(
        cls,
        widget_id: UUID,
        event_type: str,
        **kwargs: Any,
    ) -> "WidgetAnalytics":
        """Factory method to create analytics event."""
        return cls(
            id=uuid4(),
            widget_id=widget_id,
            event_type=event_type,
            timestamp=datetime.now(UTC),
            **kwargs,
        )


@dataclass
class WidgetEmbed:
    """Widget embed tracking entity (SPEC-CAL-004).

    Tracks where widgets are embedded.
    """

    id: UUID
    widget_id: UUID
    domain: str
    embed_url: str
    page_path: str | None = None
    first_seen_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_seen_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True

    @classmethod
    def create(
        cls,
        widget_id: UUID,
        domain: str,
        embed_url: str,
        page_path: str | None = None,
    ) -> "WidgetEmbed":
        """Factory method to create embed tracking."""
        return cls(
            id=uuid4(),
            widget_id=widget_id,
            domain=domain,
            embed_url=embed_url,
            page_path=page_path,
        )


# ============================================================================
# SPEC-CAL-005: Calendar Integration Entities
# ============================================================================


@dataclass
class CalendarIntegration:
    """Calendar integration entity (SPEC-CAL-005).

    Manages external calendar service connections.
    """

    id: UUID
    user_id: UUID
    organization_id: UUID
    provider: CalendarProvider
    provider_calendar_id: str
    calendar_name: str

    # Authentication (encrypted at application level)
    access_token: str
    refresh_token: str
    token_expires_at: datetime | None = None

    # Sync settings
    sync_enabled: bool = True
    sync_direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    last_sync_at: datetime | None = None
    next_sync_at: datetime | None = None
    sync_status: SyncStatus = SyncStatus.ACTIVE

    # Configuration
    sync_created_appointments: bool = True
    sync_updated_appointments: bool = True
    sync_cancelled_appointments: bool = True
    create_video_meetings: bool = False
    video_platform: VideoPlatform | None = None

    # Webhooks
    webhook_url: str | None = None
    webhook_secret: str | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    disconnected_at: datetime | None = None

    def is_active(self) -> bool:
        """Check if integration is active."""
        return self.sync_enabled and self.sync_status == SyncStatus.ACTIVE and self.disconnected_at is None

    def requires_token_refresh(self) -> bool:
        """Check if access token needs refresh."""
        if not self.token_expires_at:
            return False
        # Refresh if token expires within 5 minutes
        return datetime.now(UTC) >= self.token_expires_at

    @classmethod
    def create(
        cls,
        user_id: UUID,
        organization_id: UUID,
        provider: CalendarProvider,
        provider_calendar_id: str,
        calendar_name: str,
        access_token: str,
        refresh_token: str,
        **kwargs: Any,
    ) -> "CalendarIntegration":
        """Factory method to create integration."""
        return cls(
            id=uuid4(),
            user_id=user_id,
            organization_id=organization_id,
            provider=provider,
            provider_calendar_id=provider_calendar_id,
            calendar_name=calendar_name,
            access_token=access_token,
            refresh_token=refresh_token,
            **kwargs,
        )


@dataclass
class SyncEvent:
    """Sync event entity (SPEC-CAL-005).

    Tracks synchronization events between internal and external calendars.
    """

    id: UUID
    integration_id: UUID
    event_type: SyncEventType
    direction: SyncDirection
    provider_event_id: str
    internal_appointment_id: UUID | None = None
    event_data: dict[str, Any] = field(default_factory=dict)
    changes: dict[str, Any] | None = None
    status: SyncEventStatus = SyncEventStatus.PENDING
    error_message: str | None = None
    retry_count: int = 0
    resolved_at: datetime | None = None
    provider_timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    processed_at: datetime | None = None

    def mark_success(self) -> None:
        """Mark sync event as successful."""
        self.status = SyncEventStatus.SUCCESS
        self.processed_at = datetime.now(UTC)

    def mark_failed(self, error_message: str) -> None:
        """Mark sync event as failed."""
        self.status = SyncEventStatus.FAILED
        self.error_message = error_message
        self.retry_count += 1
        self.processed_at = datetime.now(UTC)

    @classmethod
    def create(
        cls,
        integration_id: UUID,
        event_type: SyncEventType,
        direction: SyncDirection,
        provider_event_id: str,
        event_data: dict[str, Any],
        **kwargs: Any,
    ) -> "SyncEvent":
        """Factory method to create sync event."""
        return cls(
            id=uuid4(),
            integration_id=integration_id,
            event_type=event_type,
            direction=direction,
            provider_event_id=provider_event_id,
            event_data=event_data,
            **kwargs,
        )


@dataclass
class SyncConflict:
    """Sync conflict entity (SPEC-CAL-005).

    Records and manages sync conflicts between calendars.
    """

    id: UUID
    integration_id: UUID
    sync_event_id: UUID
    internal_version: dict[str, Any]
    external_version: dict[str, Any]
    conflict_reason: str
    resolution: ConflictResolution | None = None
    resolved_by: UUID | None = None
    resolved_at: datetime | None = None
    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def resolve(
        self,
        resolution: ConflictResolution,
        resolved_by: UUID,
    ) -> None:
        """Mark conflict as resolved."""
        self.resolution = resolution
        self.resolved_by = resolved_by
        self.resolved_at = datetime.now(UTC)

    @classmethod
    def create(
        cls,
        integration_id: UUID,
        sync_event_id: UUID,
        internal_version: dict[str, Any],
        external_version: dict[str, Any],
        conflict_reason: str,
    ) -> "SyncConflict":
        """Factory method to create conflict record."""
        return cls(
            id=uuid4(),
            integration_id=integration_id,
            sync_event_id=sync_event_id,
            internal_version=internal_version,
            external_version=external_version,
            conflict_reason=conflict_reason,
        )


@dataclass
class VideoMeeting:
    """Video meeting entity (SPEC-CAL-005).

    Represents video conferencing meeting details.
    """

    id: UUID
    appointment_id: UUID
    platform: VideoPlatform
    meeting_id: str  # Provider's meeting ID
    join_url: str
    host_url: str | None = None
    passcode: str | None = None
    waiting_room_enabled: bool = False
    recording_enabled: bool = False
    alternative_hosts: list[str] = field(default_factory=list)
    provider_data: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        appointment_id: UUID,
        platform: VideoPlatform,
        meeting_id: str,
        join_url: str,
        **kwargs: Any,
    ) -> "VideoMeeting":
        """Factory method to create video meeting."""
        return cls(
            id=uuid4(),
            appointment_id=appointment_id,
            platform=platform,
            meeting_id=meeting_id,
            join_url=join_url,
            **kwargs,
        )
