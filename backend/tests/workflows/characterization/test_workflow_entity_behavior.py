"""Characterization tests for Workflow entity behavior.

These tests document the CURRENT ACTUAL BEHAVIOR of the Workflow entity.
They serve as a safety net during refactoring - if behavior changes, these tests will fail.

IMPORTANT: These tests capture what the code DOES, not what it SHOULD DO.
If a test fails, either:
1. You broke existing behavior (bad)
2. Behavior changed intentionally (update test to document new behavior)

Generated during DDD PRESERVE phase for SPEC-WFL-001.
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.workflows.domain.entities import Workflow
from src.workflows.domain.exceptions import InvalidWorkflowStatusTransitionError
from src.workflows.domain.value_objects import WorkflowName, WorkflowStatus


class TestCharacterizeWorkflowEntityCreation:
    """Characterize Workflow entity creation behavior."""

    def test_characterize_minimal_workflow_creation(self) -> None:
        """Document: Creating workflow with minimal data initializes all required fields."""
        account_id = uuid4()
        user_id = uuid4()

        # Act: Create workflow with minimal data
        workflow = Workflow.create(
            account_id=account_id,
            name="Test Workflow",
            created_by=user_id,
        )

        # Assert: Document actual behavior
        assert workflow.id is not None, "ID is auto-generated as UUID"
        assert isinstance(workflow.id, uuid4().__class__), "ID is a UUID instance"
        assert workflow.account_id == account_id, "Account ID is preserved"
        assert str(workflow.name) == "Test Workflow", "Name is stored and accessible"
        assert workflow.name_value == "Test Workflow", "name_value property returns string"
        assert workflow.description is None, "Description defaults to None when not provided"
        assert workflow.trigger_type is None, "Trigger type defaults to None when not provided"
        assert workflow.trigger_config == {}, "Trigger config defaults to empty dict"
        assert workflow.status == WorkflowStatus.DRAFT, "Status defaults to DRAFT"
        assert workflow.version == 1, "Version starts at 1"
        assert workflow.created_by == user_id, "Creator is recorded"
        assert workflow.updated_by == user_id, "Updater is same as creator initially"
        assert isinstance(workflow.created_at, datetime), "Created at is datetime"
        assert isinstance(workflow.updated_at, datetime), "Updated at is datetime"
        assert workflow.created_at.tzinfo is not None, "Created at has timezone info (UTC)"
        assert workflow.updated_at.tzinfo is not None, "Updated at has timezone info (UTC)"

    def test_characterize_workflow_creation_with_all_fields(self) -> None:
        """Document: Creating workflow with all optional fields provided."""
        account_id = uuid4()
        user_id = uuid4()

        before = datetime.now(UTC)

        workflow = Workflow.create(
            account_id=account_id,
            name="Full Workflow",
            created_by=user_id,
            description="Complete workflow with all fields",
            trigger_type="contact_created",
            trigger_config={"filters": {"tags": ["lead"]}},
        )

        after = datetime.now(UTC)

        # Assert: All fields are set as provided
        assert str(workflow.name) == "Full Workflow"
        assert workflow.description == "Complete workflow with all fields"
        assert workflow.trigger_type == "contact_created"
        assert workflow.trigger_config == {"filters": {"tags": ["lead"]}}
        assert workflow.status == WorkflowStatus.DRAFT, "Still DRAFT even with all fields"
        assert before <= workflow.created_at <= after, "Timestamp is within creation window"
        assert before <= workflow.updated_at <= after, "Timestamp is within creation window"

    def test_characterize_workflow_creation_with_workflowname_object(self) -> None:
        """Document: Workflow can be created with WorkflowName object instead of string."""
        account_id = uuid4()
        user_id = uuid4()
        name_obj = WorkflowName("Object Name")

        workflow = Workflow.create(
            account_id=account_id,
            name=name_obj,
            created_by=user_id,
        )

        # Assert: WorkflowName object is used directly
        assert workflow.name is name_obj, "Same WorkflowName instance is used"
        assert str(workflow.name) == "Object Name"

    def test_characterize_workflow_name_validation_on_creation(self) -> None:
        """Document: Workflow name is validated through WorkflowName value object."""
        from src.workflows.domain.exceptions import InvalidWorkflowNameError

        account_id = uuid4()
        user_id = uuid4()

        # Assert: Invalid names raise InvalidWorkflowNameError
        with pytest.raises(InvalidWorkflowNameError):
            Workflow.create(
                account_id=account_id,
                name="ab",  # Too short
                created_by=user_id,
            )


class TestCharacterizeWorkflowStatusTransitions:
    """Characterize Workflow entity status transition behavior."""

    def test_characterize_activate_from_draft(self) -> None:
        """Document: Activating a draft workflow changes status to ACTIVE and increments version."""
        account_id = uuid4()
        user_id = uuid4()

        workflow = Workflow.create(
            account_id=account_id,
            name="Test",
            created_by=user_id,
        )
        initial_version = workflow.version
        initial_updated_at = workflow.updated_at

        workflow.activate(updated_by=user_id)

        # Assert: Status changed and version incremented
        assert workflow.status == WorkflowStatus.ACTIVE
        assert workflow.is_active is True
        assert workflow.is_draft is False
        assert workflow.version == initial_version + 1
        assert workflow.updated_by == user_id
        assert workflow.updated_at > initial_updated_at, "Updated at timestamp changed"

    def test_characterize_pause_from_active(self) -> None:
        """Document: Pausing an active workflow changes status to PAUSED."""
        account_id = uuid4()
        user_id = uuid4()

        workflow = Workflow.create(
            account_id=account_id,
            name="Test",
            created_by=user_id,
        )
        workflow.activate(updated_by=user_id)

        workflow.pause(updated_by=user_id)

        # Assert: Status changed to PAUSED
        assert workflow.status == WorkflowStatus.PAUSED
        assert workflow.is_paused is True
        assert workflow.is_active is False

    def test_characterize_deactivate_from_active(self) -> None:
        """Document: Deactivating an active workflow returns to DRAFT status."""
        account_id = uuid4()
        user_id = uuid4()

        workflow = Workflow.create(
            account_id=account_id,
            name="Test",
            created_by=user_id,
        )
        workflow.activate(updated_by=user_id)

        workflow.deactivate(updated_by=user_id)

        # Assert: Status returned to DRAFT
        assert workflow.status == WorkflowStatus.DRAFT
        assert workflow.is_draft is True

    def test_characterize_invalid_status_transition_raises_error(self) -> None:
        """Document: Invalid status transitions raise InvalidWorkflowStatusTransitionError."""
        account_id = uuid4()
        user_id = uuid4()

        workflow = Workflow.create(
            account_id=account_id,
            name="Test",
            created_by=user_id,
        )

        # Assert: Cannot pause from draft
        with pytest.raises(InvalidWorkflowStatusTransitionError) as exc_info:
            workflow.pause(updated_by=user_id)

        assert "draft" in str(exc_info.value).lower()
        assert "paused" in str(exc_info.value).lower()


class TestCharacterizeWorkflowUpdateBehavior:
    """Characterize Workflow entity update behavior."""

    def test_characterize_update_name_only(self) -> None:
        """Document: Updating only name changes name and increments version."""
        account_id = uuid4()
        user_id = uuid4()

        workflow = Workflow.create(
            account_id=account_id,
            name="Original",
            created_by=user_id,
        )
        initial_version = workflow.version

        workflow.update(updated_by=user_id, name="Updated")

        # Assert: Only name changed, version incremented
        assert str(workflow.name) == "Updated"
        assert workflow.version == initial_version + 1
        assert workflow.description is None, "Description still None"

    def test_characterize_update_multiple_fields(self) -> None:
        """Document: Updating multiple fields changes all specified fields."""
        account_id = uuid4()
        user_id = uuid4()

        workflow = Workflow.create(
            account_id=account_id,
            name="Original",
            created_by=user_id,
        )

        workflow.update(
            updated_by=user_id,
            name="Updated",
            description="New description",
            trigger_type="form_submitted",
            trigger_config={"form_id": "123"},
        )

        # Assert: All specified fields updated
        assert str(workflow.name) == "Updated"
        assert workflow.description == "New description"
        assert workflow.trigger_type == "form_submitted"
        assert workflow.trigger_config == {"form_id": "123"}

    def test_characterize_update_with_no_changes(self) -> None:
        """Document: Calling update with no parameters is a no-op but updates metadata."""
        account_id = uuid4()
        user_id = uuid4()

        workflow = Workflow.create(
            account_id=account_id,
            name="Test",
            created_by=user_id,
        )
        initial_version = workflow.version
        initial_updated_at = workflow.updated_at

        workflow.update(updated_by=user_id)

        # Assert: Version incremented and timestamp updated even with no changes
        assert workflow.version == initial_version + 1
        assert workflow.updated_at > initial_updated_at
        assert str(workflow.name) == "Test", "Name unchanged"


class TestCharacterizeWorkflowSerialization:
    """Characterize Workflow entity serialization behavior."""

    def test_characterize_to_dict_output_structure(self) -> None:
        """Document: to_dict() returns specific structure with all fields."""
        account_id = uuid4()
        user_id = uuid4()

        workflow = Workflow.create(
            account_id=account_id,
            name="Serialization Test",
            created_by=user_id,
            description="Test description",
            trigger_type="test_trigger",
        )

        result = workflow.to_dict()

        # Assert: Dict contains all expected keys with correct types
        assert isinstance(result, dict)
        assert "id" in result
        assert "account_id" in result
        assert "name" in result
        assert "description" in result
        assert "trigger_type" in result
        assert "trigger_config" in result
        assert "status" in result
        assert "version" in result
        assert "created_at" in result
        assert "updated_at" in result
        assert "created_by" in result
        assert "updated_by" in result

        # Assert: Values are correctly serialized
        assert result["name"] == "Serialization Test"
        assert result["description"] == "Test description"
        assert result["trigger_type"] == "test_trigger"
        assert result["status"] == "draft"
        assert result["version"] == 1
        assert result["account_id"] == str(account_id)
        assert isinstance(result["id"], str)
        assert isinstance(result["created_at"], str)
        assert isinstance(result["updated_at"], str)


class TestCharacterizeWorkflowPropertyAccessors:
    """Characterize Workflow entity property accessor behavior."""

    def test_characterize_is_active_property(self) -> None:
        """Document: is_active property returns True only when status is ACTIVE."""
        account_id = uuid4()
        user_id = uuid4()

        workflow = Workflow.create(
            account_id=account_id,
            name="Test",
            created_by=user_id,
        )

        assert workflow.is_active is False, "Draft workflow is not active"

        workflow.activate(updated_by=user_id)
        assert workflow.is_active is True, "Active workflow is active"

        workflow.pause(updated_by=user_id)
        assert workflow.is_active is False, "Paused workflow is not active"

    def test_characterize_is_draft_property(self) -> None:
        """Document: is_draft property returns True only when status is DRAFT."""
        account_id = uuid4()
        user_id = uuid4()

        workflow = Workflow.create(
            account_id=account_id,
            name="Test",
            created_by=user_id,
        )

        assert workflow.is_draft is True, "Initial status is draft"

        workflow.activate(updated_by=user_id)
        assert workflow.is_draft is False, "Active workflow is not draft"

    def test_characterize_is_paused_property(self) -> None:
        """Document: is_paused property returns True only when status is PAUSED."""
        account_id = uuid4()
        user_id = uuid4()

        workflow = Workflow.create(
            account_id=account_id,
            name="Test",
            created_by=user_id,
        )

        assert workflow.is_paused is False, "Draft workflow is not paused"

        workflow.activate(updated_by=user_id)
        workflow.pause(updated_by=user_id)
        assert workflow.is_paused is True, "Paused workflow is paused"

        workflow.activate(updated_by=user_id)  # Resume
        assert workflow.is_paused is False, "Resumed workflow is not paused"
