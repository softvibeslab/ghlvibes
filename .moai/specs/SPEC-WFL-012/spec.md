# SPEC-WFL-012: Workflow Versioning

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-012 |
| **Title** | Workflow Versioning |
| **Module** | workflows |
| **Domain** | automation |
| **Priority** | Low |
| **Status** | Planned |
| **Created** | 2026-01-26 |
| **Version** | 1.0.0 |

---

## Overview

This specification defines the requirements for workflow versioning within the GoHighLevel Clone platform. The versioning system enables users to modify active workflows while preserving execution continuity for contacts currently enrolled in previous versions. This feature ensures that workflow changes do not disrupt ongoing automation sequences and provides rollback capabilities for error recovery.

---

## EARS Requirements

### REQ-WFL-012-01: Automatic Version Creation (Event-Driven)

**WHEN** a user modifies an active workflow,
**THEN** the system shall create a new version of the workflow,
**RESULTING IN** the previous version being preserved as immutable,
**IN STATE** versioned.

### REQ-WFL-012-02: Version Number Assignment (Ubiquitous)

The system shall **always** assign sequential version numbers to workflows according to the following rules:
- Version numbers must be positive integers starting from 1
- Each modification to an active workflow increments the version by 1
- Version numbers must never be reused or decremented
- Maximum version limit is 1000 per workflow

### REQ-WFL-012-03: Execution Continuity (Event-Driven)

**WHEN** a new workflow version is created,
**THEN** the system shall maintain all active executions on their original version,
**RESULTING IN** contacts completing their journey on the version they started,
**IN STATE** executing_on_original.

### REQ-WFL-012-04: Draft Mode Editing (State-Driven)

**IF** a workflow is in draft status,
**THEN** the system shall allow direct editing without creating a new version.

**IF** a workflow is in active or paused status,
**THEN** the system shall create a new version for any structural changes.

### REQ-WFL-012-05: Version Migration (Event-Driven)

**WHEN** a user initiates version migration,
**THEN** the system shall offer options to migrate active executions to the new version,
**RESULTING IN** contacts being transferred to equivalent positions in the new workflow,
**IN STATE** migrating.

### REQ-WFL-012-06: Rollback Capability (Event-Driven)

**WHEN** a user initiates a rollback to a previous version,
**THEN** the system shall restore the previous version as active,
**RESULTING IN** new enrollments using the restored version,
**IN STATE** rolled_back.

### REQ-WFL-012-07: Version Metadata Tracking (Ubiquitous)

The system shall **always** track version metadata including:
- Version number and creation timestamp
- User who created the version
- Change summary or commit message
- Diff of changes from previous version
- Number of active executions on this version

### REQ-WFL-012-08: Version Comparison (Event-Driven)

**WHEN** a user requests to compare workflow versions,
**THEN** the system shall display a visual diff of triggers, actions, and conditions,
**RESULTING IN** clear understanding of changes between versions,
**IN STATE** compared.

### REQ-WFL-012-09: Version Archival (State-Driven)

**IF** a workflow version has no active executions and is not the current version,
**THEN** the system shall mark the version as archived after 90 days,
**RESULTING IN** reduced storage requirements while maintaining audit history.

### REQ-WFL-012-10: Concurrent Edit Prevention (Unwanted)

The system shall **not** allow multiple users to edit the same workflow simultaneously to prevent version conflicts. Optimistic locking with version checking must be enforced.

### REQ-WFL-012-11: Version Retention (Ubiquitous)

The system shall **always** retain at least the last 10 versions of any workflow, regardless of archival rules, for audit and compliance purposes.

### REQ-WFL-012-12: Auto-Save Drafts (Event-Driven)

**WHEN** a user is editing a workflow version,
**THEN** the system shall auto-save draft changes every 30 seconds,
**RESULTING IN** a recoverable draft state in case of session interruption,
**IN STATE** draft_saved.

---

## Configuration Schema

