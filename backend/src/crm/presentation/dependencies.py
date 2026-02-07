"""Dependencies for CRM routes.

Provides dependency injection for use cases and common parameters.
"""

from functools import lru_cache
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.crm.application.dtos import PaginationParams
from src.crm.application.use_cases.activities import (
    CancelActivityUseCase,
    CompleteActivityUseCase,
    CreateActivityUseCase,
    DeleteActivityUseCase,
    GetActivityUseCase,
    ListActivitiesUseCase,
    StartActivityUseCase,
    UpdateActivityUseCase,
)
from src.crm.application.use_cases.companies import (
    CreateCompanyUseCase,
    DeleteCompanyUseCase,
    GetCompanyUseCase,
    ListCompaniesUseCase,
    UpdateCompanyUseCase,
)
from src.crm.application.use_cases.contacts import (
    AddTagToContactUseCase,
    BulkImportContactsUseCase,
    CreateContactUseCase,
    DeleteContactUseCase,
    GetContactUseCase,
    ListContactsUseCase,
    RemoveTagFromContactUseCase,
    UpdateContactUseCase,
)
from src.crm.application.use_cases.deals import (
    CreateDealUseCase,
    DeleteDealUseCase,
    GetDealForecastUseCase,
    GetDealUseCase,
    ListDealsUseCase,
    LoseDealUseCase,
    MoveDealStageUseCase,
    UpdateDealUseCase,
    WinDealUseCase,
)
from src.crm.application.use_cases.notes import (
    CreateNoteUseCase,
    DeleteNoteUseCase,
    GetNoteUseCase,
    ListNotesUseCase,
    UpdateNoteUseCase,
)
from src.crm.application.use_cases.pipelines import (
    CreatePipelineUseCase,
    DeletePipelineUseCase,
    GetPipelineUseCase,
    ListPipelinesUseCase,
    UpdatePipelineUseCase,
)


# ============================================================================
# Pagination Dependency
# ============================================================================

def get_pagination(
    page: int = 1,
    page_size: int = 20,
) -> PaginationParams:
    """Get pagination parameters from query string.

    Args:
        page: Page number (1-indexed).
        page_size: Items per page.

    Returns:
        PaginationParams instance.
    """
    return PaginationParams(page=page, page_size=page_size)


PaginationDep = Annotated[PaginationParams, Depends(get_pagination)]


# ============================================================================
# Contact Use Case Dependencies
# ============================================================================

def get_create_contact_use_case(db: AsyncSession = Depends(get_db)) -> CreateContactUseCase:
    """Get CreateContactUseCase instance."""
    return CreateContactUseCase(db)


def get_get_contact_use_case(db: AsyncSession = Depends(get_db)) -> GetContactUseCase:
    """Get GetContactUseCase instance."""
    return GetContactUseCase(db)


def get_list_contacts_use_case(db: AsyncSession = Depends(get_db)) -> ListContactsUseCase:
    """Get ListContactsUseCase instance."""
    return ListContactsUseCase(db)


def get_update_contact_use_case(db: AsyncSession = Depends(get_db)) -> UpdateContactUseCase:
    """Get UpdateContactUseCase instance."""
    return UpdateContactUseCase(db)


def get_delete_contact_use_case(db: AsyncSession = Depends(get_db)) -> DeleteContactUseCase:
    """Get DeleteContactUseCase instance."""
    return DeleteContactUseCase(db)


def get_bulk_import_contacts_use_case(
    db: AsyncSession = Depends(get_db),
) -> BulkImportContactsUseCase:
    """Get BulkImportContactsUseCase instance."""
    return BulkImportContactsUseCase(db)


CreateContactUseCaseDep = Annotated[CreateContactUseCase, Depends(get_create_contact_use_case)]
GetContactUseCaseDep = Annotated[GetContactUseCase, Depends(get_get_contact_use_case)]
ListContactsUseCaseDep = Annotated[ListContactsUseCase, Depends(get_list_contacts_use_case)]
UpdateContactUseCaseDep = Annotated[UpdateContactUseCase, Depends(get_update_contact_use_case)]
DeleteContactUseCaseDep = Annotated[DeleteContactUseCase, Depends(get_delete_contact_use_case)]
BulkImportContactsUseCaseDep = Annotated[
    BulkImportContactsUseCase, Depends(get_bulk_import_contacts_use_case)
]


# ============================================================================
# Company Use Case Dependencies
# ============================================================================

def get_create_company_use_case(db: AsyncSession = Depends(get_db)) -> CreateCompanyUseCase:
    return CreateCompanyUseCase(db)


def get_get_company_use_case(db: AsyncSession = Depends(get_db)) -> GetCompanyUseCase:
    return GetCompanyUseCase(db)


def get_list_companies_use_case(db: AsyncSession = Depends(get_db)) -> ListCompaniesUseCase:
    return ListCompaniesUseCase(db)


def get_update_company_use_case(db: AsyncSession = Depends(get_db)) -> UpdateCompanyUseCase:
    return UpdateCompanyUseCase(db)


def get_delete_company_use_case(db: AsyncSession = Depends(get_db)) -> DeleteCompanyUseCase:
    return DeleteCompanyUseCase(db)


CreateCompanyUseCaseDep = Annotated[CreateCompanyUseCase, Depends(get_create_company_use_case)]
GetCompanyUseCaseDep = Annotated[GetCompanyUseCase, Depends(get_get_company_use_case)]
ListCompaniesUseCaseDep = Annotated[ListCompaniesUseCase, Depends(get_list_companies_use_case)]
UpdateCompanyUseCaseDep = Annotated[UpdateCompanyUseCase, Depends(get_update_company_use_case)]
DeleteCompanyUseCaseDep = Annotated[DeleteCompanyUseCase, Depends(get_delete_company_use_case)]


