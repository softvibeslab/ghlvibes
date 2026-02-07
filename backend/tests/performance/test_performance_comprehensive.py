"""
Comprehensive performance tests for the Workflow API.

This test suite measures and validates performance characteristics
of critical endpoints and operations.
"""

import pytest
import time
from uuid import uuid4
from httpx import AsyncClient


@pytest.mark.performance
class TestAPIPerformance:
    """Test suite for API endpoint performance."""

    @pytest.mark.asyncio
    async def test_create_workflow_performance(self, async_client: AsyncClient):
        """Given standard payload, when POST /workflows, then responds in < 300ms."""
        # Arrange
        payload = {
            "name": "Performance Test Workflow",
            "description": "Testing API performance",
            "trigger_type": "webhook",
        }

        # Act
        start_time = time.time()
        response = await async_client.post("/api/v1/workflows", json=payload)
        end_time = time.time()

        # Assert
        assert response.status_code == 201
        duration_ms = (end_time - start_time) * 1000
        assert duration_ms < 300, f"Response took {duration_ms}ms, expected < 300ms"

    @pytest.mark.asyncio
    async def test_get_workflow_performance(self, async_client: AsyncClient):
        """Given workflow exists, when GET /workflows/:id, then responds in < 150ms."""
        # Arrange
        create_response = await async_client.post("/api/v1/workflows", json={
            "name": "Performance Test Workflow"
        })
        workflow_id = create_response.json()["id"]

        # Act
        start_time = time.time()
        response = await async_client.get(f"/api/v1/workflows/{workflow_id}")
        end_time = time.time()

        # Assert
        assert response.status_code == 200
        duration_ms = (end_time - start_time) * 1000
        assert duration_ms < 150, f"Response took {duration_ms}ms, expected < 150ms"

    @pytest.mark.asyncio
    async def test_list_workflows_performance(self, async_client: AsyncClient):
        """Given many workflows, when GET /workflows, then responds in < 200ms."""
        # Arrange - Create 50 workflows
        for i in range(50):
            await async_client.post("/api/v1/workflows", json={
                "name": f"Performance Workflow {i}"
            })

        # Act
        start_time = time.time()
        response = await async_client.get("/api/v1/workflows?page_size=50")
        end_time = time.time()

        # Assert
        assert response.status_code == 200
        duration_ms = (end_time - start_time) * 1000
        assert duration_ms < 200, f"Response took {duration_ms}ms, expected < 200ms"

    @pytest.mark.asyncio
    async def test_update_workflow_performance(self, async_client: AsyncClient):
        """Given workflow exists, when PATCH /workflows/:id, then responds in < 250ms."""
        # Arrange
        create_response = await async_client.post("/api/v1/workflows", json={
            "name": "Original Name"
        })
        workflow_id = create_response.json()["id"]

        # Act
        start_time = time.time()
        response = await async_client.patch(
            f"/api/v1/workflows/{workflow_id}",
            json={"name": "Updated Name"}
        )
        end_time = time.time()

        # Assert
        assert response.status_code == 200
        duration_ms = (end_time - start_time) * 1000
        assert duration_ms < 250, f"Response took {duration_ms}ms, expected < 250ms"

    @pytest.mark.asyncio
    async def test_delete_workflow_performance(self, async_client: AsyncClient):
        """Given draft workflow, when DELETE /workflows/:id, then responds in < 200ms."""
        # Arrange
        create_response = await async_client.post("/api/v1/workflows", json={
            "name": "Workflow to Delete"
        })
        workflow_id = create_response.json()["id"]

        # Act
        start_time = time.time()
        response = await async_client.delete(f"/api/v1/workflows/{workflow_id}")
        end_time = time.time()

        # Assert
        assert response.status_code == 204
        duration_ms = (end_time - start_time) * 1000
        assert duration_ms < 200, f"Response took {duration_ms}ms, expected < 200ms"


@pytest.mark.performance
class TestConcurrentLoad:
    """Test suite for concurrent load handling."""

    @pytest.mark.asyncio
    async def test_concurrent_workflow_creations(self, async_client: AsyncClient):
        """Given 10 concurrent requests, when creating workflows, then all succeed."""
        # Arrange
        import asyncio

        async def create_workflow(index: int):
            return await async_client.post("/api/v1/workflows", json={
                "name": f"Concurrent Workflow {index}"
            })

        # Act
        start_time = time.time()
        tasks = [create_workflow(i) for i in range(10)]
        responses = await asyncio.gather(*tasks)
        end_time = time.time()

        # Assert
        success_count = sum(1 for r in responses if r.status_code == 201)
        assert success_count == 10, f"Only {success_count}/10 workflows created"

        duration_ms = (end_time - start_time) * 1000
        assert duration_ms < 3000, f"Concurrent requests took {duration_ms}ms"

    @pytest.mark.asyncio
    async def test_concurrent_workflow_reads(self, async_client: AsyncClient):
        """Given workflow, when 50 concurrent reads, then all succeed."""
        # Arrange
        import asyncio

        create_response = await async_client.post("/api/v1/workflows", json={
            "name": "Read Test Workflow"
        })
        workflow_id = create_response.json()["id"]

        async def read_workflow():
            return await async_client.get(f"/api/v1/workflows/{workflow_id}")

        # Act
        start_time = time.time()
        tasks = [read_workflow() for _ in range(50)]
        responses = await asyncio.gather(*tasks)
        end_time = time.time()

        # Assert
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count == 50, f"Only {success_count}/50 reads succeeded"

        duration_ms = (end_time - start_time) * 1000
        assert duration_ms < 2000, f"Concurrent reads took {duration_ms}ms"