### Workflow Version Entity

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | UUID | Yes | auto-generated | Unique version identifier |
| `workflow_id` | UUID | Yes | - | Parent workflow reference |
| `version_number` | integer | Yes | 1 | Sequential version number |
| `account_id` | UUID | Yes | from auth | Tenant identifier |
| `name` | string | Yes | - | Workflow name at this version |
| `description` | string | No | "" | Workflow description |
| `trigger_type` | string | No | null | Trigger configuration |
| `trigger_config` | JSONB | No | {} | Trigger-specific settings |
| `actions` | JSONB | Yes | [] | Array of action configurations |
| `conditions` | JSONB | No | [] | Array of condition configurations |
| `status` | enum | Yes | draft | One of: draft, active, archived |
| `change_summary` | string | No | "" | Description of changes |
| `is_current` | boolean | Yes | true | Whether this is the active version |
| `active_executions` | integer | Yes | 0 | Count of active executions |
| `created_at` | timestamp | Yes | now() | Version creation timestamp |
| `created_by` | UUID | Yes | from auth | User who created the version |
| `archived_at` | timestamp | No | null | When version was archived |

### Version Status Enum

| Value | Description |
|-------|-------------|
| `draft` | Version is being edited, not published |
| `active` | Version is the current live version |
| `archived` | Version has been archived after inactivity |

### Migration Configuration

| Field | Type | Description |
|-------|------|-------------|
| `strategy` | enum | One of: `immediate`, `gradual`, `manual` |
| `batch_size` | integer | Number of contacts to migrate per batch |
| `mapping_rules` | JSONB | Action-to-action mapping for migration |
| `preserve_position` | boolean | Whether to preserve relative position |
| `notify_on_complete` | boolean | Send notification when migration completes |

---

## API Specification

### Endpoint: Create Workflow Version

```
POST /api/v1/workflows/{workflow_id}/versions
```

#### Request Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | Yes | Bearer token from Clerk |
| `Content-Type` | Yes | Must be `application/json` |
| `X-Account-ID` | No | Override account (admin only) |

#### Request Body

```json
{
  "change_summary": "string (optional, max 500 chars)",
  "publish_immediately": "boolean (optional, default false)"
}
```

#### Response: 201 Created

```json
{
  "id": "uuid",
  "workflow_id": "uuid",
  "version_number": 2,
  "name": "string",
  "description": "string",
  "trigger_type": "string",
  "trigger_config": {},
  "actions": [],
  "conditions": [],
  "status": "draft",
  "change_summary": "string",
  "is_current": false,
  "active_executions": 0,
  "created_at": "2026-01-26T10:00:00Z",
  "created_by": "uuid",
  "previous_version": {
    "id": "uuid",
    "version_number": 1,
    "active_executions": 150
  }
}
```

### Endpoint: List Workflow Versions

