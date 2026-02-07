"""Unit tests for condition evaluators.

These tests verify the condition evaluation strategies work correctly.
"""

from datetime import datetime, timedelta

import pytest

from src.workflows.domain.condition_evaluators import (
    ConditionEvaluatorFactory,
    CustomFieldConditionEvaluator,
    EmailEngagementConditionEvaluator,
    EvaluationContext,
    EvaluationResult,
    FieldConditionEvaluator,
    PipelineStageConditionEvaluator,
    TagConditionEvaluator,
    TimeBasedConditionEvaluator,
)
from src.workflows.domain.condition_exceptions import ConditionEvaluationError
from src.workflows.domain.condition_value_objects import (
    ConditionConfig,
    ConditionType,
    CustomFieldType,
    FieldOperator,
    TagOperator,
    TimeConditionType,
)


class TestEvaluationContext:
    """Test suite for EvaluationContext."""

    def test_create_minimal_context(self) -> None:
        """Test creating minimal context."""
        context = EvaluationContext(
            contact_id="contact-123",
            contact_data={"email": "test@gmail.com"},
        )

        assert context.contact_id == "contact-123"
        assert context.contact_data == {"email": "test@gmail.com"}
        assert context.tags == set()
        assert context.pipeline_stages == {}

    def test_create_full_context(self) -> None:
        """Test creating full context."""
        context = EvaluationContext(
            contact_id="contact-123",
            contact_data={"email": "test@gmail.com"},
            tags=["lead", "prospect"],
            pipeline_stages={"pipeline-1": "stage-1"},
            custom_fields={"age": "25"},
            email_engagement={"opened_emails": ["email-1"]},
            execution_id="exec-123",
        )

        assert context.contact_id == "contact-123"
        assert "lead" in context.tags
        assert context.pipeline_stages["pipeline-1"] == "stage-1"
        assert context.custom_fields["age"] == "25"
        assert "email-1" in context.email_engagement["opened_emails"]


class TestEvaluationResult:
    """Test suite for EvaluationResult."""

    def test_create_result(self) -> None:
        """Test creating evaluation result."""
        result = EvaluationResult(
            match=True,
            branch_name="True",
            branch_id="branch-123",
            details={"field": "email"},
            duration_ms=5,
        )

        assert result.match is True
        assert result.branch_name == "True"
        assert result.branch_id == "branch-123"
        assert result.details["field"] == "email"
        assert result.duration_ms == 5

    def test_result_to_dict(self) -> None:
        """Test converting result to dict."""
        result = EvaluationResult(match=True, branch_name="True")

        data = result.to_dict()

        assert data["match"] is True
        assert data["branch_name"] == "True"


