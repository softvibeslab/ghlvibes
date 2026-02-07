"""FastAPI application entry point.

This module creates and configures the FastAPI application with
all routes, middleware, and exception handlers.
"""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.workflows.domain.exceptions import (
    BulkEnrollmentJobNotFoundError,
    BulkEnrollmentJobNotCancellableError,
    BulkEnrollmentValidationError,
    ContactLimitExceededError,
    InvalidStatusTransitionError,
    InvalidWorkflowNameError,
    InvalidWorkflowStatusTransitionError,
    TemplateNotFoundError,
    TemplateValidationError,
    ValidationError,
    WorkflowAlreadyExistsError,
    WorkflowDomainError,
    WorkflowNotFoundError,
)
from src.workflows.domain.action_exceptions import (
    ActionDomainError,
    ActionNotFoundError,
    InvalidActionConfigurationError,
    InvalidActionTypeError,
    MaximumActionsExceededError,
    WorkflowMustBeInDraftError,
    ActionPositionConflictError,
)
from src.workflows.presentation import router as workflow_router
from src.workflows.presentation.action_routes import router as action_router
from src.workflows.presentation.bulk_enrollment_routes import router as bulk_enrollment_router
from src.workflows.presentation.goal_routes import router as goal_router
from src.workflows.presentation.middleware import setup_middleware
from src.workflows.presentation.template_routes import router as template_router
from src.crm.presentation.routes import router as crm_router
from src.api.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Handles startup and shutdown events for resource management.

    Args:
        app: FastAPI application instance.

    Yields:
        Control to the application.
    """
    # Startup: Initialize connections, caches, etc.
    yield
    # Shutdown: Close connections, cleanup resources


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "GoHighLevel Clone API - A full-featured marketing automation platform. "
            "This API provides workflow automation, contact management, and more."
        ),
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
            "X-Response-Time",
        ],
    )

    # Setup custom middleware
    setup_middleware(app)

    # Register exception handlers
    register_exception_handlers(app)

    # Register routers
    app.include_router(
        workflow_router,
        prefix=settings.api_v1_prefix,
    )
    app.include_router(
        action_router,
        prefix=settings.api_v1_prefix,
    )
    app.include_router(goal_router)
    app.include_router(template_router)
    app.include_router(bulk_enrollment_router)
    app.include_router(crm_router)
    app.include_router(health_router)

    @app.get("/", tags=["health"])
    async def root() -> dict[str, str]:
        """Root endpoint with API information."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs" if settings.debug else "disabled",
        }

    return app


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers.

    Args:
        app: FastAPI application instance.
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        errors = []
        for error in exc.errors():
            errors.append(
                {
                    "field": ".".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "validation_error",
                "message": "Request validation failed",
                "details": errors,
            },
        )

    @app.exception_handler(WorkflowNotFoundError)
    async def workflow_not_found_handler(
        request: Request,
        exc: WorkflowNotFoundError,
    ) -> JSONResponse:
        """Handle workflow not found errors."""
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "workflow_not_found",
                "message": exc.message,
            },
        )

    @app.exception_handler(WorkflowAlreadyExistsError)
    async def workflow_already_exists_handler(
        request: Request,
        exc: WorkflowAlreadyExistsError,
    ) -> JSONResponse:
        """Handle duplicate workflow errors."""
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "duplicate_workflow",
                "message": exc.message,
            },
        )

    @app.exception_handler(InvalidWorkflowNameError)
    async def invalid_workflow_name_handler(
        request: Request,
        exc: InvalidWorkflowNameError,
    ) -> JSONResponse:
        """Handle invalid workflow name errors."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "invalid_workflow_name",
                "message": exc.message,
            },
        )

    @app.exception_handler(InvalidWorkflowStatusTransitionError)
    async def invalid_status_transition_handler(
        request: Request,
        exc: InvalidWorkflowStatusTransitionError,
    ) -> JSONResponse:
        """Handle invalid status transition errors."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "invalid_status_transition",
                "message": exc.message,
            },
        )

    @app.exception_handler(WorkflowDomainError)
    async def workflow_domain_error_handler(
        request: Request,
        exc: WorkflowDomainError,
    ) -> JSONResponse:
        """Handle generic workflow domain errors."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "domain_error",
                "message": exc.message,
            },
        )

    # Action exception handlers
    @app.exception_handler(ActionNotFoundError)
    async def action_not_found_handler(
        request: Request,
        exc: ActionNotFoundError,
    ) -> JSONResponse:
        """Handle action not found errors."""
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "action_not_found",
                "message": exc.message,
            },
        )

    @app.exception_handler(InvalidActionConfigurationError)
    async def invalid_action_config_handler(
        request: Request,
        exc: InvalidActionConfigurationError,
    ) -> JSONResponse:
        """Handle invalid action configuration errors."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "invalid_action_config",
                "message": exc.message,
                "details": {
                    "action_type": exc.action_type,
                    "errors": exc.errors,
                },
            },
        )

    @app.exception_handler(InvalidActionTypeError)
    async def invalid_action_type_handler(
        request: Request,
        exc: InvalidActionTypeError,
    ) -> JSONResponse:
        """Handle invalid action type errors."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "invalid_action_type",
                "message": exc.message,
            },
        )

    @app.exception_handler(MaximumActionsExceededError)
    async def maximum_actions_exceeded_handler(
        request: Request,
        exc: MaximumActionsExceededError,
    ) -> JSONResponse:
        """Handle maximum actions exceeded errors."""
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "maximum_actions_exceeded",
                "message": exc.message,
                "details": {
                    "current_count": exc.current_count,
                    "max_count": exc.max_count,
                },
            },
        )

    @app.exception_handler(WorkflowMustBeInDraftError)
    async def workflow_must_be_draft_handler(
        request: Request,
        exc: WorkflowMustBeInDraftError,
    ) -> JSONResponse:
        """Handle workflow must be in draft status errors."""
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "workflow_status_invalid",
                "message": exc.message,
            },
        )

    @app.exception_handler(ActionPositionConflictError)
    async def action_position_conflict_handler(
        request: Request,
        exc: ActionPositionConflictError,
    ) -> JSONResponse:
        """Handle action position conflict errors."""
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "position_conflict",
                "message": exc.message,
            },
        )

    @app.exception_handler(ActionDomainError)
    async def action_domain_error_handler(
        request: Request,
        exc: ActionDomainError,
    ) -> JSONResponse:
        """Handle generic action domain errors."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "action_domain_error",
                "message": exc.message,
            },
        )

    # Template exception handlers
    @app.exception_handler(TemplateNotFoundError)
    async def template_not_found_handler(
        request: Request,
        exc: TemplateNotFoundError,
    ) -> JSONResponse:
        """Handle template not found errors."""
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "template_not_found",
                "message": exc.message,
            },
        )

    @app.exception_handler(TemplateValidationError)
    async def template_validation_error_handler(
        request: Request,
        exc: TemplateValidationError,
    ) -> JSONResponse:
        """Handle template validation errors."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "template_validation_error",
                "message": exc.message,
            },
        )

    # Bulk enrollment exception handlers
    @app.exception_handler(BulkEnrollmentJobNotFoundError)
    async def bulk_job_not_found_handler(
        request: Request,
        exc: BulkEnrollmentJobNotFoundError,
    ) -> JSONResponse:
        """Handle bulk enrollment job not found errors."""
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "bulk_job_not_found",
                "message": exc.message,
            },
        )

    @app.exception_handler(BulkEnrollmentValidationError)
    async def bulk_enrollment_validation_error_handler(
        request: Request,
        exc: BulkEnrollmentValidationError,
    ) -> JSONResponse:
        """Handle bulk enrollment validation errors."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "bulk_enrollment_validation_error",
                "message": exc.message,
                "details": {"errors": exc.errors},
            },
        )

    @app.exception_handler(ContactLimitExceededError)
    async def contact_limit_exceeded_handler(
        request: Request,
        exc: ContactLimitExceededError,
    ) -> JSONResponse:
        """Handle contact limit exceeded errors."""
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={
                "error": "contact_limit_exceeded",
                "message": exc.message,
                "details": {
                    "current_count": exc.current_count,
                    "max_allowed": exc.max_allowed,
                },
            },
        )

    @app.exception_handler(BulkEnrollmentJobNotCancellableError)
    async def bulk_job_not_cancellable_handler(
        request: Request,
        exc: BulkEnrollmentJobNotCancellableError,
    ) -> JSONResponse:
        """Handle bulk job not cancellable errors."""
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "bulk_job_not_cancellable",
                "message": exc.message,
                "details": {
                    "job_id": exc.job_id,
                    "status": exc.status,
                },
            },
        )

    @app.exception_handler(InvalidStatusTransitionError)
    async def invalid_status_transition_handler(
        request: Request,
        exc: InvalidStatusTransitionError,
    ) -> JSONResponse:
        """Handle generic invalid status transition errors."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "invalid_status_transition",
                "message": exc.message,
                "details": {
                    "current_status": exc.current_status,
                    "target_status": exc.target_status,
                },
            },
        )


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )
