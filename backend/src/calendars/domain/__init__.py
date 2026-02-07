"""Domain layer for Calendars module.

Contains domain entities, value objects, exceptions, and domain services.
Following Domain-Driven Design principles.
"""

from src.calendars.domain.entities import (
    Appointment,
    AvailabilityRule,
    BlackoutDate,
    BookingWidget,
    BreakTime,
    BufferTime,
    BusinessHour,
    Calendar,
    CalendarIntegration,
    CalendarShare,
    TimeSlot,
)
from src.calendars.domain.exceptions import (
    AppointmentConflictError,
    AppointmentValidationError,
    CalendarNotFoundError,
    CalendarValidationError,
    InvalidAvailabilityRuleError,
    InvalidBufferTimeError,
    InvalidTimezoneError,
    SlotUnavailableError,
)

__all__ = [
    # Entities
    "Calendar",
    "BusinessHour",
    "AvailabilityRule",
    "TimeSlot",
    "CalendarShare",
    "Appointment",
    "BufferTime",
    "BreakTime",
    "BlackoutDate",
    "BookingWidget",
    "CalendarIntegration",
    # Exceptions
    "CalendarNotFoundError",
    "CalendarValidationError",
    "AppointmentConflictError",
    "AppointmentValidationError",
    "SlotUnavailableError",
    "InvalidAvailabilityRuleError",
    "InvalidBufferTimeError",
    "InvalidTimezoneError",
]
