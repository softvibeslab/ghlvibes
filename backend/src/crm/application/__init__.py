"""Application layer for CRM module.

Contains use cases, DTOs, and application services.
The application layer orchestrates business logic and coordinates domain objects.
"""

from src.crm.application.dtos import (
    # Contact DTOs (SPEC-CRM-001)
    ContactResponse,
    CreateContactRequest,
    UpdateContactRequest,
    ContactListResponse,
    BulkImportRequest,
    BulkImportResponse,

    # Company DTOs (SPEC-CRM-003)
    CompanyResponse,
    CreateCompanyRequest,
    UpdateCompanyRequest,
    CompanyListResponse,

    # Pipeline/Deal DTOs (SPEC-CRM-002)
    PipelineResponse,
    CreatePipelineRequest,
    PipelineStageResponse,
    DealResponse,
    CreateDealRequest,
    UpdateDealRequest,
    DealListResponse,
    DealForecastResponse,

    # Activity DTOs (SPEC-CRM-004)
    ActivityResponse,
    CreateActivityRequest,
    UpdateActivityRequest,
    ActivityListResponse,

    # Note DTOs (SPEC-CRM-005)
    NoteResponse,
    CreateNoteRequest,
    UpdateNoteRequest,
    NoteListResponse,

    # Common
    ErrorResponse,
    PaginationParams,
)

__all__ = [
    # Contact DTOs
    "ContactResponse",
    "CreateContactRequest",
    "UpdateContactRequest",
    "ContactListResponse",
    "BulkImportRequest",
    "BulkImportResponse",
    # Company DTOs
    "CompanyResponse",
    "CreateCompanyRequest",
    "UpdateCompanyRequest",
    "CompanyListResponse",
    # Pipeline/Deal DTOs
    "PipelineResponse",
    "CreatePipelineRequest",
    "PipelineStageResponse",
    "DealResponse",
    "CreateDealRequest",
    "UpdateDealRequest",
    "DealListResponse",
    "DealForecastResponse",
    # Activity DTOs
    "ActivityResponse",
    "CreateActivityRequest",
    "UpdateActivityRequest",
    "ActivityListResponse",
    # Note DTOs
    "NoteResponse",
    "CreateNoteRequest",
    "UpdateNoteRequest",
    "NoteListResponse",
    # Common
    "ErrorResponse",
    "PaginationParams",
]
