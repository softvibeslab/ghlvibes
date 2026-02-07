"""Application services for workflow analytics.

These services provide application-level business logic coordinating
between domain, infrastructure, and presentation layers.
"""

from datetime import UTC, datetime
from datetime import date as Date
from typing import Any
from uuid import UUID

from src.workflows.domain.analytics_entities import (
    MetricsSnapshot,
    WorkflowAnalytics,
)
from src.workflows.domain.analytics_exceptions import AnalyticsAggregationError


class AnalyticsAggregationService:
    """Service for aggregating analytics data from multiple sources.

    Coordinates aggregation of raw execution events into time-series
    metrics for efficient querying and dashboard display.
    """

    def __init__(
        self,
        execution_repository: Any,  # Will be ExecutionRepository
        analytics_repository: Any,  # Will be AnalyticsRepository
    ):
        """Initialize aggregation service.

        Args:
            execution_repository: Repository for execution data.
            analytics_repository: Repository for storing aggregated metrics.
        """
        self.execution_repository = execution_repository
        self.analytics_repository = analytics_repository

    async def aggregate_daily_metrics(
        self,
        workflow_id: UUID,
        date: Date,
    ) -> MetricsSnapshot:
        """Aggregate execution data for a single day.

        Args:
            workflow_id: Workflow to aggregate.
            date: Date to aggregate.

        Returns:
            MetricsSnapshot with aggregated data.

        Raises:
            AnalyticsAggregationError: If aggregation fails.
        """
        try:
            # Fetch executions for this date
            executions = await self.execution_repository.get_executions_by_date(
                workflow_id=workflow_id,
                date=date,
            )

            # Aggregate into snapshot
            snapshot = await self._aggregate_executions(
                workflow_id=workflow_id,
                date=date,
                executions=executions,
            )

            # Store snapshot
            await self.analytics_repository.store_snapshot(snapshot)

            return snapshot

        except Exception as err:
            raise AnalyticsAggregationError(
                f"Failed to aggregate metrics for {date}: {err}"
            ) from err

    async def aggregate_period_metrics(
        self,
        workflow_id: UUID,
        start_date: Date,
        end_date: Date,
    ) -> list[MetricsSnapshot]:
        """Aggregate metrics for a date range.

        Args:
            workflow_id: Workflow to aggregate.
            start_date: Range start.
            end_date: Range end.

        Returns:
            List of MetricsSnapshot for each day in range.
        """
        snapshots = []

        current_date = start_date
        while current_date <= end_date:
            snapshot = await self.aggregate_daily_metrics(
                workflow_id=workflow_id,
                date=current_date,
            )
            snapshots.append(snapshot)
            current_date = Date.fromordinal(current_date.toordinal() + 1)

        return snapshots

    async def _aggregate_executions(
        self,
        workflow_id: UUID,
        date: Date,
        executions: list[dict[str, Any]],
    ) -> MetricsSnapshot:
        """Aggregate execution records into metrics snapshot.

        Args:
            workflow_id: Workflow identifier.
            date: Aggregation date.
            executions: List of execution records.

        Returns:
            MetricsSnapshot with aggregated metrics.
        """
        # Initialize counters
        total_enrolled = len(executions)
        new_enrollments = 0
        currently_active = 0
        completed = 0
        goals_achieved = 0
        durations: list[int] = []

        for execution in executions:
            status = execution.get("status")
            enrolled_at = execution.get("enrolled_at")
            completed_at = execution.get("completed_at")

            # Check if new enrollment today
            if enrolled_at and enrolled_at.date() == date:
                new_enrollments += 1

            # Count active
            if status == "active":
                currently_active += 1

            # Count completions
            if status in ("completed", "goal_achieved"):
                completed += 1

                # Track duration
                if enrolled_at and completed_at:
                    duration = int((completed_at - enrolled_at).total_seconds())
                    durations.append(duration)

            # Count goals
            if status == "goal_achieved":
                goals_achieved += 1

        # Calculate average duration
        avg_duration = (
            sum(durations) // len(durations) if durations else None
        )

        return MetricsSnapshot.create(
            workflow_id=workflow_id,
            snapshot_date=date,
            total_enrolled=total_enrolled,
            new_enrollments=new_enrollments,
            currently_active=currently_active,
            completed=completed,
            goals_achieved=goals_achieved,
            average_duration_seconds=avg_duration,
        )


class AnalyticsCacheService:
    """Service for caching analytics data in Redis.

    Provides high-performance caching for frequently accessed
    analytics data to reduce database load.
    """

    def __init__(self, redis_client: Any):
        """Initialize cache service.

        Args:
            redis_client: Redis client instance.
        """
        self.redis = redis_client
        self.default_ttl = 300  # 5 minutes

    async def get(self, key: str) -> dict[str, Any] | None:
        """Get cached analytics data.

        Args:
            key: Cache key.

        Returns:
            Cached data, or None if not found.
        """
        try:
            import json

            cached = await self.redis.get(f"analytics:{key}")
            if cached:
                return json.loads(cached)
            return None
        except Exception:
            return None

    async def set(
        self,
        key: str,
        value: dict[str, Any],
        ttl: int | None = None,
    ) -> None:
        """Cache analytics data.

        Args:
            key: Cache key.
            value: Data to cache.
            ttl: Time-to-live in seconds (default: 5 minutes).
        """
        try:
            import json

            ttl = ttl or self.default_ttl
            serialized = json.dumps(value)
            await self.redis.setex(
                f"analytics:{key}",
                ttl,
                serialized,
            )
        except Exception:
            # Fail silently - cache miss is acceptable
            pass

    async def invalidate(self, key: str) -> None:
        """Invalidate cached analytics data.

        Args:
            key: Cache key to invalidate.
        """
        try:
            await self.redis.delete(f"analytics:{key}")
        except Exception:
            pass

    async def invalidate_workflow(self, workflow_id: UUID) -> None:
        """Invalidate all cached data for a workflow.

        Args:
            workflow_id: Workflow identifier.
        """
        try:
            # Find all keys matching pattern
            pattern = f"analytics:*:{workflow_id}:*"
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
        except Exception:
            pass


class RealtimeUpdateService:
    """Service for real-time analytics updates via Redis pub/sub.

    Broadcasts analytics updates to connected dashboard clients
    using Server-Sent Events (SSE).
    """

    def __init__(self, redis_client: Any):
        """Initialize realtime update service.

        Args:
            redis_client: Redis client instance.
        """
        self.redis = redis_client

    async def publish_update(
        self,
        workflow_id: UUID,
        update_type: str,
        data: dict[str, Any],
    ) -> None:
        """Publish analytics update to subscribers.

        Args:
            workflow_id: Workflow identifier.
            update_type: Type of update (metrics, funnel, action).
            data: Update data.
        """
        try:
            import json

            channel = f"analytics:updates:{workflow_id}"
            message = json.dumps({
                "type": update_type,
                "workflow_id": str(workflow_id),
                "data": data,
                "timestamp": datetime.now(UTC).isoformat(),
            })

            await self.redis.publish(channel, message)
        except Exception:
            # Fail silently - real-time updates are optional
            pass

    async def subscribe_to_updates(
        self,
        workflow_id: UUID,
    ) -> Any:
        """Subscribe to updates for a workflow.

        Args:
            workflow_id: Workflow identifier.

        Returns:
            Async iterator yielding update messages.
        """
        channel = f"analytics:updates:{workflow_id}"
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)

        async def message_iterator():
            async for message in pubsub.listen():
                if message["type"] == "message":
                    yield message["data"]

        return message_iterator()
