"""Repository implementations for condition configurations."""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.workflows.domain.condition_entities import Condition
from src.workflows.infrastructure.condition_models import (
    BranchModel,
    ConditionLogModel,
    ConditionModel,
)


class IConditionRepository(ABC):
    """Abstract interface for condition configuration repository."""

    @abstractmethod
    async def create(self, condition: Condition) -> Condition:
        """Create a new condition configuration."""
        pass

    @abstractmethod
    async def get_by_id(self, condition_id: UUID, account_id: UUID) -> Condition | None:
        """Get a condition configuration by ID."""
        pass

    @abstractmethod
    async def get_by_node_id(self, node_id: UUID, account_id: UUID) -> Condition | None:
        """Get a condition by canvas node ID."""
        pass

    @abstractmethod
    async def list_by_workflow(
        self,
        workflow_id: UUID,
        account_id: UUID,
        offset: int = 0,
        limit: int = 50,
    ) -> list[Condition]:
        """List condition configurations for a workflow."""
        pass

    @abstractmethod
    async def update(self, condition: Condition) -> Condition:
        """Update an existing condition configuration."""
        pass

    @abstractmethod
    async def delete(self, condition_id: UUID, account_id: UUID, deleted_by: UUID) -> bool:
        """Delete a condition configuration."""
        pass

    @abstractmethod
    async def count_by_workflow(self, workflow_id: UUID, account_id: UUID) -> int:
        """Count condition configurations for a workflow."""
        pass


