"""Repository implementation for workflow actions.

This repository provides data access operations for workflow actions
and their execution records.
"""

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import and_, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.workflows.domain.action_entities import (
    Action,
    ActionExecution,
    ActionExecutionStatus,
)
from src.workflows.domain.action_exceptions import ActionNotFoundError
from src.workflows.domain.action_value_objects import (
    ActionConfig,
    ActionType,
)
from src.workflows.infrastructure.action_models import (
    ActionExecutionModel,
    ActionModel,
)


class IActionRepository(ABC):
    """Abstract interface for action repository.

    This interface defines the contract that any action repository
    implementation must follow.
    """

    @abstractmethod
    async def create(self, action: Action) -> Action:
        """Create a new action.

        Args:
            action: The action entity to persist.

        Returns:
            The persisted action with any generated fields.
        """
        pass

    @abstractmethod
    async def get_by_id(self, action_id: UUID, workflow_id: UUID) -> Action | None:
        """Get an action by ID.

        Args:
            action_id: The unique action identifier.
            workflow_id: The workflow the action belongs to.

        Returns:
            The action if found, None otherwise.
        """
        pass

    @abstractmethod
    async def list_by_workflow(
        self,
        workflow_id: UUID,
        include_disabled: bool = False,
    ) -> list[Action]:
        """List all actions for a workflow.

        Args:
            workflow_id: The workflow to list actions for.
            include_disabled: Whether to include disabled actions.

        Returns:
            List of actions ordered by position.
        """
        pass

    @abstractmethod
    async def update(self, action: Action) -> Action:
        """Update an existing action.

        Args:
            action: The action entity with updated values.

        Returns:
            The updated action.
        """
        pass

    @abstractmethod
    async def delete(self, action_id: UUID, workflow_id: UUID) -> bool:
        """Delete an action.

        Args:
            action_id: The action to delete.
            workflow_id: The workflow the action belongs to.

        Returns:
            True if deleted, False if not found.
        """
        pass

    @abstractmethod
    async def count_by_workflow(self, workflow_id: UUID) -> int:
        """Count actions in a workflow.

        Args:
            workflow_id: The workflow to count actions for.

        Returns:
            Number of actions in the workflow.
        """
        pass

    @abstractmethod
    async def get_max_position(self, workflow_id: UUID) -> int:
        """Get the maximum position value in a workflow.

        Args:
            workflow_id: The workflow to check.

        Returns:
            Maximum position value, or 0 if no actions exist.
        """
        pass

    @abstractmethod
    async def reorder_actions(
        self,
        workflow_id: UUID,
        action_positions: dict[UUID, int],
    ) -> None:
        """Reorder actions in a workflow.

        Args:
            workflow_id: The workflow containing the actions.
            action_positions: Dictionary mapping action IDs to new positions.
        """
        pass

    @abstractmethod
    async def update_action_links(
        self,
        action_id: UUID,
        previous_id: UUID | None = None,
        next_id: UUID | None = None,
    ) -> None:
        """Update action linking (previous/next).

        Args:
            action_id: The action to update links for.
            previous_id: New previous action ID.
            next_id: New next action ID.
        """
        pass


class IActionExecutionRepository(ABC):
    """Abstract interface for action execution repository.

    This interface defines the contract for tracking action executions.
    """

    @abstractmethod
    async def create(self, execution: ActionExecution) -> ActionExecution:
        """Create a new execution record.

        Args:
            execution: The execution entity to persist.

        Returns:
            The persisted execution.
        """
        pass

    @abstractmethod
    async def get_by_id(self, execution_id: UUID) -> ActionExecution | None:
        """Get an execution by ID.

        Args:
            execution_id: The unique execution identifier.

        Returns:
            The execution if found, None otherwise.
        """
        pass

    @abstractmethod
    async def update(self, execution: ActionExecution) -> ActionExecution:
        """Update an execution record.

        Args:
            execution: The execution entity with updated values.

        Returns:
            The updated execution.
        """
        pass

    @abstractmethod
    async def list_by_workflow_execution(
        self,
        workflow_execution_id: UUID,
    ) -> list[ActionExecution]:
        """List all executions for a workflow execution.

        Args:
            workflow_execution_id: The workflow execution ID.

        Returns:
            List of executions ordered by action position.
        """
        pass

    @abstractmethod
    async def get_pending_executions(self, limit: int = 100) -> list[ActionExecution]:
        """Get pending executions ready to process.

        Args:
            limit: Maximum number of executions to return.

        Returns:
            List of pending executions ordered by scheduled time.
        """
        pass

    @abstractmethod
    async def get_scheduled_executions(
        self,
        before: datetime,
    ) -> list[ActionExecution]:
        """Get scheduled executions ready to run.

        Args:
            before: Get executions scheduled before this time.

        Returns:
            List of scheduled executions.
        """
        pass


