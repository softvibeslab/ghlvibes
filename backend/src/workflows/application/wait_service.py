"""Application service for wait step scheduling and management.

This service provides the business logic for creating, scheduling,
and managing wait steps in workflow executions.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.workflows.domain.wait_entities import (
    EventListener,
    EventType,
    TimeUnit,
    WaitStepExecution,
)
from src.workflows.infrastructure.wait_models import (
    EventListenerModel,
    WaitExecutionModel,
)


class WaitConfigurationError(Exception):
    """Raised when wait configuration is invalid."""

    pass


class WaitNotFoundError(Exception):
    """Raised when wait execution is not found."""

    pass


@dataclass
class WaitCreateResult:
    """Result of creating a wait execution.

    Attributes:
        wait_execution: The created wait execution entity.
        scheduled_at: When the wait is scheduled to resume.
        status: Current status of the wait.
    """

    wait_execution: WaitStepExecution
    scheduled_at: datetime | None
    status: str


@dataclass
class WaitStatus:
    """Status information for a wait execution.

    Attributes:
        id: Wait execution ID.
        status: Current status.
        scheduled_at: When scheduled to resume (if applicable).
        resumed_at: When actually resumed (if completed).
        resumed_by: What triggered resumption (if completed).
    """

    id: UUID
    status: str
    scheduled_at: datetime | None
    resumed_at: datetime | None
    resumed_by: str | None


@dataclass
class PendingWaitsSummary:
    """Summary of pending wait executions.

    Attributes:
        total_count: Total number of pending waits.
        by_type: Count of waits by type.
        upcoming_resumes: List of upcoming resume timestamps.
        overdue_count: Number of overdue waits.
    """

    total_count: int
    by_type: dict[str, int]
    upcoming_resumes: list[datetime]
    overdue_count: int


class WaitSchedulingService:
    """Service for managing wait step scheduling and execution.

    This service handles:
    - Creating wait executions for different wait types
    - Scheduling background jobs for time-based waits
    - Registering event listeners for event-based waits
    - Processing wait resumes and timeouts
    - Managing wait cancellation
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the wait scheduling service.

        Args:
            session: Database session for persistence.
        """
        self.session = session

    async def create_fixed_time_wait(
        self,
        workflow_execution_id: UUID,
        workflow_id: UUID,
        contact_id: UUID,
        account_id: UUID,
        step_id: str,
        duration: int,
        unit: TimeUnit,
        timezone: str = "UTC",
    ) -> WaitCreateResult:
        """Create a fixed time wait execution.

        Args:
            workflow_execution_id: Workflow execution instance.
            workflow_id: Workflow definition.
            contact_id: Contact being processed.
            account_id: Account identifier.
            step_id: Step identifier.
            duration: Duration value.
            unit: Time unit.
            timezone: Timezone for calculations.

        Returns:
            WaitCreateResult with created execution.

        Raises:
            WaitConfigurationError: If configuration is invalid.
        """
        try:
            # Create domain entity
            wait_execution = WaitStepExecution.create_fixed_time_wait(
                workflow_execution_id=workflow_execution_id,
                workflow_id=workflow_id,
                contact_id=contact_id,
                account_id=account_id,
                step_id=step_id,
                duration=duration,
                unit=unit,
                timezone=timezone,
            )

            # Persist to database
            model = self._domain_to_model(wait_execution)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)

            # Update domain entity with generated ID
            wait_execution.id = model.id

            # Schedule background job (placeholder for Celery integration)
            await self._schedule_resume_job(wait_execution)

            return WaitCreateResult(
                wait_execution=wait_execution,
                scheduled_at=wait_execution.scheduled_at,
                status=wait_execution.status.value,
            )

        except ValueError as e:
            raise WaitConfigurationError(f"Invalid fixed time wait configuration: {e}") from e
        except Exception as e:
            raise WaitConfigurationError(f"Failed to create fixed time wait: {e}") from e

    async def create_until_date_wait(
        self,
        workflow_execution_id: UUID,
        workflow_id: UUID,
        contact_id: UUID,
        account_id: UUID,
        step_id: str,
        target_date: datetime,
        timezone: str = "UTC",
    ) -> WaitCreateResult:
        """Create a wait until specific date.

        Args:
            workflow_execution_id: Workflow execution instance.
            workflow_id: Workflow definition.
            contact_id: Contact being processed.
            account_id: Account identifier.
            step_id: Step identifier.
            target_date: Target date/time.
            timezone: Timezone for calculations.

        Returns:
            WaitCreateResult with created execution.

        Raises:
            WaitConfigurationError: If configuration is invalid.
        """
        try:
            wait_execution = WaitStepExecution.create_until_date_wait(
                workflow_execution_id=workflow_execution_id,
                workflow_id=workflow_id,
                contact_id=contact_id,
                account_id=account_id,
                step_id=step_id,
                target_date=target_date,
                timezone=timezone,
            )

            model = self._domain_to_model(wait_execution)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)

            wait_execution.id = model.id
            await self._schedule_resume_job(wait_execution)

            return WaitCreateResult(
                wait_execution=wait_execution,
                scheduled_at=wait_execution.scheduled_at,
                status=wait_execution.status.value,
            )

        except ValueError as e:
            raise WaitConfigurationError(f"Invalid until date wait configuration: {e}") from e
        except Exception as e:
            raise WaitConfigurationError(f"Failed to create until date wait: {e}") from e

    async def create_until_time_wait(
        self,
        workflow_execution_id: UUID,
        workflow_id: UUID,
        contact_id: UUID,
        account_id: UUID,
        step_id: str,
        target_time: str,
        timezone: str,
        days: list[str] | None = None,
    ) -> WaitCreateResult:
        """Create a wait until specific time of day.

        Args:
            workflow_execution_id: Workflow execution instance.
            workflow_id: Workflow definition.
            contact_id: Contact being processed.
            account_id: Account identifier.
            step_id: Step identifier.
            target_time: Target time in HH:MM format.
            timezone: IANA timezone string.
            days: Optional day restrictions.

        Returns:
            WaitCreateResult with created execution.

        Raises:
            WaitConfigurationError: If configuration is invalid.
        """
        try:
            wait_execution = WaitStepExecution.create_until_time_wait(
                workflow_execution_id=workflow_execution_id,
                workflow_id=workflow_id,
                contact_id=contact_id,
                account_id=account_id,
                step_id=step_id,
                target_time=target_time,
                timezone=timezone,
                days=days,
            )

            model = self._domain_to_model(wait_execution)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)

            wait_execution.id = model.id
            await self._schedule_resume_job(wait_execution)

            return WaitCreateResult(
                wait_execution=wait_execution,
                scheduled_at=wait_execution.scheduled_at,
                status=wait_execution.status.value,
            )

        except ValueError as e:
            raise WaitConfigurationError(f"Invalid until time wait configuration: {e}") from e
        except Exception as e:
            raise WaitConfigurationError(f"Failed to create until time wait: {e}") from e

    async def create_event_wait(
        self,
        workflow_execution_id: UUID,
        workflow_id: UUID,
        contact_id: UUID,
        account_id: UUID,
        step_id: str,
        event_type: EventType,
        timeout_hours: int = 168,
        timeout_action: str = "continue",
        correlation_id: UUID | None = None,
    ) -> WaitCreateResult:
        """Create an event-based wait.

        Args:
            workflow_execution_id: Workflow execution instance.
            workflow_id: Workflow definition.
            contact_id: Contact being processed.
            account_id: Account identifier.
            step_id: Step identifier.
            event_type: Type of event to wait for.
            timeout_hours: Maximum hours to wait.
            timeout_action: Action on timeout.
            correlation_id: Optional correlation ID.

        Returns:
            WaitCreateResult with created execution.

        Raises:
            WaitConfigurationError: If configuration is invalid.
        """
        try:
            wait_execution = WaitStepExecution.create_event_wait(
                workflow_execution_id=workflow_execution_id,
                workflow_id=workflow_id,
                contact_id=contact_id,
                account_id=account_id,
                step_id=step_id,
                event_type=event_type,
                timeout_hours=timeout_hours,
                timeout_action=timeout_action,
                correlation_id=correlation_id,
            )

            model = self._domain_to_model(wait_execution)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)

            wait_execution.id = model.id

            # Register event listener
            await self._register_event_listener(wait_execution)

            # Schedule timeout job
            await self._schedule_timeout_job(wait_execution)

            return WaitCreateResult(
                wait_execution=wait_execution,
                scheduled_at=None,  # Event waits don't have scheduled resume
                status=wait_execution.status.value,
            )

        except ValueError as e:
            raise WaitConfigurationError(f"Invalid event wait configuration: {e}") from e
        except Exception as e:
            raise WaitConfigurationError(f"Failed to create event wait: {e}") from e

    async def get_wait_status(self, wait_id: UUID) -> WaitStatus:
        """Get the status of a wait execution.

        Args:
            wait_id: Wait execution ID.

        Returns:
            WaitStatus with current status information.

        Raises:
            WaitNotFoundError: If wait execution not found.
        """
        query = select(WaitExecutionModel).where(WaitExecutionModel.id == wait_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if model is None:
            raise WaitNotFoundError(f"Wait execution {wait_id} not found")

        return WaitStatus(
            id=model.id,
            status=model.status.value,
            scheduled_at=model.scheduled_at,
            resumed_at=model.resumed_at,
            resumed_by=model.resumed_by,
        )

    async def cancel_wait(self, wait_id: UUID) -> bool:
        """Cancel a wait execution.

        Args:
            wait_id: Wait execution ID.

        Returns:
            True if cancelled successfully.

        Raises:
            WaitNotFoundError: If wait execution not found.
        """
        query = select(WaitExecutionModel).where(WaitExecutionModel.id == wait_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if model is None:
            raise WaitNotFoundError(f"Wait execution {wait_id} not found")

        # Convert to domain entity
        wait_execution = self._model_to_domain(model)

        # Cancel the wait
        wait_execution.cancel()

        # Update model
        model.status = wait_execution.status
        model.updated_at = wait_execution.updated_at

        # Cancel associated event listeners
        await self._cancel_event_listeners(wait_id)

        # Cancel scheduled jobs
        await self._cancel_scheduled_jobs(wait_id)

        await self.session.flush()

        return True

    async def resume_wait(self, wait_id: UUID, resumed_by: str = "scheduler") -> WaitStatus:
        """Resume a wait execution.

        Args:
            wait_id: Wait execution ID.
            resumed_by: What triggered resumption.

        Returns:
            Updated WaitStatus.

        Raises:
            WaitNotFoundError: If wait execution not found.
        """
        query = select(WaitExecutionModel).where(WaitExecutionModel.id == wait_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if model is None:
            raise WaitNotFoundError(f"Wait execution {wait_id} not found")

        wait_execution = self._model_to_domain(model)
        wait_execution.resume(resumed_by)

        # Update model
        model.status = wait_execution.status
        model.resumed_at = wait_execution.resumed_at
        model.resumed_by = wait_execution.resumed_by
        model.updated_at = wait_execution.updated_at

        await self.session.flush()

        return WaitStatus(
            id=model.id,
            status=model.status.value,
            scheduled_at=model.scheduled_at,
            resumed_at=model.resumed_at,
            resumed_by=model.resumed_by,
        )

    async def _schedule_resume_job(self, wait_execution: WaitStepExecution) -> None:
        """Schedule a background job for wait resumption.

        This is a placeholder for Celery integration.
        In production, this would create a Celery task scheduled
        to execute at wait_execution.scheduled_at.

        Args:
            wait_execution: Wait execution to schedule.
        """
        # TODO: Integrate with Celery - create scheduled task
        pass

    async def _schedule_timeout_job(self, wait_execution: WaitStepExecution) -> None:
        """Schedule a background job for event wait timeout.

        This is a placeholder for Celery integration.

        Args:
            wait_execution: Event wait execution.
        """
        # TODO: Integrate with Celery - create timeout task
        pass

    async def _register_event_listener(self, wait_execution: WaitStepExecution) -> None:
        """Register an event listener for the wait.

        Args:
            wait_execution: Event wait execution.
        """
        if wait_execution.event_type is None:
            return

        listener = EventListener.create(
            wait_execution_id=wait_execution.id,
            event_type=wait_execution.event_type,
            contact_id=wait_execution.contact_id,
            workflow_execution_id=wait_execution.workflow_execution_id,
            expires_at=wait_execution.event_timeout_at or datetime.now(UTC),
            correlation_id=wait_execution.event_correlation_id,
        )

        listener_model = EventListenerModel(
            id=listener.id,
            wait_execution_id=listener.wait_execution_id,
            event_type=listener.event_type,
            correlation_id=listener.correlation_id,
            contact_id=listener.contact_id,
            workflow_execution_id=listener.workflow_execution_id,
            match_criteria=listener.match_criteria,
            expires_at=listener.expires_at,
            status=listener.status,
            created_at=listener.created_at,
        )

        self.session.add(listener_model)
        await self.session.flush()

    async def _cancel_event_listeners(self, wait_id: UUID) -> None:
        """Cancel all event listeners for a wait execution.

        Args:
            wait_id: Wait execution ID.
        """
        query = select(EventListenerModel).where(
            EventListenerModel.wait_execution_id == wait_id,
            EventListenerModel.status == "active",
        )
        result = await self.session.execute(query)
        listeners = result.scalars().all()

        for listener in listeners:
            listener.status = "cancelled"

    async def _cancel_scheduled_jobs(self, wait_id: UUID) -> None:
        """Cancel scheduled jobs for a wait execution.

        This is a placeholder for Celery integration.

        Args:
            wait_id: Wait execution ID.
        """
        # TODO: Integrate with Celery - cancel scheduled task
        pass

    def _domain_to_model(self, wait_execution: WaitStepExecution) -> WaitExecutionModel:
        """Convert domain entity to SQLAlchemy model.

        Args:
            wait_execution: Domain entity.

        Returns:
            SQLAlchemy model.
        """
        return WaitExecutionModel(
            id=wait_execution.id,
            workflow_execution_id=wait_execution.workflow_execution_id,
            workflow_id=wait_execution.workflow_id,
            contact_id=wait_execution.contact_id,
            account_id=wait_execution.account_id,
            step_id=wait_execution.step_id,
            wait_type=wait_execution.wait_type,
            wait_config=wait_execution.wait_config,
            scheduled_at=wait_execution.scheduled_at,
            timezone=wait_execution.timezone,
            event_type=wait_execution.event_type,
            event_correlation_id=wait_execution.event_correlation_id,
            event_timeout_at=wait_execution.event_timeout_at,
            status=wait_execution.status,
            resumed_at=wait_execution.resumed_at,
            resumed_by=wait_execution.resumed_by,
            created_at=wait_execution.created_at,
            updated_at=wait_execution.updated_at,
        )

    def _model_to_domain(self, model: WaitExecutionModel) -> WaitStepExecution:
        """Convert SQLAlchemy model to domain entity.

        Args:
            model: SQLAlchemy model.

        Returns:
            Domain entity.
        """
        return WaitStepExecution(
            id=model.id,
            workflow_execution_id=model.workflow_execution_id,
            workflow_id=model.workflow_id,
            contact_id=model.contact_id,
            account_id=model.account_id,
            step_id=model.step_id,
            wait_type=model.wait_type,
            wait_config=model.wait_config,
            scheduled_at=model.scheduled_at,
            timezone=model.timezone,
            event_type=model.event_type,
            event_correlation_id=model.event_correlation_id,
            event_timeout_at=model.event_timeout_at,
            status=model.status,
            resumed_at=model.resumed_at,
            resumed_by=model.resumed_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
