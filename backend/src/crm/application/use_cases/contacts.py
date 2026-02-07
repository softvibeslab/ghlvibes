"""Contact use cases (SPEC-CRM-001).

Implements business logic for contact CRUD operations,
bulk import/export, tag management, and search/filtering.
"""

from typing import Any
from uuid import UUID

from sqlalchemy import func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.dependencies import AuthenticatedUser
from src.crm.application.dtos import (
    BulkImportRequest,
    BulkImportResponse,
    ContactListResponse,
    ContactResponse,
    CreateContactRequest,
    PaginationParams,
    UpdateContactRequest,
)
from src.crm.domain.entities import Contact, Tag
from src.crm.domain.exceptions import ContactValidationError
from src.crm.infrastructure.models import ContactModel, ContactTag, TagModel


class CreateContactUseCase:
    """Use case for creating a new contact."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case.

        Args:
            session: Database session.
        """
        self.session = session

    async def execute(
        self,
        request: CreateContactRequest,
        user: AuthenticatedUser,
    ) -> ContactResponse:
        """Create a new contact.

        Args:
            request: Contact creation data.
            user: Authenticated user.

        Returns:
            Created contact.

        Raises:
            ContactValidationError: If validation fails.
        """
        # Check for duplicate email
        if request.email:
            existing = await self.session.execute(
                select(ContactModel).where(
                    ContactModel.email == request.email,
                    ContactModel.account_id == user.account_id,
                )
            )
            if existing.scalar_one_or_none():
                raise ContactValidationError("Email already exists")

        # Create domain entity
        contact = Contact.create(
            account_id=user.account_id,
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            phone=request.phone,
            company_id=request.company_id,
            created_by=user.id,
        )

        # Handle custom fields
        if request.custom_fields:
            contact.custom_fields = request.custom_fields

        # Create database model
        contact_model = ContactModel(
            id=contact.id,
            account_id=contact.account_id,
            email=str(contact.email) if contact.email else None,
            first_name=contact.first_name,
            last_name=contact.last_name,
            phone=contact.phone.formatted() if contact.phone else None,
            phone_country_code=contact.phone.country_code if contact.phone else None,
            company_id=contact.company_id,
            custom_fields=contact.custom_fields,
            created_by=contact.created_by,
        )

        # Handle tags
        if request.tag_ids:
            for tag_id in request.tag_ids:
                tag = await self.session.get(TagModel, tag_id)
                if tag and tag.account_id == user.account_id:
                    contact_tag = ContactTag(contact_id=contact.id, tag_id=tag_id)
                    self.session.add(contact_tag)

        self.session.add(contact_model)
        await self.session.flush()
        await self.session.refresh(contact_model)

        # Load tags for response
        await self.session.execute(
            select(ContactModel)
            .options(selectinload(ContactModel.tags))
            .where(ContactModel.id == contact_model.id)
        )
        contact_model.tags = [
            ct.tag for ct in await self.session.execute(
                select(ContactTag).where(ContactTag.contact_id == contact.id)
            )
        ]

        return ContactResponse.model_validate(contact_model)


class GetContactUseCase:
    """Use case for retrieving a single contact."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        contact_id: UUID,
        user: AuthenticatedUser,
    ) -> ContactResponse:
        """Get contact by ID.

        Args:
            contact_id: Contact ID.
            user: Authenticated user.

        Returns:
            Contact.

        Raises:
            ContactValidationError: If contact not found.
        """
        result = await self.session.execute(
            select(ContactModel)
            .options(selectinload(ContactModel.tags))
            .where(
                ContactModel.id == contact_id,
                ContactModel.account_id == user.account_id,
            )
        )
        contact = result.scalar_one_or_none()

        if not contact:
            raise ContactValidationError("Contact not found")

        return ContactResponse.model_validate(contact)


class ListContactsUseCase:
    """Use case for listing contacts with filtering."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        user: AuthenticatedUser,
        pagination: PaginationParams,
        search: str | None = None,
        tag_id: UUID | None = None,
        company_id: UUID | None = None,
    ) -> ContactListResponse:
        """List contacts with filters.

        Args:
            user: Authenticated user.
            pagination: Pagination parameters.
            search: Optional search term (name, email).
            tag_id: Optional filter by tag.
            company_id: Optional filter by company.

        Returns:
            Paginated contact list.
        """
        query = select(ContactModel).where(ContactModel.account_id == user.account_id)

        # Apply search filter
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    ContactModel.first_name.ilike(search_pattern),
                    ContactModel.last_name.ilike(search_pattern),
                    ContactModel.email.ilike(search_pattern),
                )
            )

        # Apply tag filter
        if tag_id:
            query = query.join(ContactTag).where(ContactTag.tag_id == tag_id)

        # Apply company filter
        if company_id:
            query = query.where(ContactModel.company_id == company_id)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar()

        # Apply pagination
        query = query.options(selectinload(ContactModel.tags))
        query = query.offset(pagination.offset).limit(pagination.page_size)

        result = await self.session.execute(query)
        contacts = result.scalars().all()

        total_pages = (total + pagination.page_size - 1) // pagination.page_size

        return ContactListResponse(
            items=[ContactResponse.model_validate(c) for c in contacts],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
        )


