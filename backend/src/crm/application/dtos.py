"""Data Transfer Objects (DTOs) for CRM module.

DTOs define the API contract between the presentation and application layers.
They include request/response models with Pydantic validation.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.crm.domain.value_objects import ActivityStatus, ActivityType, DealStatus


# ============================================================================
# Common DTOs
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: dict[str, Any] | None = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")

    model_config = ConfigDict(from_attributes=True)


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.page_size


# ============================================================================
# Contact DTOs (SPEC-CRM-001)
# ============================================================================

class ContactResponse(BaseModel):
    """Contact response model."""

    id: UUID
    account_id: UUID
    email: str | None
    first_name: str
    last_name: str
    phone: str | None
    phone_country_code: str | None
    company_id: UUID | None
    custom_fields: dict[str, Any]
    tags: list[str] = Field(default_factory=list, description="Tag names")
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None

    model_config = ConfigDict(from_attributes=True)


class CreateContactRequest(BaseModel):
    """Create contact request."""

    email: str | None = Field(None, max_length=255, description="Email address")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., max_length=100, description="Last name")
    phone: str | None = Field(None, max_length=20, description="Phone number")
    phone_country_code: str | None = Field(None, max_length=5, description="Phone country code")
    company_id: UUID | None = Field(None, description="Associated company ID")
    custom_fields: dict[str, Any] = Field(default_factory=dict, description="Custom field values")
    tag_ids: list[UUID] = Field(default_factory=list, description="Tag IDs to assign")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        """Validate email format."""
        if v and "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower().strip() if v else None


class UpdateContactRequest(BaseModel):
    """Update contact request."""

    email: str | None = Field(None, max_length=255)
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=20)
    phone_country_code: str | None = Field(None, max_length=5)
    company_id: UUID | None = Field(None)
    custom_fields: dict[str, Any] | None = Field(None)
    tag_ids: list[UUID] | None = Field(None)


class ContactListResponse(BaseModel):
    """Contact list response with pagination."""

    items: list[ContactResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class BulkImportRequest(BaseModel):
    """Bulk import contacts request."""

    contacts: list[CreateContactRequest] = Field(..., min_length=1, max_length=1000)


class BulkImportResponse(BaseModel):
    """Bulk import response."""

    imported: int
    failed: int
    errors: list[dict[str, Any]] = Field(default_factory=list)


# ============================================================================
# Company DTOs (SPEC-CRM-003)
# ============================================================================

class CompanyResponse(BaseModel):
    """Company response model."""

    id: UUID
    account_id: UUID
    name: str
    domain: str | None
    website: str | None
    parent_company_id: UUID | None
    industry: str | None
    size: str | None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CreateCompanyRequest(BaseModel):
    """Create company request."""

    name: str = Field(..., min_length=1, max_length=255)
    domain: str | None = Field(None, max_length=255)
    website: str | None = Field(None, max_length=500)
    parent_company_id: UUID | None = Field(None)
    industry: str | None = Field(None, max_length=100)
    size: str | None = Field(None, max_length=50)
    tag_ids: list[UUID] = Field(default_factory=list)


class UpdateCompanyRequest(BaseModel):
    """Update company request."""

    name: str | None = Field(None, min_length=1, max_length=255)
    domain: str | None = Field(None, max_length=255)
    website: str | None = Field(None, max_length=500)
    parent_company_id: UUID | None = Field(None)
    industry: str | None = Field(None, max_length=100)
    size: str | None = Field(None, max_length=50)
    tag_ids: list[UUID] | None = Field(None)


class CompanyListResponse(BaseModel):
    """Company list response."""

    items: list[CompanyResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# Pipeline/Deal DTOs (SPEC-CRM-002)
# ============================================================================

class PipelineStageResponse(BaseModel):
    """Pipeline stage response."""

    id: UUID
    pipeline_id: UUID
    name: str
    order: int
    probability: int
    display_color: str | None

    model_config = ConfigDict(from_attributes=True)


class PipelineResponse(BaseModel):
    """Pipeline response."""

    id: UUID
    account_id: UUID
    name: str
    is_active: bool
    stages: list[PipelineStageResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CreatePipelineRequest(BaseModel):
    """Create pipeline request."""

    name: str = Field(..., min_length=1, max_length=100)
    stages: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Stage definitions with name, order, probability"
    )


class DealResponse(BaseModel):
    """Deal response."""

    id: UUID
    account_id: UUID
    pipeline_id: UUID
    stage_id: UUID
    name: str
    value_amount: int
    value_currency: str
    contact_id: UUID | None
    company_id: UUID | None
    status: DealStatus
    expected_close_date: datetime | None
    actual_close_date: datetime | None
    probability: int
    notes: str | None
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None

    model_config = ConfigDict(from_attributes=True)

    @property
    def value_decimal(self) -> float:
        """Return deal value as decimal."""
        return self.value_amount / 100.0


class CreateDealRequest(BaseModel):
    """Create deal request."""

    pipeline_id: UUID
    stage_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    value: float = Field(..., ge=0, description="Deal value")
    contact_id: UUID | None = Field(None)
    company_id: UUID | None = Field(None)
    expected_close_date: datetime | None = Field(None)
    probability: int = Field(50, ge=0, le=100)
    notes: str | None = Field(None, max_length=5000)


class UpdateDealRequest(BaseModel):
    """Update deal request."""

    name: str | None = Field(None, min_length=1, max_length=255)
    value: float | None = Field(None, ge=0)
    stage_id: UUID | None = Field(None)
    expected_close_date: datetime | None = Field(None)
    probability: int | None = Field(None, ge=0, le=100)
    notes: str | None = Field(None, max_length=5000)


class DealListResponse(BaseModel):
    """Deal list response."""

    items: list[DealResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class DealForecastResponse(BaseModel):
    """Deal forecast response."""

    total_value: float
    weighted_value: float
    won_value: float
    lost_value: float
    open_deals: int
    won_deals: int
    lost_deals: int


# ============================================================================
# Activity DTOs (SPEC-CRM-004)
# ============================================================================

class ActivityResponse(BaseModel):
    """Activity response."""

    id: UUID
    account_id: UUID
    activity_type: ActivityType
    title: str
    description: str | None
    status: ActivityStatus
    due_date: datetime | None
    completed_at: datetime | None
    contact_id: UUID | None
    company_id: UUID | None
    deal_id: UUID | None
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CreateActivityRequest(BaseModel):
    """Create activity request."""

    activity_type: ActivityType
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None)
    due_date: datetime | None = Field(None)
    contact_id: UUID | None = Field(None)
    company_id: UUID | None = Field(None)
    deal_id: UUID | None = Field(None)


class UpdateActivityRequest(BaseModel):
    """Update activity request."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None)
    due_date: datetime | None = Field(None)
    status: ActivityStatus | None = Field(None)


class ActivityListResponse(BaseModel):
    """Activity list response."""

    items: list[ActivityResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# Note DTOs (SPEC-CRM-005)
# ============================================================================

class NoteResponse(BaseModel):
    """Note response."""

    id: UUID
    account_id: UUID
    content: str
    note_type: str
    contact_id: UUID | None
    company_id: UUID | None
    deal_id: UUID | None
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CreateNoteRequest(BaseModel):
    """Create note request."""

    content: str = Field(..., min_length=1, max_length=10000)
    note_type: str = Field("note", max_length=50)
    contact_id: UUID | None = Field(None)
    company_id: UUID | None = Field(None)
    deal_id: UUID | None = Field(None)


class UpdateNoteRequest(BaseModel):
    """Update note request."""

    content: str = Field(..., min_length=1, max_length=10000)


class NoteListResponse(BaseModel):
    """Note list response."""

    items: list[NoteResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