class TestFieldConditionEvaluator:
    """Test suite for FieldConditionEvaluator."""

    @pytest.fixture
    def evaluator(self) -> FieldConditionEvaluator:
        """Fixture for evaluator."""
        return FieldConditionEvaluator()

    @pytest.fixture
    def context(self) -> EvaluationContext:
        """Fixture for evaluation context."""
        return EvaluationContext(
            contact_id="contact-123",
            contact_data={
                "email": "test@gmail.com",
                "age": "25",
                "name": "John Doe",
                "status": "active",
            },
        )

    def test_evaluate_equals_operator(self, evaluator, context) -> None:
        """Test equals operator."""
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_FIELD_EQUALS,
            field="email",
            operator=FieldOperator.EQUALS,
            value="test@gmail.com",
        )

        result = evaluator.evaluate(config, context)

        assert result.match is True
        assert result.details["actual_value"] == "test@gmail.com"

    def test_evaluate_contains_operator(self, evaluator, context) -> None:
        """Test contains operator."""
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_FIELD_EQUALS,
            field="email",
            operator=FieldOperator.CONTAINS,
            value="@gmail.com",
        )

        result = evaluator.evaluate(config, context)

        assert result.match is True

    def test_evaluate_not_contains_operator(self, evaluator, context) -> None:
        """Test not_contains operator."""
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_FIELD_EQUALS,
            field="email",
            operator=FieldOperator.NOT_CONTAINS,
            value="@yahoo.com",
        )

        result = evaluator.evaluate(config, context)

        assert result.match is True

    def test_evaluate_greater_than_operator(self, evaluator, context) -> None:
        """Test greater_than operator."""
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_FIELD_EQUALS,
            field="age",
            operator=FieldOperator.GREATER_THAN,
            value=20,
        )

        result = evaluator.evaluate(config, context)

        assert result.match is True

    def test_evaluate_less_than_operator(self, evaluator, context) -> None:
        """Test less_than operator."""
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_FIELD_EQUALS,
            field="age",
            operator=FieldOperator.LESS_THAN,
            value=30,
        )

        result = evaluator.evaluate(config, context)

        assert result.match is True

    def test_evaluate_is_empty_operator_with_value(self, evaluator, context) -> None:
        """Test is_empty operator with non-empty value."""
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_FIELD_EQUALS,
            field="email",
            operator=FieldOperator.IS_EMPTY,
        )

        result = evaluator.evaluate(config, context)

        assert result.match is False

    def test_evaluate_is_empty_operator_with_null(self, evaluator) -> None:
        """Test is_empty operator with null value."""
        context = EvaluationContext(
            contact_id="contact-123",
            contact_data={"email": None},
        )
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_FIELD_EQUALS,
            field="email",
            operator=FieldOperator.IS_EMPTY,
        )

        result = evaluator.evaluate(config, context)

        assert result.match is True

    def test_evaluate_is_not_empty_operator(self, evaluator, context) -> None:
        """Test is_not_empty operator."""
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_FIELD_EQUALS,
            field="email",
            operator=FieldOperator.IS_NOT_EMPTY,
        )

        result = evaluator.evaluate(config, context)

        assert result.match is True

    def test_evaluate_in_list_operator(self, evaluator, context) -> None:
        """Test in_list operator."""
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_FIELD_EQUALS,
            field="status",
            operator=FieldOperator.IN_LIST,
            value=["active", "pending"],
        )

        result = evaluator.evaluate(config, context)

        assert result.match is True

    def test_evaluate_case_insensitive_string_comparison(self, evaluator, context) -> None:
        """Test case-insensitive string comparison."""
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_FIELD_EQUALS,
            field="email",
            operator=FieldOperator.CONTAINS,
            value="@GMAIL.COM",
        )

        result = evaluator.evaluate(config, context)

        assert result.match is True

    def test_evaluate_missing_field(self, evaluator, context) -> None:
        """Test evaluation with missing field."""
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_FIELD_EQUALS,
            field="missing_field",
            operator=FieldOperator.EQUALS,
            value="test",
        )

        result = evaluator.evaluate(config, context)

        assert result.match is False

    def test_evaluate_without_field_raises_error(self, evaluator, context) -> None:
        """Test evaluation without field raises error."""
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_FIELD_EQUALS,
        )

        with pytest.raises(ConditionEvaluationError, match="Field name is required"):
            evaluator.evaluate(config, context)


