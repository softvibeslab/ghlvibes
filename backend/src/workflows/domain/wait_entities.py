"""Domain entities for workflow wait steps.

This module defines the core domain entities for wait step processing
in workflow executions. Wait steps allow workflows to pause and resume
based on time delays, specific dates, or external events.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any, Self
from uuid import UUID, uuid4

from src.workflows.domain.execution_exceptions import (
    InvalidExecutionStatusTransitionError,
    WorkflowExecutionError,
)


class WaitType(str, Enum):
    """Type of wait step.

    Different wait strategies:
    - fixed_time: Wait for a specific duration (minutes, hours, days, weeks)
    - until_date: Wait until a specific date/time
    - until_time: Wait until a specific time of day
    - for_event: Wait for a specific event to occur
    """

    FIXED_TIME = "fixed_time"
    UNTIL_DATE = "until_date"
    UNTIL_TIME = "until_time"
    FOR_EVENT = "for_event"


class WaitExecutionStatus(str, Enum):
    """Status of a wait step execution.

    Lifecycle:
    - waiting: Initial state, wait is active
    - scheduled: Scheduled for future execution (time-based waits)
    - resumed: Execution resumed after wait completed
    - timeout: Wait expired without event occurring
    - cancelled: Wait was cancelled
    - error: Error occurred during wait processing
    """

    WAITING = "waiting"
    SCHEDULED = "scheduled"
    RESUMED = "resumed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    ERROR = "error"

    def can_transition_to(self, new_status: "WaitExecutionStatus") -> bool:
        """Check if status transition is valid.

        Args:
            new_status: Target status to transition to.

        Returns:
            True if transition is valid, False otherwise.
        """
        valid_transitions = {
            WaitExecutionStatus.WAITING: {
                WaitExecutionStatus.SCHEDULED,
                WaitExecutionStatus.RESUMED,
                WaitExecutionStatus.CANCELLED,
                WaitExecutionStatus.ERROR,
            },
            WaitExecutionStatus.SCHEDULED: {
                WaitExecutionStatus.RESUMED,
                WaitExecutionStatus.TIMEOUT,
                WaitExecutionStatus.CANCELLED,
                WaitExecutionStatus.ERROR,
            },
            # Terminal states have no valid transitions
            WaitExecutionStatus.RESUMED: set(),
            WaitExecutionStatus.TIMEOUT: set(),
            WaitExecutionStatus.CANCELLED: set(),
            WaitExecutionStatus.ERROR: set(),
        }

        return new_status in valid_transitions.get(self, set())


class TimeUnit(str, Enum):
    """Time units for fixed time waits.

    Supported duration units with validation constraints:
    - minutes: 1-59 minutes
    - hours: 1-23 hours
    - days: 1-30 days
    - weeks: 1-12 weeks
    """

    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"

    def to_timedelta(self, value: int) -> timedelta:
        """Convert unit and value to timedelta.

        Args:
            value: The numeric value for the time unit.

        Returns:
            A timedelta representing the duration.

        Raises:
            ValueError: If value is out of valid range for the unit.
        """
        if self == TimeUnit.MINUTES:
            if not 1 <= value <= 59:
                raise ValueError(f"Minutes must be between 1 and 59, got {value}")
            return timedelta(minutes=value)
        if self == TimeUnit.HOURS:
            if not 1 <= value <= 23:
                raise ValueError(f"Hours must be between 1 and 23, got {value}")
            return timedelta(hours=value)
        if self == TimeUnit.DAYS:
            if not 1 <= value <= 30:
                raise ValueError(f"Days must be between 1 and 30, got {value}")
            return timedelta(days=value)
        if self == TimeUnit.WEEKS:
            if not 1 <= value <= 12:
                raise ValueError(f"Weeks must be between 1 and 12, got {value}")
            return timedelta(weeks=value)

        raise ValueError(f"Unknown time unit: {self}")


class EventType(str, Enum):
    """Event types for event-based waits.

    Supported events that can trigger workflow resumption:
    - email_open: Recipient opened email
    - email_click: Recipient clicked link in email
    - sms_reply: Recipient replied to SMS
    - form_submit: Contact submitted form
    - page_visit: Contact visited page
    - appointment_booked: Contact booked appointment
    """

    EMAIL_OPEN = "email_open"
    EMAIL_CLICK = "email_click"
    SMS_REPLY = "sms_reply"
    FORM_SUBMIT = "form_submit"
    PAGE_VISIT = "page_visit"
    APPOINTMENT_BOOKED = "appointment_booked"


@dataclass
class WaitStepExecution:
    """Wait step execution entity.

    This entity represents a single wait step execution within a workflow.
    It tracks the wait configuration, scheduling, and resumption logic.

    Attributes:
        id: Unique wait execution identifier.
        workflow_execution_id: Reference to workflow execution.
        workflow_id: Reference to workflow definition.
        contact_id: Contact being processed.
        account_id: Account/tenant identifier.
        step_id: Step identifier in workflow.
        wait_type: Type of wait (time-based or event-based).
        wait_config: Configuration for the wait (JSON).
        scheduled_at: When the wait is scheduled to resume.
        timezone: Timezone for time calculations (IANA format).
        event_type: Event type being waited for (if applicable).
        event_correlation_id: Correlation ID for event matching.
        event_timeout_at: When event wait times out.
        status: Current wait execution status.
        resumed_at: When execution was resumed.
        resumed_by: What triggered resumption (scheduler, event, timeout, manual).
        created_at: Record creation time.
        updated_at: Last update time.
    """

    id: UUID
    workflow_execution_id: UUID
    workflow_id: UUID
    contact_id: UUID
    account_id: UUID
    step_id: str
    wait_type: WaitType
    wait_config: dict[str, Any]
    scheduled_at: datetime | None = None
    timezone: str = "UTC"
    event_type: EventType | None = None
    event_correlation_id: UUID | None = None
    event_timeout_at: datetime | None = None
    status: WaitExecutionStatus = WaitExecutionStatus.WAITING
    resumed_at: datetime | None = None
    resumed_by: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create_fixed_time_wait(
        cls,
        workflow_execution_id: UUID,
        workflow_id: UUID,
        contact_id: UUID,
        account_id: UUID,
        step_id: str,
        duration: int,
        unit: TimeUnit,
        timezone: str = "UTC",
    ) -> Self:
        """Create a fixed time wait execution.

        Args:
            workflow_execution_id: Workflow execution instance.
            workflow_id: Workflow definition.
            contact_id: Contact being processed.
            account_id: Account identifier.
            step_id: Step identifier.
            duration: Duration value.
            unit: Time unit (minutes, hours, days, weeks).
            timezone: Timezone for calculations (default: UTC).

        Returns:
            A new WaitStepExecution instance with scheduled resume time.

        Raises:
            WorkflowExecutionError: If duration is invalid.
        """
        try:
            delay = unit.to_timedelta(duration)
        except ValueError as e:
            raise WorkflowExecutionError(f"Invalid duration: {e}") from e

        now = datetime.now(UTC)
        scheduled_at = now + delay

        wait_config = {"duration": duration, "unit": unit.value}

        return cls(
            id=uuid4(),
            workflow_execution_id=workflow_execution_id,
            workflow_id=workflow_id,
            contact_id=contact_id,
            account_id=account_id,
            step_id=step_id,
            wait_type=WaitType.FIXED_TIME,
            wait_config=wait_config,
            scheduled_at=scheduled_at,
            timezone=timezone,
            status=WaitExecutionStatus.SCHEDULED,
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def create_until_date_wait(
        cls,
        workflow_execution_id: UUID,
        workflow_id: UUID,
        contact_id: UUID,
        account_id: UUID,
        step_id: str,
        target_date: datetime,
        timezone: str = "UTC",
    ) -> Self:
        """Create a wait until specific date execution.

        Args:
            workflow_execution_id: Workflow execution instance.
            workflow_id: Workflow definition.
            contact_id: Contact being processed.
            account_id: Account identifier.
            step_id: Step identifier.
            target_date: Target date/time for resumption.
            timezone: Timezone for calculations (default: UTC).

        Returns:
            A new WaitStepExecution instance.

        Raises:
            WorkflowExecutionError: If target date is in the past or too far in future.
        """
        now = datetime.now(UTC)

        # Ensure target_date is timezone-aware
        if target_date.tzinfo is None:
            target_date = target_date.replace(tzinfo=UTC)

        # Validate target date is in future
        if target_date <= now:
            raise WorkflowExecutionError("Target date must be in the future")

        # Validate maximum future date (1 year)
        max_future = now + timedelta(days=365)
        if target_date > max_future:
            raise WorkflowExecutionError("Target date must be within 1 year from now")

        wait_config = {"target_date": target_date.isoformat()}

        return cls(
            id=uuid4(),
            workflow_execution_id=workflow_execution_id,
            workflow_id=workflow_id,
            contact_id=contact_id,
            account_id=account_id,
            step_id=step_id,
            wait_type=WaitType.UNTIL_DATE,
            wait_config=wait_config,
            scheduled_at=target_date,
            timezone=timezone,
            status=WaitExecutionStatus.SCHEDULED,
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def create_until_time_wait(
        cls,
        workflow_execution_id: UUID,
        workflow_id: UUID,
        contact_id: UUID,
        account_id: UUID,
        step_id: str,
        target_time: str,  # HH:MM format
        timezone: str,
        days: list[str] | None = None,  # Optional day restrictions
    ) -> Self:
        """Create a wait until specific time of day execution.

        Args:
            workflow_execution_id: Workflow execution instance.
            workflow_id: Workflow definition.
            contact_id: Contact being processed.
            account_id: Account identifier.
            step_id: Step identifier.
            target_time: Target time in HH:MM format (24-hour).
            timezone: IANA timezone string (e.g., 'America/New_York').
            days: Optional list of weekday restrictions (e.g., ['monday', 'tuesday']).

        Returns:
            A new WaitStepExecution instance with calculated next occurrence.

        Raises:
            WorkflowExecutionError: If time format is invalid or timezone is invalid.
        """
        # Validate time format (HH:MM)
        try:
            # Check format with regex for strict HH:MM
            import re

            if not re.match(r"^\d{2}:\d{2}$", target_time):
                raise ValueError("Time must be in HH:MM format")

            hour, minute = map(int, target_time.split(":"))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("Hour must be 00-23, minute must be 00-59")
        except (ValueError, AttributeError) as e:
            raise WorkflowExecutionError(
                f"Invalid time format: {target_time}. Must be HH:MM in 24-hour format"
            ) from e

        # Calculate next occurrence
        # Note: This is simplified - full implementation would use zoneinfo/pytz
        # for proper timezone handling and day restrictions
        now = datetime.now(UTC)
        wait_config = {
            "target_time": target_time,
            "timezone": timezone,
            "days": days or [],
        }

        # For now, schedule for next day at target time (UTC approximation)
        # Full implementation would use proper timezone conversion
        scheduled_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if scheduled_at <= now:
            scheduled_at += timedelta(days=1)

        return cls(
            id=uuid4(),
            workflow_execution_id=workflow_execution_id,
            workflow_id=workflow_id,
            contact_id=contact_id,
            account_id=account_id,
            step_id=step_id,
            wait_type=WaitType.UNTIL_TIME,
            wait_config=wait_config,
            scheduled_at=scheduled_at,
            timezone=timezone,
            status=WaitExecutionStatus.SCHEDULED,
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def create_event_wait(
        cls,
        workflow_execution_id: UUID,
        workflow_id: UUID,
        contact_id: UUID,
        account_id: UUID,
        step_id: str,
        event_type: EventType,
        timeout_hours: int = 168,  # Default 7 days
        timeout_action: str = "continue",
        correlation_id: UUID | None = None,
    ) -> Self:
        """Create an event-based wait execution.

        Args:
            workflow_execution_id: Workflow execution instance.
            workflow_id: Workflow definition.
            contact_id: Contact being processed.
            account_id: Account identifier.
            step_id: Step identifier.
            event_type: Type of event to wait for.
            timeout_hours: Maximum hours to wait (default: 168 = 7 days).
            timeout_action: Action on timeout ('continue' or 'exit').
            correlation_id: Optional correlation ID for event matching.

        Returns:
            A new WaitStepExecution instance.

        Raises:
            WorkflowExecutionError: If timeout is out of valid range.
        """
        # Validate timeout range
        if not (1 <= timeout_hours <= 2160):  # Max 90 days
            raise WorkflowExecutionError(
                f"Timeout must be between 1 and 2160 hours (90 days), got {timeout_hours}"
            )

        now = datetime.now(UTC)
        timeout_at = now + timedelta(hours=timeout_hours)

        wait_config = {
            "event_type": event_type.value,
            "timeout_hours": timeout_hours,
            "timeout_action": timeout_action,
        }

        return cls(
            id=uuid4(),
            workflow_execution_id=workflow_execution_id,
            workflow_id=workflow_id,
            contact_id=contact_id,
            account_id=account_id,
            step_id=step_id,
            wait_type=WaitType.FOR_EVENT,
            wait_config=wait_config,
            event_type=event_type,
            event_correlation_id=correlation_id,
            event_timeout_at=timeout_at,
            status=WaitExecutionStatus.WAITING,
            created_at=now,
            updated_at=now,
        )

    def resume(self, resumed_by: str) -> None:
        """Resume the workflow execution after wait.

        Args:
            resumed_by: What triggered resumption (scheduler, event, timeout, manual).

        Raises:
            InvalidExecutionStatusTransitionError: If transition is invalid.
        """
        if not self.status.can_transition_to(WaitExecutionStatus.RESUMED):
            raise InvalidExecutionStatusTransitionError(
                self.status.value,
                WaitExecutionStatus.RESUMED.value,
            )

        self.status = WaitExecutionStatus.RESUMED
        self.resumed_at = datetime.now(UTC)
        self.resumed_by = resumed_by
        self._touch()

    def cancel(self) -> None:
        """Cancel the wait execution.

        Raises:
            InvalidExecutionStatusTransitionError: If transition is invalid.
        """
        if not self.status.can_transition_to(WaitExecutionStatus.CANCELLED):
            raise InvalidExecutionStatusTransitionError(
                self.status.value,
                WaitExecutionStatus.CANCELLED.value,
            )

        self.status = WaitExecutionStatus.CANCELLED
        self._touch()

    def timeout(self) -> None:
        """Mark the wait as timed out.

        Raises:
            InvalidExecutionStatusTransitionError: If transition is invalid.
        """
        if not self.status.can_transition_to(WaitExecutionStatus.TIMEOUT):
            raise InvalidExecutionStatusTransitionError(
                self.status.value,
                WaitExecutionStatus.TIMEOUT.value,
            )

        self.status = WaitExecutionStatus.TIMEOUT
        self.resumed_at = datetime.now(UTC)
        self.resumed_by = "timeout"
        self._touch()

    def mark_error(self, error_message: str) -> None:
        """Mark the wait as errored.

        Args:
            error_message: Error description.
        """
        self.status = WaitExecutionStatus.ERROR
        self.wait_config["error_message"] = error_message
        self._touch()

    def _touch(self) -> None:
        """Update timestamp."""
        self.updated_at = datetime.now(UTC)

    @property
    def is_waiting(self) -> bool:
        """Check if wait is still active."""
        return self.status == WaitExecutionStatus.WAITING

    @property
    def is_scheduled(self) -> bool:
        """Check if wait is scheduled."""
        return self.status == WaitExecutionStatus.SCHEDULED

    @property
    def is_resumed(self) -> bool:
        """Check if wait has been resumed."""
        return self.status == WaitExecutionStatus.RESUMED

    @property
    def is_terminal(self) -> bool:
        """Check if wait is in a terminal state."""
        return self.status in (
            WaitExecutionStatus.RESUMED,
            WaitExecutionStatus.TIMEOUT,
            WaitExecutionStatus.CANCELLED,
            WaitExecutionStatus.ERROR,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary containing all wait execution attributes.
        """
        return {
            "id": str(self.id),
            "workflow_execution_id": str(self.workflow_execution_id),
            "workflow_id": str(self.workflow_id),
            "contact_id": str(self.contact_id),
            "account_id": str(self.account_id),
            "step_id": self.step_id,
            "wait_type": self.wait_type.value,
            "wait_config": self.wait_config,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "timezone": self.timezone,
            "event_type": self.event_type.value if self.event_type else None,
            "event_correlation_id": str(self.event_correlation_id) if self.event_correlation_id else None,
            "event_timeout_at": self.event_timeout_at.isoformat() if self.event_timeout_at else None,
            "status": self.status.value,
            "resumed_at": self.resumed_at.isoformat() if self.resumed_at else None,
            "resumed_by": self.resumed_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class EventListener:
    """Event listener registration.

    This entity represents an active listener waiting for a specific event
    to trigger workflow resumption.

    Attributes:
        id: Unique listener identifier.
        wait_execution_id: Reference to wait execution.
        event_type: Type of event being listened for.
        correlation_id: Optional correlation ID for event matching.
        contact_id: Contact being processed.
        workflow_execution_id: Workflow execution instance.
        match_criteria: Additional matching criteria (JSON).
        expires_at: When the listener expires (timeout).
        status: Listener status (active, matched, expired, cancelled).
        matched_at: When the event was matched.
        matched_event_id: ID of the matched event.
        created_at: Listener creation time.
    """

    id: UUID
    wait_execution_id: UUID
    event_type: EventType
    correlation_id: UUID | None
    contact_id: UUID
    workflow_execution_id: UUID
    match_criteria: dict[str, Any]
    expires_at: datetime
    status: str = "active"
    matched_at: datetime | None = None
    matched_event_id: UUID | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        wait_execution_id: UUID,
        event_type: EventType,
        contact_id: UUID,
        workflow_execution_id: UUID,
        expires_at: datetime,
        correlation_id: UUID | None = None,
        match_criteria: dict[str, Any] | None = None,
    ) -> Self:
        """Factory method to create a new event listener.

        Args:
            wait_execution_id: Wait execution this listener is for.
            event_type: Type of event to listen for.
            contact_id: Contact being processed.
            workflow_execution_id: Workflow execution instance.
            expires_at: When the listener expires.
            correlation_id: Optional correlation ID for event matching.
            match_criteria: Additional matching criteria.

        Returns:
            A new EventListener instance.
        """
        now = datetime.now(UTC)

        return cls(
            id=uuid4(),
            wait_execution_id=wait_execution_id,
            event_type=event_type,
            correlation_id=correlation_id,
            contact_id=contact_id,
            workflow_execution_id=workflow_execution_id,
            match_criteria=match_criteria or {},
            expires_at=expires_at,
            status="active",
            created_at=now,
        )

    def match(self, event_id: UUID) -> None:
        """Mark the listener as matched.

        Args:
            event_id: ID of the event that matched.
        """
        self.status = "matched"
        self.matched_at = datetime.now(UTC)
        self.matched_event_id = event_id

    def cancel(self) -> None:
        """Cancel the listener."""
        self.status = "cancelled"

    def expire(self) -> None:
        """Mark the listener as expired."""
        self.status = "expired"

    @property
    def is_active(self) -> bool:
        """Check if listener is active."""
        return self.status == "active"

    @property
    def is_expired(self) -> bool:
        """Check if listener has expired."""
        return datetime.now(UTC) > self.expires_at

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary containing all listener attributes.
        """
        return {
            "id": str(self.id),
            "wait_execution_id": str(self.wait_execution_id),
            "event_type": self.event_type.value,
            "correlation_id": str(self.correlation_id) if self.correlation_id else None,
            "contact_id": str(self.contact_id),
            "workflow_execution_id": str(self.workflow_execution_id),
            "match_criteria": self.match_criteria,
            "expires_at": self.expires_at.isoformat(),
            "status": self.status,
            "matched_at": self.matched_at.isoformat() if self.matched_at else None,
            "matched_event_id": str(self.matched_event_id) if self.matched_event_id else None,
            "created_at": self.created_at.isoformat(),
        }
