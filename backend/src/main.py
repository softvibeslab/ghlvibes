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
    InvalidWorkflowNameError,
    InvalidWorkflowStatusTransitionError,
    WorkflowAlreadyExistsError,
    WorkflowDomainError,
    WorkflowNotFoundError,
)
from src.workflows.presentation import router as workflow_router
from src.workflows.presentation.middleware import setup_middleware


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

    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:
        """Health check endpoint for monitoring."""
        return {"status": "healthy", "version": settings.app_version}

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
