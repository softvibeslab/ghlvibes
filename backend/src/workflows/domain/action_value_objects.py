"""Value objects for workflow actions.

This module defines value objects for action types and configurations.
Value objects are immutable and represent domain concepts.
"""

import json
from enum import Enum
from typing import Any, Literal

from src.workflows.domain.action_exceptions import InvalidActionConfigurationError


class ActionType(str, Enum):
    """Types of workflow actions.

    These represent all the different actions that can be added to a workflow.
    They are organized into categories:

    Communication:
    - send_email: Send email via SendGrid
    - send_sms: Send SMS via Twilio
    - send_voicemail: Send voicemail via Twilio
    - send_messenger: Send message via Facebook Messenger
    - make_call: Make phone call via Twilio

    CRM Operations:
    - create_contact: Create a new contact
    - update_contact: Update existing contact fields
    - add_tag: Add tag to contact
    - remove_tag: Remove tag from contact
    - add_to_campaign: Add contact to campaign
    - remove_from_campaign: Remove contact from campaign
    - move_pipeline_stage: Move opportunity to new stage
    - assign_to_user: Assign contact to user
    - create_task: Create task for contact
    - add_note: Add note to contact

    Timing:
    - wait_time: Wait for specified duration
    - wait_until_date: Wait until specific date/time
    - wait_for_event: Wait for specific event

    Internal:
    - send_notification: Send internal notification
    - create_opportunity: Create opportunity in pipeline
    - webhook_call: Call external webhook
    - custom_code: Execute custom JavaScript code

    Membership:
    - grant_course_access: Grant access to course
    - revoke_course_access: Revoke access to course
    """

    # Communication actions
    SEND_EMAIL = "send_email"
    SEND_SMS = "send_sms"
    SEND_VOICEMAIL = "send_voicemail"
    SEND_MESSENGER = "send_messenger"
    MAKE_CALL = "make_call"

    # CRM actions
    CREATE_CONTACT = "create_contact"
    UPDATE_CONTACT = "update_contact"
    ADD_TAG = "add_tag"
    REMOVE_TAG = "remove_tag"
    ADD_TO_CAMPAIGN = "add_to_campaign"
    REMOVE_FROM_CAMPAIGN = "remove_from_campaign"
    MOVE_PIPELINE_STAGE = "move_pipeline_stage"
    ASSIGN_TO_USER = "assign_to_user"
    CREATE_TASK = "create_task"
    ADD_NOTE = "add_note"

    # Timing actions
    WAIT_TIME = "wait_time"
    WAIT_UNTIL_DATE = "wait_until_date"
    WAIT_FOR_EVENT = "wait_for_event"

    # Internal actions
    SEND_NOTIFICATION = "send_notification"
    CREATE_OPPORTUNITY = "create_opportunity"
    WEBHOOK_CALL = "webhook_call"
    CUSTOM_CODE = "custom_code"

    # Membership actions
    GRANT_COURSE_ACCESS = "grant_course_access"
    REVOKE_COURSE_ACCESS = "revoke_course_access"

    @property
    def category(self) -> str:
        """Get the category of this action type."""
        category_map = {
            # Communication
            ActionType.SEND_EMAIL: "communication",
            ActionType.SEND_SMS: "communication",
            ActionType.SEND_VOICEMAIL: "communication",
            ActionType.SEND_MESSENGER: "communication",
            ActionType.MAKE_CALL: "communication",
            # CRM
            ActionType.CREATE_CONTACT: "crm",
            ActionType.UPDATE_CONTACT: "crm",
            ActionType.ADD_TAG: "crm",
            ActionType.REMOVE_TAG: "crm",
            ActionType.ADD_TO_CAMPAIGN: "crm",
            ActionType.REMOVE_FROM_CAMPAIGN: "crm",
            ActionType.MOVE_PIPELINE_STAGE: "crm",
            ActionType.ASSIGN_TO_USER: "crm",
            ActionType.CREATE_TASK: "crm",
            ActionType.ADD_NOTE: "crm",
            # Timing
            ActionType.WAIT_TIME: "timing",
            ActionType.WAIT_UNTIL_DATE: "timing",
            ActionType.WAIT_FOR_EVENT: "timing",
            # Internal
            ActionType.SEND_NOTIFICATION: "internal",
            ActionType.CREATE_OPPORTUNITY: "internal",
            ActionType.WEBHOOK_CALL: "internal",
            ActionType.CUSTOM_CODE: "internal",
            # Membership
            ActionType.GRANT_COURSE_ACCESS: "membership",
            ActionType.REVOKE_COURSE_ACCESS: "membership",
        }
        return category_map.get(self, "unknown")

    @property
    def requires_execution_tracking(self) -> bool:
        """Check if this action type requires execution tracking."""
        # Most actions require tracking, except simple timing actions
        return self != ActionType.WAIT_TIME


