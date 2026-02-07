"""Unit tests for wait step domain entities.

These tests verify the behavior of wait step entities
and value objects following domain-driven design principles.
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from src.workflows.domain.execution_exceptions import (
    InvalidExecutionStatusTransitionError,
    WorkflowExecutionError,
)
from src.workflows.domain.wait_entities import (
    EventListener,
    EventType,
    TimeUnit,
    WaitExecutionStatus,
    WaitStepExecution,
    WaitType,
)
from src.workflows.domain.wait_exceptions import (
    InvalidWaitDateError,
    InvalidWaitDurationError,
    InvalidWaitTimeError,
)


class TestWaitType:
    """Tests for WaitType enum."""

    def test_wait_type_values(self) -> None:
        """Test that WaitType has all expected values."""
        assert WaitType.FIXED_TIME.value == "fixed_time"
        assert WaitType.UNTIL_DATE.value == "until_date"
        assert WaitType.UNTIL_TIME.value == "until_time"
        assert WaitType.FOR_EVENT.value == "for_event"

    def test_wait_type_is_string_enum(self) -> None:
        """Test that WaitType is a string enum."""
        assert isinstance(WaitType.FIXED_TIME.value, str)


class TestWaitExecutionStatus:
    """Tests for WaitExecutionStatus enum."""

    def test_status_values(self) -> None:
        """Test that status has all expected values."""
        assert WaitExecutionStatus.WAITING.value == "waiting"
        assert WaitExecutionStatus.SCHEDULED.value == "scheduled"
        assert WaitExecutionStatus.RESUMED.value == "resumed"
        assert WaitExecutionStatus.TIMEOUT.value == "timeout"
        assert WaitExecutionStatus.CANCELLED.value == "cancelled"
        assert WaitExecutionStatus.ERROR.value == "error"

    def test_waiting_can_transition_to_scheduled(self) -> None:
        """Test valid transition from waiting to scheduled."""
        assert WaitExecutionStatus.WAITING.can_transition_to(WaitExecutionStatus.SCHEDULED)

    def test_waiting_can_transition_to_resumed(self) -> None:
        """Test valid transition from waiting to resumed."""
        assert WaitExecutionStatus.WAITING.can_transition_to(WaitExecutionStatus.RESUMED)

    def test_waiting_can_transition_to_cancelled(self) -> None:
        """Test valid transition from waiting to cancelled."""
        assert WaitExecutionStatus.WAITING.can_transition_to(WaitExecutionStatus.CANCELLED)

    def test_scheduled_can_transition_to_resumed(self) -> None:
        """Test valid transition from scheduled to resumed."""
        assert WaitExecutionStatus.SCHEDULED.can_transition_to(WaitExecutionStatus.RESUMED)

    def test_scheduled_can_transition_to_timeout(self) -> None:
        """Test valid transition from scheduled to timeout."""
        assert WaitExecutionStatus.SCHEDULED.can_transition_to(WaitExecutionStatus.TIMEOUT)

    def test_resumed_is_terminal(self) -> None:
        """Test that resumed is a terminal state."""
        assert not WaitExecutionStatus.RESUMED.can_transition_to(WaitExecutionStatus.SCHEDULED)
        assert not WaitExecutionStatus.RESUMED.can_transition_to(WaitExecutionStatus.WAITING)

    def test_cancelled_is_terminal(self) -> None:
        """Test that cancelled is a terminal state."""
        transitions = WaitExecutionStatus.CANCELLED.can_transition_to(WaitExecutionStatus.WAITING)
        assert not transitions


class TestTimeUnit:
    """Tests for TimeUnit enum and timedelta conversion."""

    def test_time_unit_values(self) -> None:
        """Test that TimeUnit has all expected values."""
        assert TimeUnit.MINUTES.value == "minutes"
        assert TimeUnit.HOURS.value == "hours"
        assert TimeUnit.DAYS.value == "days"
        assert TimeUnit.WEEKS.value == "weeks"

    def test_minutes_to_timedelta(self) -> None:
        """Test converting minutes to timedelta."""
        td = TimeUnit.MINUTES.to_timedelta(30)
        assert td == timedelta(minutes=30)

    def test_hours_to_timedelta(self) -> None:
        """Test converting hours to timedelta."""
        td = TimeUnit.HOURS.to_timedelta(2)
        assert td == timedelta(hours=2)

    def test_days_to_timedelta(self) -> None:
        """Test converting days to timedelta."""
        td = TimeUnit.DAYS.to_timedelta(7)
        assert td == timedelta(days=7)

    def test_weeks_to_timedelta(self) -> None:
        """Test converting weeks to timedelta."""
        td = TimeUnit.WEEKS.to_timedelta(2)
        assert td == timedelta(weeks=2)

    def test_minutes_valid_range(self) -> None:
        """Test that minutes accept valid range."""
        TimeUnit.MINUTES.to_timedelta(1)  # Minimum
        TimeUnit.MINUTES.to_timedelta(59)  # Maximum

    def test_minutes_invalid_range_low(self) -> None:
        """Test that minutes reject values below minimum."""
        with pytest.raises(ValueError, match="Minutes must be between 1 and 59"):
            TimeUnit.MINUTES.to_timedelta(0)

    def test_minutes_invalid_range_high(self) -> None:
        """Test that minutes reject values above maximum."""
        with pytest.raises(ValueError, match="Minutes must be between 1 and 59"):
            TimeUnit.MINUTES.to_timedelta(60)

    def test_hours_valid_range(self) -> None:
        """Test that hours accept valid range."""
        TimeUnit.HOURS.to_timedelta(1)  # Minimum
        TimeUnit.HOURS.to_timedelta(23)  # Maximum

    def test_hours_invalid_range(self) -> None:
        """Test that hours reject invalid range."""
        with pytest.raises(ValueError, match="Hours must be between 1 and 23"):
            TimeUnit.HOURS.to_timedelta(24)

    def test_days_valid_range(self) -> None:
        """Test that days accept valid range."""
        TimeUnit.DAYS.to_timedelta(1)  # Minimum
        TimeUnit.DAYS.to_timedelta(30)  # Maximum

    def test_days_invalid_range(self) -> None:
        """Test that days reject invalid range."""
        with pytest.raises(ValueError, match="Days must be between 1 and 30"):
            TimeUnit.DAYS.to_timedelta(31)

    def test_weeks_valid_range(self) -> None:
        """Test that weeks accept valid range."""
        TimeUnit.WEEKS.to_timedelta(1)  # Minimum
        TimeUnit.WEEKS.to_timedelta(12)  # Maximum

    def test_weeks_invalid_range(self) -> None:
        """Test that weeks reject invalid range."""
        with pytest.raises(ValueError, match="Weeks must be between 1 and 12"):
            TimeUnit.WEEKS.to_timedelta(13)


class TestWaitStepExecution:
    """Tests for WaitStepExecution entity."""

    def test_create_fixed_time_wait_minutes(self) -> None:
        """Test creating a fixed time wait with minutes."""
        execution_id = uuid4()
        workflow_id = uuid4()
        contact_id = uuid4()
        account_id = uuid4()

        wait = WaitStepExecution.create_fixed_time_wait(
            workflow_execution_id=execution_id,
            workflow_id=workflow_id,
            contact_id=contact_id,
            account_id=account_id,
            step_id="step_1",
            duration=30,
            unit=TimeUnit.MINUTES,
        )

        assert wait.wait_type == WaitType.FIXED_TIME
        assert wait.status == WaitExecutionStatus.SCHEDULED
        assert wait.scheduled_at is not None
        assert wait.wait_config == {"duration": 30, "unit": "minutes"}
        assert wait.timezone == "UTC"

        # Verify scheduled time is approximately 30 minutes in the future
        expected_delta = timedelta(minutes=30)
        actual_delta = wait.scheduled_at - wait.created_at
        assert abs(actual_delta - expected_delta) < timedelta(seconds=1)

    def test_create_fixed_time_wait_days(self) -> None:
        """Test creating a fixed time wait with days."""
        execution_id = uuid4()
        workflow_id = uuid4()
        contact_id = uuid4()
        account_id = uuid4()

        wait = WaitStepExecution.create_fixed_time_wait(
            workflow_execution_id=execution_id,
            workflow_id=workflow_id,
            contact_id=contact_id,
            account_id=account_id,
            step_id="step_1",
            duration=7,
            unit=TimeUnit.DAYS,
        )

        assert wait.wait_config == {"duration": 7, "unit": "days"}

        # Verify scheduled time is approximately 7 days in the future
        expected_delta = timedelta(days=7)
        actual_delta = wait.scheduled_at - wait.created_at
        assert abs(actual_delta - expected_delta) < timedelta(seconds=1)

    def test_create_fixed_time_wait_invalid_duration(self) -> None:
        """Test that invalid duration raises error."""
        with pytest.raises(WorkflowExecutionError, match="Invalid duration"):
            WaitStepExecution.create_fixed_time_wait(
                workflow_execution_id=uuid4(),
                workflow_id=uuid4(),
                contact_id=uuid4(),
                account_id=uuid4(),
                step_id="step_1",
                duration=100,  # Invalid for minutes
                unit=TimeUnit.MINUTES,
            )

    def test_create_until_date_wait_future(self) -> None:
        """Test creating wait until future date."""
        target_date = datetime.now(UTC) + timedelta(days=7)

        wait = WaitStepExecution.create_until_date_wait(
            workflow_execution_id=uuid4(),
            workflow_id=uuid4(),
            contact_id=uuid4(),
            account_id=uuid4(),
            step_id="step_1",
            target_date=target_date,
        )

        assert wait.wait_type == WaitType.UNTIL_DATE
        assert wait.status == WaitExecutionStatus.SCHEDULED
        assert wait.scheduled_at == target_date
        assert "target_date" in wait.wait_config

    def test_create_until_date_wait_past_raises_error(self) -> None:
        """Test that past date raises error."""
        past_date = datetime.now(UTC) - timedelta(days=1)

        with pytest.raises(WorkflowExecutionError, match="Target date must be in the future"):
            WaitStepExecution.create_until_date_wait(
                workflow_execution_id=uuid4(),
                workflow_id=uuid4(),
                contact_id=uuid4(),
                account_id=uuid4(),
                step_id="step_1",
                target_date=past_date,
            )

    def test_create_until_date_wait_too_far_raises_error(self) -> None:
        """Test that date too far in future raises error."""
        far_future = datetime.now(UTC) + timedelta(days=400)

        with pytest.raises(WorkflowExecutionError, match="Target date must be within 1 year"):
            WaitStepExecution.create_until_date_wait(
                workflow_execution_id=uuid4(),
                workflow_id=uuid4(),
                contact_id=uuid4(),
                account_id=uuid4(),
                step_id="step_1",
                target_date=far_future,
            )

    def test_create_until_time_wait(self) -> None:
        """Test creating wait until specific time of day."""
        wait = WaitStepExecution.create_until_time_wait(
            workflow_execution_id=uuid4(),
            workflow_id=uuid4(),
            contact_id=uuid4(),
            account_id=uuid4(),
            step_id="step_1",
            target_time="09:00",
            timezone="America/New_York",
        )

        assert wait.wait_type == WaitType.UNTIL_TIME
        assert wait.status == WaitExecutionStatus.SCHEDULED
        assert wait.scheduled_at is not None
        assert wait.timezone == "America/New_York"
        assert wait.wait_config["target_time"] == "09:00"

    def test_create_until_time_wait_invalid_format(self) -> None:
        """Test that invalid time format raises error."""
        with pytest.raises(WorkflowExecutionError, match="Invalid time format"):
            WaitStepExecution.create_until_time_wait(
                workflow_execution_id=uuid4(),
                workflow_id=uuid4(),
                contact_id=uuid4(),
                account_id=uuid4(),
                step_id="step_1",
                target_time="9:00",  # Should be HH:MM
                timezone="UTC",
            )

    def test_create_event_wait(self) -> None:
        """Test creating event-based wait."""
        wait = WaitStepExecution.create_event_wait(
            workflow_execution_id=uuid4(),
            workflow_id=uuid4(),
            contact_id=uuid4(),
            account_id=uuid4(),
            step_id="step_1",
            event_type=EventType.EMAIL_OPEN,
            timeout_hours=72,
            timeout_action="continue",
        )

        assert wait.wait_type == WaitType.FOR_EVENT
        assert wait.status == WaitExecutionStatus.WAITING
        assert wait.event_type == EventType.EMAIL_OPEN
        assert wait.event_timeout_at is not None
        assert wait.wait_config["timeout_hours"] == 72
        assert wait.wait_config["timeout_action"] == "continue"

    def test_create_event_wait_default_timeout(self) -> None:
        """Test creating event wait with default timeout."""
        wait = WaitStepExecution.create_event_wait(
            workflow_execution_id=uuid4(),
            workflow_id=uuid4(),
            contact_id=uuid4(),
            account_id=uuid4(),
            step_id="step_1",
            event_type=EventType.SMS_REPLY,
        )

        # Default timeout is 168 hours (7 days)
        expected_timeout = timedelta(hours=168)
        actual_timeout = wait.event_timeout_at - wait.created_at
        assert abs(actual_timeout - expected_timeout) < timedelta(seconds=1)

    def test_create_event_wait_invalid_timeout(self) -> None:
        """Test that invalid timeout raises error."""
        with pytest.raises(WorkflowExecutionError, match="Timeout must be between 1 and 2160"):
            WaitStepExecution.create_event_wait(
                workflow_execution_id=uuid4(),
                workflow_id=uuid4(),
                contact_id=uuid4(),
                account_id=uuid4(),
                step_id="step_1",
                event_type=EventType.EMAIL_CLICK,
                timeout_hours=3000,  # Exceeds 90 days
            )

    def test_resume_scheduled_wait(self) -> None:
        """Test resuming a scheduled wait."""
        wait = WaitStepExecution.create_fixed_time_wait(
            workflow_execution_id=uuid4(),
            workflow_id=uuid4(),
            contact_id=uuid4(),
            account_id=uuid4(),
            step_id="step_1",
            duration=1,
            unit=TimeUnit.HOURS,
        )

        wait.resume("scheduler")

        assert wait.status == WaitExecutionStatus.RESUMED
        assert wait.resumed_at is not None
        assert wait.resumed_by == "scheduler"

    def test_resume_waiting_wait(self) -> None:
        """Test resuming a waiting (event-based) wait."""
        wait = WaitStepExecution.create_event_wait(
            workflow_execution_id=uuid4(),
            workflow_id=uuid4(),
            contact_id=uuid4(),
            account_id=uuid4(),
            step_id="step_1",
            event_type=EventType.EMAIL_OPEN,
        )

        wait.resume("event")

        assert wait.status == WaitExecutionStatus.RESUMED
        assert wait.resumed_by == "event"

    def test_resume_invalid_transition_raises_error(self) -> None:
        """Test that resuming resumed wait raises error."""
        wait = WaitStepExecution.create_fixed_time_wait(
            workflow_execution_id=uuid4(),
            workflow_id=uuid4(),
            contact_id=uuid4(),
            account_id=uuid4(),
            step_id="step_1",
            duration=1,
            unit=TimeUnit.HOURS,
        )

        wait.resume("scheduler")

        with pytest.raises(InvalidExecutionStatusTransitionError):
            wait.resume("scheduler")

    def test_cancel_scheduled_wait(self) -> None:
        """Test cancelling a scheduled wait."""
        wait = WaitStepExecution.create_fixed_time_wait(
            workflow_execution_id=uuid4(),
            workflow_id=uuid4(),
            contact_id=uuid4(),
            account_id=uuid4(),
            step_id="step_1",
            duration=1,
            unit=TimeUnit.HOURS,
        )

        wait.cancel()

        assert wait.status == WaitExecutionStatus.CANCELLED

    def test_timeout_scheduled_wait(self) -> None:
        """Test marking a wait as timed out."""
        wait = WaitStepExecution.create_fixed_time_wait(
            workflow_execution_id=uuid4(),
            workflow_id=uuid4(),
            contact_id=uuid4(),
            account_id=uuid4(),
            step_id="step_1",
            duration=1,
            unit=TimeUnit.HOURS,
        )

        wait.timeout()

        assert wait.status == WaitExecutionStatus.TIMEOUT
        assert wait.resumed_by == "timeout"
        assert wait.resumed_at is not None

    def test_mark_error(self) -> None:
        """Test marking a wait as errored."""
        wait = WaitStepExecution.create_fixed_time_wait(
            workflow_execution_id=uuid4(),
            workflow_id=uuid4(),
            contact_id=uuid4(),
            account_id=uuid4(),
            step_id="step_1",
            duration=1,
            unit=TimeUnit.HOURS,
        )

        wait.mark_error("Redis connection failed")

        assert wait.status == WaitExecutionStatus.ERROR
        assert wait.wait_config["error_message"] == "Redis connection failed"

    def test_is_waiting_property(self) -> None:
        """Test is_waiting property."""
        wait = WaitStepExecution.create_event_wait(
            workflow_execution_id=uuid4(),
            workflow_id=uuid4(),
            contact_id=uuid4(),
            account_id=uuid4(),
            step_id="step_1",
            event_type=EventType.EMAIL_OPEN,
        )

        assert wait.is_waiting is True

        wait.resume("event")
        assert wait.is_waiting is False

    def test_is_scheduled_property(self) -> None:
        """Test is_scheduled property."""
        wait = WaitStepExecution.create_fixed_time_wait(
            workflow_execution_id=uuid4(),
            workflow_id=uuid4(),
            contact_id=uuid4(),
            account_id=uuid4(),
            step_id="step_1",
            duration=1,
            unit=TimeUnit.HOURS,
        )

        assert wait.is_scheduled is True

        wait.resume("scheduler")
        assert wait.is_scheduled is False

    def test_is_terminal_property(self) -> None:
        """Test is_terminal property."""
        wait = WaitStepExecution.create_fixed_time_wait(
            workflow_execution_id=uuid4(),
            workflow_id=uuid4(),
            contact_id=uuid4(),
            account_id=uuid4(),
            step_id="step_1",
            duration=1,
            unit=TimeUnit.HOURS,
        )

        assert wait.is_terminal is False

        wait.resume("scheduler")
        assert wait.is_terminal is True

    def test_to_dict(self) -> None:
        """Test converting to dictionary."""
        wait = WaitStepExecution.create_fixed_time_wait(
            workflow_execution_id=uuid4(),
            workflow_id=uuid4(),
            contact_id=uuid4(),
            account_id=uuid4(),
            step_id="step_1",
            duration=30,
            unit=TimeUnit.MINUTES,
        )

        result = wait.to_dict()

        assert "id" in result
        assert "workflow_execution_id" in result
        assert "wait_type" in result
        assert "status" in result
        assert "scheduled_at" in result
        assert result["wait_type"] == "fixed_time"
        assert result["status"] == "scheduled"


class TestEventListener:
    """Tests for EventListener entity."""

    def test_create_event_listener(self) -> None:
        """Test creating an event listener."""
        listener = EventListener.create(
            wait_execution_id=uuid4(),
            event_type=EventType.EMAIL_OPEN,
            contact_id=uuid4(),
            workflow_execution_id=uuid4(),
            expires_at=datetime.now(UTC) + timedelta(hours=24),
        )

        assert listener.status == "active"
        assert listener.is_active is True
        assert listener.is_expired is False

    def test_create_event_listener_with_correlation(self) -> None:
        """Test creating listener with correlation ID."""
        correlation_id = uuid4()
        listener = EventListener.create(
            wait_execution_id=uuid4(),
            event_type=EventType.EMAIL_CLICK,
            contact_id=uuid4(),
            workflow_execution_id=uuid4(),
            expires_at=datetime.now(UTC) + timedelta(hours=24),
            correlation_id=correlation_id,
        )

        assert listener.correlation_id == correlation_id

    def test_match_event(self) -> None:
        """Test matching an event."""
        listener = EventListener.create(
            wait_execution_id=uuid4(),
            event_type=EventType.EMAIL_OPEN,
            contact_id=uuid4(),
            workflow_execution_id=uuid4(),
            expires_at=datetime.now(UTC) + timedelta(hours=24),
        )

        event_id = uuid4()
        listener.match(event_id)

        assert listener.status == "matched"
        assert listener.matched_event_id == event_id
        assert listener.matched_at is not None

    def test_cancel_listener(self) -> None:
        """Test cancelling a listener."""
        listener = EventListener.create(
            wait_execution_id=uuid4(),
            event_type=EventType.EMAIL_OPEN,
            contact_id=uuid4(),
            workflow_execution_id=uuid4(),
            expires_at=datetime.now(UTC) + timedelta(hours=24),
        )

        listener.cancel()

        assert listener.status == "cancelled"

    def test_expire_listener(self) -> None:
        """Test expiring a listener."""
        listener = EventListener.create(
            wait_execution_id=uuid4(),
            event_type=EventType.EMAIL_OPEN,
            contact_id=uuid4(),
            workflow_execution_id=uuid4(),
            expires_at=datetime.now(UTC) + timedelta(hours=24),
        )

        listener.expire()

        assert listener.status == "expired"

    def test_is_expired_true(self) -> None:
        """Test is_expired when expired."""
        listener = EventListener.create(
            wait_execution_id=uuid4(),
            event_type=EventType.EMAIL_OPEN,
            contact_id=uuid4(),
            workflow_execution_id=uuid4(),
            expires_at=datetime.now(UTC) - timedelta(hours=1),  # Past
        )

        assert listener.is_expired is True

    def test_to_dict(self) -> None:
        """Test converting to dictionary."""
        listener = EventListener.create(
            wait_execution_id=uuid4(),
            event_type=EventType.EMAIL_OPEN,
            contact_id=uuid4(),
            workflow_execution_id=uuid4(),
            expires_at=datetime.now(UTC) + timedelta(hours=24),
        )

        result = listener.to_dict()

        assert "id" in result
        assert "event_type" in result
        assert "status" in result
        assert "expires_at" in result
        assert result["event_type"] == "email_open"
