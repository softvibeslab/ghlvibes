"""Use cases for CRM module.

Use cases orchestrate business logic and coordinate domain entities.
They represent application services that implement specific business operations.
"""

from src.crm.application.use_cases.contacts import (
    CreateContactUseCase,
    GetContactUseCase,
    ListContactsUseCase,
    UpdateContactUseCase,
    DeleteContactUseCase,
    BulkImportContactsUseCase,
    AddTagToContactUseCase,
    RemoveTagFromContactUseCase,
)
from src.crm.application.use_cases.companies import (
    CreateCompanyUseCase,
    GetCompanyUseCase,
    ListCompaniesUseCase,
    UpdateCompanyUseCase,
    DeleteCompanyUseCase,
)
from src.crm.application.use_cases.pipelines import (
    CreatePipelineUseCase,
    GetPipelineUseCase,
    ListPipelinesUseCase,
    UpdatePipelineUseCase,
    DeletePipelineUseCase,
)
from src.crm.application.use_cases.deals import (
    CreateDealUseCase,
    GetDealUseCase,
    ListDealsUseCase,
    UpdateDealUseCase,
    DeleteDealUseCase,
    MoveDealStageUseCase,
    WinDealUseCase,
    LoseDealUseCase,
    GetDealForecastUseCase,
)
from src.crm.application.use_cases.activities import (
    CreateActivityUseCase,
    GetActivityUseCase,
    ListActivitiesUseCase,
    UpdateActivityUseCase,
    DeleteActivityUseCase,
    CompleteActivityUseCase,
    StartActivityUseCase,
    CancelActivityUseCase,
)
from src.crm.application.use_cases.notes import (
    CreateNoteUseCase,
    GetNoteUseCase,
    ListNotesUseCase,
    UpdateNoteUseCase,
    DeleteNoteUseCase,
)

__all__ = [
    # Contacts
    "CreateContactUseCase",
    "GetContactUseCase",
    "ListContactsUseCase",
    "UpdateContactUseCase",
    "DeleteContactUseCase",
    "BulkImportContactsUseCase",
    "AddTagToContactUseCase",
    "RemoveTagFromContactUseCase",
    # Companies
    "CreateCompanyUseCase",
    "GetCompanyUseCase",
    "ListCompaniesUseCase",
    "UpdateCompanyUseCase",
    "DeleteCompanyUseCase",
    # Pipelines
    "CreatePipelineUseCase",
    "GetPipelineUseCase",
    "ListPipelinesUseCase",
    "UpdatePipelineUseCase",
    "DeletePipelineUseCase",
    # Deals
    "CreateDealUseCase",
    "GetDealUseCase",
    "ListDealsUseCase",
    "UpdateDealUseCase",
    "DeleteDealUseCase",
    "MoveDealStageUseCase",
    "WinDealUseCase",
    "LoseDealUseCase",
    "GetDealForecastUseCase",
    # Activities
    "CreateActivityUseCase",
    "GetActivityUseCase",
    "ListActivitiesUseCase",
    "UpdateActivityUseCase",
    "DeleteActivityUseCase",
    "CompleteActivityUseCase",
    "StartActivityUseCase",
    "CancelActivityUseCase",
    # Notes
    "CreateNoteUseCase",
    "GetNoteUseCase",
    "ListNotesUseCase",
    "UpdateNoteUseCase",
    "DeleteNoteUseCase",
]
