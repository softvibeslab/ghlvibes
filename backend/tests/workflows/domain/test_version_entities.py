"""Unit tests for workflow version domain entities."""

import pytest
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from src.workflows.domain.version_entities import (
    VersionDiff,
    VersionMigration,
    WorkflowVersion,
)
from src.workflows.domain.version_exceptions import (
    InvalidVersionStatusError,
    VersionDomainError,
)
from src.workflows.domain.version_value_objects import (
    ChangeSummary,
    VersionNumber,
    VersionStatus,
)


class TestWorkflowVersion:
    """Test suite for WorkflowVersion entity."""

    @pytest.fixture
    def valid_version_data(self):
        """Provide valid version data for testing."""
        return {
            "workflow_id": uuid4(),
            "account_id": uuid4(),
            "version_number": 1,
            "name": "Test Workflow",
            "description": "Test description",
            "trigger_type": "webhook",
            "trigger_config": {"url": "https://example.com"},
            "actions": [{"id": "action-1", "type": "send_email"}],
            "conditions": [],
            "created_by": uuid4(),
        }

    def test_create_workflow_version(self, valid_version_data):
        """Test creating a workflow version."""
        version = WorkflowVersion.create(**valid_version_data)

        assert version.is_draft is True
        assert version.is_current is False
        assert version.active_executions == 0

    def test_version_number_conversion(self, valid_version_data):
        """Test version number is converted to value object."""
        valid_version_data["version_number"] = 5
        version = WorkflowVersion.create(**valid_version_data)

        assert isinstance(version.version_number, VersionNumber)
        assert version.version_number.value == 5

    def test_change_summary_conversion(self, valid_version_data):
        """Test change summary is converted to value object."""
        valid_version_data["change_summary"] = "Added email action"
        version = WorkflowVersion.create(**valid_version_data)

        assert isinstance(version.change_summary, ChangeSummary)
        assert str(version.change_summary) == "Added email action"

    def test_publish_version(self, valid_version_data):
        """Test publishing a version."""
        version = WorkflowVersion.create(**valid_version_data)

        version.publish()

        assert version.is_active is True
        assert version.is_current is True

    def test_publish_non_draft_version_fails(self, valid_version_data):
        """Test publishing non-draft version fails."""
        version = WorkflowVersion.create(**valid_version_data)
        version.status = VersionStatus.ACTIVE

        with pytest.raises(InvalidVersionStatusError):
            version.publish()

    def test_archive_version(self, valid_version_data):
        """Test archiving a version."""
        version = WorkflowVersion.create(**valid_version_data)
        version.status = VersionStatus.ACTIVE

        version.archive()

        assert version.is_archived is True
        assert version.is_current is False
        assert version.archived_at is not None

    def test_archive_version_with_executions_fails(self, valid_version_data):
        """Test archiving version with executions fails."""
        version = WorkflowVersion.create(**valid_version_data)
        version.status = VersionStatus.ACTIVE
        version.active_executions = 5

        with pytest.raises(VersionDomainError, match="active executions"):
            version.archive()

    def test_deactivate_current(self, valid_version_data):
        """Test deactivating current version."""
        version = WorkflowVersion.create(**valid_version_data)
        version.is_current = True

        version.deactivate_current()

        assert version.is_current is False

    def test_increment_executions(self, valid_version_data):
        """Test incrementing execution count."""
        version = WorkflowVersion.create(**valid_version_data)

        version.increment_executions()
        assert version.active_executions == 1

        version.increment_executions()
        assert version.active_executions == 2

    def test_decrement_executions(self, valid_version_data):
        """Test decrementing execution count."""
        version = WorkflowVersion.create(**valid_version_data)
        version.active_executions = 5

        version.decrement_executions()
        assert version.active_executions == 4

    def test_decrement_executions_below_zero_fails(self, valid_version_data):
        """Test decrementing executions below zero fails."""
        version = WorkflowVersion.create(**valid_version_data)
        version.active_executions = 0

        with pytest.raises(VersionDomainError, match="below zero"):
            version.decrement_executions()

    def test_to_dict(self, valid_version_data):
        """Test converting version to dictionary."""
        version = WorkflowVersion.create(**valid_version_data)

        version_dict = version.to_dict()

        assert version_dict["version_number"] == 1
        assert version_dict["name"] == "Test Workflow"
        assert version_dict["status"] == "draft"
        assert "id" in version_dict
        assert "workflow_id" in version_dict


class TestVersionMigration:
    """Test suite for VersionMigration entity."""

    @pytest.fixture
    def valid_migration_data(self):
        """Provide valid migration data for testing."""
        return {
            "workflow_id": uuid4(),
            "source_version_id": uuid4(),
            "target_version_id": uuid4(),
            "account_id": uuid4(),
            "strategy": "gradual",
            "created_by": uuid4(),
            "contacts_total": 100,
        }

    def test_create_migration(self, valid_migration_data):
        """Test creating a migration."""
        migration = VersionMigration.create(**valid_migration_data)

        assert migration.is_pending is True
        assert migration.contacts_total == 100
        assert migration.contacts_migrated == 0
        assert migration.contacts_failed == 0

    def test_migration_start(self, valid_migration_data):
        """Test starting a migration."""
        migration = VersionMigration.create(**valid_migration_data)

        migration.start()

        assert migration.is_in_progress is True
        assert migration.started_at is not None

    def test_migration_complete(self, valid_migration_data):
        """Test completing a migration."""
        migration = VersionMigration.create(**valid_migration_data)
        migration.start()

        migration.complete()

        assert migration.is_completed is True
        assert migration.completed_at is not None

    def test_migration_fail(self, valid_migration_data):
        """Test failing a migration."""
        migration = VersionMigration.create(**valid_migration_data)
        error = {"message": "Connection timeout"}

        migration.fail(error)

        assert migration.is_failed is True
        assert migration.completed_at is not None
        assert len(migration.error_log) == 1

    def test_migration_cancel(self, valid_migration_data):
        """Test cancelling a migration."""
        migration = VersionMigration.create(**valid_migration_data)

        migration.cancel()

        assert migration.is_cancelled is True
        assert migration.completed_at is not None

    def test_record_success(self, valid_migration_data):
        """Test recording successful migration."""
        migration = VersionMigration.create(**valid_migration_data)

        migration.record_success(10)

        assert migration.contacts_migrated == 10

    def test_record_failure(self, valid_migration_data):
        """Test recording migration failure."""
        migration = VersionMigration.create(**valid_migration_data)
        error = {"contact_id": "123", "error": "Invalid state"}

        migration.record_failure(error)

        assert migration.contacts_failed == 1
        assert len(migration.error_log) == 1

    def test_completion_percentage(self, valid_migration_data):
        """Test completion percentage calculation."""
        migration = VersionMigration.create(**valid_migration_data)
        migration.contacts_total = 100

        assert migration.completion_percentage == 0.0

        migration.record_success(50)
        assert migration.completion_percentage == 50.0

        migration.record_success(50)
        assert migration.completion_percentage == 100.0

    def test_remaining_contacts(self, valid_migration_data):
        """Test remaining contacts calculation."""
        migration = VersionMigration.create(**valid_migration_data)
        migration.contacts_total = 100

        assert migration.remaining_contacts == 100

        migration.record_success(30)
        assert migration.remaining_contacts == 70


class TestVersionDiff:
    """Test suite for VersionDiff value object."""

    def test_create_version_diff(self):
        """Test creating a version diff."""
        diff = VersionDiff(
            from_version_number=1,
            to_version_number=2,
            trigger_changed=True,
            added_actions=[{"id": "action-2", "type": "send_sms"}],
            removed_actions=[],
            modified_actions=[],
            total_changes=2,
            breaking_changes=0,
        )

        assert diff.from_version_number == 1
        assert diff.to_version_number == 2
        assert diff.trigger_changed is True

    def test_diff_to_dict(self):
        """Test converting diff to dictionary."""
        diff = VersionDiff(
            from_version_number=1,
            to_version_number=2,
            total_changes=3,
            breaking_changes=1,
        )

        diff_dict = diff.to_dict()

        assert diff_dict["from_version"] == 1
        assert diff_dict["to_version"] == 2
        assert "diff" in diff_dict
        assert "summary" in diff_dict
