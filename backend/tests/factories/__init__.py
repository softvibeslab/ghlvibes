"""Test factories for generating test data."""

import uuid
from datetime import datetime
from typing import Optional

import factory
from factory import Faker, LazyFunction, SubFactory, post_generation

from src.workflows.domain.entities import (
    Action,
    Condition,
    Goal,
    Trigger,
    Workflow,
)
from src.workflows.domain.value_objects import (
    ActionName,
    ActionPriority,
    ActionType,
    ConditionName,
    ConditionOperator,
    ConditionType,
    GoalName,
    GoalThreshold,
    TriggerName,
    TriggerType,
    WorkflowDescription,
    WorkflowName,
)
from src.workflows.domain.exceptions import InvalidWorkflowNameError
from src.workflows.domain.entities import (
    WorkflowStatus,
    ActionStatus,
    ConditionStatus,
    TriggerStatus,
    GoalStatus,
)


class WorkflowFactory(factory.Factory):
    """Factory for creating Workflow entities in tests."""

    class Meta:
        model = Workflow

    id = LazyFunction(uuid.uuid4)
    account_id = LazyFunction(uuid.uuid4)
    name = Faker("sentence", nb_words=3)
    description = Faker("text", max_nb_chars=200)
    status = WorkflowStatus.DRAFT
    version = 1
    trigger_type = None
    created_at = LazyFunction(datetime.utcnow)
    updated_at = LazyFunction(datetime.utcnow)

    class Params:
        """Factory parameters for common test scenarios."""

        active = factory.Trait(
            status=WorkflowStatus.ACTIVE,
            trigger_type=TriggerType.WEBHOOK
        )

        paused = factory.Trait(
            status=WorkflowStatus.PAUSED
        )

        archived = factory.Trait(
            status=WorkflowStatus.ARCHIVED
        )

        with_webhook_trigger = factory.Trait(
            trigger_type=TriggerType.WEBHOOK
        )

        with_manual_trigger = factory.Trait(
            trigger_type=TriggerType.MANUAL
        )

        with_scheduled_trigger = factory.Trait(
            trigger_type=TriggerType.SCHEDULED
        )

        minimal = factory.Trait(
            name="Minimal Workflow",
            description=""
        )

        version_2 = factory.Trait(
            version=2
        )


class TriggerFactory(factory.Factory):
    """Factory for creating Trigger entities in tests."""

    class Meta:
        model = Trigger

    id = LazyFunction(uuid.uuid4)
    workflow_id = LazyFunction(uuid.uuid4)
    trigger_type = TriggerType.WEBHOOK
    config = {}
    status = TriggerStatus.ACTIVE
    created_at = LazyFunction(datetime.utcnow)
    updated_at = LazyFunction(datetime.utcnow)

    class Params:
        webhook = factory.Trait(
            trigger_type=TriggerType.WEBHOOK,
            config={"webhook_url": "/webhooks/test"}
        )

        manual = factory.Trait(
            trigger_type=TriggerType.MANUAL,
            config={}
        )

        scheduled = factory.Trait(
            trigger_type=TriggerType.SCHEDULED,
            config={"schedule": "0 0 * * *"}  # Daily
        )

        contact_added = factory.Trait(
            trigger_type=TriggerType.CONTACT_ADDED,
            config={"tags": ["new-lead"]}
        )


class ActionFactory(factory.Factory):
    """Factory for creating Action entities in tests."""

    class Meta:
        model = Action

    id = LazyFunction(uuid.uuid4)
    workflow_id = LazyFunction(uuid.uuid4)
    action_type = ActionType.SEND_EMAIL
    config = {}
    status = ActionStatus.ACTIVE
    order = 1
    created_at = LazyFunction(datetime.utcnow)
    updated_at = LazyFunction(datetime.utcnow)

    class Params:
        send_email = factory.Trait(
            action_type=ActionType.SEND_EMAIL,
            config={
                "to": "{{contact.email}}",
                "subject": "Test Email",
                "body": "Test body"
            }
        )

        update_contact = factory.Trait(
            action_type=ActionType.UPDATE_CONTACT,
            config={
                "updates": {"tags": ["processed"]}
            }
        )

        add_tag = factory.Trait(
            action_type=ActionType.ADD_TAG,
            config={
                "tags": ["customer", "qualified"]
            }
        )

        remove_tag = factory.Trait(
            action_type=ActionType.REMOVE_TAG,
            config={
                "tags": ["unqualified"]
            }
        )

        wait = factory.Trait(
            action_type=ActionType.WAIT,
            config={
                "duration": 60,
                "unit": "minutes"
            }
        )


class ConditionFactory(factory.Factory):
    """Factory for creating Condition entities in tests."""

    class Meta:
        model = Condition

    id = LazyFunction(uuid.uuid4)
    workflow_id = LazyFunction(uuid.uuid4)
    condition_type = ConditionType.FIELD_COMPARISON
    operator = ConditionOperator.EQUALS
    value = ""
    status = ConditionStatus.ACTIVE
    created_at = LazyFunction(datetime.utcnow)
    updated_at = LazyFunction(datetime.utcnow)

    class Params:
        field_equals = factory.Trait(
            condition_type=ConditionType.FIELD_COMPARISON,
            operator=ConditionOperator.EQUALS,
            value="premium"
        )

        field_contains = factory.Trait(
            condition_type=ConditionType.FIELD_COMPARISON,
            operator=ConditionOperator.CONTAINS,
            value="important"
        )

        field_greater_than = factory.Trait(
            condition_type=ConditionType.FIELD_COMPARISON,
            operator=ConditionOperator.GREATER_THAN,
            value="100"
        )

        has_tag = factory.Trait(
            condition_type=ConditionType.HAS_TAG,
            operator=ConditionOperator.EQUALS,
            value="vip"
        )

        webhook_received = factory.Trait(
            condition_type=ConditionType.WEBHOOK_RECEIVED,
            operator=ConditionOperator.EQUALS,
            value="webhook-event"
        )


class GoalFactory(factory.Factory):
    """Factory for creating Goal entities in tests."""

    class Meta:
        model = Goal

    id = LazyFunction(uuid.uuid4)
    workflow_id = LazyFunction(uuid.uuid4)
    goal_type = "workflow_completion"
    threshold = 100
    current_value = 0
    status = GoalStatus.ACTIVE
    created_at = LazyFunction(datetime.utcnow)
    updated_at = LazyFunction(datetime.utcnow)

    class Params:
        completion_goal = factory.Trait(
            goal_type="workflow_completion",
            threshold=100,
            current_value=45
        )

        conversion_goal = factory.Trait(
            goal_type="conversion",
            threshold=50,
            current_value=25
        )

        engagement_goal = factory.Trait(
            goal_type="engagement",
            threshold=1000,
            current_value=750
        )

        achieved = factory.Trait(
            status=GoalStatus.ACHIEVED,
            current_value=100
        )

        in_progress = factory.Trait(
            status=GoalStatus.IN_PROGRESS,
            current_value=50
        )
