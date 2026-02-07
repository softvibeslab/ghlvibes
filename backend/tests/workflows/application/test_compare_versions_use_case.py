"""Integration tests for CompareVersionsUseCase."""

import pytest
from uuid import uuid4
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.workflows.application.use_cases.compare_versions import CompareVersionsUseCase
from src.workflows.domain.version_entities import WorkflowVersion
from src.workflows.infrastructure.version_repository import WorkflowVersionRepository


@pytest.mark.asyncio
class TestCompareVersionsUseCase:
    """Test suite for CompareVersionsUseCase."""

    @pytest.fixture
    def workflow_id(self):
        """Provide test workflow ID."""
        return uuid4()

    @pytest.fixture
    def account_id(self):
        """Provide test account ID."""
        return uuid4()

    @pytest.fixture
    async def sample_versions(self, db: AsyncSession, workflow_id, account_id):
        """Create sample versions for testing."""
        repo = WorkflowVersionRepository(db)

        # Create version 1
        v1 = WorkflowVersion.create(
            workflow_id=workflow_id,
            account_id=account_id,
            version_number=1,
            name="Workflow v1",
            created_by=uuid4(),
            trigger_type="webhook",
            trigger_config={"url": "https://example.com/webhook"},
            actions=[
                {"id": "action-1", "type": "send_email", "config": {"to": "user@example.com"}},
                {"id": "action-2", "type": "wait", "config": {"duration": 60}},
            ],
            conditions=[],
        )
        await repo.create(v1)

        # Create version 2 with changes
        v2 = WorkflowVersion.create(
            workflow_id=workflow_id,
            account_id=account_id,
            version_number=2,
            name="Workflow v2",
            created_by=uuid4(),
            trigger_type="webhook",
            trigger_config={"url": "https://example.com/webhook"},  # Same trigger
            actions=[
                {"id": "action-1", "type": "send_email", "config": {"to": "admin@example.com"}},  # Modified
                {"id": "action-2", "type": "wait", "config": {"duration": 60}},  # Same
                {"id": "action-3", "type": "send_sms", "config": {"to": "+1234567890"}},  # Added
            ],
            # action-2 removed, action-3 added, action-1 modified
            conditions=[],
        )
        await repo.create(v2)

        await db.commit()

        return {"v1": v1, "v2": v2}

    async def test_compare_versions_success(
        self, db: AsyncSession, workflow_id, account_id, sample_versions
    ):
        """Test successful version comparison."""
        use_case = CompareVersionsUseCase(db)

        result = await use_case.execute(
            workflow_id=workflow_id,
            account_id=account_id,
            from_version=1,
            to_version=2,
        )

        assert result.from_version == 1
        assert result.to_version == 2
        assert result.diff.trigger.changed is False
        assert len(result.diff.actions.added) == 1
        assert len(result.diff.actions.modified) == 1
        assert result.summary.total_changes > 0

    async def test_compare_nonexistent_version_raises_error(
        self, db: AsyncSession, workflow_id, account_id
    ):
        """Test comparing non-existent version raises error."""
        use_case = CompareVersionsUseCase(db)

        with pytest.raises(Exception) as exc_info:
            await use_case.execute(
                workflow_id=workflow_id,
                account_id=account_id,
                from_version=1,
                to_version=999,
            )

        assert "not found" in str(exc_info.value).lower()

    async def test_trigger_change_detected(
        self, db: AsyncSession, workflow_id, account_id
    ):
        """Test trigger configuration change is detected."""
        repo = WorkflowVersionRepository(db)

        # Create versions with different triggers
        v1 = WorkflowVersion.create(
            workflow_id=workflow_id,
            account_id=account_id,
            version_number=1,
            name="Workflow v1",
            created_by=uuid4(),
            trigger_type="webhook",
            trigger_config={"url": "https://example.com/old"},
            actions=[],
        )
        await repo.create(v1)

        v2 = WorkflowVersion.create(
            workflow_id=workflow_id,
            account_id=account_id,
            version_number=2,
            name="Workflow v2",
            created_by=uuid4(),
            trigger_type="webhook",
            trigger_config={"url": "https://example.com/new"},
            actions=[],
        )
        await repo.create(v2)

        await db.commit()

        use_case = CompareVersionsUseCase(db)
        result = await use_case.execute(
            workflow_id=workflow_id,
            account_id=account_id,
            from_version=1,
            to_version=2,
        )

        assert result.diff.trigger.changed is True

    async def test_action_added_detected(
        self, db: AsyncSession, workflow_id, account_id
    ):
        """Test added action is detected."""
        repo = WorkflowVersionRepository(db)

        v1 = WorkflowVersion.create(
            workflow_id=workflow_id,
            account_id=account_id,
            version_number=1,
            name="Workflow v1",
            created_by=uuid4(),
            actions=[{"id": "action-1", "type": "send_email"}],
        )
        await repo.create(v1)

        v2 = WorkflowVersion.create(
            workflow_id=workflow_id,
            account_id=account_id,
            version_number=2,
            name="Workflow v2",
            created_by=uuid4(),
            actions=[
                {"id": "action-1", "type": "send_email"},
                {"id": "action-2", "type": "send_sms"},  # Added
            ],
        )
        await repo.create(v2)

        await db.commit()

        use_case = CompareVersionsUseCase(db)
        result = await use_case.execute(
            workflow_id=workflow_id,
            account_id=account_id,
            from_version=1,
            to_version=2,
        )

        assert len(result.diff.actions.added) == 1
        assert result.diff.actions.added[0]["id"] == "action-2"

    async def test_action_removed_detected(
        self, db: AsyncSession, workflow_id, account_id
    ):
        """Test removed action is detected."""
        repo = WorkflowVersionRepository(db)

        v1 = WorkflowVersion.create(
            workflow_id=workflow_id,
            account_id=account_id,
            version_number=1,
            name="Workflow v1",
            created_by=uuid4(),
            actions=[
                {"id": "action-1", "type": "send_email"},
                {"id": "action-2", "type": "send_sms"},
            ],
        )
        await repo.create(v1)

        v2 = WorkflowVersion.create(
            workflow_id=workflow_id,
            account_id=account_id,
            version_number=2,
            name="Workflow v2",
            created_by=uuid4(),
            actions=[{"id": "action-1", "type": "send_email"}],  # action-2 removed
        )
        await repo.create(v2)

        await db.commit()

        use_case = CompareVersionsUseCase(db)
        result = await use_case.execute(
            workflow_id=workflow_id,
            account_id=account_id,
            from_version=1,
            to_version=2,
        )

        assert len(result.diff.actions.removed) == 1
        assert result.diff.actions.removed[0]["id"] == "action-2"

    async def test_action_modified_detected(
        self, db: AsyncSession, workflow_id, account_id
    ):
        """Test modified action is detected."""
        repo = WorkflowVersionRepository(db)

        v1 = WorkflowVersion.create(
            workflow_id=workflow_id,
            account_id=account_id,
            version_number=1,
            name="Workflow v1",
            created_by=uuid4(),
            actions=[{"id": "action-1", "type": "send_email", "to": "old@example.com"}],
        )
        await repo.create(v1)

        v2 = WorkflowVersion.create(
            workflow_id=workflow_id,
            account_id=account_id,
            version_number=2,
            name="Workflow v2",
            created_by=uuid4(),
            actions=[{"id": "action-1", "type": "send_email", "to": "new@example.com"}],
        )
        await repo.create(v2)

        await db.commit()

        use_case = CompareVersionsUseCase(db)
        result = await use_case.execute(
            workflow_id=workflow_id,
            account_id=account_id,
            from_version=1,
            to_version=2,
        )

        assert len(result.diff.actions.modified) == 1
        assert result.diff.actions.modified[0]["id"] == "action-1"

    async def test_breaking_changes_counted(
        self, db: AsyncSession, workflow_id, account_id
    ):
        """Test breaking changes are counted correctly."""
        repo = WorkflowVersionRepository(db)

        v1 = WorkflowVersion.create(
            workflow_id=workflow_id,
            account_id=account_id,
            version_number=1,
            name="Workflow v1",
            created_by=uuid4(),
            trigger_type="webhook",
            actions=[{"id": "action-1", "type": "send_email"}],
        )
        await repo.create(v1)

        v2 = WorkflowVersion.create(
            workflow_id=workflow_id,
            account_id=account_id,
            version_number=2,
            name="Workflow v2",
            created_by=uuid4(),
            trigger_type="manual",  # Breaking change
            actions=[],  # Breaking change (action-1 removed)
        )
        await repo.create(v2)

        await db.commit()

        use_case = CompareVersionsUseCase(db)
        result = await use_case.execute(
            workflow_id=workflow_id,
            account_id=account_id,
            from_version=1,
            to_version=2,
        )

        # Trigger change (1) + removed action (1) = 2 breaking changes
        assert result.summary.breaking_changes >= 2
