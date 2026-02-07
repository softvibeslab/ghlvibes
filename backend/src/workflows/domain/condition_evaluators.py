"""Condition evaluation strategies.

This module implements the Strategy pattern for evaluating different
condition types. Each condition type has its own evaluator strategy.

Strategy Pattern:
- BaseConditionEvaluator: Abstract base class defining the interface
- Type-specific evaluators: Implement evaluation logic for each condition type
- ConditionEvaluatorFactory: Creates appropriate evaluator based on type
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any

from src.workflows.domain.condition_exceptions import ConditionEvaluationError
from src.workflows.domain.condition_value_objects import (
    ConditionConfig,
    ConditionType,
    FieldOperator,
    TagOperator,
)


class EvaluationContext:
    """Context data for condition evaluation.

    Attributes:
        contact_id: ID of contact being evaluated
        contact_data: Contact field values
        tags: Contact's tags
        pipeline_stages: Contact's pipeline stages
        custom_fields: Contact's custom field values
        email_engagement: Email engagement data
        execution_id: Workflow execution ID
    """

    def __init__(
        self,
        contact_id: str,
        contact_data: dict[str, Any],
        tags: list[str] | None = None,
        pipeline_stages: dict[str, str] | None = None,
        custom_fields: dict[str, Any] | None = None,
        email_engagement: dict[str, Any] | None = None,
        execution_id: str | None = None,
    ) -> None:
        """Initialize evaluation context.

        Args:
            contact_id: Contact ID.
            contact_data: Contact field data.
            tags: Contact tags.
            pipeline_stages: Pipeline stage data.
            custom_fields: Custom field values.
            email_engagement: Email engagement data.
            execution_id: Execution ID.
        """
        self.contact_id = contact_id
        self.contact_data = contact_data
        self.tags = set(tags or [])
        self.pipeline_stages = pipeline_stages or {}
        self.custom_fields = custom_fields or {}
        self.email_engagement = email_engagement or {}
        self.execution_id = execution_id


class EvaluationResult:
    """Result of condition evaluation.

    Attributes:
        match: Whether the condition matched
        branch_name: Name of matching branch
        branch_id: ID of matching branch
        details: Evaluation details for logging
        duration_ms: Evaluation duration in milliseconds
    """

    def __init__(
        self,
        match: bool,
        branch_name: str | None = None,
        branch_id: str | None = None,
        details: dict[str, Any] | None = None,
        duration_ms: int = 0,
    ) -> None:
        """Initialize evaluation result.

        Args:
            match: Whether condition matched.
            branch_name: Name of matching branch.
            branch_id: ID of matching branch.
            details: Evaluation details.
            duration_ms: Duration in milliseconds.
        """
        self.match = match
        self.branch_name = branch_name
        self.branch_id = branch_id
        self.details = details or {}
        self.duration_ms = duration_ms

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "match": self.match,
            "branch_name": self.branch_name,
            "branch_id": self.branch_id,
            "details": self.details,
            "duration_ms": self.duration_ms,
        }


class BaseConditionEvaluator(ABC):
    """Abstract base class for condition evaluators.

    Each condition type has its own evaluator that implements
    the evaluation logic for that type.
    """

    @abstractmethod
    def evaluate(
        self,
        config: ConditionConfig,
        context: EvaluationContext,
    ) -> EvaluationResult:
        """Evaluate the condition.

        Args:
            config: Condition configuration.
            context: Evaluation context.

        Returns:
            Evaluation result.

        Raises:
            ConditionEvaluationError: If evaluation fails.
        """
        pass

    def _get_field_value(self, field: str, context: EvaluationContext) -> Any:
        """Get field value from context.

        Args:
            field: Field name.
            context: Evaluation context.

        Returns:
            Field value or None if not found.
        """
        return context.contact_data.get(field)

    def _compare_values(
        self,
        operator: str,
        actual: Any,
        expected: Any,
    ) -> bool:
        """Compare two values using the specified operator.

        Args:
            operator: Comparison operator.
            actual: Actual value.
            expected: Expected value.

        Returns:
            True if comparison matches, False otherwise.
        """
        # Handle null/empty values
        if operator == FieldOperator.IS_EMPTY:
            return actual is None or actual == ""
        if operator == FieldOperator.IS_NOT_EMPTY:
            return actual is not None and actual != ""

        # Handle None actual value for other operators
        if actual is None:
            return False

        # Type coercion for numeric comparisons
        if operator in (FieldOperator.GREATER_THAN, FieldOperator.LESS_THAN):
            try:
                actual_num = float(actual)
                expected_num = float(expected)
                if operator == FieldOperator.GREATER_THAN:
                    return actual_num > expected_num
                else:
                    return actual_num < expected_num
            except (ValueError, TypeError):
                return False

        # String comparisons (case-insensitive by default)
        if isinstance(actual, str) and isinstance(expected, str):
            actual_lower = actual.lower()
            expected_lower = expected.lower()

            if operator == FieldOperator.EQUALS:
                return actual_lower == expected_lower
            if operator == FieldOperator.NOT_EQUALS:
                return actual_lower != expected_lower
            if operator == FieldOperator.CONTAINS:
                return expected_lower in actual_lower
            if operator == FieldOperator.NOT_CONTAINS:
                return expected_lower not in actual_lower
            if operator == FieldOperator.STARTS_WITH:
                return actual_lower.startswith(expected_lower)
            if operator == FieldOperator.ENDS_WITH:
                return actual_lower.endswith(expected_lower)

        # List comparisons
        if operator in (FieldOperator.IN_LIST, FieldOperator.NOT_IN_LIST):
            if isinstance(expected, list):
                in_list = actual in expected
                return in_list if operator == FieldOperator.IN_LIST else not in_list
            # Single value comparison
            in_list = actual == expected
            return in_list if operator == FieldOperator.IN_LIST else not in_list

        # Default equality comparison
        if operator == FieldOperator.EQUALS:
            return actual == expected
        if operator == FieldOperator.NOT_EQUALS:
            return actual != expected

        return False


class FieldConditionEvaluator(BaseConditionEvaluator):
    """Evaluator for contact field conditions.

    Evaluates conditions based on contact field values using
    various comparison operators.
    """

    def evaluate(
        self,
        config: ConditionConfig,
        context: EvaluationContext,
    ) -> EvaluationResult:
        """Evaluate field condition.

        Args:
            config: Condition configuration.
            context: Evaluation context.

        Returns:
            Evaluation result.
        """
        if not config.field:
            raise ConditionEvaluationError("Field name is required for field condition")

        actual_value = self._get_field_value(config.field, context)
        match = self._compare_values(
            config.operator or FieldOperator.EQUALS,
            actual_value,
            config.value,
        )

        return EvaluationResult(
            match=match,
            details={
                "field": config.field,
                "operator": config.operator,
                "actual_value": str(actual_value) if actual_value is not None else None,
                "expected_value": str(config.value) if config.value is not None else None,
            },
        )


class TagConditionEvaluator(BaseConditionEvaluator):
    """Evaluator for tag-based conditions.

    Evaluates conditions based on contact tags using
    various tag operators (has_any, has_all, has_none, has_only).
    """

    def evaluate(
        self,
        config: ConditionConfig,
        context: EvaluationContext,
    ) -> EvaluationResult:
        """Evaluate tag condition.

        Args:
            config: Condition configuration.
            context: Evaluation context.

        Returns:
            Evaluation result.
        """
        if not config.tags:
            raise ConditionEvaluationError("Tags are required for tag condition")

        contact_tags = context.tags
        required_tags = set(config.tags)
        operator = config.operator or TagOperator.HAS_ANY_TAG

        if operator == TagOperator.HAS_ANY_TAG:
            match = bool(contact_tags & required_tags)
        elif operator == TagOperator.HAS_ALL_TAGS:
            match = required_tags.issubset(contact_tags)
        elif operator == TagOperator.HAS_NO_TAGS:
            match = not bool(contact_tags & required_tags)
        elif operator == TagOperator.HAS_ONLY_TAGS:
            match = contact_tags == required_tags
        else:
            match = False

        return EvaluationResult(
            match=match,
            details={
                "operator": operator,
                "required_tags": list(required_tags),
                "contact_tags": list(contact_tags),
                "match_count": len(contact_tags & required_tags),
            },
        )


class PipelineStageConditionEvaluator(BaseConditionEvaluator):
    """Evaluator for pipeline stage conditions.

    Evaluates conditions based on contact's pipeline stage position.
    """

    def evaluate(
        self,
        config: ConditionConfig,
        context: EvaluationContext,
    ) -> EvaluationResult:
        """Evaluate pipeline stage condition.

        Args:
            config: Condition configuration.
            context: Evaluation context.

        Returns:
            Evaluation result.
        """
        if not config.stages:
            raise ConditionEvaluationError("Stages are required for pipeline stage condition")

        operator = config.operator or "is_in_stage"
        match = False
        matched_stage = None

        for pipeline_id, stage_id in context.pipeline_stages.items():
            if stage_id in config.stages:
                if operator in ("is_in_stage", "is_not_in_stage"):
                    match = True
                    matched_stage = stage_id
                    break
                # Simplified before/after check (would need stage ordering in real impl)
                elif operator == "is_before_stage":
                    match = stage_id < config.stages[0]
                    matched_stage = stage_id
                    break
                elif operator == "is_after_stage":
                    match = stage_id > config.stages[-1]
                    matched_stage = stage_id
                    break

        if operator == "is_not_in_stage":
            match = not match

        return EvaluationResult(
            match=match,
            details={
                "operator": operator,
                "required_stages": config.stages,
                "matched_stage": matched_stage,
                "pipeline_stages": context.pipeline_stages,
            },
        )


class CustomFieldConditionEvaluator(BaseConditionEvaluator):
    """Evaluator for custom field conditions.

    Evaluates conditions based on custom field values with
    type-appropriate operators.
    """

    def evaluate(
        self,
        config: ConditionConfig,
        context: EvaluationContext,
    ) -> EvaluationResult:
        """Evaluate custom field condition.

        Args:
            config: Condition configuration.
            context: Evaluation context.

        Returns:
            Evaluation result.
        """
        if not config.field:
            raise ConditionEvaluationError("Field name is required for custom field condition")

        # Get custom field value
        if config.field not in context.custom_fields:
            return EvaluationResult(
                match=False,
                details={"field": config.field, "error": "field_not_found"},
            )

        actual_value = context.custom_fields[config.field]

        # Type-specific evaluation based on field type
        if config.custom_field_type:
            return self._evaluate_typed_field(config, actual_value)
        else:
            return self._evaluate_generic_field(config, actual_value)

    def _evaluate_typed_field(
        self,
        config: ConditionConfig,
        actual_value: Any,
    ) -> EvaluationResult:
        """Evaluate with type-specific logic.

        Args:
            config: Condition configuration.
            actual_value: Actual field value.

        Returns:
            Evaluation result.
        """
        from src.workflows.domain.condition_value_objects import CustomFieldType

        field_type = config.custom_field_type
        operator = config.operator or FieldOperator.EQUALS

        if field_type == CustomFieldType.DATE:
            # Date comparisons
            if isinstance(actual_value, str):
                try:
                    actual_date = datetime.fromisoformat(actual_value.replace("Z", "+00:00"))
                except ValueError:
                    return EvaluationResult(
                        match=False,
                        details={"error": "invalid_date_format"},
                    )
            else:
                actual_date = actual_value

            if isinstance(config.value, str):
                try:
                    expected_date = datetime.fromisoformat(
                        config.value.replace("Z", "+00:00")
                    )
                except ValueError:
                    return EvaluationResult(
                        match=False,
                        details={"error": "invalid_expected_date"},
                    )
            else:
                expected_date = config.value

            if operator == "equals":
                match = actual_date.date() == expected_date.date()
            elif operator == "before":
                match = actual_date < expected_date
            elif operator == "after":
                match = actual_date > expected_date
            else:
                match = actual_date == expected_date

        elif field_type == CustomFieldType.CHECKBOX:
            # Boolean comparison
            match = bool(actual_value) == (config.value in (True, "true", "1"))

        elif field_type == CustomFieldType.NUMBER:
            # Numeric comparison
            try:
                actual_num = float(actual_value)
                expected_num = float(config.value)
                match = self._compare_values(operator, actual_num, expected_num)
            except (ValueError, TypeError):
                match = False

        else:
            # Default string comparison
            match = self._compare_values(operator, str(actual_value), str(config.value))

        return EvaluationResult(
            match=match,
            details={
                "field_type": field_type.value,
                "operator": operator,
                "actual_value": str(actual_value),
                "expected_value": str(config.value),
            },
        )

    def _evaluate_generic_field(
        self,
        config: ConditionConfig,
        actual_value: Any,
    ) -> EvaluationResult:
        """Evaluate without type information.

        Args:
            config: Condition configuration.
            actual_value: Actual field value.

        Returns:
            Evaluation result.
        """
        match = self._compare_values(
            config.operator or FieldOperator.EQUALS,
            actual_value,
            config.value,
        )

        return EvaluationResult(
            match=match,
            details={
                "operator": config.operator,
                "actual_value": str(actual_value),
                "expected_value": str(config.value),
            },
        )


class EmailEngagementConditionEvaluator(BaseConditionEvaluator):
    """Evaluator for email engagement conditions.

    Evaluates conditions based on email opens and link clicks.
    """

    def evaluate(
        self,
        config: ConditionConfig,
        context: EvaluationContext,
    ) -> EvaluationResult:
        """Evaluate email engagement condition.

        Args:
            config: Condition configuration.
            context: Evaluation context.

        Returns:
            Evaluation result.
        """
        # Check if contact opened email
        if config.condition_type == ConditionType.EMAIL_WAS_OPENED:
            email_id = str(config.value) if config.value else None
            if not email_id:
                raise ConditionEvaluationError("Email ID is required for email open condition")

            opened_emails = context.email_engagement.get("opened_emails", [])
            match = email_id in opened_emails

            return EvaluationResult(
                match=match,
                details={
                    "email_id": email_id,
                    "opened_emails": opened_emails,
                },
            )

        # Check if contact clicked link
        elif config.condition_type == ConditionType.LINK_WAS_CLICKED:
            link_url = str(config.value) if config.value else None
            if not link_url:
                raise ConditionEvaluationError("Link URL is required for link click condition")

            clicked_links = context.email_engagement.get("clicked_links", [])
            match = any(link_url in clicked for clicked in clicked_links)

            return EvaluationResult(
                match=match,
                details={
                    "link_url": link_url,
                    "clicked_links": clicked_links,
                },
            )

        return EvaluationResult(match=False)


class TimeBasedConditionEvaluator(BaseConditionEvaluator):
    """Evaluator for time-based conditions.

    Evaluates conditions based on current time or contact-specific dates.
    """

    def evaluate(
        self,
        config: ConditionConfig,
        context: EvaluationContext,
    ) -> EvaluationResult:
        """Evaluate time-based condition.

        Args:
            config: Condition configuration.
            context: Evaluation context.

        Returns:
            Evaluation result.
        """
        from src.workflows.domain.condition_value_objects import TimeConditionType

        if not config.time_condition:
            raise ConditionEvaluationError("Time condition type is required")

        time_condition = config.time_condition
        now = datetime.now()

        if time_condition == TimeConditionType.CURRENT_DAY_OF_WEEK:
            # Day of week check
            target_day = config.value  # Monday, Tuesday, etc.
            actual_day = now.strftime("%A")
            match = actual_day == target_day

            return EvaluationResult(
                match=match,
                details={
                    "condition": "day_of_week",
                    "expected_day": target_day,
                    "actual_day": actual_day,
                },
            )

        elif time_condition == TimeConditionType.CONTACT_DATE_FIELD:
            # Compare contact's date field
            if not config.field:
                raise ConditionEvaluationError("Field name is required for contact date condition")

            if config.field not in context.custom_fields:
                return EvaluationResult(
                    match=False,
                    details={"error": "date_field_not_found"},
                )

            contact_date_str = context.custom_fields[config.field]
            try:
                contact_date = datetime.fromisoformat(str(contact_date_str).replace("Z", "+00:00"))
            except ValueError:
                return EvaluationResult(
                    match=False,
                    details={"error": "invalid_contact_date"},
                )

            # Days since/before/after logic
            days = config.days or 0
            target_date = now - timedelta(days=days)

            if config.operator == "days_since":
                match = contact_date <= target_date
            else:
                match = contact_date.date() == target_date.date()

            return EvaluationResult(
                match=match,
                details={
                    "condition": "contact_date",
                    "field": config.field,
                    "operator": config.operator,
                    "days": days,
                    "contact_date": contact_date.isoformat(),
                    "target_date": target_date.isoformat(),
                },
            )

        # Default: no match
        return EvaluationResult(
            match=False,
            details={"condition": time_condition.value, "error": "not_implemented"},
        )


class ConditionEvaluatorFactory:
    """Factory for creating condition evaluators.

    This factory creates the appropriate evaluator based on the
    condition type.
    """

    _evaluators: dict[ConditionType, type[BaseConditionEvaluator]] = {
        ConditionType.CONTACT_FIELD_EQUALS: FieldConditionEvaluator,
        ConditionType.CONTACT_HAS_TAG: TagConditionEvaluator,
        ConditionType.PIPELINE_STAGE_IS: PipelineStageConditionEvaluator,
        ConditionType.CUSTOM_FIELD_VALUE: CustomFieldConditionEvaluator,
        ConditionType.EMAIL_WAS_OPENED: EmailEngagementConditionEvaluator,
        ConditionType.LINK_WAS_CLICKED: EmailEngagementConditionEvaluator,
        ConditionType.TIME_BASED: TimeBasedConditionEvaluator,
    }

    @classmethod
    def create(cls, condition_type: ConditionType | str) -> BaseConditionEvaluator:
        """Create evaluator for condition type.

        Args:
            condition_type: Type of condition.

        Returns:
            Evaluator instance.

        Raises:
            ConditionEvaluationError: If condition type not supported.
        """
        if isinstance(condition_type, str):
            try:
                condition_type = ConditionType(condition_type)
            except ValueError as e:
                raise ConditionEvaluationError(
                    f"Unknown condition type: {condition_type}"
                ) from e

        evaluator_class = cls._evaluators.get(condition_type)
        if not evaluator_class:
            raise ConditionEvaluationError(
                f"No evaluator registered for condition type: {condition_type.value}"
            )

        return evaluator_class()

    @classmethod
    def register_evaluator(
        cls,
        condition_type: ConditionType,
        evaluator_class: type[BaseConditionEvaluator],
    ) -> None:
        """Register a custom evaluator.

        Args:
            condition_type: Condition type.
            evaluator_class: Evaluator class.
        """
        cls._evaluators[condition_type] = evaluator_class
