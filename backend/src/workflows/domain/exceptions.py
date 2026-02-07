"""Domain exceptions for the workflow module.

These exceptions represent domain-level errors that occur
when business rules are violated.
"""


class WorkflowDomainError(Exception):
    """Base exception for all workflow domain errors.

    All domain-specific exceptions should inherit from this class
    to allow for easy catching of workflow-related errors.
    """

    def __init__(self, message: str) -> None:
        """Initialize the exception with a message.

        Args:
            message: Human-readable error description.
        """
        self.message = message
        super().__init__(message)


class InvalidWorkflowNameError(WorkflowDomainError):
    """Raised when a workflow name violates naming rules.

    This exception is raised when:
    - Name is empty or whitespace only
    - Name is too short (< 3 characters)
    - Name is too long (> 100 characters)
    - Name contains invalid characters
    - Name has leading/trailing spaces
    """

    pass


class InvalidWorkflowStatusTransitionError(WorkflowDomainError):
    """Raised when an invalid status transition is attempted.

    Valid transitions:
    - draft -> active
    - active -> paused
    - active -> draft
    - paused -> active
    - paused -> draft
    """

    def __init__(self, current_status: str, target_status: str) -> None:
        """Initialize with current and target status.

        Args:
            current_status: The current workflow status.
            target_status: The status attempted to transition to.
        """
        message = (
            f"Cannot transition workflow from '{current_status}' to '{target_status}'. "
            f"This transition is not allowed."
        )
        super().__init__(message)
        self.current_status = current_status
        self.target_status = target_status


class WorkflowNotFoundError(WorkflowDomainError):
    """Raised when a workflow cannot be found.

    This exception is raised when attempting to access
    a workflow that does not exist or has been deleted.
    """

    def __init__(self, workflow_id: str) -> None:
        """Initialize with the workflow ID.

        Args:
            workflow_id: The ID of the workflow that was not found.
        """
        message = f"Workflow with ID '{workflow_id}' not found"
        super().__init__(message)
        self.workflow_id = workflow_id


class WorkflowValidationError(WorkflowDomainError):
    """Raised when workflow data fails validation.

    This exception is raised when the workflow data
    does not meet business validation requirements.
    """

    def __init__(self, errors: list[str]) -> None:
        """Initialize with validation errors.

        Args:
            errors: List of validation error messages.
        """
        message = f"Workflow validation failed: {'; '.join(errors)}"
        super().__init__(message)
        self.errors = errors


class WorkflowAlreadyExistsError(WorkflowDomainError):
    """Raised when attempting to create a duplicate workflow.

    This exception is raised when a workflow with the same
    name already exists in the same account.
    """

    def __init__(self, name: str, account_id: str) -> None:
        """Initialize with workflow name and account ID.

        Args:
            name: The workflow name that already exists.
            account_id: The account where the duplicate was found.
        """
        message = f"Workflow with name '{name}' already exists in account '{account_id}'"
        super().__init__(message)
        self.name = name
        self.account_id = account_id


class WorkflowOperationError(WorkflowDomainError):
    """Raised when a workflow operation fails.

    This is a general exception for workflow operations
    that fail due to unexpected conditions.
    """

    pass


class ValidationError(WorkflowDomainError):
    """Raised when data fails validation.

    This exception is raised when input data does not meet
    validation requirements for entities or value objects.
    """

    pass


class InvalidStatusTransitionError(WorkflowDomainError):
    """Raised when an invalid status transition is attempted.

    Generic status transition error for any entity with status tracking.
    """

    def __init__(self, current_status: str, target_status: str) -> None:
        """Initialize with current and target status.

        Args:
            current_status: The current status.
            target_status: The status attempted to transition to.
        """
        message = (
            f"Cannot transition from '{current_status}' to '{target_status}'. "
            f"This transition is not allowed."
        )
        super().__init__(message)
        self.current_status = current_status
        self.target_status = target_status


