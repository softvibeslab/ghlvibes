"""Use case for comparing workflow versions."""

import asyncio
from uuid import UUID
from deepdiff import DeepDiff
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.workflows.application.version_dtos import (
    CompareVersionsResponseDTO,
    VersionActionDiffDTO,
    VersionDiffDetailDTO,
    VersionDiffDTO,
    VersionDiffSummaryDTO,
)
from src.workflows.domain.version_entities import VersionDiff
from src.workflows.domain.version_exceptions import VersionNotFoundError
from src.workflows.infrastructure.version_repository import WorkflowVersionRepository


class CompareVersionsUseCase:
    """Use case for comparing two workflow versions.

    Generates a structured diff showing changes between versions.
    """

    def __init__(self, db: AsyncSession) -> None:
        """Initialize use case.

        Args:
            db: Async database session.
        """
        self.db = db
        self.repository = WorkflowVersionRepository(db)

    async def execute(
        self,
        workflow_id: UUID,
        account_id: UUID,
        from_version: int,
        to_version: int,
    ) -> CompareVersionsResponseDTO:
        """Execute the use case.

        Args:
            workflow_id: Workflow ID.
            account_id: Account ID for tenant isolation.
            from_version: Source version number.
            to_version: Target version number.

        Returns:
            Version comparison response with detailed diff.

        Raises:
            VersionNotFoundError: If either version not found.
        """
        # Fetch both versions concurrently
        from_v, to_v = await asyncio.gather(
            self.repository.get_by_workflow_and_number(workflow_id, account_id, from_version),
            self.repository.get_by_workflow_and_number(workflow_id, account_id, to_version),
        )

        if from_v is None:
            raise VersionNotFoundError(f"Version {from_version}")
        if to_v is None:
            raise VersionNotFoundError(f"Version {to_version}")

        # Generate diff
        diff = self._generate_diff(from_v, to_v)

        # Convert to DTO
        return CompareVersionsResponseDTO(
            from_version=from_version,
            to_version=to_version,
            diff=VersionDiffDetailDTO(
                trigger=VersionDiffDTO(changed=diff.trigger_changed),
                actions=VersionActionDiffDTO(
                    added=diff.added_actions,
                    removed=diff.removed_actions,
                    modified=diff.modified_actions,
                ),
                conditions=VersionActionDiffDTO(
                    added=diff.added_conditions,
                    removed=diff.removed_conditions,
                    modified=diff.modified_conditions,
                ),
            ),
            summary=VersionDiffSummaryDTO(
                total_changes=diff.total_changes,
                breaking_changes=diff.breaking_changes,
            ),
        )

    def _generate_diff(self, from_v: Any, to_v: Any) -> VersionDiff:
        """Generate diff between two versions.

        Args:
            from_v: Source version entity.
            to_v: Target version entity.

        Returns:
            VersionDiff entity with changes.
        """
        # Compare triggers
        trigger_changed = self._compare_triggers(from_v, to_v)

        # Compare actions
        added_actions, removed_actions, modified_actions = self._compare_actions(from_v, to_v)

        # Compare conditions
        added_conditions, removed_conditions, modified_conditions = self._compare_conditions(
            from_v, to_v
        )

        # Calculate totals
        total_changes = (
            (1 if trigger_changed else 0)
            + len(added_actions)
            + len(removed_actions)
            + len(modified_actions)
            + len(added_conditions)
            + len(removed_conditions)
            + len(modified_conditions)
        )

        # Count breaking changes
        breaking_changes = self._count_breaking_changes(
            removed_actions, removed_conditions, trigger_changed
        )

        return VersionDiff(
            from_version_number=from_v.version_number.value,
            to_version_number=to_v.version_number.value,
            trigger_changed=trigger_changed,
            added_actions=added_actions,
            removed_actions=removed_actions,
            modified_actions=modified_actions,
            added_conditions=added_conditions,
            removed_conditions=removed_conditions,
            modified_conditions=modified_conditions,
            total_changes=total_changes,
            breaking_changes=breaking_changes,
        )

    def _compare_triggers(self, from_v: Any, to_v: Any) -> bool:
        """Compare trigger configurations.

        Args:
            from_v: Source version.
            to_v: Target version.

        Returns:
            True if triggers changed, False otherwise.
        """
        if from_v.trigger_type != to_v.trigger_type:
            return True

        if from_v.trigger_config != to_v.trigger_config:
            return True

        return False

    def _compare_actions(
        self, from_v: Any, to_v: Any
    ) -> tuple[list[dict], list[dict], list[dict]]:
        """Compare action configurations.

        Args:
            from_v: Source version.
            to_v: Target version.

        Returns:
            Tuple of (added, removed, modified) actions.
        """
        from_actions = {a.get("id"): a for a in from_v.actions if a.get("id")}
        to_actions = {a.get("id"): a for a in to_v.actions if a.get("id")}

        # Find added actions (in to but not in from)
        added = [a for id, a in to_actions.items() if id not in from_actions]

        # Find removed actions (in from but not in to)
        removed = [a for id, a in from_actions.items() if id not in to_actions]

        # Find modified actions (in both but different)
        modified = []
        for id, to_action in to_actions.items():
            if id in from_actions:
                from_action = from_actions[id]
                diff = DeepDiff(from_action, to_action, ignore_order=True)
                if diff:
                    modified.append(
                        {
                            "id": id,
                            "type": to_action.get("type"),
                            "changes": self._format_changes(diff),
                        }
                    )

        return added, removed, modified

    def _compare_conditions(
        self, from_v: Any, to_v: Any
    ) -> tuple[list[dict], list[dict], list[dict]]:
        """Compare condition configurations.

        Args:
            from_v: Source version.
            to_v: Target version.

        Returns:
            Tuple of (added, removed, modified) conditions.
        """
        from_conditions = {c.get("id"): c for c in from_v.conditions if c.get("id")}
        to_conditions = {c.get("id"): c for c in to_v.conditions if c.get("id")}

        # Find added conditions
        added = [c for id, c in to_conditions.items() if id not in from_conditions]

        # Find removed conditions
        removed = [c for id, c in from_conditions.items() if id not in to_conditions]

        # Find modified conditions
        modified = []
        for id, to_condition in to_conditions.items():
            if id in from_conditions:
                from_condition = from_conditions[id]
                diff = DeepDiff(from_condition, to_condition, ignore_order=True)
                if diff:
                    modified.append(
                        {
                            "id": id,
                            "type": to_condition.get("type"),
                            "changes": self._format_changes(diff),
                        }
                    )

        return added, removed, modified

    def _format_changes(self, diff: DeepDiff) -> dict[str, Any]:
        """Format DeepDiff result for API response.

        Args:
            diff: DeepDiff result.

        Returns:
            Formatted changes dict.
        """
        changes = {}

        if "values_changed" in diff:
            changes["changed_fields"] = list(diff["values_changed"].keys())

        if "type_changes" in diff:
            changes["type_changes"] = list(diff["type_changes"].keys())

        if "dictionary_item_added" in diff:
            changes["added_fields"] = list(diff["dictionary_item_added"])

        if "dictionary_item_removed" in diff:
            changes["removed_fields"] = list(diff["dictionary_item_removed"])

        return changes

    def _count_breaking_changes(
        self, removed_actions: list, removed_conditions: list, trigger_changed: bool
    ) -> int:
        """Count breaking changes.

        Breaking changes include:
        - Removed actions
        - Removed conditions
        - Trigger changes

        Args:
            removed_actions: List of removed actions.
            removed_conditions: List of removed conditions.
            trigger_changed: Whether trigger changed.

        Returns:
            Count of breaking changes.
        """
        count = len(removed_actions) + len(removed_conditions)
        if trigger_changed:
            count += 1
        return count
