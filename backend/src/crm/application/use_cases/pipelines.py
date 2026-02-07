"""Pipeline use cases (SPEC-CRM-002).

Implements business logic for pipeline CRUD operations
and stage management.
"""

from uuid import UUID

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.dependencies import AuthenticatedUser
from src.crm.application.dtos import (
    CreatePipelineRequest,
    PaginationParams,
    PipelineResponse,
)
from src.crm.domain.entities import Pipeline, PipelineStage
from src.crm.domain.exceptions import PipelineValidationError
from src.crm.infrastructure.models import PipelineModel, PipelineStageModel


class CreatePipelineUseCase:
    """Use case for creating a new pipeline."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        request: CreatePipelineRequest,
        user: AuthenticatedUser,
    ) -> PipelineResponse:
        """Create a new pipeline.

        Args:
            request: Pipeline creation data.
            user: Authenticated user.

        Returns:
            Created pipeline.
        """
        # Create domain entity
        pipeline = Pipeline.create(
            account_id=user.account_id,
            name=request.name,
        )

        # Create database model
        pipeline_model = PipelineModel(
            id=pipeline.id,
            account_id=pipeline.account_id,
            name=pipeline.name,
            is_active=True,
        )

        self.session.add(pipeline_model)
        await self.session.flush()

        # Create stages
        for stage_data in request.stages:
            stage = PipelineStage(
                id=uuid4(),
                pipeline_id=pipeline.id,
                name=stage_data["name"],
                order=stage_data.get("order", 0),
                probability=stage_data.get("probability", 50),
                display_color=stage_data.get("display_color"),
            )

            stage_model = PipelineStageModel(
                id=stage.id,
                pipeline_id=stage.pipeline_id,
                name=stage.name,
                order=stage.order,
                probability=stage.probability,
                display_color=stage.display_color,
            )
            self.session.add(stage_model)

        await self.session.flush()
        await self.session.refresh(pipeline_model)

        return PipelineResponse.model_validate(pipeline_model)


class GetPipelineUseCase:
    """Use case for retrieving a single pipeline."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        pipeline_id: UUID,
        user: AuthenticatedUser,
    ) -> PipelineResponse:
        """Get pipeline by ID.

        Args:
            pipeline_id: Pipeline ID.
            user: Authenticated user.

        Returns:
            Pipeline.

        Raises:
            PipelineValidationError: If pipeline not found.
        """
        result = await self.session.execute(
            select(PipelineModel)
            .options(selectinload(PipelineModel.stages))
            .where(
                PipelineModel.id == pipeline_id,
                PipelineModel.account_id == user.account_id,
            )
        )
        pipeline = result.scalar_one_or_none()

        if not pipeline:
            raise PipelineValidationError("Pipeline not found")

        return PipelineResponse.model_validate(pipeline)


class ListPipelinesUseCase:
    """Use case for listing pipelines."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        user: AuthenticatedUser,
        pagination: PaginationParams,
    ) -> list[PipelineResponse]:
        """List all pipelines for account.

        Args:
            user: Authenticated user.
            pagination: Pagination parameters.

        Returns:
            List of pipelines.
        """
        query = (
            select(PipelineModel)
            .options(selectinload(PipelineModel.stages))
            .where(PipelineModel.account_id == user.account_id)
            .order_by(PipelineModel.created_at.desc())
        )

        query = query.offset(pagination.offset).limit(pagination.page_size)

        result = await self.session.execute(query)
        pipelines = result.scalars().all()

        return [PipelineResponse.model_validate(p) for p in pipelines]


class UpdatePipelineUseCase:
    """Use case for updating a pipeline."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        pipeline_id: UUID,
        name: str,
        user: AuthenticatedUser,
    ) -> PipelineResponse:
        """Update pipeline name.

        Args:
            pipeline_id: Pipeline ID.
            name: New name.
            user: Authenticated user.

        Returns:
            Updated pipeline.

        Raises:
            PipelineValidationError: If pipeline not found.
        """
        result = await self.session.execute(
            select(PipelineModel).where(
                PipelineModel.id == pipeline_id,
                PipelineModel.account_id == user.account_id,
            )
        )
        pipeline = result.scalar_one_or_none()

        if not pipeline:
            raise PipelineValidationError("Pipeline not found")

        pipeline.name = name
        await self.session.flush()
        await self.session.refresh(pipeline)

        return PipelineResponse.model_validate(pipeline)


class DeletePipelineUseCase:
    """Use case for deleting a pipeline."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        pipeline_id: UUID,
        user: AuthenticatedUser,
    ) -> None:
        """Delete pipeline.

        Args:
            pipeline_id: Pipeline ID.
            user: Authenticated user.

        Raises:
            PipelineValidationError: If pipeline not found.
        """
        result = await self.session.execute(
            select(PipelineModel).where(
                PipelineModel.id == pipeline_id,
                PipelineModel.account_id == user.account_id,
            )
        )
        pipeline = result.scalar_one_or_none()

        if not pipeline:
            raise PipelineValidationError("Pipeline not found")

        await self.session.delete(pipeline)
