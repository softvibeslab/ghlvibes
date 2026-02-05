"""Unit tests for workflow domain entities.

These tests verify the Workflow aggregate root behaves correctly
and enforces domain invariants.
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.workflows.domain.entities import Workflow
from src.workflows.domain.exceptions import InvalidWorkflowStatusTransitionError
from src.workflows.domain.value_objects import WorkflowName, WorkflowStatus


class TestWorkflowEntity:
    """Test suite for Workflow entity."""

    @pytest.fixture
    def account_id(self) -> str:
        """Fixture for test account ID."""
        return uuid4()

    @pytest.fixture
    def user_id(self) -> str:
        """Fixture for test user ID."""
        return uuid4()

    def test_create_workflow_with_minimal_data(self, account_id, user_id) -> None:
        """Test creating workflow with minimal required data."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Test Workflow",
            created_by=user_id,
        )

        assert workflow.name_value == "Test Workflow"
        assert workflow.account_id == account_id
        assert workflow.created_by == user_id
        assert workflow.status == WorkflowStatus.DRAFT
        assert workflow.version == 1
        assert workflow.description is None
        assert workflow.trigger_type is None
        assert workflow.trigger_config == {}

    def test_create_workflow_with_all_data(self, account_id, user_id) -> None:
        """Test creating workflow with all optional data."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Full Workflow",
            created_by=user_id,
            description="A complete workflow",
            trigger_type="contact_created",
            trigger_config={"filters": {"tags": ["lead"]}},
        )

        assert workflow.name_value == "Full Workflow"
        assert workflow.description == "A complete workflow"
        assert workflow.trigger_type == "contact_created"
        assert workflow.trigger_config == {"filters": {"tags": ["lead"]}}

    def test_create_workflow_with_workflow_name_object(self, account_id, user_id) -> None:
        """Test creating workflow with WorkflowName object."""
        name = WorkflowName("Named Workflow")
        workflow = Workflow.create(
            account_id=account_id,
            name=name,
            created_by=user_id,
        )

        assert workflow.name == name
        assert workflow.name_value == "Named Workflow"

    def test_workflow_timestamps(self, account_id, user_id) -> None:
        """Test that timestamps are set correctly."""
        before = datetime.now(UTC)
        workflow = Workflow.create(
            account_id=account_id,
            name="Timestamp Test",
            created_by=user_id,
        )
        after = datetime.now(UTC)

        assert before <= workflow.created_at <= after
        assert before <= workflow.updated_at <= after

    def test_workflow_uuid_generation(self, account_id, user_id) -> None:
        """Test that UUID is generated on creation."""
        workflow = Workflow.create(
            account_id=account_id,
            name="UUID Test",
            created_by=user_id,
        )

        assert workflow.id is not None
        # Verify it's a valid UUID by trying to convert to string
        assert len(str(workflow.id)) == 36

    def test_activate_workflow_from_draft(self, account_id, user_id) -> None:
        """Test activating a draft workflow."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Activate Test",
            created_by=user_id,
        )
        initial_version = workflow.version

        workflow.activate(updated_by=user_id)

        assert workflow.status == WorkflowStatus.ACTIVE
        assert workflow.is_active is True
        assert workflow.version == initial_version + 1
        assert workflow.updated_by == user_id

    def test_pause_workflow_from_active(self, account_id, user_id) -> None:
        """Test pausing an active workflow."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Pause Test",
            created_by=user_id,
        )
        workflow.activate(updated_by=user_id)
        initial_version = workflow.version

        workflow.pause(updated_by=user_id)

        assert workflow.status == WorkflowStatus.PAUSED
        assert workflow.is_paused is True
        assert workflow.version == initial_version + 1

    def test_deactivate_workflow_from_active(self, account_id, user_id) -> None:
        """Test deactivating an active workflow."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Deactivate Test",
            created_by=user_id,
        )
        workflow.activate(updated_by=user_id)

        workflow.deactivate(updated_by=user_id)

        assert workflow.status == WorkflowStatus.DRAFT
        assert workflow.is_draft is True

    def test_deactivate_workflow_from_paused(self, account_id, user_id) -> None:
        """Test deactivating a paused workflow."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Deactivate Paused Test",
            created_by=user_id,
        )
        workflow.activate(updated_by=user_id)
        workflow.pause(updated_by=user_id)

        workflow.deactivate(updated_by=user_id)

        assert workflow.status == WorkflowStatus.DRAFT

    def test_resume_workflow_from_paused(self, account_id, user_id) -> None:
        """Test resuming a paused workflow."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Resume Test",
            created_by=user_id,
        )
        workflow.activate(updated_by=user_id)
        workflow.pause(updated_by=user_id)

        workflow.activate(updated_by=user_id)

        assert workflow.status == WorkflowStatus.ACTIVE

    def test_invalid_pause_from_draft(self, account_id, user_id) -> None:
        """Test that pausing a draft workflow raises error."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Invalid Pause Test",
            created_by=user_id,
        )

        with pytest.raises(InvalidWorkflowStatusTransitionError) as exc_info:
            workflow.pause(updated_by=user_id)

        assert "draft" in str(exc_info.value)
        assert "paused" in str(exc_info.value)

    def test_update_workflow_name(self, account_id, user_id) -> None:
        """Test updating workflow name."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Original Name",
            created_by=user_id,
        )
        initial_version = workflow.version

        workflow.update(updated_by=user_id, name="Updated Name")

        assert workflow.name_value == "Updated Name"
        assert workflow.version == initial_version + 1

    def test_update_workflow_description(self, account_id, user_id) -> None:
        """Test updating workflow description."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Description Test",
            created_by=user_id,
        )

        workflow.update(updated_by=user_id, description="New description")

        assert workflow.description == "New description"

    def test_update_workflow_trigger(self, account_id, user_id) -> None:
        """Test updating workflow trigger."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Trigger Test",
            created_by=user_id,
        )

        workflow.update(
            updated_by=user_id,
            trigger_type="form_submitted",
            trigger_config={"form_id": "123"},
        )

        assert workflow.trigger_type == "form_submitted"
        assert workflow.trigger_config == {"form_id": "123"}

    def test_update_with_workflow_name_object(self, account_id, user_id) -> None:
        """Test updating with WorkflowName object."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Original Name",
            created_by=user_id,
        )
        new_name = WorkflowName("New Name Object")

        workflow.update(updated_by=user_id, name=new_name)

        assert workflow.name == new_name

    def test_to_dict(self, account_id, user_id) -> None:
        """Test converting workflow to dictionary."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Dict Test",
            created_by=user_id,
            description="Test description",
            trigger_type="contact_created",
            trigger_config={"key": "value"},
        )

        result = workflow.to_dict()

        assert result["name"] == "Dict Test"
        assert result["description"] == "Test description"
        assert result["trigger_type"] == "contact_created"
        assert result["trigger_config"] == {"key": "value"}
        assert result["status"] == "draft"
        assert result["version"] == 1
        assert result["account_id"] == str(account_id)
        assert "created_at" in result
        assert "updated_at" in result

    def test_is_active_property(self, account_id, user_id) -> None:
        """Test is_active property."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Active Property Test",
            created_by=user_id,
        )

        assert workflow.is_active is False
        workflow.activate(updated_by=user_id)
        assert workflow.is_active is True

    def test_is_draft_property(self, account_id, user_id) -> None:
        """Test is_draft property."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Draft Property Test",
            created_by=user_id,
        )

        assert workflow.is_draft is True
        workflow.activate(updated_by=user_id)
        assert workflow.is_draft is False

    def test_is_paused_property(self, account_id, user_id) -> None:
        """Test is_paused property."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Paused Property Test",
            created_by=user_id,
        )

        assert workflow.is_paused is False
        workflow.activate(updated_by=user_id)
        workflow.pause(updated_by=user_id)
        assert workflow.is_paused is True
