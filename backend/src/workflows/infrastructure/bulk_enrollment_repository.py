"""Repository implementations for bulk enrollment."""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.workflows.domain.bulk_enrollment_entities import (
    BulkEnrollmentBatch,
    BulkEnrollmentJob,
    EnrollmentFailure,
)
from src.workflows.infrastructure.bulk_enrollment_models import (
    BulkEnrollmentBatchModel,
    BulkEnrollmentFailureModel,
    BulkEnrollmentJobModel,
)


class IBulkEnrollmentRepository(ABC):
    """Abstract interface for bulk enrollment repository."""

    @abstractmethod
    async def create_job(self, job: BulkEnrollmentJob) -> BulkEnrollmentJob:
        """Create a new bulk enrollment job."""
        pass

    @abstractmethod
    async def get_job_by_id(
        self, job_id: UUID, account_id: UUID
    ) -> BulkEnrollmentJob | None:
        """Get a job by ID."""
        pass

    @abstractmethod
    async def list_jobs(
        self,
        account_id: UUID,
        workflow_id: UUID | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[BulkEnrollmentJob], int]:
        """List jobs with filters."""
        pass

    @abstractmethod
    async def update_job(self, job: BulkEnrollmentJob) -> BulkEnrollmentJob:
        """Update an existing job."""
        pass

    @abstractmethod
    async def create_batch(self, batch: BulkEnrollmentBatch) -> BulkEnrollmentBatch:
        """Create a new batch."""
        pass

    @abstractmethod
    async def update_batch(self, batch: BulkEnrollmentBatch) -> BulkEnrollmentBatch:
        """Update an existing batch."""
        pass

    @abstractmethod
    async def get_batches_by_job(
        self, job_id: UUID, offset: int = 0, limit: int = 50
    ) -> list[BulkEnrollmentBatch]:
        """Get batches for a job."""
        pass

    @abstractmethod
    async def create_failure(self, failure: EnrollmentFailure) -> EnrollmentFailure:
        """Create a failure record."""
        pass

    @abstractmethod
    async def get_failures_by_job(
        self, job_id: UUID, offset: int = 0, limit: int = 50
    ) -> list[EnrollmentFailure]:
        """Get failures for a job."""
        pass

    @abstractmethod
    async def count_failures_by_job(self, job_id: UUID) -> int:
        """Count failures for a job."""
        pass


