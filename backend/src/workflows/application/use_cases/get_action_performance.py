"""Use case: Get action performance metrics.

This use case retrieves performance metrics for individual workflow actions
including execution counts, success rates, and durations.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from src.workflows.application.analytics_dtos import (
    ActionPerformanceDTO,
    ActionPerformanceQueryDTO,
    ActionPerformanceResponseDTO,
)


class GetActionPerformanceUseCase:
    """Use case for retrieving action performance metrics.

    Orchestrates retrieval of per-action execution statistics
    and performance data.
    """

    def __init__(
        self,
        action_repository: Any,  # Will be ActionMetricsRepository
        cache_service: Any | None = None,  # Will be AnalyticsCacheService
    ):
        """Initialize use case.

        Args:
            action_repository: Repository for action metrics.
            cache_service: Optional cache service for performance.
        """
        self.action_repository = action_repository
        self.cache_service = cache_service

    async def execute(
        self,
        query: ActionPerformanceQueryDTO,
    ) -> ActionPerformanceResponseDTO:
        """Execute action performance query.

        Args:
            query: Action performance query parameters.

        Returns:
            ActionPerformanceResponseDTO with action metrics.

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
                return ActionPerformanceResponseDTO(**cached)

        # Fetch action performance data
        action_data = await self.action_repository.get_action_metrics(
            workflow_id=query.workflow_id,
            start_date=query.start_date,
            end_date=query.end_date,
            action_types=query.action_types if query.action_types else None,
        )

        # Build response
        response = self._build_response(query, action_data)

        # Cache response
        if self.cache_service:
            await self.cache_service.set(
                cache_key,
                response.model_dump(),
                ttl=300,  # 5 minutes
            )

        return response

    def _build_cache_key(self, query: ActionPerformanceQueryDTO) -> str:
        """Build cache key from query parameters."""
        types_str = ",".join(sorted(query.action_types)) if query.action_types else "all"
        return (
            f"actions:{query.workflow_id}:"
            f"{query.start_date}:{query.end_date}:{types_str}"
        )

    def _build_response(
        self,
        query: ActionPerformanceQueryDTO,
        data: dict[str, Any],
    ) -> ActionPerformanceResponseDTO:
        """Build action performance response from raw data.

        Args:
            query: Original query parameters.
            data: Raw action metrics from repository.

        Returns:
            Formatted ActionPerformanceResponseDTO.
        """
        # Extract actions data
        actions_data = data.get("actions", [])
        actions_dto = [
            ActionPerformanceDTO(
                action_id=UUID(a["action_id"]),
                action_type=a["action_type"],
                action_name=a["action_name"],
                executions=a["executions"],
                successes=a["successes"],
                failures=a["failures"],
                success_rate=a["success_rate"],
                average_duration_ms=a.get("average_duration_ms"),
            )
            for a in actions_data
        ]

        return ActionPerformanceResponseDTO(
            workflow_id=query.workflow_id,
            period={
                "start_date": query.start_date.isoformat(),
                "end_date": query.end_date.isoformat(),
            },
            actions=actions_dto,
            generated_at=datetime.now(UTC),
        )
