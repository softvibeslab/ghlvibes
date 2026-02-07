"""
Page aggregate root entity.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Any
from uuid import UUID, uuid4

from src.funnels_pages.domain.value_objects import PageType, PageStatus


@dataclass
class PageElement:
    """Page element value object."""
    element_type: str = ""
    id: str = ""
    props: dict = field(default_factory=dict)
    styles: dict = field(default_factory=dict)
    children: List["PageElement"] = field(default_factory=list)


@dataclass
class TrackingScript:
    """Tracking script value object."""
    src: str = ""
    async_: bool = False
    position: Literal["head", "body"] = "head"
    attributes: dict = field(default_factory=dict)


@dataclass
class ResponsiveSettings:
    """Responsive settings value object."""
    mobile: dict = field(default_factory=dict)
    tablet: dict = field(default_factory=dict)


@dataclass
class Page:
    """
    Page aggregate root.

    Invariants:
    - Slug must be unique within account
    - Elements must form valid tree structure
    - Published pages cannot be modified (create new version)
    """
    id: UUID = field(default_factory=uuid4)
    account_id: UUID = None
    funnel_id: Optional[UUID] = None
    name: str = ""
    page_type: PageType = PageType.OPTIN
    slug: str = ""
    status: PageStatus = PageStatus.DRAFT
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    canonical_url: Optional[str] = None
    elements: List[dict] = field(default_factory=list)
    responsive_settings: ResponsiveSettings = field(default_factory=ResponsiveSettings)
    tracking_scripts: List[TrackingScript] = field(default_factory=list)
    custom_head: Optional[str] = None
    custom_body: Optional[str] = None
    published_url: Optional[str] = None
    version: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    last_published_at: Optional[datetime] = None
    created_by: UUID = None
    updated_by: Optional[UUID] = None
    deleted_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate page invariants."""
        if not self.name or len(self.name) < 3 or len(self.name) > 100:
            raise ValueError("Page name must be between 3 and 100 characters")
        if not self.slug or len(self.slug) < 3 or len(self.slug) > 100:
            raise ValueError("Page slug must be between 3 and 100 characters")
        if self.seo_title and len(self.seo_title) > 60:
            raise ValueError("SEO title must be 60 characters or less")
        if self.seo_description and len(self.seo_description) > 160:
            raise ValueError("SEO description must be 160 characters or less")

    def publish(self, base_url: str) -> None:
        """Publish the page."""
        if self.status == PageStatus.PUBLISHED:
            raise ValueError("Page is already published")
        self.status = PageStatus.PUBLISHED
        self.published_at = datetime.utcnow()
        self.last_published_at = datetime.utcnow()
        self.published_url = f"{base_url}/p/{self.slug}"
        self.version += 1
        self.updated_at = datetime.utcnow()

    def unpublish(self) -> None:
        """Unpublish the page."""
        if self.status != PageStatus.PUBLISHED:
            raise ValueError("Page is not published")
        self.status = PageStatus.DRAFT
        self.published_url = None
        self.updated_at = datetime.utcnow()

    def add_element(self, element: dict, parent_id: Optional[str] = None) -> None:
        """Add element to page tree."""
        if parent_id is None:
            self.elements.append(element)
        else:
            parent = self._find_element(self.elements, parent_id)
            if parent:
                if "children" not in parent:
                    parent["children"] = []
                parent["children"].append(element)
        self.updated_at = datetime.utcnow()

    def _find_element(self, elements: List[dict], element_id: str) -> Optional[dict]:
        """Recursively find element by ID."""
        for element in elements:
            if element.get("id") == element_id:
                return element
            if "children" in element:
                found = self._find_element(element["children"], element_id)
                if found:
                    return found
        return None

    def soft_delete(self) -> None:
        """Soft delete the page."""
        self.deleted_at = datetime.utcnow()

    def is_deleted(self) -> bool:
        """Check if page is deleted."""
        return self.deleted_at is not None

    def can_edit(self) -> bool:
        """Check if page can be edited."""
        return self.status == PageStatus.DRAFT and not self.is_deleted()

    def duplicate(self, new_name: str, new_slug: str) -> "Page":
        """Create a copy of the page."""
        import copy
        cloned = copy.copy(self)
        cloned.id = uuid4()
        cloned.name = new_name
        cloned.slug = new_slug
        cloned.status = PageStatus.DRAFT
        cloned.published_url = None
        cloned.published_at = None
        cloned.version = 1
        cloned.created_at = datetime.utcnow()
        cloned.updated_at = datetime.utcnow()
        cloned.elements = copy.deepcopy(self.elements)
        return cloned
