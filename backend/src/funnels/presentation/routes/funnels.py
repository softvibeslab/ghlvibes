"""
Funnel API routes - SPEC-FUN-001.
14 endpoints for funnel lifecycle management.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, validator

from src.core.dependencies import get_db, get_current_account
from src.funnels.application.use_cases import (
    CreateFunnelUseCase,
    ListFunnelsUseCase,
    GetFunnelUseCase,
    UpdateFunnelUseCase,
    DeleteFunnelUseCase,
    CloneFunnelUseCase,
    AddStepUseCase,
    UpdateStepUseCase,
    DeleteStepUseCase,
    ReorderStepsUseCase,
    ListTemplatesUseCase,
    InstantiateTemplateUseCase,
    GetVersionsUseCase,
    RestoreVersionUseCase,
)

router = APIRouter(prefix="/api/v1/funnels", tags=["Funnels"])


# Request/Response Schemas
class FunnelStepCreate(BaseModel):
    step_type: str = Field(..., regex="^(page|upsell|downsell|order_bump|thank_you)$")
    name: str = Field(..., min_length=3, max_length=100)
    order: int
    page_id: UUID | None = None
    config: dict = Field(default_factory=dict)

    @validator('page_id')
    def validate_page_id_for_page_steps(cls, v, values):
        if values.get('step_type') == 'page' and not v:
            raise ValueError('page_id is required for page steps')
        return v


class FunnelCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str | None = Field(None, max_length=1000)
    funnel_type: str = Field(..., regex="^(lead_generation|sales|webinar|booking)$")
    status: str = Field("draft", regex="^(draft|active|archived)$")
    template_id: UUID | None = None
    steps: List[FunnelStepCreate] = Field(default_factory=list)


class FunnelUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=100)
    description: str | None = Field(None, max_length=1000)
    status: str | None = Field(None, regex="^(draft|active|paused|archived)$")
    steps: List[FunnelStepCreate] | None = None


class FunnelResponse(BaseModel):
    id: UUID
    account_id: UUID
    name: str
    description: str | None
    funnel_type: str
    status: str
    version: int
    created_at: str
    updated_at: str
    created_by: UUID
    updated_by: UUID | None
    steps: List[dict]

    class Config:
        from_attributes = True


class FunnelListResponse(BaseModel):
    items: List[FunnelResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Endpoints

@router.post("", response_model=FunnelResponse, status_code=status.HTTP_201_CREATED)
async def create_funnel(
    data: FunnelCreate,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Create a new funnel."""
    use_case = CreateFunnelUseCase(db)
    funnel = await use_case.execute(account_id, data.dict())
    return FunnelResponse(**funnel.to_dict())


@router.get("", response_model=FunnelListResponse)
async def list_funnels(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str | None = None,
    funnel_type: str | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """List funnels with pagination and filters."""
    use_case = ListFunnelsUseCase(db)
    result = await use_case.execute(
        account_id,
        page=page,
        page_size=page_size,
        status_filter=status_filter,
        funnel_type=funnel_type,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return FunnelListResponse(**result)


@router.get("/{funnel_id}", response_model=FunnelResponse)
async def get_funnel(
    funnel_id: UUID,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Get funnel details."""
    use_case = GetFunnelUseCase(db)
    funnel = await use_case.execute(funnel_id, account_id)
    if not funnel:
        raise HTTPException(status_code=404, detail="Funnel not found")
    return FunnelResponse(**funnel.to_dict())


@router.patch("/{funnel_id}", response_model=FunnelResponse)
async def update_funnel(
    funnel_id: UUID,
    data: FunnelUpdate,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Update funnel."""
    use_case = UpdateFunnelUseCase(db)
    funnel = await use_case.execute(funnel_id, account_id, data.dict(exclude_unset=True))
    if not funnel:
        raise HTTPException(status_code=404, detail="Funnel not found")
    return FunnelResponse(**funnel.to_dict())


@router.delete("/{funnel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_funnel(
    funnel_id: UUID,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Delete funnel (soft delete)."""
    use_case = DeleteFunnelUseCase(db)
    success = await use_case.execute(funnel_id, account_id)
    if not success:
        raise HTTPException(status_code=404, detail="Funnel not found")


@router.post("/{funnel_id}/clone", response_model=FunnelResponse, status_code=status.HTTP_201_CREATED)
async def clone_funnel(
    funnel_id: UUID,
    name: str | None = None,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Clone a funnel."""
    use_case = CloneFunnelUseCase(db)
    cloned = await use_case.execute(funnel_id, account_id, name)
    if not cloned:
        raise HTTPException(status_code=404, detail="Funnel not found")
    return FunnelResponse(**cloned.to_dict())


@router.post("/{funnel_id}/steps", status_code=status.HTTP_201_CREATED)
async def add_step(
    funnel_id: UUID,
    step: FunnelStepCreate,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Add a step to the funnel."""
    use_case = AddStepUseCase(db)
    result = await use_case.execute(funnel_id, account_id, step.dict())
    if not result:
        raise HTTPException(status_code=404, detail="Funnel not found")
    return result


@router.patch("/{funnel_id}/steps/{step_id}")
async def update_step(
    funnel_id: UUID,
    step_id: UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Update a funnel step."""
    use_case = UpdateStepUseCase(db)
    result = await use_case.execute(funnel_id, step_id, account_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Step not found")
    return result


@router.delete("/{funnel_id}/steps/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_step(
    funnel_id: UUID,
    step_id: UUID,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Delete a step from the funnel."""
    use_case = DeleteStepUseCase(db)
    success = await use_case.execute(funnel_id, step_id, account_id)
    if not success:
        raise HTTPException(status_code=404, detail="Step not found")


@router.post("/{funnel_id}/steps/reorder")
async def reorder_steps(
    funnel_id: UUID,
    step_orders: dict[UUID, int],
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Reorder funnel steps."""
    use_case = ReorderStepsUseCase(db)
    result = await use_case.execute(funnel_id, account_id, step_orders)
    if not result:
        raise HTTPException(status_code=404, detail="Funnel not found")
    return result


@router.get("/templates", tags=["Funnels"])
async def list_templates(
    category: str | None = None,
    funnel_type: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List funnel templates."""
    use_case = ListTemplatesUseCase(db)
    templates = await use_case.execute(category, funnel_type)
    return templates


@router.post("/templates/{template_id}/instantiate", response_model=FunnelResponse, status_code=status.HTTP_201_CREATED)
async def instantiate_template(
    template_id: UUID,
    name: str = Field(..., min_length=3, max_length=100),
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Create a funnel from a template."""
    use_case = InstantiateTemplateUseCase(db)
    funnel = await use_case.execute(template_id, account_id, name)
    if not funnel:
        raise HTTPException(status_code=404, detail="Template not found")
    return FunnelResponse(**funnel.to_dict())


@router.get("/{funnel_id}/versions")
async def get_versions(
    funnel_id: UUID,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Get funnel version history."""
    use_case = GetVersionsUseCase(db)
    versions = await use_case.execute(funnel_id, account_id)
    if not versions:
        raise HTTPException(status_code=404, detail="Funnel not found")
    return versions


@router.post("/{funnel_id}/versions/{version}/restore")
async def restore_version(
    funnel_id: UUID,
    version: int,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Restore a funnel to a previous version."""
    use_case = RestoreVersionUseCase(db)
    funnel = await use_case.execute(funnel_id, account_id, version)
    if not funnel:
        raise HTTPException(status_code=404, detail="Version not found")
    return FunnelResponse(**funnel.to_dict())