class TestTagConditionEvaluator:
    """Test suite for TagConditionEvaluator."""

    @pytest.fixture
    def evaluator(self) -> TagConditionEvaluator:
        """Fixture for evaluator."""
        return TagConditionEvaluator()

    @pytest.fixture
    def context(self) -> EvaluationContext:
        """Fixture for evaluation context."""
        return EvaluationContext(
            contact_id="contact-123",
            contact_data={},
            tags=["lead", "prospect", "customer"],
        )

    def test_evaluate_has_any_tag(self, evaluator, context) -> None:
        """Test has_any_tag operator."""
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_HAS_TAG,
            operator=TagOperator.HAS_ANY_TAG,
            tags=["lead", "vip"],
        )

        result = evaluator.evaluate(config, context)

        assert result.match is True
        assert result.details["match_count"] == 1

    def test_evaluate_has_all_tags(self, evaluator, context) -> None:
        """Test has_all_tags operator."""
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_HAS_TAG,
            operator=TagOperator.HAS_ALL_TAGS,
            tags=["lead", "prospect"],
        )

        result = evaluator.evaluate(config, context)

        assert result.match is True

    def test_evaluate_has_no_tags(self, evaluator, context) -> None:
        """Test has_no_tags operator."""
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_HAS_TAG,
            operator=TagOperator.HAS_NO_TAGS,
            tags=["vip", "premium"],
        )

        result = evaluator.evaluate(config, context)

        assert result.match is True

    def test_evaluate_has_only_tags(self, evaluator) -> None:
        """Test has_only_tags operator."""
        context = EvaluationContext(
            contact_id="contact-123",
            contact_data={},
            tags=["lead", "prospect"],
        )
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_HAS_TAG,
            operator=TagOperator.HAS_ONLY_TAGS,
            tags=["lead", "prospect"],
        )

        result = evaluator.evaluate(config, context)

        assert result.match is True

    def test_evaluate_without_tags_raises_error(self, evaluator, context) -> None:
        """Test evaluation without tags raises error."""
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_HAS_TAG,
        )

        with pytest.raises(ConditionEvaluationError, match="Tags are required"):
            evaluator.evaluate(config, context)


class TestPipelineStageConditionEvaluator:
    """Test suite for PipelineStageConditionEvaluator."""

    @pytest.fixture
    def evaluator(self) -> PipelineStageConditionEvaluator:
        """Fixture for evaluator."""
        return PipelineStageConditionEvaluator()

    @pytest.fixture
    def context(self) -> EvaluationContext:
        """Fixture for evaluation context."""
        return EvaluationContext(
            contact_id="contact-123",
            contact_data={},
            pipeline_stages={"pipeline-1": "stage-2", "pipeline-2": "stage-1"},
        )

    def test_evaluate_is_in_stage(self, evaluator, context) -> None:
        """Test is_in_stage operator."""
        config = ConditionConfig(
            condition_type=ConditionType.PIPELINE_STAGE_IS,
            operator="is_in_stage",
            stages=["stage-1", "stage-2"],
        )

        result = evaluator.evaluate(config, context)

        assert result.match is True

    def test_evaluate_is_not_in_stage(self, evaluator, context) -> None:
        """Test is_not_in_stage operator."""
        config = ConditionConfig(
            condition_type=ConditionType.PIPELINE_STAGE_IS,
            operator="is_not_in_stage",
            stages=["stage-3"],
        )

        result = evaluator.evaluate(config, context)

        assert result.match is True

    def test_evaluate_without_stages_raises_error(self, evaluator, context) -> None:
        """Test evaluation without stages raises error."""
        config = ConditionConfig(
            condition_type=ConditionType.PIPELINE_STAGE_IS,
        )

        with pytest.raises(ConditionEvaluationError, match="Stages are required"):
            evaluator.evaluate(config, context)


