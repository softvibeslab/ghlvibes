"""Unit tests for workflow template use cases."""

from uuid import UUID, uuid4

import pytest

from src.workflows.application.template_dtos import (
    CreateTemplateRequestDTO,
    UpdateTemplateRequestDTO,
)
from src.workflows.application.use_cases.create_template import CreateTemplateUseCase
from src.workflows.application.use_cases.update_template import UpdateTemplateUseCase
from src.workflows.domain.exceptions import ValidationError
from src.workflows.domain.template_entities import TemplateCategory, WorkflowTemplate


class TestCreateTemplateUseCase:
    """Test suite for CreateTemplateUseCase."""

    @pytest.mark.asyncio
    async def test_create_template_success(self, template_repository):
        """Test successful template creation."""
        # Arrange
        account_id = uuid4()
        created_by = uuid4()
        request_dto = CreateTemplateRequestDTO(
            name="Test Template",
            description="A test template for unit testing",
            category="lead_nurturing",
            workflow_config={
                "trigger": {"type": "webhook"},
                "actions": [{"type": "send_email", "subject": "Test"}],
            },
            tags=["test", "automation"],
        )
        use_case = CreateTemplateUseCase(template_repository=template_repository)

        # Act
        result = await use_case.execute(
            account_id=account_id,
            request_dto=request_dto,
            created_by=created_by,
        )

        # Assert
        assert result.name == "Test Template"
        assert result.description == "A test template for unit testing"
        assert result.category == "lead_nurturing"
        assert result.metadata.is_system_template is False
        assert result.metadata.tags == ["test", "automation"]

    @pytest.mark.asyncio
    async def test_create_template_invalid_category(self, template_repository):
        """Test template creation with invalid category."""
        # Arrange
        account_id = uuid4()
        created_by = uuid4()
        request_dto = CreateTemplateRequestDTO(
            name="Test Template",
            description="A test template",
            category="invalid_category",
            workflow_config={
                "trigger": {"type": "webhook"},
                "actions": [{"type": "send_email"}],
            },
        )
        use_case = CreateTemplateUseCase(template_repository=template_repository)

        # Act & Assert
        with pytest.raises(ValidationError, match="Invalid template category"):
            await use_case.execute(
                account_id=account_id,
                request_dto=request_dto,
                created_by=created_by,
            )

    @pytest.mark.asyncio
    async def test_create_template_missing_trigger(self, template_repository):
        """Test template creation without trigger."""
        # Arrange
        account_id = uuid4()
        created_by = uuid4()
        request_dto = CreateTemplateRequestDTO(
            name="Test Template",
            description="A test template",
            category="lead_nurturing",
            workflow_config={"actions": [{"type": "send_email"}]},
        )
        use_case = CreateTemplateUseCase(template_repository=template_repository)

        # Act & Assert
        with pytest.raises(ValidationError, match="must include a trigger"):
            await use_case.execute(
                account_id=account_id,
                request_dto=request_dto,
                created_by=created_by,
            )

    @pytest.mark.asyncio
    async def test_create_template_missing_actions(self, template_repository):
        """Test template creation without actions."""
        # Arrange
        account_id = uuid4()
        created_by = uuid4()
        request_dto = CreateTemplateRequestDTO(
            name="Test Template",
            description="A test template",
            category="lead_nurturing",
            workflow_config={"trigger": {"type": "webhook"}},
        )
        use_case = CreateTemplateUseCase(template_repository=template_repository)

        # Act & Assert
        with pytest.raises(ValidationError, match="must include at least one action"):
            await use_case.execute(
                account_id=account_id,
                request_dto=request_dto,
                created_by=created_by,
            )


class TestUpdateTemplateUseCase:
    """Test suite for UpdateTemplateUseCase."""

    @pytest.mark.asyncio
    async def test_update_template_success(self, template_repository):
        """Test successful template update."""
        # Arrange
        account_id = uuid4()
        template_id = uuid4()

        # Create existing template
        existing_template = WorkflowTemplate.create(
            account_id=account_id,
            name="Original Name",
            description="Original description",
            category=TemplateCategory.LEAD_NURTURING,
            workflow_config={
                "trigger": {"type": "webhook"},
                "actions": [{"type": "send_email"}],
            },
            created_by=uuid4(),
        )
        existing_template.id = template_id

        # Mock repository returns existing template
        template_repository.get_by_id.return_value = existing_template
        template_repository.update.return_value = existing_template

        request_dto = UpdateTemplateRequestDTO(
            name="Updated Name",
            description="Updated description",
        )
        use_case = UpdateTemplateUseCase(template_repository=template_repository)

        # Act
        result = await use_case.execute(
            template_id=template_id,
            account_id=account_id,
            request_dto=request_dto,
        )

        # Assert
        assert result.name == "Updated Name"
        assert result.description == "Updated description"

    @pytest.mark.asyncio
    async def test_update_template_not_found(self, template_repository):
        """Test updating non-existent template."""
        # Arrange
        account_id = uuid4()
        template_id = uuid4()
        template_repository.get_by_id.return_value = None

        request_dto = UpdateTemplateRequestDTO(name="Updated Name")
        use_case = UpdateTemplateUseCase(template_repository=template_repository)

        # Act & Assert
        with pytest.raises(Exception):  # WorkflowNotFoundError
            await use_case.execute(
                template_id=template_id,
                account_id=account_id,
                request_dto=request_dto,
            )

    @pytest.mark.asyncio
    async def test_update_template_invalid_workflow_config(self, template_repository):
        """Test template update with invalid workflow config."""
        # Arrange
        account_id = uuid4()
        template_id = uuid4()
        existing_template = WorkflowTemplate.create(
            account_id=account_id,
            name="Test",
            description="Test",
            category=TemplateCategory.LEAD_NURTURING,
            workflow_config={
                "trigger": {"type": "webhook"},
                "actions": [{"type": "send_email"}],
            },
            created_by=uuid4(),
        )
        existing_template.id = template_id
        template_repository.get_by_id.return_value = existing_template

        request_dto = UpdateTemplateRequestDTO(
            workflow_config={"actions": [{"type": "send_email"}]}  # Missing trigger
        )
        use_case = UpdateTemplateUseCase(template_repository=template_repository)

        # Act & Assert
        with pytest.raises(ValidationError, match="must include a trigger"):
            await use_case.execute(
                template_id=template_id,
                account_id=account_id,
                request_dto=request_dto,
            )


@pytest.fixture
def template_repository(mocker):
    """Fixture for mocked template repository."""
    return mocker.AsyncMock()
