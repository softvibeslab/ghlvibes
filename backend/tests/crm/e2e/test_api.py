"""E2E tests for CRM API endpoints.

Tests full HTTP request/response cycles.
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
class TestContactAPIE2E:
    """E2E tests for contact API endpoints."""

    async def test_create_contact_endpoint(self, async_client: AsyncClient):
        """Test POST /api/v1/crm/contacts creates contact."""
        response = await async_client.post(
            "/api/v1/crm/contacts",
            json={
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "john@example.com"
        assert data["first_name"] == "John"
        assert "id" in data

    async def test_get_contact_endpoint(self, async_client: AsyncClient):
        """Test GET /api/v1/crm/contacts/{id} retrieves contact."""
        # First create a contact
        create_response = await async_client.post(
            "/api/v1/crm/contacts",
            json={
                "email": "jane@example.com",
                "first_name": "Jane",
                "last_name": "Doe",
            },
        )
        contact_id = create_response.json()["id"]

        # Then retrieve it
        response = await async_client.get(f"/api/v1/crm/contacts/{contact_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "jane@example.com"

    async def test_list_contacts_endpoint(self, async_client: AsyncClient):
        """Test GET /api/v1/crm/contacts lists contacts."""
        response = await async_client.get("/api/v1/crm/contacts?page=1&page_size=20")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data

    async def test_update_contact_endpoint(self, async_client: AsyncClient):
        """Test PATCH /api/v1/crm/contacts/{id} updates contact."""
        # Create contact
        create_response = await async_client.post(
            "/api/v1/crm/contacts",
            json={
                "email": "bob@example.com",
                "first_name": "Bob",
                "last_name": "Smith",
            },
        )
        contact_id = create_response.json()["id"]

        # Update contact
        response = await async_client.patch(
            f"/api/v1/crm/contacts/{contact_id}",
            json={
                "first_name": "Robert",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Robert"

    async def test_delete_contact_endpoint(self, async_client: AsyncClient):
        """Test DELETE /api/v1/crm/contacts/{id} deletes contact."""
        # Create contact
        create_response = await async_client.post(
            "/api/v1/crm/contacts",
            json={
                "email": "delete@example.com",
                "first_name": "Delete",
                "last_name": "Me",
            },
        )
        contact_id = create_response.json()["id"]

        # Delete contact
        response = await async_client.delete(f"/api/v1/crm/contacts/{contact_id}")

        assert response.status_code == 204

    async def test_bulk_import_contacts_endpoint(self, async_client: AsyncClient):
        """Test POST /api/v1/crm/contacts/bulk-import imports contacts."""
        response = await async_client.post(
            "/api/v1/crm/contacts/bulk-import",
            json={
                "contacts": [
                    {
                        "email": "bulk1@example.com",
                        "first_name": "Bulk",
                        "last_name": "One",
                    },
                    {
                        "email": "bulk2@example.com",
                        "first_name": "Bulk",
                        "last_name": "Two",
                    },
                ]
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["imported"] == 2
        assert data["failed"] == 0


@pytest.mark.asyncio
class TestDealAPIE2E:
    """E2E tests for deal API endpoints."""

    async def test_create_deal_endpoint(self, async_client: AsyncClient):
        """Test POST /api/v1/crm/deals creates deal."""
        # First create a pipeline
        pipeline_response = await async_client.post(
            "/api/v1/crm/pipelines",
            json={
                "name": "Test Pipeline",
                "stages": [
                    {
                        "name": "Stage 1",
                        "order": 1,
                        "probability": 50,
                    }
                ],
            },
        )
        pipeline_id = pipeline_response.json()["id"]
        stage_id = pipeline_response.json()["stages"][0]["id"]

        # Create deal
        response = await async_client.post(
            "/api/v1/crm/deals",
            json={
                "pipeline_id": pipeline_id,
                "stage_id": stage_id,
                "name": "Test Deal",
                "value": 10000.00,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Deal"
        assert data["value_amount"] == 1000000  # Stored as cents

    async def test_move_deal_stage_endpoint(self, async_client: AsyncClient):
        """Test POST /api/v1/crm/deals/{id}/move moves deal."""
        # Setup: Create pipeline with 2 stages and a deal
        pipeline_response = await async_client.post(
            "/api/v1/crm/pipelines",
            json={
                "name": "Test Pipeline",
                "stages": [
                    {"name": "Stage 1", "order": 1, "probability": 10},
                    {"name": "Stage 2", "order": 2, "probability": 50},
                ],
            },
        )
        pipeline = pipeline_response.json()
        stage_1_id = pipeline["stages"][0]["id"]
        stage_2_id = pipeline["stages"][1]["id"]

        deal_response = await async_client.post(
            "/api/v1/crm/deals",
            json={
                "pipeline_id": pipeline["id"],
                "stage_id": stage_1_id,
                "name": "Test Deal",
                "value": 5000.00,
            },
        )
        deal_id = deal_response.json()["id"]

        # Move deal to stage 2
        response = await async_client.post(
            f"/api/v1/crm/deals/{deal_id}/move",
            params={"stage_id": stage_2_id, "probability": 60},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["stage_id"] == stage_2_id
        assert data["probability"] == 60

    async def test_win_deal_endpoint(self, async_client: AsyncClient):
        """Test POST /api/v1/crm/deals/{id}/win marks deal as won."""
        # Setup: Create pipeline and deal
        pipeline_response = await async_client.post(
            "/api/v1/crm/pipelines",
            json={
                "name": "Test Pipeline",
                "stages": [
                    {"name": "Stage 1", "order": 1, "probability": 50}
                ],
            },
        )
        pipeline = pipeline_response.json()
        stage_id = pipeline["stages"][0]["id"]

        deal_response = await async_client.post(
            "/api/v1/crm/deals",
            json={
                "pipeline_id": pipeline["id"],
                "stage_id": stage_id,
                "name": "Test Deal",
                "value": 25000.00,
            },
        )
        deal_id = deal_response.json()["id"]

        # Mark deal as won
        response = await async_client.post(f"/api/v1/crm/deals/{deal_id}/win")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "won"
        assert data["probability"] == 100
        assert data["actual_close_date"] is not None

    async def test_get_deal_forecast_endpoint(self, async_client: AsyncClient):
        """Test GET /api/v1/crm/deals/forecast returns forecast."""
        response = await async_client.get("/api/v1/crm/deals/forecast")

        assert response.status_code == 200
        data = response.json()
        assert "total_value" in data
        assert "weighted_value" in data
        assert "won_value" in data
        assert "open_deals" in data
