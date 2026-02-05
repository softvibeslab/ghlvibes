"""Core module for shared infrastructure components.

This module contains configuration, database setup, and
common dependencies used across the application.
"""

from src.core.config import settings
from src.core.database import Base, get_db


__all__ = ["settings", "Base", "get_db"]
