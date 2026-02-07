"""Integration tests for template repository."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.workflows.domain.template_entities import TemplateCategory, WorkflowTemplate
from src.workflows.infrastructure.template_repository import PostgresTemplateRepository


@pytest.mark.integration
class TestTemplateRepositoryIntegration:
    """Integration tests for template repository with real database."""

    @pytest.mark.asyncio
    async def test_create_and_retrieve_template(self, db_session: AsyncSession):
        """Test creating a template and retrieving it."""
        # Arrange
        account_id = pytest.UUID("12345678-1234-5678-1234-567812345678")
        created_by = pytest.UUID("87654321-4321-8765-4321-876543218765")

        template = WorkflowTemplate.create(
            account_id=account_id,
            name="Integration Test Template",
            description="Template for integration testing",
            category=TemplateCategory.ONBOARDING,
            workflow_config={
                "trigger": {"type": "contact_added"},
                "actions": [
                    {"type": "send_email", "subject": "Welcome"},
                    {"type": "wait", "duration": 3600},
                ],
            },
            created_by=created_by,
            tags=["integration", "test"],
        )

        repository = PostgresTemplateRepository(session=db_session)

        # Act
        created = await repository.create(template)
        retrieved = await repository.get_by_id(created.id, account_id)

        # Assert
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Integration Test Template"
        assert retrieved.category == TemplateCategory.ONBOARDING
        assert retrieved.metadata.tags == ["integration", "test"]

    @pytest.mark.asyncio
    async def test_list_templates_with_filters(self, db_session: AsyncSession):
        """Test listing templates with category filter."""
        # Arrange
        account_id = pytest.UUID("12345678-1234-5678-1234-567812345678")
        repository = PostgresTemplateRepository(session=db_session)

        # Create templates in different categories
        for category in [TemplateCategory.LEAD_NURTURING, TemplateCategory.ONBOARDING]:
            template = WorkflowTemplate.create(
                account_id=account_id,
                name=f"{category.value.title()} Template",
                description=f"Template for {category.value}",
                category=category,
                workflow_config={
                    "trigger": {"type": "webhook"},
                    "actions": [{"type": "send_email"}],
                },
                created_by=pytest.UUID("87654321-4321-8765-4321-876543218765"),
            )
            await repository.create(template)

        # Act - Filter by onboarding category
        templates, total = await repository.list(
            account_id=account_id,
            category="onboarding",
            limit=10,
        )

        # Assert
        assert len(templates) >= 1
        assert all(t.category == TemplateCategory.ONBOARDING for t in templates)
        assert total >= 1

    @pytest.mark.asyncio
    async def test_update_template(self, db_session: AsyncSession):
        """Test updating an existing template."""
        # Arrange
        account_id = pytest.UUID("12345678-1234-5678-1234-567812345678")
        repository = PostgresTemplateRepository(session=db_session)

        template = WorkflowTemplate.create(
            account_id=account_id,
            name="Original Name",
            description="Original description",
            category=TemplateCategory.RE_ENGAGEMENT,
            workflow_config={
                "trigger": {"type": "webhook"},
                "actions": [{"type": "send_email"}],
            },
            created_by=pytest.UUID("87654321-4321-8765-4321-876543218765"),
        )
        created = await repository.create(template)

        # Act
        created.update(
            name="Updated Name",
            description="Updated description",
            tags=["updated"],
        )
        updated = await repository.update(created)

        # Assert
        assert updated.name == "Updated Name"
        assert updated.description == "Updated description"
        assert updated.metadata.tags == ["updated"]

    @pytest.mark.asyncio
    async def test_delete_template(self, db_session: AsyncSession):
        """Test deleting a custom template."""
        # Arrange
        account_id = pytest.UUID("12345678-1234-5678-1234-567812345678")
        repository = PostgresTemplateRepository(session=db_session)

        template = WorkflowTemplate.create(
            account_id=account_id,
            name="To Be Deleted",
            description="This template will be deleted",
            category=TemplateCategory.REVIEW_REQUEST,
            workflow_config={
                "trigger": {"type": "webhook"},
                "actions": [{"type": "send_email"}],
            },
            created_by=pytest.UUID("87654321-4321-8765-4321-876543218765"),
        )
        created = await repository.create(template)

        # Act
        result = await repository.delete(created.id, account_id)
        retrieved = await repository.get_by_id(created.id, account_id)

        # Assert
        assert result is True
        assert retrieved is None
