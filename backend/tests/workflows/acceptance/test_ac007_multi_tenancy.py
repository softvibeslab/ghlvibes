"""Acceptance test for AC-007: Multi-tenancy isolation.

Gherkin Scenario:
  GIVEN a user from Account A
  AND a workflow exists in Account A
  WHEN a user from Account B attempts to access the workflow
  THEN the system should deny access (404 Not Found)
  AND Account B should not see Account A workflows in listings

Acceptance Criteria: AC-007
Requirement: REQ-WFL-001-08
"""

from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.workflows.infrastructure.models import AccountModel, UserModel, WorkflowModel
from datetime import UTC, datetime


@pytest.mark.e2e
@pytest.mark.acceptance
class TestAC007MultiTenancyIsolation:
    """Verify multi-tenancy isolation is enforced."""

    @pytest.fixture
    async def setup_two_accounts(self, db_session: AsyncSession):
        """Create two separate accounts with users."""
        # Account A
        account_a = AccountModel(
            id=uuid4(),
            name="Account A",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db_session.add(account_a)

        user_a = UserModel(
            id=uuid4(),
            email="user_a@example.com",
            account_id=account_a.id,
            created_at=datetime.now(UTC),
        )
        db_session.add(user_a)

        # Account B
        account_b = AccountModel(
            id=uuid4(),
            name="Account B",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db_session.add(account_b)

        user_b = UserModel(
            id=uuid4(),
            email="user_b@example.com",
            account_id=account_b.id,
            created_at=datetime.now(UTC),
        )
        db_session.add(user_b)

        await db_session.flush()

        return {
            "account_a": account_a,
            "user_a": user_a,
            "account_b": account_b,
            "user_b": user_b,
        }

    @pytest.fixture
    async def create_workflow_in_account_a(
        self,
        db_session: AsyncSession,
        setup_two_accounts,
    ):
        """Create a workflow in Account A."""
        account_a = setup_two_accounts["account_a"]
        user_a = setup_two_accounts["user_a"]

        workflow = WorkflowModel(
            id=uuid4(),
            account_id=account_a.id,
            name="Account A Workflow",
            status="draft",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            created_by=user_a.id,
            updated_by=user_a.id,
        )
        db_session.add(workflow)
        await db_session.flush()

        return workflow

    @pytest.mark.asyncio
    async def test_account_b_cannot_access_account_a_workflow(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        setup_two_accounts,
        create_workflow_in_account_a,
    ) -> None:
        """
        AC-007: Verify Account B cannot access Account A workflow by ID.

        Given:
          - Workflow exists in Account A
          - User is authenticated from Account B

        When:
          - User attempts to GET Account A workflow by ID

        Then:
          - System returns 404 Not Found
          - No data is leaked
        """
        account_b = setup_two_accounts["account_b"]
        workflow_a = create_workflow_in_account_a

        # Create auth headers for Account B user
        auth_headers_b = {
            "Authorization": f"Bearer fake_token_for_{setup_two_accounts['user_b'].id}"
        }

        # Attempt to access Account A workflow
        response = await client.get(
            f"/api/v1/workflows/{workflow_a.id}",
            headers=auth_headers_b,
        )

        # Assert: Access denied
        assert response.status_code == 404

        data = response.json()
        assert "not_found" in str(data.get("detail", {})).lower() or "not found" in str(data.get("detail", "")).lower()

    @pytest.mark.asyncio
    async def test_account_b_listing_does_not_show_account_a_workflows(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        setup_two_accounts,
        create_workflow_in_account_a,
    ) -> None:
        """
        AC-007: Verify Account B listing doesn't show Account A workflows.

        Given:
          - Multiple workflows exist in Account A
          - User is authenticated from Account B

        When:
          - User lists all workflows

        Then:
          - Only Account B workflows are returned
          - Account A workflows are not visible
        """
        # Create additional workflows in Account A
        account_a = setup_two_accounts["account_a"]
        user_a = setup_two_accounts["user_a"]

        for i in range(3):
            workflow = WorkflowModel(
                id=uuid4(),
                account_id=account_a.id,
                name=f"Account A Workflow {i}",
                status="draft",
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                created_by=user_a.id,
                updated_by=user_a.id,
            )
            db_session.add(workflow)

        await db_session.flush()

        # Create auth headers for Account B
        auth_headers_b = {
            "Authorization": f"Bearer fake_token_for_{setup_two_accounts['user_b'].id}"
        }

        # List workflows as Account B user
        response = await client.get(
            "/api/v1/workflows",
            headers=auth_headers_b,
        )

        # Assert: Only Account B workflows returned
        assert response.status_code == 200
        data = response.json()

        # Account A workflows should not be present
        workflow_names = [w["name"] for w in data["items"]]
        for name in workflow_names:
            assert "Account A" not in name, "Account A workflow leaked into Account B listing"

    @pytest.mark.asyncio
    async def test_account_b_cannot_update_account_a_workflow(
        self,
        client: AsyncClient,
        setup_two_accounts,
        create_workflow_in_account_a,
    ) -> None:
        """
        AC-007: Verify Account B cannot update Account A workflow.

        Given:
          - Workflow exists in Account A
          - User is authenticated from Account B

        When:
          - User attempts to PATCH Account A workflow

        Then:
          - System returns 404 Not Found
          - Workflow is not modified
        """
        account_b = setup_two_accounts["account_b"]
        workflow_a = create_workflow_in_account_a

        auth_headers_b = {
            "Authorization": f"Bearer fake_token_for_{account_b.id}"
        }

        response = await client.patch(
            f"/api/v1/workflows/{workflow_a.id}",
            json={"name": "Attempted Update"},
            headers=auth_headers_b,
        )

        # Assert: Update denied
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_account_b_cannot_delete_account_a_workflow(
        self,
        client: AsyncClient,
        setup_two_accounts,
        create_workflow_in_account_a,
    ) -> None:
        """
        AC-007: Verify Account B cannot delete Account A workflow.

        Given:
          - Workflow exists in Account A
          - User is authenticated from Account B

        When:
          - User attempts to DELETE Account A workflow

        Then:
          - System returns 404 Not Found
          - Workflow is not deleted
        """
        account_b = setup_two_accounts["account_b"]
        workflow_a = create_workflow_in_account_a

        auth_headers_b = {
            "Authorization": f"Bearer fake_token_for_{account_b.id}"
        }

        response = await client.delete(
            f"/api/v1/workflows/{workflow_a.id}",
            headers=auth_headers_b,
        )

        # Assert: Deletion denied
        assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.acceptance
class TestAC007RepositoryIsolation:
    """Integration tests for repository-level tenant isolation."""

    @pytest.mark.asyncio
    async def test_repository_filters_by_account_id(
        self,
        db_session: AsyncSession,
    ) -> None:
        """
        AC-007: Verify repository queries enforce account isolation.

        Given:
          - Workflows exist for multiple accounts in database
          - Repository is queried with specific account_id

        When:
          - get_by_id is called with different account_id

        Then:
          - Workflow is not returned
          - None is returned instead
        """
        from src.workflows.infrastructure.repositories import WorkflowRepository

        account_a = uuid4()
        account_b = uuid4()
        user_id = uuid4()

        repo = WorkflowRepository(db_session)

        # Create workflow for Account A
        from src.workflows.domain.entities import Workflow

        workflow_a = Workflow.create(
            account_id=account_a,
            name="Account A Workflow",
            created_by=user_id,
        )

        # Persist workflow
        await repo.create(workflow_a)
        await db_session.flush()

        # Try to retrieve with Account B context
        result = await repo.get_by_id(
            workflow_id=workflow_a.id,
            account_id=account_b,  # Different account!
        )

        # Assert: Not found
        assert result is None, "Repository should not return workflow for different account"

    @pytest.mark.asyncio
    async def test_repository_list_filters_by_account(
        self,
        db_session: AsyncSession,
    ) -> None:
        """
        AC-007: Verify list_by_account only returns workflows for that account.

        Given:
          - Workflows exist for Account A and Account B

        When:
          - list_by_account is called for Account A

        Then:
          - Only Account A workflows are returned
          - Account B workflows are excluded
        """
        from src.workflows.infrastructure.repositories import WorkflowRepository
        from src.workflows.domain.entities import Workflow

        account_a = uuid4()
        account_b = uuid4()
        user_id = uuid4()

        repo = WorkflowRepository(db_session)

        # Create workflows for Account A
        for i in range(3):
            workflow = Workflow.create(
                account_id=account_a,
                name=f"Account A {i}",
                created_by=user_id,
            )
            await repo.create(workflow)

        # Create workflows for Account B
        for i in range(2):
            workflow = Workflow.create(
                account_id=account_b,
                name=f"Account B {i}",
                created_by=user_id,
            )
            await repo.create(workflow)

        await db_session.flush()

        # List Account A workflows
        workflows_a = await repo.list_by_account(account_id=account_a)

        # Assert: Only Account A workflows returned
        assert len(workflows_a) == 3
        for wf in workflows_a:
            assert wf.account_id == account_a
            assert "Account B" not in wf.name_value
