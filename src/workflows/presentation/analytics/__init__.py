"""
Workflow Analytics Presentation Layer

This module contains the presentation layer for workflow analytics,
including FastAPI routes and Pydantic schemas.

Components:
- Routes: FastAPI endpoints for analytics API
- Schemas: Request/response validation schemas
"""

from .analytics_routes import router

__all__ = [
    "router",
]
