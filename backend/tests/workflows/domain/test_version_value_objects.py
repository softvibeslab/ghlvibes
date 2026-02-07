"""Unit tests for workflow version value objects."""

import pytest

from src.workflows.domain.version_value_objects import (
    ChangeSummary,
    VersionNumber,
    VersionStatus,
)
from src.workflows.domain.exceptions import ValidationError


class TestVersionNumber:
    """Test suite for VersionNumber value object."""

    def test_create_valid_version_number(self):
        """Test creating valid version numbers."""
        vn = VersionNumber(1)
        assert vn.value == 1

        vn = VersionNumber(100)
        assert vn.value == 100

        vn = VersionNumber(1000)
        assert vn.value == 1000

    def test_version_number_minimum(self):
        """Test version number minimum constraint."""
        with pytest.raises(ValidationError, match="at least 1"):
            VersionNumber(0)

        with pytest.raises(ValidationError, match="at least 1"):
            VersionNumber(-1)

    def test_version_number_maximum(self):
        """Test version number maximum constraint."""
        with pytest.raises(ValidationError, match="cannot exceed 1000"):
            VersionNumber(1001)

    def test_version_number_must_be_integer(self):
        """Test version number must be integer."""
        with pytest.raises(ValidationError, match="must be an integer"):
            VersionNumber("1")  # type: ignore

    def test_version_number_string_representation(self):
        """Test version number string representation."""
        vn = VersionNumber(42)
        assert str(vn) == "v42"

    def test_version_number_increment(self):
        """Test version number increment."""
        vn1 = VersionNumber(1)
        vn2 = vn1.increment()
        assert vn2.value == 2

        # Original is immutable
        assert vn1.value == 1


class TestChangeSummary:
    """Test suite for ChangeSummary value object."""

    def test_create_valid_summary(self):
        """Test creating valid change summary."""
        cs = ChangeSummary("Fixed bug in email action")
        assert cs.text == "Fixed bug in email action"

    def test_change_summary_max_length(self):
        """Test change summary max length constraint."""
        # 500 characters should be valid
        long_text = "a" * 500
        cs = ChangeSummary(long_text)
        assert len(cs.text) == 500

        # 501 characters should fail
        too_long = "a" * 501
        with pytest.raises(ValidationError, match="cannot exceed 500"):
            ChangeSummary(too_long)

    def test_change_summary_must_be_string(self):
        """Test change summary must be string."""
        with pytest.raises(ValidationError, match="must be a string"):
            ChangeSummary(123)  # type: ignore

    def test_change_summary_empty_check(self):
        """Test change summary empty check."""
        # Empty string
        cs = ChangeSummary("")
        assert cs.is_empty is True

        # Whitespace only
        cs = ChangeSummary("   ")
        assert cs.is_empty is True

        # Non-empty
        cs = ChangeSummary("Added new action")
        assert cs.is_empty is False


class TestVersionStatus:
    """Test suite for VersionStatus enum."""

    def test_status_values(self):
        """Test status enum values."""
        assert VersionStatus.DRAFT.value == "draft"
        assert VersionStatus.ACTIVE.value == "active"
        assert VersionStatus.ARCHIVED.value == "archived"

    def test_status_comparison(self):
        """Test status comparison."""
        status1 = VersionStatus.DRAFT
        status2 = VersionStatus.DRAFT
        status3 = VersionStatus.ACTIVE

        assert status1 == status2
        assert status1 != status3
