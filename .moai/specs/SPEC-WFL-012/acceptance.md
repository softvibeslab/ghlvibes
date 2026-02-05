# SPEC-WFL-012: Workflow Versioning - Acceptance Criteria

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

## Quality Gate Criteria

### Test Coverage

- [ ] Unit test coverage >= 85%
- [ ] Integration test coverage >= 75%
- [ ] All critical paths tested
- [ ] Edge cases documented and tested

### Performance

- [ ] Version creation < 300ms (p95)
- [ ] Version comparison < 500ms (p95)
- [ ] Version list < 200ms (p95)
- [ ] Migration throughput >= 1000 contacts/minute
- [ ] Draft auto-save < 100ms (p95)

### Security

- [ ] All endpoints require authentication
- [ ] Authorization checks for all operations
- [ ] Tenant isolation verified
- [ ] Audit logging complete
- [ ] No sensitive data in logs

### Code Quality

- [ ] Zero linter errors (ruff)
- [ ] Zero type errors (pyright)
- [ ] All functions documented
- [ ] Follows Clean Architecture patterns

---

## Acceptance Criteria by Feature

### AC-WFL-012-01: Version Creation

**Given** a user with `workflows:edit` permission
**And** an active workflow with existing configuration
**When** the user requests to create a new version
**Then** the system creates a new version with:
- Sequential version number (previous + 1)
- Copy of all trigger configuration
- Copy of all action configurations
- Copy of all condition configurations
- Status set to "draft"
- is_current set to false
- Creation timestamp and user recorded

**Given** a user attempting to create a version
**And** the workflow has reached 1000 versions
**When** the user requests to create a new version
**Then** the system returns error code MAX_VERSIONS_EXCEEDED
**And** no new version is created

**Given** a workflow in draft status
**When** the user edits the workflow
**Then** the system modifies the existing version directly
**And** no new version is created

---

### AC-WFL-012-02: Version Publishing

**Given** a version in draft status with complete configuration
**And** a user with `workflows:edit` permission
**When** the user publishes the version
**Then** the system:
- Sets the draft version status to "active"
- Sets the draft version is_current to true
- Sets the previous current version is_current to false
- Updates the main workflow reference
- Logs the publish action

**Given** a version in draft status
**And** the version has no trigger configured
**When** the user attempts to publish
**Then** the system returns error code VALIDATION_ERROR
**And** message indicates missing trigger configuration
**And** the version remains in draft status

---

### AC-WFL-012-03: Execution Continuity

**Given** a workflow version V1 with 150 active executions
**When** version V2 is published
**Then** all 150 executions continue on version V1
**And** new enrollments use version V2
**And** V1 active_executions count remains accurate

**Given** a contact enrolled in workflow version V1
**And** the contact is at action step 3 of 5
**When** version V2 is published
**Then** the contact continues from step 3 on version V1
**And** the contact completes all remaining steps on V1
**And** the contact is never automatically migrated

---

### AC-WFL-012-04: Version Comparison

**Given** two versions of the same workflow (V1 and V2)
**When** a user requests comparison between V1 and V2
**Then** the system returns a diff containing:
- Trigger changes (changed: boolean)
- Actions added (list of new actions)
- Actions removed (list of deleted actions)
- Actions modified (list with change details)
- Conditions added/removed/modified
- Total change count
- Breaking change count

