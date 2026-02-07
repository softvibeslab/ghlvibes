"""Use case for deleting workflow templates."""

from uuid import UUID

from src.workflows.domain.exceptions import WorkflowNotFoundError
from src.workflows.infrastructure.template_repository import ITemplateRepository


class DeleteTemplateUseCase:
    """Use case for deleting a workflow template.

    This use case permanently removes a custom template.
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
    ) -> None:
        """Execute the use case.

        Args:
            template_id: Template to delete.
            account_id: Account owning the template.

        Raises:
            WorkflowNotFoundError: If template doesn't exist.
        """
        # Verify template exists
        template = await self._template_repository.get_by_id(template_id, account_id)
        if template is None:
            raise WorkflowNotFoundError(f"Template not found: {template_id}")

        # System templates cannot be deleted
        if template.is_system_template:
            raise ValidationError("System templates cannot be deleted")

        # Delete template
        await self._template_repository.delete(template_id, account_id)
