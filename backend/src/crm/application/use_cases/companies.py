"""Company use cases (SPEC-CRM-003).

Implements business logic for company CRUD operations,
hierarchy management, and tag assignment.
"""

from uuid import UUID

from sqlalchemy import func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.dependencies import AuthenticatedUser
from src.crm.application.dtos import (
    CompanyListResponse,
    CompanyResponse,
    CreateCompanyRequest,
    PaginationParams,
    UpdateCompanyRequest,
)
from src.crm.domain.entities import Company
from src.crm.domain.exceptions import CompanyValidationError
from src.crm.infrastructure.models import CompanyModel, CompanyTag, TagModel


class CreateCompanyUseCase:
    """Use case for creating a new company."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        request: CreateCompanyRequest,
        user: AuthenticatedUser,
    ) -> CompanyResponse:
        """Create a new company.

        Args:
            request: Company creation data.
            user: Authenticated user.

        Returns:
            Created company.

        Raises:
            CompanyValidationError: If validation fails.
        """
        # Check for duplicate domain
        if request.domain:
            existing = await self.session.execute(
                select(CompanyModel).where(
                    CompanyModel.domain == request.domain.lower(),
                )
            )
            if existing.scalar_one_or_none():
                raise CompanyValidationError("Domain already exists")

        # Create domain entity
        company = Company.create(
            account_id=user.account_id,
            name=request.name,
            domain=request.domain,
            website=request.website,
            parent_company_id=request.parent_company_id,
            industry=request.industry,
            size=request.size,
        )

        # Create database model
        company_model = CompanyModel(
            id=company.id,
            account_id=company.account_id,
            name=company.name,
            domain=company.domain,
            website=company.website,
            parent_company_id=company.parent_company_id,
            industry=company.industry,
            size=company.size,
        )

        # Handle tags
        if request.tag_ids:
            for tag_id in request.tag_ids:
                tag = await self.session.get(TagModel, tag_id)
                if tag and tag.account_id == user.account_id:
                    company_tag = CompanyTag(company_id=company.id, tag_id=tag_id)
                    self.session.add(company_tag)

        self.session.add(company_model)
        await self.session.flush()
        await self.session.refresh(company_model)

        return CompanyResponse.model_validate(company_model)


class GetCompanyUseCase:
    """Use case for retrieving a single company."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        company_id: UUID,
        user: AuthenticatedUser,
    ) -> CompanyResponse:
        """Get company by ID.

        Args:
            company_id: Company ID.
            user: Authenticated user.

        Returns:
            Company.

        Raises:
            CompanyValidationError: If company not found.
        """
        result = await self.session.execute(
            select(CompanyModel)
            .options(selectinload(CompanyModel.tags))
            .where(
                CompanyModel.id == company_id,
                CompanyModel.account_id == user.account_id,
            )
        )
        company = result.scalar_one_or_none()

        if not company:
            raise CompanyValidationError("Company not found")

        return CompanyResponse.model_validate(company)


class ListCompaniesUseCase:
    """Use case for listing companies with filtering."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        user: AuthenticatedUser,
        pagination: PaginationParams,
        search: str | None = None,
        tag_id: UUID | None = None,
    ) -> CompanyListResponse:
        """List companies with filters.

        Args:
            user: Authenticated user.
            pagination: Pagination parameters.
            search: Optional search term (name, domain).
            tag_id: Optional filter by tag.

        Returns:
            Paginated company list.
        """
        query = select(CompanyModel).where(CompanyModel.account_id == user.account_id)

        # Apply search filter
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    CompanyModel.name.ilike(search_pattern),
                    CompanyModel.domain.ilike(search_pattern),
                )
            )

        # Apply tag filter
        if tag_id:
            query = query.join(CompanyTag).where(CompanyTag.tag_id == tag_id)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar()

        # Apply pagination
        query = query.options(selectinload(CompanyModel.tags))
        query = query.offset(pagination.offset).limit(pagination.page_size)

        result = await self.session.execute(query)
        companies = result.scalars().all()

        total_pages = (total + pagination.page_size - 1) // pagination.page_size

        return CompanyListResponse(
            items=[CompanyResponse.model_validate(c) for c in companies],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
        )


class UpdateCompanyUseCase:
    """Use case for updating a company."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        company_id: UUID,
        request: UpdateCompanyRequest,
        user: AuthenticatedUser,
    ) -> CompanyResponse:
        """Update company.

        Args:
            company_id: Company ID.
            request: Update data.
            user: Authenticated user.

        Returns:
            Updated company.

        Raises:
            CompanyValidationError: If company not found or validation fails.
        """
        result = await self.session.execute(
            select(CompanyModel).where(
                CompanyModel.id == company_id,
                CompanyModel.account_id == user.account_id,
            )
        )
        company_model = result.scalar_one_or_none()

        if not company_model:
            raise CompanyValidationError("Company not found")

        # Update fields
        if request.name is not None:
            company_model.name = request.name
        if request.domain is not None:
            # Check for duplicate domain
            existing = await self.session.execute(
                select(CompanyModel).where(
                    CompanyModel.domain == request.domain.lower(),
                    CompanyModel.id != company_id,
                )
            )
            if existing.scalar_one_or_none():
                raise CompanyValidationError("Domain already exists")
            company_model.domain = request.domain.lower()
        if request.website is not None:
            company_model.website = request.website
        if request.parent_company_id is not None:
            company_model.parent_company_id = request.parent_company_id
        if request.industry is not None:
            company_model.industry = request.industry
        if request.size is not None:
            company_model.size = request.size

        # Update tags
        if request.tag_ids is not None:
            # Remove existing tags
            for ct in (await self.session.execute(
                select(CompanyTag).where(CompanyTag.company_id == company_id)
            )).scalars():
                await self.session.delete(ct)

            # Add new tags
            for tag_id in request.tag_ids:
                tag = await self.session.get(TagModel, tag_id)
                if tag and tag.account_id == user.account_id:
                    company_tag = CompanyTag(company_id=company_id, tag_id=tag_id)
                    self.session.add(company_tag)

        await self.session.flush()
        await self.session.refresh(company_model)

        return CompanyResponse.model_validate(company_model)


class DeleteCompanyUseCase:
    """Use case for deleting a company."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        company_id: UUID,
        user: AuthenticatedUser,
    ) -> None:
        """Delete company.

        Args:
            company_id: Company ID.
            user: Authenticated user.

        Raises:
            CompanyValidationError: If company not found.
        """
        result = await self.session.execute(
            select(CompanyModel).where(
                CompanyModel.id == company_id,
                CompanyModel.account_id == user.account_id,
            )
        )
        company = result.scalar_one_or_none()

        if not company:
            raise CompanyValidationError("Company not found")

        await self.session.delete(company)