# ============================================================================
# Pipeline/Deal Use Case Dependencies
# ============================================================================

def get_create_pipeline_use_case(db: AsyncSession = Depends(get_db)) -> CreatePipelineUseCase:
    return CreatePipelineUseCase(db)


def get_get_pipeline_use_case(db: AsyncSession = Depends(get_db)) -> GetPipelineUseCase:
    return GetPipelineUseCase(db)


def get_list_pipelines_use_case(db: AsyncSession = Depends(get_db)) -> ListPipelinesUseCase:
    return ListPipelinesUseCase(db)


def get_update_pipeline_use_case(db: AsyncSession = Depends(get_db)) -> UpdatePipelineUseCase:
    return UpdatePipelineUseCase(db)


def get_delete_pipeline_use_case(db: AsyncSession = Depends(get_db)) -> DeletePipelineUseCase:
    return DeletePipelineUseCase(db)


CreatePipelineUseCaseDep = Annotated[CreatePipelineUseCase, Depends(get_create_pipeline_use_case)]
GetPipelineUseCaseDep = Annotated[GetPipelineUseCase, Depends(get_get_pipeline_use_case)]
ListPipelinesUseCaseDep = Annotated[ListPipelinesUseCase, Depends(get_list_pipelines_use_case)]
UpdatePipelineUseCaseDep = Annotated[UpdatePipelineUseCase, Depends(get_update_pipeline_use_case)]
DeletePipelineUseCaseDep = Annotated[DeletePipelineUseCase, Depends(get_delete_pipeline_use_case)]


def get_create_deal_use_case(db: AsyncSession = Depends(get_db)) -> CreateDealUseCase:
    return CreateDealUseCase(db)


def get_get_deal_use_case(db: AsyncSession = Depends(get_db)) -> GetDealUseCase:
    return GetDealUseCase(db)


def get_list_deals_use_case(db: AsyncSession = Depends(get_db)) -> ListDealsUseCase:
    return ListDealsUseCase(db)


def get_update_deal_use_case(db: AsyncSession = Depends(get_db)) -> UpdateDealUseCase:
    return UpdateDealUseCase(db)


def get_delete_deal_use_case(db: AsyncSession = Depends(get_db)) -> DeleteDealUseCase:
    return DeleteDealUseCase(db)


CreateDealUseCaseDep = Annotated[CreateDealUseCase, Depends(get_create_deal_use_case)]
GetDealUseCaseDep = Annotated[GetDealUseCase, Depends(get_get_deal_use_case)]
ListDealsUseCaseDep = Annotated[ListDealsUseCase, Depends(get_list_deals_use_case)]
UpdateDealUseCaseDep = Annotated[UpdateDealUseCase, Depends(get_update_deal_use_case)]
DeleteDealUseCaseDep = Annotated[DeleteDealUseCase, Depends(get_delete_deal_use_case)]


# ============================================================================
# Activity Use Case Dependencies
# ============================================================================

def get_create_activity_use_case(db: AsyncSession = Depends(get_db)) -> CreateActivityUseCase:
    return CreateActivityUseCase(db)


def get_get_activity_use_case(db: AsyncSession = Depends(get_db)) -> GetActivityUseCase:
    return GetActivityUseCase(db)


def get_list_activities_use_case(db: AsyncSession = Depends(get_db)) -> ListActivitiesUseCase:
    return ListActivitiesUseCase(db)


def get_update_activity_use_case(db: AsyncSession = Depends(get_db)) -> UpdateActivityUseCase:
    return UpdateActivityUseCase(db)


def get_delete_activity_use_case(db: AsyncSession = Depends(get_db)) -> DeleteActivityUseCase:
    return DeleteActivityUseCase(db)


CreateActivityUseCaseDep = Annotated[CreateActivityUseCase, Depends(get_create_activity_use_case)]
GetActivityUseCaseDep = Annotated[GetActivityUseCase, Depends(get_get_activity_use_case)]
ListActivitiesUseCaseDep = Annotated[ListActivitiesUseCase, Depends(get_list_activities_use_case)]
UpdateActivityUseCaseDep = Annotated[UpdateActivityUseCase, Depends(get_update_activity_use_case)]
DeleteActivityUseCaseDep = Annotated[DeleteActivityUseCase, Depends(get_delete_activity_use_case)]


# ============================================================================
# Note Use Case Dependencies
# ============================================================================

def get_create_note_use_case(db: AsyncSession = Depends(get_db)) -> CreateNoteUseCase:
    return CreateNoteUseCase(db)


def get_get_note_use_case(db: AsyncSession = Depends(get_db)) -> GetNoteUseCase:
    return GetNoteUseCase(db)


def get_list_notes_use_case(db: AsyncSession = Depends(get_db)) -> ListNotesUseCase:
    return ListNotesUseCase(db)


def get_update_note_use_case(db: AsyncSession = Depends(get_db)) -> UpdateNoteUseCase:
    return UpdateNoteUseCase(db)


def get_delete_note_use_case(db: AsyncSession = Depends(get_db)) -> DeleteNoteUseCase:
    return DeleteNoteUseCase(db)


CreateNoteUseCaseDep = Annotated[CreateNoteUseCase, Depends(get_create_note_use_case)]
GetNoteUseCaseDep = Annotated[GetNoteUseCase, Depends(get_get_note_use_case)]
ListNotesUseCaseDep = Annotated[ListNotesUseCase, Depends(get_list_notes_use_case)]
UpdateNoteUseCaseDep = Annotated[UpdateNoteUseCase, Depends(get_update_note_use_case)]
DeleteNoteUseCaseDep = Annotated[DeleteNoteUseCase, Depends(get_delete_note_use_case)]
