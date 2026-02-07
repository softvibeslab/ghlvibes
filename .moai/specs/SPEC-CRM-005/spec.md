# SPEC-CRM-005: Notes & Communications

## Overview

Implement comprehensive notes system with communication logging (email, call, SMS), rich text support, note associations, and communication history timeline.

## Requirements (EARS Format)

### 1. Note CRUD Operations

**WHEN** an authenticated user creates a note, **THE SYSTEM** shall store note with required content field and optional note_type.

**THE SYSTEM** shall support note types: note (default), email, call, sms.

**THE SYSTEM** shall associate notes with optional contact, company, or deal.

**THE SYSTEM** shall maintain audit trail (created_by, created_at, updated_at).

### 2. Communication Logging

**WHEN** logging an email communication, **THE SYSTEM** shall store note_type="email" with email metadata in content (subject, body, from, to).

**WHEN** logging a call, **THE SYSTEM** shall store note_type="call" with call details (duration, outcome, notes).

**WHEN** logging an SMS, **THE SYSTEM** shall store note_type="sms" with message content and direction (incoming/outgoing).

**THE SYSTEM** shall parse and structure communication data from JSON content.

### 3. Note Content Validation

**THE SYSTEM** shall require content field (1-10,000 characters).

**THE SYSTEM** shall support plain text and markdown formatting.

**THE SYSTEM** shall sanitize HTML to prevent XSS attacks.

**THE SYSTEM** shall preserve whitespace and line breaks for readability.

### 4. Note Associations

**THE SYSTEM** shall support linking notes to contacts (contact_id).

**THE SYSTEM** shall support linking notes to companies (company_id).

**THE SYSTEM** shall support linking notes to deals (deal_id).

**WHEN** a note is associated with multiple entities, **THE SYSTEM** shall store the primary association and cross-reference others in content.

### 5. Communication History

**WHEN** retrieving communication history for a contact, **THE SYSTEM** shall return notes ordered by created_at descending.

**THE SYSTEM** shall support filtering by note_type (email only, calls only, etc.).

**THE SYSTEM** shall support pagination for large communication histories.

**THE SYSTEM** shall include author information (created_by user name) in response.

### 6. Note Search and Filter

**WHEN** searching notes, **THE SYSTEM** shall support full-text search across content field.

**THE SYSTEM** shall filter notes by note_type, contact_id, company_id, deal_id.

**THE SYSTEM** shall support date range filtering (created_after, created_before).

**THE SYSTEM** shall return search highlights for matching terms.

## API Endpoints

### POST /api/v1/crm/notes
Create a new note.

**Request (General Note):**
```json
{
  "content": "Discussed budget approval. Follow up next week.",
  "note_type": "note",
  "contact_id": "uuid",
  "company_id": "uuid",
  "deal_id": "uuid"
}
```

**Request (Email Log):**
```json
{
  "content": "{\"subject\":\"Proposal Review\",\"from\":\"john@example.com\",\"to\":\"jane@company.com\",\"body\":\"Please review attached proposal...\"}",
  "note_type": "email",
  "contact_id": "uuid"
}
```

**Request (Call Log):**
```json
{
  "content": "{\"duration\":\"15 minutes\",\"outcome\":\"Left voicemail\",\"summary\":\"Discussed Q2 pricing\"}",
  "note_type": "call",
  "contact_id": "uuid"
}
```

