"""Characterization tests for existing trigger behavior in Workflow entity.

These tests capture the CURRENT behavior of trigger_type and trigger_config
fields to ensure backward compatibility during SPEC-WFL-002 implementation.

NOTE: These tests document WHAT IS, not what SHOULD BE.
They ensure existing behavior is preserved during refactoring.
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.workflows.domain.entities import Workflow
from src.workflows.domain.value_objects import WorkflowName, WorkflowStatus


class TestExistingTriggerTypeBehavior:
    """Characterization tests for trigger_type field behavior."""

    @pytest.fixture
    def account_id(self) -> UUID:
        """Fixture for test account ID."""
        return uuid4()

    @pytest.fixture
    def user_id(self) -> UUID:
        """Fixture for test user ID."""
        return uuid4()

    def test_characterize_trigger_type_defaults_to_none(self, account_id, user_id) -> None:
        """Characterize: trigger_type defaults to None when not provided."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Test Workflow",
            created_by=user_id,
        )

        # Document actual behavior
        assert workflow.trigger_type is None, "trigger_type defaults to None"

    def test_characterize_trigger_config_defaults_to_empty_dict(
        self, account_id, user_id
    ) -> None:
        """Characterize: trigger_config defaults to empty dict when not provided."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Test Workflow",
            created_by=user_id,
        )

        # Document actual behavior
        assert workflow.trigger_config == {}, "trigger_config defaults to {}"

    def test_characterize_trigger_type_accepts_string(self, account_id, user_id) -> None:
        """Characterize: trigger_type accepts any string value."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Test Workflow",
            created_by=user_id,
            trigger_type="contact_created",
        )

        # Document actual behavior
        assert workflow.trigger_type == "contact_created"
        assert isinstance(workflow.trigger_type, str)

    def test_characterize_trigger_type_accepts_any_string(self, account_id, user_id) -> None:
        """Characterize: trigger_type does NOT validate against valid trigger types."""
        # This demonstrates the lack of validation in existing code
        workflow = Workflow.create(
            account_id=account_id,
            name="Test Workflow",
            created_by=user_id,
            trigger_type="invalid_trigger_type_that_does_not_exist",
        )

        # Document actual behavior - no validation occurs
        assert workflow.trigger_type == "invalid_trigger_type_that_does_not_exist"

    def test_characterize_trigger_config_accepts_dict(self, account_id, user_id) -> None:
        """Characterize: trigger_config accepts dict with any structure."""
        config = {
            "filters": {"tags": ["lead", "prospect"]},
            "settings": {"enrollment_limit": "single"},
        }
        workflow = Workflow.create(
            account_id=account_id,
            name="Test Workflow",
            created_by=user_id,
            trigger_config=config,
        )

        # Document actual behavior
        assert workflow.trigger_config == config

    def test_characterize_trigger_config_no_validation(self, account_id, user_id) -> None:
        """Characterize: trigger_config does NOT validate structure."""
        # This demonstrates lack of validation
        invalid_configs = [
            None,  # None is allowed
            {"invalid": "structure"},  # Any structure is allowed
            {"nested": {"deep": {"structure": True}}},  # Deep nesting allowed
            [],  # Even lists (will be converted)
            "string_value",  # Even strings (will fail but type hint allows)
        ]

        for config in invalid_configs[:2]:  # Test first two that won't cause errors
            workflow = Workflow.create(
                account_id=account_id,
                name="Test Workflow",
                created_by=user_id,
                trigger_config=config if config is not None else {},
            )
            assert workflow.trigger_config == (config if config is not None else {})

    def test_characterize_update_trigger_type(self, account_id, user_id) -> None:
        """Characterize: trigger_type can be updated via update method."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Test Workflow",
            created_by=user_id,
            trigger_type="contact_created",
        )

        workflow.update(
            updated_by=user_id,
            trigger_type="form_submitted",
        )

        # Document actual behavior
        assert workflow.trigger_type == "form_submitted"
        assert workflow.version == 2  # Version increments

    def test_characterize_update_trigger_config(self, account_id, user_id) -> None:
        """Characterize: trigger_config can be updated via update method."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Test Workflow",
            created_by=user_id,
            trigger_config={"old": "config"},
        )

        new_config = {"new": "config", "filters": {"tag": "vip"}}
        workflow.update(
            updated_by=user_id,
            trigger_config=new_config,
        )

        # Document actual behavior
        assert workflow.trigger_config == new_config
        assert workflow.version == 2

    def test_characterize_trigger_type_in_to_dict(self, account_id, user_id) -> None:
        """Characterize: trigger_type is included in to_dict output."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Test Workflow",
            created_by=user_id,
            trigger_type="contact_created",
            trigger_config={"key": "value"},
        )

        result = workflow.to_dict()

        # Document actual behavior
        assert "trigger_type" in result
        assert result["trigger_type"] == "contact_created"
        assert "trigger_config" in result
        assert result["trigger_config"] == {"key": "value"}

    def test_characterize_workflow_status_independent_of_trigger(
        self, account_id, user_id
    ) -> None:
        """Characterize: workflow status transitions work regardless of trigger."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Test Workflow",
            created_by=user_id,
            trigger_type="contact_created",
        )

        # Can activate even with trigger configured
        workflow.activate(updated_by=user_id)
        assert workflow.status == WorkflowStatus.ACTIVE
        assert workflow.trigger_type == "contact_created"

        # Can pause with trigger
        workflow.pause(updated_by=user_id)
        assert workflow.status == WorkflowStatus.PAUSED
        assert workflow.trigger_type == "contact_created"

    def test_characterize_trigger_without_workflow(self, account_id, user_id) -> None:
        """Characterize: workflow can exist without trigger configuration."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Test Workflow",
            created_by=user_id,
        )

        # Can activate workflow even without trigger
        workflow.activate(updated_by=user_id)
        assert workflow.is_active
        assert workflow.trigger_type is None

    def test_characterize_multiple_trigger_config_fields(self, account_id, user_id) -> None:
        """Characterize: trigger_config can contain multiple top-level fields."""
        config = {
            "filters": {
                "conditions": [
                    {"field": "tags", "operator": "contains", "value": "lead"}
                ],
                "logic": "AND",
            },
            "settings": {
                "enrollment_limit": "single",
                "respect_business_hours": True,
            },
            "custom_field": "custom_value",
        }
        workflow = Workflow.create(
            account_id=account_id,
            name="Test Workflow",
            created_by=user_id,
            trigger_config=config,
        )

        # Document actual behavior - all fields preserved
        assert workflow.trigger_config == config
        assert workflow.trigger_config["filters"]["logic"] == "AND"
        assert workflow.trigger_config["settings"]["enrollment_limit"] == "single"

    def test_characterize_trigger_config_mutation_direct(self, account_id, user_id) -> None:
        """Characterize: trigger_config dict can be mutated directly (no immutability)."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Test Workflow",
            created_by=user_id,
            trigger_config={"initial": "value"},
        )

        # Direct mutation is possible (not immutable)
        workflow.trigger_config["new_field"] = "new_value"

        # Document actual behavior - mutation works
        assert workflow.trigger_config == {"initial": "value", "new_field": "new_value"}

    def test_characterize_timestamp_behavior_with_trigger(self, account_id, user_id) -> None:
        """Characterize: timestamps update when trigger is updated."""
        before = datetime.now(UTC)
        workflow = Workflow.create(
            account_id=account_id,
            name="Test Workflow",
            created_by=user_id,
        )
        after_creation = datetime.now(UTC)

        assert before <= workflow.created_at <= after_creation
        assert before <= workflow.updated_at <= after_creation

        # Wait a bit and update trigger
        import time

        time.sleep(0.01)
        before_update = datetime.now(UTC)
        workflow.update(
            updated_by=user_id,
            trigger_type="contact_created",
            trigger_config={"filters": {"tag": "lead"}},
        )
        after_update = datetime.now(UTC)

        # updated_at should be after creation
        assert workflow.updated_at > workflow.created_at
        assert before_update <= workflow.updated_at <= after_update

    def test_characterize_version_increments_with_trigger_update(
        self, account_id, user_id
    ) -> None:
        """Characterize: version increments on trigger update."""
        workflow = Workflow.create(
            account_id=account_id,
            name="Test Workflow",
            created_by=user_id,
        )
        assert workflow.version == 1

        workflow.update(updated_by=user_id, trigger_type="contact_created")
        assert workflow.version == 2

        workflow.update(updated_by=user_id, trigger_config={"new": "config"})
        assert workflow.version == 3

        workflow.update(
            updated_by=user_id, trigger_type="form_submitted", trigger_config={}
        )
        assert workflow.version == 4
