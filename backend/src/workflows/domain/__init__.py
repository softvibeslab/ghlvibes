"""Workflow domain layer.

This module contains the pure domain logic for workflows including:
- Entities: Workflow aggregate root
- Value Objects: WorkflowName, WorkflowStatus
- Domain Exceptions: InvalidWorkflowNameError, etc.

The domain layer has no external dependencies and contains
only business logic and domain rules.
"""

from src.workflows.domain.entities import Workflow
from src.workflows.domain.exceptions import (
    InvalidWorkflowNameError,
    InvalidWorkflowStatusTransitionError,
    WorkflowDomainError,
    WorkflowNotFoundError,
)
from src.workflows.domain.value_objects import WorkflowName, WorkflowStatus


__all__ = [
    "Workflow",
    "WorkflowName",
    "WorkflowStatus",
    "WorkflowDomainError",
    "InvalidWorkflowNameError",
    "InvalidWorkflowStatusTransitionError",
    "WorkflowNotFoundError",
]
