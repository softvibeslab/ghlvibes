"""Workflow domain layer.

This module contains the pure domain logic for workflows including:
- Entities: Workflow aggregate root, Action, ActionExecution
- Value Objects: WorkflowName, WorkflowStatus, ActionType, ActionConfig
- Domain Exceptions: InvalidWorkflowNameError, InvalidActionConfigurationError, etc.

The domain layer has no external dependencies and contains
only business logic and domain rules.
"""

from src.workflows.domain.action_entities import Action, ActionExecution, ActionExecutionStatus
from src.workflows.domain.action_exceptions import (
    ActionDependencyCycleError,
    ActionDomainError,
    ActionExecutionError,
    ActionNotFoundError,
    ActionPositionConflictError,
    InvalidActionConfigurationError,
    InvalidActionTypeError,
    MaximumActionsExceededError,
    WorkflowMustBeInDraftError,
)
from src.workflows.domain.action_value_objects import ActionConfig, ActionType
from src.workflows.domain.condition_entities import Branch, Condition
from src.workflows.domain.entities import Workflow
from src.workflows.domain.exceptions import (
    InvalidWorkflowNameError,
    InvalidWorkflowStatusTransitionError,
    WorkflowDomainError,
    WorkflowNotFoundError,
)
from src.workflows.domain.execution_entities import ExecutionLog, ExecutionStatus, WorkflowExecution
from src.workflows.domain.execution_exceptions import (
    ActionExecutionError as ExecutionActionExecutionError,
    ConcurrentExecutionLimitError,
    ContactOptedOutError,
    ExecutionLockError,
    ExecutionNotFoundError,
    ExecutionTimeoutError,
    InvalidExecutionStatusTransitionError,
    RetryExhaustedError,
    WorkflowExecutionError,
    WorkflowNotActiveError,
)
from src.workflows.domain.value_objects import WorkflowName, WorkflowStatus
from src.workflows.domain.analytics_entities import (
    MetricsSnapshot,
    WorkflowAnalytics,
    WorkflowStepMetrics,
)
from src.workflows.domain.analytics_exceptions import (
    AnalyticsAggregationError,
    AnalyticsError,
    FunnelAnalysisError,
    InvalidCompletionRateError,
    InvalidConversionRateError,
    InvalidEnrollmentSourceError,
    MetricsCalculationError,
)
from src.workflows.domain.analytics_value_objects import (
    CompletionRate,
    ConversionRate,
    EnrollmentSource,
    ExitReason,
    StepConversionRate,
)
from src.workflows.domain.version_entities import (
    VersionDiff,
    VersionMigration,
    WorkflowVersion,
)
from src.workflows.domain.version_exceptions import (
    InvalidVersionStatusError,
    InvalidVersionNumberError,
    MaxVersionsExceededError,
    MigrationInProgressError,
    VersionConflictError,
    VersionDomainError,
    VersionNotFoundError,
)
from src.workflows.domain.version_value_objects import (
    ChangeSummary,
    VersionNumber,
    VersionStatus,
)


__all__ = [
    # Workflow entities
    "Workflow",
    "WorkflowName",
    "WorkflowStatus",
    "WorkflowDomainError",
    "InvalidWorkflowNameError",
    "InvalidWorkflowStatusTransitionError",
    "WorkflowNotFoundError",
    # Action entities
    "Action",
    "ActionExecution",
    "ActionExecutionStatus",
    "ActionType",
    "ActionConfig",
    "ActionDomainError",
    "InvalidActionTypeError",
    "InvalidActionConfigurationError",
    "ActionNotFoundError",
    "WorkflowMustBeInDraftError",
    "ActionPositionConflictError",
    "MaximumActionsExceededError",
    "ActionExecutionError",
    "ActionDependencyCycleError",
    # Condition entities
    "Branch",
    "Condition",
    # Execution entities
    "WorkflowExecution",
    "ExecutionLog",
    "ExecutionStatus",
    "WorkflowExecutionError",
    "InvalidExecutionStatusTransitionError",
    "ExecutionNotFoundError",
    "ExecutionActionExecutionError",
    "RetryExhaustedError",
    "ExecutionLockError",
    "WorkflowNotActiveError",
    "ContactOptedOutError",
    "ConcurrentExecutionLimitError",
    "ExecutionTimeoutError",
    # Analytics entities
    "WorkflowAnalytics",
    "WorkflowStepMetrics",
    "MetricsSnapshot",
    "CompletionRate",
    "ConversionRate",
    "StepConversionRate",
    "EnrollmentSource",
    "ExitReason",
    "AnalyticsError",
    "AnalyticsAggregationError",
    "MetricsCalculationError",
    "FunnelAnalysisError",
    "InvalidCompletionRateError",
    "InvalidConversionRateError",
    "InvalidEnrollmentSourceError",
    # Versioning entities
    "WorkflowVersion",
    "VersionDiff",
    "VersionMigration",
    "VersionNumber",
    "VersionStatus",
    "ChangeSummary",
    "VersionDomainError",
    "InvalidVersionStatusError",
    "MaxVersionsExceededError",
    "VersionNotFoundError",
    "VersionConflictError",
    "InvalidVersionNumberError",
    "MigrationInProgressError",
]