class TestCustomFieldConditionEvaluator:
    """Test suite for CustomFieldConditionEvaluator."""

    @pytest.fixture
    def evaluator(self) -> CustomFieldConditionEvaluator:
        """Fixture for evaluator."""
        return CustomFieldConditionEvaluator()

    @pytest.fixture
    def context(self) -> EvaluationContext:
        """Fixture for evaluation context."""
        return EvaluationContext(
            contact_id="contact-123",
            contact_data={},
            custom_fields={"age": "25", "name": "John", "is_vip": "true"},
        )

    def test_evaluate_text_field(self, evaluator, context) -> None:
        """Test text field evaluation."""
        config = ConditionConfig(
            condition_type=ConditionType.CUSTOM_FIELD_VALUE,
            field="name",
            operator=FieldOperator.EQUALS,
            value="John",
            custom_field_type=CustomFieldType.TEXT,
        )

        result = evaluator.evaluate(config, context)

        assert result.match is True

    def test_evaluate_number_field(self, evaluator, context) -> None:
        """Test number field evaluation."""
        config = ConditionConfig(
            condition_type=ConditionType.CUSTOM_FIELD_VALUE,
            field="age",
            operator=FieldOperator.GREATER_THAN,
            value=20,
            custom_field_type=CustomFieldType.NUMBER,
        )

        result = evaluator.evaluate(config, context)

        assert result.match is True

    def test_evaluate_checkbox_field_true(self, evaluator, context) -> None:
        """Test checkbox field evaluation with true."""
        config = ConditionConfig(
            condition_type=ConditionType.CUSTOM_FIELD_VALUE,
            field="is_vip",
            operator="is_true",
            value=True,
            custom_field_type=CustomFieldType.CHECKBOX,
        )

        result = evaluator.evaluate(config, context)

        assert result.match is True

    def test_evaluate_date_field(self, evaluator, context) -> None:
        """Test date field evaluation."""
        date_str = "2020-01-15T00:00:00"
        context.custom_fields["signup_date"] = date_str

        config = ConditionConfig(
            condition_type=ConditionType.CUSTOM_FIELD_VALUE,
            field="signup_date",
            operator="before",
            value="2020-02-01T00:00:00",
            custom_field_type=CustomFieldType.DATE,
        )

        result = evaluator.evaluate(config, context)

        assert result.match is True

    def test_evaluate_missing_field(self, evaluator, context) -> None:
        """Test evaluation with missing field."""
        config = ConditionConfig(
            condition_type=ConditionType.CUSTOM_FIELD_VALUE,
            field="missing_field",
            operator=FieldOperator.EQUALS,
            value="test",
        )

        result = evaluator.evaluate(config, context)

        assert result.match is False


class TestEmailEngagementConditionEvaluator:
    """Test suite for EmailEngagementConditionEvaluator."""

    @pytest.fixture
    def evaluator(self) -> EmailEngagementConditionEvaluator:
        """Fixture for evaluator."""
        return EmailEngagementConditionEvaluator()

    @pytest.fixture
    def context(self) -> EvaluationContext:
        """Fixture for evaluation context."""
        return EvaluationContext(
            contact_id="contact-123",
            contact_data={},
            email_engagement={
                "opened_emails": ["email-1", "email-2"],
                "clicked_links": ["https://example.com", "https://test.com"],
            },
        )

    def test_evaluate_email_opened(self, evaluator, context) -> None:
        """Test email was opened condition."""
        config = ConditionConfig(
            condition_type=ConditionType.EMAIL_WAS_OPENED,
            value="email-1",
        )

        result = evaluator.evaluate(config, context)

        assert result.match is True

    def test_evaluate_email_not_opened(self, evaluator, context) -> None:
        """Test email was not opened."""
        config = ConditionConfig(
            condition_type=ConditionType.EMAIL_WAS_OPENED,
            value="email-999",
        )

        result = evaluator.evaluate(config, context)

        assert result.match is False

    def test_evaluate_link_clicked(self, evaluator, context) -> None:
        """Test link was clicked condition."""
        config = ConditionConfig(
            condition_type=ConditionType.LINK_WAS_CLICKED,
            value="https://example.com",
        )

        result = evaluator.evaluate(config, context)

        assert result.match is True

    def test_evaluate_link_not_clicked(self, evaluator, context) -> None:
        """Test link was not clicked."""
        config = ConditionConfig(
            condition_type=ConditionType.LINK_WAS_CLICKED,
            value="https://notclicked.com",
        )

        result = evaluator.evaluate(config, context)

        assert result.match is False

    def test_evaluate_without_email_id_raises_error(self, evaluator, context) -> None:
        """Test evaluation without email ID raises error."""
        config = ConditionConfig(
            condition_type=ConditionType.EMAIL_WAS_OPENED,
        )

        with pytest.raises(ConditionEvaluationError, match="Email ID is required"):
            evaluator.evaluate(config, context)


