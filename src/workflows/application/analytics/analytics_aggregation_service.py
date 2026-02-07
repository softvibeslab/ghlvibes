"""
Application Service: Analytics Aggregation Service

Orchestrates metrics aggregation, caching, and real-time updates
for workflow analytics.
"""

from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
import json

from ...domain.analytics import (
    WorkflowAnalytics,
    MetricsSnapshot,
    TimeRange,
)


class AnalyticsAggregationService:
    """
    Application service for aggregating analytics data.

    Manages the aggregation pipeline, caching layer, and
    real-time update broadcasting.
    """

    def __init__(
        self,
        analytics_repository,
        cache_service,
        event_bus,
    ):
        self.analytics_repository = analytics_repository
        self.cache_service = cache_service
        self.event_bus = event_bus

    async def aggregate_and_cache_metrics(
        self,
        workflow_id: UUID,
        aggregation_date: date,
    ) -> MetricsSnapshot:
        """
        Aggregate metrics for a specific date and cache the results.

        Args:
            workflow_id: Workflow identifier
            aggregation_date: Date to aggregate

        Returns:
            MetricsSnapshot with aggregated data
        """
        # Fetch execution records for the date
        execution_records = await self.analytics_repository.get_execution_data(
            workflow_id=workflow_id,
            start_date=aggregation_date,
            end_date=aggregation_date,
        )

        # Create snapshot
        snapshot = MetricsSnapshot(
            workflow_id=workflow_id,
            snapshot_date=aggregation_date,
            snapshot_timestamp=datetime.utcnow(),
            metrics_data={
                "total_enrolled": len(execution_records),
                "new_enrollments": len(execution_records),
                "completed": sum(1 for e in execution_records if e.get("status") == "completed"),
                "goals_achieved": sum(1 for e in execution_records if e.get("status") == "goal_achieved"),
            },
        )

        # Cache the snapshot
        cache_key = f"analytics:daily:{workflow_id}:{aggregation_date.isoformat()}"
        await self.cache_service.set(
            key=cache_key,
            value=snapshot.to_dict(),
            ttl=86400,  # 24 hours
        )

        # Publish aggregation event
        await self.event_bus.publish(
            event_type="analytics_aggregated",
            payload={
                "workflow_id": str(workflow_id),
                "date": aggregation_date.isoformat(),
                "metrics": snapshot.metrics_data,
            },
        )

        return snapshot

    async def get_cached_analytics(
        self,
        workflow_id: UUID,
        start_date: date,
        end_date: date,
    ) -> Optional[WorkflowAnalytics]:
        """
        Get analytics from cache if available.

        Args:
            workflow_id: Workflow identifier
            start_date: Start date
            end_date: End date

        Returns:
            WorkflowAnalytics if cached, None otherwise
        """
        cache_key = f"analytics:period:{workflow_id}:{start_date.isoformat()}:{end_date.isoformat()}"

        cached_data = await self.cache_service.get(cache_key)
        if cached_data:
            # Deserialize and return
            return WorkflowAnalytics.from_dict(cached_data)

        return None

    async def cache_analytics(
        self,
        analytics: WorkflowAnalytics,
        ttl: int = 300,  # 5 minutes default
    ) -> None:
        """
        Cache analytics data.

        Args:
            analytics: Analytics to cache
            ttl: Time-to-live in seconds
        """
        cache_key = f"analytics:period:{analytics.workflow_id}:{analytics.time_range.start_date.isoformat()}:{analytics.time_range.end_date.isoformat()}"

        await self.cache_service.set(
            key=cache_key,
            value=analytics.to_dict(),
            ttl=ttl,
        )

    async def invalidate_cache(self, workflow_id: UUID) -> None:
        """
        Invalidate all cached analytics for a workflow.

        Args:
            workflow_id: Workflow identifier
        """
        # Delete pattern-based cache keys
        pattern = f"analytics:*:{workflow_id}:*"
        await self.cache_service.delete_pattern(pattern)

    async def broadcast_realtime_update(
        self,
        workflow_id: UUID,
        metrics: Dict[str, Any],
    ) -> None:
        """
        Broadcast real-time analytics update via SSE/WebSocket.

        Args:
            workflow_id: Workflow identifier
            metrics: Updated metrics data
        """
        await self.event_bus.publish(
            event_type="analytics_update",
            channel=f"workflow_analytics:{workflow_id}",
            payload={
                "workflow_id": str(workflow_id),
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": metrics,
            },
        )


class AnalyticsCacheService:
    """
    Service for managing analytics cache.

    Provides caching layer for performance optimization.
    """

    def __init__(self, redis_client):
        self.redis_client = redis_client

    async def get(self, key: str) -> Optional[Dict]:
        """Get value from cache."""
        value = await self.redis_client.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Dict, ttl: int) -> None:
        """Set value in cache with TTL."""
        await self.redis_client.setex(
            key,
            ttl,
            json.dumps(value),
        )

    async def delete(self, key: str) -> None:
        """Delete key from cache."""
        await self.redis_client.delete(key)

    async def delete_pattern(self, pattern: str) -> None:
        """Delete keys matching pattern."""
        keys = await self.redis_client.keys(pattern)
        if keys:
            await self.redis_client.delete(*keys)


class ExportGenerationService:
    """
    Service for generating analytics export reports.

    Handles CSV, JSON, and PDF generation with formatting.
    """

    def __init__(self, storage_service):
        self.storage_service = storage_service

    async def generate_csv(
        self,
        analytics_data: Dict[str, Any],
        workflow_id: UUID,
    ) -> bytes:
        """Generate CSV export."""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["Metric", "Value"])

        # Flatten and write metrics
        flattened = self._flatten_dict(analytics_data)
        for key, value in flattened.items():
            writer.writerow([key, value])

        return output.getvalue().encode("utf-8")

    async def generate_json(
        self,
        analytics_data: Dict[str, Any],
        workflow_id: UUID,
    ) -> bytes:
        """Generate JSON export."""
        return json.dumps(analytics_data, indent=2, default=str).encode("utf-8")

    async def generate_pdf(
        self,
        analytics_data: Dict[str, Any],
        workflow_id: UUID,
        include_charts: bool = False,
    ) -> bytes:
        """Generate PDF export."""
        # PDF generation requires reportlab or similar
        # For now, return placeholder
        return b"PDF export (requires reportlab integration)"

    def _flatten_dict(self, d: Dict, parent_key: str = "", sep: str = ".") -> Dict:
        """Flatten nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
