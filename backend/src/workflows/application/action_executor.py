"""Action executor interface and implementations.

This module defines the strategy pattern for executing different
action types. Each action type has its own executor implementation.
"""

import httpx
from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4


class ExecutionResult:
    """Result of an action execution.

    Attributes:
        success: Whether execution was successful.
        data: Result data from execution.
        error: Error message if failed.
        duration_ms: Execution duration in milliseconds.
        should_retry: Whether execution should be retried.
        retry_delay_seconds: Delay before retry (if applicable).
    """

    def __init__(
        self,
        success: bool,
        data: dict[str, Any] | None = None,
        error: str | None = None,
        duration_ms: int = 0,
        should_retry: bool = False,
        retry_delay_seconds: int = 60,
    ) -> None:
        """Initialize execution result.

        Args:
            success: Whether execution was successful.
            data: Result data.
            error: Error message.
            duration_ms: Duration in milliseconds.
            should_retry: Whether to retry.
            retry_delay_seconds: Delay before retry.
        """
        self.success = success
        self.data = data or {}
        self.error = error
        self.duration_ms = duration_ms
        self.should_retry = should_retry
        self.retry_delay_seconds = retry_delay_seconds

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "should_retry": self.should_retry,
            "retry_delay_seconds": self.retry_delay_seconds,
        }