class ActionRepository(IActionRepository):
    """SQLAlchemy-based implementation of action repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async database session.
        """
        self._session = session

    def _model_to_entity(self, model: ActionModel) -> Action:
        """Convert SQLAlchemy model to domain entity.

        Args:
            model: The database model.

        Returns:
            The domain entity.
        """
        return Action(
            id=model.id,
            workflow_id=model.workflow_id,
            action_type=ActionType(model.action_type),
            action_config=ActionConfig(
                ActionType(model.action_type),
                model.action_config,
            ),
            position=model.position,
            previous_action_id=model.previous_action_id,
            next_action_id=model.next_action_id,
            branch_id=model.branch_id,
            is_enabled=model.is_enabled,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by,
        )

    def _entity_to_model(self, entity: Action) -> ActionModel:
        """Convert domain entity to SQLAlchemy model.

        Args:
            entity: The domain entity.

        Returns:
            The database model.
        """
        return ActionModel(
            id=entity.id,
            workflow_id=entity.workflow_id,
            action_type=entity.action_type.value,
            action_config=entity.action_config.to_dict(),
            position=entity.position,
            previous_action_id=entity.previous_action_id,
            next_action_id=entity.next_action_id,
            branch_id=entity.branch_id,
            is_enabled=entity.is_enabled,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            created_by=entity.created_by,
            updated_by=entity.updated_by,
        )

    async def create(self, action: Action) -> Action:
        """Create a new action."""
        model = self._entity_to_model(action)
        self._session.add(model)
        await self._session.flush()

        # Refresh to get any database-generated values
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def get_by_id(self, action_id: UUID, workflow_id: UUID) -> Action | None:
        """Get an action by ID."""
        stmt = select(ActionModel).where(
            and_(
                ActionModel.id == action_id,
                ActionModel.workflow_id == workflow_id,
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def list_by_workflow(
        self,
        workflow_id: UUID,
        include_disabled: bool = False,
    ) -> list[Action]:
        """List all actions for a workflow."""
        stmt = select(ActionModel).where(ActionModel.workflow_id == workflow_id)

        if not include_disabled:
            stmt = stmt.where(ActionModel.is_enabled == True)

        stmt = stmt.order_by(ActionModel.position)

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(m) for m in models]

    async def update(self, action: Action) -> Action:
        """Update an existing action."""
        stmt = (
            update(ActionModel)
            .where(ActionModel.id == action.id)
            .values(
                action_config=action.action_config.to_dict(),
                is_enabled=action.is_enabled,
                position=action.position,
                previous_action_id=action.previous_action_id,
                next_action_id=action.next_action_id,
                updated_at=datetime.now(UTC),
                updated_by=action.updated_by,
            )
        )
        await self._session.execute(stmt)
        await self._session.flush()

        # Return updated entity
        return await self.get_by_id(action.id, action.workflow_id)  # type: ignore

    async def delete(self, action_id: UUID, workflow_id: UUID) -> bool:
        """Delete an action."""
        stmt = delete(ActionModel).where(
            and_(
                ActionModel.id == action_id,
                ActionModel.workflow_id == workflow_id,
            )
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount > 0

    async def count_by_workflow(self, workflow_id: UUID) -> int:
        """Count actions in a workflow."""
        stmt = select(func.count(ActionModel.id)).where(
            ActionModel.workflow_id == workflow_id
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def get_max_position(self, workflow_id: UUID) -> int:
        """Get the maximum position value in a workflow."""
        stmt = select(func.max(ActionModel.position)).where(
            ActionModel.workflow_id == workflow_id
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def reorder_actions(
        self,
        workflow_id: UUID,
        action_positions: dict[UUID, int],
    ) -> None:
        """Reorder actions in a workflow."""
        for action_id, position in action_positions.items():
            stmt = (
                update(ActionModel)
                .where(
                    and_(
                        ActionModel.id == action_id,
                        ActionModel.workflow_id == workflow_id,
                    )
                )
                .values(position=position, updated_at=datetime.now(UTC))
            )
            await self._session.execute(stmt)
        await self._session.flush()

    async def update_action_links(
        self,
        action_id: UUID,
        previous_id: UUID | None = None,
        next_id: UUID | None = None,
    ) -> None:
        """Update action linking (previous/next)."""
        stmt = (
            update(ActionModel)
            .where(ActionModel.id == action_id)
            .values(
                previous_action_id=previous_id,
                next_action_id=next_id,
                updated_at=datetime.now(UTC),
            )
        )
        await self._session.execute(stmt)
        await self._session.flush()


class ActionExecutionRepository(IActionExecutionRepository):
    """SQLAlchemy-based implementation of action execution repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async database session.
        """
        self._session = session

    def _model_to_entity(self, model: ActionExecutionModel) -> ActionExecution:
        """Convert SQLAlchemy model to domain entity.

        Args:
            model: The database model.

        Returns:
            The domain entity.
        """
        return ActionExecution(
            id=model.id,
            workflow_execution_id=model.workflow_execution_id,
            action_id=model.action_id,
            contact_id=model.contact_id,
            status=ActionExecutionStatus(model.status),
            started_at=model.started_at,
            completed_at=model.completed_at,
            execution_data=model.execution_data,
            result_data=model.result_data,
            error_message=model.error_message,
            retry_count=model.retry_count,
            scheduled_at=model.scheduled_at,
        )

    def _entity_to_model(self, entity: ActionExecution) -> ActionExecutionModel:
        """Convert domain entity to SQLAlchemy model.

        Args:
            entity: The domain entity.

        Returns:
            The database model.
        """
        return ActionExecutionModel(
            id=entity.id,
            workflow_execution_id=entity.workflow_execution_id,
            action_id=entity.action_id,
            contact_id=entity.contact_id,
            status=entity.status.value,
            started_at=entity.started_at,
            completed_at=entity.completed_at,
            execution_data=entity.execution_data,
            result_data=entity.result_data,
            error_message=entity.error_message,
            retry_count=entity.retry_count,
            scheduled_at=entity.scheduled_at,
        )

    async def create(self, execution: ActionExecution) -> ActionExecution:
        """Create a new execution record."""
        model = self._entity_to_model(execution)
        self._session.add(model)
        await self._session.flush()

        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def get_by_id(self, execution_id: UUID) -> ActionExecution | None:
        """Get an execution by ID."""
        stmt = select(ActionExecutionModel).where(
            ActionExecutionModel.id == execution_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def update(self, execution: ActionExecution) -> ActionExecution:
        """Update an execution record."""
        stmt = (
            update(ActionExecutionModel)
            .where(ActionExecutionModel.id == execution.id)
            .values(
                status=execution.status.value,
                started_at=execution.started_at,
                completed_at=execution.completed_at,
                execution_data=execution.execution_data,
                result_data=execution.result_data,
                error_message=execution.error_message,
                retry_count=execution.retry_count,
                scheduled_at=execution.scheduled_at,
            )
        )
        await self._session.execute(stmt)
        await self._session.flush()

        return await self.get_by_id(execution.id)  # type: ignore

    async def list_by_workflow_execution(
        self,
        workflow_execution_id: UUID,
    ) -> list[ActionExecution]:
        """List all executions for a workflow execution."""
        stmt = (
            select(ActionExecutionModel)
            .where(ActionExecutionModel.workflow_execution_id == workflow_execution_id)
            .order_by(ActionExecutionModel.started_at)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(m) for m in models]

    async def get_pending_executions(self, limit: int = 100) -> list[ActionExecution]:
        """Get pending executions ready to process."""
        stmt = (
            select(ActionExecutionModel)
            .where(ActionExecutionModel.status == "pending")
            .order_by(ActionExecutionModel.started_at)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(m) for m in models]

    async def get_scheduled_executions(
        self,
        before: datetime,
    ) -> list[ActionExecution]:
        """Get scheduled executions ready to run."""
        stmt = select(ActionExecutionModel).where(
            and_(
                ActionExecutionModel.status == "scheduled",
                ActionExecutionModel.scheduled_at <= before,
            )
        ).order_by(ActionExecutionModel.scheduled_at)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(m) for m in models]
