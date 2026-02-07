"""Repository for trigger persistence and retrieval.

This repository handles all database operations for triggers
and trigger execution logs.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.workflows.domain.trigger_entity import Trigger
from src.workflows.domain.triggers import TriggerEvent, TriggerFilters, TriggerSettings
from src.workflows.infrastructure.trigger_models import (
    TriggerExecutionLogModel,
    TriggerModel,
)


class TriggerRepository:
    """Repository for trigger data access.

    This repository provides methods for creating, updating, and querying
    trigger configurations and execution logs.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with a database session.

        Args:
            session: The async database session.
        """
        self._session = session

    async def create(self, trigger: Trigger) -> Trigger:
        """Create a new trigger in the database.

        Args:
            trigger: The trigger entity to persist.

        Returns:
            The persisted trigger with database-assigned values.
        """
        model = TriggerModel(
            id=trigger.id,
            workflow_id=trigger.workflow_id,
            event=trigger.event.value,
            category=trigger.event.get_category().value,
            filters=trigger.filters.to_dict(),
            settings=trigger.settings.to_dict(),
            is_active=trigger.is_active,
            created_at=trigger.created_at,
            updated_at=trigger.updated_at,
            created_by=trigger.created_by,
        )

        self._session.add(model)
        await self._session.flush()

        return trigger

    async def get_by_workflow_id(self, workflow_id: UUID) -> Trigger | None:
        """Get trigger by workflow ID.

        Args:
            workflow_id: The workflow ID.

        Returns:
            Trigger entity if found, None otherwise.
        """
        stmt = select(TriggerModel).where(
            TriggerModel.workflow_id == workflow_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._model_to_entity(model)

    async def get_by_id(self, trigger_id: UUID) -> Trigger | None:
        """Get trigger by ID.

        Args:
            trigger_id: The trigger ID.

        Returns:
            Trigger entity if found, None otherwise.
        """
        stmt = select(TriggerModel).where(TriggerModel.id == trigger_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._model_to_entity(model)

    async def get_active_triggers_by_event(
        self,
        event: TriggerEvent,
        account_id: UUID,
    ) -> list[Trigger]:
        """Get all active triggers for a specific event within an account.

        Args:
            event: The trigger event.
            account_id: The account ID.

        Returns:
            List of active triggers for the event.
        """
        category = event.get_category()

        stmt = (
            select(TriggerModel)
            .join(TriggerModel.workflow)
            .where(
                TriggerModel.event == event.value,
                TriggerModel.category == category.value,
                TriggerModel.is_active == True,
                TriggerModel.workflow_id
                == select(TriggerModel.workflow_id).where(TriggerModel.is_active == True),
            )
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(model) for model in models]

    async def update(self, trigger: Trigger) -> Trigger | None:
        """Update an existing trigger.

        Args:
            trigger: The trigger entity with updated values.

        Returns:
            Updated trigger entity, or None if not found.
        """
        stmt = (
            update(TriggerModel)
            .where(TriggerModel.id == trigger.id)
            .values(
                event=trigger.event.value,
                category=trigger.event.get_category().value,
                filters=trigger.filters.to_dict(),
                settings=trigger.settings.to_dict(),
                is_active=trigger.is_active,
                updated_at=trigger.updated_at,
            )
            .returning(TriggerModel)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return trigger

    async def delete(self, trigger_id: UUID) -> bool:
        """Delete a trigger by ID.

        Args:
            trigger_id: The trigger ID.

        Returns:
            True if deleted, False if not found.
        """
        # Note: Deletion is handled by CASCADE delete from workflow
        # This method is for explicit trigger deletion if needed
        stmt = select(TriggerModel).where(TriggerModel.id == trigger_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return False

        await self._session.delete(model)
        return True

    async def log_execution(
        self,
        trigger_id: UUID,
        contact_id: UUID,
        event_data: dict[str, Any],
        matched: bool,
        enrolled: bool,
        failure_reason: str | None = None,
    ) -> None:
        """Log a trigger execution event.

        Args:
            trigger_id: The trigger ID.
            contact_id: The contact ID.
            event_data: The event payload.
            matched: Whether the filters matched.
            enrolled: Whether the contact was enrolled.
            failure_reason: Reason if enrollment failed.
        """
        log = TriggerExecutionLogModel(
            id=uuid4(),
            trigger_id=trigger_id,
            contact_id=contact_id,
            event_data=event_data,
            matched=matched,
            enrolled=enrolled,
            failure_reason=failure_reason,
            executed_at=datetime.now(UTC),
        )

        self._session.add(log)

    async def get_execution_logs(
        self,
        trigger_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get execution logs for a trigger.

        Args:
            trigger_id: The trigger ID.
            limit: Maximum number of logs to return.
            offset: Number of logs to skip.

        Returns:
            List of execution log dictionaries.
        """
        stmt = (
            select(TriggerExecutionLogModel)
            .where(TriggerExecutionLogModel.trigger_id == trigger_id)
            .order_by(TriggerExecutionLogModel.executed_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [
            {
                "id": str(model.id),
                "trigger_id": str(model.trigger_id),
                "contact_id": str(model.contact_id),
                "event_data": model.event_data,
                "matched": model.matched,
                "enrolled": model.enrolled,
                "failure_reason": model.failure_reason,
                "executed_at": model.executed_at.isoformat(),
            }
            for model in models
        ]

    @staticmethod
    def _model_to_entity(model: TriggerModel) -> Trigger:
        """Convert a database model to a domain entity.

        Args:
            model: The database model.

        Returns:
            Trigger domain entity.
        """
        return Trigger(
            id=model.id,
            workflow_id=model.workflow_id,
            event=TriggerEvent(model.event),
            filters=TriggerFilters.from_dict(model.filters),
            settings=TriggerSettings.from_dict(model.settings),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
        )
