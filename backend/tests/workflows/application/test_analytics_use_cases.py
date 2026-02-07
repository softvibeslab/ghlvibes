"""Tests for analytics application layer use cases.

Tests validate the application use cases for analytics queries,
funnel analysis, action performance, and export generation.
"""

from datetime import UTC, datetime
from datetime import date as Date
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest

from src.workflows.application.analytics_dtos import (
    ActionPerformanceDTO,
    ActionPerformanceQueryDTO,
    ActionPerformanceResponseDTO,
    AnalyticsQueryDTO,
    AnalyticsResponseDTO,
    CompletionMetricsDTO,
    ConversionMetricsDTO,
    EnrollmentMetricsDTO,
    ExportFormat,
    ExportRequestDTO,
    ExportResponseDTO,
    FunnelAnalyticsDTO,
    FunnelQueryDTO,
    FunnelStepDTO,
    Granularity,
    TrendDataPointDTO,
)
from src.workflows.application.use_cases.get_action_performance import (
    GetActionPerformanceUseCase,
)
from src.workflows.application.use_cases.get_funnel_analytics import (
    GetFunnelAnalyticsUseCase,
)
from src.workflows.application.use_cases.get_workflow_analytics import (
    GetWorkflowAnalyticsUseCase,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def sample_workflow_id() -> UUID:
    """Sample workflow ID."""
    return uuid4()


@pytest.fixture
def sample_date() -> Date:
    """Sample date."""
    return Date(2026, 1, 15)


@pytest.fixture
def sample_analytics_data():
    """Sample analytics data for testing."""
    return {
        "summary": {
            "total_enrolled": 1000,
            "currently_active": 400,
            "new_enrollments": 100,
            "enrollment_rate": 14.29,
            "enrollment_sources": {
                "trigger": 60,
                "bulk": 30,
                "api": 10,
            },
            "completed": 500,
            "completion_rate": 50.0,
            "average_duration_hours": 72.5,
            "exit_reasons": {
                "completed": 500,
            },
            "goals_achieved": 250,
            "conversion_rate": 25.0,
        },
        "trends": [
            {
                "date": "2026-01-01",
                "new_enrollments": 10,
                "completions": 5,
                "conversions": 2,
            },
            {
                "date": "2026-01-02",
                "new_enrollments": 15,
                "completions": 8,
                "conversions": 4,
            },
        ],
    }


@pytest.fixture
def sample_funnel_data():
    """Sample funnel data for testing."""
    return {
        "workflow_id": str(uuid4()),
        "total_enrolled": 1000,
        "final_converted": 500,
        "overall_conversion_rate": 50.0,
        "bottleneck_step_id": str(uuid4()),
        "steps": [
            {
                "step_id": str(uuid4()),
                "step_name": "Send Welcome Email",
                "step_order": 1,
                "entered": 1000,
                "completed": 950,
                "dropped_off": 50,
                "conversion_rate": 95.0,
                "drop_off_rate": 5.0,
                "is_bottleneck": False,
            },
            {
                "step_id": str(uuid4()),
                "step_name": "Wait 1 Day",
                "step_order": 2,
                "entered": 950,
                "completed": 500,
                "dropped_off": 450,
                "conversion_rate": 52.63,
                "drop_off_rate": 47.37,
                "is_bottleneck": True,
            },
        ],
    }


# =============================================================================
# GetWorkflowAnalyticsUseCase Tests
# =============================================================================


class TestGetWorkflowAnalyticsUseCase:
    """Test workflow analytics use case."""

    @pytest.mark.asyncio
    async def test_execute_returns_analytics_response(
        self,
        sample_workflow_id,
        sample_date,
        sample_analytics_data,
    ):
        """WHEN executing analytics query
        THEN returns complete analytics response.
        """
        # Given use case with mocked repository
        mock_repo = AsyncMock()
        mock_repo.get_workflow_analytics.return_value = sample_analytics_data

        use_case = GetWorkflowAnalyticsUseCase(
            analytics_repository=mock_repo,
            cache_service=None,
        )

        query = AnalyticsQueryDTO(
            workflow_id=sample_workflow_id,
            start_date=Date(2026, 1, 1),
            end_date=Date(2026, 1, 31),
            granularity=Granularity.DAILY,
        )

        # When executing query
        response = await use_case.execute(query)

        # Then response should be properly formatted
        assert isinstance(response, AnalyticsResponseDTO)
        assert response.workflow_id == sample_workflow_id
        assert isinstance(response.enrollment, EnrollmentMetricsDTO)
        assert isinstance(response.completion, CompletionMetricsDTO)
        assert isinstance(response.conversion, ConversionMetricsDTO)
        assert len(response.trends) == 2

    @pytest.mark.asyncio
    async def test_invalid_date_range_raises_error(
        self,
        sample_workflow_id,
    ):
        """WHEN start_date > end_date
        THEN raises ValueError.
        """
        mock_repo = AsyncMock()
        use_case = GetWorkflowAnalyticsUseCase(
            analytics_repository=mock_repo,
            cache_service=None,
        )

        query = AnalyticsQueryDTO(
            workflow_id=sample_workflow_id,
            start_date=Date(2026, 1, 31),
            end_date=Date(2026, 1, 1),
            granularity=Granularity.DAILY,
        )

        with pytest.raises(ValueError):
            await use_case.execute(query)


# =============================================================================
# GetFunnelAnalyticsUseCase Tests
# =============================================================================


class TestGetFunnelAnalyticsUseCase:
    """Test funnel analytics use case."""

    @pytest.mark.asyncio
    async def test_execute_returns_funnel_response(
        self,
        sample_workflow_id,
        sample_funnel_data,
    ):
        """WHEN executing funnel query
        THEN returns complete funnel analysis response.
        """
        # Given use case with mocked repository
        mock_repo = AsyncMock()
        mock_repo.get_funnel_metrics.return_value = sample_funnel_data

        use_case = GetFunnelAnalyticsUseCase(
            funnel_repository=mock_repo,
            cache_service=None,
        )

        query = FunnelQueryDTO(
            workflow_id=sample_workflow_id,
            start_date=Date(2026, 1, 1),
            end_date=Date(2026, 1, 31),
            include_step_details=True,
        )

        # When executing query
        response = await use_case.execute(query)

        # Then response should be properly formatted
        assert isinstance(response, FunnelAnalyticsDTO)
        assert response.workflow_id == sample_workflow_id
        assert response.total_enrolled == 1000
        assert response.final_converted == 500
        assert response.overall_conversion_rate == 50.0
        assert len(response.steps) == 2

        # Check funnel steps
        step = response.steps[0]
        assert isinstance(step, FunnelStepDTO)
        assert step.step_name == "Send Welcome Email"
        assert step.entered == 1000
        assert step.completed == 950
        assert step.is_bottleneck is False


# =============================================================================
# GetActionPerformanceUseCase Tests
# =============================================================================


class TestGetActionPerformanceUseCase:
    """Test action performance use case."""

    @pytest.mark.asyncio
    async def test_execute_returns_action_performance(
        self,
        sample_workflow_id,
    ):
        """WHEN executing action performance query
        THEN returns action metrics response.
        """
        # Given use case with mocked repository
        mock_repo = AsyncMock()
        mock_repo.get_action_metrics.return_value = {
            "workflow_id": str(sample_workflow_id),
            "actions": [
                {
                    "action_id": str(uuid4()),
                    "action_type": "send_email",
                    "action_name": "Welcome Email",
                    "executions": 100,
                    "successes": 95,
                    "failures": 5,
                    "success_rate": 95.0,
                    "average_duration_ms": 250,
                }
            ],
        }

        use_case = GetActionPerformanceUseCase(
            action_repository=mock_repo,
            cache_service=None,
        )

        query = ActionPerformanceQueryDTO(
            workflow_id=sample_workflow_id,
            start_date=Date(2026, 1, 1),
            end_date=Date(2026, 1, 31),
            action_types=["send_email"],
        )

        # When executing query
        response = await use_case.execute(query)

        # Then response should be properly formatted
        assert isinstance(response, ActionPerformanceResponseDTO)
        assert response.workflow_id == sample_workflow_id
        assert len(response.actions) == 1

        action = response.actions[0]
        assert isinstance(action, ActionPerformanceDTO)
        assert action.action_type == "send_email"
        assert action.executions == 100
        assert action.success_rate == 95.0


# =============================================================================
# DTO Validation Tests
# =============================================================================


class TestAnalyticsDTOs:
    """Test analytics DTOs."""

    def test_analytics_query_dto_validation(
        self,
        sample_workflow_id,
    ):
        """WHEN creating AnalyticsQueryDTO
        THEN validates required fields.
        """
        query = AnalyticsQueryDTO(
            workflow_id=sample_workflow_id,
            start_date=Date(2026, 1, 1),
            end_date=Date(2026, 1, 31),
            granularity=Granularity.DAILY,
        )

        assert query.workflow_id == sample_workflow_id
        assert query.granularity == Granularity.DAILY

    def test_export_request_dto_validation(
        self,
        sample_workflow_id,
    ):
        """WHEN creating ExportRequestDTO
        THEN validates export format.
        """
        request = ExportRequestDTO(
            workflow_id=sample_workflow_id,
            start_date=Date(2026, 1, 1),
            end_date=Date(2026, 1, 31),
            format=ExportFormat.CSV,
            include_charts=False,
        )

        assert request.format == ExportFormat.CSV
        assert request.include_charts is False

    def test_funnel_step_dto_serialization(self):
        """WHEN serializing FunnelStepDTO
        THEN produces correct JSON structure.
        """
        step = FunnelStepDTO(
            step_id=uuid4(),
            step_name="Test Step",
            step_order=1,
            entered=100,
            completed=85,
            dropped_off=15,
            conversion_rate=85.0,
            drop_off_rate=15.0,
            is_bottleneck=False,
        )

        # Should serialize without errors
        data = step.model_dump()
        assert data["step_name"] == "Test Step"
        assert data["conversion_rate"] == 85.0
