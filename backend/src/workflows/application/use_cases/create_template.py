"""Use case for creating workflow templates."""

from uuid import UUID

from src.workflows.application.template_dtos import (
    CreateTemplateRequestDTO,
    TemplateResponseDTO,
)
from src.workflows.domain.exceptions import ValidationError
from src.workflows.domain.template_entities import (
    TemplateCategory,
    WorkflowTemplate,
)
from src.workflows.infrastructure.template_repository import ITemplateRepository


class CreateTemplateUseCase:
    """Use case for creating a new workflow template.

    This use case validates the template configuration and creates
    a custom workflow template for the account.
    """

    def __init__(
        self,
        template_repository: ITemplateRepository,
    ) -> None:
        """Initialize the use case.

        Args:
            template_repository: Repository for workflow templates.
        """
        self._template_repository = template_repository

    async def execute(
        self,
        account_id: UUID,
        request_dto: CreateTemplateRequestDTO,
        created_by: UUID,
    ) -> TemplateResponseDTO:
        """Execute the use case.

        Args:
            account_id: Account creating the template.
            request_dto: Template creation request.
            created_by: User creating the template.

        Returns:
            Created template configuration.

        Raises:
            ValidationError: If template configuration is invalid.
        """
        # Validate category
        try:
            category = TemplateCategory(request_dto.category)
        except ValueError as exc:
            raise ValidationError(f"Invalid template category: {request_dto.category}") from exc

        # Validate workflow_config structure
        if not request_dto.workflow_config.get("trigger"):
            raise ValidationError("Workflow configuration must include a trigger")

        if not request_dto.workflow_config.get("actions"):
            raise ValidationError("Workflow configuration must include at least one action")

        # Create template
        template = WorkflowTemplate.create(
            account_id=account_id,
            name=request_dto.name,
            description=request_dto.description,
            category=category,
            workflow_config=request_dto.workflow_config,
            created_by=created_by,
            required_integrations=request_dto.required_integrations,
            tags=request_dto.tags,
            estimated_completion_rate=request_dto.estimated_completion_rate,
            is_shared=request_dto.is_shared,
        )

        # Persist template
        saved_template = await self._template_repository.create(template)

        return TemplateResponseDTO.model_validate(saved_template.to_dict())
