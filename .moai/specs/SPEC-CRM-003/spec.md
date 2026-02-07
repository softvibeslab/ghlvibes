# SPEC-CRM-003: Companies

## Overview

Implement company management with hierarchies, domain management, industry classification, and contact-company relationships.

## Requirements (EARS Format)

### 1. Company CRUD Operations

**WHEN** an authenticated user creates a company, **THE SYSTEM** shall store company with required name and optional domain, website, industry, size.

**THE SYSTEM** shall validate domain format and enforce uniqueness globally (domains are unique across all accounts).

**WHEN** updating a company, **THE SYSTEM** shall allow changes to all fields except domain (immutable after creation).

**THE SYSTEM** shall maintain audit trail (created_at, updated_at).

### 2. Company Hierarchies

**WHEN** a company has a parent_company_id, **THE SYSTEM** shall establish parent-child relationship for company hierarchies.

**THE SYSTEM** shall support unlimited hierarchy depth (parent -> child -> grandchild).

**THE SYSTEM** shall prevent circular references (company cannot be its own ancestor).

**WHEN** listing companies, **THE SYSTEM** shall optionally include child companies in response.

### 3. Company Domains

**THE SYSTEM** shall validate domain format (example.com, no protocol, no paths).

**THE SYSTEM** shall store domains in lowercase for uniqueness.

**THE SYSTEM** shall enforce global domain uniqueness (two accounts cannot claim same domain).

**WHEN** domain is provided, **THE SYSTEM** shall attempt to auto-enrich company data (optional feature).

### 4. Company Classification

**THE SYSTEM** shall support industry classification (e.g., Technology, Healthcare, Finance, Manufacturing, Retail).

**THE SYSTEM** shall support company size categories (e.g., "1-10", "11-50", "51-200", "201-500", "501-1000", "1000+").

**WHEN** filtering companies, **THE SYSTEM** shall support filtering by industry and size.

### 5. Contact-Company Relationships

**WHEN** a contact is associated with a company, **THE SYSTEM** shall link via contact.company_id foreign key.

**THE SYSTEM** shall support one-to-many relationship (one company can have many contacts).

**WHEN** listing contacts, **THE SYSTEM** shall support filtering by company_id.

**THE SYSTEM** shall return company name/domain in contact response for context.

### 6. Company Tags

**WHEN** tags are assigned to companies, **THE SYSTEM** shall support multiple tags per company for categorization.

**THE SYSTEM** shall allow filtering companies by tag.

**THE SYSTEM** shall maintain company tag associations (same tag system as contacts).

## API Endpoints

### POST /api/v1/crm/companies
Create a new company.

**Request:**
```json
{
  "name": "Acme Corporation",
  "domain": "acme.com",
  "website": "https://www.acme.com",
  "parent_company_id": "uuid",
  "industry": "Technology",
  "size": "51-200",
  "tag_ids": ["uuid1", "uuid2"]
}
```

**Response:** 201 Created
```json
{
  "id": "uuid",
  "account_id": "uuid",
  "name": "Acme Corporation",
  "domain": "acme.com",
  "website": "https://www.acme.com",
  "parent_company_id": "uuid",
  "industry": "Technology",
  "size": "51-200",
  "tags": ["Enterprise", "Prospect"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### GET /api/v1/crm/companies/{company_id}
Get company by ID.

**Response:** 200 OK with company details

### GET /api/v1/crm/companies
List companies with filters.

**Query Parameters:**
- page: int (default: 1)
- page_size: int (default: 20, max: 100)
- search: string (optional, searches name/domain)
- tag_id: UUID (optional)

**Response:** 200 OK
```json
{
  "items": [...],
  "total": 45,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

### PATCH /api/v1/crm/companies/{company_id}
Update company details.

**Request:**
```json
{
  "name": "Acme Corporation Inc.",
  "website": "https://www.acme.com/new",
  "parent_company_id": "uuid",
  "industry": "Technology",
  "size": "201-500",
  "tag_ids": ["uuid1", "uuid3"]
}
```

**Response:** 200 OK with updated company

### DELETE /api/v1/crm/companies/{company_id}
Delete company.

**Response:** 204 No Content

## Database Schema

### crm_companies table

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| account_id | UUID | FK, NOT NULL, indexed |
| name | VARCHAR(255) | NOT NULL |
| domain | VARCHAR(255) | UNIQUE, nullable |
| website | VARCHAR(500) | nullable |
| parent_company_id | UUID | FK to crm_companies |
| industry | VARCHAR(100) | nullable |
| size | VARCHAR(50) | nullable |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

**Indexes:**
- ix_crm_companies_account_id
- ix_crm_companies_domain (unique)
- ix_crm_companies_name

**Relationships:**
- parent_company: self-referential FK to crm_companies.id
- child_companies: reverse relationship
- contacts: One-to-many to crm_contacts

### crm_company_tags association table

| Column | Type | Constraints |
|--------|------|-------------|
| company_id | UUID | FK, PK |
| tag_id | UUID | FK, PK |
| created_at | TIMESTAMPTZ | NOT NULL |

## Acceptance Criteria

**AC1:** User can create company with required name and optional fields.

**AC2:** Domain validation accepts valid format (example.com) and enforces global uniqueness.

**AC3:** Parent company establishes hierarchy relationship.

**AC4:** Circular reference prevention (company cannot be ancestor of itself).

**AC5:** Industry and size fields support filtering and classification.

**AC6:** Contacts can be associated with companies via company_id.

**AC7:** Company tags work same way as contact tags (shared tags table).

**AC8:** Search supports name and domain partial matching.

**AC9:** Domain is immutable after creation (cannot update via PATCH).

**AC10:** Account isolation enforced in all company queries.

## Testing Strategy

**Unit Tests:**
- Company entity creation and validation
- Domain format validation
- Hierarchy circular reference detection

**Integration Tests:**
- Company CRUD with database
- Parent-child relationships
- Domain uniqueness enforcement

**E2E Tests:**
- Create company with parent
- Update company fields (except domain)
- Filter companies by industry/size

**Test Coverage Target:** 85%+

## Dependencies

**Dependencies:**
- SPEC-CRM-001 (Contacts - contacts linked to companies)

**Dependent Modules:**
- SPEC-CRM-002 (Pipelines & Deals - deals linked to companies)
- SPEC-CRM-004 (Activities/Tasks - activities linked to companies)
- SPEC-CRM-005 (Notes - notes linked to companies)

## Technical Notes

**Performance Considerations:**
- Index domain for uniqueness lookups
- Use recursive CTE for hierarchy queries
- Cache company hierarchies for 10 minutes

**Business Logic:**
- Domain validation regex: `^[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,}$`
- Industry values: Technology, Healthcare, Finance, Manufacturing, Retail, Education, Government, Other
- Size values: 1-10, 11-50, 51-200, 201-500, 501-1000, 1000+

**Future Enhancements:**
- Company enrichment from Clearbit/API
- Company logo fetching from domain
- Company hierarchy visualization
- Company similarity matching