```
GET /api/v1/workflows/{workflow_id}/versions
```

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_archived` | boolean | false | Include archived versions |
| `page` | integer | 1 | Page number for pagination |
| `per_page` | integer | 20 | Items per page (max 100) |

#### Response: 200 OK

```json
{
  "versions": [
    {
      "id": "uuid",
      "version_number": 2,
      "status": "active",
      "is_current": true,
      "active_executions": 0,
      "change_summary": "Added SMS follow-up action",
      "created_at": "2026-01-26T10:00:00Z",
      "created_by": {
        "id": "uuid",
        "name": "John Doe"
      }
    }
  ],
  "pagination": {
    "total": 5,
    "page": 1,
    "per_page": 20,
    "total_pages": 1
  }
}
```

### Endpoint: Compare Versions

```
GET /api/v1/workflows/{workflow_id}/versions/compare
```

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `from_version` | integer | Yes | Source version number |
| `to_version` | integer | Yes | Target version number |

#### Response: 200 OK

```json
{
  "from_version": 1,
  "to_version": 2,
  "diff": {
    "trigger": {
      "changed": false
    },
    "actions": {
      "added": [
        {
          "id": "uuid",
          "type": "send_sms",
          "position": 3
        }
      ],
      "removed": [],
      "modified": [
        {
          "id": "uuid",
          "type": "send_email",
          "changes": {
            "subject": {
              "from": "Welcome!",
              "to": "Welcome to our platform!"
            }
          }
        }
      ]
    },
    "conditions": {
      "added": [],
      "removed": [],
      "modified": []
    }
  },
  "summary": {
    "total_changes": 2,
    "breaking_changes": 0
  }
}
```

### Endpoint: Publish Version

```
POST /api/v1/workflows/{workflow_id}/versions/{version_id}/publish
```

#### Request Body

```json
{
  "migration_strategy": "string (optional: immediate, gradual, manual)",
  "batch_size": "integer (optional, default 100)",
  "notify_on_complete": "boolean (optional, default true)"
}
```

#### Response: 200 OK

```json
{
  "id": "uuid",
  "version_number": 2,
  "status": "active",
  "is_current": true,
  "migration": {
    "status": "in_progress",
    "strategy": "gradual",
    "contacts_migrated": 0,
    "contacts_remaining": 150,
    "estimated_completion": "2026-01-26T12:00:00Z"
  }
}
```

### Endpoint: Rollback Version

```
POST /api/v1/workflows/{workflow_id}/versions/{version_id}/rollback
```

#### Response: 200 OK

```json
{
  "id": "uuid",
  "version_number": 1,
  "status": "active",
  "is_current": true,
  "rollback_info": {
    "rolled_back_from": 2,
    "rolled_back_at": "2026-01-26T10:30:00Z",
    "rolled_back_by": "uuid"
  }
}
```

### Endpoint: Migrate Executions

```
POST /api/v1/workflows/{workflow_id}/versions/{version_id}/migrate
```

#### Request Body

```json
{
  "source_version": "integer (required)",
  "contact_ids": "array (optional, migrate specific contacts)",
  "mapping_rules": {
    "action_mappings": {
      "old_action_id": "new_action_id"
    },
    "preserve_position": true
  },
  "batch_size": 100
}
```

#### Response: 202 Accepted

```json
{
  "migration_id": "uuid",
  "status": "queued",
  "contacts_to_migrate": 150,
  "estimated_duration_minutes": 5
}
```

### Error Responses

| Status | Code | Description |
|--------|------|-------------|
| 400 | `VALIDATION_ERROR` | Invalid request body |
| 401 | `UNAUTHORIZED` | Missing or invalid auth token |
| 403 | `FORBIDDEN` | User lacks required permission |
| 404 | `NOT_FOUND` | Workflow or version not found |
| 409 | `CONFLICT` | Version conflict or concurrent edit |
| 409 | `MAX_VERSIONS_EXCEEDED` | Reached 1000 version limit |
| 422 | `MIGRATION_IN_PROGRESS` | Cannot modify during migration |
| 429 | `RATE_LIMITED` | Exceeded rate limit |
| 500 | `INTERNAL_ERROR` | Server error |

---

## Database Schema

### Table: workflow_versions

```sql
CREATE TABLE workflow_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT '',
    trigger_type VARCHAR(50),
    trigger_config JSONB DEFAULT '{}',
    actions JSONB NOT NULL DEFAULT '[]',
    conditions JSONB DEFAULT '[]',
    status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'archived')),
    change_summary VARCHAR(500) DEFAULT '',
    is_current BOOLEAN NOT NULL DEFAULT false,
    active_executions INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    archived_at TIMESTAMPTZ,

    CONSTRAINT workflow_versions_unique UNIQUE (workflow_id, version_number),
    CONSTRAINT workflow_versions_max CHECK (version_number <= 1000)
);

-- Indexes
CREATE INDEX idx_workflow_versions_workflow_id ON workflow_versions(workflow_id);
CREATE INDEX idx_workflow_versions_status ON workflow_versions(status);
CREATE INDEX idx_workflow_versions_is_current ON workflow_versions(is_current) WHERE is_current = true;
CREATE INDEX idx_workflow_versions_created_at ON workflow_versions(created_at);
CREATE INDEX idx_workflow_versions_active_executions ON workflow_versions(active_executions) WHERE active_executions > 0;

-- Partial unique index for current version
CREATE UNIQUE INDEX idx_workflow_versions_current_unique
    ON workflow_versions(workflow_id)
    WHERE is_current = true;

-- Row Level Security
ALTER TABLE workflow_versions ENABLE ROW LEVEL SECURITY;

CREATE POLICY workflow_versions_tenant_isolation ON workflow_versions
    FOR ALL
    USING (account_id = current_setting('app.current_account_id')::uuid);
