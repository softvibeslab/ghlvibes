"""End-to-end tests for workflow API endpoints.

These tests verify the full request/response cycle through
the API layer.

Note: These tests require a running database.
Skip with: pytest -m "not e2e" to run only unit tests.
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.workflows.domain.value_objects import WorkflowStatus
from src.workflows.infrastructure.models import AccountModel, UserModel, WorkflowModel


@pytest.mark.e2e
class TestWorkflowAPI:
    """End-to-end tests for workflow API endpoints."""

    @pytest.fixture
    async def setup_account_and_user(self, db_session):
        """Create account and user for testing."""
        account = AccountModel(
            id=uuid4(),
            name="API Test Account",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db_session.add(account)

        user = UserModel(
            id=uuid4(),
            email="api@example.com",
            account_id=account.id,
            created_at=datetime.now(UTC),
        )
        db_session.add(user)

        await db_session.flush()
        return account, user

    @pytest.mark.asyncio
    async def test_create_workflow_success(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        setup_account_and_user,
    ) -> None:
        """Test creating a workflow via API."""
        response = await client.post(
            "/api/v1/workflows",
            json={
                "name": "API Test Workflow",
                "description": "Created via API",
                "trigger_type": "contact_created",
                "trigger_config": {"filters": {"tags": ["new"]}},
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "API Test Workflow"
        assert data["status"] == "draft"
        assert data["version"] == 1
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_workflow_minimal(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        setup_account_and_user,
    ) -> None:
        """Test creating a workflow with minimal data."""
        response = await client.post(
            "/api/v1/workflows",
            json={"name": "Minimal Workflow"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Workflow"
        assert data["description"] is None
        assert data["trigger_type"] is None

    @pytest.mark.asyncio
    async def test_create_workflow_invalid_name_too_short(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ) -> None:
        """Test that short names are rejected."""
        response = await client.post(
            "/api/v1/workflows",
            json={"name": "ab"},
            headers=auth_headers,
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_create_workflow_without_auth(
        self,
        client: AsyncClient,
    ) -> None:
        """Test that unauthenticated requests are rejected."""
        response = await client.post(
            "/api/v1/workflows",
            json={"name": "Unauthorized Test"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_workflows(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        setup_account_and_user,
    ) -> None:
        """Test listing workflows."""
        # Create a few workflows first
        for i in range(3):
            await client.post(
                "/api/v1/workflows",
                json={"name": f"List Test {i}"},
                headers=auth_headers,
            )

        response = await client.get(
            "/api/v1/workflows",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "has_more" in data
        assert len(data["items"]) >= 3

    @pytest.mark.asyncio
    async def test_list_workflows_pagination(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        setup_account_and_user,
    ) -> None:
        """Test workflow list pagination."""
        # Create 10 workflows
        for i in range(10):
            await client.post(
                "/api/v1/workflows",
                json={"name": f"Pagination Test {i:02d}"},
                headers=auth_headers,
            )

        # Get first page
        response = await client.get(
            "/api/v1/workflows?limit=5&offset=0",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
        assert data["has_more"] is True

    @pytest.mark.asyncio
    async def test_list_workflows_filter_by_status(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        setup_account_and_user,
    ) -> None:
        """Test filtering workflows by status."""
        # Create a draft workflow
        await client.post(
            "/api/v1/workflows",
            json={"name": "Draft Only"},
            headers=auth_headers,
        )

        response = await client.get(
            "/api/v1/workflows?status=draft",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        # All returned should be draft
        for item in data["items"]:
            assert item["status"] == "draft"

    @pytest.mark.asyncio
    async def test_get_workflow_by_id(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        setup_account_and_user,
    ) -> None:
        """Test getting a workflow by ID."""
        # Create a workflow
        create_response = await client.post(
            "/api/v1/workflows",
            json={"name": "Get By ID Test"},
            headers=auth_headers,
        )
        workflow_id = create_response.json()["id"]

        # Get it by ID
        response = await client.get(
            f"/api/v1/workflows/{workflow_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == workflow_id
        assert data["name"] == "Get By ID Test"

    @pytest.mark.asyncio
    async def test_get_workflow_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ) -> None:
        """Test getting a non-existent workflow."""
        fake_id = uuid4()
        response = await client.get(
            f"/api/v1/workflows/{fake_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_workflow(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        setup_account_and_user,
    ) -> None:
        """Test updating a workflow."""
        # Create a workflow
        create_response = await client.post(
            "/api/v1/workflows",
            json={"name": "Original Name"},
            headers=auth_headers,
        )
        workflow_id = create_response.json()["id"]

        # Update it
        response = await client.patch(
            f"/api/v1/workflows/{workflow_id}",
            json={
                "name": "Updated Name",
                "description": "New description",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "New description"
        assert data["version"] == 2

    @pytest.mark.asyncio
    async def test_update_workflow_partial(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        setup_account_and_user,
    ) -> None:
        """Test partial update (only description)."""
        # Create a workflow
        create_response = await client.post(
            "/api/v1/workflows",
            json={"name": "Partial Update Test"},
            headers=auth_headers,
        )
        workflow_id = create_response.json()["id"]

        # Update only description
        response = await client.patch(
            f"/api/v1/workflows/{workflow_id}",
            json={"description": "Only description updated"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        # Name should remain unchanged
        assert data["name"] == "Partial Update Test"
        assert data["description"] == "Only description updated"

    @pytest.mark.asyncio
    async def test_delete_workflow(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        setup_account_and_user,
    ) -> None:
        """Test deleting a workflow."""
        # Create a workflow
        create_response = await client.post(
            "/api/v1/workflows",
            json={"name": "To Be Deleted"},
            headers=auth_headers,
        )
        workflow_id = create_response.json()["id"]

        # Delete it
        response = await client.delete(
            f"/api/v1/workflows/{workflow_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify it's gone
        get_response = await client.get(
            f"/api/v1/workflows/{workflow_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_workflow_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ) -> None:
        """Test deleting a non-existent workflow."""
        fake_id = uuid4()
        response = await client.delete(
            f"/api/v1/workflows/{fake_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient) -> None:
        """Test health check endpoint."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient) -> None:
        """Test root endpoint."""
        response = await client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data


@pytest.mark.e2e
class TestWorkflowAPIErrorHandling:
    """Tests for API error handling."""

    @pytest.mark.asyncio
    async def test_validation_error_response_format(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ) -> None:
        """Test validation error response format."""
        response = await client.post(
            "/api/v1/workflows",
            json={"name": ""},  # Empty name
            headers=auth_headers,
        )

        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert "details" in data

    @pytest.mark.asyncio
    async def test_duplicate_workflow_name(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        setup_account_and_user,
    ) -> None:
        """Test creating workflow with duplicate name."""
        # Create first workflow
        await client.post(
            "/api/v1/workflows",
            json={"name": "Duplicate Test"},
            headers=auth_headers,
        )

        # Try to create another with same name
        response = await client.post(
            "/api/v1/workflows",
            json={"name": "Duplicate Test"},
            headers=auth_headers,
        )

        assert response.status_code == 409
        data = response.json()
        assert "duplicate" in data.get("detail", {}).get("error", "").lower()

    @pytest.fixture
    async def setup_account_and_user(self, db_session):
        """Create account and user for testing."""
        account = AccountModel(
            id=uuid4(),
            name="Error Test Account",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db_session.add(account)

        user = UserModel(
            id=uuid4(),
            email="error@example.com",
            account_id=account.id,
            created_at=datetime.now(UTC),
        )
        db_session.add(user)

        await db_session.flush()
        return account, user
