"""Domain entities for workflow conditions and branches.

This module defines the core domain entities for conditional branching
in workflows, including condition nodes and branch paths.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Self
from uuid import UUID, uuid4

from src.workflows.domain.condition_exceptions import (
    BranchValidationError,
    ConditionValidationError,
    InvalidPercentageError,
)
from src.workflows.domain.condition_value_objects import (
    BranchCriteria,
    BranchType,
    ConditionConfig,
    LogicOperator,
)


@dataclass
class Branch:
    """Branch entity representing a conditional path.

    A branch defines a path that can be taken when a condition
    is evaluated. Each branch belongs to a condition node and
    can have its own criteria and next action.

    Attributes:
        id: Unique branch identifier.
        condition_id: Parent condition node ID.
        branch_name: Display name for this branch.
        branch_order: Evaluation priority order.
        is_default: Whether this is the default/else branch.
        percentage: Percentage for split test distribution.
        next_node_id: ID of next action in this branch.
        criteria: Branch-specific condition criteria.
    """

    id: UUID
    condition_id: UUID
    branch_name: str
    branch_order: int
    is_default: bool = False
    percentage: float | None = None
    next_node_id: UUID | None = None
    criteria: BranchCriteria | None = None

    def __post_init__(self) -> None:
        """Validate branch state after initialization."""
        # Ensure criteria is BranchCriteria instance
        if self.criteria is None:
            object.__setattr__(self, "criteria", BranchCriteria())
        elif isinstance(self.criteria, dict):
            object.__setattr__(self, "criteria", BranchCriteria.from_dict(self.criteria))

        # Validate percentage for split test branches
        if self.is_default and self.percentage is not None:
            raise BranchValidationError(
                "Default branch cannot have percentage distribution"
            )

    @classmethod
    def create(
        cls,
        condition_id: UUID,
        branch_name: str,
        branch_order: int,
        is_default: bool = False,
        percentage: float | None = None,
        next_node_id: UUID | None = None,
        criteria: BranchCriteria | dict[str, Any] | None = None,
    ) -> Self:
        """Factory method to create a new branch.

        Args:
            condition_id: Parent condition node ID.
            branch_name: Display name for this branch.
            branch_order: Evaluation priority order.
            is_default: Whether this is the default/else branch.
            percentage: Percentage for split tests.
            next_node_id: ID of next action.
            criteria: Branch-specific criteria.

        Returns:
            A new Branch instance.

        Raises:
            BranchValidationError: If configuration is invalid.
        """
        # Convert criteria to object if dict
        if isinstance(criteria, dict):
            criteria = BranchCriteria.from_dict(criteria)
        elif criteria is None:
            criteria = BranchCriteria()

        # Validate percentage range
        if percentage is not None and not 0 <= percentage <= 100:
            raise BranchValidationError(
                f"Percentage must be between 0 and 100, got {percentage}"
            )

        return cls(
            id=uuid4(),
            condition_id=condition_id,
            branch_name=branch_name,
            branch_order=branch_order,
            is_default=is_default,
            percentage=percentage,
            next_node_id=next_node_id,
            criteria=criteria,
        )

    def set_next_node(self, next_node_id: UUID) -> None:
        """Set the next action in this branch.

        Args:
            next_node_id: ID of the next action.
        """
        self.next_node_id = next_node_id

    def update_criteria(self, criteria: BranchCriteria) -> None:
        """Update branch criteria.

        Args:
            criteria: New criteria.
        """
        self.criteria = criteria

    def to_dict(self) -> dict[str, Any]:
        """Convert branch to dictionary representation.

        Returns:
            Dictionary containing all branch attributes.
        """
        return {
            "id": str(self.id),
            "condition_id": str(self.condition_id),
            "branch_name": self.branch_name,
            "branch_order": self.branch_order,
            "is_default": self.is_default,
            "percentage": self.percentage,
            "next_node_id": str(self.next_node_id) if self.next_node_id else None,
            "criteria": self.criteria.to_dict() if self.criteria else None,
        }


@dataclass
class Condition:
    """Condition entity for workflow branching.

    A condition represents a decision point in a workflow where
    execution can branch based on configurable criteria. It supports
    if/else, multi-branch, and split test branching.

    Attributes:
        id: Unique condition identifier.
        workflow_id: ID of the workflow this condition belongs to.
        node_id: Canvas node identifier.
        condition_type: Type of condition to evaluate.
        branch_type: Type of branching (if_else, multi_branch, split_test).
        configuration: Condition-specific settings.
        position_x: Canvas X position.
        position_y: Canvas Y position.
        branches: List of branches for this condition.
        is_active: Whether this condition is enabled.
        created_at: Timestamp when condition was created.
        updated_at: Timestamp of last update.
        created_by: User who created the condition.
        updated_by: User who last updated the condition.
    """

    id: UUID
    workflow_id: UUID
    node_id: UUID
    condition_type: str
    branch_type: BranchType
    configuration: ConditionConfig
    position_x: int
    position_y: int
    branches: list[Branch] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: UUID | None = None
    updated_by: UUID | None = None

    def __post_init__(self) -> None:
        """Validate condition state after initialization."""
        # Ensure branch_type is BranchType instance
        if isinstance(self.branch_type, str):
            object.__setattr__(self, "branch_type", BranchType(self.branch_type))

        # Ensure configuration is ConditionConfig instance
        if isinstance(self.configuration, dict):
            object.__setattr__(
                self,
                "configuration",
                ConditionConfig.from_dict(self.configuration),
            )

        # Validate branches match branch type
        self._validate_branches()

    @classmethod
    def create(
        cls,
        workflow_id: UUID,
        node_id: UUID,
        condition_type: str,
        branch_type: BranchType | str,
        configuration: ConditionConfig | dict[str, Any],
        position_x: int,
        position_y: int,
        created_by: UUID,
        branches: list[Branch] | None = None,
    ) -> Self:
        """Factory method to create a new condition.

        Args:
            workflow_id: ID of the workflow.
            node_id: Canvas node identifier.
            condition_type: Type of condition.
            branch_type: Type of branching.
            configuration: Condition configuration.
            position_x: Canvas X position.
            position_y: Canvas Y position.
            created_by: User creating the condition.
            branches: Optional list of branches.

        Returns:
            A new Condition instance.

        Raises:
            ConditionValidationError: If configuration is invalid.
        """
        # Validate branch_type
        validated_branch_type = (
            branch_type if isinstance(branch_type, BranchType) else BranchType(branch_type)
        )

        # Validate configuration
        validated_config = (
            configuration
            if isinstance(configuration, ConditionConfig)
            else ConditionConfig.from_dict(configuration)
        )

        # Create default branches based on type
        if branches is None:
            branches = cls._create_default_branches(
                validated_branch_type, uuid4()  # temp ID, will be replaced
            )

        now = datetime.now(UTC)

        condition = cls(
            id=uuid4(),
            workflow_id=workflow_id,
            node_id=node_id,
            condition_type=condition_type,
            branch_type=validated_branch_type,
            configuration=validated_config,
            position_x=position_x,
            position_y=position_y,
            branches=branches,
            is_active=True,
            created_at=now,
            updated_at=now,
            created_by=created_by,
            updated_by=created_by,
        )

        # Update branches with actual condition_id
        for branch in condition.branches:
            object.__setattr__(branch, "condition_id", condition.id)

        # Validate final configuration
        errors = condition.validate()
        if errors:
            raise ConditionValidationError(errors)

        return condition

    @staticmethod
    def _create_default_branches(branch_type: BranchType, temp_id: UUID) -> list[Branch]:
        """Create default branches for a given branch type.

        Args:
            branch_type: Type of branching.
            temp_id: Temporary condition ID.

        Returns:
            List of default branches.
        """
        if branch_type == BranchType.IF_ELSE:
            return [
                Branch.create(
                    condition_id=temp_id,
                    branch_name="True",
                    branch_order=0,
                    is_default=False,
                ),
                Branch.create(
                    condition_id=temp_id,
                    branch_name="False",
                    branch_order=1,
                    is_default=True,
                ),
            ]
        elif branch_type == BranchType.MULTI_BRANCH:
            return [
                Branch.create(
                    condition_id=temp_id,
                    branch_name="Branch 1",
                    branch_order=0,
                    is_default=False,
                ),
                Branch.create(
                    condition_id=temp_id,
                    branch_name="Default",
                    branch_order=1,
                    is_default=True,
                ),
            ]
        elif branch_type == BranchType.SPLIT_TEST:
            return [
                Branch.create(
                    condition_id=temp_id,
                    branch_name="Variant A",
                    branch_order=0,
                    is_default=False,
                    percentage=50.0,
                ),
                Branch.create(
                    condition_id=temp_id,
                    branch_name="Variant B",
                    branch_order=1,
                    is_default=False,
                    percentage=50.0,
                ),
            ]
        else:
            return []

    def add_branch(self, branch: Branch) -> None:
        """Add a branch to this condition.

        Args:
            branch: Branch to add.
        """
        branch.condition_id = self.id
        self.branches.append(branch)
        self._touch(self.updated_by or self.created_by)

    def remove_branch(self, branch_id: UUID) -> None:
        """Remove a branch from this condition.

        Args:
            branch_id: ID of branch to remove.
        """
        self.branches = [b for b in self.branches if b.id != branch_id]
        self._touch(self.updated_by or self.created_by)

    def update_branch(self, branch_id: UUID, **updates: Any) -> None:
        """Update a branch.

        Args:
            branch_id: ID of branch to update.
            **updates: Fields to update.
        """
        for branch in self.branches:
            if branch.id == branch_id:
                for key, value in updates.items():
                    setattr(branch, key, value)
                self._touch(self.updated_by or self.created_by)
                return

    def update_configuration(self, configuration: ConditionConfig | dict[str, Any]) -> None:
        """Update condition configuration.

        Args:
            configuration: New configuration.
        """
        if isinstance(configuration, dict):
            self.configuration = ConditionConfig.from_dict(configuration)
        else:
            self.configuration = configuration

        errors = self.validate()
        if errors:
            raise ConditionValidationError(errors)

        self._touch(self.updated_by or self.created_by)

    def validate(self) -> list[str]:
        """Validate condition configuration.

        Returns:
            List of validation error messages (empty if valid).
        """
        errors: list[str] = []

        # Validate branch count
        if self.branch_type == BranchType.IF_ELSE:
            if len(self.branches) != 2:
                errors.append(f"If/else branch must have exactly 2 branches, got {len(self.branches)}")
        elif self.branch_type == BranchType.MULTI_BRANCH:
            if len(self.branches) < 2 or len(self.branches) > 11:
                errors.append(
                    f"Multi-branch must have 2-11 branches (including default), "
                    f"got {len(self.branches)}"
                )
        elif self.branch_type == BranchType.SPLIT_TEST:
            if len(self.branches) < 2 or len(self.branches) > 5:
                errors.append(
                    f"Split test must have 2-5 variants, got {len(self.branches)}"
                )

        # Validate default branch exists
        if self.branch_type in (BranchType.IF_ELSE, BranchType.MULTI_BRANCH):
            if not any(b.is_default for b in self.branches):
                errors.append(f"{self.branch_type.value} must have a default branch")

        # Validate split test percentages
        if self.branch_type == BranchType.SPLIT_TEST:
            total = sum(b.percentage or 0 for b in self.branches)
            if not (99.9 <= total <= 100.1):  # Allow small floating point errors
                errors.append(
                    f"Split test percentages must sum to 100%, got {total:.2f}%"
                )

        # Validate branch orders are unique
        orders = [b.branch_order for b in self.branches]
        if len(orders) != len(set(orders)):
            errors.append("Branch orders must be unique")

        return errors

    def _validate_branches(self) -> None:
        """Validate branch configuration matches branch type."""
        if not self.branches:
            return

        for branch in self.branches:
            if self.branch_type == BranchType.SPLIT_TEST:
                if branch.percentage is None and not branch.is_default:
                    raise BranchValidationError(
                        f"Branch '{branch.branch_name}' in split test must have percentage"
                    )
            elif self.branch_type in (BranchType.IF_ELSE, BranchType.MULTI_BRANCH):
                if branch.percentage is not None:
                    raise BranchValidationError(
                        f"Branch '{branch.branch_name}' in {self.branch_type.value} "
                        "should not have percentage"
                    )

    def activate(self) -> None:
        """Activate the condition."""
        self.is_active = True
        self._touch(self.updated_by or self.created_by)

    def deactivate(self) -> None:
        """Deactivate the condition."""
        self.is_active = False
        self._touch(self.updated_by or self.created_by)

    def _touch(self, updated_by: UUID) -> None:
        """Update timestamp and user.

        Args:
            updated_by: User making the change.
        """
        self.updated_at = datetime.now(UTC)
        self.updated_by = updated_by

    def to_dict(self) -> dict[str, Any]:
        """Convert condition to dictionary representation.

        Returns:
            Dictionary containing all condition attributes.
        """
        return {
            "id": str(self.id),
            "workflow_id": str(self.workflow_id),
            "node_id": str(self.node_id),
            "condition_type": self.condition_type,
            "branch_type": self.branch_type.value,
            "configuration": self.configuration.to_dict(),
            "position_x": self.position_x,
            "position_y": self.position_y,
            "branches": [b.to_dict() for b in self.branches],
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": str(self.created_by) if self.created_by else None,
            "updated_by": str(self.updated_by) if self.updated_by else None,
        }