```

### Table: workflow_version_migrations

```sql
CREATE TABLE workflow_version_migrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    source_version_id UUID NOT NULL REFERENCES workflow_versions(id),
    target_version_id UUID NOT NULL REFERENCES workflow_versions(id),
    account_id UUID NOT NULL REFERENCES accounts(id),
    strategy VARCHAR(20) NOT NULL CHECK (strategy IN ('immediate', 'gradual', 'manual')),
    mapping_rules JSONB DEFAULT '{}',
    batch_size INTEGER NOT NULL DEFAULT 100,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'failed', 'cancelled')),
    contacts_total INTEGER NOT NULL DEFAULT 0,
    contacts_migrated INTEGER NOT NULL DEFAULT 0,
    contacts_failed INTEGER NOT NULL DEFAULT 0,
    error_log JSONB DEFAULT '[]',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id)
);

-- Indexes
CREATE INDEX idx_version_migrations_workflow_id ON workflow_version_migrations(workflow_id);
CREATE INDEX idx_version_migrations_status ON workflow_version_migrations(status);
CREATE INDEX idx_version_migrations_created_at ON workflow_version_migrations(created_at);
```

### Table: workflow_version_drafts

```sql
CREATE TABLE workflow_version_drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    account_id UUID NOT NULL REFERENCES accounts(id),
    draft_data JSONB NOT NULL,
    last_saved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT workflow_version_drafts_unique UNIQUE (workflow_id, user_id)
);

-- Indexes
CREATE INDEX idx_version_drafts_workflow_id ON workflow_version_drafts(workflow_id);
CREATE INDEX idx_version_drafts_user_id ON workflow_version_drafts(user_id);
CREATE INDEX idx_version_drafts_last_saved ON workflow_version_drafts(last_saved_at);

-- Auto-cleanup old drafts (trigger)
CREATE OR REPLACE FUNCTION cleanup_old_drafts()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM workflow_version_drafts
    WHERE last_saved_at < NOW() - INTERVAL '7 days';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Table: workflow_version_audit_logs

```sql
CREATE TABLE workflow_version_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    version_id UUID REFERENCES workflow_versions(id) ON DELETE SET NULL,
    account_id UUID NOT NULL REFERENCES accounts(id),
    action VARCHAR(50) NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id),
    details JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_version_audit_workflow_id ON workflow_version_audit_logs(workflow_id);
CREATE INDEX idx_version_audit_version_id ON workflow_version_audit_logs(version_id);
CREATE INDEX idx_version_audit_action ON workflow_version_audit_logs(action);
CREATE INDEX idx_version_audit_created_at ON workflow_version_audit_logs(created_at);
```

---

## Technical Approach

### Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        Client Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Version    │  │  Version     │  │   Version    │           │
│  │   History    │  │  Comparison  │  │   Migration  │           │
│  │   Panel      │  │  Diff View   │  │   Wizard     │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                        API Layer (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Version    │  │   Migration  │  │   Rollback   │           │
│  │   Routes     │  │   Routes     │  │   Routes     │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Application Layer (Use Cases)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Create     │  │   Compare    │  │   Migrate    │           │
│  │   Version    │  │   Versions   │  │   Executions │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Publish    │  │   Rollback   │  │   Archive    │           │
│  │   Version    │  │   Version    │  │   Versions   │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Domain Layer                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ Workflow     │  │  Version     │  │  Migration   │           │
│  │ Version      │  │  Diff        │  │  Strategy    │           │
│  │ Entity       │  │  Service     │  │  Entity      │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  Version     │  │  Migration   │  │  Draft       │           │
│  │  Repository  │  │  Queue       │  │  Cache       │           │
│  │  (Postgres)  │  │  (Redis)     │  │  (Redis)     │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└──────────────────────────────────────────────────────────────────┘
```

### Implementation Layers

1. **Presentation Layer (FastAPI Routes)**
   - Version CRUD endpoints
   - Version comparison endpoint
   - Migration management endpoints
   - Rollback endpoint
   - Draft auto-save endpoint

2. **Application Layer (Use Cases)**
   - CreateVersionUseCase: Creates new version from current workflow state
   - PublishVersionUseCase: Activates a draft version
   - CompareVersionsUseCase: Generates diff between versions
   - MigrateExecutionsUseCase: Handles execution migration
   - RollbackVersionUseCase: Reverts to previous version
   - ArchiveVersionsUseCase: Scheduled archival of old versions

3. **Domain Layer (Entities and Services)**
   - WorkflowVersion entity with validation rules
   - VersionDiffService for generating comparisons
   - MigrationStrategy value objects
   - VersionNumber value object with constraints

4. **Infrastructure Layer (Repositories and Services)**
   - WorkflowVersionRepository (SQLAlchemy async)
   - MigrationQueueService (Celery + Redis)
   - DraftCacheService (Redis)
   - VersionAuditRepository

### Key Implementation Details

#### Version Creation Service

```python
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

class WorkflowVersionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_version(
        self,
        workflow_id: UUID,
        user_id: UUID,
        change_summary: Optional[str] = None
    ) -> WorkflowVersion:
        # Get current version
        current = await self._get_current_version(workflow_id)

        # Calculate next version number
        next_version = await self._get_next_version_number(workflow_id)

        # Create new version from current state
        new_version = WorkflowVersion(
            workflow_id=workflow_id,
            version_number=next_version,
            account_id=current.account_id,
            name=current.name,
            description=current.description,
            trigger_type=current.trigger_type,
            trigger_config=current.trigger_config,
            actions=current.actions,
            conditions=current.conditions,
            status='draft',
            change_summary=change_summary or '',
            is_current=False,
            created_by=user_id
        )

        self.db.add(new_version)
        await self.db.commit()
        await self.db.refresh(new_version)

        return new_version

    async def _get_next_version_number(self, workflow_id: UUID) -> int:
        result = await self.db.execute(
            select(func.max(WorkflowVersion.version_number))
            .where(WorkflowVersion.workflow_id == workflow_id)
        )
        max_version = result.scalar() or 0
        return max_version + 1
```

#### Version Diff Service

```python
from deepdiff import DeepDiff
from typing import Dict, Any

class VersionDiffService:
    def compare_versions(
        self,
        from_version: WorkflowVersion,
        to_version: WorkflowVersion
    ) -> Dict[str, Any]:
        diff = {
            'trigger': self._compare_triggers(from_version, to_version),
            'actions': self._compare_actions(from_version, to_version),
            'conditions': self._compare_conditions(from_version, to_version)
        }

        total_changes = sum([
            len(diff['actions'].get('added', [])),
            len(diff['actions'].get('removed', [])),
            len(diff['actions'].get('modified', [])),
            len(diff['conditions'].get('added', [])),
            len(diff['conditions'].get('removed', [])),
            1 if diff['trigger']['changed'] else 0
        ])

        return {
            'from_version': from_version.version_number,
            'to_version': to_version.version_number,
            'diff': diff,
            'summary': {
                'total_changes': total_changes,
                'breaking_changes': self._count_breaking_changes(diff)
            }
        }

    def _compare_actions(
        self,
        from_version: WorkflowVersion,
        to_version: WorkflowVersion
    ) -> Dict[str, Any]:
        from_actions = {a['id']: a for a in from_version.actions}
        to_actions = {a['id']: a for a in to_version.actions}

        added = [a for id, a in to_actions.items() if id not in from_actions]
        removed = [a for id, a in from_actions.items() if id not in to_actions]

        modified = []
        for id, to_action in to_actions.items():
            if id in from_actions:
                from_action = from_actions[id]
                changes = DeepDiff(from_action, to_action, ignore_order=True)
                if changes:
                    modified.append({
                        'id': id,
                        'type': to_action['type'],
                        'changes': self._format_changes(changes)
                    })

        return {'added': added, 'removed': removed, 'modified': modified}
```

#### Migration Queue Worker

```python
from celery import Celery
from typing import List, Optional
from uuid import UUID

celery_app = Celery('workflow_migrations')

@celery_app.task(bind=True, max_retries=3)
def migrate_executions_batch(
    self,
    migration_id: str,
    execution_ids: List[str],
    target_version_id: str,
    mapping_rules: dict
):
    try:
        with get_db_session() as db:
            migration = db.query(WorkflowVersionMigration).get(migration_id)

            for exec_id in execution_ids:
                execution = db.query(WorkflowExecution).get(exec_id)

                # Map current position to new version
                new_position = map_execution_position(
                    execution=execution,
                    target_version_id=target_version_id,
                    mapping_rules=mapping_rules
                )

                # Update execution
                execution.version_id = target_version_id
                execution.current_action_index = new_position

            # Update migration progress
            migration.contacts_migrated += len(execution_ids)

            if migration.contacts_migrated >= migration.contacts_total:
                migration.status = 'completed'
                migration.completed_at = datetime.now(timezone.utc)

            db.commit()

    except Exception as exc:
        self.retry(exc=exc, countdown=60)
```

#### Optimistic Locking for Concurrent Edits

```python
from sqlalchemy import Column, Integer
from sqlalchemy.orm import Session
from fastapi import HTTPException

class WorkflowVersion(Base):
    # ... other fields ...
    lock_version = Column(Integer, default=0, nullable=False)

async def update_version_with_lock(
    db: AsyncSession,
    version_id: UUID,
    expected_lock_version: int,
    updates: dict
) -> WorkflowVersion:
    result = await db.execute(
        update(WorkflowVersion)
        .where(
            WorkflowVersion.id == version_id,
            WorkflowVersion.lock_version == expected_lock_version
        )
        .values(
            **updates,
            lock_version=expected_lock_version + 1
        )
        .returning(WorkflowVersion)
    )

    version = result.scalar_one_or_none()
    if not version:
        raise HTTPException(
            status_code=409,
            detail={
                'code': 'CONFLICT',
                'message': 'Workflow was modified by another user. Please refresh and try again.'
            }
        )

    return version
```

---

## Dependencies

### Internal Dependencies

| Module | Dependency Type | Description |
|--------|-----------------|-------------|
| SPEC-WFL-001 | Hard | Requires workflow creation functionality |
| SPEC-WFL-005 | Hard | Integrates with workflow execution system |
| Authentication | Hard | Requires Clerk authentication |
| Multi-tenancy | Hard | Requires account isolation |

### External Dependencies

| Service | Purpose | Required |
|---------|---------|----------|
| Supabase PostgreSQL | Version storage | Yes |
| Clerk | Authentication and authorization | Yes |
| Redis | Draft caching, migration queue | Yes |
| Celery | Background migration processing | Yes |

---

## Security Considerations

### Authentication

- All endpoints require valid JWT from Clerk
- JWT must contain `account_id` claim for tenant isolation

### Authorization

- `workflows:read` permission for viewing versions
- `workflows:edit` permission for creating/editing versions
- `workflows:admin` permission for rollback and migration
- Permission checked via Clerk metadata or custom RBAC

### Data Protection

- All version data encrypted at rest (Supabase default)
- TLS 1.3 for all API communications
- Audit logging for all version changes
- Draft data encrypted in Redis cache

### Concurrent Access

- Optimistic locking prevents conflicting edits
- Clear error messages for version conflicts
- Lock version displayed to users for awareness

---

## Performance Requirements

| Metric | Target |
|--------|--------|
| Version Creation (p95) | < 300ms |
| Version Comparison (p95) | < 500ms |
| Version List (p95) | < 200ms |
| Migration Throughput | 1000 contacts/minute |
| Draft Auto-save (p95) | < 100ms |

---

## Constraints

### Technical Constraints

- Must use FastAPI async patterns
- Must use SQLAlchemy 2.0 async with Supabase
- Must integrate with existing Clerk authentication
- Must follow Clean Architecture patterns
- Migration must be non-blocking for workflow execution

### Business Constraints

- Maximum 1000 versions per workflow
- Retain minimum 10 versions for audit
- Archive versions after 90 days of inactivity
- Draft auto-save every 30 seconds
- Migration must support gradual rollout

---

## Related SPECs

| SPEC ID | Title | Relationship |
|---------|-------|--------------|
| SPEC-WFL-001 | Create Workflow | Base workflow functionality |
| SPEC-WFL-002 | Configure Trigger | Version includes trigger config |
| SPEC-WFL-003 | Add Action Step | Version includes actions |
| SPEC-WFL-004 | Add Condition/Branch | Version includes conditions |
| SPEC-WFL-005 | Execute Workflow | Executions run on specific versions |
| SPEC-WFL-009 | Workflow Analytics | Analytics per version |

---

## Traceability Tags

- TAG:SPEC-WFL-012
- TAG:MODULE-WORKFLOWS
- TAG:DOMAIN-AUTOMATION
- TAG:PRIORITY-LOW
- TAG:FEATURE-VERSIONING
- TAG:FEATURE-MIGRATION
- TAG:FEATURE-ROLLBACK
