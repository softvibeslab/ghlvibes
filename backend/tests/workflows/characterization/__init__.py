"""Characterization tests for workflow module.

Characterization tests capture the CURRENT ACTUAL BEHAVIOR of the system.
They serve as a safety net during refactoring by documenting existing behavior.

Unlike traditional tests that verify correct behavior, characterization tests
document what the code actually does - even if it's wrong.

Purpose:
- Preserve baseline behavior during refactoring
- Detect unintended behavior changes
- Document existing behavior for refactoring safety

Usage:
- Run before refactoring to establish baseline
- If test fails after refactoring, either revert or update test intentionally
- Never modify characterization tests without explicit intent

Generated during DDD PRESERVE phase for SPEC-WFL-001.
"""
