"""
Comprehensive integration tests for Workflow API endpoints.

These tests verify the full integration between HTTP layer, use cases,
repositories, and database.
"""

import pytest
from uuid import uuid4
from httpx import AsyncClient

from src.workflows.domain.entities import Workflow, WorkflowStatus
from src.workflows.domain.value_objects import TriggerType, ActionType


@pytest.mark.integration
class TestWorkflowAPIEndpoints:
    """Test suite for Workflow API endpoints integration."""

    async def test_create_workflow_end_to_end(self, async_client: AsyncClient):
        """Given valid request, when POST /workflows, then creates workflow."""
        # Arrange
        payload = {
            "name": "Integration Test Workflow",
            "description": "Testing API end to end",
            "trigger_type": "webhook",
            "trigger_config": {"webhook_url": "/webhooks/test"}
        }

        # Act
        response = await async_client.post("/api/v1/workflows", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["description"] == payload["description"]
        assert data["trigger_type"] == "webhook"
        assert "id" in data
        assert data["status"] == "draft"

    async def test_get_workflow_returns_workflow(self, async_client: AsyncClient):
        """Given existing workflow, when GET /workflows/:id, then returns workflow."""
        # Arrange
        create_response = await async_client.post("/api/v1/workflows", json={
            "name": "Test Workflow",
            "trigger_type": "webhook"
        })
        workflow_id = create_response.json()["id"]

        # Act
        response = await async_client.get(f"/api/v1/workflows/{workflow_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == workflow_id
        assert data["name"] == "Test Workflow"

    async def test_get_workflow_not_found(self, async_client: AsyncClient):
        """Given non-existent workflow, when GET /workflows/:id, then returns 404."""
        # Arrange
        workflow_id = uuid4()

        # Act
        response = await async_client.get(f"/api/v1/workflows/{workflow_id}")

        # Assert
        assert response.status_code == 404

    async def test_list_workflows_paginated(self, async_client: AsyncClient):
        """Given multiple workflows, when GET /workflows, then returns paginated list."""
        # Arrange
        for i in range(15):
            await async_client.post("/api/v1/workflows", json={
                "name": f"Workflow {i}",
                "trigger_type": "webhook"
            })

        # Act
        response = await async_client.get("/api/v1/workflows?page=1&page_size=10")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["workflows"]) == 10
        assert data["total_count"] == 15
        assert data["page"] == 1
        assert data["page_size"] == 10

    async def test_update_workflow_success(self, async_client: AsyncClient):
        """Given workflow, when PATCH /workflows/:id, then updates workflow."""
        # Arrange
        create_response = await async_client.post("/api/v1/workflows", json={
            "name": "Original Name",
            "trigger_type": "webhook"
        })
        workflow_id = create_response.json()["id"]

        # Act
        update_response = await async_client.patch(
            f"/api/v1/workflows/{workflow_id}",
            json={"name": "Updated Name"}
        )

        # Assert
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["name"] == "Updated Name"

    async def test_delete_workflow_success(self, async_client: AsyncClient):
        """Given draft workflow, when DELETE /workflows/:id, then deletes workflow."""
        # Arrange
        create_response = await async_client.post("/api/v1/workflows", json={
            "name": "Workflow to Delete"
        })
        workflow_id = create_response.json()["id"]

        # Act
        delete_response = await async_client.delete(f"/api/v1/workflows/{workflow_id}")

        # Assert
        assert delete_response.status_code == 204

        # Verify deletion
        get_response = await async_client.get(f"/api/v1/workflows/{workflow_id}")
        assert get_response.status_code == 404

    async def test_activate_workflow_success(self, async_client: AsyncClient):
        """Given workflow with trigger, when POST /activate, then activates workflow."""
        # Arrange
        create_response = await async_client.post("/api/v1/workflows", json={
            "name": "Workflow to Activate",
            "trigger_type": "webhook",
            "trigger_config": {"webhook_url": "/webhooks/test"}
        })
        workflow_id = create_response.json()["id"]

        # Act
        activate_response = await async_client.post(f"/api/v1/workflows/{workflow_id}/activate")

        # Assert
        assert activate_response.status_code == 200
        data = activate_response.json()
        assert data["status"] == "active"

    async def test_pause_workflow_success(self, async_client: AsyncClient):
        """Given active workflow, when POST /pause, then pauses workflow."""
        # Arrange
        create_response = await async_client.post("/api/v1/workflows", json={
            "name": "Workflow to Pause",
            "trigger_type": "webhook"
        })
        workflow_id = create_response.json()["id"]

        # Activate first
        await async_client.post(f"/api/v1/workflows/{workflow_id}/activate")

        # Act
        pause_response = await async_client.post(f"/api/v1/workflows/{workflow_id}/pause")

        # Assert
        assert pause_response.status_code == 200
        data = pause_response.json()
        assert data["status"] == "paused"

    async def test_create_workflow_validation_error(self, async_client: AsyncClient):
        """Given invalid request, when POST /workflows, then returns 422."""
        # Arrange
        payload = {
            "name": "ab",  # Too short
        }

        # Act
        response = await async_client.post("/api/v1/workflows", json=payload)

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_execute_workflow_endpoint(self, async_client: AsyncClient):
        """Given active workflow, when POST /execute, then executes workflow."""
        # Arrange
        create_response = await async_client.post("/api/v1/workflows", json={
            "name": "Workflow to Execute",
            "trigger_type": "manual"
        })
        workflow_id = create_response.json()["id"]

        await async_client.post(f"/api/v1/workflows/{workflow_id}/activate")

        # Act
        execute_response = await async_client.post(
            f"/api/v1/workflows/{workflow_id}/execute",
            json={"contact_id": str(uuid4())}
        )

        # Assert
        assert execute_response.status_code == 200
        data = execute_response.json()
        assert "execution_id" in data

    async def test_workflow_crud_lifecycle(self, async_client: AsyncClient):
        """Given workflow, when performing CRUD, then all operations succeed."""
        # Create
        create_response = await async_client.post("/api/v1/workflows", json={
            "name": "CRUD Test Workflow"
        })
        assert create_response.status_code == 201
        workflow_id = create_response.json()["id"]

        # Read
        read_response = await async_client.get(f"/api/v1/workflows/{workflow_id}")
        assert read_response.status_code == 200
        assert read_response.json()["name"] == "CRUD Test Workflow"

        # Update
        update_response = await async_client.patch(
            f"/api/v1/workflows/{workflow_id}",
            json={"name": "Updated CRUD Workflow"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "Updated CRUD Workflow"

        # Delete
        delete_response = await async_client.delete(f"/api/v1/workflows/{workflow_id}")
        assert delete_response.status_code == 204

        # Verify deleted
        verify_response = await async_client.get(f"/api/v1/workflows/{workflow_id}")
        assert verify_response.status_code == 404


@pytest.mark.integration
class TestWorkflowTriggerAPI:
    """Test suite for workflow trigger endpoints."""

    async def test_add_trigger_to_workflow(self, async_client: AsyncClient):
        """Given workflow, when POST /triggers, then adds trigger."""
        # Arrange
        workflow_response = await async_client.post("/api/v1/workflows", json={
            "name": "Workflow with Trigger"
        })
        workflow_id = workflow_response.json()["id"]

        # Act
        trigger_response = await async_client.post(
            f"/api/v1/workflows/{workflow_id}/triggers",
            json={
                "trigger_type": "webhook",
                "config": {"webhook_url": "/webhooks/test"}
            }
        )

        # Assert
        assert trigger_response.status_code == 201
        data = trigger_response.json()
        assert data["trigger_type"] == "webhook"

    async def test_update_trigger(self, async_client: AsyncClient):
        """Given workflow with trigger, when PATCH /triggers/:id, then updates trigger."""
        # Arrange
        workflow_response = await async_client.post("/api/v1/workflows", json={
            "name": "Workflow",
            "trigger_type": "webhook",
            "trigger_config": {"webhook_url": "/webhooks/old"}
        })
        workflow_id = workflow_response.json()["id"]

        # Act
        update_response = await async_client.patch(
            f"/api/v1/workflows/{workflow_id}/trigger",
            json={"config": {"webhook_url": "/webhooks/new"}}
        )

        # Assert
        assert update_response.status_code == 200


@pytest.mark.integration
class TestWorkflowActionAPI:
    """Test suite for workflow action endpoints."""

    async def test_add_action_to_workflow(self, async_client: AsyncClient):
        """Given workflow, when POST /actions, then adds action."""
        # Arrange
        workflow_response = await async_client.post("/api/v1/workflows", json={
            "name": "Workflow with Action"
        })
        workflow_id = workflow_response.json()["id"]

        # Act
        action_response = await async_client.post(
            f"/api/v1/workflows/{workflow_id}/actions",
            json={
                "action_type": "send_email",
                "config": {
                    "to": "{{contact.email}}",
                    "subject": "Test Email",
                    "body": "Test body"
                },
                "order": 1
            }
        )

        # Assert
        assert action_response.status_code == 201
        data = action_response.json()
        assert data["action_type"] == "send_email"
        assert data["order"] == 1

    async def test_list_actions(self, async_client: AsyncClient):
        """Given workflow with actions, when GET /actions, then returns actions."""
        # Arrange
        workflow_response = await async_client.post("/api/v1/workflows", json={
            "name": "Workflow"
        })
        workflow_id = workflow_response.json()["id"]

        await async_client.post(
            f"/api/v1/workflows/{workflow_id}/actions",
            json={
                "action_type": "send_email",
                "config": {"to": "test@example.com"},
                "order": 1
            }
        )

        # Act
        list_response = await async_client.get(f"/api/v1/workflows/{workflow_id}/actions")

        # Assert
        assert list_response.status_code == 200
        data = list_response.json()
        assert len(data["actions"]) == 1

    async def test_update_action(self, async_client: AsyncClient):
        """Given workflow with action, when PATCH /actions/:id, then updates action."""
        # Arrange
        workflow_response = await async_client.post("/api/v1/workflows", json={
            "name": "Workflow"
        })
        workflow_id = workflow_response.json()["id"]

        action_response = await async_client.post(
            f"/api/v1/workflows/{workflow_id}/actions",
            json={
                "action_type": "send_email",
                "config": {"subject": "Old Subject"},
                "order": 1
            }
        )
        action_id = action_response.json()["id"]

        # Act
        update_response = await async_client.patch(
            f"/api/v1/workflows/{workflow_id}/actions/{action_id}",
            json={"config": {"subject": "New Subject"}}
        )

        # Assert
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["config"]["subject"] == "New Subject"

    async def test_delete_action(self, async_client: AsyncClient):
        """Given workflow with action, when DELETE /actions/:id, then deletes action."""
        # Arrange
        workflow_response = await async_client.post("/api/v1/workflows", json={
            "name": "Workflow"
        })
        workflow_id = workflow_response.json()["id"]

        action_response = await async_client.post(
            f"/api/v1/workflows/{workflow_id}/actions",
            json={
                "action_type": "send_email",
                "config": {},
                "order": 1
            }
        )
        action_id = action_response.json()["id"]

        # Act
        delete_response = await async_client.delete(
            f"/api/v1/workflows/{workflow_id}/actions/{action_id}"
        )

        # Assert
        assert delete_response.status_code == 204


@pytest.mark.integration
@pytest.mark.performance
class TestWorkflowAPIPerformance:
    """Performance tests for workflow API endpoints."""

    async def test_create_workflow_performance(self, async_client: AsyncClient):
        """Given standard payload, when POST /workflows, then responds in < 300ms."""
        import time

        # Arrange
        payload = {
            "name": "Performance Test Workflow",
            "trigger_type": "webhook"
        }

        # Act
        start_time = time.time()
        response = await async_client.post("/api/v1/workflows", json=payload)
        end_time = time.time()

        # Assert
        assert response.status_code == 201
        duration_ms = (end_time - start_time) * 1000
        assert duration_ms < 300, f"Response took {duration_ms}ms"

    async def test_list_workflows_performance(self, async_client: AsyncClient):
        """Given many workflows, when GET /workflows, then responds in < 200ms."""
        import time

        # Arrange - Create 50 workflows
        for i in range(50):
            await async_client.post("/api/v1/workflows", json={
                "name": f"Workflow {i}"
            })

        # Act
        start_time = time.time()
        response = await async_client.get("/api/v1/workflows?page_size=50")
        end_time = time.time()

        # Assert
        assert response.status_code == 200
        duration_ms = (end_time - start_time) * 1000
        assert duration_ms < 200, f"Response took {duration_ms}ms"
