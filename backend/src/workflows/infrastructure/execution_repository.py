"""Repository for workflow execution persistence.

This module provides database operations for workflow executions.
"""

from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.workflows.domain.execution_entities import (
    ExecutionLog,
    WorkflowExecution,
)
from src.workflows.infrastructure.execution_models import (
    ExecutionLogModel,
    WorkflowExecutionModel,
)


class ExecutionRepository:
    """Repository for workflow execution data access.

    This repository handles CRUD operations for workflow executions
    and execution logs.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: Database session.
        """
        self.session = session

    async def create(
        self,
        execution: WorkflowExecution,
    ) -> WorkflowExecution:
        """Create a new execution.

        Args:
            execution: Execution to create.

        Returns:
            Created execution.
        """
        model = WorkflowExecutionModel(
            id=execution.id,
            workflow_id=execution.workflow_id,
            workflow_version=execution.workflow_version,
            contact_id=execution.contact_id,
            account_id=execution.account_id,
            status=execution.status,
            current_step_index=execution.current_step_index,
            started_at=execution.started_at,
            completed_at=execution.completed_at,
            error_message=execution.error_message,
            retry_count=execution.retry_count,
            metadata=execution.metadata,
            created_at=execution.created_at,
            updated_at=execution.updated_at,
        )

        self.session.add(model)
        await self.session.flush()

        return execution

    async def get(
        self,
        execution_id: UUID,
    ) -> WorkflowExecution | None:
        """Get execution by ID.

        Args:
            execution_id: Execution ID.

        Returns:
            Execution or None if not found.
        """
        stmt = select(WorkflowExecutionModel).where(
            WorkflowExecutionModel.id == execution_id
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._model_to_entity(model)

    async def update(
        self,
        execution: WorkflowExecution,
    ) -> WorkflowExecution:
        """Update execution.

        Args:
            execution: Execution to update.

        Returns:
            Updated execution.
        """
        stmt = (
            update(WorkflowExecutionModel)
            .where(WorkflowExecutionModel.id == execution.id)
            .values(
                status=execution.status,
                current_step_index=execution.current_step_index,
                started_at=execution.started_at,
                completed_at=execution.completed_at,
                error_message=execution.error_message,
                retry_count=execution.retry_count,
                metadata=execution.metadata,
                updated_at=execution.updated_at,
            )
        )

        await self.session.execute(stmt)
        await self.session.flush()

        return execution

    async def list_by_workflow(
        self,
        workflow_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[WorkflowExecution]:
        """List executions for a workflow.

        Args:
            workflow_id: Workflow ID.
            limit: Maximum number of results.
            offset: Query offset.

        Returns:
            List of executions.
        """
        stmt = (
            select(WorkflowExecutionModel)
            .where(WorkflowExecutionModel.workflow_id == workflow_id)
            .order_by(WorkflowExecutionModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(model) for model in models]

    async def list_by_contact(
        self,
        contact_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[WorkflowExecution]:
        """List executions for a contact.

        Args:
            contact_id: Contact ID.
            limit: Maximum number of results.
            offset: Query offset.

        Returns:
            List of executions.
        """
        stmt = (
            select(WorkflowExecutionModel)
            .where(WorkflowExecutionModel.contact_id == contact_id)
            .order_by(WorkflowExecutionModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(model) for model in models]

    async def list_active_by_account(
        self,
        account_id: UUID,
        limit: int = 100,
    ) -> list[WorkflowExecution]:
        """List active executions for an account.

        Args:
            account_id: Account ID.
            limit: Maximum number of results.

        Returns:
            List of active executions.
        """
        from src.workflows.domain.execution_entities import ExecutionStatus

        stmt = (
            select(WorkflowExecutionModel)
            .where(
                WorkflowExecutionModel.account_id == account_id,
                WorkflowExecutionModel.status.in_(
                    [
                        ExecutionStatus.QUEUED,
                        ExecutionStatus.ACTIVE,
                        ExecutionStatus.WAITING,
                    ]
                ),
            )
            .order_by(WorkflowExecutionModel.created_at.asc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(model) for model in models]

    async def count_active_by_account(
        self,
        account_id: UUID,
    ) -> int:
        """Count active executions for an account.

        Args:
            account_id: Account ID.

        Returns:
            Number of active executions.
        """
        from src.workflows.domain.execution_entities import ExecutionStatus
        from sqlalchemy import func

        stmt = (
            select(func.count())
            .select_from(WorkflowExecutionModel)
            .where(
                WorkflowExecutionModel.account_id == account_id,
                WorkflowExecutionModel.status.in_(
                    [
                        ExecutionStatus.QUEUED,
                        ExecutionStatus.ACTIVE,
                        ExecutionStatus.WAITING,
                    ]
                ),
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def create_log(
        self,
        log: ExecutionLog,
    ) -> ExecutionLog:
        """Create an execution log.

        Args:
            log: Log to create.

        Returns:
            Created log.
        """
        model = ExecutionLogModel(
            id=log.id,
            execution_id=log.execution_id,
            step_index=log.step_index,
            action_type=log.action_type,
            action_config=log.action_config,
            status=log.status,
            started_at=log.started_at,
            completed_at=log.completed_at,
            duration_ms=log.duration_ms,
            error_details=log.error_details,
            response_data=log.response_data,
            created_at=log.created_at,
        )

        self.session.add(model)
        await self.session.flush()

        return log

    async def list_logs_by_execution(
        self,
        execution_id: UUID,
    ) -> list[ExecutionLog]:
        """List logs for an execution.

        Args:
            execution_id: Execution ID.

        Returns:
            List of logs.
        """
        stmt = (
            select(ExecutionLogModel)
            .where(ExecutionLogModel.execution_id == execution_id)
            .order_by(ExecutionLogModel.step_index.asc())
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_log_entity(model) for model in models]

    def _model_to_entity(self, model: WorkflowExecutionModel) -> WorkflowExecution:
        """Convert model to domain entity.

        Args:
            model: Database model.

        Returns:
            Domain entity.
        """
        return WorkflowExecution(
            id=model.id,
            workflow_id=model.workflow_id,
            workflow_version=model.workflow_version,
            contact_id=model.contact_id,
            account_id=model.account_id,
            status=model.status,
            current_step_index=model.current_step_index,
            started_at=model.started_at,
            completed_at=model.completed_at,
            error_message=model.error_message,
            retry_count=model.retry_count,
            metadata=model.metadata,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _model_to_log_entity(self, model: ExecutionLogModel) -> ExecutionLog:
        """Convert model to log entity.

        Args:
            model: Database model.

        Returns:
            Log entity.
        """
        return ExecutionLog(
            id=model.id,
            execution_id=model.execution_id,
            step_index=model.step_index,
            action_type=model.action_type,
            action_config=model.action_config,
            status=model.status,
            started_at=model.started_at,
            completed_at=model.completed_at,
            duration_ms=model.duration_ms,
            error_details=model.error_details,
            response_data=model.response_data,
            created_at=model.created_at,
        )
