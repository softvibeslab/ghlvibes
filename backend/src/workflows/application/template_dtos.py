"""DTOs for workflow template operations.

Data Transfer Objects define the contract between application and presentation layers.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class TemplateMetadataDTO(BaseModel):
    """DTO for template metadata."""

    required_integrations: list[str]
    tags: list[str]
    estimated_completion_rate: float | None = None
    is_system_template: bool = False
    is_shared: bool = False


class CreateTemplateRequestDTO(BaseModel):
    """DTO for creating a workflow template."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=1000)
    category: str = Field(..., min_length=1)
    workflow_config: dict[str, Any] = Field(..., min_length=1)
    required_integrations: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    estimated_completion_rate: float | None = Field(None, ge=0, le=100)
    is_shared: bool = False


class UpdateTemplateRequestDTO(BaseModel):
    """DTO for updating a workflow template."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, min_length=1, max_length=1000)
    category: str | None = None
    workflow_config: dict[str, Any] | None = None
    tags: list[str] | None = None
    required_integrations: list[str] | None = None
    estimated_completion_rate: float | None = Field(None, ge=0, le=100)
    is_shared: bool | None = None


class TemplateResponseDTO(BaseModel):
    """DTO for workflow template response."""

    id: UUID
    account_id: UUID | None
    name: str
    description: str
    category: str
    metadata: TemplateMetadataDTO
    workflow_config: dict[str, Any]
    version: int
    usage_count: int
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None


class ListTemplatesRequestDTO(BaseModel):
    """DTO for listing workflow templates with filters."""

    category: str | None = None
    is_system_template: bool | None = None
    search: str | None = None
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)


class ListTemplatesResponseDTO(BaseModel):
    """DTO for workflow template list response."""

    templates: list[TemplateResponseDTO]
    total: int
    offset: int
    limit: int


class InstantiateTemplateRequestDTO(BaseModel):
    """DTO for instantiating a template to a workflow."""

    workflow_name: str = Field(..., min_length=1, max_length=255)
    workflow_description: str | None = Field(None, max_length=1000)


class TemplateUsageResponseDTO(BaseModel):
    """DTO for template usage tracking."""

    id: UUID
    template_id: UUID
    workflow_id: UUID
    account_id: UUID
    cloned_at: datetime
    template_version: int
