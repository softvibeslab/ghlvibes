# SPEC-FUN-002: Pages & Elements - Page Builder Backend

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-FUN-002 |
| **Title** | Pages & Elements - Page Builder Backend |
| **Module** | funnels-pages |
| **Domain** | landing-page-builder |
| **Priority** | Critical |
| **Status** | Planned |
| **Created** | 2026-02-07 |
| **Version** | 1.0.0 |

---

## Overview

This specification defines the backend system for the Page Builder module, enabling users to create, manage, and customize funnel pages with drag-and-drop elements, responsive design, and SEO settings.

**Scope:** Complete backend API for landing page management with element library and responsive configurations.

**Target Users:** Marketing teams requiring custom funnel pages without coding.

---

## Environment

### Technical Environment

**Backend Framework:**
- FastAPI 0.115+ with Python 3.13+
- Async/await patterns
- Pydantic v2.9 validation

**Database:**
- PostgreSQL 16+ with JSONB for page content
- SQLAlchemy 2.0 async
- Element library stored as templates

**Storage:**
- S3-compatible storage for images/assets
- CDN integration for page assets

---

## Assumptions

**Assumption 1:** S3-compatible storage available for image uploads.

**Confidence Level:** High

**Evidence Basis:** Project likely uses S3 or MinIO for assets.

**Risk if Wrong:** Image upload functionality fails.

**Validation Method:** Verify S3 credentials on startup.

**Assumption 2:** Page content (JSONB) typically under 500KB per page.

**Confidence Level:** High

**Evidence Basis:** Element-based builders store configuration, not full HTML.

**Risk if Wrong:** Large pages slow down queries.

**Validation Method:** Monitor average page size in production.

---

## EARS Requirements

### REQ-FUN-002-01: Create Page (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/pages with valid page data,
**THEN** the system shall create a new page with unique ID,
**RESULTING IN** 201 status with page object,
**IN STATE** created.

**Request Body:**
```json
{
  "funnel_id": "uuid",
  "name": "string (3-100 chars)",
  "page_type": "optin | sales | checkout | thank_you | webinar | order_form",
  "slug": "string (unique per account)",
  "seo_title": "string (optional, max 60 chars)",
  "seo_description": "string (optional, max 160 chars)",
  "elements": [
    {
      "element_type": "headline | subheadline | text | image | video | button | form | countdown_timer | countdown_evergreen | progressBar | social_proof | testimonial | pricing_table | faq | custom_html | custom_css | divider | spacer | columns",
      "id": "string",
      "props": "object",
      "styles": "object",
      "children": ["array of nested elements"]
    }
  ],
  "responsive_settings": {
    "mobile": "object (element overrides for mobile)",
    "tablet": "object (element overrides for tablet)"
  },
  "tracking_scripts": ["array of script objects"],
  "custom_head": "string (optional HTML)",
  "custom_body": "string (optional HTML)"
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "account_id": "uuid",
  "funnel_id": "uuid",
  "name": "string",
  "page_type": "string",
  "slug": "string",
  "status": "draft | published",
  "seo_title": "string",
  "seo_description": "string",
  "elements": "array",
  "responsive_settings": "object",
  "tracking_scripts": "array",
  "custom_head": "string",
  "custom_body": "string",
  "published_url": "string",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "created_by": "uuid"
}
```

**Acceptance Criteria:**
- Page ID is valid UUID
- Slug unique within account
- Elements validated against element library
- Returns 400 if validation fails
- Returns 409 if slug exists

### REQ-FUN-002-02: List Pages (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/pages with filters,
**THEN** the system shall return paginated list of pages for the account,
**RESULTING IN** 200 status with pages array,
**IN STATE** retrieved.

**Query Parameters:**
- funnel_id: uuid (optional, filter by funnel)
- page_type: string (optional)
- status: string (optional)
- page, page_size, search, sort_by, sort_order

**Response 200:**
```json
{
  "items": ["array of page objects"],
  "total": "integer",
  "page": "integer",
  "page_size": "integer",
  "total_pages": "integer"
}
```

**Acceptance Criteria:**
- Only returns pages for account_id from JWT
- Filters applied server-side
- Pagination metadata accurate

### REQ-FUN-002-03: Get Page Detail (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/pages/{id},
**THEN** the system shall return complete page details with full element tree,
**RESULTING IN** 200 status with full page object,
**IN STATE** retrieved.

