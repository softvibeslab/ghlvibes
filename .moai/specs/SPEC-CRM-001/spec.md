# SPEC-CRM-001: Contacts Management

## Overview

Implement comprehensive contact management system for the CRM module with CRUD operations, custom fields, tag management, search/filtering, and bulk import/export capabilities.

## Requirements (EARS Format)

### 1. Contact CRUD Operations

**WHEN** an authenticated user creates a contact, **THE SYSTEM** shall store the contact with required fields (first name, last name) and optional fields (email, phone, company).

**WHEN** an authenticated user updates a contact, **THE SYSTEM** shall apply changes to editable fields and maintain audit trail (updated_at, updated_by).

**WHEN** an authenticated user deletes a contact, **THE SYSTEM** shall soft-delete or permanently remove the contact based on retention policy.

**WHEN** retrieving a contact, **THE SYSTEM** shall return all contact fields including associated tags and custom fields.

### 2. Contact Fields and Validation

**THE SYSTEM** shall require first_name (1-100 characters) and last_name (0-100 characters).

**THE SYSTEM** shall validate email format if provided (RFC 5322 compliant, unique per account).

**THE SYSTEM** shall validate phone number format if provided (E.164 format support, 10-15 digits).

**THE SYSTEM** shall support custom fields with flexible JSON schema (string, number, boolean, date, list).

**THE SYSTEM** shall enforce account isolation (contacts scoped to account_id).

### 3. Tag Management

**WHEN** an authenticated user assigns tags to a contact, **THE SYSTEM** shall associate multiple tags with the contact for categorization.

**WHEN** tags are assigned, **THE SYSTEM** shall maintain tag names (unique per account) and optional color codes.

**WHEN** filtering contacts by tag, **THE SYSTEM** shall return contacts with specified tag.

**THE SYSTEM** shall support adding/removing individual tags from contacts.

### 4. Search and Filtering

**WHEN** searching contacts, **THE SYSTEM** shall support full-text search across first_name, last_name, and email fields.

**WHEN** filtering contacts, **THE SYSTEM** shall support filters by tag, company, and custom field values.

**THE SYSTEM** shall return paginated results (default 20 per page, max 100).

**THE SYSTEM** shall support sorting by created_at, updated_at, first_name, last_name.

### 5. Bulk Operations

**WHEN** importing contacts in bulk, **THE SYSTEM** shall process up to 1000 contacts per request and return success/failure counts.

**THE SYSTEM** shall validate each contact in bulk import and continue processing on individual failures.

**THE SYSTEM** shall provide detailed error reporting for failed imports (index, email, error message).

**WHEN** exporting contacts, **THE SYSTEM** shall support CSV and JSON formats with all fields.

### 6. Company Association

**WHEN** a contact is associated with a company, **THE SYSTEM** shall link via company_id foreign key.

**WHEN** listing contacts, **THE SYSTEM** shall support filtering by company_id.

**THE SYSTEM** shall return company details (name, domain) in contact response.

## API Endpoints

### POST /api/v1/crm/contacts
Create a new contact.

**Request:**
```json
{
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+14155551234",
  "company_id": "uuid",
  "custom_fields": {
    "linkedin": "https://linkedin.com/in/johndoe",
    "source": "website"
  },
  "tag_ids": ["uuid1", "uuid2"]
}
```

**Response:** 201 Created
```json
{
  "id": "uuid",
  "account_id": "uuid",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+14155551234",
  "company_id": "uuid",
  "custom_fields": {},
  "tags": ["VIP", "Lead"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "created_by": "uuid"
}
```

### GET /api/v1/crm/contacts/{contact_id}
Retrieve a specific contact.

**Response:** 200 OK
```json
{
  "id": "uuid",
  "account_id": "uuid",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+14155551234",
  "company_id": "uuid",
  "custom_fields": {},
  "tags": ["VIP"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "created_by": "uuid"
}
```

### GET /api/v1/crm/contacts
List contacts with filters.