# Goal Tracking Exceptions
class GoalConfigNotFoundError(WorkflowDomainError):
    """Raised when a goal configuration cannot be found."""

    def __init__(self, goal_id: str) -> None:
        """Initialize with goal config ID.

        Args:
            goal_id: The ID of the goal config that was not found.
        """
        message = f"Goal configuration with ID '{goal_id}' not found"
        super().__init__(message)
        self.goal_id = goal_id


class GoalValidationError(WorkflowDomainError):
    """Raised when goal configuration fails validation."""

    pass


# Template Exceptions
class TemplateNotFoundError(WorkflowDomainError):
    """Raised when a workflow template cannot be found."""

    def __init__(self, template_id: str) -> None:
        """Initialize with template ID.

        Args:
            template_id: The ID of the template that was not found.
        """
        message = f"Workflow template with ID '{template_id}' not found"
        super().__init__(message)
        self.template_id = template_id


class TemplateValidationError(WorkflowDomainError):
    """Raised when template configuration fails validation."""

    def __init__(self, errors: list[str]) -> None:
        """Initialize with validation errors.

        Args:
            errors: List of validation error messages.
        """
        message = f"Template validation failed: {'; '.join(errors)}"
        super().__init__(message)
        self.errors = errors


class TemplateCloneError(WorkflowDomainError):
    """Raised when template cloning fails."""

    pass


class TemplateLimitExceededError(WorkflowDomainError):
    """Raised when account exceeds template limit."""

    def __init__(self, current_count: int, max_allowed: int) -> None:
        """Initialize with current count and limit.

        Args:
            current_count: Current number of templates.
            max_allowed: Maximum allowed templates.
        """
        message = (
            f"Template limit exceeded: {current_count} templates created, "
            f"maximum allowed is {max_allowed}"
        )
        super().__init__(message)
        self.current_count = current_count
        self.max_allowed = max_allowed


class MissingIntegrationError(WorkflowDomainError):
    """Raised when required integration is not available."""

    def __init__(self, integration: str) -> None:
        """Initialize with integration name.

        Args:
            integration: The missing integration name.
        """
        message = (
            f"Required integration '{integration}' is not available in this account"
        )
        super().__init__(message)
        self.integration = integration


# Bulk Enrollment Exceptions
class BulkEnrollmentJobNotFoundError(WorkflowDomainError):
    """Raised when a bulk enrollment job cannot be found."""

    def __init__(self, job_id: str) -> None:
        """Initialize with job ID.

        Args:
            job_id: The ID of the job that was not found.
        """
        message = f"Bulk enrollment job with ID '{job_id}' not found"
        super().__init__(message)
        self.job_id = job_id


class BulkEnrollmentValidationError(WorkflowDomainError):
    """Raised when bulk enrollment data fails validation."""

    def __init__(self, errors: list[str]) -> None:
        """Initialize with validation errors.

        Args:
            errors: List of validation error messages.
        """
        message = f"Bulk enrollment validation failed: {'; '.join(errors)}"
        super().__init__(message)
        self.errors = errors


class ContactLimitExceededError(WorkflowDomainError):
    """Raised when contact count exceeds maximum allowed."""

    def __init__(self, current_count: int, max_allowed: int) -> None:
        """Initialize with current count and limit.

        Args:
            current_count: Current number of contacts.
            max_allowed: Maximum allowed contacts.
        """
        message = (
            f"Contact limit exceeded: {current_count} contacts selected, "
            f"maximum allowed is {max_allowed}"
        )
        super().__init__(message)
        self.current_count = current_count
        self.max_allowed = max_allowed


class BulkEnrollmentJobNotCancellableError(WorkflowDomainError):
    """Raised when attempting to cancel a job that cannot be cancelled."""

    def __init__(self, job_id: str, status: str) -> None:
        """Initialize with job ID and status.

        Args:
            job_id: The ID of the job.
            status: The current status of the job.
        """
        message = (
            f"Cannot cancel job '{job_id}' with status '{status}'. "
            f"Job can only be cancelled while pending or processing."
        )
        super().__init__(message)
        self.job_id = job_id
        self.status = status
