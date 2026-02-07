"""API routes for CRM module.

Comprehensive REST API covering all 5 CRM SPECs:
- SPEC-CRM-001: Contacts Management
- SPEC-CRM-002: Pipelines & Deals
- SPEC-CRM-003: Companies
- SPEC-CRM-004: Activities/Tasks
- SPEC-CRM-005: Notes & Communications
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import AuthenticatedUser
from src.crm.application.dtos import (
    ErrorResponse,
    # Contact DTOs
    ContactResponse,
    CreateContactRequest,
    UpdateContactRequest,
    ContactListResponse,
    BulkImportRequest,
    BulkImportResponse,
    # Company DTOs
    CompanyResponse,
    CreateCompanyRequest,
    UpdateCompanyRequest,
    CompanyListResponse,
    # Pipeline/Deal DTOs
    PipelineResponse,
    CreatePipelineRequest,
    DealResponse,
    CreateDealRequest,
    UpdateDealRequest,
    DealListResponse,
    DealForecastResponse,
    # Activity DTOs
    ActivityResponse,
    CreateActivityRequest,
    UpdateActivityRequest,
    ActivityListResponse,
    # Note DTOs
    NoteResponse,
    CreateNoteRequest,
    UpdateNoteRequest,
    NoteListResponse,
)
from src.crm.domain.exceptions import (
    ContactValidationError,
    CompanyValidationError,
    DealValidationError,
    ActivityValidationError,
    NoteValidationError,
    PipelineValidationError,
    InvalidStageTransitionError,
)
from src.crm.domain.value_objects import ActivityStatus, ActivityType, DealStatus
from src.crm.presentation.dependencies import (
    # Contacts
    CreateContactUseCaseDep,
    GetContactUseCaseDep,
    ListContactsUseCaseDep,
    UpdateContactUseCaseDep,
    DeleteContactUseCaseDep,
    BulkImportContactsUseCaseDep,
    # Companies
    CreateCompanyUseCaseDep,
    GetCompanyUseCaseDep,
    ListCompaniesUseCaseDep,
    UpdateCompanyUseCaseDep,
    DeleteCompanyUseCaseDep,
    # Pipelines/Deals
    CreatePipelineUseCaseDep,
    GetPipelineUseCaseDep,
    ListPipelinesUseCaseDep,
    UpdatePipelineUseCaseDep,
    DeletePipelineUseCaseDep,
    CreateDealUseCaseDep,
    GetDealUseCaseDep,
    ListDealsUseCaseDep,
    UpdateDealUseCaseDep,
    DeleteDealUseCaseDep,
    # Activities
    CreateActivityUseCaseDep,
    GetActivityUseCaseDep,
    ListActivitiesUseCaseDep,
    UpdateActivityUseCaseDep,
    DeleteActivityUseCaseDep,
    # Notes
    CreateNoteUseCaseDep,
    GetNoteUseCaseDep,
    ListNotesUseCaseDep,
    UpdateNoteUseCaseDep,
    DeleteNoteUseCaseDep,
    PaginationDep,
)

router = APIRouter(
    prefix="/api/v1/crm",
    tags=["CRM"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)


# ============================================================================
# Contact Routes (SPEC-CRM-001)
# ============================================================================

contact_router = APIRouter(prefix="/contacts", tags=["Contacts"])


@contact_router.post(
    "",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new contact",
)
async def create_contact(
    body: CreateContactRequest,
    user: AuthenticatedUser,
    use_case: CreateContactUseCaseDep,
) -> ContactResponse:
    """Create a new contact."""
    try:
        return await use_case.execute(body, user)
    except ContactValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@contact_router.get(
    "/{contact_id}",
    response_model=ContactResponse,
    summary="Get contact by ID",
)
async def get_contact(
    contact_id: UUID,
    user: AuthenticatedUser,
    use_case: GetContactUseCaseDep,
) -> ContactResponse:
    """Get a specific contact."""
    try:
        return await use_case.execute(contact_id, user)
    except ContactValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))


@contact_router.get(
    "",
    response_model=ContactListResponse,
    summary="List contacts with filters",
)
async def list_contacts(
    user: AuthenticatedUser,
    pagination: PaginationDep,
    use_case: ListContactsUseCaseDep,
    search: str | None = Query(None, description="Search by name or email"),
    tag_id: UUID | None = Query(None, description="Filter by tag"),
    company_id: UUID | None = Query(None, description="Filter by company"),
) -> ContactListResponse:
    """List contacts with optional filters."""
    return await use_case.execute(user, pagination, search, tag_id, company_id)


@contact_router.patch(
    "/{contact_id}",
    response_model=ContactResponse,
    summary="Update contact",
)
async def update_contact(
    contact_id: UUID,
    body: UpdateContactRequest,
    user: AuthenticatedUser,
    use_case: UpdateContactUseCaseDep,
) -> ContactResponse:
    """Update contact details."""
    try:
        return await use_case.execute(contact_id, body, user)
    except ContactValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@contact_router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete contact",
)
async def delete_contact(
    contact_id: UUID,
    user: AuthenticatedUser,
    use_case: DeleteContactUseCaseDep,
) -> None:
    """Delete a contact."""
    try:
        await use_case.execute(contact_id, user)
    except ContactValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))


@contact_router.post(
    "/bulk-import",
    response_model=BulkImportResponse,
    summary="Bulk import contacts",
)
async def bulk_import_contacts(
    body: BulkImportRequest,
    user: AuthenticatedUser,
    use_case: BulkImportContactsUseCaseDep,
) -> BulkImportResponse:
    """Import multiple contacts in bulk."""
    return await use_case.execute(body, user)


router.include_router(contact_router)


# ============================================================================
# Company Routes (SPEC-CRM-003)
# ============================================================================

company_router = APIRouter(prefix="/companies", tags=["Companies"])


@company_router.post(
    "",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new company",
)
async def create_company(
    body: CreateCompanyRequest,
    user: AuthenticatedUser,
    use_case: CreateCompanyUseCaseDep,
) -> CompanyResponse:
    """Create a new company."""
    try:
        return await use_case.execute(body, user)
    except CompanyValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@company_router.get(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="Get company by ID",
)
async def get_company(
    company_id: UUID,
    user: AuthenticatedUser,
    use_case: GetCompanyUseCaseDep,
) -> CompanyResponse:
    """Get a specific company."""
    try:
        return await use_case.execute(company_id, user)
    except CompanyValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))


@company_router.get(
    "",
    response_model=CompanyListResponse,
    summary="List companies with filters",
)
async def list_companies(
    user: AuthenticatedUser,
    pagination: PaginationDep,
    use_case: ListCompaniesUseCaseDep,
    search: str | None = Query(None, description="Search by name or domain"),
    tag_id: UUID | None = Query(None, description="Filter by tag"),
) -> CompanyListResponse:
    """List companies with optional filters."""
    return await use_case.execute(user, pagination, search, tag_id)


@company_router.patch(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="Update company",
)
async def update_company(
    company_id: UUID,
    body: UpdateCompanyRequest,
    user: AuthenticatedUser,
    use_case: UpdateCompanyUseCaseDep,
) -> CompanyResponse:
    """Update company details."""
    try:
        return await use_case.execute(company_id, body, user)
    except CompanyValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@company_router.delete(
    "/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete company",
)
async def delete_company(
    company_id: UUID,
    user: AuthenticatedUser,
    use_case: DeleteCompanyUseCaseDep,
) -> None:
    """Delete a company."""
    try:
        await use_case.execute(company_id, user)
    except CompanyValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))


router.include_router(company_router)


# ============================================================================
# Pipeline Routes (SPEC-CRM-002)
# ============================================================================

pipeline_router = APIRouter(prefix="/pipelines", tags=["Pipelines"])


@pipeline_router.post(
    "",
    response_model=PipelineResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new pipeline",
)
async def create_pipeline(
    body: CreatePipelineRequest,
    user: AuthenticatedUser,
    use_case: CreatePipelineUseCaseDep,
) -> PipelineResponse:
    """Create a new sales pipeline."""
    try:
        return await use_case.execute(body, user)
    except PipelineValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@pipeline_router.get(
    "/{pipeline_id}",
    response_model=PipelineResponse,
    summary="Get pipeline by ID",
)
async def get_pipeline(
    pipeline_id: UUID,
    user: AuthenticatedUser,
    use_case: GetPipelineUseCaseDep,
) -> PipelineResponse:
    """Get a specific pipeline with stages."""
    try:
        return await use_case.execute(pipeline_id, user)
    except PipelineValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))


@pipeline_router.get(
    "",
    response_model=list[PipelineResponse],
    summary="List all pipelines",
)
async def list_pipelines(
    user: AuthenticatedUser,
    use_case: ListPipelinesUseCaseDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> list[PipelineResponse]:
    """List all pipelines for the account."""
    from src.crm.application.dtos import PaginationParams
    return await use_case.execute(user, PaginationParams(page=page, page_size=page_size))


@pipeline_router.patch(
    "/{pipeline_id}",
    response_model=PipelineResponse,
    summary="Update pipeline",
)
async def update_pipeline(
    pipeline_id: UUID,
    name: str = Query(..., min_length=1, max_length=100),
    user: AuthenticatedUser,
    use_case: UpdatePipelineUseCaseDep,
) -> PipelineResponse:
    """Update pipeline name."""
    try:
        return await use_case.execute(pipeline_id, name, user)
    except PipelineValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@pipeline_router.delete(
    "/{pipeline_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete pipeline",
)
async def delete_pipeline(
    pipeline_id: UUID,
    user: AuthenticatedUser,
    use_case: DeletePipelineUseCaseDep,
) -> None:
    """Delete a pipeline."""
    try:
        await use_case.execute(pipeline_id, user)
    except PipelineValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))


router.include_router(pipeline_router)


# ============================================================================
# Deal Routes (SPEC-CRM-002)
# ============================================================================

deal_router = APIRouter(prefix="/deals", tags=["Deals"])


@deal_router.post(
    "",
    response_model=DealResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new deal",
)
async def create_deal(
    body: CreateDealRequest,
    user: AuthenticatedUser,
    use_case: CreateDealUseCaseDep,
) -> DealResponse:
    """Create a new deal/opportunity."""
    try:
        return await use_case.execute(body, user)
    except DealValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@deal_router.get(
    "/{deal_id}",
    response_model=DealResponse,
    summary="Get deal by ID",
)
async def get_deal(
    deal_id: UUID,
    user: AuthenticatedUser,
    use_case: GetDealUseCaseDep,
) -> DealResponse:
    """Get a specific deal."""
    try:
        return await use_case.execute(deal_id, user)
    except DealValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))


@deal_router.get(
    "",
    response_model=DealListResponse,
    summary="List deals with filters",
)
async def list_deals(
    user: AuthenticatedUser,
    use_case: ListDealsUseCaseDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    pipeline_id: UUID | None = Query(None),
    stage_id: UUID | None = Query(None),
    status: DealStatus | None = Query(None),
    contact_id: UUID | None = Query(None),
    company_id: UUID | None = Query(None),
) -> DealListResponse:
    """List deals with optional filters."""
    from src.crm.application.dtos import PaginationParams
    return await use_case.execute(
        user,
        PaginationParams(page=page, page_size=page_size),
        pipeline_id,
        stage_id,
        status,
        contact_id,
        company_id,
    )


@deal_router.patch(
    "/{deal_id}",
    response_model=DealResponse,
    summary="Update deal",
)
async def update_deal(
    deal_id: UUID,
    body: UpdateDealRequest,
    user: AuthenticatedUser,
    use_case: UpdateDealUseCaseDep,
) -> DealResponse:
    """Update deal details."""
    try:
        return await use_case.execute(deal_id, body, user)
    except DealValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@deal_router.delete(
    "/{deal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete deal",
)
async def delete_deal(
    deal_id: UUID,
    user: AuthenticatedUser,
    use_case: DeleteDealUseCaseDep,
) -> None:
    """Delete a deal."""
    try:
        await use_case.execute(deal_id, user)
    except DealValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))


@deal_router.post(
    "/{deal_id}/move",
    response_model=DealResponse,
    summary="Move deal to new stage",
)
async def move_deal_stage(
    deal_id: UUID,
    stage_id: UUID = Query(..., description="New stage ID"),
    probability: int | None = Query(None, ge=0, le=100, description="Probability override"),
    user: AuthenticatedUser,
) -> DealResponse:
    """Move deal to a different pipeline stage."""
    from src.crm.application.use_cases.deals import MoveDealStageUseCase
    from src.core.database import get_db
    from sqlalchemy.ext.asyncio import AsyncSession

    # Create use case with session
    session: AsyncSession = Depends(get_db)()
    use_case = MoveDealStageUseCase(session)

    try:
        return await use_case.execute(deal_id, stage_id, probability, user)
    except (DealValidationError, InvalidStageTransitionError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@deal_router.post(
    "/{deal_id}/win",
    response_model=DealResponse,
    summary="Mark deal as won",
)
async def win_deal(
    deal_id: UUID,
    user: AuthenticatedUser,
) -> DealResponse:
    """Mark a deal as won."""
    from src.crm.application.use_cases.deals import WinDealUseCase
    from src.core.database import get_db
    from sqlalchemy.ext.asyncio import AsyncSession
    from datetime import datetime

    session: AsyncSession = Depends(get_db)()
    use_case = WinDealUseCase(session)

    try:
        return await use_case.execute(deal_id, datetime.now(), user)
    except DealValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@deal_router.post(
    "/{deal_id}/lose",
    response_model=DealResponse,
    summary="Mark deal as lost",
)
async def lose_deal(
    deal_id: UUID,
    user: AuthenticatedUser,
) -> DealResponse:
    """Mark a deal as lost."""
    from src.crm.application.use_cases.deals import LoseDealUseCase
    from src.core.database import get_db
    from sqlalchemy.ext.asyncio import AsyncSession
    from datetime import datetime

    session: AsyncSession = Depends(get_db)()
    use_case = LoseDealUseCase(session)

    try:
        return await use_case.execute(deal_id, datetime.now(), user)
    except DealValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@deal_router.get(
    "/forecast",
    response_model=DealForecastResponse,
    summary="Get deal forecast",
)
async def get_deal_forecast(
    user: AuthenticatedUser,
    pipeline_id: UUID | None = Query(None),
) -> DealForecastResponse:
    """Generate deal forecast summary."""
    from src.crm.application.use_cases.deals import GetDealForecastUseCase
    from src.core.database import get_db
    from sqlalchemy.ext.asyncio import AsyncSession

    session: AsyncSession = Depends(get_db)()
    use_case = GetDealForecastUseCase(session)

    return await use_case.execute(user, pipeline_id)


router.include_router(deal_router)


# ============================================================================
# Activity Routes (SPEC-CRM-004)
# ============================================================================

activity_router = APIRouter(prefix="/activities", tags=["Activities"])


@activity_router.post(
    "",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new activity",
)
async def create_activity(
    body: CreateActivityRequest,
    user: AuthenticatedUser,
    use_case: CreateActivityUseCaseDep,
) -> ActivityResponse:
    """Create a new activity (task, call, meeting, etc.)."""
    try:
        return await use_case.execute(body, user)
    except ActivityValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@activity_router.get(
    "/{activity_id}",
    response_model=ActivityResponse,
    summary="Get activity by ID",
)
async def get_activity(
    activity_id: UUID,
    user: AuthenticatedUser,
    use_case: GetActivityUseCaseDep,
) -> ActivityResponse:
    """Get a specific activity."""
    try:
        return await use_case.execute(activity_id, user)
    except ActivityValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))


@activity_router.get(
    "",
    response_model=ActivityListResponse,
    summary="List activities with filters",
)
async def list_activities(
    user: AuthenticatedUser,
    use_case: ListActivitiesUseCaseDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    activity_type: ActivityType | None = Query(None),
    status: ActivityStatus | None = Query(None),
    contact_id: UUID | None = Query(None),
    company_id: UUID | None = Query(None),
    deal_id: UUID | None = Query(None),
) -> ActivityListResponse:
    """List activities with optional filters."""
    from src.crm.application.dtos import PaginationParams
    return await use_case.execute(
        user,
        PaginationParams(page=page, page_size=page_size),
        activity_type,
        status,
        contact_id,
        company_id,
        deal_id,
    )


@activity_router.patch(
    "/{activity_id}",
    response_model=ActivityResponse,
    summary="Update activity",
)
async def update_activity(
    activity_id: UUID,
    body: UpdateActivityRequest,
    user: AuthenticatedUser,
    use_case: UpdateActivityUseCaseDep,
) -> ActivityResponse:
    """Update activity details."""
    try:
        return await use_case.execute(activity_id, body, user)
    except ActivityValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@activity_router.delete(
    "/{activity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete activity",
)
async def delete_activity(
    activity_id: UUID,
    user: AuthenticatedUser,
    use_case: DeleteActivityUseCaseDep,
) -> None:
    """Delete an activity."""
    try:
        await use_case.execute(activity_id, user)
    except ActivityValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))


@activity_router.post(
    "/{activity_id}/complete",
    response_model=ActivityResponse,
    summary="Mark activity as completed",
)
async def complete_activity(
    activity_id: UUID,
    user: AuthenticatedUser,
) -> ActivityResponse:
    """Mark an activity as completed."""
    from src.crm.application.use_cases.activities import CompleteActivityUseCase
    from src.core.database import get_db
    from sqlalchemy.ext.asyncio import AsyncSession

    session: AsyncSession = Depends(get_db)()
    use_case = CompleteActivityUseCase(session)

    try:
        return await use_case.execute(activity_id, user)
    except ActivityValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


router.include_router(activity_router)


# ============================================================================
# Note Routes (SPEC-CRM-005)
# ============================================================================

note_router = APIRouter(prefix="/notes", tags=["Notes"])


@note_router.post(
    "",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new note",
)
async def create_note(
    body: CreateNoteRequest,
    user: AuthenticatedUser,
    use_case: CreateNoteUseCaseDep,
) -> NoteResponse:
    """Create a new note or communication log."""
    try:
        return await use_case.execute(body, user)
    except NoteValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@note_router.get(
    "/{note_id}",
    response_model=NoteResponse,
    summary="Get note by ID",
)
async def get_note(
    note_id: UUID,
    user: AuthenticatedUser,
    use_case: GetNoteUseCaseDep,
) -> NoteResponse:
    """Get a specific note."""
    try:
        return await use_case.execute(note_id, user)
    except NoteValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))


@note_router.get(
    "",
    response_model=NoteListResponse,
    summary="List notes with filters",
)
async def list_notes(
    user: AuthenticatedUser,
    use_case: ListNotesUseCaseDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    note_type: str | None = Query(None, description="Filter by type: note, email, call, sms"),
    contact_id: UUID | None = Query(None),
    company_id: UUID | None = Query(None),
    deal_id: UUID | None = Query(None),
) -> NoteListResponse:
    """List notes with optional filters."""
    from src.crm.application.dtos import PaginationParams
    return await use_case.execute(
        user,
        PaginationParams(page=page, page_size=page_size),
        note_type,
        contact_id,
        company_id,
        deal_id,
    )


@note_router.patch(
    "/{note_id}",
    response_model=NoteResponse,
    summary="Update note",
)
async def update_note(
    note_id: UUID,
    body: UpdateNoteRequest,
    user: AuthenticatedUser,
    use_case: UpdateNoteUseCaseDep,
) -> NoteResponse:
    """Update note content."""
    try:
        return await use_case.execute(note_id, body, user)
    except NoteValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@note_router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete note",
)
async def delete_note(
    note_id: UUID,
    user: AuthenticatedUser,
    use_case: DeleteNoteUseCaseDep,
) -> None:
    """Delete a note."""
    try:
        await use_case.execute(note_id, user)
    except NoteValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))


router.include_router(note_router)