class UpdateContactUseCase:
    """Use case for updating a contact."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        contact_id: UUID,
        request: UpdateContactRequest,
        user: AuthenticatedUser,
    ) -> ContactResponse:
        """Update contact.

        Args:
            contact_id: Contact ID.
            request: Update data.
            user: Authenticated user.

        Returns:
            Updated contact.

        Raises:
            ContactValidationError: If contact not found or validation fails.
        """
        result = await self.session.execute(
            select(ContactModel).where(
                ContactModel.id == contact_id,
                ContactModel.account_id == user.account_id,
            )
        )
        contact_model = result.scalar_one_or_none()

        if not contact_model:
            raise ContactValidationError("Contact not found")

        # Update fields
        if request.email is not None:
            # Check for duplicate email
            existing = await self.session.execute(
                select(ContactModel).where(
                    ContactModel.email == request.email,
                    ContactModel.account_id == user.account_id,
                    ContactModel.id != contact_id,
                )
            )
            if existing.scalar_one_or_none():
                raise ContactValidationError("Email already exists")
            contact_model.email = request.email

        if request.first_name is not None:
            contact_model.first_name = request.first_name
        if request.last_name is not None:
            contact_model.last_name = request.last_name
        if request.phone is not None:
            contact_model.phone = request.phone
        if request.phone_country_code is not None:
            contact_model.phone_country_code = request.phone_country_code
        if request.company_id is not None:
            contact_model.company_id = request.company_id
        if request.custom_fields is not None:
            contact_model.custom_fields.update(request.custom_fields)

        # Update tags
        if request.tag_ids is not None:
            # Remove existing tags
            await self.session.execute(
                select(ContactTag).where(ContactTag.contact_id == contact_id)
            )
            for ct in (await self.session.execute(
                select(ContactTag).where(ContactTag.contact_id == contact_id)
            )).scalars():
                await self.session.delete(ct)

            # Add new tags
            for tag_id in request.tag_ids:
                tag = await self.session.get(TagModel, tag_id)
                if tag and tag.account_id == user.account_id:
                    contact_tag = ContactTag(contact_id=contact_id, tag_id=tag_id)
                    self.session.add(contact_tag)

        await self.session.flush()
        await self.session.refresh(contact_model)

        return ContactResponse.model_validate(contact_model)


class DeleteContactUseCase:
    """Use case for deleting a contact."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        contact_id: UUID,
        user: AuthenticatedUser,
    ) -> None:
        """Delete contact.

        Args:
            contact_id: Contact ID.
            user: Authenticated user.

        Raises:
            ContactValidationError: If contact not found.
        """
        result = await self.session.execute(
            select(ContactModel).where(
                ContactModel.id == contact_id,
                ContactModel.account_id == user.account_id,
            )
        )
        contact = result.scalar_one_or_none()

        if not contact:
            raise ContactValidationError("Contact not found")

        await self.session.delete(contact)


class BulkImportContactsUseCase:
    """Use case for bulk importing contacts."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        request: BulkImportRequest,
        user: AuthenticatedUser,
    ) -> BulkImportResponse:
        """Bulk import contacts.

        Args:
            request: Import data with contacts list.
            user: Authenticated user.

        Returns:
            Import results with success/error counts.
        """
        imported = 0
        failed = 0
        errors: list[dict[str, Any]] = []

        for idx, contact_data in enumerate(request.contacts):
            try:
                create_use_case = CreateContactUseCase(self.session)
                await create_use_case.execute(contact_data, user)
                imported += 1
            except Exception as e:
                failed += 1
                errors.append({
                    "index": idx,
                    "email": contact_data.email,
                    "error": str(e),
                })

        return BulkImportResponse(
            imported=imported,
            failed=failed,
            errors=errors,
        )


class AddTagToContactUseCase:
    """Use case for adding a tag to a contact."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        contact_id: UUID,
        tag_id: UUID,
        user: AuthenticatedUser,
    ) -> ContactResponse:
        """Add tag to contact.

        Args:
            contact_id: Contact ID.
            tag_id: Tag ID.
            user: Authenticated user.

        Returns:
            Updated contact.

        Raises:
            ContactValidationError: If contact or tag not found.
        """
        # Verify contact exists
        contact = await self.session.get(ContactModel, contact_id)
        if not contact or contact.account_id != user.account_id:
            raise ContactValidationError("Contact not found")

        # Verify tag exists
        tag = await self.session.get(TagModel, tag_id)
        if not tag or tag.account_id != user.account_id:
            raise ContactValidationError("Tag not found")

        # Check if already tagged
        existing = await self.session.execute(
            select(ContactTag).where(
                ContactTag.contact_id == contact_id,
                ContactTag.tag_id == tag_id,
            )
        )
        if existing.scalar_one_or_none():
            return ContactResponse.model_validate(contact)

        # Add tag
        contact_tag = ContactTag(contact_id=contact_id, tag_id=tag_id)
        self.session.add(contact_tag)

        await self.session.flush()
        await self.session.refresh(contact)

        return ContactResponse.model_validate(contact)


class RemoveTagFromContactUseCase:
    """Use case for removing a tag from a contact."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        contact_id: UUID,
        tag_id: UUID,
        user: AuthenticatedUser,
    ) -> ContactResponse:
        """Remove tag from contact.

        Args:
            contact_id: Contact ID.
            tag_id: Tag ID.
            user: Authenticated user.

        Returns:
            Updated contact.

        Raises:
            ContactValidationError: If contact not found.
        """
        # Verify contact exists
        contact = await self.session.get(ContactModel, contact_id)
        if not contact or contact.account_id != user.account_id:
            raise ContactValidationError("Contact not found")

        # Remove tag
        result = await self.session.execute(
            select(ContactTag).where(
                ContactTag.contact_id == contact_id,
                ContactTag.tag_id == tag_id,
            )
        )
        contact_tag = result.scalar_one_or_none()
        if contact_tag:
            await self.session.delete(contact_tag)

        await self.session.flush()
        await self.session.refresh(contact)

        return ContactResponse.model_validate(contact)
