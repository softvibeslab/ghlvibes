"""Value objects for Calendars module.

Value objects are immutable objects that represent concepts
in the domain without identity.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Literal
from uuid import UUID


# ============================================================================
# Calendar Value Objects (SPEC-CAL-001)
# ============================================================================


class CalendarStatus(str, Enum):
    """Calendar status values."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class PermissionLevel(str, Enum):
    """Calendar sharing permission levels."""

    VIEW_ONLY = "view_only"
    BOOK = "book"
    MANAGE = "manage"
    ADMIN = "admin"


@dataclass(frozen=True)
class TimeRange:
    """Immutable time range value object."""

    start_time: str  # HH:MM format
    end_time: str  # HH:MM format

    def __post_init__(self) -> None:
        """Validate time range."""
        try:
            start = self._parse_time(self.start_time)
            end = self._parse_time(self.end_time)
            if end <= start:
                raise ValueError("End time must be after start time")
        except ValueError as e:
            raise ValueError(f"Invalid time range: {e}")

    @staticmethod
    def _parse_time(time_str: str) -> tuple[int, int]:
        """Parse HH:MM time string to hours and minutes."""
        parts = time_str.split(":")
        if len(parts) != 2:
            raise ValueError(f"Invalid time format: {time_str}")
        hours, minutes = int(parts[0]), int(parts[1])
        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            raise ValueError(f"Invalid time values: {time_str}")
        return hours, minutes

    def duration_minutes(self) -> int:
        """Calculate duration in minutes."""
        start_h, start_m = self._parse_time(self.start_time)
        end_h, end_m = self._parse_time(self.end_time)
        return (end_h * 60 + end_m) - (start_h * 60 + start_m)

    def overlaps_with(self, other: "TimeRange") -> bool:
        """Check if this time range overlaps with another."""
        self_start = self._parse_time(self.start_time)
        self_end = self._parse_time(self.end_time)
        other_start = other._parse_time(other.start_time)
        other_end = other._parse_time(other.end_time)

        return not (self_end <= other_start or self_start >= other_end)


# ============================================================================
# Availability Rule Value Objects (SPEC-CAL-001, SPEC-CAL-003)
# ============================================================================


class AvailabilityRuleType(str, Enum):
    """Availability rule types."""

    FIXED_SCHEDULE = "fixed_schedule"
    RECURRING_PATTERN = "recurring_pattern"
    CUSTOM_DATES = "custom_dates"


@dataclass(frozen=True)
class RecurrencePattern:
    """Immutable recurrence pattern value object (RRULE format)."""

    pattern: str  # RRULE format string
    until: datetime | None = None

    def __post_init__(self) -> None:
        """Validate RRULE pattern."""
        if not self.pattern or not self.pattern.strip():
            raise ValueError("Recurrence pattern cannot be empty")
        # Basic RRULE validation
        if not self.pattern.startswith("FREQ="):
            raise ValueError("Invalid RRULE pattern: must start with FREQ=")

    @classmethod
    def daily(cls) -> "RecurrencePattern":
        """Create daily recurrence pattern."""
        return cls(pattern="FREQ=DAILY")

    @classmethod
    def weekly(cls, days: list[int] | None = None) -> "RecurrencePattern":
        """Create weekly recurrence pattern.

        Args:
            days: List of days (0=Monday, 6=Sunday)
        """
        if days:
            day_str = ",".join(f"MO,TU,WE,TH,FR,SA,SU"[d * 3 : d * 3 + 2] for d in days)
            return cls(pattern=f"FREQ=WEEKLY;BYDAY={day_str}")
        return cls(pattern="FREQ=WEEKLY")


# ============================================================================
# Appointment Value Objects (SPEC-CAL-002)
# ============================================================================


class AppointmentStatus(str, Enum):
    """Appointment status values."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
    LATE_CANCEL = "late_cancel"


class LocationType(str, Enum):
    """Appointment location types."""

    IN_PERSON = "in_person"
    VIRTUAL = "virtual"
    PHONE = "phone"


@dataclass(frozen=True)
class AppointmentTime:
    """Immutable appointment time value object."""

    start_time: datetime
    end_time: datetime
    timezone: str  # IANA timezone identifier

    def __post_init__(self) -> None:
        """Validate appointment time."""
        if self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")

    def duration_minutes(self) -> int:
        """Calculate duration in minutes."""
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)


class ReminderType(str, Enum):
    """Reminder types."""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class ReminderStatus(str, Enum):
    """Reminder delivery status."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ============================================================================
