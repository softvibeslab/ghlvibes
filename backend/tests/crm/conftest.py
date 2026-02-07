"""Test configuration and fixtures for CRM module."""

import pytest
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.crm.domain.entities import (
    Activity,
    Company,
    Contact,
    Deal,
    Note,
    Pipeline,
    PipelineStage,
    Tag,
)
from src.crm.domain.value_objects import (
    ActivityStatus,
    ActivityType,
    DealStatus,
    Money,
)
from src.crm.infrastructure.models import (
    ActivityModel,
    CompanyModel,
    ContactModel,
    ContactTag,
    DealModel,
    NoteModel,
    PipelineModel,
    PipelineStageModel,
    TagModel,
)


# ============================================================================
# Fixtures for Domain Entities
# ============================================================================

@pytest.fixture
def sample_tag():
    """Create a sample tag."""
    return Tag.create(
        account_id=uuid4(),
        name="VIP",
        color="#FF5733",
    )


@pytest.fixture
def sample_contact():
    """Create a sample contact."""
    return Contact.create(
        account_id=uuid4(),
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="+14155551234",
        created_by=uuid4(),
    )


@pytest.fixture
def sample_company():
    """Create a sample company."""
    return Company.create(
        account_id=uuid4(),
        name="Acme Corporation",
        domain="acme.com",
        industry="Technology",
    )


@pytest.fixture
def sample_pipeline():
    """Create a sample pipeline with stages."""
    pipeline = Pipeline.create(
        account_id=uuid4(),
        name="Sales Pipeline",
    )

    stages = [
        PipelineStage(
            id=uuid4(),
            pipeline_id=pipeline.id,
            name="Prospect",
            order=1,
            probability=10,
        ),
        PipelineStage(
            id=uuid4(),
            pipeline_id=pipeline.id,
            name="Qualification",
            order=2,
            probability=30,
        ),
        PipelineStage(
            id=uuid4(),
            pipeline_id=pipeline.id,
            name="Closed Won",
            order=3,
            probability=100,
        ),
    ]

    pipeline.stages = stages
    return pipeline


@pytest.fixture
def sample_deal(sample_pipeline):
    """Create a sample deal."""
    return Deal.create(
        account_id=uuid4(),
        pipeline_id=sample_pipeline.id,
        stage_id=sample_pipeline.stages[0].id,
        name="Enterprise Deal",
        value=50000.00,
        contact_id=uuid4(),
        company_id=uuid4(),
        created_by=uuid4(),
    )


@pytest.fixture
def sample_activity():
    """Create a sample activity."""
    return Activity.create(
        account_id=uuid4(),
        activity_type=ActivityType.MEETING,
        title="Product Demo",
        description="Demo to CTO",
        due_date=datetime.now(UTC),
        contact_id=uuid4(),
        created_by=uuid4(),
    )


@pytest.fixture
def sample_note():
    """Create a sample note."""
    return Note.create(
        account_id=uuid4(),
        content="Discussed budget approval",
        note_type="note",
        contact_id=uuid4(),
        created_by=uuid4(),
    )


# ============================================================================
# Fixtures for Database Models
# ============================================================================

@pytest.fixture
async def sample_contact_model(async_session: AsyncSession):
    """Create and persist a sample contact model."""
    contact = ContactModel(
        id=uuid4(),
        account_id=uuid4(),
        email="test@example.com",
        first_name="Test",
        last_name="User",
        phone="+14155551234",
        custom_fields={},
        created_by=uuid4(),
    )
    async_session.add(contact)
    await async_session.flush()
    return contact


@pytest.fixture
async def sample_company_model(async_session: AsyncSession):
    """Create and persist a sample company model."""
    company = CompanyModel(
        id=uuid4(),
        account_id=uuid4(),
        name="Test Company",
        domain="testcompany.com",
        industry="Technology",
    )
    async_session.add(company)
    await async_session.flush()
    return company


@pytest.fixture
async def sample_tag_model(async_session: AsyncSession):
    """Create and persist a sample tag model."""
    tag = TagModel(
        id=uuid4(),
        account_id=uuid4(),
        name="Test Tag",
        color="#FF5733",
    )
    async_session.add(tag)
    await async_session.flush()
    return tag


# ============================================================================
# Fixtures for Test Data
# ============================================================================

@pytest.fixture
def valid_contact_data():
    """Valid contact creation data."""
    return {
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+14155551234",
        "custom_fields": {"source": "website"},
        "tag_ids": [],
    }


@pytest.fixture
def valid_company_data():
    """Valid company creation data."""
    return {
        "name": "Acme Corporation",
        "domain": "acme.com",
        "website": "https://www.acme.com",
        "industry": "Technology",
        "size": "51-200",
        "tag_ids": [],
    }


@pytest.fixture
def valid_deal_data():
    """Valid deal creation data."""
    return {
        "pipeline_id": str(uuid4()),
        "stage_id": str(uuid4()),
        "name": "Enterprise Deal",
        "value": 50000.00,
        "contact_id": str(uuid4()),
        "probability": 60,
    }


@pytest.fixture
def valid_activity_data():
    """Valid activity creation data."""
    return {
        "activity_type": ActivityType.MEETING,
        "title": "Product Demo",
        "description": "Demo to CTO",
        "due_date": datetime.now(UTC),
        "contact_id": str(uuid4()),
    }


@pytest.fixture
def valid_note_data():
    """Valid note creation data."""
    return {
        "content": "Discussed budget approval",
        "note_type": "note",
        "contact_id": str(uuid4()),
    }
