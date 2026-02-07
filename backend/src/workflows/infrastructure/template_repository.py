"""Repository implementations for workflow templates."""

from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.workflows.domain.template_entities import TemplateUsage, WorkflowTemplate
from src.workflows.infrastructure.template_models import TemplateModel, TemplateUsageModel


class ITemplateRepository(ABC):
    """Abstract interface for workflow template repository."""

    @abstractmethod
    async def create(self, template: WorkflowTemplate) -> WorkflowTemplate:
        """Create a new workflow template."""
        pass

    @abstractmethod
    async def get_by_id(self, template_id: Any, account_id: Any) -> WorkflowTemplate | None:
        """Get a template by ID."""
        pass

    @abstractmethod
    async def list(
        self,
        account_id: Any,
        category: str | None = None,
        is_system_template: bool | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[WorkflowTemplate], int]:
        """List templates with filters."""
        pass

    @abstractmethod
    async def update(self, template: WorkflowTemplate) -> WorkflowTemplate:
        """Update an existing template."""
        pass

    @abstractmethod
    async def delete(self, template_id: Any, account_id: Any) -> bool:
        """Delete a template."""
        pass

    @abstractmethod
    async def record_usage(self, usage: TemplateUsage) -> TemplateUsage:
        """Record template usage when cloning."""
        pass


class PostgresTemplateRepository(ITemplateRepository):
    """PostgreSQL implementation of template repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: Async database session.
        """
        self._session = session

    async def create(self, template: WorkflowTemplate) -> WorkflowTemplate:
        """Create a new workflow template.

        Args:
            template: WorkflowTemplate entity.

        Returns:
            Created template with generated ID.
        """
        model = TemplateModel.from_domain(template)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model.to_domain()

    async def get_by_id(
        self, template_id: Any, account_id: Any
    ) -> WorkflowTemplate | None:
        """Get a template by ID.

        Args:
            template_id: Template ID.
            account_id: Account ID (None for system templates).

        Returns:
            Template if found, None otherwise.
        """
        # Build query - system templates don't have account_id
        if account_id is None:
            # System template lookup
            result = await self._session.execute(
                select(TemplateModel).where(
                    and_(
                        TemplateModel.id == template_id,
                        TemplateModel.is_system_template == True,
                    )
                )
            )
        else:
            # User template lookup
            result = await self._session.execute(
                select(TemplateModel).where(
                    or_(
                        and_(
                            TemplateModel.id == template_id,
                            TemplateModel.account_id == account_id,
                        ),
                        and_(
                            TemplateModel.id == template_id,
                            TemplateModel.is_system_template == True,
                        ),
                    )
                )
            )

        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def list(
        self,
        account_id: Any,
        category: str | None = None,
        is_system_template: bool | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[WorkflowTemplate], int]:
        """List templates with filters.

        Args:
            account_id: Account ID.
            category: Filter by category.
            is_system_template: Filter by system template flag.
            search: Search in name and description.
            offset: Pagination offset.
            limit: Maximum results.

        Returns:
            Tuple of (templates list, total count).
        """
        # Build base query
        query = select(TemplateModel)

        # Build conditions
        conditions = []

        # Include system templates and user's templates
        conditions.append(
            or_(
                TemplateModel.is_system_template == True,
                TemplateModel.account_id == account_id,
            )
        )

        if category:
            conditions.append(TemplateModel.category == category)

        if is_system_template is not None:
            conditions.append(TemplateModel.is_system_template == is_system_template)

        if search:
            search_pattern = f"%{search}%"
            conditions.append(
                or_(
                    TemplateModel.name.ilike(search_pattern),
                    TemplateModel.description.ilike(search_pattern),
                    TemplateModel.tags.any(search),  # Search in tags array
                )
            )

        # Apply conditions
        if conditions:
            query = query.where(and_(*conditions))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self._session.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        query = query.order_by(TemplateModel.usage_count.desc()).offset(offset).limit(limit)
        result = await self._session.execute(query)
        models = result.scalars().all()

        templates = [model.to_domain() for model in models]

        return templates, total

    async def update(self, template: WorkflowTemplate) -> WorkflowTemplate:
        """Update an existing template.

        Args:
            template: Template with updated values.

        Returns:
            Updated template.
        """
        result = await self._session.execute(
            select(TemplateModel).where(
                and_(
                    TemplateModel.id == template.id,
                    or_(
                        TemplateModel.account_id == template.account_id,
                        TemplateModel.is_system_template == True,
                    ),
                )
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None

        # Update fields
        model.name = template.name
        model.description = template.description
        model.category = template.category.value
        model.required_integrations = template.metadata.required_integrations
        model.tags = template.metadata.tags
        model.estimated_completion_rate = template.metadata.estimated_completion_rate
        model.is_shared = template.metadata.is_shared
        model.workflow_config = template.workflow_config
        model.version = template.version
        model.updated_at = template.updated_at

        await self._session.flush()
        await self._session.refresh(model)
        return model.to_domain()

    async def delete(self, template_id: Any, account_id: Any) -> bool:
        """Delete a template.

        Args:
            template_id: Template ID.
            account_id: Account ID.

        Returns:
            True if deleted, False if not found.
        """
        result = await self._session.execute(
            select(TemplateModel).where(
                and_(
                    TemplateModel.id == template_id,
                    TemplateModel.account_id == account_id,
                    TemplateModel.is_system_template == False,  # Cannot delete system templates
                )
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            return False

        await self._session.delete(model)
        await self._session.flush()
        return True

    async def record_usage(self, usage: TemplateUsage) -> TemplateUsage:
        """Record template usage when cloning.

        Args:
            usage: TemplateUsage entity.

        Returns:
            Created usage record.
        """
        model = TemplateUsageModel.from_domain(usage)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model.to_domain()