# Availability Slot Value Objects (SPEC-CAL-003)
# ============================================================================


class SlotSourceType(str, Enum):
    """Slot generation source types."""

    BUSINESS_HOURS = "business_hours"
    RECURRING_PATTERN = "recurring_pattern"
    SPECIFIC_DATE = "specific_date"


@dataclass(frozen=True)
class AvailableSlot:
    """Immutable available slot value object."""

    start_time: datetime
    end_time: datetime
    duration_minutes: int
    buffer_before_minutes: int = 0
    buffer_after_minutes: int = 0
    max_bookings: int = 1
    current_bookings: int = 0

    def __post_init__(self) -> None:
        """Validate slot."""
        if self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")
        if self.duration_minutes <= 0:
            raise ValueError("Duration must be positive")
        if self.max_bookings < 0:
            raise ValueError("Max bookings cannot be negative")
        if self.current_bookings < 0:
            raise ValueError("Current bookings cannot be negative")
        if self.current_bookings > self.max_bookings and self.max_bookings != 0:
            raise ValueError("Current bookings cannot exceed max bookings")

    def is_available(self) -> bool:
        """Check if slot has availability."""
        if self.max_bookings == 0:  # Unlimited
            return True
        return self.current_bookings < self.max_bookings


class BreakType(str, Enum):
    """Break time types."""

    FIXED_DAILY = "fixed_daily"
    RECURRING = "recurring"
    ONE_TIME = "one_time"


class BufferType(str, Enum):
    """Buffer time types."""

    BEFORE = "before"
    AFTER = "after"
    BOTH = "both"


# ============================================================================
# Widget Value Objects (SPEC-CAL-004)
# ============================================================================


class WidgetType(str, Enum):
    """Booking widget types."""

    INLINE = "inline"
    POPUP = "popup"
    FULL_PAGE = "full_page"


class WidgetStatus(str, Enum):
    """Widget status values."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class WidgetBranding:
    """Immutable widget branding configuration."""

    primary_color: str  # Hex color
    secondary_color: str  # Hex color
    background_color: str  # Hex color
    text_color: str  # Hex color
    font_family: str
    border_radius: int
    logo_url: str | None = None
    background_image_url: str | None = None

    def __post_init__(self) -> None:
        """Validate branding configuration."""
        # Validate hex colors
        for color_field in ["primary_color", "secondary_color", "background_color", "text_color"]:
            color = getattr(self, color_field)
            if not color.startswith("#") or len(color) != 7:
                raise ValueError(f"Invalid hex color for {color_field}: {color}")
        if self.border_radius < 0:
            raise ValueError("Border radius cannot be negative")


# ============================================================================
# Integration Value Objects (SPEC-CAL-005)
# ============================================================================


class CalendarProvider(str, Enum):
    """External calendar providers."""

    GOOGLE = "google"
    OUTLOOK = "outlook"
    ICLOUD = "icloud"


class SyncDirection(str, Enum):
    """Sync direction options."""

    BIDIRECTIONAL = "bidirectional"
    IMPORT_ONLY = "import_only"
    EXPORT_ONLY = "export_only"


class SyncStatus(str, Enum):
    """Integration sync status."""

    ACTIVE = "active"
    ERROR = "error"
    PAUSED = "paused"


class VideoPlatform(str, Enum):
    """Video conferencing platforms."""

    ZOOM = "zoom"
    GOOGLE_MEET = "google_meet"
    TEAMS = "teams"


class SyncEventType(str, Enum):
    """Sync event types."""

    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    CONFLICT = "conflict"


class SyncEventStatus(str, Enum):
    """Sync event processing status."""

    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CONFLICT = "conflict"


class ConflictResolution(str, Enum):
    """Sync conflict resolution options."""

    KEPT_INTERNAL = "kept_internal"
    KEPT_EXTERNAL = "kept_external"
    MERGED = "merged"
    CREATED_DUPLICATE = "created_duplicate"
