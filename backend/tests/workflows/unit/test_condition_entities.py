"""Unit tests for condition domain entities.

These tests verify the Condition and Branch entities behave correctly
and enforce domain invariants.
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.workflows.domain.condition_entities import Branch, Condition
from src.workflows.domain.condition_exceptions import (
    BranchValidationError,
    ConditionValidationError,
)
from src.workflows.domain.condition_value_objects import (
    BranchCriteria,
    BranchType,
    ConditionConfig,
    ConditionType,
)


class TestBranch:
    """Test suite for Branch entity."""

    @pytest.fixture
    def condition_id(self) -> str:
        """Fixture for condition ID."""
        return uuid4()

    @pytest.fixture
    def next_node_id(self) -> str:
        """Fixture for next node ID."""
        return uuid4()

    def test_create_minimal_branch(self, condition_id) -> None:
        """Test creating branch with minimal data."""
        branch = Branch.create(
            condition_id=condition_id,
            branch_name="True",
            branch_order=0,
        )

        assert branch.condition_id == condition_id
        assert branch.branch_name == "True"
        assert branch.branch_order == 0
        assert branch.is_default is False
        assert branch.percentage is None
        assert branch.next_node_id is None

    def test_create_default_branch(self, condition_id) -> None:
        """Test creating default branch."""
        branch = Branch.create(
            condition_id=condition_id,
            branch_name="False",
            branch_order=1,
            is_default=True,
        )

        assert branch.is_default is True

    def test_create_branch_with_percentage(self, condition_id) -> None:
        """Test creating branch with percentage."""
        branch = Branch.create(
            condition_id=condition_id,
            branch_name="Variant A",
            branch_order=0,
            percentage=50.0,
        )

        assert branch.percentage == 50.0

    def test_create_branch_with_invalid_percentage_low(self, condition_id) -> None:
        """Test creating branch with percentage too low."""
        with pytest.raises(BranchValidationError, match="Percentage must be between 0 and 100"):
            Branch.create(
                condition_id=condition_id,
                branch_name="Test",
                branch_order=0,
                percentage=-1.0,
            )

    def test_create_branch_with_invalid_percentage_high(self, condition_id) -> None:
        """Test creating branch with percentage too high."""
        with pytest.raises(BranchValidationError, match="Percentage must be between 0 and 100"):
            Branch.create(
                condition_id=condition_id,
                branch_name="Test",
                branch_order=0,
                percentage=101.0,
            )

    def test_create_branch_with_next_node(self, condition_id, next_node_id) -> None:
        """Test creating branch with next node."""
        branch = Branch.create(
            condition_id=condition_id,
            branch_name="True",
            branch_order=0,
            next_node_id=next_node_id,
        )

        assert branch.next_node_id == next_node_id

    def test_create_branch_with_criteria(self, condition_id) -> None:
        """Test creating branch with criteria."""
        config = ConditionConfig(
            condition_type=ConditionType.CONTACT_FIELD_EQUALS,
            field="email",
            operator="contains",
            value="@gmail.com",
        )
        criteria = BranchCriteria(config=config)

        branch = Branch.create(
            condition_id=condition_id,
            branch_name="Branch 1",
            branch_order=0,
            criteria=criteria,
        )

        assert branch.criteria is not None
        assert branch.criteria.config.field == "email"

    def test_branch_set_next_node(self, condition_id, next_node_id) -> None:
        """Test setting next node."""
        branch = Branch.create(
            condition_id=condition_id,
            branch_name="True",
            branch_order=0,
        )

        branch.set_next_node(next_node_id)

        assert branch.next_node_id == next_node_id

    def test_branch_update_criteria(self, condition_id) -> None:
        """Test updating branch criteria."""
        branch = Branch.create(
            condition_id=condition_id,
            branch_name="Test",
            branch_order=0,
        )

        new_config = ConditionConfig(
            condition_type=ConditionType.CONTACT_HAS_TAG,
            tags=["lead"],
        )
        new_criteria = BranchCriteria(config=new_config)

        branch.update_criteria(new_criteria)

        assert branch.criteria.config.condition_type == ConditionType.CONTACT_HAS_TAG

    def test_branch_to_dict(self, condition_id, next_node_id) -> None:
        """Test converting branch to dictionary."""
        branch = Branch.create(
            condition_id=condition_id,
            branch_name="True",
            branch_order=0,
            is_default=False,
            next_node_id=next_node_id,
        )

        result = branch.to_dict()

        assert result["condition_id"] == str(condition_id)
        assert result["branch_name"] == "True"
        assert result["branch_order"] == 0
        assert result["is_default"] is False
        assert result["next_node_id"] == str(next_node_id)


class TestCondition:
    """Test suite for Condition entity."""

    @pytest.fixture
    def workflow_id(self) -> str:
        """Fixture for workflow ID."""
        return uuid4()

    @pytest.fixture
    def node_id(self) -> str:
        """Fixture for node ID."""
        return uuid4()

    @pytest.fixture
    def user_id(self) -> str:
        """Fixture for user ID."""
        return uuid4()

    @pytest.fixture
    def basic_config(self) -> ConditionConfig:
        """Fixture for basic condition config."""
        return ConditionConfig(
            condition_type=ConditionType.CONTACT_FIELD_EQUALS,
            field="email",
            operator="contains",
            value="@gmail.com",
        )

    def test_create_if_else_condition(self, workflow_id, node_id, user_id, basic_config) -> None:
        """Test creating if/else condition."""
        condition = Condition.create(
            workflow_id=workflow_id,
            node_id=node_id,
            condition_type="contact_field_equals",
            branch_type=BranchType.IF_ELSE,
            configuration=basic_config,
            position_x=100,
            position_y=200,
            created_by=user_id,
        )

        assert condition.workflow_id == workflow_id
        assert condition.node_id == node_id
        assert condition.branch_type == BranchType.IF_ELSE
        assert len(condition.branches) == 2
        assert condition.branches[0].branch_name == "True"
        assert condition.branches[1].branch_name == "False"
        assert condition.branches[1].is_default is True

    def test_create_multi_branch_condition(self, workflow_id, node_id, user_id, basic_config) -> None:
        """Test creating multi-branch condition."""
        condition = Condition.create(
            workflow_id=workflow_id,
            node_id=node_id,
            condition_type="contact_field_equals",
            branch_type=BranchType.MULTI_BRANCH,
            configuration=basic_config,
            position_x=100,
            position_y=200,
            created_by=user_id,
        )

        assert condition.branch_type == BranchType.MULTI_BRANCH
        assert len(condition.branches) == 2
        assert condition.branches[0].branch_name == "Branch 1"
        assert condition.branches[1].branch_name == "Default"

    def test_create_split_test_condition(self, workflow_id, node_id, user_id, basic_config) -> None:
        """Test creating split test condition."""
        condition = Condition.create(
            workflow_id=workflow_id,
            node_id=node_id,
            condition_type="contact_field_equals",
            branch_type=BranchType.SPLIT_TEST,
            configuration=basic_config,
            position_x=100,
            position_y=200,
            created_by=user_id,
        )

        assert condition.branch_type == BranchType.SPLIT_TEST
        assert len(condition.branches) == 2
        assert condition.branches[0].percentage == 50.0
        assert condition.branches[1].percentage == 50.0

    def test_create_with_dict_config(self, workflow_id, node_id, user_id) -> None:
        """Test creating condition with dict config."""
        config_dict = {
            "condition_type": "contact_field_equals",
            "field": "email",
            "operator": "contains",
            "value": "@gmail.com",
        }

        condition = Condition.create(
            workflow_id=workflow_id,
            node_id=node_id,
            condition_type="contact_field_equals",
            branch_type=BranchType.IF_ELSE,
            configuration=config_dict,
            position_x=100,
            position_y=200,
            created_by=user_id,
        )

        assert condition.configuration.condition_type == ConditionType.CONTACT_FIELD_EQUALS
        assert condition.configuration.field == "email"

    def test_create_with_custom_branches(self, workflow_id, node_id, user_id, basic_config) -> None:
        """Test creating condition with custom branches."""
        branches = [
            Branch.create(
                condition_id=uuid4(),
                branch_name="Custom Branch 1",
                branch_order=0,
            ),
            Branch.create(
                condition_id=uuid4(),
                branch_name="Custom Default",
                branch_order=1,
                is_default=True,
            ),
        ]

        condition = Condition.create(
            workflow_id=workflow_id,
            node_id=node_id,
            condition_type="contact_field_equals",
            branch_type=BranchType.MULTI_BRANCH,
            configuration=basic_config,
            position_x=100,
            position_y=200,
            created_by=user_id,
            branches=branches,
        )

        assert len(condition.branches) == 2
        assert condition.branches[0].branch_name == "Custom Branch 1"

    def test_add_branch(self, workflow_id, node_id, user_id, basic_config) -> None:
        """Test adding a branch to condition."""
        condition = Condition.create(
            workflow_id=workflow_id,
            node_id=node_id,
            condition_type="contact_field_equals",
            branch_type=BranchType.MULTI_BRANCH,
            configuration=basic_config,
            position_x=100,
            position_y=200,
            created_by=user_id,
        )

        initial_count = len(condition.branches)
        new_branch = Branch.create(
            condition_id=condition.id,
            branch_name="New Branch",
            branch_order=2,
        )

        condition.add_branch(new_branch)

        assert len(condition.branches) == initial_count + 1
        assert new_branch.condition_id == condition.id

    def test_remove_branch(self, workflow_id, node_id, user_id, basic_config) -> None:
        """Test removing a branch from condition."""
        condition = Condition.create(
            workflow_id=workflow_id,
            node_id=node_id,
            condition_type="contact_field_equals",
            branch_type=BranchType.MULTI_BRANCH,
            configuration=basic_config,
            position_x=100,
            position_y=200,
            created_by=user_id,
        )

        initial_count = len(condition.branches)
        branch_to_remove = condition.branches[0]

        condition.remove_branch(branch_to_remove.id)

        assert len(condition.branches) == initial_count - 1
        assert branch_to_remove not in condition.branches

    def test_update_branch(self, workflow_id, node_id, user_id, basic_config) -> None:
        """Test updating a branch."""
        condition = Condition.create(
            workflow_id=workflow_id,
            node_id=node_id,
            condition_type="contact_field_equals",
            branch_type=BranchType.MULTI_BRANCH,
            configuration=basic_config,
            position_x=100,
            position_y=200,
            created_by=user_id,
        )

        branch = condition.branches[0]
        condition.update_branch(branch.id, branch_name="Updated Name")

        assert branch.branch_name == "Updated Name"

    def test_update_configuration(self, workflow_id, node_id, user_id, basic_config) -> None:
        """Test updating condition configuration."""
        condition = Condition.create(
            workflow_id=workflow_id,
            node_id=node_id,
            condition_type="contact_field_equals",
            branch_type=BranchType.IF_ELSE,
            configuration=basic_config,
            position_x=100,
            position_y=200,
            created_by=user_id,
        )

        new_config = ConditionConfig(
            condition_type=ConditionType.CONTACT_HAS_TAG,
            tags=["lead"],
        )

        condition.update_configuration(new_config)

        assert condition.configuration.condition_type == ConditionType.CONTACT_HAS_TAG

    def test_validate_if_else_branch_count(self, workflow_id, node_id, user_id, basic_config) -> None:
        """Test validation rejects if/else with wrong branch count."""
        branches = [
            Branch.create(
                condition_id=uuid4(),
                branch_name="Only",
                branch_order=0,
            ),
        ]

        with pytest.raises(ConditionValidationError) as exc_info:
            Condition.create(
                workflow_id=workflow_id,
                node_id=node_id,
                condition_type="contact_field_equals",
                branch_type=BranchType.IF_ELSE,
                configuration=basic_config,
                position_x=100,
                position_y=200,
                created_by=user_id,
                branches=branches,
            )

        assert "exactly 2 branches" in str(exc_info.value)

    def test_validate_split_test_percentages(self, workflow_id, node_id, user_id, basic_config) -> None:
        """Test validation rejects split test with invalid percentages."""
        branches = [
            Branch.create(
                condition_id=uuid4(),
                branch_name="A",
                branch_order=0,
                percentage=30.0,
            ),
            Branch.create(
                condition_id=uuid4(),
                branch_name="B",
                branch_order=1,
                percentage=50.0,
            ),
        ]

        with pytest.raises(ConditionValidationError) as exc_info:
            Condition.create(
                workflow_id=workflow_id,
                node_id=node_id,
                condition_type="contact_field_equals",
                branch_type=BranchType.SPLIT_TEST,
                configuration=basic_config,
                position_x=100,
                position_y=200,
                created_by=user_id,
                branches=branches,
            )

        assert "sum to 100%" in str(exc_info.value).lower()

    def test_activate_condition(self, workflow_id, node_id, user_id, basic_config) -> None:
        """Test activating a condition."""
        condition = Condition.create(
            workflow_id=workflow_id,
            node_id=node_id,
            condition_type="contact_field_equals",
            branch_type=BranchType.IF_ELSE,
            configuration=basic_config,
            position_x=100,
            position_y=200,
            created_by=user_id,
        )
        condition.is_active = False
        initial_version = condition.updated_at

        condition.activate()

        assert condition.is_active is True
        assert condition.updated_at > initial_version

    def test_deactivate_condition(self, workflow_id, node_id, user_id, basic_config) -> None:
        """Test deactivating a condition."""
        condition = Condition.create(
            workflow_id=workflow_id,
            node_id=node_id,
            condition_type="contact_field_equals",
            branch_type=BranchType.IF_ELSE,
            configuration=basic_config,
            position_x=100,
            position_y=200,
            created_by=user_id,
        )
        initial_version = condition.updated_at

        condition.deactivate()

        assert condition.is_active is False
        assert condition.updated_at > initial_version

    def test_to_dict(self, workflow_id, node_id, user_id, basic_config) -> None:
        """Test converting condition to dictionary."""
        condition = Condition.create(
            workflow_id=workflow_id,
            node_id=node_id,
            condition_type="contact_field_equals",
            branch_type=BranchType.IF_ELSE,
            configuration=basic_config,
            position_x=100,
            position_y=200,
            created_by=user_id,
        )

        result = condition.to_dict()

        assert result["workflow_id"] == str(workflow_id)
        assert result["node_id"] == str(node_id)
        assert result["branch_type"] == "if_else"
        assert result["position_x"] == 100
        assert result["position_y"] == 200
        assert len(result["branches"]) == 2
        assert "created_at" in result
        assert "updated_at" in result