class ActionContext:
    """Context for action execution.

    Attributes:
        execution_id: Workflow execution ID.
        contact_id: Contact being processed.
        account_id: Account identifier.
        action_id: Action being executed.
        action_config: Action configuration.
        metadata: Additional execution metadata.
    """

    def __init__(
        self,
        execution_id: UUID,
        contact_id: UUID,
        account_id: UUID,
        action_id: UUID,
        action_config: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize action context.

        Args:
            execution_id: Workflow execution ID.
            contact_id: Contact ID.
            account_id: Account ID.
            action_id: Action ID.
            action_config: Action configuration.
            metadata: Optional metadata.
        """
        self.execution_id = execution_id
        self.contact_id = contact_id
        self.account_id = account_id
        self.action_id = action_id
        self.action_config = action_config
        self.metadata = metadata or {}


class BaseActionExecutor(ABC):
    """Abstract base class for action executors.

    Each action type implements this interface to provide
    type-specific execution logic.
    """

    @abstractmethod
    async def execute(self, context: ActionContext) -> ExecutionResult:
        """Execute the action.

        Args:
            context: Action execution context.

        Returns:
            Execution result.

        Raises:
            ActionExecutionError: If execution fails critically.
        """
        pass

    def _validate_config(self, context: ActionContext, required_fields: list[str]) -> None:
        """Validate that required config fields are present.

        Args:
            context: Action context.
            required_fields: List of required field names.

        Raises:
            ActionExecutionError: If validation fails.
        """
        from src.workflows.domain.execution_exceptions import ActionExecutionError

        missing_fields = [
            field for field in required_fields if field not in context.action_config
        ]

        if missing_fields:
            raise ActionExecutionError(
                context.action_config.get("type", "unknown"),
                f"Missing required configuration fields: {', '.join(missing_fields)}",
            )


class SendEmailExecutor(BaseActionExecutor):
    """Executor for send_email action type.

    Sends emails through the marketing module's email service.
    """

    async def execute(self, context: ActionContext) -> ExecutionResult:
        """Execute send email action.

        Args:
            context: Action context.

        Returns:
            Execution result.
        """
        from src.workflows.domain.execution_exceptions import ActionExecutionError

        start_time = datetime.now(UTC)

        try:
            # Validate configuration
            self._validate_config(
                context,
                ["template_id", "from_email", "subject"],
            )

            # In production, this would call the marketing module
            # For now, we simulate the execution
            template_id = context.action_config["template_id"]
            from_email = context.action_config["from_email"]
            subject = context.action_config["subject"]

            # Simulate API call
            # result = await marketing_service.send_email(
            #     contact_id=context.contact_id,
            #     template_id=template_id,
            #     from_email=from_email,
            #     subject=subject,
            #     variables=context.action_config.get("variables", {}),
            # )

            # Simulated success
            duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

            return ExecutionResult(
                success=True,
                data={
                    "email_id": str(uuid4()),
                    "template_id": template_id,
                    "from_email": from_email,
                    "subject": subject,
                },
                duration_ms=duration_ms,
                should_retry=False,
            )

        except ActionExecutionError:
            # Re-raise validation errors
            raise
        except Exception as e:
            # Handle unexpected errors
            duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            return ExecutionResult(
                success=False,
                error=str(e),
                duration_ms=duration_ms,
                should_retry=True,
                retry_delay_seconds=60,
            )


class SendSMSExecutor(BaseActionExecutor):
    """Executor for send_sms action type.

    Sends SMS messages through the marketing module's SMS service.
    """

    async def execute(self, context: ActionContext) -> ExecutionResult:
        """Execute send SMS action.

        Args:
            context: Action context.

        Returns:
            Execution result.
        """
        from src.workflows.domain.execution_exceptions import ActionExecutionError

        start_time = datetime.now(UTC)

        try:
            # Validate configuration
            self._validate_config(context, ["message", "from_number"])

            message = context.action_config["message"]
            from_number = context.action_config["from_number"]

            # Simulate API call
            # result = await marketing_service.send_sms(
            #     contact_id=context.contact_id,
            #     message=message,
            #     from_number=from_number,
            # )

            duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

            return ExecutionResult(
                success=True,
                data={
                    "sms_id": str(uuid4()),
                    "message": message,
                    "from_number": from_number,
                },
                duration_ms=duration_ms,
                should_retry=False,
            )

        except ActionExecutionError:
            raise
        except Exception as e:
            duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            return ExecutionResult(
                success=False,
                error=str(e),
                duration_ms=duration_ms,
                should_retry=True,
                retry_delay_seconds=60,
            )


class WebhookExecutor(BaseActionExecutor):
    """Executor for webhook action type.

    Makes HTTP requests to external webhooks.
    """

    async def execute(self, context: ActionContext) -> ExecutionResult:
        """Execute webhook action.

        Args:
            context: Action context.

        Returns:
            Execution result.
        """
        from src.workflows.domain.execution_exceptions import ActionExecutionError

        start_time = datetime.now(UTC)

        try:
            # Validate configuration
            self._validate_config(context, ["url", "method"])

            url = context.action_config["url"]
            method = context.action_config.get("method", "POST").upper()
            headers = context.action_config.get("headers", {})
            body = context.action_config.get("body", {})
            timeout = context.action_config.get("timeout", 30)

            # Make HTTP request
            async with httpx.AsyncClient(timeout=timeout) as client:
                if method == "GET":
                    response = await client.get(url, headers=headers, params=body)
                elif method == "POST":
                    response = await client.post(
                        url,
                        headers=headers,
                        json=body,
                    )
                elif method == "PUT":
                    response = await client.put(
                        url,
                        headers=headers,
                        json=body,
                    )
                else:
                    raise ActionExecutionError(
                        "webhook",
                        f"Unsupported HTTP method: {method}",
                    )

                duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

                # Determine success based on status code
                if 200 <= response.status_code < 300:
                    return ExecutionResult(
                        success=True,
                        data={
                            "status_code": response.status_code,
                            "response": response.json() if response.text else {},
                        },
                        duration_ms=duration_ms,
                        should_retry=False,
                    )
                elif 400 <= response.status_code < 500:
                    # Client error - don't retry
                    return ExecutionResult(
                        success=False,
                        error=f"Client error: {response.status_code}",
                        duration_ms=duration_ms,
                        should_retry=False,
                    )
                else:
                    # Server error - retry
                    return ExecutionResult(
                        success=False,
                        error=f"Server error: {response.status_code}",
                        duration_ms=duration_ms,
                        should_retry=True,
                        retry_delay_seconds=60,
                    )

        except ActionExecutionError:
            raise
        except httpx.TimeoutException as e:
            duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            return ExecutionResult(
                success=False,
                error=f"Request timeout: {str(e)}",
                duration_ms=duration_ms,
                should_retry=True,
                retry_delay_seconds=60,
            )
        except httpx.HTTPError as e:
            duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            return ExecutionResult(
                success=False,
                error=f"HTTP error: {str(e)}",
                duration_ms=duration_ms,
                should_retry=True,
                retry_delay_seconds=60,
            )
        except Exception as e:
            duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            return ExecutionResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                duration_ms=duration_ms,
                should_retry=True,
                retry_delay_seconds=60,
            )


class WaitTimeExecutor(BaseActionExecutor):
    """Executor for wait_time action type.

    Pauses workflow execution for specified duration.
    """

    async def execute(self, context: ActionContext) -> ExecutionResult:
        """Execute wait time action.

        Args:
            context: Action context.

        Returns:
            Execution result with scheduled resume time.
        """
        from src.workflows.domain.execution_exceptions import ActionExecutionError

        start_time = datetime.now(UTC)

        try:
            # Validate configuration
            self._validate_config(context, ["duration"])

            duration = context.action_config["duration"]
            unit = context.action_config.get("unit", "minutes")

            # Calculate wait duration
            if unit == "seconds":
                wait_delta = timedelta(seconds=duration)
            elif unit == "minutes":
                wait_delta = timedelta(minutes=duration)
            elif unit == "hours":
                wait_delta = timedelta(hours=duration)
            elif unit == "days":
                wait_delta = timedelta(days=duration)
            else:
                raise ActionExecutionError(
                    "wait_time",
                    f"Invalid unit: {unit}",
                )

            resume_at = datetime.now(UTC) + wait_delta
            duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

            return ExecutionResult(
                success=True,
                data={
                    "resume_at": resume_at.isoformat(),
                    "duration": duration,
                    "unit": unit,
                },
                duration_ms=duration_ms,
                should_retry=False,
            )

        except ActionExecutionError:
            raise
        except Exception as e:
            duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            return ExecutionResult(
                success=False,
                error=str(e),
                duration_ms=duration_ms,
                should_retry=False,
            )


class UpdateContactExecutor(BaseActionExecutor):
    """Executor for update_contact action type.

    Updates contact fields in the CRM.
    """

    async def execute(self, context: ActionContext) -> ExecutionResult:
        """Execute update contact action.

        Args:
            context: Action context.

        Returns:
            Execution result.
        """
        from src.workflows.domain.execution_exceptions import ActionExecutionError

        start_time = datetime.now(UTC)

        try:
            # Validate configuration
            self._validate_config(context, ["updates"])

            updates = context.action_config["updates"]

            # Simulate API call
            # result = await crm_service.update_contact(
            #     contact_id=context.contact_id,
            #     updates=updates,
            # )

            duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

            return ExecutionResult(
                success=True,
                data={
                    "contact_id": str(context.contact_id),
                    "updates": updates,
                    "fields_updated": len(updates),
                },
                duration_ms=duration_ms,
                should_retry=False,
            )

        except ActionExecutionError:
            raise
        except Exception as e:
            duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            return ExecutionResult(
                success=False,
                error=str(e),
                duration_ms=duration_ms,
                should_retry=True,
                retry_delay_seconds=60,
            )


class AddTagExecutor(BaseActionExecutor):
    """Executor for add_tag action type.

    Adds tags to a contact.
    """

    async def execute(self, context: ActionContext) -> ExecutionResult:
        """Execute add tag action.

        Args:
            context: Action context.

        Returns:
            Execution result.
        """
        from src.workflows.domain.execution_exceptions import ActionExecutionError

        start_time = datetime.now(UTC)

        try:
            # Validate configuration
            self._validate_config(context, ["tags"])

            tags = context.action_config["tags"]

            if not isinstance(tags, list):
                raise ActionExecutionError(
                    "add_tag",
                    "Tags must be a list",
                )

            # Simulate API call
            # result = await crm_service.add_tags(
            #     contact_id=context.contact_id,
            #     tags=tags,
            # )

            duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

            return ExecutionResult(
                success=True,
                data={
                    "contact_id": str(context.contact_id),
                    "tags_added": tags,
                    "count": len(tags),
                },
                duration_ms=duration_ms,
                should_retry=False,
            )

        except ActionExecutionError:
            raise
        except Exception as e:
            duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            return ExecutionResult(
                success=False,
                error=str(e),
                duration_ms=duration_ms,
                should_retry=True,
                retry_delay_seconds=60,
            )


class RemoveTagExecutor(BaseActionExecutor):
    """Executor for remove_tag action type.

    Removes tags from a contact.
    """

    async def execute(self, context: ActionContext) -> ExecutionResult:
        """Execute remove tag action.

        Args:
            context: Action context.

        Returns:
            Execution result.
        """
        from src.workflows.domain.execution_exceptions import ActionExecutionError

        start_time = datetime.now(UTC)

        try:
            # Validate configuration
            self._validate_config(context, ["tags"])

            tags = context.action_config["tags"]

            if not isinstance(tags, list):
                raise ActionExecutionError(
                    "remove_tag",
                    "Tags must be a list",
                )

            # Simulate API call
            # result = await crm_service.remove_tags(
            #     contact_id=context.contact_id,
            #     tags=tags,
            # )

            duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

            return ExecutionResult(
                success=True,
                data={
                    "contact_id": str(context.contact_id),
                    "tags_removed": tags,
                    "count": len(tags),
                },
                duration_ms=duration_ms,
                should_retry=False,
            )

        except ActionExecutionError:
            raise
        except Exception as e:
            duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            return ExecutionResult(
                success=False,
                error=str(e),
                duration_ms=duration_ms,
                should_retry=True,
                retry_delay_seconds=60,
            )


class ActionExecutorFactory:
    """Factory for creating action executors.

    This factory creates the appropriate executor based on
    the action type.
    """

    _executors: dict[str, type[BaseActionExecutor]] = {
        "send_email": SendEmailExecutor,
        "send_sms": SendSMSExecutor,
        "webhook_call": WebhookExecutor,  # Maps to basic webhook executor
        "webhook": WebhookExecutor,  # Legacy name
        "wait_time": WaitTimeExecutor,
        "update_contact": UpdateContactExecutor,
        "add_tag": AddTagExecutor,
        "remove_tag": RemoveTagExecutor,
    }

    @classmethod
    def create(cls, action_type: str) -> BaseActionExecutor:
        """Create executor for action type.

        Args:
            action_type: Type of action.

        Returns:
            Executor instance.

        Raises:
            ActionExecutionError: If action type not supported.
        """
        from src.workflows.domain.execution_exceptions import ActionExecutionError

        executor_class = cls._executors.get(action_type)
        if not executor_class:
            raise ActionExecutionError(
                action_type,
                f"No executor registered for action type: {action_type}",
            )

        return executor_class()

    @classmethod
    def register_executor(
        cls,
        action_type: str,
        executor_class: type[BaseActionExecutor],
    ) -> None:
        """Register a custom executor.

        Args:
            action_type: Action type.
            executor_class: Executor class.
        """
        cls._executors[action_type] = executor_class
