"""Calendars and Bookings module.

This module provides comprehensive booking and scheduling capabilities including:
- Calendar management (SPEC-CAL-001)
- Appointments (SPEC-CAL-002)
- Availability management (SPEC-CAL-003)
- Booking widgets (SPEC-CAL-004)
- Calendar integrations (SPEC-CAL-005)
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
    TimeSlot,
)

__all__ = [
    # Entities
    "Calendar",
    "BusinessHour",
    "AvailabilityRule",
    "TimeSlot",
    "Appointment",
    "BufferTime",
    "BreakTime",
    "BlackoutDate",
    "BookingWidget",
    "CalendarIntegration",
]
