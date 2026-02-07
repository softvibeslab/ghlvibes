"""Service for detecting goal achievement from events.

This service evaluates incoming events against configured goals
to determine if a contact has achieved a goal.
"""

from uuid import UUID

from src.workflows.application.goal_dtos import GoalEvaluationResultDTO
from src.workflows.domain.goal_entities import GoalConfig, GoalCriteria, GoalType
from src.workflows.infrastructure.goal_repository import (
    IGoalAchievementRepository,
    IGoalRepository,
)


class GoalDetectionService:
    """Service for detecting goal achievement from events.

    Evaluates events (tag added, purchase made, appointment booked, etc.)
    against configured goals to determine if workflow exit should be triggered.
    """

    def __init__(
        self,
        goal_repository: IGoalRepository,
        achievement_repository: IGoalAchievementRepository,
    ) -> None:
        """Initialize the service.
        Args:
            goal_repository: Goal configuration repository.
            achievement_repository: Goal achievement repository.
        """
        self._goal_repository = goal_repository
        self._achievement_repository = achievement_repository

    async def evaluate_event(
        self,
        workflow_id: UUID,
        contact_id: UUID,
        account_id: UUID,
        event_type: str,
        event_data: dict,
    ) -> GoalEvaluationResultDTO:
        """Evaluate an event for goal achievement.
        Args:
            workflow_id: Workflow to check.
            contact_id: Contact to evaluate.
            account_id: Account/tenant ID.
            event_type: Type of event (e.g., "contact.tag.added").
            event_data: Event payload data.
        Returns:
            Goal evaluation result indicating if goal was achieved.
        """
        # Get active goals for workflow
        goals = await self._goal_repository.list_by_workflow(
            workflow_id=workflow_id,
            account_id=account_id,
            offset=0,
            limit=100,  # Support multiple goals
        )

        # Filter active goals
        active_goals = [g for g in goals if g.is_active]

        if not active_goals:
            return GoalEvaluationResultDTO(
                goal_achieved=False,
                goal_config_id=None,
                goal_type=None,
                should_exit_workflow=False,
            )

        # Evaluate each goal
        for goal in active_goals:
            if await self._check_goal_achieved(goal, event_type, event_data):
                # Check if not already achieved
                already_achieved = await self._achievement_repository.check_already_achieved(
                    contact_id=contact_id,
                    goal_config_id=goal.id,
                    account_id=account_id,
                )

                if not already_achieved:
                    return GoalEvaluationResultDTO(
                        goal_achieved=True,
                        goal_config_id=goal.id,
                        goal_type=goal.goal_type.value,
                        should_exit_workflow=True,
                    )

        # No goal achieved
        return GoalEvaluationResultDTO(
            goal_achieved=False,
            goal_config_id=None,
            goal_type=None,
            should_exit_workflow=False,
        )

    async def _check_goal_achieved(
        self,
        goal: GoalConfig,
        event_type: str,
        event_data: dict,
    ) -> bool:
        """Check if an event indicates goal achievement.
        Args:
            goal: Goal configuration to check.
            event_type: Type of event.
            event_data: Event data.
        Returns:
            True if goal achieved, False otherwise.
        """
        criteria = goal.criteria.criteria

        if goal.goal_type == GoalType.TAG_ADDED:
            return self._check_tag_goal(event_type, event_data, criteria)

        if goal.goal_type == GoalType.PURCHASE_MADE:
            return self._check_purchase_goal(event_type, event_data, criteria)

        if goal.goal_type == GoalType.APPOINTMENT_BOOKED:
            return self._check_appointment_goal(event_type, event_data, criteria)

        if goal.goal_type == GoalType.FORM_SUBMITTED:
            return self._check_form_goal(event_type, event_data, criteria)

        if goal.goal_type == GoalType.PIPELINE_STAGE_REACHED:
            return self._check_pipeline_goal(event_type, event_data, criteria)

        return False

    def _check_tag_goal(
        self,
        event_type: str,
        event_data: dict,
        criteria: dict,
    ) -> bool:
        """Check if tag added goal is achieved."""
        if event_type != "contact.tag.added":
            return False

        # Check tag_id match
        if "tag_id" in criteria:
            return str(event_data.get("tag_id", "")) == str(criteria["tag_id"])

        # Check tag_name match
        if "tag_name" in criteria:
            return event_data.get("tag_name", "") == criteria["tag_name"]

        return False

    def _check_purchase_goal(
        self,
        event_type: str,
        event_data: dict,
        criteria: dict,
    ) -> bool:
        """Check if purchase made goal is achieved."""
        if event_type != "payment.completed":
            return False

        # Any purchase
        if criteria.get("any_purchase", False):
            return True

        # Specific product
        if "product_id" in criteria:
            return str(event_data.get("product_id", "")) == str(criteria["product_id"])

        # Minimum amount
        if "min_amount" in criteria:
            return event_data.get("amount", 0) >= criteria["min_amount"]

        return False

    def _check_appointment_goal(
        self,
        event_type: str,
        event_data: dict,
        criteria: dict,
    ) -> bool:
        """Check if appointment booked goal is achieved."""
        if event_type != "appointment.booked":
            return False

        # Any appointment
        if criteria.get("any_appointment", False):
            return True

        # Specific calendar
        if "calendar_id" in criteria:
            return (
                str(event_data.get("calendar_id", "")) == str(criteria["calendar_id"])
            )

        # Specific service
        if "service_id" in criteria:
            return str(event_data.get("service_id", "")) == str(criteria["service_id"])

        return False

    def _check_form_goal(
        self,
        event_type: str,
        event_data: dict,
        criteria: dict,
    ) -> bool:
        """Check if form submitted goal is achieved."""
        if event_type != "form.submitted":
            return False

        # Check form_id match
        return str(event_data.get("form_id", "")) == str(criteria.get("form_id", ""))

    def _check_pipeline_goal(
        self,
        event_type: str,
        event_data: dict,
        criteria: dict,
    ) -> bool:
        """Check if pipeline stage reached goal is achieved."""
        if event_type != "pipeline.stage.changed":
            return False

        # Check pipeline_id match
        if str(event_data.get("pipeline_id", "")) != str(criteria.get("pipeline_id", "")):
            return False

        # Check stage_id match
        return str(event_data.get("stage_id", "")) == str(criteria.get("stage_id", ""))