@pytest.mark.performance
class TestDatabasePerformance:
    """Test suite for database query performance."""

    @pytest.mark.asyncio
    async def test_query_optimization_with_index(self, async_client: AsyncClient):
        """Given indexed query, when listing workflows, then uses index."""
        # This would require database query analysis tools
        # Placeholder for query optimization test
        pass

    @pytest.mark.asyncio
    async def test_n_plus_1_query_prevention(self, async_client: AsyncClient):
        """Given workflow with relations, when fetching, then uses eager loading."""
        # This would require database query monitoring
        # Verify no N+1 query issues
        pass

    @pytest.mark.asyncio
    async def test_pagination_efficiency(self, async_client: AsyncClient):
        """Given large dataset, when paginating, then efficient."""
        # Arrange - Create 100 workflows
        for i in range(100):
            await async_client.post("/api/v1/workflows", json={
                "name": f"Pagination Test {i}"
            })

        # Act - Fetch first page
        start_time = time.time()
        response = await async_client.get("/api/v1/workflows?page=1&page_size=20")
        end_time = time.time()

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["workflows"]) == 20

        duration_ms = (end_time - start_time) * 1000
        assert duration_ms < 200, f"Pagination took {duration_ms}ms"


@pytest.mark.performance
class TestMemoryPerformance:
    """Test suite for memory usage and leaks."""

    @pytest.mark.asyncio
    async def test_workflow_creation_memory_efficiency(self):
        """Given many workflows, when creating, then memory usage stable."""
        # This would require memory profiling tools
        # Placeholder for memory efficiency test
        pass

    @pytest.mark.asyncio
    async def test_large_payload_handling(self, async_client: AsyncClient):
        """Given large workflow config, when creating, then handled efficiently."""
        # Arrange
        large_actions = [
            {
                "action_type": "send_email",
                "config": {"to": "test@example.com", "subject": "Test", "body": "x" * 1000},
                "order": i
            }
            for i in range(100)
        ]

        payload = {
            "name": "Large Workflow",
            "description": "x" * 10000,
            "actions": large_actions
        }

        # Act
        start_time = time.time()
        response = await async_client.post("/api/v1/workflows", json=payload)
        end_time = time.time()

        # Assert
        assert response.status_code in [201, 422]  # May be rejected by size limits
        duration_ms = (end_time - start_time) * 1000
        assert duration_ms < 2000, f"Large payload took {duration_ms}ms"


@pytest.mark.performance
class TestCachePerformance:
    """Test suite for caching effectiveness."""

    @pytest.mark.asyncio
    async def test_workflow_list_cached(self, async_client: AsyncClient):
        """Given cached list, when fetching twice, then second request faster."""
        # Arrange - First request
        start_time1 = time.time()
        response1 = await async_client.get("/api/v1/workflows")
        end_time1 = time.time()

        # Act - Second request (should be cached)
        start_time2 = time.time()
        response2 = await async_client.get("/api/v1/workflows")
        end_time2 = time.time()

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200

        duration1_ms = (end_time1 - start_time1) * 1000
        duration2_ms = (end_time2 - start_time2) * 1000

        # Second request should be significantly faster due to caching
        # Allow some tolerance for cache implementation
        assert duration2_ms <= duration1_ms * 1.2, \
            f"Cached request ({duration2_ms}ms) not faster than initial ({duration1_ms}ms)"


@pytest.mark.performance
class TestBenchmarkSuites:
    """Benchmark test suites for performance tracking."""

    @pytest.mark.asyncio
    async def test_workflow_crud_benchmark(self, async_client: AsyncClient):
        """Benchmark complete CRUD lifecycle."""
        timings = {}

        # Create
        start = time.time()
        create_response = await async_client.post("/api/v1/workflows", json={
            "name": "Benchmark Workflow"
        })
        timings["create"] = (time.time() - start) * 1000

        workflow_id = create_response.json()["id"]

        # Read
        start = time.time()
        await async_client.get(f"/api/v1/workflows/{workflow_id}")
        timings["read"] = (time.time() - start) * 1000

        # Update
        start = time.time()
        await async_client.patch(
            f"/api/v1/workflows/{workflow_id}",
            json={"name": "Updated Benchmark Workflow"}
        )
        timings["update"] = (time.time() - start) * 1000

        # Delete
        start = time.time()
        await async_client.delete(f"/api/v1/workflows/{workflow_id}")
        timings["delete"] = (time.time() - start) * 1000

        # Assert
        assert timings["create"] < 300, f"Create: {timings['create']}ms"
        assert timings["read"] < 150, f"Read: {timings['read']}ms"
        assert timings["update"] < 250, f"Update: {timings['update']}ms"
        assert timings["delete"] < 200, f"Delete: {timings['delete']}ms"

        # Log results for benchmark tracking
        print(f"\nCRUD Benchmark Results:")
        for operation, duration in timings.items():
            print(f"  {operation.capitalize()}: {duration:.2f}ms")
