# SPEC-WFL-012: Workflow Versioning - Implementation Plan

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-012 |
| **Title** | Workflow Versioning |
| **Module** | workflows |
| **Domain** | automation |
| **Priority** | Low |
| **Created** | 2026-01-26 |

---

## Implementation Overview

This plan outlines the implementation strategy for workflow versioning, enabling users to modify active workflows while maintaining execution continuity for contacts on previous versions.

---

## Milestone 1: Database Schema and Core Entities

**Priority:** Primary Goal

### Objectives

- Create workflow_versions table with all required fields
- Create workflow_version_migrations table for migration tracking
- Create workflow_version_drafts table for auto-save functionality
- Create workflow_version_audit_logs table for compliance
- Implement Row Level Security policies
- Create necessary indexes for performance

### Tasks

1. **Database Migration: workflow_versions table**
   - Create migration file with schema
   - Add unique constraints and check constraints
   - Create indexes for workflow_id, status, is_current
   - Implement partial unique index for current version

2. **Database Migration: workflow_version_migrations table**
   - Create migration file with schema
   - Add foreign key references to workflow_versions
   - Create indexes for status and workflow_id

3. **Database Migration: workflow_version_drafts table**
   - Create migration file with schema
   - Add unique constraint per workflow per user
   - Create index for last_saved_at for cleanup

4. **Database Migration: workflow_version_audit_logs table**
   - Create migration file with schema
   - Create indexes for workflow_id, version_id, action

5. **SQLAlchemy Models**
   - Create WorkflowVersion model with all fields
   - Create WorkflowVersionMigration model
   - Create WorkflowVersionDraft model
   - Create WorkflowVersionAuditLog model
   - Add relationships between models

### Dependencies

- Existing workflows table (SPEC-WFL-001)
- Supabase PostgreSQL connection

### Technical Approach

- Use Alembic for database migrations
- Implement optimistic locking with lock_version column
- Use JSONB for flexible storage of actions, conditions, and configs

---

## Milestone 2: Version CRUD Operations

**Priority:** Primary Goal

### Objectives

- Implement version creation from existing workflow
- Implement version listing with pagination
- Implement version retrieval by ID or version number
- Implement version update (draft versions only)
- Implement version deletion (draft versions only)

### Tasks

1. **WorkflowVersionRepository**
   - Create async repository with CRUD operations
   - Implement get_current_version method
   - Implement get_by_version_number method
   - Implement list_versions with pagination
   - Implement create_version_from_current
   - Add optimistic locking support

2. **CreateVersionUseCase**
   - Validate user has workflows:edit permission
   - Check version limit (max 1000)
   - Copy current version state to new version
   - Assign next version number
   - Log creation in audit table

3. **UpdateVersionUseCase**
   - Validate version is in draft status
   - Validate optimistic lock version
   - Update version data
   - Log changes in audit table

4. **DeleteVersionUseCase**
   - Validate version is in draft status
   - Validate version is not current
   - Soft delete version record
   - Log deletion in audit table

5. **FastAPI Routes**
   - POST /api/v1/workflows/{workflow_id}/versions
   - GET /api/v1/workflows/{workflow_id}/versions
   - GET /api/v1/workflows/{workflow_id}/versions/{version_id}
   - PATCH /api/v1/workflows/{workflow_id}/versions/{version_id}
   - DELETE /api/v1/workflows/{workflow_id}/versions/{version_id}

### Dependencies

- Milestone 1 (Database Schema)
- Clerk authentication middleware
- RBAC permission system

### Technical Approach

- Use Pydantic v2 for request/response validation
- Implement cursor-based pagination
- Use dependency injection for repository

---

## Milestone 3: Version Publishing and Rollback

**Priority:** Primary Goal

### Objectives

- Implement version publishing (activating a draft)
- Implement version rollback to previous version
- Handle current version flag management
- Ensure only one current version at a time

### Tasks

1. **PublishVersionUseCase**
   - Validate version is in draft status
   - Validate workflow structure is complete
   - Begin transaction
   - Set previous current version to non-current
   - Set new version as current and active
   - Update workflow's main version reference
   - Commit transaction
   - Log publish action

