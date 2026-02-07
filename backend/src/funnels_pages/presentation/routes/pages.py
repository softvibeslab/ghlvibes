"""
Pages API routes - SPEC-FUN-002.
15 endpoints for page management.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from src.core.dependencies import get_db, get_current_account
from src.funnels_pages.application.use_cases import (
    CreatePageUseCase,
    ListPagesUseCase,
    GetPageUseCase,
    UpdatePageUseCase,
    DeletePageUseCase,
    PublishPageUseCase,
    UnpublishPageUseCase,
    DuplicatePageUseCase,
    UploadAssetUseCase,
    ListElementLibraryUseCase,
    ValidateElementsUseCase,
    GetPagePreviewUseCase,
    UpdatePageSEOUseCase,
    GetPageVersionsUseCase,
    RestorePageVersionUseCase,
)

router = APIRouter(prefix="/api/v1/pages", tags=["Pages"])


class PageCreate(BaseModel):
    funnel_id: UUID
    name: str = Field(..., min_length=3, max_length=100)
    page_type: str = Field(..., regex="^(optin|sales|checkout|thank_you|webinar|order_form)$")
    slug: str = Field(..., min_length=3, max_length=100)
    seo_title: str | None = Field(None, max_length=60)
    seo_description: str | None = Field(None, max_length=160)
    elements: List[dict] = Field(default_factory=list)
    responsive_settings: dict = Field(default_factory=dict)
    tracking_scripts: List[dict] = Field(default_factory=list)
    custom_head: str | None = None
    custom_body: str | None = None


class PageResponse(BaseModel):
    id: UUID
    account_id: UUID
    funnel_id: UUID | None
    name: str
    page_type: str
    slug: str
    status: str
    seo_title: str | None
    seo_description: str | None
    published_url: str | None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.post("", response_model=PageResponse, status_code=status.HTTP_201_CREATED)
async def create_page(
    data: PageCreate,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Create a new page."""
    use_case = CreatePageUseCase(db)
    page = await use_case.execute(account_id, data.dict())
    return PageResponse(**page.to_dict())


@router.get("")
async def list_pages(
    funnel_id: UUID | None = None,
    page_type: str | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """List pages with pagination."""
    use_case = ListPagesUseCase(db)
    result = await use_case.execute(account_id, funnel_id, page_type, status, page, page_size)
    return result


@router.get("/{page_id}", response_model=PageResponse)
async def get_page(
    page_id: UUID,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Get page details."""
    use_case = GetPageUseCase(db)
    page = await use_case.execute(page_id, account_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return PageResponse(**page.to_dict())


@router.patch("/{page_id}", response_model=PageResponse)
async def update_page(
    page_id: UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Update page."""
    use_case = UpdatePageUseCase(db)
    page = await use_case.execute(page_id, account_id, data)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return PageResponse(**page.to_dict())


@router.delete("/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_page(
    page_id: UUID,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Delete page (soft delete)."""
    use_case = DeletePageUseCase(db)
    success = await use_case.execute(page_id, account_id)
    if not success:
        raise HTTPException(status_code=404, detail="Page not found")


@router.post("/{page_id}/publish")
async def publish_page(
    page_id: UUID,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Publish page."""
    use_case = PublishPageUseCase(db)
    page = await use_case.execute(page_id, account_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return PageResponse(**page.to_dict())


@router.post("/{page_id}/unpublish")
async def unpublish_page(
    page_id: UUID,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Unpublish page."""
    use_case = UnpublishPageUseCase(db)
    page = await use_case.execute(page_id, account_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return PageResponse(**page.to_dict())


@router.post("/{page_id}/duplicate")
async def duplicate_page(
    page_id: UUID,
    name: str | None = None,
    slug: str | None = None,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Duplicate page."""
    use_case = DuplicatePageUseCase(db)
    page = await use_case.execute(page_id, account_id, name, slug)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return PageResponse(**page.to_dict())


@router.post("/assets")
async def upload_asset(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Upload page asset."""
    use_case = UploadAssetUseCase(db)
    asset = await use_case.execute(account_id, file)
    return asset


@router.get("/elements/library")
async def list_element_library(
    db: AsyncSession = Depends(get_db),
):
    """List available element types."""
    use_case = ListElementLibraryUseCase(db)
    return await use_case.execute()


@router.post("/validate")
async def validate_elements(
    elements: List[dict],
    db: AsyncSession = Depends(get_db),
):
    """Validate page elements."""
    use_case = ValidateElementsUseCase(db)
    return await use_case.execute(elements)


@router.get("/{page_id}/preview")
async def get_page_preview(
    page_id: UUID,
    device: str = "desktop",
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Get HTML preview of page."""
    use_case = GetPagePreviewUseCase(db)
    html = await use_case.execute(page_id, account_id, device)
    if not html:
        raise HTTPException(status_code=404, detail="Page not found")
    return html


@router.patch("/{page_id}/seo")
async def update_page_seo(
    page_id: UUID,
    seo_title: str | None = None,
    seo_description: str | None = None,
    og_title: str | None = None,
    og_description: str | None = None,
    og_image: str | None = None,
    canonical_url: str | None = None,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Update page SEO settings."""
    use_case = UpdatePageSEOUseCase(db)
    page = await use_case.execute(page_id, account_id, {
        "seo_title": seo_title,
        "seo_description": seo_description,
        "og_title": og_title,
        "og_description": og_description,
        "og_image": og_image,
        "canonical_url": canonical_url,
    })
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return PageResponse(**page.to_dict())


@router.get("/{page_id}/versions")
async def get_page_versions(
    page_id: UUID,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Get page version history."""
    use_case = GetPageVersionsUseCase(db)
    versions = await use_case.execute(page_id, account_id)
    if not versions:
        raise HTTPException(status_code=404, detail="Page not found")
    return versions


@router.post("/{page_id}/versions/{version}/restore")
async def restore_page_version(
    page_id: UUID,
    version: int,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Restore page to a previous version."""
    use_case = RestorePageVersionUseCase(db)
    page = await use_case.execute(page_id, account_id, version)
    if not page:
        raise HTTPException(status_code=404, detail="Version not found")
    return PageResponse(**page.to_dict())
