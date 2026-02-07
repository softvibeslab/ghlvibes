"""Use case for instantiating workflow templates."""

from uuid import UUID

from src.workflows.application.template_dtos import (
    InstantiateTemplateRequestDTO,
    TemplateResponseDTO,
    TemplateUsageResponseDTO,
)
from src.workflows.domain.exceptions import ValidationError, WorkflowNotFoundError
from src.workflows.domain.template_entities import TemplateUsage, WorkflowTemplate
from src.workflows.infrastructure.repositories import IWorkflowRepository
from src.workflows.infrastructure.template_repository import ITemplateRepository


class InstantiateTemplateUseCase:
    """Use case for instantiating a template to a workflow.

    This use case clones a template configuration into a new workflow
    and tracks the template usage.
    """

    def __init__(
        self,
        template_repository: ITemplateRepository,
        workflow_repository: IWorkflowRepository,
    ) -> None:
        """Initialize the use case.

        Args:
            template_repository: Repository for workflow templates.
            workflow_repository: Repository for workflows.
        """
        self._template_repository = template_repository
        self._workflow_repository = workflow_repository

    async def execute(
        self,
        template_id: UUID,
        account_id: UUID,
        request_dto: InstantiateTemplateRequestDTO,
        created_by: UUID,
    ) -> TemplateUsageResponseDTO:
        """Execute the use case.

        Args:
            template_id: Template to instantiate.
            account_id: Account instantiating the template.
            request_dto: Instantiation request with workflow details.
            created_by: User creating the workflow.

        Returns:
            Template usage record with new workflow ID.

        Raises:
            WorkflowNotFoundError: If template doesn't exist.
            ValidationError: If template cannot be cloned.
        """
        # Get template
        template = await self._template_repository.get_by_id(template_id, account_id)
        if template is None:
            raise WorkflowNotFoundError(f"Template not found: {template_id}")

        # Validate template can be cloned
        # TODO: Check available integrations when integration system is implemented
        missing_integrations = []  # template.validate_for_cloning(available_integrations)
        if missing_integrations:
            raise ValidationError(
                f"Template requires missing integrations: {', '.join(missing_integrations)}"
            )

        # Create workflow from template
        workflow_data = {
            "account_id": account_id,
            "name": request_dto.workflow_name,
            "description": request_dto.workflow_description or template.description,
            "trigger": template.workflow_config.get("trigger", {}),
            "actions": template.workflow_config.get("actions", []),
            "status": "draft",
            "template_id": template_id,
            "template_version": template.version,
            "created_by": created_by,
        }

        workflow = await self._workflow_repository.create_from_template(workflow_data)

        # Create usage record
        usage = TemplateUsage.create(
            template_id=template_id,
            workflow_id=workflow.id,
            account_id=account_id,
            template_version=template.version,
        )

        await self._template_repository.record_usage(usage)

        # Increment template usage count
        template.increment_usage_count()
        await self._template_repository.update(template)

        return TemplateUsageResponseDTO.model_validate(usage.to_dict())
