"""Implementation tests for workflow analytics domain.

These tests validate the actual implementation of analytics entities,
value objects, and services against SPEC-WFL-009 requirements.
"""

from datetime import UTC, datetime
from datetime import date as Date
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from src.workflows.domain.analytics_entities import (
    MetricsSnapshot,
    WorkflowAnalytics,
    WorkflowStepMetrics,
)
from src.workflows.domain.analytics_exceptions import (
    InvalidCompletionRateError,
    InvalidConversionRateError,
    InvalidEnrollmentSourceError,
)
from src.workflows.domain.analytics_services import (
    AnalyticsAggregationService,
    ConversionCalculationService,
    FunnelAnalysisService,
    MetricsCalculationService,
    TimeRange,
)
from src.workflows.domain.analytics_value_objects import (
    CompletionRate,
    ConversionRate,
    EnrollmentSource,
    ExitReason,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def sample_workflow_id() -> UUID:
    """Sample workflow ID for testing."""
    return uuid4()


@pytest.fixture
def sample_account_id() -> UUID:
    """Sample account ID for testing."""
    return uuid4()


@pytest.fixture
def sample_date() -> Date:
    """Sample date for testing."""
    return Date(2026, 1, 15)


# =============================================================================
# REQ-WFL-009-02: Enrollment Tracking Tests
# =============================================================================


class TestEnrollmentTracking:
    """Test enrollment tracking behavior (REQ-WFL-009-02)."""

    def test_record_enrollment_increments_metrics(
        self,
        sample_workflow_id,
        sample_account_id,
    ):
        """WHEN a contact is enrolled
        THEN total_enrolled and currently_active increment by 1.
        """
        # Given analytics entity
        analytics = WorkflowAnalytics.create(sample_workflow_id, sample_account_id)

        # When recording enrollment
        analytics.record_enrollment(source="trigger")

        # Then metrics should increment
        assert analytics.total_enrolled == 1
        assert analytics.currently_active == 1

    def test_track_enrollment_sources(
        self,
        sample_workflow_id,
        sample_account_id,
    ):
        """WHEN contacts enroll from different sources
        THEN system tracks enrollment breakdown by source.
        """
        # Given analytics entity
        analytics = WorkflowAnalytics.create(sample_workflow_id, sample_account_id)

        # When recording enrollments from different sources
        analytics.record_enrollment(source="trigger")
        analytics.record_enrollment(source="bulk", count=500)
        analytics.record_enrollment(source="api")

        # Then enrollment sources should be tracked
        assert analytics.enrollment_sources["trigger"] == 1
        assert analytics.enrollment_sources["bulk"] == 500
        assert analytics.enrollment_sources["api"] == 1

    def test_invalid_enrollment_source_raises_error(
        self,
        sample_workflow_id,
        sample_account_id,
    ):
        """WHEN recording enrollment with invalid source
        THEN system raises InvalidEnrollmentSourceError.
        """
        analytics = WorkflowAnalytics.create(sample_workflow_id, sample_account_id)

        with pytest.raises(InvalidEnrollmentSourceError):
            analytics.record_enrollment(source="invalid_source")


# =============================================================================
# REQ-WFL-009-03: Completion Metrics Tests
# =============================================================================


class TestCompletionMetrics:
    """Test completion metrics behavior (REQ-WFL-009-03)."""

    def test_completion_rate_calculation(
        self,
        sample_workflow_id,
        sample_account_id,
    ):
        """GIVEN 1000 enrollments and 600 completions
        THEN completion_rate equals 60.0%.
        """
        analytics = WorkflowAnalytics.create(sample_workflow_id, sample_account_id)

        # Record enrollments and completions
        analytics.total_enrolled = 1000
        analytics.completed = 600

        # When calculating completion rate
        completion_rate = analytics.completion_rate

        # Then rate should be 60%
        assert completion_rate.value == Decimal("60.0")

    def test_completion_rate_zero_division(
        self,
        sample_workflow_id,
        sample_account_id,
    ):
        """GIVEN zero enrollments
        THEN completion_rate equals 0%.
        """
        analytics = WorkflowAnalytics.create(sample_workflow_id, sample_account_id)

        completion_rate = analytics.completion_rate

        assert completion_rate.value == Decimal("0")

    def test_record_completion_decreases_active(
        self,
        sample_workflow_id,
        sample_account_id,
    ):
        """WHEN recording completion
        THEN currently_active decreases.
        """
        analytics = WorkflowAnalytics.create(sample_workflow_id, sample_account_id)
        analytics.record_enrollment(source="trigger")
        analytics.record_enrollment(source="trigger")

        # When recording completion
        analytics.record_completion()

        # Then active count should decrease
        assert analytics.total_enrolled == 2
        assert analytics.completed == 1
        assert analytics.currently_active == 1

    def test_exit_reason_tracking(
        self,
        sample_workflow_id,
        sample_account_id,
    ):
        """WHEN contacts exit for various reasons
        THEN system tracks exit reason distribution.
        """
        analytics = WorkflowAnalytics.create(sample_workflow_id, sample_account_id)
        analytics.record_enrollment(source="bulk", count=1000)

        # Record various exits
        analytics.record_completion(exit_reason=ExitReason.COMPLETED, count=600)
        analytics.record_completion(exit_reason=ExitReason.GOAL_ACHIEVED, count=200)
        analytics.record_exit(exit_reason=ExitReason.MANUAL_REMOVAL, count=100)
        analytics.record_exit(exit_reason=ExitReason.UNSUBSCRIBED, count=50)
        analytics.record_exit(exit_reason=ExitReason.ERROR, count=50)

        # Then exit reasons should be tracked
        assert analytics.exit_reasons["completed"] == 600
        assert analytics.exit_reasons["goal_achieved"] == 200
        assert analytics.exit_reasons["manual_removal"] == 100
        assert analytics.exit_reasons["unsubscribed"] == 50
        assert analytics.exit_reasons["error"] == 50


# =============================================================================
# REQ-WFL-009-04: Conversion Tracking Tests
# =============================================================================


class TestConversionTracking:
    """Test conversion tracking behavior (REQ-WFL-009-04)."""

    def test_conversion_rate_calculation(
        self,
        sample_workflow_id,
        sample_account_id,
    ):
        """GIVEN 1000 enrollments and 250 goals achieved
        THEN conversion_rate equals 25.0%.
        """
        analytics = WorkflowAnalytics.create(sample_workflow_id, sample_account_id)

        # Record enrollments and goals
        analytics.total_enrolled = 1000
        analytics.record_goal_achievement(count=250)

        # When calculating conversion rate
        conversion_rate = analytics.conversion_rate

        # Then rate should be 25%
        assert conversion_rate.value == Decimal("25.0")

    def test_conversion_rate_zero_division(
        self,
        sample_workflow_id,
        sample_account_id,
    ):
        """GIVEN zero enrollments
        THEN conversion_rate equals 0%.
        """
        analytics = WorkflowAnalytics.create(sample_workflow_id, sample_account_id)

        conversion_rate = analytics.conversion_rate

        assert conversion_rate.value == Decimal("0")

    def test_record_goal_achievement(
        self,
        sample_workflow_id,
        sample_account_id,
    ):
        """WHEN goal is achieved
        THEN goals_achieved increments.
        """
        analytics = WorkflowAnalytics.create(sample_workflow_id, sample_account_id)

        analytics.record_goal_achievement()

        assert analytics.goals_achieved == 1


# =============================================================================
# REQ-WFL-009-05: Action Performance Metrics Tests
# =============================================================================


class TestActionPerformanceMetrics:
    """Test action performance metrics (REQ-WFL-009-05)."""

    def test_step_metrics_success_rate_calculation(
        self,
        sample_workflow_id,
        sample_date,
    ):
        """GIVEN step with 100 executions and 95 successes
        THEN success_rate equals 95.0%.
        """
        step_metrics = WorkflowStepMetrics.create(
            workflow_id=sample_workflow_id,
            step_id=uuid4(),
            step_name="Send Email",
            step_order=1,
            metrics_date=sample_date,
            entered=100,
            completed=95,
        )

        # Record action executions
        step_metrics.executions = 100
        step_metrics.successes = 95
        step_metrics.failures = 5

        # Then success rate should be 95%
        assert step_metrics.success_rate == Decimal("95.0")

    def test_step_bottleneck_detection(
        self,
        sample_workflow_id,
        sample_date,
    ):
        """GIVEN step with 40% drop-off rate
        THEN step is identified as bottleneck.
        """
        step_metrics = WorkflowStepMetrics.create(
            workflow_id=sample_workflow_id,
            step_id=uuid4(),
            step_name="Wait Step",
            step_order=2,
            metrics_date=sample_date,
            entered=100,
            completed=60,  # 40% drop-off
        )

        # Then step should be a bottleneck
        assert step_metrics.is_bottleneck(threshold=Decimal("30"))


# =============================================================================
# REQ-WFL-009-06: Drop-off Analysis Tests
# =============================================================================


class TestDropoffAnalysis:
    """Test funnel drop-off analysis (REQ-WFL-009-06)."""

    def test_identify_bottleneck_step(
        self,
        sample_workflow_id,
        sample_date,
    ):
        """GIVEN workflow funnel with varying conversion rates
        THEN system identifies step with highest drop-off.
        """
        # Create step metrics
        step1 = WorkflowStepMetrics.create(
            workflow_id=sample_workflow_id,
            step_id=uuid4(),
            step_name="Step 1",
            step_order=1,
            metrics_date=sample_date,
            entered=1000,
            completed=950,  # 5% drop-off
        )

        step2 = WorkflowStepMetrics.create(
            workflow_id=sample_workflow_id,
            step_id=uuid4(),
            step_name="Step 2",
            step_order=2,
            metrics_date=sample_date,
            entered=950,
            completed=800,  # 16% drop-off
        )

        step3 = WorkflowStepMetrics.create(
            workflow_id=sample_workflow_id,
            step_id=uuid4(),
            step_name="Step 3",
            step_order=3,
            metrics_date=sample_date,
            entered=800,
            completed=400,  # 50% drop-off - BOTTLENECK
        )

        # Analyze funnel
        funnel_service = FunnelAnalysisService(bottleneck_threshold=Decimal("30"))
        funnel_analysis = funnel_service.analyze_funnel(
            step_metrics=[step1, step2, step3],
            total_enrolled=1000,
        )

        # Then step 3 should be identified as bottleneck
        assert funnel_analysis.bottleneck_step_id == step3.step_id

    def test_step_conversion_rates(
        self,
        sample_workflow_id,
        sample_date,
    ):
        """WHEN analyzing funnel
        THEN each step has conversion metrics.
        """
        step = WorkflowStepMetrics.create(
            workflow_id=sample_workflow_id,
            step_id=uuid4(),
            step_name="Test Step",
            step_order=1,
            metrics_date=sample_date,
            entered=100,
            completed=85,
        )

        # Then metrics should be calculated
        assert step.entered == 100
        assert step.completed == 85
        assert step.dropped_off == 15
        assert step.step_conversion_rate == Decimal("85.0")
        assert step.drop_off_rate == Decimal("15.0")


# =============================================================================
# REQ-WFL-009-07: Time-Based Filtering Tests
# =============================================================================


class TestTimeBasedFiltering:
    """Test time-based filtering (REQ-WFL-009-07)."""

    def test_time_range_validation(self):
        """WHEN creating time range with start > end
        THEN system raises ValueError.
        """
        with pytest.raises(ValueError):
            TimeRange(
                start_date=Date(2026, 1, 31),
                end_date=Date(2026, 1, 1),
            )

    def test_preset_date_ranges(self):
        """WHEN using preset date ranges
        THEN system generates correct ranges.
        """
        # Last 7 days
        last_7 = TimeRange.last_7_days()
        assert (last_7.end_date - last_7.start_date).days == 7

        # Last 30 days
        last_30 = TimeRange.last_30_days()
        assert (last_30.end_date - last_30.start_date).days == 30

        # Last 90 days
        last_90 = TimeRange.last_90_days()
        assert (last_90.end_date - last_90.start_date).days == 90


# =============================================================================
# Value Object Validation Tests
# =============================================================================


class TestValueObjects:
    """Test analytics value objects."""

    def test_conversion_rate_validation(self):
        """WHEN creating conversion rate
        THEN system validates range (0-100).
        """
        # Valid rates
        ConversionRate(Decimal("0"))
        ConversionRate(Decimal("100"))
        ConversionRate(Decimal("50.5"))

        # Invalid rates
        with pytest.raises(InvalidConversionRateError):
            ConversionRate(Decimal("-1"))

        with pytest.raises(InvalidConversionRateError):
            ConversionRate(Decimal("101"))

    def test_completion_rate_validation(self):
        """WHEN creating completion rate
        THEN system validates range (0-100).
        """
        # Valid rates
        CompletionRate(Decimal("0"))
        CompletionRate(Decimal("100"))

        # Invalid rates
        with pytest.raises(InvalidCompletionRateError):
            CompletionRate(Decimal("-5"))

    def test_enrollment_source_validation(self):
        """WHEN creating enrollment source
        THEN system validates against allowed values.
        """
        # Valid sources
        EnrollmentSource.from_string("trigger")
        EnrollmentSource.from_string("bulk")
        EnrollmentSource.from_string("api")
        EnrollmentSource.from_string("manual")

        # Invalid source
        with pytest.raises(InvalidEnrollmentSourceError):
            EnrollmentSource.from_string("invalid")


# =============================================================================
# Aggregate Root Tests
# =============================================================================


class TestWorkflowAnalyticsAggregate:
    """Test WorkflowAnalytics aggregate behavior."""

    def test_aggregate_maintains_invariants(
        self,
        sample_workflow_id,
        sample_account_id,
    ):
        """WHEN performing analytics operations
        THEN aggregate maintains invariants.
        """
        analytics = WorkflowAnalytics.create(sample_workflow_id, sample_account_id)

        # Record enrollments and completions
        analytics.record_enrollment(source="trigger", count=100)
        analytics.record_completion(count=60)

        # Then invariants should hold
        assert analytics.total_enrolled >= analytics.completed
        assert analytics.completed >= analytics.goals_achieved
        assert analytics.currently_active >= 0

    def test_create_metrics_snapshot(
        self,
        sample_workflow_id,
        sample_account_id,
        sample_date,
    ):
        """WHEN creating metrics snapshot
        THEN it captures point-in-time state.
        """
        analytics = WorkflowAnalytics.create(sample_workflow_id, sample_account_id)
        analytics.record_enrollment(source="trigger", count=100)

        # Create snapshot
        snapshot = analytics.create_snapshot(snapshot_date=sample_date)

        # Then snapshot should capture state
        assert snapshot.workflow_id == sample_workflow_id
        assert snapshot.date == sample_date
        assert snapshot.total_enrolled == 100
        assert snapshot.snapshot_at is not None
