"""Use case for listing workflow templates."""

from uuid import UUID

from src.workflows.application.template_dtos import (
    ListTemplatesRequestDTO,
    ListTemplatesResponseDTO,
    TemplateResponseDTO,
)
from src.workflows.infrastructure.template_repository import ITemplateRepository


class ListTemplatesUseCase:
    """Use case for listing workflow templates.

    This use case retrieves templates with filtering and pagination.
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
        request_dto: ListTemplatesRequestDTO,
    ) -> ListTemplatesResponseDTO:
        """Execute the use case.

        Args:
            account_id: Account to list templates for.
            request_dto: List request with filters.

        Returns:
            Paginated list of templates.
        """
        templates, total = await self._template_repository.list(
            account_id=account_id,
            category=request_dto.category,
            is_system_template=request_dto.is_system_template,
            search=request_dto.search,
            offset=request_dto.offset,
            limit=request_dto.limit,
        )

        template_dtos = [TemplateResponseDTO.model_validate(t.to_dict()) for t in templates]

        return ListTemplatesResponseDTO(
            templates=template_dtos,
            total=total,
            offset=request_dto.offset,
            limit=request_dto.limit,
        )