**Response 200:**
Includes all fields from create response plus:
```json
{
  "stats": {
    "views": "integer",
    "conversions": "integer",
    "conversion_rate": "decimal"
  },
  "published_at": "ISO8601 or null",
  "last_published_at": "ISO8601 or null"
}
```

**Acceptance Criteria:**
- Returns 404 if page not found
- Returns 403 if different account
- Element tree fully expanded

### REQ-FUN-002-04: Update Page (Event-Driven)

**WHEN** a user submits a PATCH request to /api/v1/pages/{id} with partial data,
**THEN** the system shall update specified fields,
**RESULTING IN** 200 status with updated page object,
**IN STATE** updated.

**Request Body (partial):**
```json
{
  "name": "string",
  "slug": "string",
  "seo_title": "string",
  "seo_description": "string",
  "elements": "array",
  "responsive_settings": "object",
  "tracking_scripts": "array",
  "custom_head": "string",
  "custom_body": "string"
}
```

**Acceptance Criteria:**
- Updated_at set to now
- Returns 404 if not found
- Returns 403 if different account
- Returns 400 if validation fails

### REQ-FUN-002-05: Delete Page (Event-Driven)

**WHEN** a user submits a DELETE request to /api/v1/pages/{id},
**THEN** the system shall soft delete the page,
**RESULTING IN** 204 status with no body,
**IN STATE** deleted.

**Acceptance Criteria:**
- Soft delete (set deleted_at)
- Returns 404 if not found
- Returns 403 if different account
- Cascade to funnel steps referencing page

### REQ-FUN-002-06: Publish Page (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/pages/{id}/publish,
**THEN** the system shall mark page as published and generate published URL,
**RESULTING IN** 200 status with published page object,
**IN STATE** published.

