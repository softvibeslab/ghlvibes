"""Unit tests for action value objects.

These tests verify the behavior of action-related value objects
including ActionType and ActionConfig.
"""

import pytest

from src.workflows.domain.action_exceptions import InvalidActionConfigurationError
from src.workflows.domain.action_value_objects import ActionConfig, ActionType


class TestActionType:
    """Test ActionType enum."""

    def test_action_type_values(self) -> None:
        """Test that all expected action types are defined."""
        # Communication actions
        assert ActionType.SEND_EMAIL == "send_email"
        assert ActionType.SEND_SMS == "send_sms"
        assert ActionType.SEND_VOICEMAIL == "send_voicemail"
        assert ActionType.SEND_MESSENGER == "send_messenger"
        assert ActionType.MAKE_CALL == "make_call"

        # CRM actions
        assert ActionType.CREATE_CONTACT == "create_contact"
        assert ActionType.UPDATE_CONTACT == "update_contact"
        assert ActionType.ADD_TAG == "add_tag"
        assert ActionType.REMOVE_TAG == "remove_tag"
        assert ActionType.ADD_TO_CAMPAIGN == "add_to_campaign"
        assert ActionType.REMOVE_FROM_CAMPAIGN == "remove_from_campaign"
        assert ActionType.MOVE_PIPELINE_STAGE == "move_pipeline_stage"
        assert ActionType.ASSIGN_TO_USER == "assign_to_user"
        assert ActionType.CREATE_TASK == "create_task"
        assert ActionType.ADD_NOTE == "add_note"

        # Timing actions
        assert ActionType.WAIT_TIME == "wait_time"
        assert ActionType.WAIT_UNTIL_DATE == "wait_until_date"
        assert ActionType.WAIT_FOR_EVENT == "wait_for_event"

        # Internal actions
        assert ActionType.SEND_NOTIFICATION == "send_notification"
        assert ActionType.CREATE_OPPORTUNITY == "create_opportunity"
        assert ActionType.WEBHOOK_CALL == "webhook_call"
        assert ActionType.CUSTOM_CODE == "custom_code"

        # Membership actions
        assert ActionType.GRANT_COURSE_ACCESS == "grant_course_access"
        assert ActionType.REVOKE_COURSE_ACCESS == "revoke_course_access"

    def test_action_type_categories(self) -> None:
        """Test that action types have correct categories."""
        assert ActionType.SEND_EMAIL.category == "communication"
        assert ActionType.CREATE_CONTACT.category == "crm"
        assert ActionType.WAIT_TIME.category == "timing"
        assert ActionType.SEND_NOTIFICATION.category == "internal"
        assert ActionType.GRANT_COURSE_ACCESS.category == "membership"

    def test_action_type_requires_execution_tracking(self) -> None:
        """Test execution tracking requirement property."""
        assert ActionType.SEND_EMAIL.requires_execution_tracking is True
        assert ActionType.CREATE_CONTACT.requires_execution_tracking is True
        assert ActionType.WAIT_TIME.requires_execution_tracking is False