**Given** V1 has actions [A, B, C] and V2 has actions [A, B', D]
**When** comparing V1 to V2
**Then** the diff shows:
- Added: [D]
- Removed: [C]
- Modified: [B with changes to B']

---

### AC-WFL-012-05: Version Migration

**Given** 100 contacts executing on version V1
**And** version V2 is the current version
**And** a user with `workflows:admin` permission
**When** the user initiates migration with strategy "immediate"
**Then** the system:
- Creates a migration record
- Queues all 100 contacts for migration
- Returns migration ID and estimated completion time

**Given** a contact at action index 3 on V1
**And** V1 action order: [email, wait, sms, tag]
**And** V2 action order: [email, sms, tag, notification]
**When** the contact is migrated to V2 with preserve_position=true
**Then** the contact is placed at the equivalent position
**And** mapping preserves logical flow where possible

**Given** an in-progress migration
**When** the user cancels the migration
**Then** the system:
- Stops processing new batches
- Keeps already-migrated contacts on V2
- Returns non-migrated contacts remain on V1
- Sets migration status to "cancelled"

---

### AC-WFL-012-06: Version Rollback

**Given** current version is V3
**And** V1 exists and is not archived
**And** a user with `workflows:admin` permission
**When** the user initiates rollback to V1
**Then** the system:
- Creates V4 as a copy of V1
- Sets V4 as current version
- Preserves V3 in history
- Logs rollback action with source and target

**Given** current version V2 with 50 active executions
**When** rollback to V1 is completed
**Then** the 50 executions continue on V2
**And** new enrollments use the rolled-back version

---

### AC-WFL-012-07: Concurrent Edit Prevention

**Given** user A is editing version V1 (lock_version=5)
**And** user B loads version V1 (lock_version=5)
**When** user A saves changes
**Then** V1 lock_version becomes 6
**And** save succeeds

**When** user B attempts to save changes with lock_version=5
**Then** the system returns error code CONFLICT
**And** message indicates concurrent modification
**And** user B must refresh and re-apply changes

---

### AC-WFL-012-08: Draft Auto-Save

**Given** a user editing a draft version
**When** 30 seconds elapse since the last manual save
**Then** the system automatically saves draft to Redis cache
**And** updates last_saved_at timestamp
**And** displays save status indicator

**Given** a user with an unsaved draft
**When** the user closes the browser unexpectedly
**And** the user returns to the workflow editor
**Then** the system prompts to restore the auto-saved draft
**And** the user can choose to restore or discard

**Given** an auto-saved draft
**When** 7 days pass without user access
**Then** the system deletes the draft
**And** the deletion is logged

---

### AC-WFL-012-09: Version Archival

**Given** version V1 with 0 active executions
**And** V1 is not the current version
**And** V1 was last modified more than 90 days ago
**When** the daily archival job runs
**Then** V1 status is set to "archived"
**And** V1 remains queryable with include_archived=true

**Given** a workflow with versions V1 through V12
**And** V1-V10 have 0 active executions
**And** V1-V10 are older than 90 days
**When** the archival job runs
**Then** only V1 and V2 are archived
**And** V3-V12 are retained (minimum 10 versions rule)

---

### AC-WFL-012-10: Version Listing

**Given** a workflow with 25 versions
**When** listing versions with default pagination
**Then** the system returns:
- First 20 versions (default per_page)
- Sorted by version_number descending
- Pagination metadata with total=25

**Given** versions V1 (archived), V2 (active), V3 (draft)
**When** listing without include_archived parameter
**Then** only V2 and V3 are returned

**When** listing with include_archived=true
**Then** V1, V2, and V3 are all returned

---

### AC-WFL-012-11: Audit Logging

**Given** any version operation (create, publish, rollback, migrate, archive)
**When** the operation completes successfully
**Then** the system logs:
- Workflow ID
- Version ID
- Action type
- User ID who performed action
- Timestamp
- Relevant details (change summary, migration stats, etc.)

---

### AC-WFL-012-12: Authorization

**Given** a user without `workflows:edit` permission
**When** attempting to create or publish a version
**Then** the system returns 403 Forbidden

**Given** a user without `workflows:admin` permission
**When** attempting to rollback or migrate
**Then** the system returns 403 Forbidden

**Given** a user from account A
**When** attempting to access workflow versions in account B
**Then** the system returns 404 Not Found (RLS prevents access)

---

## Test Scenarios

### test_version_creation

```python
@pytest.mark.asyncio
async def test_create_version_success(async_client, auth_headers, workflow):
    """Test successful version creation from active workflow."""
    response = await async_client.post(
        f"/api/v1/workflows/{workflow.id}/versions",
        headers=auth_headers,
        json={"change_summary": "Added SMS follow-up"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["version_number"] == 2
    assert data["status"] == "draft"
    assert data["is_current"] is False
    assert data["change_summary"] == "Added SMS follow-up"

@pytest.mark.asyncio
async def test_create_version_max_limit(async_client, auth_headers, workflow_with_999_versions):
    """Test version creation at limit."""
    # Create 1000th version
    response = await async_client.post(
        f"/api/v1/workflows/{workflow_with_999_versions.id}/versions",
        headers=auth_headers,
        json={}
    )
    assert response.status_code == 201

    # Attempt 1001st version
    response = await async_client.post(
        f"/api/v1/workflows/{workflow_with_999_versions.id}/versions",
        headers=auth_headers,
        json={}
    )
    assert response.status_code == 409
    assert response.json()["code"] == "MAX_VERSIONS_EXCEEDED"

@pytest.mark.asyncio
async def test_create_version_unauthorized(async_client, workflow):
    """Test version creation without auth returns 401."""
    response = await async_client.post(
        f"/api/v1/workflows/{workflow.id}/versions",
        json={}
    )
    assert response.status_code == 401
```

### test_execution_continuity

```python
@pytest.mark.asyncio
async def test_executions_continue_on_old_version(
    async_client, auth_headers, workflow_with_executions
):
    """Test that active executions remain on their original version."""
    workflow = workflow_with_executions
    original_version_id = workflow.current_version_id
    original_execution_count = 150

    # Create and publish new version
    create_response = await async_client.post(
        f"/api/v1/workflows/{workflow.id}/versions",
        headers=auth_headers,
        json={"change_summary": "Updated actions"}
    )
    new_version_id = create_response.json()["id"]

    await async_client.post(
        f"/api/v1/workflows/{workflow.id}/versions/{new_version_id}/publish",
        headers=auth_headers
    )

    # Verify original version still has executions
    response = await async_client.get(
        f"/api/v1/workflows/{workflow.id}/versions/{original_version_id}",
        headers=auth_headers
    )

    assert response.json()["active_executions"] == original_execution_count
    assert response.json()["is_current"] is False

@pytest.mark.asyncio
async def test_new_enrollments_use_current_version(
    async_client, auth_headers, workflow, contact
):
    """Test that new enrollments use the current version."""
    # Publish a new version
    create_response = await async_client.post(
        f"/api/v1/workflows/{workflow.id}/versions",
        headers=auth_headers,
        json={}
    )
    new_version_id = create_response.json()["id"]

    await async_client.post(
        f"/api/v1/workflows/{workflow.id}/versions/{new_version_id}/publish",
        headers=auth_headers
    )

    # Enroll a new contact
    enroll_response = await async_client.post(
        f"/api/v1/workflows/{workflow.id}/enroll",
        headers=auth_headers,
        json={"contact_id": str(contact.id)}
    )

    execution = enroll_response.json()
    assert execution["version_id"] == new_version_id
```

### test_version_comparison

```python
@pytest.mark.asyncio
async def test_compare_versions_diff(async_client, auth_headers, workflow_with_versions):
    """Test version comparison shows correct diff."""
    workflow = workflow_with_versions

    response = await async_client.get(
        f"/api/v1/workflows/{workflow.id}/versions/compare",
        params={"from_version": 1, "to_version": 2},
        headers=auth_headers
    )

    assert response.status_code == 200
    diff = response.json()["diff"]

    assert "actions" in diff
    assert "added" in diff["actions"]
    assert "removed" in diff["actions"]
    assert "modified" in diff["actions"]
    assert "summary" in response.json()
    assert "total_changes" in response.json()["summary"]

@pytest.mark.asyncio
async def test_compare_versions_breaking_changes(
    async_client, auth_headers, workflow_with_breaking_changes
):
    """Test that breaking changes are detected."""
    workflow = workflow_with_breaking_changes

    response = await async_client.get(
        f"/api/v1/workflows/{workflow.id}/versions/compare",
        params={"from_version": 1, "to_version": 2},
        headers=auth_headers
    )

    summary = response.json()["summary"]
    assert summary["breaking_changes"] > 0
```

### test_migration

```python
@pytest.mark.asyncio
async def test_migrate_executions_immediate(
    async_client, auth_headers, workflow_with_executions
):
    """Test immediate migration of executions."""
    workflow = workflow_with_executions
    source_version = 1
    target_version = 2

    response = await async_client.post(
        f"/api/v1/workflows/{workflow.id}/versions/{target_version}/migrate",
        headers=auth_headers,
        json={
            "source_version": source_version,
            "batch_size": 50
        }
    )

    assert response.status_code == 202
    data = response.json()
    assert "migration_id" in data
    assert data["status"] == "queued"
    assert data["contacts_to_migrate"] == 150

@pytest.mark.asyncio
async def test_migrate_preserves_position(
    async_client, auth_headers, workflow_with_execution_at_step_3
):
    """Test migration preserves execution position."""
    workflow = workflow_with_execution_at_step_3
    execution_id = workflow.executions[0].id

    # Initiate migration
    response = await async_client.post(
        f"/api/v1/workflows/{workflow.id}/versions/2/migrate",
        headers=auth_headers,
        json={
            "source_version": 1,
            "contact_ids": [str(execution_id)],
            "mapping_rules": {"preserve_position": True}
        }
    )

    # Wait for migration to complete
    migration_id = response.json()["migration_id"]
    await wait_for_migration_complete(async_client, workflow.id, migration_id)

    # Verify execution position
    execution = await get_execution(async_client, execution_id, auth_headers)
    assert execution["version_id"] == workflow.version_2_id
    # Position should be equivalent in new version
```

### test_rollback

```python
@pytest.mark.asyncio
async def test_rollback_success(async_client, admin_headers, workflow_v3):
    """Test successful rollback to previous version."""
    workflow = workflow_v3

    response = await async_client.post(
        f"/api/v1/workflows/{workflow.id}/versions/1/rollback",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["version_number"] == 4  # New version created
    assert data["is_current"] is True
    assert "rollback_info" in data
    assert data["rollback_info"]["rolled_back_from"] == 3

@pytest.mark.asyncio
async def test_rollback_unauthorized(async_client, auth_headers, workflow_v3):
    """Test rollback requires admin permission."""
    workflow = workflow_v3

    response = await async_client.post(
        f"/api/v1/workflows/{workflow.id}/versions/1/rollback",
        headers=auth_headers  # Regular user, not admin
    )

    assert response.status_code == 403
```

### test_concurrent_edit

```python
@pytest.mark.asyncio
async def test_concurrent_edit_conflict(async_client, auth_headers, workflow_draft):
    """Test optimistic locking prevents concurrent edits."""
    workflow = workflow_draft
    version = workflow.current_version

    # Simulate user A and B loading same version
    lock_version = version.lock_version

    # User A saves successfully
    response_a = await async_client.patch(
        f"/api/v1/workflows/{workflow.id}/versions/{version.id}",
        headers=auth_headers,
        json={
            "name": "Updated by A",
            "lock_version": lock_version
        }
    )
    assert response_a.status_code == 200

    # User B tries to save with stale lock_version
    response_b = await async_client.patch(
        f"/api/v1/workflows/{workflow.id}/versions/{version.id}",
        headers=auth_headers,
        json={
            "name": "Updated by B",
            "lock_version": lock_version  # Stale version
        }
    )
    assert response_b.status_code == 409
    assert response_b.json()["code"] == "CONFLICT"
```

### test_auto_save

```python
@pytest.mark.asyncio
async def test_draft_auto_save(async_client, auth_headers, workflow_draft):
    """Test draft auto-save functionality."""
    workflow = workflow_draft
    version = workflow.current_version

    draft_data = {
        "actions": [{"type": "send_email", "config": {}}],
        "unsaved_changes": True
    }

    response = await async_client.post(
        f"/api/v1/workflows/{workflow.id}/versions/{version.id}/draft",
        headers=auth_headers,
        json=draft_data
    )

    assert response.status_code == 200
    assert "last_saved_at" in response.json()

@pytest.mark.asyncio
async def test_draft_recovery(async_client, auth_headers, workflow_with_draft):
    """Test draft recovery on session restore."""
    workflow = workflow_with_draft
    version = workflow.current_version

    response = await async_client.get(
        f"/api/v1/workflows/{workflow.id}/versions/{version.id}/draft",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["has_draft"] is True
    assert "draft_data" in data
    assert "last_saved_at" in data
```

### test_archival

```python
@pytest.mark.asyncio
async def test_version_archival_after_90_days(db_session, workflow_with_old_versions):
    """Test versions are archived after 90 days of inactivity."""
    workflow = workflow_with_old_versions

    # Run archival job
    from app.jobs.archive_versions import archive_old_versions
    await archive_old_versions()

    # Check versions older than 90 days with no executions are archived
    old_version = await get_version(db_session, workflow.old_version_id)
    assert old_version.status == "archived"

@pytest.mark.asyncio
async def test_minimum_version_retention(db_session, workflow_with_12_old_versions):
    """Test minimum 10 versions are retained."""
    workflow = workflow_with_12_old_versions

    # Run archival job
    from app.jobs.archive_versions import archive_old_versions
    await archive_old_versions()

    # Count non-archived versions
    versions = await list_versions(db_session, workflow.id, include_archived=False)
    assert len(versions) >= 10
```

---

## Definition of Done Checklist

### Functional Requirements

- [ ] Version creation works correctly
- [ ] Version publishing transitions states properly
- [ ] Execution continuity is maintained
- [ ] Version comparison generates accurate diffs
- [ ] Migration moves executions correctly
- [ ] Rollback restores previous versions
- [ ] Concurrent edit prevention works
- [ ] Draft auto-save functions correctly
- [ ] Version archival follows rules
- [ ] Authorization enforced on all endpoints

### Non-Functional Requirements

- [ ] Performance targets met
- [ ] Security review passed
- [ ] Audit logging complete
- [ ] Error handling comprehensive
- [ ] API documentation complete

### Quality Assurance

- [ ] All test scenarios pass
- [ ] Code coverage >= 85%
- [ ] Zero critical/high vulnerabilities
- [ ] Zero linter errors

---

## Traceability Tags

- TAG:SPEC-WFL-012
- TAG:ACCEPTANCE-WFL-012
- TAG:MODULE-WORKFLOWS
- TAG:DOMAIN-AUTOMATION
