"""Use case: Get workflow analytics.

This use case retrieves and aggregates workflow analytics data
including enrollment, completion, and conversion metrics.
"""

from datetime import UTC, datetime
from datetime import date as Date
from typing import Any
from uuid import UUID

from src.workflows.application.analytics_dtos import (
    ActionPerformanceDTO,
    AnalyticsQueryDTO,
    AnalyticsResponseDTO,
    CompletionMetricsDTO,
    ConversionMetricsDTO,
    EnrollmentMetricsDTO,
    TrendDataPointDTO,
)


class GetWorkflowAnalyticsUseCase:
    """Use case for retrieving workflow analytics.

    Orchestrates the retrieval and aggregation of workflow metrics
    from various data sources.
    """

    def __init__(
        self,
        analytics_repository: Any,  # Will be AnalyticsRepository
        cache_service: Any | None = None,  # Will be AnalyticsCacheService
    ):
        """Initialize use case.

        Args:
            analytics_repository: Repository for analytics data access.
            cache_service: Optional cache service for performance.
        """
        self.analytics_repository = analytics_repository
        self.cache_service = cache_service

    async def execute(self, query: AnalyticsQueryDTO) -> AnalyticsResponseDTO:
        """Execute analytics query.

        Args:
            query: Analytics query parameters.

        Returns:
            AnalyticsResponseDTO with complete analytics data.

        Raises:
            WorkflowNotFoundError: If workflow doesn't exist.
            InvalidDateRangeError: If date range is invalid.
        """
        # Validate date range
        if query.start_date > query.end_date:
            raise ValueError("start_date must be before or equal to end_date")

        # Check cache if available
        cache_key = self._build_cache_key(query)
        if self.cache_service:
            cached = await self.cache_service.get(cache_key)
            if cached:
                return AnalyticsResponseDTO(**cached)

        # Fetch analytics data
        analytics_data = await self.analytics_repository.get_workflow_analytics(
            workflow_id=query.workflow_id,
            start_date=query.start_date,
            end_date=query.end_date,
            granularity=query.granularity,
        )

        # Build response
        response = self._build_response(query, analytics_data)

        # Cache response
        if self.cache_service:
            await self.cache_service.set(
                cache_key,
                response.model_dump(),
                ttl=300,  # 5 minutes
            )

        return response

    def _build_cache_key(self, query: AnalyticsQueryDTO) -> str:
        """Build cache key from query parameters."""
        return (
            f"analytics:{query.workflow_id}:"
            f"{query.start_date}:{query.end_date}:{query.granularity}"
        )

    def _build_response(
        self,
        query: AnalyticsQueryDTO,
        data: dict[str, Any],
    ) -> AnalyticsResponseDTO:
        """Build analytics response from raw data.

        Args:
            query: Original query parameters.
            data: Raw analytics data from repository.

        Returns:
            Formatted AnalyticsResponseDTO.
        """
        # Extract summary data
        summary = data.get("summary", {})

        # Build enrollment metrics
        enrollment_dto = EnrollmentMetricsDTO(
            total_enrolled=summary.get("total_enrolled", 0),
            currently_active=summary.get("currently_active", 0),
            new_enrollments=summary.get("new_enrollments", 0),
            enrollment_rate=summary.get("enrollment_rate", 0.0),
            enrollment_sources=summary.get("enrollment_sources", {}),
        )

        # Build completion metrics
        completion_dto = CompletionMetricsDTO(
            completed=summary.get("completed", 0),
            completion_rate=summary.get("completion_rate", 0.0),
            average_duration_hours=summary.get("average_duration_hours"),
            exit_reasons=summary.get("exit_reasons", {}),
        )

        # Build conversion metrics
        conversion_dto = ConversionMetricsDTO(
            goals_achieved=summary.get("goals_achieved", 0),
            conversion_rate=summary.get("conversion_rate", 0.0),
            average_time_to_conversion_hours=summary.get(
                "average_time_to_conversion_hours"
            ),
            median_time_to_conversion_hours=summary.get(
                "median_time_to_conversion_hours"
            ),
        )

        # Build trend data
        trend_data = data.get("trends", [])
        trends_dto = [
            TrendDataPointDTO(
                date=t["date"],
                new_enrollments=t.get("new_enrollments", 0),
                completions=t.get("completions", 0),
                conversions=t.get("conversions", 0),
            )
            for t in trend_data
        ]

        return AnalyticsResponseDTO(
            workflow_id=query.workflow_id,
            period={
                "start_date": query.start_date.isoformat(),
                "end_date": query.end_date.isoformat(),
                "granularity": query.granularity,
            },
            summary=summary,
            enrollment=enrollment_dto,
            completion=completion_dto,
            conversion=conversion_dto,
            trends=trends_dto,
            generated_at=datetime.now(UTC),
        )
