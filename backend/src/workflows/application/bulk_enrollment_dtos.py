"""DTOs for bulk enrollment operations.

Data Transfer Objects define the contract between application and presentation layers.
"""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ManualSelectionDTO(BaseModel):
    """DTO for manual contact selection."""

    type: Literal["manual"] = "manual"
    contact_ids: list[UUID] = Field(..., min_length=1, max_length=10000)


class FilterSelectionDTO(BaseModel):
    """DTO for filter-based contact selection."""

    type: Literal["filter"] = "filter"
    filter: dict[str, Any] = Field(..., min_length=1)


class CSVSelectionDTO(BaseModel):
    """DTO for CSV-based contact selection."""

    type: Literal["csv"] = "csv"
    file_key: str = Field(..., min_length=1)
    identifier_column: Literal["email", "contact_id"] = "email"


class BulkEnrollmentOptionsDTO(BaseModel):
    """DTO for bulk enrollment options."""

    batch_size: int = Field(default=100, ge=10, le=500)
    skip_duplicates: bool = True
    skip_unsubscribed: bool = True
    scheduled_at: datetime | None = None
    notify_on_completion: bool = True
    notification_email: str | None = None


class CreateBulkJobRequestDTO(BaseModel):
    """DTO for creating a bulk enrollment job."""

    selection: ManualSelectionDTO | FilterSelectionDTO | CSVSelectionDTO
    options: BulkEnrollmentOptionsDTO | None = None


class BulkEnrollmentJobResponseDTO(BaseModel):
    """DTO for bulk enrollment job response."""

    id: UUID
    workflow_id: UUID
    status: str
    selection_type: str
    total_contacts: int
    processed_count: int
    success_count: int
    failure_count: int
    skipped_count: int
    progress_percentage: float
    batch_size: int
    total_batches: int
    completed_batches: int
    scheduled_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    estimated_completion: datetime | None
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime


class BulkEnrollmentProgressDTO(BaseModel):
    """DTO for bulk enrollment progress."""

    job_id: UUID
    status: str
    total_contacts: int
    processed: int
    success: int
    failed: int
    skipped: int
    current_batch: int
    total_batches: int
    progress_percentage: float
    rate: float
    estimated_time_remaining_seconds: int | None


class ListBulkJobsRequestDTO(BaseModel):
    """DTO for listing bulk enrollment jobs."""

    workflow_id: UUID | None = None
    status: str | None = None
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)


class ListBulkJobsResponseDTO(BaseModel):
    """DTO for bulk enrollment job list response."""

    jobs: list[BulkEnrollmentJobResponseDTO]
    total: int
    offset: int
    limit: int


class EnrollmentFailureDTO(BaseModel):
    """DTO for enrollment failure details."""

    contact_id: UUID
    contact_email: str | None
    error_code: str
    error_message: str
    batch_number: int | None
    created_at: datetime


class FailuresResponseDTO(BaseModel):
    """DTO for failures list response."""

    job_id: UUID
    failures: list[EnrollmentFailureDTO]
    total: int
    offset: int
    limit: int


class DryRunRequestDTO(BaseModel):
    """DTO for dry run validation."""

    selection: ManualSelectionDTO | FilterSelectionDTO | CSVSelectionDTO


class DryRunResponseDTO(BaseModel):
    """DTO for dry run results."""

    valid_contacts: int
    duplicates: int
    unsubscribed: int
    not_found: int
    estimated_processing_time_seconds: int
    warnings: list[str]
