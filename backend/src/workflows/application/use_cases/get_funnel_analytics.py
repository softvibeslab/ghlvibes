"""Use case: Get funnel analytics.

This use case analyzes workflow funnel performance identifying
drop-off points and bottlenecks.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from src.workflows.application.analytics_dtos import (
    FunnelAnalyticsDTO,
    FunnelQueryDTO,
    FunnelStepDTO,
)


class GetFunnelAnalyticsUseCase:
    """Use case for retrieving funnel analytics.

    Orchestrates funnel analysis to identify conversion drop-offs
    and bottleneck steps.
    """

    def __init__(
        self,
        funnel_repository: Any,  # Will be FunnelMetricsRepository
        cache_service: Any | None = None,  # Will be AnalyticsCacheService
    ):
        """Initialize use case.

        Args:
            funnel_repository: Repository for funnel metrics.
            cache_service: Optional cache service for performance.
        """
        self.funnel_repository = funnel_repository
        self.cache_service = cache_service

    async def execute(self, query: FunnelQueryDTO) -> FunnelAnalyticsDTO:
        """Execute funnel analytics query.

        Args:
            query: Funnel query parameters.

        Returns:
            FunnelAnalyticsDTO with complete funnel analysis.

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
                return FunnelAnalyticsDTO(**cached)

        # Fetch funnel data
        funnel_data = await self.funnel_repository.get_funnel_metrics(
            workflow_id=query.workflow_id,
            start_date=query.start_date,
            end_date=query.end_date,
            include_step_details=query.include_step_details,
        )

        # Build response
        response = self._build_response(query, funnel_data)

        # Cache response
        if self.cache_service:
            await self.cache_service.set(
                cache_key,
                response.model_dump(),
                ttl=300,  # 5 minutes
            )

        return response

    def _build_cache_key(self, query: FunnelQueryDTO) -> str:
        """Build cache key from query parameters."""
        return (
            f"funnel:{query.workflow_id}:"
            f"{query.start_date}:{query.end_date}:{query.include_step_details}"
        )

    def _build_response(
        self,
        query: FunnelQueryDTO,
        data: dict[str, Any],
    ) -> FunnelAnalyticsDTO:
        """Build funnel analytics response from raw data.

        Args:
            query: Original query parameters.
            data: Raw funnel data from repository.

        Returns:
            Formatted FunnelAnalyticsDTO.
        """
        # Extract step data
        steps_data = data.get("steps", [])
        steps_dto = [
            FunnelStepDTO(
                step_id=UUID(s["step_id"]),
                step_name=s["step_name"],
                step_order=s["step_order"],
                entered=s["entered"],
                completed=s["completed"],
                dropped_off=s["dropped_off"],
                conversion_rate=s["conversion_rate"],
                drop_off_rate=s["drop_off_rate"],
                is_bottleneck=s.get("is_bottleneck", False),
            )
            for s in steps_data
        ]

        # Extract bottleneck
        bottleneck_id = data.get("bottleneck_step_id")
        bottleneck_uuid = UUID(bottleneck_id) if bottleneck_id else None

        return FunnelAnalyticsDTO(
            workflow_id=query.workflow_id,
            total_enrolled=data.get("total_enrolled", 0),
            final_converted=data.get("final_converted", 0),
            overall_conversion_rate=data.get("overall_conversion_rate", 0.0),
            bottleneck_step_id=bottleneck_uuid,
            steps=steps_dto,
            analyzed_at=datetime.now(UTC),
        )