**Response:** 201 Created
```json
{
  "id": "uuid",
  "account_id": "uuid",
  "content": "Discussed budget approval. Follow up next week.",
  "note_type": "note",
  "contact_id": "uuid",
  "company_id": "uuid",
  "deal_id": "uuid",
  "created_by": "uuid",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### GET /api/v1/crm/notes/{note_id}
Get note by ID.

### GET /api/v1/crm/notes
List notes with filters.

**Query Parameters:**
- page: int (default: 1)
- page_size: int (default: 20, max: 100)
- note_type: string (optional: note, email, call, sms)
- contact_id: UUID (optional)
- company_id: UUID (optional)
- deal_id: UUID (optional)

**Response:** 200 OK
```json
{
  "items": [...],
  "total": 125,
  "page": 1,
  "page_size": 20,
  "total_pages": 7
}
```

### PATCH /api/v1/crm/notes/{note_id}
Update note content.

**Request:**
```json
{
  "content": "Updated: Discussed budget approval. Follow up next Tuesday."
}
```

**Response:** 200 OK with updated note

### DELETE /api/v1/crm/notes/{note_id}
Delete note.

**Response:** 204 No Content

### GET /api/v1/crm/contacts/{contact_id}/notes
Get communication history for contact.

**Query Parameters:**
- note_type: string (optional filter)
- page: int (default: 1)
- page_size: int (default: 20)

**Response:** 200 OK with chronological notes

## Database Schema

### crm_notes table

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| account_id | UUID | FK, NOT NULL, indexed |
| content | TEXT | NOT NULL, 1-10,000 chars |
| note_type | VARCHAR(50) | NOT NULL, default "note" |
| contact_id | UUID | FK to crm_contacts |
| company_id | UUID | FK to crm_companies |
| deal_id | UUID | FK to crm_deals |
| created_by | UUID | FK to users |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

**Indexes:**
- ix_crm_notes_account_id
- ix_crm_notes_type
- ix_crm_notes_created_at (for ordering)

**Relationships:**
- contact: Many-to-one to crm_contacts
- company: Many-to-one to crm_companies
- deal: Many-to-one to crm_deals
- created_by_user: Many-to-one to users

## Acceptance Criteria

**AC1:** User can create note with required content (1-10,000 characters).

**AC2:** Note types support note, email, call, sms with structured content.

**AC3:** Notes can be associated with contact, company, or deal.

**AC4:** Communication history returns notes in reverse chronological order.

**AC5:** Filter notes by type and association entity.

**AC6:** Search supports full-text search across note content.

**AC7:** Update note modifies content and updated_at timestamp.

**AC8:** Delete note removes record permanently (no soft delete).

**AC9:** Email logging stores structured JSON with subject, from, to, body.

**AC10:** Account isolation enforced in all note queries.

## Testing Strategy

**Unit Tests:**
- Note entity creation and validation
- Content length validation (1-10,000 characters)
- Note type validation

**Integration Tests:**
- Note CRUD with database
- Association with contacts/companies/deals
- Communication history ordering

**E2E Tests:**
- Create general note via API
- Log email communication
- Log call with outcome
- Retrieve communication history

**Test Coverage Target:** 85%+

## Dependencies

**Dependencies:**
- SPEC-CRM-001 (Contacts - notes linked to contacts)
- SPEC-CRM-002 (Pipelines & Deals - notes linked to deals)
- SPEC-CRM-003 (Companies - notes linked to companies)

**Dependent Modules:**
- None (leaf node in dependency graph)

## Technical Notes

**Content Format:**
- Plain text with markdown support
- Sanitize HTML: strip <script>, <iframe>, onclick attributes
- Preserve whitespace: pre-wrap CSS for display
- Max length: 10,000 characters (approximately 1,500 words)

**Communication Logging Patterns:**

Email (JSON in content):
```json
{
  "subject": "Proposal Review",
  "from": "john@example.com",
  "to": ["jane@company.com", "bob@company.com"],
  "cc": ["manager@company.com"],
  "body": "Please review...",
  "timestamp": "2024-01-01T12:00:00Z",
  "email_id": "message-id@example.com"
}
```

Call (JSON in content):
```json
{
  "direction": "outbound",
  "duration_seconds": 900,
  "outcome": "Connected",
  "summary": "Discussed budget",
  "recording_url": "https://..."
}
```

SMS (JSON in content):
```json
{
  "direction": "inbound",
  "from": "+14155551234",
  "to": "+14155555678",
  "message": "Yes, interested in demo",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Search Implementation:**
- PostgreSQL full-text search: `to_tsvector('english', content)`
- GIN index on content for fast search
- Highlight matches: `ts_headline()`

**Future Enhancements:**
- Rich text editor (WYSIWYG)
- File attachments to notes
- Note templates
- Email threading (group related emails)
- Voice-to-text for call notes
- AI-powered call summarization