**Acceptance Criteria:**
- Status set to "published"
- published_at set to now
- published_url generated (https://{domain}/p/{slug})
- Page version saved before publish
- Returns 400 if page has validation errors
- Returns 403 if different account

### REQ-FUN-002-07: Unpublish Page (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/pages/{id}/unpublish,
**THEN** the system shall mark page as draft,
**RESULTING IN** 200 status with draft page object,
**IN STATE** unpublished.

**Acceptance Criteria:**
- Status set to "draft"
- published_url cleared
- Returns 404 if not found

### REQ-FUN-002-08: Duplicate Page (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/pages/{id}/duplicate,
**THEN** the system shall create a copy with "- Copy" suffix,
**RESULTING IN** 201 status with duplicated page object,
**IN STATE** duplicated.

**Request Body:**
```json
{
  "name": "string (optional)",
  "slug": "string (optional)"
}
```

**Acceptance Criteria:**
- New page ID
- Elements deep copied
- Assets copied (images, videos)
- Returns 404 if original not found
- Returns 403 if different account

### REQ-FUN-002-09: Upload Page Asset (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/pages/assets with file,
**THEN** the system shall upload file to storage and return URL,
**RESULTING IN** 201 status with asset object,
**IN STATE** uploaded.

**Request:** multipart/form-data with file field

**Response 201:**
```json
{
  "id": "uuid",
  "url": "string",
  "filename": "string",
  "size": "integer (bytes)",
  "content_type": "string",
  "width": "integer (for images)",
  "height": "integer (for images)",
  "uploaded_at": "ISO8601"
}
```

**Acceptance Criteria:**
- File stored in S3
- URL is CDN-accessible
- Image dimensions extracted
- Returns 400 if file too large (max 10MB)
- Returns 400 if invalid file type

### REQ-FUN-002-10: List Element Library (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/pages/elements/library,
**THEN** the system shall return available element types with schemas,
**RESULTING IN** 200 status with element library,
**IN STATE** library_retrieved.

**Response 200:**
```json
{
  "elements": [
    {
      "element_type": "string",
      "category": "basic | advanced | media | form",
      "name": "string",
      "description": "string",
      "icon": "string",
      "default_props": "object",
      "prop_schema": "object (JSON Schema)",
      "style_schema": "object",
      "can_have_children": "boolean",
      "preview_image_url": "string"
    }
  ]
}
```

**Acceptance Criteria:**
- All element types returned
- Schemas valid JSON Schema
- Categories for grouping

### REQ-FUN-002-11: Validate Page Elements (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/pages/validate with elements array,
**THEN** the system shall validate elements against schemas,
**RESULTING IN** 200 status with validation results,
**IN STATE** validated.

**Request Body:**
```json
{
  "elements": ["array of element objects"]
}
```

**Response 200:**
```json
{
  "valid": "boolean",
  "errors": [
    {
      "element_id": "string",
      "field": "string",
      "message": "string"
    }
  ]
}
```

**Acceptance Criteria:**
- All elements validated against schemas
- Returns all validation errors
- Does not save page

### REQ-FUN-002-12: Get Page Preview (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/pages/{id}/preview,
**THEN** the system shall return rendered HTML preview,
**RESULTING IN** 200 status with HTML content,
**IN STATE** preview_generated.

**Query Parameters:**
- device: string (default: desktop, options: mobile, tablet)

**Response 200:**
Content-Type: text/html
Body: Rendered page HTML

**Acceptance Criteria:**
- Elements rendered to HTML
- Responsive styles applied based on device
- Tracking scripts included
- Does not affect page stats

### REQ-FUN-002-13: Update Page SEO (Event-Driven)

**WHEN** a user submits a PATCH request to /api/v1/pages/{id}/seo,
**THEN** the system shall update SEO fields only,
**RESULTING IN** 200 status with updated page object,
**IN STATE** seo_updated.

**Request Body:**
```json
{
  "seo_title": "string (max 60 chars)",
  "seo_description": "string (max 160 chars)",
  "og_title": "string (optional)",
  "og_description": "string (optional)",
  "og_image": "string (optional, URL)",
  "canonical_url": "string (optional)"
}
```

**Acceptance Criteria:**
- Only SEO fields updated
- Character limits enforced
- Returns 400 if exceeds limits

### REQ-FUN-002-14: Get Page Versions (Event-Driven)

**WHEN** a user submits a GET request to /api/v1/pages/{id}/versions,
**THEN** the system shall return list of page versions,
**RESULTING IN** 200 status with versions array,
**IN STATE** versions_retrieved.

**Response 200:**
```json
{
  "items": [
    {
      "version": "integer",
      "created_at": "ISO8601",
      "created_by": "uuid",
      "change_summary": "string"
    }
  ]
}
```

**Acceptance Criteria:**
- Ordered by version descending
- Maximum 50 versions retained
- Older versions auto-deleted

### REQ-FUN-002-15: Restore Page Version (Event-Driven)

**WHEN** a user submits a POST request to /api/v1/pages/{id}/versions/{version}/restore,
**THEN** the system shall restore page to specified version,
**RESULTING IN** 200 status with restored page object,
**IN STATE** version_restored.

**Acceptance Criteria:**
- Creates new version with restored state
- Returns 404 if version not found
- Returns 403 if different account

---

## Technical Specifications

### Database Schema

```sql
-- Pages table
CREATE TABLE pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id),
    funnel_id UUID REFERENCES funnels(id) ON DELETE SET NULL,
    name VARCHAR(100) NOT NULL,
    page_type VARCHAR(20) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    seo_title VARCHAR(60),
    seo_description VARCHAR(160),
    og_title VARCHAR(100),
    og_description VARCHAR(200),
    og_image VARCHAR(500),
    canonical_url VARCHAR(500),
    elements JSONB NOT NULL DEFAULT '[]',
    responsive_settings JSONB NOT NULL DEFAULT '{}',
    tracking_scripts JSONB NOT NULL DEFAULT '[]',
    custom_head TEXT,
    custom_body TEXT,
    published_url VARCHAR(500),
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    last_published_at TIMESTAMPTZ,
    created_by UUID NOT NULL REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    deleted_at TIMESTAMPTZ,
    CONSTRAINT pages_account_slug_unique UNIQUE (account_id, slug, deleted_at)
);

CREATE INDEX idx_pages_account_id ON pages(account_id);
CREATE INDEX idx_pages_funnel_id ON pages(funnel_id);
CREATE INDEX idx_pages_status ON pages(status);
CREATE INDEX idx_pages_deleted_at ON pages(deleted_at);

-- Page assets table
CREATE TABLE page_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id),
    page_id UUID REFERENCES pages(id) ON DELETE SET NULL,
    filename VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    size INTEGER NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    width INTEGER,
    height INTEGER,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    uploaded_by UUID NOT NULL REFERENCES users(id)
);

CREATE INDEX idx_page_assets_account_id ON page_assets(account_id);
CREATE INDEX idx_page_assets_page_id ON page_assets(page_id);

-- Page versions table
CREATE TABLE page_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    page_id UUID NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    page_snapshot JSONB NOT NULL,
    change_summary TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    CONSTRAINT page_versions_page_version_unique UNIQUE (page_id, version)
);

CREATE INDEX idx_page_versions_page_id ON page_versions(page_id);
```

### Element Library Schema

Element Types (25 total):

**Basic Elements (6):**
1. headline - Text heading with typography styles
2. subheadline - Subheading with styles
3. text - Rich text paragraph
4. button - CTA button with styles
5. divider - Horizontal line
6. spacer - Vertical spacing

**Media Elements (4):**
7. image - Image with URL, alt, dimensions
8. video - Embed or hosted video
9. gif - Animated GIF
10. image_gallery - Multiple images carousel

**Form Elements (5):**
11. form - Input form with fields
12. input_field - Single input (text, email, phone)
13. textarea - Multi-line text input
14. dropdown - Select dropdown
15. checkbox_group - Multiple checkboxes

**Advanced Elements (6):**
16. countdown_timer - Fixed date countdown
17. countdown_evergreen - Evergreen timer
18. progress_bar - Goal progress
19. social_proof - Recent activity popup
20. testimonial - Customer testimonial
21. pricing_table - Pricing options

**Layout Elements (4):**
22. columns - Multi-column layout
23. section - Container with background
24. container - Width-limited container
25. row - Horizontal flex container

### API Endpoints Summary

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/pages | Create page |
| GET | /api/v1/pages | List pages |
| GET | /api/v1/pages/{id} | Get page detail |
| PATCH | /api/v1/pages/{id} | Update page |
| DELETE | /api/v1/pages/{id} | Delete page (soft) |
| POST | /api/v1/pages/{id}/publish | Publish page |
| POST | /api/v1/pages/{id}/unpublish | Unpublish page |
| POST | /api/v1/pages/{id}/duplicate | Duplicate page |
| POST | /api/v1/pages/assets | Upload asset |
| GET | /api/v1/pages/elements/library | List element library |
| POST | /api/v1/pages/validate | Validate elements |
| GET | /api/v1/pages/{id}/preview | Get HTML preview |
| PATCH | /api/v1/pages/{id}/seo | Update SEO |
| GET | /api/v1/pages/{id}/versions | List versions |
| POST | /api/v1/pages/{id}/versions/{version}/restore | Restore version |

**Total Endpoints: 15**

---

## Constraints

### Technical Constraints

- Page elements JSONB max 1MB per page
- Asset upload max 10MB per file
- Supported image types: JPG, PNG, GIF, WebP, SVG
- Supported video types: MP4, WebM

### Business Constraints

- Maximum 1000 pages per account
- Page slug: 3-100 chars, alphanumeric with hyphens
- SEO title: max 60 characters
- SEO description: max 160 characters
- Maximum 100 elements per page
- Maximum 6 nesting levels

### Performance Constraints

- List pages: < 500ms
- Get page detail: < 300ms (with element tree)
- Publish page: < 2000ms (includes URL generation)
- Preview generation: < 1000ms

---

## Dependencies

### Internal Dependencies

| Module | Dependency Type | Description |
|--------|-----------------|-------------|
| Funnels Module | Hard | Pages belong to funnels |
| Accounts Module | Hard | Multi-tenancy |
| Storage Service | Hard | Asset uploads |

### External Dependencies

| Service | Purpose |
|---------|---------|
| S3-compatible storage | Asset storage |
| CDN | Asset delivery |

---

## Related SPECs

| SPEC ID | Title | Relationship |
|---------|-------|--------------|
| SPEC-FUN-001 | Funnel Builder | Pages used in funnel steps |
| SPEC-FUN-003 | Orders & Payments | Order form pages |
| SPEC-FUN-004 | Funnel Analytics | Page conversion tracking |

---

## Traceability Tags

- TAG:SPEC-FUN-002
- TAG:MODULE-FUNNELS-PAGES
- TAG:DOMAIN-LANDING-PAGE-BUILDER
- TAG:PRIORITY-CRITICAL
- TAG:API-REST
- TAG:DDD-IMPLEMENTATION