2. **RollbackVersionUseCase**
   - Validate target version exists and is not archived
   - Validate user has workflows:admin permission
   - Begin transaction
   - Set current version to non-current
   - Create new version from target (preserves history)
   - Set new version as current
   - Commit transaction
   - Log rollback action

3. **Version Status Management**
   - Implement status transition validation
   - draft -> active (publish)
   - active -> archived (auto-archive)
   - Prevent invalid transitions

4. **FastAPI Routes**
   - POST /api/v1/workflows/{workflow_id}/versions/{version_id}/publish
   - POST /api/v1/workflows/{workflow_id}/versions/{version_id}/rollback

### Dependencies

- Milestone 2 (Version CRUD)
- Transaction management

### Technical Approach

- Use database transactions for atomic operations
- Implement state machine pattern for status transitions
- Add validation middleware for workflow completeness

---

## Milestone 4: Version Comparison

**Priority:** Secondary Goal

### Objectives

- Implement version diff calculation
- Generate visual comparison data
- Identify added, removed, and modified elements
- Calculate breaking changes

### Tasks

1. **VersionDiffService**
   - Implement trigger comparison
   - Implement actions comparison
   - Implement conditions comparison
   - Implement change classification

2. **CompareVersionsUseCase**
   - Validate both versions exist
   - Validate both versions belong to same workflow
   - Generate comprehensive diff
   - Format diff for API response

3. **Breaking Change Detection**
   - Define breaking change criteria
   - Detect removed actions with active references
   - Detect trigger type changes
   - Generate warnings for breaking changes

4. **FastAPI Routes**
   - GET /api/v1/workflows/{workflow_id}/versions/compare

### Dependencies

- Milestone 2 (Version CRUD)
- deepdiff library for comparison

### Technical Approach

- Use deepdiff library for nested object comparison
- Implement custom formatters for readable output
- Cache comparison results for repeated requests

---

## Milestone 5: Execution Migration

**Priority:** Secondary Goal

### Objectives

- Implement execution migration between versions
- Support multiple migration strategies
- Handle position mapping between versions
- Track migration progress

### Tasks

1. **MigrationStrategyService**
   - Implement immediate migration strategy
   - Implement gradual migration strategy
   - Implement manual migration strategy
   - Create action mapping algorithms

2. **MigrateExecutionsUseCase**
   - Validate source and target versions
   - Create migration record
   - Queue migration batches
   - Return migration ID for tracking

3. **MigrationWorker (Celery)**
   - Process migration batches
   - Map execution positions
   - Handle migration failures
   - Update progress counters

4. **MigrationProgressService**
   - Track migration status
   - Calculate ETA
   - Handle cancellation requests
   - Generate completion notifications

5. **FastAPI Routes**
   - POST /api/v1/workflows/{workflow_id}/versions/{version_id}/migrate
   - GET /api/v1/workflows/{workflow_id}/migrations/{migration_id}
   - POST /api/v1/workflows/{workflow_id}/migrations/{migration_id}/cancel

### Dependencies

- Milestone 3 (Version Publishing)
- Redis for queue
- Celery for background processing
- SPEC-WFL-005 (Workflow Execution)

### Technical Approach

- Use Celery for background job processing
- Implement batch processing for scalability
- Use Redis for migration progress tracking

---

## Milestone 6: Draft Auto-Save

**Priority:** Secondary Goal

### Objectives

- Implement automatic draft saving
- Handle draft recovery on session restore
- Implement draft cleanup for old drafts
- Prevent data loss during editing

### Tasks

1. **DraftCacheService**
   - Implement Redis-based draft storage
   - Auto-save drafts every 30 seconds
   - Encrypt sensitive draft data
   - Set TTL for automatic cleanup

2. **DraftRepository**
   - Save draft to database (backup)
   - Retrieve latest draft
   - Delete draft on publish
   - Cleanup drafts older than 7 days

3. **SaveDraftUseCase**
   - Validate user owns the draft
   - Merge changes with existing draft
   - Update last_saved_at timestamp
   - Return draft status

