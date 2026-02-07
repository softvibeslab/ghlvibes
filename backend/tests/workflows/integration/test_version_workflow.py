"""End-to-end integration tests for workflow versioning.

Tests the complete workflow from version creation through
publishing, comparison, and rollback.
"""

import pytest
from uuid import uuid4, UUID
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.workflows.application.use_cases.create_version import CreateVersionUseCase
from src.workflows.application.use_cases.list_versions import ListVersionsUseCase
from src.workflows.application.use_cases.publish_version import PublishVersionUseCase
from src.workflows.application.use_cases.rollback_version import RollbackVersionUseCase
from src.workflows.application.use_cases.compare_versions import CompareVersionsUseCase
from src.workflows.application.version_dtos import CreateVersionDTO, PublishVersionDTO
from src.workflows.domain.version_entities import WorkflowVersion
from src.workflows.infrastructure.version_repository import WorkflowVersionRepository


@pytest.mark.asyncio
class TestWorkflowVersioningIntegration:
    """Integration tests for workflow versioning."""

    @pytest.fixture
    def workflow_id(self) -> UUID:
        """Provide test workflow ID."""
        return uuid4()

    @pytest.fixture
    def account_id(self) -> UUID:
        """Provide test account ID."""
        return uuid4()

    @pytest.fixture
    def user_id(self) -> UUID:
        """Provide test user ID."""
        return uuid4()

    async def test_complete_version_lifecycle(
        self, db: AsyncSession, workflow_id, account_id, user_id
    ):
        """Test complete version lifecycle from creation to rollback."""
        repo = WorkflowVersionRepository(db)

        # Step 1: Create initial version
        v1 = WorkflowVersion.create(
            workflow_id=workflow_id,
            account_id=account_id,
            version_number=1,
            name="Initial Workflow",
            created_by=user_id,
            trigger_type="webhook",
            actions=[{"id": "action-1", "type": "send_email"}],
        )
        v1.publish()
        await repo.create(v1)
        await db.commit()

        # Verify v1 is current
        current = await repo.get_current_version(workflow_id, account_id)
        assert current is not None
        assert current.version_number.value == 1
        assert current.is_current is True

        # Step 2: Create new version
        create_dto = CreateVersionDTO(
            change_summary="Added SMS action",
            publish_immediately=False,
        )
        create_use_case = CreateVersionUseCase(db)

        # Note: This would normally get workflow from workflow repository
        # For this test, we'll manually create the second version
        v2 = WorkflowVersion.create(
            workflow_id=workflow_id,
            account_id=account_id,
            version_number=2,
            name="Initial Workflow",
            created_by=user_id,
            trigger_type="webhook",
            actions=[
                {"id": "action-1", "type": "send_email"},
                {"id": "action-2", "type": "send_sms"},  # New action
            ],
            change_summary="Added SMS action",
            is_current=False,
        )
        await repo.create(v2)
        await db.commit()

        # Verify v2 is draft
        saved_v2 = await repo.get_by_workflow_and_number(workflow_id, account_id, 2)
        assert saved_v2 is not None
        assert saved_v2.is_draft is True

        # Step 3: Publish v2
        publish_dto = PublishVersionDTO(
            migration_strategy="immediate",
            batch_size=100,
        )
        publish_use_case = PublishVersionUseCase(db)

        result = await publish_use_case.execute(
            workflow_id=workflow_id,
            version_id=v2.id,
            account_id=account_id,
            user_id=user_id,
            dto=publish_dto,
        )

        assert result.is_current is True
        assert result.is_active is True

        # Verify v1 is no longer current
        v1_check = await repo.get_by_workflow_and_number(workflow_id, account_id, 1)
        assert v1_check.is_current is False

        # Step 4: Compare versions
        compare_use_case = CompareVersionsUseCase(db)
        diff = await compare_use_case.execute(
            workflow_id=workflow_id,
            account_id=account_id,
            from_version=1,
            to_version=2,
        )

        assert diff.from_version == 1
        assert diff.to_version == 2
        assert len(diff.diff.actions.added) == 1

        # Step 5: List versions
        list_use_case = ListVersionsUseCase(db)
        list_result = await list_use_case.execute(
            workflow_id=workflow_id,
            account_id=account_id,
            include_archived=False,
            page=1,
            per_page=10,
        )

        assert len(list_result.versions) == 2
        assert list_result.pagination.total == 2

        # Step 6: Rollback to v1
        rollback_use_case = RollbackVersionUseCase(db)
        rollback_result = await rollback_use_case.execute(
            workflow_id=workflow_id,
            version_id=v1.id,
            account_id=account_id,
            user_id=user_id,
        )

        assert rollback_result.is_current is True
        assert rollback_result.rollback_info.rolled_back_from == 2

        # Verify v2 is no longer current
        v2_check = await repo.get_by_workflow_and_number(workflow_id, account_id, 2)
        assert v2_check.is_current is False

    async def test_version_execution_tracking(
        self, db: AsyncSession, workflow_id, account_id, user_id
    ):
        """Test execution count tracking on versions."""
        repo = WorkflowVersionRepository(db)

        # Create active version
        v1 = WorkflowVersion.create(
            workflow_id=workflow_id,
            account_id=account_id,
            version_number=1,
            name="Test Workflow",
            created_by=user_id,
            actions=[],
        )
        v1.publish()
        created_v1 = await repo.create(v1)

        # Increment executions
        await repo.increment_executions(created_v1.id, account_id)
        await repo.increment_executions(created_v1.id, account_id)
        await db.commit()

        # Verify count
        check = await repo.get_by_id(created_v1.id, account_id)
        assert check.active_executions == 2

        # Decrement executions
        await repo.decrement_executions(created_v1.id, account_id)
        await db.commit()

        # Verify decrement
        check = await repo.get_by_id(created_v1.id, account_id)
        assert check.active_executions == 1

    async def test_version_number_sequencing(
        self, db: AsyncSession, workflow_id, account_id, user_id
    ):
        """Test version numbers are assigned sequentially."""
        repo = WorkflowVersionRepository(db)

        # Create multiple versions
        for i in range(1, 6):
            next_number = await repo.get_next_version_number(workflow_id, account_id)
            assert next_number == i

            version = WorkflowVersion.create(
                workflow_id=workflow_id,
                account_id=account_id,
                version_number=next_number,
                name=f"Version {i}",
                created_by=user_id,
                actions=[],
            )
            await repo.create(version)

        await db.commit()

        # Verify all versions exist
        all_versions, total = await repo.list_versions(
            workflow_id=workflow_id,
            account_id=account_id,
            include_archived=False,
            limit=100,
            offset=0,
        )

        assert total == 5
        assert len(all_versions) == 5

        # Verify sequential numbering
        version_numbers = [v.version_number.value for v in all_versions]
        assert sorted(version_numbers, reverse=True) == version_numbers

    async def test_max_versions_limit(
        self, db: AsyncSession, workflow_id, account_id, user_id
    ):
        """Test maximum versions limit enforcement."""
        repo = WorkflowVersionRepository(db)

        # This test is conceptual - actual max is 1000
        # We'll test the count mechanism works
        for i in range(10):
            version = WorkflowVersion.create(
                workflow_id=workflow_id,
                account_id=account_id,
                version_number=i + 1,
                name=f"Version {i + 1}",
                created_by=user_id,
                actions=[],
            )
            await repo.create(version)

        await db.commit()

        count = await repo.count_versions(workflow_id, account_id)
        assert count == 10

    async def test_version_archival(
        self, db: AsyncSession, workflow_id, account_id, user_id
    ):
        """Test version archival process."""
        repo = WorkflowVersionRepository(db)

        # Create old version with no executions
        v1 = WorkflowVersion.create(
            workflow_id=workflow_id,
            account_id=account_id,
            version_number=1,
            name="Old Workflow",
            created_by=user_id,
            actions=[],
        )
        v1.publish()
        created_v1 = await repo.create(v1)

        # Create new version
        v2 = WorkflowVersion.create(
            workflow_id=workflow_id,
            account_id=account_id,
            version_number=2,
            name="New Workflow",
            created_by=user_id,
            actions=[],
        )
        v2.publish()

        # Deactivate v1
        created_v1.deactivate_current()
        await repo.update(created_v1)
        await repo.create(v2)
        await db.commit()

        # Archive v1 (no active executions)
        await db.refresh(created_v1)
        created_v1.archive()
        archived_v1 = await repo.update(created_v1)

        assert archived_v1.is_archived is True
        assert archived_v1.archived_at is not None

    async def test_draft_auto_save_simulation(
        self, db: AsyncSession, workflow_id, account_id, user_id
    ):
        """Test draft auto-save functionality."""
        repo = WorkflowVersionRepository(db)

        # Simulate auto-save
        draft_data = {
            "name": "Draft Workflow",
            "actions": [{"id": "action-1", "type": "send_email"}],
            "last_edited": datetime.now(UTC).isoformat(),
        }

        await repo.save_draft(
            workflow_id=workflow_id,
            user_id=user_id,
            account_id=account_id,
            draft_data=draft_data,
        )
        await db.commit()

        # Retrieve draft
        retrieved_draft = await repo.get_draft(
            workflow_id=workflow_id,
            user_id=user_id,
            account_id=account_id,
        )

        assert retrieved_draft is not None
        assert retrieved_draft["name"] == "Draft Workflow"

        # Delete draft after version creation
        await repo.delete_draft(
            workflow_id=workflow_id,
            user_id=user_id,
            account_id=account_id,
        )
        await db.commit()

        # Verify deletion
        deleted_draft = await repo.get_draft(
            workflow_id=workflow_id,
            user_id=user_id,
            account_id=account_id,
        )

        assert deleted_draft is None