class TestActionConfig:
    """Test ActionConfig value object."""

    def test_valid_email_config(self) -> None:
        """Test valid email action configuration."""
        config = {
            "template_id": "550e8400-e29b-41d4-a716-446655440000",
            "subject": "Welcome {{contact.first_name}}!",
            "from_name": "Support Team",
            "from_email": "support@example.com",
        }

        action_config = ActionConfig(ActionType.SEND_EMAIL, config)

        assert action_config.action_type == ActionType.SEND_EMAIL
        assert action_config["template_id"] == config["template_id"]
        assert action_config["subject"] == config["subject"]
        assert action_config.to_dict() == config

    def test_valid_sms_config(self) -> None:
        """Test valid SMS action configuration."""
        config = {
            "message": "Hello from our team!",
            "from_number": "+1234567890",
        }

        action_config = ActionConfig(ActionType.SEND_SMS, config)

        assert action_config.action_type == ActionType.SEND_SMS
        assert action_config["message"] == config["message"]
        assert action_config.to_dict() == config

    def test_valid_wait_time_config(self) -> None:
        """Test valid wait_time action configuration."""
        config = {
            "duration": 5,
            "unit": "days",
        }

        action_config = ActionConfig(ActionType.WAIT_TIME, config)

        assert action_config.action_type == ActionType.WAIT_TIME
        assert action_config["duration"] == 5
        assert action_config["unit"] == "days"

    def test_invalid_email_config_missing_fields(self) -> None:
        """Test that email config without required fields raises error."""
        config = {
            "subject": "Test",
            # Missing template_id, from_name, from_email
        }

        with pytest.raises(InvalidActionConfigurationError) as exc_info:
            ActionConfig(ActionType.SEND_EMAIL, config)

        assert exc_info.value.action_type == "send_email"
        assert len(exc_info.value.errors) > 0
        assert "template_id" in str(exc_info.value.errors).lower()

    def test_invalid_sms_config_message_too_long(self) -> None:
        """Test that SMS message over 1600 characters raises error."""
        config = {
            "message": "a" * 1601,  # Exceeds 1600 character limit
            "from_number": "+1234567890",
        }

        with pytest.raises(InvalidActionConfigurationError) as exc_info:
            ActionConfig(ActionType.SEND_SMS, config)

        assert exc_info.value.action_type == "send_sms"

    def test_invalid_wait_time_config_invalid_unit(self) -> None:
        """Test that wait_time with invalid unit raises error."""
        config = {
            "duration": 5,
            "unit": "invalid_unit",
        }

        with pytest.raises(InvalidActionConfigurationError) as exc_info:
            ActionConfig(ActionType.WAIT_TIME, config)

        assert exc_info.value.action_type == "wait_time"

    def test_action_config_get_method(self) -> None:
        """Test ActionConfig get method with default values."""
        config = {
            "template_id": "test-id",
            "subject": "Test",
            "from_name": "Test",
            "from_email": "test@example.com",
        }

        action_config = ActionConfig(ActionType.SEND_EMAIL, config)

        assert action_config.get("template_id") == "test-id"
        assert action_config.get("nonexistent") is None
        assert action_config.get("nonexistent", "default") == "default"

    def test_action_config_contains(self) -> None:
        """Test 'in' operator for ActionConfig."""
        config = {
            "template_id": "test-id",
            "subject": "Test",
        }

        action_config = ActionConfig(ActionType.SEND_EMAIL, config)

        assert "template_id" in action_config
        assert "subject" in action_config
        assert "nonexistent" not in action_config

    def test_action_config_immutability(self) -> None:
        """Test that ActionConfig is immutable."""
        config = {"template_id": "test-id"}
        action_config = ActionConfig(ActionType.SEND_EMAIL, config)

        # Attempting to set attribute should raise AttributeError
        with pytest.raises(AttributeError):
            action_config.new_field = "value"  # type: ignore

    def test_action_config_equality(self) -> None:
        """Test ActionConfig equality."""
        config1 = {"template_id": "test-id", "subject": "Test"}
        config2 = {"template_id": "test-id", "subject": "Test"}
        config3 = {"template_id": "other-id", "subject": "Test"}

        action_config1 = ActionConfig(ActionType.SEND_EMAIL, config1)
        action_config2 = ActionConfig(ActionType.SEND_EMAIL, config2)
        action_config3 = ActionConfig(ActionType.SEND_EMAIL, config3)

        assert action_config1 == action_config2
        assert action_config1 != action_config3

    def test_action_config_hash(self) -> None:
        """Test ActionConfig hash for use in sets."""
        config = {"template_id": "test-id", "subject": "Test"}
        action_config = ActionConfig(ActionType.SEND_EMAIL, config)

        # Should be hashable
        hash_value = hash(action_config)
        assert isinstance(hash_value, int)

        # Same config should have same hash
        action_config2 = ActionConfig(ActionType.SEND_EMAIL, config)
        assert hash(action_config) == hash(action_config2)

    def test_action_config_repr(self) -> None:
        """Test ActionConfig string representation."""
        config = {"template_id": "test-id"}
        action_config = ActionConfig(ActionType.SEND_EMAIL, config)

        repr_str = repr(action_config)
        assert "send_email" in repr_str
        assert "test-id" in repr_str

    def test_messenger_config_validation(self) -> None:
        """Test messenger action configuration validation."""
        # Valid config
        config = {
            "page_id": "page-123",
            "message_type": "text",
            "content": {"text": "Hello"},
        }
        action_config = ActionConfig(ActionType.SEND_MESSENGER, config)
        assert action_config["message_type"] == "text"

        # Invalid message_type
        invalid_config = {
            "page_id": "page-123",
            "message_type": "invalid",
            "content": {"text": "Hello"},
        }
        with pytest.raises(InvalidActionConfigurationError):
            ActionConfig(ActionType.SEND_MESSENGER, invalid_config)

    def test_webhook_config_validation(self) -> None:
        """Test webhook action configuration validation."""
        # Valid config
        config = {
            "url": "https://example.com/webhook",
            "method": "POST",
        }
        action_config = ActionConfig(ActionType.WEBHOOK_CALL, config)
        assert action_config["url"] == "https://example.com/webhook"

        # Invalid method
        invalid_config = {
            "url": "https://example.com/webhook",
            "method": "INVALID",
        }
        with pytest.raises(InvalidActionConfigurationError):
            ActionConfig(ActionType.WEBHOOK_CALL, invalid_config)

    def test_create_contact_config_all_optional(self) -> None:
        """Test that create_contact accepts empty config."""
        config = {}
        action_config = ActionConfig(ActionType.CREATE_CONTACT, config)
        assert action_config.to_dict() == {}

    def test_update_contact_config_validation(self) -> None:
        """Test update_contact config validation."""
        # Valid config
        config = {
            "field_updates": [
                {"field": "first_name", "value": "John"},
                {"field": "last_name", "value": "Doe"},
            ]
        }
        action_config = ActionConfig(ActionType.UPDATE_CONTACT, config)
        assert len(action_config["field_updates"]) == 2

        # Missing field_updates
        invalid_config = {}
        with pytest.raises(InvalidActionConfigurationError):
            ActionConfig(ActionType.UPDATE_CONTACT, invalid_config)

    def test_add_tag_config_validation(self) -> None:
        """Test add_tag config validation."""
        # Valid config
        config = {"tag_name": "VIP Customer"}
        action_config = ActionConfig(ActionType.ADD_TAG, config)
        assert action_config["tag_name"] == "VIP Customer"

        # Missing tag_name
        invalid_config = {}
        with pytest.raises(InvalidActionConfigurationError):
            ActionConfig(ActionType.ADD_TAG, invalid_config)
