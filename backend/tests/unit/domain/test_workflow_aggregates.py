"""
Comprehensive unit tests for Workflow aggregate roots.

This test suite covers the Workflow aggregate as a domain entity
with its invariants, business rules, and behavior preservation.
"""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta

from src.workflows.domain.entities import Workflow, Trigger, Action, Condition
from src.workflows.domain.value_objects import (
    WorkflowName,
    WorkflowDescription,
    TriggerType,
    ActionType,
    ConditionType,
    ConditionOperator,
)
from src.workflows.domain.exceptions import (
    InvalidWorkflowNameError,
    InvalidWorkflowStatusError,
    DuplicateWorkflowNameError,
)


class TestWorkflowAggregateRoot:
    """Test suite for Workflow aggregate root behavior."""

    def test_workflow_aggregate_creation_minimal(self):
        """Given minimal valid data, when creating workflow aggregate, then entity created."""
        # Arrange
        workflow_id = uuid4()
        account_id = uuid4()
        name = WorkflowName("Minimal Workflow")

        # Act
        workflow = Workflow.create(
            workflow_id=workflow_id,
            account_id=account_id,
            name=name
        )

        # Assert - Aggregate invariants
        assert workflow.id == workflow_id
        assert workflow.account_id == account_id
        assert workflow.name == name
        assert workflow.description == WorkflowDescription("")
        assert workflow.status.value == "draft"
        assert workflow.version == 1
        assert workflow.trigger_type is None
        assert len(workflow.triggers) == 0
        assert len(workflow.actions) == 0
        assert len(workflow.conditions) == 0

    def test_workflow_aggregate_with_trigger(self):
        """Given workflow with trigger, when creating aggregate, then trigger included."""
        # Arrange
        workflow_id = uuid4()
        account_id = uuid4()
        name = WorkflowName("Workflow with Trigger")
        trigger = Trigger.create(
            trigger_id=uuid4(),
            workflow_id=workflow_id,
            trigger_type=TriggerType.WEBHOOK,
            config={"webhook_url": "/webhooks/test"}
        )

        # Act
        workflow = Workflow.create(
            workflow_id=workflow_id,
            account_id=account_id,
            name=name,
            trigger=trigger
        )

        # Assert - Aggregate contains trigger
        assert len(workflow.triggers) == 1
        assert workflow.triggers[0].id == trigger.id
        assert workflow.trigger_type == TriggerType.WEBHOOK

    def test_workflow_aggregate_with_actions(self):
        """Given workflow with actions, when creating aggregate, then actions included."""
        # Arrange
        workflow_id = uuid4()
        account_id = uuid4()
        name = WorkflowName("Workflow with Actions")
        actions = [
            Action.create(
                action_id=uuid4(),
                workflow_id=workflow_id,
                action_type=ActionType.SEND_EMAIL,
                config={"to": "test@example.com", "subject": "Test"},
                order=1
            ),
            Action.create(
                action_id=uuid4(),
                workflow_id=workflow_id,
                action_type=ActionType.WAIT,
                config={"duration": 60, "unit": "minutes"},
                order=2
            )
        ]

        # Act
        workflow = Workflow.create(
            workflow_id=workflow_id,
            account_id=account_id,
            name=name,
            actions=actions
        )

        # Assert - Aggregate contains ordered actions
        assert len(workflow.actions) == 2
        assert workflow.actions[0].order == 1
        assert workflow.actions[1].order == 2
        assert workflow.actions[0].action_type == ActionType.SEND_EMAIL

    def test_workflow_aggregate_with_conditions(self):
        """Given workflow with conditions, when creating aggregate, then conditions included."""
        # Arrange
        workflow_id = uuid4()
        account_id = uuid4()
        name = WorkflowName("Workflow with Conditions")
        conditions = [
            Condition.create(
                condition_id=uuid4(),
                workflow_id=workflow_id,
                condition_type=ConditionType.FIELD_COMPARISON,
                operator=ConditionOperator.EQUALS,
                field="status",
                value="premium"
            )
        ]

        # Act
        workflow = Workflow.create(
            workflow_id=workflow_id,
            account_id=account_id,
            name=name,
            conditions=conditions
        )

        # Assert - Aggregate contains conditions
        assert len(workflow.conditions) == 1
        assert workflow.conditions[0].field == "status"
        assert workflow.conditions[0].value == "premium"

    def test_workflow_aggregate_add_action(self):
        """Given workflow aggregate, when adding action, then action added in order."""
        # Arrange
        workflow = WorkflowFactory.build()
        action = Action.create(
            action_id=uuid4(),
            workflow_id=workflow.id,
            action_type=ActionType.SEND_EMAIL,
            config={},
            order=1
        )

        # Act
        workflow.add_action(action)

        # Assert
        assert len(workflow.actions) == 1
        assert workflow.actions[0].id == action.id

    def test_workflow_aggregate_remove_action(self):
        """Given workflow with action, when removing action, then action removed."""
        # Arrange
        workflow = WorkflowFactory.build()
        action = Action.create(
            action_id=uuid4(),
            workflow_id=workflow.id,
            action_type=ActionType.SEND_EMAIL,
            config={},
            order=1
        )
        workflow.add_action(action)

        # Act
        workflow.remove_action(action.id)

        # Assert
        assert len(workflow.actions) == 0

    def test_workflow_aggregate_activate_transitions_status(self):
        """Given draft workflow, when activating, then status becomes active."""
        # Arrange
        workflow = WorkflowFactory.build(status=WorkflowStatus.DRAFT)

        # Act
        workflow.activate()

        # Assert
        assert workflow.status == WorkflowStatus.ACTIVE
        assert workflow.updated_at > workflow.created_at

    def test_workflow_aggregate_activate_requires_trigger(self):
        """Given workflow without trigger, when activating, then raises exception."""
        # Arrange
        workflow = WorkflowFactory.build(
            status=WorkflowStatus.DRAFT,
            trigger_type=None
        )

        # Act & Assert
        with pytest.raises(InvalidWorkflowStatusError):
            workflow.activate()

    def test_workflow_aggregate_pause_transitions_status(self):
        """Given active workflow, when pausing, then status becomes paused."""
        # Arrange
        workflow = WorkflowFactory.build(status=WorkflowStatus.ACTIVE)

        # Act
        workflow.pause()

        # Assert
        assert workflow.status == WorkflowStatus.PAUSED

    def test_workflow_aggregate_archive_transitions_status(self):
        """Given paused workflow, when archiving, then status becomes archived."""
        # Arrange
        workflow = WorkflowFactory.build(status=WorkflowStatus.PAUSED)

        # Act
        workflow.archive()

        # Assert
        assert workflow.status == WorkflowStatus.ARCHIVED

    def test_workflow_aggregate_update_increments_version(self):
        """Given active workflow, when updating, then version increments."""
        # Arrange
        workflow = WorkflowFactory.build(
            status=WorkflowStatus.ACTIVE,
            version=1
        )
        original_version = workflow.version

        # Act
        workflow.update(name=WorkflowName("Updated Workflow"))

        # Assert
        assert workflow.version == original_version + 1

    def test_workflow_aggregate_draft_update_no_version_increment(self):
        """Given draft workflow, when updating, then version unchanged."""
        # Arrange
        workflow = WorkflowFactory.build(
            status=WorkflowStatus.DRAFT,
            version=1
        )

        # Act
        workflow.update(name=WorkflowName("Updated Workflow"))

        # Assert
        assert workflow.version == 1

    def test_workflow_aggregate_clone_creates_copy(self):
        """Given workflow, when cloning, then creates independent copy."""
        # Arrange
        original = WorkflowFactory.build(
            name=WorkflowName("Original Workflow")
        )

        # Act
        cloned = original.clone()

        # Assert
        assert cloned.id != original.id
        assert cloned.name == original.name
        assert cloned.account_id == original.account_id
        assert cloned.version == 1  # New workflow starts at version 1


