"""Integration tests for Contact CRUD operations.

Tests database interactions and repository patterns.
"""

import pytest
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.crm.application.dtos import (
    CreateContactRequest,
    UpdateContactRequest,
    BulkImportRequest,
    PaginationParams,
)
from src.crm.application.use_cases.contacts import (
    CreateContactUseCase,
    GetContactUseCase,
    ListContactsUseCase,
    UpdateContactUseCase,
    DeleteContactUseCase,
    BulkImportContactsUseCase,
)
from src.core.dependencies import AuthenticatedUser


@pytest.mark.asyncio
class TestContactIntegration:
    """Integration tests for contact operations."""

    async def test_create_contact_persists_to_database(
        self,
        async_session: AsyncSession,
        test_user: AuthenticatedUser,
    ):
        """Test creating a contact persists to database."""
        request = CreateContactRequest(
            email="john@example.com",
            first_name="John",
            last_name="Doe",
            phone="+14155551234",
        )

        use_case = CreateContactUseCase(async_session)
        response = await use_case.execute(request, test_user)

        assert response.email == "john@example.com"
        assert response.first_name == "John"
        assert response.last_name == "Doe"

    async def test_get_contact_retrieves_from_database(
        self,
        async_session: AsyncSession,
        test_user: AuthenticatedUser,
        sample_contact_model,
    ):
        """Test getting a contact retrieves from database."""
        use_case = GetContactUseCase(async_session)
        response = await use_case.execute(sample_contact_model.id, test_user)

        assert response.id == sample_contact_model.id
        assert response.email == sample_contact_model.email

    async def test_list_contacts_with_pagination(
        self,
        async_session: AsyncSession,
        test_user: AuthenticatedUser,
        sample_contact_model,
    ):
        """Test listing contacts with pagination."""
        use_case = ListContactsUseCase(async_session)
        pagination = PaginationParams(page=1, page_size=20)

        response = await use_case.execute(test_user, pagination)

        assert len(response.items) >= 1
        assert response.total >= 1
        assert response.page == 1

    async def test_update_contact_modifies_database(
        self,
        async_session: AsyncSession,
        test_user: AuthenticatedUser,
        sample_contact_model,
    ):
        """Test updating a contact modifies database."""
        request = UpdateContactRequest(
            first_name="Jane",
            email="jane@example.com",
        )

        use_case = UpdateContactUseCase(async_session)
        response = await use_case.execute(sample_contact_model.id, request, test_user)

        assert response.first_name == "Jane"
        assert response.email == "jane@example.com"

    async def test_delete_contact_removes_from_database(
        self,
        async_session: AsyncSession,
        test_user: AuthenticatedUser,
        sample_contact_model,
    ):
        """Test deleting a contact removes from database."""
        use_case = DeleteContactUseCase(async_session)
        await use_case.execute(sample_contact_model.id, test_user)

        # Verify deletion
        get_use_case = GetContactUseCase(async_session)
        with pytest.raises(Exception):  # ContactNotFoundError expected
            await get_use_case.execute(sample_contact_model.id, test_user)

    async def test_bulk_import_contacts(
        self,
        async_session: AsyncSession,
        test_user: AuthenticatedUser,
    ):
        """Test bulk importing contacts."""
        request = BulkImportRequest(
            contacts=[
                CreateContactRequest(
                    email="contact1@example.com",
                    first_name="Contact",
                    last_name="One",
                ),
                CreateContactRequest(
                    email="contact2@example.com",
                    first_name="Contact",
                    last_name="Two",
                ),
                CreateContactRequest(
                    email="invalid-email",  # Invalid
                    first_name="Invalid",
                    last_name="Email",
                ),
            ]
        )

        use_case = BulkImportContactsUseCase(async_session)
        response = await use_case.execute(request, test_user)

        assert response.imported == 2
        assert response.failed == 1
        assert len(response.errors) == 1
