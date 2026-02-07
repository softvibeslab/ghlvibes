"""Note use cases (SPEC-CRM-005).

Implements business logic for note CRUD operations
and communication logging.
"""

from uuid import UUID

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import AuthenticatedUser
from src.crm.application.dtos import (
    CreateNoteRequest,
    NoteListResponse,
    NoteResponse,
    PaginationParams,
    UpdateNoteRequest,
)
from src.crm.domain.entities import Note
from src.crm.domain.exceptions import NoteValidationError
from src.crm.infrastructure.models import NoteModel


class CreateNoteUseCase:
    """Use case for creating a new note."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        request: CreateNoteRequest,
        user: AuthenticatedUser,
    ) -> NoteResponse:
        """Create a new note.

        Args:
            request: Note creation data.
            user: Authenticated user.

        Returns:
            Created note.
        """
        note = Note.create(
            account_id=user.account_id,
            content=request.content,
            note_type=request.note_type,
            contact_id=request.contact_id,
            company_id=request.company_id,
            deal_id=request.deal_id,
            created_by=user.id,
        )

        note_model = NoteModel(
            id=note.id,
            account_id=note.account_id,
            content=note.content,
            note_type=note.note_type,
            contact_id=note.contact_id,
            company_id=note.company_id,
            deal_id=note.deal_id,
            created_by=note.created_by,
        )

        self.session.add(note_model)
        await self.session.flush()
        await self.session.refresh(note_model)

        return NoteResponse.model_validate(note_model)


class GetNoteUseCase:
    """Use case for retrieving a single note."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        note_id: UUID,
        user: AuthenticatedUser,
    ) -> NoteResponse:
        """Get note by ID.

        Args:
            note_id: Note ID.
            user: Authenticated user.

        Returns:
            Note.

        Raises:
            NoteValidationError: If note not found.
        """
        result = await self.session.execute(
            select(NoteModel).where(
                NoteModel.id == note_id,
                NoteModel.account_id == user.account_id,
            )
        )
        note = result.scalar_one_or_none()

        if not note:
            raise NoteValidationError("Note not found")

        return NoteResponse.model_validate(note)


class ListNotesUseCase:
    """Use case for listing notes with filtering."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        user: AuthenticatedUser,
        pagination: PaginationParams,
        note_type: str | None = None,
        contact_id: UUID | None = None,
        company_id: UUID | None = None,
        deal_id: UUID | None = None,
    ) -> NoteListResponse:
        """List notes with filters.

        Args:
            user: Authenticated user.
            pagination: Pagination parameters.
            note_type: Optional filter by type (note, email, call, sms).
            contact_id: Optional filter by contact.
            company_id: Optional filter by company.
            deal_id: Optional filter by deal.

        Returns:
            Paginated note list.
        """
        query = select(NoteModel).where(NoteModel.account_id == user.account_id)

        if note_type:
            query = query.where(NoteModel.note_type == note_type)
        if contact_id:
            query = query.where(NoteModel.contact_id == contact_id)
        if company_id:
            query = query.where(NoteModel.company_id == company_id)
        if deal_id:
            query = query.where(NoteModel.deal_id == deal_id)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar()

        # Apply pagination
        query = query.order_by(NoteModel.created_at.desc())
        query = query.offset(pagination.offset).limit(pagination.page_size)

        result = await self.session.execute(query)
        notes = result.scalars().all()

        total_pages = (total + pagination.page_size - 1) // pagination.page_size

        return NoteListResponse(
            items=[NoteResponse.model_validate(n) for n in notes],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
        )


class UpdateNoteUseCase:
    """Use case for updating a note."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        note_id: UUID,
        request: UpdateNoteRequest,
        user: AuthenticatedUser,
    ) -> NoteResponse:
        """Update note content.

        Args:
            note_id: Note ID.
            request: Update data with new content.
            user: Authenticated user.

        Returns:
            Updated note.

        Raises:
            NoteValidationError: If note not found.
        """
        result = await self.session.execute(
            select(NoteModel).where(
                NoteModel.id == note_id,
                NoteModel.account_id == user.account_id,
            )
        )
        note_model = result.scalar_one_or_none()

        if not note_model:
            raise NoteValidationError("Note not found")

        note_model.content = request.content

        await self.session.flush()
        await self.session.refresh(note_model)

        return NoteResponse.model_validate(note_model)


class DeleteNoteUseCase:
    """Use case for deleting a note."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize use case."""
        self.session = session

    async def execute(
        self,
        note_id: UUID,
        user: AuthenticatedUser,
    ) -> None:
        """Delete note.

        Args:
            note_id: Note ID.
            user: Authenticated user.

        Raises:
            NoteValidationError: If note not found.
        """
        result = await self.session.execute(
            select(NoteModel).where(
                NoteModel.id == note_id,
                NoteModel.account_id == user.account_id,
            )
        )
        note = result.scalar_one_or_none()

        if not note:
            raise NoteValidationError("Note not found")

        await self.session.delete(note)
