"""Use case for updating workflow templates."""

from uuid import UUID

from src.workflows.application.template_dtos import (
    TemplateResponseDTO,
    UpdateTemplateRequestDTO,
)
from src.workflows.domain.exceptions import ValidationError, WorkflowNotFoundError
from src.workflows.domain.template_entities import TemplateCategory, WorkflowTemplate
from src.workflows.infrastructure.template_repository import ITemplateRepository


class UpdateTemplateUseCase:
    """Use case for updating a workflow template.

    This use case updates template properties and persists changes.
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
        template_id: UUID,
        account_id: UUID,
        request_dto: UpdateTemplateRequestDTO,
    ) -> TemplateResponseDTO:
        """Execute the use case.

        Args:
            template_id: Template to update.
            account_id: Account owning the template.
            request_dto: Update request data.

        Returns:
            Updated template configuration.

        Raises:
            WorkflowNotFoundError: If template doesn't exist.
            ValidationError: If update data is invalid.
        """
        # Get template
        template = await self._template_repository.get_by_id(template_id, account_id)
        if template is None:
            raise WorkflowNotFoundError(f"Template not found: {template_id}")

        # Convert category if provided
        category = None
        if request_dto.category:
            try:
                category = TemplateCategory(request_dto.category)
            except ValueError as exc:
                raise ValidationError(f"Invalid template category: {request_dto.category}") from exc

        # Validate workflow_config if provided
        if request_dto.workflow_config:
            if not request_dto.workflow_config.get("trigger"):
                raise ValidationError("Workflow configuration must include a trigger")
            if not request_dto.workflow_config.get("actions"):
                raise ValidationError("Workflow configuration must include at least one action")

        # Update template
        template.update(
            name=request_dto.name,
            description=request_dto.description,
            workflow_config=request_dto.workflow_config,
            category=category,
            tags=request_dto.tags,
            required_integrations=request_dto.required_integrations,
            estimated_completion_rate=request_dto.estimated_completion_rate,
            is_shared=request_dto.is_shared,
        )

        # Persist changes
        updated_template = await self._template_repository.update(template)

        return TemplateResponseDTO.model_validate(updated_template.to_dict())
