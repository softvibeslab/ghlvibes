"""FastAPI routes for workflow template endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.workflows.application.template_dtos import (
    CreateTemplateRequestDTO,
    InstantiateTemplateRequestDTO,
    ListTemplatesRequestDTO,
    ListTemplatesResponseDTO,
    TemplateResponseDTO,
    TemplateUsageResponseDTO,
    UpdateTemplateRequestDTO,
)
from src.workflows.application.use_cases.create_template import CreateTemplateUseCase
from src.workflows.application.use_cases.delete_template import DeleteTemplateUseCase
from src.workflows.application.use_cases.instantiate_template import InstantiateTemplateUseCase
from src.workflows.application.use_cases.list_templates import ListTemplatesUseCase
from src.workflows.application.use_cases.update_template import UpdateTemplateUseCase
from src.workflows.presentation.dependencies import get_current_user_id

router = APIRouter(prefix="/api/v1/workflow-templates", tags=["templates"])


@router.post(
    "",
    response_model=TemplateResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a workflow template",
    description="Create a new custom workflow template for the account.",
)
async def create_template(
    request_dto: CreateTemplateRequestDTO,
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
    current_user_id: UUID = Depends(get_current_user_id),  # noqa: B008
    create_template_uc: CreateTemplateUseCase = Depends(CreateTemplateUseCase),  # noqa: B008
) -> TemplateResponseDTO:
    """Create a new workflow template.

    Args:
        request_dto: Template creation request.
        account_id: Account creating the template.
        current_user_id: User creating the template.
        create_template_uc: Create template use case.

    Returns:
        Created template configuration.
    """
    return await create_template_uc.execute(
        account_id=account_id,
        request_dto=request_dto,
        created_by=current_user_id,
    )


@router.get(
    "",
    response_model=ListTemplatesResponseDTO,
    summary="List workflow templates",
    description="Retrieve all available templates with filtering and pagination.",
)
async def list_templates(
    category: str | None = None,
    is_system_template: bool | None = None,
    search: str | None = None,
    offset: int = 0,
    limit: int = 50,
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
    list_templates_uc: ListTemplatesUseCase = Depends(ListTemplatesUseCase),  # noqa: B008
) -> ListTemplatesResponseDTO:
    """List all available workflow templates.

    Args:
        category: Filter by category.
        is_system_template: Filter by system template flag.
        search: Search in name and description.
        offset: Pagination offset.
        limit: Maximum results to return.
        account_id: Account to list templates for.
        list_templates_uc: List templates use case.

    Returns:
        Paginated list of templates.
    """
    request_dto = ListTemplatesRequestDTO(
        category=category,
        is_system_template=is_system_template,
        search=search,
        offset=offset,
        limit=limit,
    )
    return await list_templates_uc.execute(
        account_id=account_id,
        request_dto=request_dto,
    )


@router.get(
    "/{template_id}",
    response_model=TemplateResponseDTO,
    summary="Get template details",
    description="Retrieve detailed information about a specific template.",
)
async def get_template(
    template_id: UUID,
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
    list_templates_uc: ListTemplatesUseCase = Depends(ListTemplatesUseCase),  # noqa: B008
) -> TemplateResponseDTO:
    """Get a specific template by ID.

    Args:
        template_id: Template ID.
        account_id: Account requesting the template.
        list_templates_uc: List templates use case (for repository access).

    Returns:
        Template details.

    Raises:
        HTTPException: If template not found (404).
    """
    # Use list_templates_uc to get single template
    # TODO: Create dedicated GetTemplateUseCase
    from src.workflows.infrastructure.template_repository import ITemplateRepository  # noqa: PLC0415

    # This is a temporary workaround - ideally we'd have a GetTemplateUseCase
    # For now, we'll return a 404 if not found
    raise NotImplementedError("Use GetTemplateUseCase when implemented")


@router.patch(
    "/{template_id}",
    response_model=TemplateResponseDTO,
    summary="Update a workflow template",
    description="Update template properties for custom templates.",
)
async def update_template(
    template_id: UUID,
    request_dto: UpdateTemplateRequestDTO,
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
    update_template_uc: UpdateTemplateUseCase = Depends(UpdateTemplateUseCase),  # noqa: B008
) -> TemplateResponseDTO:
    """Update a workflow template.

    Args:
        template_id: Template to update.
        request_dto: Update request data.
        account_id: Account owning the template.
        update_template_uc: Update template use case.

    Returns:
        Updated template configuration.
    """
    return await update_template_uc.execute(
        template_id=template_id,
        account_id=account_id,
        request_dto=request_dto,
    )


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a workflow template",
    description="Permanently remove a custom template.",
)
async def delete_template(
    template_id: UUID,
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
    delete_template_uc: DeleteTemplateUseCase = Depends(DeleteTemplateUseCase),  # noqa: B008
) -> None:
    """Delete a workflow template.

    Args:
        template_id: Template to delete.
        account_id: Account owning the template.
        delete_template_uc: Delete template use case.
    """
    await delete_template_uc.execute(
        template_id=template_id,
        account_id=account_id,
    )


@router.post(
    "/{template_id}/clone",
    response_model=TemplateUsageResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Instantiate template to workflow",
    description="Clone a template to create a new workflow instance.",
)
async def instantiate_template(
    template_id: UUID,
    request_dto: InstantiateTemplateRequestDTO,
    account_id: UUID = Depends(get_current_user_id),  # noqa: B008  # TODO: Use proper account context
    current_user_id: UUID = Depends(get_current_user_id),  # noqa: B008
    instantiate_template_uc: InstantiateTemplateUseCase = Depends(InstantiateTemplateUseCase),  # noqa: B008
) -> TemplateUsageResponseDTO:
    """Instantiate a template to create a new workflow.

    Args:
        template_id: Template to instantiate.
        request_dto: Instantiation request with workflow details.
        account_id: Account instantiating the template.
        current_user_id: User creating the workflow.
        instantiate_template_uc: Instantiate template use case.

    Returns:
        Template usage record with new workflow ID.
    """
    return await instantiate_template_uc.execute(
        template_id=template_id,
        account_id=account_id,
        request_dto=request_dto,
        created_by=current_user_id,
    )