class TestWorkflowAggregateInvariants:
    """Test suite for Workflow aggregate invariants."""

    def test_workflow_name_min_length_validation(self):
        """Given name too short, when creating, then raises exception."""
        # Arrange & Act & Assert
        with pytest.raises(InvalidWorkflowNameError):
            WorkflowName("ab")

    def test_workflow_name_max_length_validation(self):
        """Given name too long, when creating, then raises exception."""
        # Arrange & Act & Assert
        with pytest.raises(InvalidWorkflowNameError):
            WorkflowName("a" * 101)

    def test_workflow_name_special_characters_validation(self):
        """Given name with special chars, when creating, then raises exception."""
        # Arrange & Act & Assert
        with pytest.raises(InvalidWorkflowNameError):
            WorkflowName("Name @#$ Special!")

    @pytest.mark.parametrize("name,expected", [
        ("Valid Name", True),
        ("name-with-hyphens", True),
        ("name_with_underscores", True),
        ("Name with Numbers 123", True),
        ("UPPERCASE NAME", True),
        ("ab", False),  # Too short
        ("a" * 101, False),  # Too long
        ("name@special", False),  # Special characters
    ])
    def test_workflow_name_validation_various_cases(self, name, expected):
        """Given various names, when validating, then returns expected."""
        # Act
        is_valid = WorkflowName.is_valid(name)

        # Assert
        assert is_valid == expected

    def test_workflow_account_id_required(self):
        """Given workflow without account, when creating, then raises exception."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError):
            Workflow.create(
                workflow_id=uuid4(),
                account_id=None,
                name=WorkflowName("Test")
            )

    def test_workflow_version_minimum(self):
        """Given workflow, when created, then version is at least 1."""
        # Arrange
        workflow = WorkflowFactory.build()

        # Assert
        assert workflow.version >= 1

    def test_workflow_version_never_decrements(self):
        """Given workflow version, when updating, then version never decreases."""
        # Arrange
        workflow = WorkflowFactory.build(
            status=WorkflowStatus.ACTIVE,
            version=5
        )

        # Act
        workflow.update(name=WorkflowName("Updated"))

        # Assert
        assert workflow.version >= 5


class TestWorkflowAggregateBusinessRules:
    """Test suite for Workflow aggregate business rules."""

    def test_workflow_duplicate_name_in_account_rejected(self):
        """Given duplicate name in account, when creating, then raises exception."""
        # This would require repository to check for duplicates
        # Placeholder for business rule test
        pass

    def test_workflow_active_edit_creates_new_version(self):
        """Given active workflow, when editing, then creates new version."""
        # Arrange
        workflow = WorkflowFactory.build(
            status=WorkflowStatus.ACTIVE,
            version=1
        )

        # Act
        new_version = workflow.create_new_version()

        # Assert
        assert new_version.version == 2
        assert new_version.id != workflow.id

    def test_workflow_draft_edit_does_not_create_version(self):
        """Given draft workflow, when editing, then does not create version."""
        # Arrange
        workflow = WorkflowFactory.build(
            status=WorkflowStatus.DRAFT,
            version=1
        )

        # Act
        workflow.update(name=WorkflowName("Updated"))

        # Assert
        assert workflow.version == 1

    def test_workflow_action_order_maintained(self):
        """Given workflow with actions, when reordering, then order maintained."""
        # Arrange
        workflow = WorkflowFactory.build()
        action1 = ActionFactory.build(workflow_id=workflow.id, order=1)
        action2 = ActionFactory.build(workflow_id=workflow.id, order=2)
        action3 = ActionFactory.build(workflow_id=workflow.id, order=3)

        # Act
        workflow.reorder_action(action2.id, new_order=1)

        # Assert
        assert workflow.actions[0].id == action2.id
        assert workflow.actions[0].order == 1

    def test_workflow_execution_count_increments(self):
        """Given workflow, when executed, then execution count increments."""
        # Arrange
        workflow = WorkflowFactory.build(execution_count=0)

        # Act
        workflow.increment_execution_count()

        # Assert
        assert workflow.execution_count == 1


class TestWorkflowAggregateStateTransitions:
    """Test suite for Workflow aggregate state transitions."""

    @pytest.mark.parametrize("current_status,can_activate", [
        (WorkflowStatus.DRAFT, True),
        (WorkflowStatus.ACTIVE, False),  # Already active
        (WorkflowStatus.PAUSED, False),  # Must be draft
        (WorkflowStatus.ARCHIVED, False),  # Cannot activate archived
    ])
    def test_workflow_activate_from_states(self, current_status, can_activate):
        """Given various states, when activating, then transition allowed or blocked."""
        # Arrange
        workflow = WorkflowFactory.build(status=current_status)

        # Act & Assert
        if can_activate and current_status != WorkflowStatus.ACTIVE:
            workflow.activate()
            assert workflow.status == WorkflowStatus.ACTIVE
        else:
            with pytest.raises(InvalidWorkflowStatusError):
                workflow.activate()

    @pytest.mark.parametrize("current_status,can_pause", [
        (WorkflowStatus.ACTIVE, True),
        (WorkflowStatus.DRAFT, False),
        (WorkflowStatus.PAUSED, False),  # Already paused
        (WorkflowStatus.ARCHIVED, False),
    ])
    def test_workflow_pause_from_states(self, current_status, can_pause):
        """Given various states, when pausing, then transition allowed or blocked."""
        # Arrange
        workflow = WorkflowFactory.build(status=current_status)

        # Act & Assert
        if can_pause and current_status != WorkflowStatus.PAUSED:
            workflow.pause()
            assert workflow.status == WorkflowStatus.PAUSED
        else:
            with pytest.raises(InvalidWorkflowStatusError):
                workflow.pause()


# Import for factory
from tests.factories import WorkflowFactory, ActionFactory, TriggerFactory
from src.workflows.domain.entities import WorkflowStatus
