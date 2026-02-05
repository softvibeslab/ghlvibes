"""Workflow presentation layer.

This module contains the API routes, dependencies, and middleware
for the workflow HTTP API.

Structure:
- routes.py: FastAPI route definitions
- dependencies.py: Dependency injection for routes
- middleware.py: Rate limiting and other middleware
"""

from src.workflows.presentation.routes import router


__all__ = ["router"]