class TestTimeBasedConditionEvaluator:
    """Test suite for TimeBasedConditionEvaluator."""

    @pytest.fixture
    def evaluator(self) -> TimeBasedConditionEvaluator:
        """Fixture for evaluator."""
        return TimeBasedConditionEvaluator()

    @pytest.fixture
    def context(self) -> EvaluationContext:
        """Fixture for evaluation context."""
        return EvaluationContext(
            contact_id="contact-123",
            contact_data={},
            custom_fields={"birthday": "1990-01-15T00:00:00"},
        )

    def test_evaluate_day_of_week_match(self, evaluator, context) -> None:
        """Test day of week condition matches."""
        today = datetime.now().strftime("%A")
        config = ConditionConfig(
            condition_type=ConditionType.TIME_BASED,
            time_condition=TimeConditionType.CURRENT_DAY_OF_WEEK,
            value=today,
        )

        result = evaluator.evaluate(config, context)

        assert result.match is True

    def test_evaluate_day_of_week_no_match(self, evaluator, context) -> None:
        """Test day of week condition doesn't match."""
        config = ConditionConfig(
            condition_type=ConditionType.TIME_BASED,
            time_condition=TimeConditionType.CURRENT_DAY_OF_WEEK,
            value="NotADay",
        )

        result = evaluator.evaluate(config, context)

        assert result.match is False

    def test_evaluate_contact_date_field_days_since(self, evaluator, context) -> None:
        """Test contact date field with days since."""
        old_date = (datetime.now() - timedelta(days=10)).isoformat()
        context.custom_fields["last_purchase"] = old_date

        config = ConditionConfig(
            condition_type=ConditionType.TIME_BASED,
            time_condition=TimeConditionType.CONTACT_DATE_FIELD,
            field="last_purchase",
            operator="days_since",
            days=7,
        )

        result = evaluator.evaluate(config, context)

        assert result.match is True

    def test_evaluate_without_time_condition_raises_error(self, evaluator, context) -> None:
        """Test evaluation without time condition raises error."""
        config = ConditionConfig(
            condition_type=ConditionType.TIME_BASED,
        )

        with pytest.raises(ConditionEvaluationError, match="Time condition type is required"):
            evaluator.evaluate(config, context)


class TestConditionEvaluatorFactory:
    """Test suite for ConditionEvaluatorFactory."""

    def test_create_field_evaluator(self) -> None:
        """Test creating field condition evaluator."""
        evaluator = ConditionEvaluatorFactory.create(ConditionType.CONTACT_FIELD_EQUALS)

        assert isinstance(evaluator, FieldConditionEvaluator)

    def test_create_tag_evaluator(self) -> None:
        """Test creating tag condition evaluator."""
        evaluator = ConditionEvaluatorFactory.create(ConditionType.CONTACT_HAS_TAG)

        assert isinstance(evaluator, TagConditionEvaluator)

    def test_create_with_string_type(self) -> None:
        """Test creating evaluator with string type."""
        evaluator = ConditionEvaluatorFactory.create("contact_field_equals")

        assert isinstance(evaluator, FieldConditionEvaluator)

    def test_create_with_invalid_type_raises_error(self) -> None:
        """Test creating evaluator with invalid type raises error."""
        with pytest.raises(ConditionEvaluationError, match="Unknown condition type"):
            ConditionEvaluatorFactory.create("invalid_type")

    def test_register_custom_evaluator(self) -> None:
        """Test registering a custom evaluator."""
        custom_type = ConditionType.CONTACT_FIELD_EQUALS  # Use existing for test

        class CustomEvaluator(FieldConditionEvaluator):
            pass

        ConditionEvaluatorFactory.register_evaluator(custom_type, CustomEvaluator)

        evaluator = ConditionEvaluatorFactory.create(custom_type)

        assert isinstance(evaluator, CustomEvaluator)