class ActionConfig:
    """Value object representing action configuration.

    This class provides type-safe configuration for different action types.
    It validates configuration based on the action type requirements.

    Business rules:
    - Configuration must match action type schema
    - Required fields must be present
    - Values must be valid for their types
    - This is an immutable value object
    """

    __slots__ = ("_action_type", "_config")

    def __init__(self, action_type: ActionType, config: dict[str, Any]) -> None:
        """Initialize action configuration with validation.

        Args:
            action_type: The type of action.
            config: Configuration dictionary for the action.

        Raises:
            InvalidActionConfigurationError: If configuration is invalid.
        """
        validated_config = self._validate(action_type, config)
        object.__setattr__(self, "_action_type", action_type)
        object.__setattr__(self, "_config", validated_config)

    def _validate(self, action_type: ActionType, config: dict[str, Any]) -> dict[str, Any]:
        """Validate action configuration.

        Args:
            action_type: The action type to validate against.
            config: The configuration to validate.

        Returns:
            Validated configuration.

        Raises:
            InvalidActionConfigurationError: If validation fails.
        """
        errors = []

        # Validate based on action type
        if action_type == ActionType.SEND_EMAIL:
            errors = self._validate_email_config(config)
        elif action_type == ActionType.SEND_SMS:
            errors = self._validate_sms_config(config)
        elif action_type == ActionType.SEND_VOICEMAIL:
            errors = self._validate_voicemail_config(config)
        elif action_type == ActionType.SEND_MESSENGER:
            errors = self._validate_messenger_config(config)
        elif action_type == ActionType.MAKE_CALL:
            errors = self._validate_call_config(config)
        elif action_type == ActionType.CREATE_CONTACT:
            errors = self._validate_create_contact_config(config)
        elif action_type == ActionType.UPDATE_CONTACT:
            errors = self._validate_update_contact_config(config)
        elif action_type == ActionType.ADD_TAG:
            errors = self._validate_add_tag_config(config)
        elif action_type == ActionType.REMOVE_TAG:
            errors = self._validate_remove_tag_config(config)
        elif action_type == ActionType.ADD_TO_CAMPAIGN:
            errors = self._validate_add_to_campaign_config(config)
        elif action_type == ActionType.REMOVE_FROM_CAMPAIGN:
            errors = self._validate_remove_from_campaign_config(config)
        elif action_type == ActionType.MOVE_PIPELINE_STAGE:
            errors = self._validate_move_pipeline_stage_config(config)
        elif action_type == ActionType.ASSIGN_TO_USER:
            errors = self._validate_assign_to_user_config(config)
        elif action_type == ActionType.CREATE_TASK:
            errors = self._validate_create_task_config(config)
        elif action_type == ActionType.ADD_NOTE:
            errors = self._validate_add_note_config(config)
        elif action_type == ActionType.WAIT_TIME:
            errors = self._validate_wait_time_config(config)
        elif action_type == ActionType.WAIT_UNTIL_DATE:
            errors = self._validate_wait_until_date_config(config)
        elif action_type == ActionType.WAIT_FOR_EVENT:
            errors = self._validate_wait_for_event_config(config)
        elif action_type == ActionType.SEND_NOTIFICATION:
            errors = self._validate_send_notification_config(config)
        elif action_type == ActionType.CREATE_OPPORTUNITY:
            errors = self._validate_create_opportunity_config(config)
        elif action_type == ActionType.WEBHOOK_CALL:
            errors = self._validate_webhook_call_config(config)
        elif action_type == ActionType.CUSTOM_CODE:
            errors = self._validate_custom_code_config(config)
        elif action_type == ActionType.GRANT_COURSE_ACCESS:
            errors = self._validate_grant_course_access_config(config)
        elif action_type == ActionType.REVOKE_COURSE_ACCESS:
            errors = self._validate_revoke_course_access_config(config)
        else:
            # No validation for unknown types
            pass

        if errors:
            raise InvalidActionConfigurationError(
                action_type=action_type.value,
                errors=errors,
            )

        return config

    def _validate_email_config(self, config: dict[str, Any]) -> list[str]:
        """Validate email action configuration."""
        errors = []

        if "template_id" not in config:
            errors.append("template_id is required for send_email action")
        if "subject" not in config:
            errors.append("subject is required for send_email action")
        if "from_name" not in config:
            errors.append("from_name is required for send_email action")
        if "from_email" not in config:
            errors.append("from_email is required for send_email action")

        return errors

    def _validate_sms_config(self, config: dict[str, Any]) -> list[str]:
        """Validate SMS action configuration."""
        errors = []

        if "message" not in config:
            errors.append("message is required for send_sms action")
        elif not isinstance(config["message"], str) or len(config["message"]) > 1600:
            errors.append("message must be a string with max 1600 characters")
        if "from_number" not in config:
            errors.append("from_number is required for send_sms action")

        return errors

    def _validate_voicemail_config(self, config: dict[str, Any]) -> list[str]:
        """Validate voicemail action configuration."""
        errors = []

        if "audio_file_id" not in config:
            errors.append("audio_file_id is required for send_voicemail action")
        if "from_number" not in config:
            errors.append("from_number is required for send_voicemail action")

        return errors

    def _validate_messenger_config(self, config: dict[str, Any]) -> list[str]:
        """Validate messenger action configuration."""
        errors = []

        if "page_id" not in config:
            errors.append("page_id is required for send_messenger action")
        if "message_type" not in config:
            errors.append("message_type is required for send_messenger action")
        elif config["message_type"] not in ["text", "image", "template", "quick_reply"]:
            errors.append("message_type must be one of: text, image, template, quick_reply")
        if "content" not in config:
            errors.append("content is required for send_messenger action")

        return errors

    def _validate_call_config(self, config: dict[str, Any]) -> list[str]:
        """Validate call action configuration."""
        errors = []

        if "from_number" not in config:
            errors.append("from_number is required for make_call action")
        if "destination_type" not in config:
            errors.append("destination_type is required for make_call action")
        elif config["destination_type"] not in ["user", "queue", "external", "ivr"]:
            errors.append("destination_type must be one of: user, queue, external, ivr")
        if "destination_value" not in config:
            errors.append("destination_value is required for make_call action")

        return errors

    def _validate_create_contact_config(self, config: dict[str, Any]) -> list[str]:
        """Validate create contact configuration."""
        # All fields are optional, so no validation needed
        return []

    def _validate_update_contact_config(self, config: dict[str, Any]) -> list[str]:
        """Validate update contact configuration."""
        errors = []

        if "field_updates" not in config:
            errors.append("field_updates is required for update_contact action")
        elif not isinstance(config["field_updates"], list) or len(config["field_updates"]) == 0:
            errors.append("field_updates must be a non-empty array")

        return errors

    def _validate_add_tag_config(self, config: dict[str, Any]) -> list[str]:
        """Validate add tag configuration."""
        errors = []

        if "tag_name" not in config:
            errors.append("tag_name is required for add_tag action")

        return errors

    def _validate_remove_tag_config(self, config: dict[str, Any]) -> list[str]:
        """Validate remove tag configuration."""
        errors = []

        if "tag_name" not in config:
            errors.append("tag_name is required for remove_tag action")

        return errors

    def _validate_add_to_campaign_config(self, config: dict[str, Any]) -> list[str]:
        """Validate add to campaign configuration."""
        errors = []

        if "campaign_id" not in config:
            errors.append("campaign_id is required for add_to_campaign action")

        return errors

    def _validate_remove_from_campaign_config(self, config: dict[str, Any]) -> list[str]:
        """Validate remove from campaign configuration."""
        errors = []

        if "campaign_id" not in config:
            errors.append("campaign_id is required for remove_from_campaign action")

        return errors

    def _validate_move_pipeline_stage_config(self, config: dict[str, Any]) -> list[str]:
        """Validate move pipeline stage configuration."""
        errors = []

        if "pipeline_id" not in config:
            errors.append("pipeline_id is required for move_pipeline_stage action")
        if "stage_id" not in config:
            errors.append("stage_id is required for move_pipeline_stage action")

        return errors

    def _validate_assign_to_user_config(self, config: dict[str, Any]) -> list[str]:
        """Validate assign to user configuration."""
        errors = []

        if "assignment_type" not in config:
            errors.append("assignment_type is required for assign_to_user action")
        elif config["assignment_type"] not in ["specific", "round_robin", "least_busy"]:
            errors.append("assignment_type must be one of: specific, round_robin, least_busy")

        return errors

    def _validate_create_task_config(self, config: dict[str, Any]) -> list[str]:
        """Validate create task configuration."""
        errors = []

        if "title" not in config:
            errors.append("title is required for create_task action")

        return errors

    def _validate_add_note_config(self, config: dict[str, Any]) -> list[str]:
        """Validate add note configuration."""
        errors = []

        if "content" not in config:
            errors.append("content is required for add_note action")

        return errors

    def _validate_wait_time_config(self, config: dict[str, Any]) -> list[str]:
        """Validate wait time configuration."""
        errors = []

        if "duration" not in config:
            errors.append("duration is required for wait_time action")
        elif not isinstance(config["duration"], (int, float)) or config["duration"] <= 0:
            errors.append("duration must be a positive number")
        if "unit" not in config:
            errors.append("unit is required for wait_time action")
        elif config["unit"] not in ["minutes", "hours", "days", "weeks"]:
            errors.append("unit must be one of: minutes, hours, days, weeks")

        return errors

    def _validate_wait_until_date_config(self, config: dict[str, Any]) -> list[str]:
        """Validate wait until date configuration."""
        errors = []

        if "date_type" not in config:
            errors.append("date_type is required for wait_until_date action")
        elif config["date_type"] not in ["specific", "contact_field", "calculated"]:
            errors.append("date_type must be one of: specific, contact_field, calculated")

        return errors

    def _validate_wait_for_event_config(self, config: dict[str, Any]) -> list[str]:
        """Validate wait for event configuration."""
        errors = []

        if "event_type" not in config:
            errors.append("event_type is required for wait_for_event action")
        elif config["event_type"] not in ["email_open", "email_click", "sms_reply", "form_submit"]:
            errors.append("event_type must be one of: email_open, email_click, sms_reply, form_submit")

        return errors

    def _validate_send_notification_config(self, config: dict[str, Any]) -> list[str]:
        """Validate send notification configuration."""
        errors = []

        if "recipient_type" not in config:
            errors.append("recipient_type is required for send_notification action")
        if "channels" not in config:
            errors.append("channels is required for send_notification action")
        if "title" not in config:
            errors.append("title is required for send_notification action")
        if "message" not in config:
            errors.append("message is required for send_notification action")

        return errors

    def _validate_create_opportunity_config(self, config: dict[str, Any]) -> list[str]:
        """Validate create opportunity configuration."""
        errors = []

        if "pipeline_id" not in config:
            errors.append("pipeline_id is required for create_opportunity action")
        if "name" not in config:
            errors.append("name is required for create_opportunity action")

        return errors

    def _validate_webhook_call_config(self, config: dict[str, Any]) -> list[str]:
        """Validate webhook call configuration."""
        errors = []

        if "url" not in config:
            errors.append("url is required for webhook_call action")
        if "method" not in config:
            errors.append("method is required for webhook_call action")
        elif config["method"] not in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
            errors.append("method must be one of: GET, POST, PUT, PATCH, DELETE")

        return errors

    def _validate_custom_code_config(self, config: dict[str, Any]) -> list[str]:
        """Validate custom code configuration."""
        errors = []

        if "code" not in config:
            errors.append("code is required for custom_code action")

        return errors

    def _validate_grant_course_access_config(self, config: dict[str, Any]) -> list[str]:
        """Validate grant course access configuration."""
        errors = []

        if "course_id" not in config:
            errors.append("course_id is required for grant_course_access action")

        return errors

    def _validate_revoke_course_access_config(self, config: dict[str, Any]) -> list[str]:
        """Validate revoke course access configuration."""
        errors = []

        if "course_id" not in config:
            errors.append("course_id is required for revoke_course_access action")

        return errors

    @property
    def action_type(self) -> ActionType:
        """Get the action type."""
        return self._action_type

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key.
            default: Default value if key not found.

        Returns:
            Configuration value or default.
        """
        return self._config.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Configuration dictionary.
        """
        return self._config.copy()

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if isinstance(other, ActionConfig):
            return self._action_type == other._action_type and self._config == other._config
        return False

    def __hash__(self) -> int:
        """Return hash for use in sets and dicts."""
        return hash((self._action_type, json.dumps(self._config, sort_keys=True)))

    def __repr__(self) -> str:
        """Return string representation."""
        return f"ActionConfig({self._action_type.value}, {self._config})"

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-like access."""
        return self._config[key]

    def __contains__(self, key: str) -> bool:
        """Check if key exists in configuration."""
        return key in self._config