**Query Parameters:**
- page: int (default: 1)
- page_size: int (default: 20, max: 100)
- search: string (optional, searches name/email)
- tag_id: UUID (optional)
- company_id: UUID (optional)

**Response:** 200 OK
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

### PATCH /api/v1/crm/contacts/{contact_id}
Update contact details.

**Request:**
```json
{
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+14155551235",
  "company_id": "uuid",
  "custom_fields": {
    "source": "referral"
  },
  "tag_ids": ["uuid1", "uuid3"]
}
```

**Response:** 200 OK with updated contact

### DELETE /api/v1/crm/contacts/{contact_id}
Delete a contact.

**Response:** 204 No Content

### POST /api/v1/crm/contacts/bulk-import
Bulk import contacts.

**Request:**
```json
{
  "contacts": [
    {
      "email": "contact1@example.com",
      "first_name": "Jane",
      "last_name": "Smith"
    },
    {
      "email": "contact2@example.com",
      "first_name": "Bob",
      "last_name": "Jones"
    }
  ]
}
```

**Response:** 200 OK
```json
{
  "imported": 195,
  "failed": 5,
  "errors": [
    {
      "index": 5,
      "email": "invalid-email",
      "error": "Invalid email format"
    }
  ]
}
```

## Database Schema

### crm_contacts table

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| account_id | UUID | FK, NOT NULL, indexed |
| email | VARCHAR(255) | UNIQUE, nullable |
| first_name | VARCHAR(100) | NOT NULL |
| last_name | VARCHAR(100) | NOT NULL |
| phone | VARCHAR(20) | nullable |
| phone_country_code | VARCHAR(5) | nullable |
| company_id | UUID | FK to crm_companies |
| custom_fields | JSONB | default {} |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |
| created_by | UUID | FK to users |

**Indexes:**
- idx_crm_contacts_account_id
- idx_crm_contacts_email
- idx_crm_contacts_full_name (first_name, last_name)

### crm_contact_tags association table

| Column | Type | Constraints |
|--------|------|-------------|
| contact_id | UUID | FK, PK |
| tag_id | UUID | FK, PK |
| created_at | TIMESTAMPTZ | NOT NULL |

## Acceptance Criteria

**AC1:** User can create contact with required fields (first_name, last_name) and optional email.

**AC2:** Email validation prevents duplicate emails within same account.

**AC3:** Phone number validation accepts E.164 format (+14155551234).

**AC4:** Custom fields support flexible JSON schema for storing additional data.

**AC5:** Tags can be assigned to multiple contacts for categorization.

**AC6:** Search returns contacts matching name or email with partial matching.

**AC7:** Filter by tag returns only contacts with specified tag.

**AC8:** Bulk import processes up to 1000 contacts and reports success/failure.

**AC9:** Contact deletion removes contact and tag associations.

**AC10:** Account isolation ensures users can only access their account's contacts.

## Testing Strategy

**Unit Tests:**
- Contact entity creation and validation
- Email and phone value object validation
- Custom field JSON serialization/deserialization

**Integration Tests:**
- Contact CRUD operations with database
- Tag association and removal
- Bulk import with error handling

**E2E Tests:**
- Create contact via API
- Search and filter contacts
- Bulk import flow

**Test Coverage Target:** 85%+

## Dependencies

**Dependencies:**
- None (foundational CRM module)

**Dependent Modules:**
- SPEC-CRM-002 (Pipelines & Deals - contacts linked to deals)
- SPEC-CRM-004 (Activities/Tasks - activities linked to contacts)
- SPEC-CRM-005 (Notes - notes linked to contacts)

## Technical Notes

**Performance Considerations:**
- Index email for unique constraint lookups
- Index account_id for multi-tenant isolation
- Use PostgreSQL GIN index for custom_fields JSONB queries

**Security Considerations:**
- Validate and sanitize custom field inputs
- Rate limit bulk import endpoints
- Enforce account-level isolation in all queries

**Future Enhancements:**
- Contact deduplication algorithm
- Email verification workflow
- Contact enrichment from external APIs
