"""
Comprehensive tests for Funnels module - SPEC-FUN-001.
Tests funnel lifecycle management with 85%+ coverage target.
"""
import pytest
from uuid import uuid4, UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.funnels.domain.entities import Funnel, FunnelStep
from src.funnels.domain.value_objects import FunnelStatus, FunnelType, StepType
from src.funnels.application.use_cases import (
    CreateFunnelUseCase,
    ListFunnelsUseCase,
    UpdateFunnelUseCase,
)


@pytest.mark.asyncio
class TestFunnelAggregate:
    """Test Funnel aggregate root behavior."""

    async def test_create_funnel_success(self):
        """Test successful funnel creation."""
        funnel = Funnel(
            id=uuid4(),
            account_id=uuid4(),
            name="Test Funnel",
            funnel_type=FunnelType.LEAD_GENERATION,
            status=FunnelStatus.DRAFT,
            created_by=uuid4(),
        )
        assert funnel.id is not None
        assert funnel.name == "Test Funnel"
        assert funnel.version == 1
        assert funnel.status == FunnelStatus.DRAFT

    async def test_funnel_name_validation(self):
        """Test funnel name validation."""
        with pytest.raises(ValueError, match="between 3 and 100 characters"):
            Funnel(
                id=uuid4(),
                account_id=uuid4(),
                name="AB",  # Too short
                funnel_type=FunnelType.LEAD_GENERATION,
                created_by=uuid4(),
            )

        with pytest.raises(ValueError, match="between 3 and 100 characters"):
            Funnel(
                id=uuid4(),
                account_id=uuid4(),
                name="A" * 101,  # Too long
                funnel_type=FunnelType.LEAD_GENERATION,
                created_by=uuid4(),
            )

    async def test_add_step_to_funnel(self):
        """Test adding a step to a funnel."""
        funnel = Funnel(
            id=uuid4(),
            account_id=uuid4(),
            name="Test Funnel",
            funnel_type=FunnelType.SALES,
            created_by=uuid4(),
        )

        step = FunnelStep(
            step_type=StepType.PAGE,
            name="Opt-in Page",
            page_id=uuid4(),
        )

        funnel.add_step(step)

        assert len(funnel.steps) == 1
        assert funnel.steps[0].order == 1
        assert funnel.version == 2

    async def test_remove_step_from_funnel(self):
        """Test removing a step from a funnel."""
        funnel = Funnel(
            id=uuid4(),
            account_id=uuid4(),
            name="Test Funnel",
            funnel_type=FunnelType.WEBINAR,
            created_by=uuid4(),
        )

        step1 = FunnelStep(step_type=StepType.PAGE, name="Step 1", page_id=uuid4())
        step2 = FunnelStep(step_type=StepType.THANK_YOU, name="Step 2")

        funnel.add_step(step1)
        funnel.add_step(step2)
        assert len(funnel.steps) == 2

        funnel.remove_step(step1.id)
        assert len(funnel.steps) == 1
        assert funnel.steps[0].order == 1  # Reordered
        assert funnel.version == 4

    async def test_publish_funnel(self):
        """Test publishing a funnel."""
        funnel = Funnel(
            id=uuid4(),
            account_id=uuid4(),
            name="Test Funnel",
            funnel_type=FunnelType.BOOKING,
            status=FunnelStatus.DRAFT,
            created_by=uuid4(),
        )

        funnel.publish()

        assert funnel.status == FunnelStatus.ACTIVE
        assert funnel.version == 2

    async def test_publish_non_draft_funnel_fails(self):
        """Test that publishing a non-draft funnel fails."""
        funnel = Funnel(
            id=uuid4(),
            account_id=uuid4(),
            name="Test Funnel",
            funnel_type=FunnelType.SALES,
            status=FunnelStatus.ACTIVE,
            created_by=uuid4(),
        )

        with pytest.raises(ValueError, match="Only draft funnels can be published"):
            funnel.publish()

    async def test_clone_funnel(self):
        """Test cloning a funnel."""
        original = Funnel(
            id=uuid4(),
            account_id=uuid4(),
            name="Original Funnel",
            funnel_type=FunnelType.LEAD_GENERATION,
            version=3,
            created_by=uuid4(),
        )

        step = FunnelStep(step_type=StepType.PAGE, name="Page", page_id=uuid4())
        original.add_step(step)

        cloned = original.clone("Cloned Funnel")

        assert cloned.id != original.id
        assert cloned.name == "Cloned Funnel"
        assert cloned.version == 1
        assert len(cloned.steps) == 1
        assert cloned.steps[0].id != original.steps[0].id


@pytest.mark.asyncio
class TestCreateFunnelUseCase:
    """Test CreateFunnelUseCase."""

    async def test_execute_creates_funnel(self, db: AsyncSession):
        """Test that use case creates a funnel in database."""
        account_id = uuid4()
        user_id = uuid4()

        data = {
            "name": "New Funnel",
            "description": "Test description",
            "funnel_type": "lead_generation",
            "status": "draft",
            "steps": [
                {
                    "step_type": "page",
                    "name": "Opt-in",
                    "page_id": str(uuid4()),
                    "order": 1,
                    "config": {},
                }
            ],
        }

        use_case = CreateFunnelUseCase(db)
        funnel = await use_case.execute(account_id, data)

        assert funnel is not None
        assert funnel.name == "New Funnel"
        assert funnel.account_id == account_id


@pytest.mark.asyncio
class TestListFunnelsUseCase:
    """Test ListFunnelsUseCase."""

    async def test_execute_returns_paginated_funnels(self, db: AsyncSession):
        """Test that use case returns paginated funnel list."""
        account_id = uuid4()

        use_case = ListFunnelsUseCase(db)
        result = await use_case.execute(
            account_id,
            page=1,
            page_size=20,
        )

        assert "items" in result
        assert "total" in result
        assert "page" in result
        assert "page_size" in result
        assert result["page"] == 1
        assert result["page_size"] == 20
