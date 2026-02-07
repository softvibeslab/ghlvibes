"""Acceptance tests for workflow templates.

These tests verify the EARS requirements from SPEC-WFL-008.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.acceptance
class TestWorkflowTemplatesAcceptance:
    """Acceptance tests for workflow template requirements."""

    @pytest.mark.asyncio
    async def test_req_001_template_library_access(self, client: AsyncClient):
        """REQ-001: Template library access from workflow creation interface.

        WHEN: User accesses workflow template library
        THEN: System displays available templates organized by category
        """
        # Act
        response = await client.get("/api/v1/workflow-templates")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert "total" in data
        assert isinstance(data["templates"], list)

    @pytest.mark.asyncio
    async def test_req_002_template_selection(self, client: AsyncClient, auth_headers):
        """REQ-002: Template selection displays detailed preview.

        WHEN: User selects a template from library
        THEN: System displays detailed preview with trigger, actions, metadata
        """
        # Arrange - Create a template first
        create_response = await client.post(
            "/api/v1/workflow-templates",
            json={
                "name": "Preview Test Template",
                "description": "Template for testing preview",
                "category": "lead_nurturing",
                "workflow_config": {
                    "trigger": {"type": "webhook", "url": "https://example.com"},
                    "actions": [
                        {"type": "send_email", "subject": "Test Subject"},
                        {"type": "wait", "duration": 3600},
                    ],
                },
                "tags": ["test", "preview"],
            },
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        template_id = create_response.json()["id"]

        # Act - Get template details
        response = await client.get(f"/api/v1/workflow-templates/{template_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Preview Test Template"
        assert "workflow_config" in data
        assert data["workflow_config"]["trigger"]["type"] == "webhook"
        assert len(data["workflow_config"]["actions"]) == 2
        assert "metadata" in data
        assert data["metadata"]["tags"] == ["test", "preview"]

    @pytest.mark.asyncio
    async def test_req_003_template_cloning(self, client: AsyncClient, auth_headers):
        """REQ-003: Template cloning creates new workflow instance.

        WHEN: User confirms template selection
        THEN: System creates new workflow with unique ID, draft status
        """
        # Arrange - Create template
        template_response = await client.post(
            "/api/v1/workflow-templates",
            json={
                "name": "Clone Test Template",
                "description": "Template for testing cloning",
                "category": "appointment_reminder",
                "workflow_config": {
                    "trigger": {"type": "webhook"},
                    "actions": [{"type": "send_sms", "message": "Reminder"}],
                },
            },
            headers=auth_headers,
        )
        template_id = template_response.json()["id"]

        # Act - Clone template to workflow
        clone_response = await client.post(
            f"/api/v1/workflow-templates/{template_id}/clone",
            json={
                "workflow_name": "Cloned Workflow",
                "workflow_description": "Workflow created from template",
            },
            headers=auth_headers,
        )

        # Assert
        assert clone_response.status_code == 201
        data = clone_response.json()
        assert "workflow_id" in data
        assert data["template_id"] == template_id
        assert "cloned_at" in data

    @pytest.mark.asyncio
    async def test_req_005_category_filtering(self, client: AsyncClient):
        """REQ-005: Template category filtering.

        WHEN: User selects category filter
        THEN: System displays only templates in that category
        """
        # Act - Filter by lead_nurturing category
        response = await client.get(
            "/api/v1/workflow-templates?category=lead_nurturing"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        # All returned templates should be in lead_nurturing category
        for template in data["templates"]:
            assert template["category"] == "lead_nurturing"

    @pytest.mark.asyncio
    async def test_req_006_search_functionality(self, client: AsyncClient):
        """REQ-006: Template search functionality.

        WHEN: User enters search query
        THEN: System returns matching templates
        """
        # Act - Search for templates
        response = await client.get("/api/v1/workflow-templates?search=nurturing")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        # Results should match search term
        for template in data["templates"]:
            # Search matches name, description, or tags
            text_match = (
                "nurturing" in template["name"].lower()
                or "nurturing" in template["description"].lower()
                or any("nurturing" in tag.lower() for tag in template["metadata"]["tags"])
            )
            assert text_match

    @pytest.mark.asyncio
    async def test_req_011_import_protections(self, client: AsyncClient, auth_headers):
        """REQ-011: Template import protection.

        System shall NOT allow template cloning when:
        - Required integrations not available
        - User lacks permission
        - Template is deprecated
        """
        # Test: Attempt to clone non-existent template
        response = await client.post(
            f"/api/v1/workflow-templates/{pytest.UUID('00000000-0000-0000-0000-000000000000')}/clone",
            json={"workflow_name": "Test"},
            headers=auth_headers,
        )

        # Assert - Should return 404
        assert response.status_code in [404, 400]


@pytest.mark.acceptance
class TestBulkEnrollmentAcceptance:
    """Acceptance tests for bulk enrollment requirements.

    These tests verify the EARS requirements from SPEC-WFL-011.
    """

    @pytest.mark.asyncio
    async def test_req_001_bulk_enrollment_initiation(
        self, client: AsyncClient, auth_headers
    ):
        """REQ-001: Bulk enrollment initiation creates job.

        WHEN: User initiates bulk enrollment
        THEN: System creates job with unique ID and initial status 'pending'
        """
        # Arrange
        workflow_id = pytest.UUID("12345678-1234-5678-1234-567812345678")

        # Act
        response = await client.post(
            f"/api/v1/bulk-enrollment/workflows/{workflow_id}/jobs",
            json={
                "selection": {
                    "type": "manual",
                    "contact_ids": [
                        str(pytest.UUID(f"{i:032x}")) for i in range(1, 11)
                    ],
                },
                "options": {
                    "batch_size": 100,
                    "skip_duplicates": True,
                },
            },
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending"
        assert data["total_contacts"] == 10

    @pytest.mark.asyncio
    async def test_req_004_contact_count_limits(self, client: AsyncClient, auth_headers):
        """REQ-004: Contact count limits enforced.

        System shall enforce:
        - Maximum 10,000 contacts per bulk operation
        - Batch size 100 contacts per batch
        """
        # Arrange
        workflow_id = pytest.UUID("12345678-1234-5678-1234-567812345678")
        too_many_contacts = [str(pytest.UUID(f"{i:032x}")) for i in range(1, 10001)]

        # Act & Assert - Should reject > 10,000 contacts
        response = await client.post(
            f"/api/v1/bulk-enrollment/workflows/{workflow_id}/jobs",
            json={
                "selection": {
                    "type": "manual",
                    "contact_ids": too_many_contacts,
                },
            },
            headers=auth_headers,
        )

        # Assert - Should fail validation
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_req_006_progress_tracking(self, client: AsyncClient, auth_headers):
        """REQ-006: Real-time progress tracking.

        WHILE: Job is processing
        THEN: System maintains real-time progress data
        """
        # Arrange - Create a job first
        workflow_id = pytest.UUID("12345678-1234-5678-1234-567812345678")
        create_response = await client.post(
            f"/api/v1/bulk-enrollment/workflows/{workflow_id}/jobs",
            json={
                "selection": {
                    "type": "manual",
                    "contact_ids": [str(pytest.UUID(f"{i:032x}")) for i in range(1, 101)],
                },
            },
            headers=auth_headers,
        )
        job_id = create_response.json()["id"]

        # Act - Get job progress
        response = await client.get(
            f"/api/v1/bulk-enrollment/jobs/{job_id}/progress",
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert "total_contacts" in data
        assert "processed" in data
        assert "success" in data
        assert "failed" in data
        assert "skipped" in data
        assert "progress_percentage" in data
        assert "rate" in data

    @pytest.mark.asyncio
    async def test_req_013_job_cancellation(self, client: AsyncClient, auth_headers):
        """REQ-013: Job cancellation.

        WHEN: User requests cancellation
        THEN: System marks job as 'cancelling' and stops processing
        """
        # Arrange - Create a job
        workflow_id = pytest.UUID("12345678-1234-5678-1234-567812345678")
        create_response = await client.post(
            f"/api/v1/bulk-enrollment/workflows/{workflow_id}/jobs",
            json={
                "selection": {
                    "type": "manual",
                    "contact_ids": [str(pytest.UUID(f"{i:032x}")) for i in range(1, 11)],
                },
            },
            headers=auth_headers,
        )
        job_id = create_response.json()["id"]

        # Act - Cancel the job
        response = await client.post(
            f"/api/v1/bulk-enrollment/jobs/{job_id}/cancel",
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"
        assert data["is_terminal"] is True


# Fixtures


@pytest.fixture
async def client(async_client):
    """Fixture for async HTTP client."""
    return async_client


@pytest.fixture
def auth_headers(test_user_token):
    """Fixture for authentication headers."""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture
def test_user_token():
    """Fixture for test user token."""
    # In real implementation, this would generate a valid JWT
    return "test_token_here"
