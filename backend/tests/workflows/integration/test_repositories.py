"""Integration tests for workflow repositories.

These tests verify repository implementations work correctly
with a real database.

Note: These tests require a running PostgreSQL database.
Skip with: pytest -m "not integration" to run only unit tests.
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.workflows.domain.entities import Workflow
from src.workflows.domain.value_objects import WorkflowStatus
from src.workflows.infrastructure.models import AccountModel, UserModel, WorkflowModel
from src.workflows.infrastructure.repositories import (
    AuditLogRepository,
    WorkflowRepository,
)


@pytest.mark.integration
class TestWorkflowRepository:
    """Integration tests for WorkflowRepository."""

    @pytest.fixture
    async def account(self, db_session):
        """Create test account in database."""
        account = AccountModel(
            id=uuid4(),
            name="Test Account",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db_session.add(account)
        await db_session.flush()
        return account

    @pytest.fixture
    async def user(self, db_session, account):
        """Create test user in database."""
        user = UserModel(
            id=uuid4(),
            email="test@example.com",
            account_id=account.id,
            created_at=datetime.now(UTC),
        )
        db_session.add(user)
        await db_session.flush()
        return user

    @pytest.fixture
    def repository(self, db_session) -> WorkflowRepository:
        """Create repository with test session."""
        return WorkflowRepository(db_session)

    @pytest.mark.asyncio
    async def test_create_workflow(self, repository, account, user) -> None:
        """Test creating a workflow in the database."""
        workflow = Workflow.create(
            account_id=account.id,
            name="Test Workflow",
            created_by=user.id,
            description="Integration test workflow",
            trigger_type="contact_created",
        )

        result = await repository.create(workflow)

        assert result.id == workflow.id
        assert result.name_value == "Test Workflow"
        assert result.status == WorkflowStatus.DRAFT

    @pytest.mark.asyncio
    async def test_get_workflow_by_id(self, repository, account, user) -> None:
        """Test retrieving a workflow by ID."""
        workflow = Workflow.create(
            account_id=account.id,
            name="Get By ID Test",
            created_by=user.id,
        )
        await repository.create(workflow)

        result = await repository.get_by_id(
            workflow_id=workflow.id,
            account_id=account.id,
        )

        assert result is not None
        assert result.id == workflow.id
        assert result.name_value == "Get By ID Test"

    @pytest.mark.asyncio
    async def test_get_workflow_by_id_wrong_account(
        self, repository, account, user, db_session
    ) -> None:
        """Test that workflows are account-isolated."""
        workflow = Workflow.create(
            account_id=account.id,
            name="Isolation Test",
            created_by=user.id,
        )
        await repository.create(workflow)

        # Try to get with different account ID
        result = await repository.get_by_id(
            workflow_id=workflow.id,
            account_id=uuid4(),
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_get_workflow_by_name(self, repository, account, user) -> None:
        """Test retrieving a workflow by name."""
        workflow = Workflow.create(
            account_id=account.id,
            name="Unique Name Test",
            created_by=user.id,
        )
        await repository.create(workflow)

        result = await repository.get_by_name(
            name="Unique Name Test",
            account_id=account.id,
        )

        assert result is not None
        assert result.id == workflow.id

    @pytest.mark.asyncio
    async def test_list_workflows(self, repository, account, user) -> None:
        """Test listing workflows."""
        for i in range(5):
            workflow = Workflow.create(
                account_id=account.id,
                name=f"List Test {i}",
                created_by=user.id,
            )
            await repository.create(workflow)

        results = await repository.list_by_account(
            account_id=account.id,
            offset=0,
            limit=10,
        )

        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_list_workflows_with_pagination(
        self, repository, account, user
    ) -> None:
        """Test workflow list pagination."""
        for i in range(10):
            workflow = Workflow.create(
                account_id=account.id,
                name=f"Pagination Test {i:02d}",
                created_by=user.id,
            )
            await repository.create(workflow)

        # Get first page
        page1 = await repository.list_by_account(
            account_id=account.id,
            offset=0,
            limit=5,
        )
        assert len(page1) == 5

        # Get second page
        page2 = await repository.list_by_account(
            account_id=account.id,
            offset=5,
            limit=5,
        )
        assert len(page2) == 5

        # Ensure no duplicates
        page1_ids = {w.id for w in page1}
        page2_ids = {w.id for w in page2}
        assert not page1_ids.intersection(page2_ids)

    @pytest.mark.asyncio
    async def test_list_workflows_with_status_filter(
        self, repository, account, user
    ) -> None:
        """Test filtering workflows by status."""
        # Create draft workflow
        draft = Workflow.create(
            account_id=account.id,
            name="Draft Workflow",
            created_by=user.id,
        )
        await repository.create(draft)

        # Create active workflow
        active = Workflow.create(
            account_id=account.id,
            name="Active Workflow",
            created_by=user.id,
        )
        active.activate(updated_by=user.id)
        await repository.create(active)

        # Filter by active status
        results = await repository.list_by_account(
            account_id=account.id,
            status=WorkflowStatus.ACTIVE,
        )

        assert len(results) == 1
        assert results[0].is_active

    @pytest.mark.asyncio
    async def test_update_workflow(self, repository, account, user) -> None:
        """Test updating a workflow."""
        workflow = Workflow.create(
            account_id=account.id,
            name="Update Test Original",
            created_by=user.id,
        )
        await repository.create(workflow)

        # Update the workflow
        workflow.update(
            updated_by=user.id,
            name="Update Test Modified",
            description="Updated description",
        )
        result = await repository.update(workflow)

        assert result.name_value == "Update Test Modified"
        assert result.description == "Updated description"
        assert result.version == 2

    @pytest.mark.asyncio
    async def test_soft_delete_workflow(self, repository, account, user) -> None:
        """Test soft deleting a workflow."""
        workflow = Workflow.create(
            account_id=account.id,
            name="Delete Test",
            created_by=user.id,
        )
        await repository.create(workflow)

        # Delete the workflow
        deleted = await repository.delete(
            workflow_id=workflow.id,
            account_id=account.id,
            deleted_by=user.id,
        )

        assert deleted is True

        # Verify it's not returned in queries
        result = await repository.get_by_id(
            workflow_id=workflow.id,
            account_id=account.id,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_count_workflows(self, repository, account, user) -> None:
        """Test counting workflows."""
        for i in range(3):
            workflow = Workflow.create(
                account_id=account.id,
                name=f"Count Test {i}",
                created_by=user.id,
            )
            await repository.create(workflow)

        count = await repository.count_by_account(account_id=account.id)

        assert count == 3


@pytest.mark.integration
class TestAuditLogRepository:
    """Integration tests for AuditLogRepository."""

    @pytest.fixture
    async def account(self, db_session):
        """Create test account."""
        account = AccountModel(
            id=uuid4(),
            name="Audit Test Account",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db_session.add(account)
        await db_session.flush()
        return account

    @pytest.fixture
    async def user(self, db_session, account):
        """Create test user."""
        user = UserModel(
            id=uuid4(),
            email="audit@example.com",
            account_id=account.id,
            created_at=datetime.now(UTC),
        )
        db_session.add(user)
        await db_session.flush()
        return user

    @pytest.fixture
    async def workflow(self, db_session, account, user):
        """Create test workflow."""
        workflow = WorkflowModel(
            id=uuid4(),
            account_id=account.id,
            name="Audit Test Workflow",
            status=WorkflowStatus.DRAFT,
            trigger_config={},
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            created_by=user.id,
        )
        db_session.add(workflow)
        await db_session.flush()
        return workflow

    @pytest.fixture
    def repository(self, db_session) -> AuditLogRepository:
        """Create repository with test session."""
        return AuditLogRepository(db_session)

    @pytest.mark.asyncio
    async def test_create_audit_log(
        self, repository, workflow, user
    ) -> None:
        """Test creating an audit log entry."""
        await repository.create(
            workflow_id=workflow.id,
            action="created",
            changed_by=user.id,
            new_values={"name": "Test"},
            ip_address="192.168.1.1",
            user_agent="Test/1.0",
        )

        logs = await repository.list_by_workflow(workflow_id=workflow.id)

        assert len(logs) == 1
        assert logs[0]["action"] == "created"
        assert logs[0]["ip_address"] == "192.168.1.1"

    @pytest.mark.asyncio
    async def test_list_audit_logs_ordered(
        self, repository, workflow, user
    ) -> None:
        """Test audit logs are ordered by time (newest first)."""
        for action in ["created", "updated", "activated"]:
            await repository.create(
                workflow_id=workflow.id,
                action=action,
                changed_by=user.id,
            )

        logs = await repository.list_by_workflow(workflow_id=workflow.id)

        assert len(logs) == 3
        # Most recent should be first
        assert logs[0]["action"] == "activated"
        assert logs[2]["action"] == "created"
