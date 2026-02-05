"""Unit tests for workflow value objects.

These tests verify the domain value objects follow business rules
and are properly immutable.
"""

import pytest

from src.workflows.domain.exceptions import InvalidWorkflowNameError
from src.workflows.domain.value_objects import WorkflowName, WorkflowStatus


class TestWorkflowName:
    """Test suite for WorkflowName value object."""

    def test_valid_name_creation(self) -> None:
        """Test creating a valid workflow name."""
        name = WorkflowName("Test Workflow")
        assert str(name) == "Test Workflow"
        assert name.value == "Test Workflow"

    def test_valid_name_with_hyphens(self) -> None:
        """Test name with hyphens is valid."""
        name = WorkflowName("lead-nurturing-workflow")
        assert str(name) == "lead-nurturing-workflow"

    def test_valid_name_with_underscores(self) -> None:
        """Test name with underscores is valid."""
        name = WorkflowName("welcome_email_sequence")
        assert str(name) == "welcome_email_sequence"

    def test_valid_name_minimum_length(self) -> None:
        """Test minimum valid name length (3 characters)."""
        name = WorkflowName("abc")
        assert str(name) == "abc"

    def test_valid_name_maximum_length(self) -> None:
        """Test maximum valid name length (100 characters)."""
        long_name = "a" * 100
        name = WorkflowName(long_name)
        assert str(name) == long_name
        assert len(name.value) == 100

    def test_strips_whitespace(self) -> None:
        """Test that leading/trailing whitespace is stripped."""
        name = WorkflowName("  Test Workflow  ")
        assert str(name) == "Test Workflow"

    def test_invalid_empty_name(self) -> None:
        """Test that empty name raises error."""
        with pytest.raises(InvalidWorkflowNameError) as exc_info:
            WorkflowName("")
        assert "empty" in str(exc_info.value).lower()

    def test_invalid_whitespace_only(self) -> None:
        """Test that whitespace-only name raises error."""
        with pytest.raises(InvalidWorkflowNameError) as exc_info:
            WorkflowName("   ")
        assert "empty" in str(exc_info.value).lower()

    def test_invalid_too_short(self) -> None:
        """Test that name shorter than 3 characters raises error."""
        with pytest.raises(InvalidWorkflowNameError) as exc_info:
            WorkflowName("ab")
        assert "3 characters" in str(exc_info.value)

    def test_invalid_too_long(self) -> None:
        """Test that name longer than 100 characters raises error."""
        with pytest.raises(InvalidWorkflowNameError) as exc_info:
            WorkflowName("a" * 101)
        assert "100 characters" in str(exc_info.value)

    def test_invalid_special_characters(self) -> None:
        """Test that names with special characters raise error."""
        invalid_names = [
            "Test@Workflow",
            "Test#Workflow",
            "Test!Workflow",
            "Test$Workflow",
        ]
        for invalid_name in invalid_names:
            with pytest.raises(InvalidWorkflowNameError):
                WorkflowName(invalid_name)

    def test_invalid_leading_special_char(self) -> None:
        """Test that name starting with special char raises error."""
        with pytest.raises(InvalidWorkflowNameError):
            WorkflowName("-test-workflow")

    def test_invalid_trailing_special_char(self) -> None:
        """Test that name ending with special char raises error."""
        with pytest.raises(InvalidWorkflowNameError):
            WorkflowName("test-workflow-")

    def test_equality_same_value(self) -> None:
        """Test equality between same values."""
        name1 = WorkflowName("Test Workflow")
        name2 = WorkflowName("Test Workflow")
        assert name1 == name2

    def test_equality_with_string(self) -> None:
        """Test equality with string."""
        name = WorkflowName("Test Workflow")
        assert name == "Test Workflow"

    def test_inequality_different_values(self) -> None:
        """Test inequality between different values."""
        name1 = WorkflowName("Test Workflow 1")
        name2 = WorkflowName("Test Workflow 2")
        assert name1 != name2

    def test_hash_for_set_usage(self) -> None:
        """Test that WorkflowName can be used in sets."""
        name1 = WorkflowName("Test Workflow")
        name2 = WorkflowName("Test Workflow")
        name_set = {name1, name2}
        assert len(name_set) == 1

    def test_immutability(self) -> None:
        """Test that WorkflowName is immutable."""
        name = WorkflowName("Test Workflow")
        with pytest.raises(AttributeError):
            name._value = "New Value"  # type: ignore[misc]

    def test_repr(self) -> None:
        """Test string representation."""
        name = WorkflowName("Test Workflow")
        assert repr(name) == "WorkflowName('Test Workflow')"

    def test_factory_method(self) -> None:
        """Test create factory method."""
        name = WorkflowName.create("Test Workflow")
        assert str(name) == "Test Workflow"

    def test_non_string_input(self) -> None:
        """Test that non-string input raises error."""
        with pytest.raises(InvalidWorkflowNameError):
            WorkflowName(123)  # type: ignore[arg-type]


class TestWorkflowStatus:
    """Test suite for WorkflowStatus enum."""

    def test_status_values(self) -> None:
        """Test all status values exist."""
        assert WorkflowStatus.DRAFT.value == "draft"
        assert WorkflowStatus.ACTIVE.value == "active"
        assert WorkflowStatus.PAUSED.value == "paused"

    def test_valid_transitions_from_draft(self) -> None:
        """Test valid transitions from draft status."""
        status = WorkflowStatus.DRAFT
        assert status.can_transition_to(WorkflowStatus.ACTIVE) is True
        assert status.can_transition_to(WorkflowStatus.DRAFT) is True
        assert status.can_transition_to(WorkflowStatus.PAUSED) is False

    def test_valid_transitions_from_active(self) -> None:
        """Test valid transitions from active status."""
        status = WorkflowStatus.ACTIVE
        assert status.can_transition_to(WorkflowStatus.PAUSED) is True
        assert status.can_transition_to(WorkflowStatus.DRAFT) is True
        assert status.can_transition_to(WorkflowStatus.ACTIVE) is False

    def test_valid_transitions_from_paused(self) -> None:
        """Test valid transitions from paused status."""
        status = WorkflowStatus.PAUSED
        assert status.can_transition_to(WorkflowStatus.ACTIVE) is True
        assert status.can_transition_to(WorkflowStatus.DRAFT) is True
        assert status.can_transition_to(WorkflowStatus.PAUSED) is False

    def test_status_is_string_enum(self) -> None:
        """Test that status values are strings."""
        assert isinstance(WorkflowStatus.DRAFT.value, str)
        assert str(WorkflowStatus.DRAFT) == "draft"
