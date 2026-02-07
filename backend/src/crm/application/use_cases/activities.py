"""Activity use cases (SPEC-CRM-004).

Implements business logic for activity CRUD operations,
status management, and completion tracking.
"""

from uuid import UUID

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import AuthenticatedUser
from src.crm.application.dtos import (
    ActivityListResponse,
    ActivityResponse,
    CreateActivityRequest,
    PaginationParams,
    UpdateActivityRequest,
)
from src.crm.domain.entities import Activity
from src.crm.domain.exceptions import ActivityValidationError
from src.crm.domain.value_objects import ActivityStatus, ActivityType
from src.crm.infrastructure.models import ActivityModel


class CreateActivityUseCase:
    """Use case for creating a new activity."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        request: CreateActivityRequest,
        user: AuthenticatedUser,
    ) -> ActivityResponse:
        """Create a new activity.

        Args:
            request: Activity creation data.
            user: Authenticated user.

        Returns:
            Created activity.
        """
        activity = Activity.create(
            account_id=user.account_id,
            activity_type=request.activity_type,
            title=request.title,
            description=request.description,
            due_date=request.due_date,
            contact_id=request.contact_id,
            company_id=request.company_id,
            deal_id=request.deal_id,
            created_by=user.id,
        )

        activity_model = ActivityModel(
            id=activity.id,
            account_id=activity.account_id,
            activity_type=activity.activity_type,
            title=activity.title,
            description=activity.description,
            status=activity.status,
            due_date=activity.due_date,
            contact_id=activity.contact_id,
            company_id=activity.company_id,
            deal_id=activity.deal_id,
            created_by=activity.created_by,
        )

        self.session.add(activity_model)
        await self.session.flush()
        await self.session.refresh(activity_model)

        return ActivityResponse.model_validate(activity_model)


class GetActivityUseCase:
    """Use case for retrieving a single activity."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        activity_id: UUID,
        user: AuthenticatedUser,
    ) -> ActivityResponse:
        """Get activity by ID.

        Args:
            activity_id: Activity ID.
            user: Authenticated user.

        Returns:
            Activity.

        Raises:
            ActivityValidationError: If activity not found.
        """
        result = await self.session.execute(
            select(ActivityModel).where(
                ActivityModel.id == activity_id,
                ActivityModel.account_id == user.account_id,
            )
        )
        activity = result.scalar_one_or_none()

        if not activity:
            raise ActivityValidationError("Activity not found")

        return ActivityResponse.model_validate(activity)


class ListActivitiesUseCase:
    """Use case for listing activities with filtering."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        user: AuthenticatedUser,
        pagination: PaginationParams,
        activity_type: ActivityType | None = None,
        status: ActivityStatus | None = None,
        contact_id: UUID | None = None,
        company_id: UUID | None = None,
        deal_id: UUID | None = None,
    ) -> ActivityListResponse:
        """List activities with filters.

        Args:
            user: Authenticated user.
            pagination: Pagination parameters.
            activity_type: Optional filter by type.
            status: Optional filter by status.
            contact_id: Optional filter by contact.
            company_id: Optional filter by company.
            deal_id: Optional filter by deal.

        Returns:
            Paginated activity list.
        """
        query = select(ActivityModel).where(
            ActivityModel.account_id == user.account_id
        )

        if activity_type:
            query = query.where(ActivityModel.activity_type == activity_type)
        if status:
            query = query.where(ActivityModel.status == status)
        if contact_id:
            query = query.where(ActivityModel.contact_id == contact_id)
        if company_id:
            query = query.where(ActivityModel.company_id == company_id)
        if deal_id:
            query = query.where(ActivityModel.deal_id == deal_id)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar()

        # Apply pagination
        query = query.order_by(ActivityModel.due_date.asc())
        query = query.offset(pagination.offset).limit(pagination.page_size)

        result = await self.session.execute(query)
        activities = result.scalars().all()

        total_pages = (total + pagination.page_size - 1) // pagination.page_size

        return ActivityListResponse(
            items=[ActivityResponse.model_validate(a) for a in activities],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
        )


class UpdateActivityUseCase:
    """Use case for updating an activity."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        activity_id: UUID,
        request: UpdateActivityRequest,
        user: AuthenticatedUser,
    ) -> ActivityResponse:
        """Update activity.

        Args:
            activity_id: Activity ID.
            request: Update data.
            user: Authenticated user.

        Returns:
            Updated activity.

        Raises:
            ActivityValidationError: If activity not found.
        """
        result = await self.session.execute(
            select(ActivityModel).where(
                ActivityModel.id == activity_id,
                ActivityModel.account_id == user.account_id,
            )
        )
        activity_model = result.scalar_one_or_none()

        if not activity_model:
            raise ActivityValidationError("Activity not found")

        # Update fields
        if request.title is not None:
            activity_model.title = request.title
        if request.description is not None:
            activity_model.description = request.description
        if request.due_date is not None:
            activity_model.due_date = request.due_date
        if request.status is not None:
            activity_model.status = request.status

        await self.session.flush()
        await self.session.refresh(activity_model)

        return ActivityResponse.model_validate(activity_model)


