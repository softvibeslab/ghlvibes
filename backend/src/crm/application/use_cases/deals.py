"""Deal use cases (SPEC-CRM-002).

Implements business logic for deal CRUD operations,
stage movement, and forecasting.
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.dependencies import AuthenticatedUser
from src.crm.application.dtos import (
    CreateDealRequest,
    DealForecastResponse,
    DealListResponse,
    DealResponse,
    PaginationParams,
    UpdateDealRequest,
)
from src.crm.domain.entities import Deal
from src.crm.domain.exceptions import (
    DealValidationError,
    InvalidStageTransitionError,
)
from src.crm.domain.value_objects import DealStatus, Money
from src.crm.infrastructure.models import DealModel, PipelineStageModel


class CreateDealUseCase:
    """Use case for creating a new deal."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        request: CreateDealRequest,
        user: AuthenticatedUser,
    ) -> DealResponse:
        """Create a new deal.

        Args:
            request: Deal creation data.
            user: Authenticated user.

        Returns:
            Created deal.
        """
        # Verify stage exists
        stage = await self.session.get(PipelineStageModel, request.stage_id)
        if not stage:
            raise DealValidationError("Stage not found")

        # Create domain entity
        deal = Deal.create(
            account_id=user.account_id,
            pipeline_id=stage.pipeline_id,
            stage_id=request.stage_id,
            name=request.name,
            value=request.value,
            contact_id=request.contact_id,
            company_id=request.company_id,
            created_by=user.id,
        )

        if request.expected_close_date:
            deal.expected_close_date = request.expected_close_date
        if request.probability != 50:
            deal.probability = request.probability
        if request.notes:
            deal.notes = request.notes

        # Create database model
        deal_model = DealModel(
            id=deal.id,
            account_id=deal.account_id,
            pipeline_id=deal.pipeline_id,
            stage_id=deal.stage_id,
            name=deal.name,
            value_amount=deal.value.amount,
            value_currency=deal.value.currency,
            contact_id=deal.contact_id,
            company_id=deal.company_id,
            status=deal.status,
            expected_close_date=deal.expected_close_date,
            probability=deal.probability,
            notes=deal.notes,
            created_by=deal.created_by,
        )

        self.session.add(deal_model)
        await self.session.flush()
        await self.session.refresh(deal_model)

        return DealResponse.model_validate(deal_model)


class GetDealUseCase:
    """Use case for retrieving a single deal."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        deal_id: UUID,
        user: AuthenticatedUser,
    ) -> DealResponse:
        """Get deal by ID.

        Args:
            deal_id: Deal ID.
            user: Authenticated user.

        Returns:
            Deal.

        Raises:
            DealValidationError: If deal not found.
        """
        result = await self.session.execute(
            select(DealModel).where(
                DealModel.id == deal_id,
                DealModel.account_id == user.account_id,
            )
        )
        deal = result.scalar_one_or_none()

        if not deal:
            raise DealValidationError("Deal not found")

        return DealResponse.model_validate(deal)


class ListDealsUseCase:
    """Use case for listing deals with filtering."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        user: AuthenticatedUser,
        pagination: PaginationParams,
        pipeline_id: UUID | None = None,
        stage_id: UUID | None = None,
        status: DealStatus | None = None,
        contact_id: UUID | None = None,
        company_id: UUID | None = None,
    ) -> DealListResponse:
        """List deals with filters.

        Args:
            user: Authenticated user.
            pagination: Pagination parameters.
            pipeline_id: Optional filter by pipeline.
            stage_id: Optional filter by stage.
            status: Optional filter by status.
            contact_id: Optional filter by contact.
            company_id: Optional filter by company.

        Returns:
            Paginated deal list.
        """
        query = select(DealModel).where(DealModel.account_id == user.account_id)

        if pipeline_id:
            query = query.where(DealModel.pipeline_id == pipeline_id)
        if stage_id:
            query = query.where(DealModel.stage_id == stage_id)
        if status:
            query = query.where(DealModel.status == status)
        if contact_id:
            query = query.where(DealModel.contact_id == contact_id)
        if company_id:
            query = query.where(DealModel.company_id == company_id)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar()

        # Apply pagination
        query = query.order_by(DealModel.created_at.desc())
        query = query.offset(pagination.offset).limit(pagination.page_size)

        result = await self.session.execute(query)
        deals = result.scalars().all()

        total_pages = (total + pagination.page_size - 1) // pagination.page_size

        return DealListResponse(
            items=[DealResponse.model_validate(d) for d in deals],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
        )


class UpdateDealUseCase:
    """Use case for updating a deal."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        deal_id: UUID,
        request: UpdateDealRequest,
        user: AuthenticatedUser,
    ) -> DealResponse:
        """Update deal.

        Args:
            deal_id: Deal ID.
            request: Update data.
            user: Authenticated user.

        Returns:
            Updated deal.

        Raises:
            DealValidationError: If deal not found.
        """
        result = await self.session.execute(
            select(DealModel).where(
                DealModel.id == deal_id,
                DealModel.account_id == user.account_id,
            )
        )
        deal_model = result.scalar_one_or_none()

        if not deal_model:
            raise DealValidationError("Deal not found")

        # Update fields
        if request.name is not None:
            deal_model.name = request.name
        if request.value is not None:
            deal_model.value_amount = int(request.value * 100)
        if request.stage_id is not None:
            deal_model.stage_id = request.stage_id
        if request.expected_close_date is not None:
            deal_model.expected_close_date = request.expected_close_date
        if request.probability is not None:
            deal_model.probability = request.probability
        if request.notes is not None:
            deal_model.notes = request.notes

        await self.session.flush()
        await self.session.refresh(deal_model)

        return DealResponse.model_validate(deal_model)


class DeleteDealUseCase:
    """Use case for deleting a deal."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        deal_id: UUID,
        user: AuthenticatedUser,
    ) -> None:
        """Delete deal.

        Args:
            deal_id: Deal ID.
            user: Authenticated user.

        Raises:
            DealValidationError: If deal not found.
        """
        result = await self.session.execute(
            select(DealModel).where(
                DealModel.id == deal_id,
                DealModel.account_id == user.account_id,
            )
        )
        deal = result.scalar_one_or_none()

        if not deal:
            raise DealValidationError("Deal not found")

        await self.session.delete(deal)


