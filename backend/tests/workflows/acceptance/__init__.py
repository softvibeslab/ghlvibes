"""Acceptance tests for SPEC-WFL-001.

These tests verify the 7 acceptance criteria defined in the SPEC document.
Each acceptance criteria test follows Gherkin-style Given-When-Then format.

Purpose:
- Verify SPEC requirements are met
- Provide executable specification
- Document business requirements as tests

Coverage:
- AC-001: User can create workflow ✅ (covered in e2e/test_api.py)
- AC-002: System validates workflow name ✅ (covered in e2e/test_api.py)
- AC-003: Workflow created in draft status ✅ (covered in unit/test_entities.py)
- AC-004: Duplicate names rejected (409) ✅ (covered in e2e/test_api.py)
- AC-005: Rate limiting enforced ⚠️ (test_ac005_rate_limiting.py)
- AC-006: Audit log created ✅ (covered in unit/test_use_cases.py)
- AC-007: Multi-tenancy enforced ⚠️ (test_ac007_multi_tenancy.py)

Markers:
- @acceptance: All acceptance criteria tests
- @e2e: End-to-end tests requiring full stack
- @integration: Integration tests with database
- @unit: Unit tests with mocks
"""