class GoalAchievementService:
    """Service for recording and managing goal achievements.

    Creates achievement records and triggers workflow exit when
    goals are achieved.
    """

    def __init__(
        self,
        achievement_repository: IGoalAchievementRepository,
    ) -> None:
        """Initialize the service.
        Args:
            achievement_repository: Goal achievement repository.
        """
        self._achievement_repository = achievement_repository

    async def record_achievement(
        self,
        workflow_id: UUID,
        workflow_enrollment_id: UUID,
        contact_id: UUID,
        goal_config_id: UUID,
        account_id: UUID,
        goal_type: GoalType,
        trigger_event: dict,
        metadata: dict | None = None,
    ) -> None:
        """Record a goal achievement.
        Args:
            workflow_id: Workflow where goal was achieved.
            workflow_enrollment_id: Enrollment that achieved goal.
            contact_id: Contact who achieved goal.
            goal_config_id: Goal configuration that was achieved.
            account_id: Account/tenant ID.
            goal_type: Type of goal achieved.
            trigger_event: Event data that triggered achievement.
            metadata: Additional context (optional).
        """
        from src.workflows.domain.goal_entities import GoalAchievement

        achievement = GoalAchievement.create(
            workflow_id=workflow_id,
            workflow_enrollment_id=workflow_enrollment_id,
            contact_id=contact_id,
            goal_config_id=goal_config_id,
            account_id=account_id,
            goal_type=goal_type,
            trigger_event=trigger_event,
            metadata=metadata,
        )

        await self._achievement_repository.create(achievement)