class MoveDealStageUseCase:
    """Use case for moving a deal to a different stage."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        deal_id: UUID,
        new_stage_id: UUID,
        probability: int | None,
        user: AuthenticatedUser,
    ) -> DealResponse:
        """Move deal to new stage.

        Args:
            deal_id: Deal ID.
            new_stage_id: New stage ID.
            probability: Optional probability override.
            user: Authenticated user.

        Returns:
            Updated deal.

        Raises:
            DealValidationError: If deal not found.
            InvalidStageTransitionError: If transition invalid.
        """
        result = await self.session.execute(
            select(DealModel).where(
                DealModel.id == deal_id,
                DealModel.account_id == user.account_id,
            )
        )
        deal_model = result.scalar_one_or_none()

        if not deal_model:
            raise DealValidationError("Deal not found")

        # Check if deal is closed
        if deal_model.status in [DealStatus.WON, DealStatus.LOST, DealStatus.ABANDONED]:
            raise InvalidStageTransitionError(
                f"Cannot move deal with status {deal_model.status.value}"
            )

        deal_model.stage_id = new_stage_id
        if probability is not None:
            deal_model.probability = probability

        await self.session.flush()
        await self.session.refresh(deal_model)

        return DealResponse.model_validate(deal_model)


class WinDealUseCase:
    """Use case for marking a deal as won."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        deal_id: UUID,
        close_date: datetime | None,
        user: AuthenticatedUser,
    ) -> DealResponse:
        """Mark deal as won.

        Args:
            deal_id: Deal ID.
            close_date: Optional close date.
            user: Authenticated user.

        Returns:
            Updated deal.

        Raises:
            DealValidationError: If deal not found.
        """
        result = await self.session.execute(
            select(DealModel).where(
                DealModel.id == deal_id,
                DealModel.account_id == user.account_id,
            )
        )
        deal_model = result.scalar_one_or_none()

        if not deal_model:
            raise DealValidationError("Deal not found")

        deal_model.status = DealStatus.WON
        deal_model.actual_close_date = close_date or datetime.now()
        deal_model.probability = 100

        await self.session.flush()
        await self.session.refresh(deal_model)

        return DealResponse.model_validate(deal_model)


class LoseDealUseCase:
    """Use case for marking a deal as lost."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        deal_id: UUID,
        close_date: datetime | None,
        user: AuthenticatedUser,
    ) -> DealResponse:
        """Mark deal as lost.

        Args:
            deal_id: Deal ID.
            close_date: Optional close date.
            user: Authenticated user.

        Returns:
            Updated deal.

        Raises:
            DealValidationError: If deal not found.
        """
        result = await self.session.execute(
            select(DealModel).where(
                DealModel.id == deal_id,
                DealModel.account_id == user.account_id,
            )
        )
        deal_model = result.scalar_one_or_none()

        if not deal_model:
            raise DealValidationError("Deal not found")

        deal_model.status = DealStatus.LOST
        deal_model.actual_close_date = close_date or datetime.now()
        deal_model.probability = 0

        await self.session.flush()
        await self.session.refresh(deal_model)

        return DealResponse.model_validate(deal_model)


class GetDealForecastUseCase:
    """Use case for generating deal forecast."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        user: AuthenticatedUser,
        pipeline_id: UUID | None = None,
    ) -> DealForecastResponse:
        """Generate deal forecast.

        Args:
            user: Authenticated user.
            pipeline_id: Optional filter by pipeline.

        Returns:
            Deal forecast summary.
        """
        query = select(DealModel).where(DealModel.account_id == user.account_id)

        if pipeline_id:
            query = query.where(DealModel.pipeline_id == pipeline_id)

        result = await self.session.execute(query)
        deals = result.scalars().all()

        total_value = sum(d.value_amount for d in deals) / 100.0
        weighted_value = sum(
            d.value_amount * d.probability / 100 for d in deals
        ) / 100.0
        won_value = sum(
            d.value_amount for d in deals if d.status == DealStatus.WON
        ) / 100.0
        lost_value = sum(
            d.value_amount for d in deals if d.status == DealStatus.LOST
        ) / 100.0

        open_deals = sum(1 for d in deals if d.status == DealStatus.OPEN)
        won_deals = sum(1 for d in deals if d.status == DealStatus.WON)
        lost_deals = sum(1 for d in deals if d.status == DealStatus.LOST)

        return DealForecastResponse(
            total_value=total_value,
            weighted_value=weighted_value,
            won_value=won_value,
            lost_value=lost_value,
            open_deals=open_deals,
            won_deals=won_deals,
            lost_deals=lost_deals,
        )
