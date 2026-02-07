"""Presentation layer for CRM module.

Contains FastAPI routes, dependencies, and middleware.
The presentation layer handles HTTP requests and responses.
"""

from src.crm.presentation.dependencies import (
    PaginationDep,
)
from src.crm.presentation.routes import router

__all__ = [
    "PaginationDep",
    "router",
]