class DeleteActivityUseCase:
    """Use case for deleting an activity."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        activity_id: UUID,
        user: AuthenticatedUser,
    ) -> None:
        """Delete activity.

        Args:
            activity_id: Activity ID.
            user: Authenticated user.

        Raises:
            ActivityValidationError: If activity not found.
        """
        result = await self.session.execute(
            select(ActivityModel).where(
                ActivityModel.id == activity_id,
                ActivityModel.account_id == user.account_id,
            )
        )
        activity = result.scalar_one_or_none()

        if not activity:
            raise ActivityValidationError("Activity not found")

        await self.session.delete(activity)


class CompleteActivityUseCase:
    """Use case for marking an activity as completed."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        activity_id: UUID,
        user: AuthenticatedUser,
    ) -> ActivityResponse:
        """Mark activity as completed.

        Args:
            activity_id: Activity ID.
            user: Authenticated user.

        Returns:
            Updated activity.

        Raises:
            ActivityValidationError: If activity not found or already completed.
        """
        result = await self.session.execute(
            select(ActivityModel).where(
                ActivityModel.id == activity_id,
                ActivityModel.account_id == user.account_id,
            )
        )
        activity_model = result.scalar_one_or_none()

        if not activity_model:
            raise ActivityValidationError("Activity not found")

        if activity_model.status == ActivityStatus.COMPLETED:
            raise ActivityValidationError("Activity is already completed")

        activity_model.status = ActivityStatus.COMPLETED
        activity_model.completed_at = func.now()

        await self.session.flush()
        await self.session.refresh(activity_model)

        return ActivityResponse.model_validate(activity_model)


class StartActivityUseCase:
    """Use case for starting an activity."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        activity_id: UUID,
        user: AuthenticatedUser,
    ) -> ActivityResponse:
        """Mark activity as in progress.

        Args:
            activity_id: Activity ID.
            user: Authenticated user.

        Returns:
            Updated activity.

        Raises:
            ActivityValidationError: If activity not found or not in pending status.
        """
        result = await self.session.execute(
            select(ActivityModel).where(
                ActivityModel.id == activity_id,
                ActivityModel.account_id == user.account_id,
            )
        )
        activity_model = result.scalar_one_or_none()

        if not activity_model:
            raise ActivityValidationError("Activity not found")

        if activity_model.status != ActivityStatus.PENDING:
            raise ActivityValidationError("Can only start pending activities")

        activity_model.status = ActivityStatus.IN_PROGRESS

        await self.session.flush()
        await self.session.refresh(activity_model)

        return ActivityResponse.model_validate(activity_model)


class CancelActivityUseCase:
    """Use case for cancelling an activity."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        activity_id: UUID,
        user: AuthenticatedUser,
    ) -> ActivityResponse:
        """Cancel activity.

        Args:
            activity_id: Activity ID.
            user: Authenticated user.

        Returns:
            Updated activity.

        Raises:
            ActivityValidationError: If activity not found or already completed.
        """
        result = await self.session.execute(
            select(ActivityModel).where(
                ActivityModel.id == activity_id,
                ActivityModel.account_id == user.account_id,
            )
        )
        activity_model = result.scalar_one_or_none()

        if not activity_model:
            raise ActivityValidationError("Activity not found")

        if activity_model.status == ActivityStatus.COMPLETED:
            raise ActivityValidationError("Cannot cancel completed activities")

        activity_model.status = ActivityStatus.CANCELLED

        await self.session.flush()
        await self.session.refresh(activity_model)

        return ActivityResponse.model_validate(activity_model)