4. **RestoreDraftUseCase**
   - Check for existing draft
   - Return draft if exists
   - Handle draft conflicts

5. **FastAPI Routes**
   - POST /api/v1/workflows/{workflow_id}/versions/{version_id}/draft
   - GET /api/v1/workflows/{workflow_id}/versions/{version_id}/draft
   - DELETE /api/v1/workflows/{workflow_id}/versions/{version_id}/draft

### Dependencies

- Milestone 2 (Version CRUD)
- Redis for caching

### Technical Approach

- Use Redis with TTL for fast access
- Implement conflict resolution
- Use database as backup storage

---

## Milestone 7: Version Archival

**Priority:** Final Goal

### Objectives

- Implement automatic version archival
- Archive versions with no active executions after 90 days
- Maintain minimum 10 versions regardless of archival
- Implement scheduled cleanup job

### Tasks

1. **ArchiveVersionsUseCase**
   - Identify versions eligible for archival
   - Validate minimum version retention
   - Update version status to archived
   - Log archival actions

2. **ArchivalScheduler (Celery Beat)**
   - Schedule daily archival job
   - Process archival in batches
   - Generate archival reports

3. **Version Retention Policy**
   - Implement 90-day inactivity rule
   - Implement 10-version minimum rule
   - Handle exceptions for compliance

4. **FastAPI Routes (Admin)**
   - GET /api/v1/admin/workflows/archival-candidates
   - POST /api/v1/admin/workflows/archive-versions

### Dependencies

- Milestone 3 (Version Publishing)
- Celery Beat for scheduling

### Technical Approach

- Use Celery Beat for scheduled tasks
- Implement soft archive (status change)
- Keep audit logs for compliance

---

## Milestone 8: Frontend Integration

**Priority:** Final Goal

### Objectives

- Create version history panel component
- Implement version comparison view
- Create migration wizard component
- Implement auto-save indicator

### Tasks

1. **Version History Panel**
   - List versions with status indicators
   - Show active execution counts
   - Enable version selection
   - Display change summaries

2. **Version Comparison View**
   - Side-by-side diff display
   - Color-coded changes
   - Expandable action details
   - Breaking change warnings

3. **Migration Wizard**
   - Strategy selection step
   - Mapping configuration step
   - Progress monitoring step
   - Completion summary

4. **Auto-Save Indicator**
   - Show save status
   - Display last saved time
   - Handle offline mode
   - Recovery notification

### Dependencies

- All backend milestones
- Next.js frontend
- Shadcn/UI components

### Technical Approach

- Use React Query for API integration
- Implement optimistic updates
- Use WebSocket for real-time progress

---

## Risk Assessment

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Migration data loss | Low | High | Implement dry-run mode, backups |
| Version conflicts | Medium | Medium | Optimistic locking, clear UI |
| Performance degradation | Low | Medium | Batch processing, caching |
| Draft corruption | Low | High | Redis + DB backup strategy |

### Business Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| User confusion | Medium | Medium | Clear UI, documentation |
| Breaking changes | Low | High | Warning system, validation |
| Compliance issues | Low | High | Audit logging, retention |

---

## Testing Strategy

### Unit Tests

- VersionDiffService tests
- MigrationStrategyService tests
- Version status transition tests
- Repository tests with mocks

### Integration Tests

- Full version lifecycle test
- Migration end-to-end test
- Concurrent edit handling test
- Archival job test

### Performance Tests

- Version comparison with 50+ actions
- Migration of 10,000 contacts
- Concurrent version creation
- Draft auto-save under load

---

## Definition of Done

- [ ] All database migrations created and tested
- [ ] All API endpoints implemented and documented
- [ ] All use cases have unit test coverage >= 85%
- [ ] Integration tests pass
- [ ] Performance targets met
- [ ] Security review completed
- [ ] API documentation updated
- [ ] Frontend components integrated
- [ ] Audit logging verified

---

## Traceability Tags

- TAG:SPEC-WFL-012
- TAG:PLAN-WFL-012
- TAG:MODULE-WORKFLOWS
- TAG:DOMAIN-AUTOMATION
