"""Domain exceptions for Calendars module.

Custom exceptions that represent business rule violations
and domain-specific error conditions.
"""

from src.calendars.domain.value_objects import (
    AppointmentStatus,
    AvailabilityRuleType,
    CalendarStatus,
)


class CalendarsDomainError(Exception):
    """Base exception for all calendars domain errors."""

    pass


# ============================================================================
# Calendar Exceptions (SPEC-CAL-001)
# ============================================================================


class CalendarNotFoundError(CalendarsDomainError):
    """Raised when a calendar cannot be found."""

    def __init__(self, calendar_id: str | None = None) -> None:
        self.calendar_id = calendar_id
        if calendar_id:
            message = f"Calendar with ID '{calendar_id}' not found"
        else:
            message = "Calendar not found"
        super().__init__(message)


class CalendarValidationError(CalendarsDomainError):
    """Raised when calendar data validation fails."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
    ) -> None:
        self.field = field
        self.message = message
        super().__init__(message)


class InvalidTimezoneError(CalendarValidationError):
    """Raised when an invalid timezone is provided."""

    def __init__(self, timezone: str) -> None:
        self.timezone = timezone
        message = f"Invalid timezone identifier: '{timezone}'. Must be a valid IANA timezone."
        super().__init__(message, field="timezone")


class CalendarMaxLimitExceededError(CalendarsDomainError):
    """Raised when organization exceeds maximum calendar limit."""

    def __init__(self, current_count: int, max_limit: int = 50) -> None:
        self.current_count = current_count
        self.max_limit = max_limit
        message = (
            f"Organization has reached maximum calendar limit ({max_limit}). "
            f"Current: {current_count}"
        )
        super().__init__(message)


class CalendarDeleteRestrictedError(CalendarsDomainError):
    """Raised when calendar cannot be deleted due to restrictions."""

    def __init__(self, future_appointments_count: int) -> None:
        self.future_appointments_count = future_appointments_count
        message = (
            f"Cannot delete calendar with {future_appointments_count} future appointments. "
            "Cancel or reschedule appointments first."
        )
        super().__init__(message)


# ============================================================================
# Availability Rule Exceptions (SPEC-CAL-001, SPEC-CAL-003)
# ============================================================================


class InvalidAvailabilityRuleError(CalendarsDomainError):
    """Raised when availability rule validation fails."""

    def __init__(
        self,
        message: str,
        rule_type: AvailabilityRuleType | None = None,
    ) -> None:
        self.rule_type = rule_type
        self.message = message
        super().__init__(message)


class InvalidBufferTimeError(CalendarsDomainError):
    """Raised when buffer time configuration is invalid."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


# ============================================================================
# Appointment Exceptions (SPEC-CAL-002)
# ============================================================================


class AppointmentValidationError(CalendarsDomainError):
    """Raised when appointment data validation fails."""

    def __init__(self, message: str, field: str | None = None) -> None:
        self.field = field
        self.message = message
        super().__init__(message)


class AppointmentConflictError(CalendarsDomainError):
    """Raised when appointment conflicts with existing booking."""

    def __init__(
        self,
        start_time: str,
        end_time: str,
        existing_appointment_id: str | None = None,
    ) -> None:
        self.start_time = start_time
        self.end_time = end_time
        self.existing_appointment_id = existing_appointment_id
        message = f"Time slot {start_time} - {end_time} is already booked"
        if existing_appointment_id:
            message += f" (appointment: {existing_appointment_id})"
        super().__init__(message)


class SlotUnavailableError(CalendarsDomainError):
    """Raised when requested time slot is not available for booking."""

    def __init__(
        self,
        reason: str = "Slot is no longer available",
        alternatives: list[dict] | None = None,
    ) -> None:
        self.reason = reason
        self.alternatives = alternatives or []
        message = f"Slot unavailable: {reason}"
        if alternatives:
            message += f". {len(alternatives)} alternative slots available."
        super().__init__(message)


class AppointmentCancellationError(CalendarsDomainError):
    """Raised when appointment cancellation is not allowed."""

    def __init__(
        self,
        reason: str,
        policy_hours: int | None = None,
        hours_until_appointment: int | None = None,
    ) -> None:
        self.reason = reason
        self.policy_hours = policy_hours
        self.hours_until_appointment = hours_until_appointment
        message = reason
        if policy_hours is not None and hours_until_appointment is not None:
            message += (
                f" Policy requires {policy_hours}h notice, "
                f"appointment is in {hours_until_appointment}h."
            )
        super().__init__(message)


class InvalidAppointmentStatusTransitionError(CalendarsDomainError):
    """Raised when invalid status transition is attempted."""

    def __init__(
        self,
        current_status: AppointmentStatus,
        new_status: AppointmentStatus,
    ) -> None:
        self.current_status = current_status
        self.new_status = new_status
        message = (
            f"Cannot transition appointment from {current_status.value} "
            f"to {new_status.value}"
        )
        super().__init__(message)


# ============================================================================
# Widget Exceptions (SPEC-CAL-004)
# ============================================================================


class WidgetNotFoundError(CalendarsDomainError):
    """Raised when a booking widget cannot be found."""

    def __init__(self, widget_id: str) -> None:
        self.widget_id = widget_id
        message = f"Booking widget with ID '{widget_id}' not found"
        super().__init__(message)


class WidgetValidationError(CalendarsDomainError):
    """Raised when widget configuration is invalid."""

    def __init__(self, message: str, field: str | None = None) -> None:
        self.field = field
        self.message = message
        super().__init__(message)


# ============================================================================
# Integration Exceptions (SPEC-CAL-005)
# ============================================================================


class CalendarIntegrationError(CalendarsDomainError):
    """Base exception for calendar integration errors."""

    pass


class IntegrationAuthenticationError(CalendarIntegrationError):
    """Raised when integration authentication fails."""

    def __init__(self, provider: str, reason: str = "Authentication failed") -> None:
        self.provider = provider
        message = f"{provider} integration: {reason}"
        super().__init__(message)


class IntegrationSyncError(CalendarIntegrationError):
    """Raised when calendar sync fails."""

    def __init__(
        self,
        provider: str,
        reason: str,
        retry_after: int | None = None,
    ) -> None:
        self.provider = provider
        self.reason = reason
        self.retry_after = retry_after
        message = f"{provider} sync failed: {reason}"
        if retry_after:
            message += f" (retry after {retry_after}s)"
        super().__init__(message)


class SyncConflictError(CalendarIntegrationError):
    """Raised when sync conflict is detected."""

    def __init__(
        self,
        internal_version: dict,
        external_version: dict,
        reason: str,
    ) -> None:
        self.internal_version = internal_version
        self.external_version = external_version
        self.reason = reason
        message = f"Sync conflict detected: {reason}"
        super().__init__(message)


class VideoMeetingError(CalendarIntegrationError):
    """Raised when video meeting creation fails."""

    def __init__(self, platform: str, reason: str) -> None:
        self.platform = platform
        self.reason = reason
        message = f"{platform} meeting creation failed: {reason}"
        super().__init__(message)