class PostgresBulkEnrollmentRepository(IBulkEnrollmentRepository):
    """PostgreSQL implementation of bulk enrollment repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: Async database session.
        """
        self._session = session

    async def create_job(self, job: BulkEnrollmentJob) -> BulkEnrollmentJob:
        """Create a new bulk enrollment job.

        Args:
            job: BulkEnrollmentJob entity.

        Returns:
            Created job with generated ID.
        """
        model = BulkEnrollmentJobModel.from_domain(job)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model.to_domain()

    async def get_job_by_id(
        self, job_id: UUID, account_id: UUID
    ) -> BulkEnrollmentJob | None:
        """Get a job by ID.

        Args:
            job_id: Job ID.
            account_id: Account ID.

        Returns:
            Job if found, None otherwise.
        """
        result = await self._session.execute(
            select(BulkEnrollmentJobModel).where(
                and_(
                    BulkEnrollmentJobModel.id == job_id,
                    BulkEnrollmentJobModel.account_id == account_id,
                )
            )
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def list_jobs(
        self,
        account_id: UUID,
        workflow_id: UUID | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[BulkEnrollmentJob], int]:
        """List jobs with filters.

        Args:
            account_id: Account ID.
            workflow_id: Filter by workflow.
            status: Filter by status.
            offset: Pagination offset.
            limit: Maximum results.

        Returns:
            Tuple of (jobs list, total count).
        """
        # Build query
        query = select(BulkEnrollmentJobModel).where(
            BulkEnrollmentJobModel.account_id == account_id
        )

        # Apply filters
        conditions = []
        if workflow_id:
            conditions.append(BulkEnrollmentJobModel.workflow_id == workflow_id)
        if status:
            conditions.append(BulkEnrollmentJobModel.status == status)

        if conditions:
            query = query.where(and_(*conditions))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self._session.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        query = query.order_by(BulkEnrollmentJobModel.created_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(query)
        models = result.scalars().all()

        jobs = [model.to_domain() for model in models]

        return jobs, total

    async def update_job(self, job: BulkEnrollmentJob) -> BulkEnrollmentJob:
        """Update an existing job.

        Args:
            job: Job with updated values.

        Returns:
            Updated job.
        """
        result = await self._session.execute(
            select(BulkEnrollmentJobModel).where(
                and_(
                    BulkEnrollmentJobModel.id == job.id,
                    BulkEnrollmentJobModel.account_id == job.account_id,
                )
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None

        # Update fields
        model.status = job.status.value
        model.processed_count = job.processed_count
        model.success_count = job.success_count
        model.failure_count = job.failure_count
        model.skipped_count = job.skipped_count
        model.completed_batches = job.completed_batches
        model.started_at = job.started_at
        model.completed_at = job.completed_at
        model.estimated_completion = job.estimated_completion
        model.version = job.version
        model.updated_at = job.updated_at

        await self._session.flush()
        await self._session.refresh(model)
        return model.to_domain()

    async def create_batch(self, batch: BulkEnrollmentBatch) -> BulkEnrollmentBatch:
        """Create a new batch.

        Args:
            batch: BulkEnrollmentBatch entity.

        Returns:
            Created batch.
        """
        model = BulkEnrollmentBatchModel.from_domain(batch)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model.to_domain()

    async def update_batch(self, batch: BulkEnrollmentBatch) -> BulkEnrollmentBatch:
        """Update an existing batch.

        Args:
            batch: Batch with updated values.

        Returns:
            Updated batch.
        """
        result = await self._session.execute(
            select(BulkEnrollmentBatchModel).where(BulkEnrollmentBatchModel.id == batch.id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None

        # Update fields
        model.status = batch.status.value
        model.success_ids = batch.success_ids
        model.failure_ids = batch.failure_ids
        model.attempt_count = batch.attempt_count
        model.error_message = batch.error_message
        model.started_at = batch.started_at
        model.completed_at = batch.completed_at
        model.duration_ms = batch.duration_ms

        await self._session.flush()
        await self._session.refresh(model)
        return model.to_domain()

    async def get_batches_by_job(
        self, job_id: UUID, offset: int = 0, limit: int = 50
    ) -> list[BulkEnrollmentBatch]:
        """Get batches for a job.

        Args:
            job_id: Job ID.
            offset: Pagination offset.
            limit: Maximum results.

        Returns:
            List of batches.
        """
        result = await self._session.execute(
            select(BulkEnrollmentBatchModel)
            .where(BulkEnrollmentBatchModel.job_id == job_id)
            .order_by(BulkEnrollmentBatchModel.batch_number)
            .offset(offset)
            .limit(limit)
        )
        models = result.scalars().all()
        return [model.to_domain() for model in models]

    async def create_failure(self, failure: EnrollmentFailure) -> EnrollmentFailure:
        """Create a failure record.

        Args:
            failure: EnrollmentFailure entity.

        Returns:
            Created failure record.
        """
        model = BulkEnrollmentFailureModel.from_domain(failure)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model.to_domain()

    async def get_failures_by_job(
        self, job_id: UUID, offset: int = 0, limit: int = 50
    ) -> list[EnrollmentFailure]:
        """Get failures for a job.

        Args:
            job_id: Job ID.
            offset: Pagination offset.
            limit: Maximum results.

        Returns:
            List of failures.
        """
        result = await self._session.execute(
            select(BulkEnrollmentFailureModel)
            .where(BulkEnrollmentFailureModel.job_id == job_id)
            .order_by(BulkEnrollmentFailureModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        models = result.scalars().all()
        return [model.to_domain() for model in models]

    async def count_failures_by_job(self, job_id: UUID) -> int:
        """Count failures for a job.

        Args:
            job_id: Job ID.

        Returns:
            Number of failures.
        """
        result = await self._session.execute(
            select(func.count())
            .select_from(BulkEnrollmentFailureModel)
            .where(BulkEnrollmentFailureModel.job_id == job_id)
        )
        return result.scalar() or 0