class IConditionLogRepository(ABC):
    """Abstract interface for condition evaluation log repository."""

    @abstractmethod
    async def create_log(
        self,
        execution_id: UUID,
        condition_id: UUID,
        contact_id: UUID,
        account_id: UUID,
        evaluation_inputs: dict[str, Any],
        evaluation_result: str,
        duration_ms: int,
    ) -> None:
        """Create a condition evaluation log entry."""
        pass

    @abstractmethod
    async def get_by_contact(
        self,
        contact_id: UUID,
        account_id: UUID,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get evaluation logs for a contact."""
        pass


class PostgresConditionRepository(IConditionRepository):
    """PostgreSQL implementation of condition repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: Async database session.
        """
        self._session = session

    async def create(self, condition: Condition) -> Condition:
        """Create a new condition configuration.

        Args:
            condition: Condition entity.

        Returns:
            Created condition with generated ID.
        """
        # Import account_id from workflow context (placeholder for now)
        # In production, this would come from the workflow entity
        account_id = UUID("00000000-0000-0000-0000-000000000000")

        model = ConditionModel.from_domain(condition)
        model.account_id = account_id

        self._session.add(model)

        # Create branch models
        for branch in condition.branches:
            branch_model = BranchModel(
                id=branch.id,
                condition_id=model.id,
                branch_name=branch.branch_name,
                branch_order=branch.branch_order,
                is_default=branch.is_default,
                percentage=branch.percentage,
                next_node_id=branch.next_node_id,
                criteria=branch.criteria.to_dict() if branch.criteria else None,
            )
            self._session.add(branch_model)

        await self._session.flush()
        await self._session.refresh(model)

        # Load branches and convert to domain
        result = await self._session.execute(
            select(ConditionModel)
            .where(ConditionModel.id == model.id)
            .options(selectinload(ConditionModel.branches))
        )
        model_with_branches = result.scalar_one()
        return model_with_branches.to_domain()

    async def get_by_id(self, condition_id: UUID, account_id: UUID) -> Condition | None:
        """Get a condition configuration by ID.

        Args:
            condition_id: Condition configuration ID.
            account_id: Account/tenant ID.

        Returns:
            Condition configuration if found, None otherwise.
        """
        result = await self._session.execute(
            select(ConditionModel)
            .where(
                and_(ConditionModel.id == condition_id, ConditionModel.account_id == account_id)
            )
            .options(selectinload(ConditionModel.branches))
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_by_node_id(self, node_id: UUID, account_id: UUID) -> Condition | None:
        """Get a condition by canvas node ID.

        Args:
            node_id: Canvas node identifier.
            account_id: Account/tenant ID.

        Returns:
            Condition configuration if found, None otherwise.
        """
        result = await self._session.execute(
            select(ConditionModel)
            .where(
                and_(ConditionModel.node_id == node_id, ConditionModel.account_id == account_id)
            )
            .options(selectinload(ConditionModel.branches))
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def list_by_workflow(
        self,
        workflow_id: UUID,
        account_id: UUID,
        offset: int = 0,
        limit: int = 50,
    ) -> list[Condition]:
        """List condition configurations for a workflow.

        Args:
            workflow_id: Workflow ID.
            account_id: Account/tenant ID.
            offset: Pagination offset.
            limit: Maximum results.

        Returns:
            List of condition configurations.
        """
        result = await self._session.execute(
            select(ConditionModel)
            .where(
                and_(
                    ConditionModel.workflow_id == workflow_id,
                    ConditionModel.account_id == account_id,
                )
            )
            .options(selectinload(ConditionModel.branches))
            .order_by(ConditionModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        models = result.scalars().all()
        return [model.to_domain() for model in models]

    async def update(self, condition: Condition) -> Condition:
        """Update an existing condition configuration.

        Args:
            condition: Condition configuration with updated values.

        Returns:
            Updated condition configuration.
        """
        result = await self._session.execute(
            select(ConditionModel).where(
                and_(ConditionModel.id == condition.id, ConditionModel.account_id == UUID("00000000-0000-0000-0000-000000000000"))
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None

        # Update fields
        model.configuration = condition.configuration.to_dict()
        model.position_x = condition.position_x
        model.position_y = condition.position_y
        model.is_active = condition.is_active
        model.updated_at = condition.updated_at
        model.updated_by = condition.updated_by

        # Update branches (delete and recreate for simplicity)
        await self._session.execute(
            select(BranchModel).where(BranchModel.condition_id == condition.id)
        )
        # Delete existing branches
        for branch_model in await self._session.scalars(
            select(BranchModel).where(BranchModel.condition_id == condition.id)
        ):
            await self._session.delete(branch_model)

        # Create new branch models
        for branch in condition.branches:
            branch_model = BranchModel(
                id=branch.id,
                condition_id=model.id,
                branch_name=branch.branch_name,
                branch_order=branch.branch_order,
                is_default=branch.is_default,
                percentage=branch.percentage,
                next_node_id=branch.next_node_id,
                criteria=branch.criteria.to_dict() if branch.criteria else None,
            )
            self._session.add(branch_model)

        await self._session.flush()
        await self._session.refresh(model)

        # Load branches and convert to domain
        result = await self._session.execute(
            select(ConditionModel)
            .where(ConditionModel.id == model.id)
            .options(selectinload(ConditionModel.branches))
        )
        model_with_branches = result.scalar_one()
        return model_with_branches.to_domain()

    async def delete(self, condition_id: UUID, account_id: UUID, deleted_by: UUID) -> bool:
        """Delete a condition configuration.

        Args:
            condition_id: Condition configuration ID.
            account_id: Account/tenant ID.
            deleted_by: User performing deletion.

        Returns:
            True if deleted, False if not found.
        """
        result = await self._session.execute(
            select(ConditionModel).where(
                and_(
                    ConditionModel.id == condition_id,
                    ConditionModel.account_id == account_id,
                )
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            return False

        # Delete associated branches (cascade should handle this, but being explicit)
        await self._session.execute(
            select(BranchModel).where(BranchModel.condition_id == condition_id)
        )
        for branch_model in await self._session.scalars(
            select(BranchModel).where(BranchModel.condition_id == condition_id)
        ):
            await self._session.delete(branch_model)

        await self._session.delete(model)
        await self._session.flush()
        return True

    async def count_by_workflow(self, workflow_id: UUID, account_id: UUID) -> int:
        """Count condition configurations for a workflow.

        Args:
            workflow_id: Workflow ID.
            account_id: Account/tenant ID.

        Returns:
            Count of condition configurations.
        """
        result = await self._session.execute(
            select(func.count())
            .select_from(ConditionModel)
            .where(
                and_(
                    ConditionModel.workflow_id == workflow_id,
                    ConditionModel.account_id == account_id,
                )
            )
        )
        return result.scalar() or 0


class PostgresConditionLogRepository(IConditionLogRepository):
    """PostgreSQL implementation of condition log repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: Async database session.
        """
        self._session = session

    async def create_log(
        self,
        execution_id: UUID,
        condition_id: UUID,
        contact_id: UUID,
        account_id: UUID,
        evaluation_inputs: dict[str, Any],
        evaluation_result: str,
        duration_ms: int,
    ) -> None:
        """Create a condition evaluation log entry.

        Args:
            execution_id: Workflow execution ID.
            condition_id: Condition configuration ID.
            contact_id: Contact being evaluated.
            account_id: Account/tenant ID.
            evaluation_inputs: Input values snapshot.
            evaluation_result: Result/branch taken.
            duration_ms: Evaluation duration.
        """
        log = ConditionLogModel(
            execution_id=execution_id,
            condition_id=condition_id,
            contact_id=contact_id,
            account_id=account_id,
            evaluation_inputs=evaluation_inputs,
            evaluation_result=evaluation_result,
            duration_ms=duration_ms,
        )
        self._session.add(log)
        await self._session.flush()

    async def get_by_contact(
        self,
        contact_id: UUID,
        account_id: UUID,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get evaluation logs for a contact.

        Args:
            contact_id: Contact ID.
            account_id: Account/tenant ID.
            offset: Pagination offset.
            limit: Maximum results.

        Returns:
            List of evaluation log entries.
        """
        result = await self._session.execute(
            select(ConditionLogModel)
            .where(
                and_(
                    ConditionLogModel.contact_id == contact_id,
                    ConditionLogModel.account_id == account_id,
                )
            )
            .order_by(ConditionLogModel.evaluated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        models = result.scalars().all()

        return [
            {
                "id": str(m.id),
                "execution_id": str(m.execution_id),
                "condition_id": str(m.condition_id),
                "evaluation_result": m.evaluation_result,
                "evaluated_at": m.evaluated_at.isoformat(),
                "duration_ms": m.duration_ms,
            }
            for m in models
        ]
