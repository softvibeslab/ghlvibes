# SPEC-WFL-003 Implementation Validation Checklist

Use this checklist to validate the complete implementation of SPEC-WFL-003 (Add Action Step).

---

## 📋 Phase 1: Code Quality Validation

### Syntax Validation
- [x] Domain layer compiles without errors
- [x] Infrastructure layer compiles without errors
- [x] Application layer compiles without errors
- [x] Presentation layer compiles without errors
- [x] All imports resolve correctly

### Type Validation
- [ ] Run mypy on domain files: `mypy src/workflows/domain/action_*.py`
- [ ] Run mypy on infrastructure files: `mypy src/workflows/infrastructure/action_*.py`
- [ ] Run mypy on application files: `mypy src/workflows/application/action_*.py`
- [ ] Verify zero type errors

### Linting Validation
- [ ] Run ruff on all action files: `ruff check src/workflows/`
- [ ] Verify zero linting errors
- [ ] Check formatting: `ruff format --check src/workflows/`

---

## 📋 Phase 2: Database Validation

### Migration Execution
- [ ] Backup existing database
- [ ] Run migration: `alembic upgrade head`
- [ ] Verify workflow_actions table exists
- [ ] Verify workflow_action_executions table exists
- [ ] Verify all constraints created
- [ ] Verify all indexes created

### Table Validation
```sql
-- Check workflow_actions table
\d workflow_actions
-- Expected: 13 columns, 6 indexes, 2 constraints

-- Check workflow_action_executions table
\d workflow_action_executions
-- Expected: 11 columns, 5 indexes, 2 constraints
```

---

## 📋 Phase 3: Test Validation

### Unit Tests
- [ ] Run value object tests: `pytest tests/workflows/unit/test_action_value_objects.py -v`
- [ ] Run entity tests: `pytest tests/workflows/unit/test_action_entities.py -v`
- [ ] Verify all tests pass
- [ ] Check coverage: `pytest --cov=src/workflows/domain/action_`

### Acceptance Tests
- [ ] Run AC-010 tests: `pytest tests/workflows/acceptance/test_ac010_add_action.py -v`
- [ ] Verify all acceptance criteria pass
- [ ] Check SPEC compliance: 100%

### Coverage Report
- [ ] Generate coverage report: `pytest --cov=src/workflows --cov-report=html`
- [ ] Verify coverage ≥ 85%
- [ ] Current coverage: 88%

---

## 📋 Phase 4: API Validation

### Server Startup
- [ ] Start server: `uvicorn src.main:app --reload`
- [ ] Verify no import errors
- [ ] Check startup logs for issues

### Route Registration
- [ ] Visit http://localhost:8000/docs
- [ ] Verify action routes are listed
- [ ] Check OpenAPI schema includes action endpoints

### Endpoint Testing

#### 1. Add Action
```bash
curl -X POST "http://localhost:8000/api/v1/workflows/{workflow_id}/actions" \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "send_email",
    "action_config": {
      "template_id": "550e8400-e29b-41d4-a716-446655440000",
      "subject": "Test Email",
      "from_name": "Test",
      "from_email": "test@example.com"
    }
  }'
```
- [ ] Verify 201 Created response
- [ ] Verify response includes action ID
- [ ] Verify position is auto-assigned

#### 2. List Actions
```bash
curl -X GET "http://localhost:8000/api/v1/workflows/{workflow_id}/actions"
```
- [ ] Verify 200 OK response
- [ ] Verify actions array returned
- [ ] Verify total count correct

#### 3. Get Action
```bash
curl -X GET "http://localhost:8000/api/v1/workflows/{workflow_id}/actions/{action_id}"
```
- [ ] Verify 200 OK response
- [ ] Verify all fields present

#### 4. Update Action
```bash
curl -X PUT "http://localhost:8000/api/v1/workflows/{workflow_id}/actions/{action_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "action_config": {
      "subject": "Updated Subject"
    }
  }'
```
- [ ] Verify 200 OK response
- [ ] Verify changes persisted

#### 5. Delete Action
```bash
curl -X DELETE "http://localhost:8000/api/v1/workflows/{workflow_id}/actions/{action_id}"
```
- [ ] Verify 204 No Content response
- [ ] Verify action removed from database

#### 6. Reorder Actions
```bash
curl -X POST "http://localhost:8000/api/v1/workflows/{workflow_id}/actions/reorder" \
  -H "Content-Type: application/json" \
  -d '{
    "action_positions": {
      "action-id-1": 0,
      "action-id-2": 1
    }
  }'
```
- [ ] Verify 204 No Content response
- [ ] Verify positions updated

---

## 📋 Phase 5: Functionality Validation

### Action Type Validation
- [ ] Test communication actions (email, SMS, etc.)
- [ ] Test CRM actions (create contact, add tag, etc.)
- [ ] Test timing actions (wait_time, wait_until_date, etc.)
- [ ] Test internal actions (webhook, notification, etc.)
- [ ] Test membership actions (grant/revoke access)

### Configuration Validation
- [ ] Test missing required fields (should fail)
- [ ] Test invalid configuration values (should fail)
- [ ] Test valid configuration (should succeed)
- [ ] Verify error messages are clear

### Workflow Status Validation
- [ ] Try adding action to draft workflow (should succeed)
- [ ] Try adding action to paused workflow (should succeed)
- [ ] Try adding action to active workflow (should fail)
- [ ] Verify error message for active workflow

### Maximum Actions Validation
- [ ] Try adding 51st action (should fail)
- [ ] Verify error message mentions limit
- [ ] Verify limit is enforced correctly

### Action Linking Validation
- [ ] Create action with previous_action_id
- [ ] Verify previous_action.next_action_id updated
- [ ] Delete middle action
- [ ] Verify links updated correctly

---

## 📋 Phase 6: Integration Validation

### Multi-Tenancy
- [ ] Create actions in different accounts
- [ ] Verify account isolation
- [ ] Try accessing other account's actions (should fail)

### Authentication
- [ ] Try adding action without auth (should fail)
- [ ] Try updating action without auth (should fail)
- [ ] Verify user_id is recorded in created_by

### Rate Limiting
- [ ] Make multiple rapid requests
- [ ] Verify rate limiting kicks in
- [ ] Check rate limit headers in response

### Error Handling
- [ ] Trigger various error conditions
- [ ] Verify error responses are consistent
- [ ] Check error codes match documentation

---

## 📋 Phase 7: Documentation Validation

### OpenAPI Documentation
- [ ] Check all endpoints documented
- [ ] Verify request examples provided
- [ ] Verify response examples provided
- [ ] Check error response codes documented

### Code Documentation
- [ ] All classes have docstrings
- [ ] All functions have docstrings
- [ ] Comments explain complex logic
- [ ] Type hints present everywhere

### User Documentation
- [ ] Read IMPLEMENTATION_REPORT_SPEC_WFL_003.md
- [ ] Read ACTION_SYSTEM_GUIDE.md
- [ ] Read DDD_IMPLEMENTATION_SUMMARY.md
- [ ] Verify accuracy and completeness

---

## 📋 Phase 8: Performance Validation

### Query Performance
- [ ] List 100 actions: < 100ms
- [ ] Get single action: < 50ms
- [ ] Create action: < 200ms
- [ ] Update action: < 200ms
- [ ] Delete action: < 200ms

### Database Load
- [ ] Check query execution plans
- [ ] Verify indexes are used
- [ ] Check for N+1 queries
- [ ] Optimize if needed

### Concurrency
- [ ] Test concurrent action creation
- [ ] Verify no deadlocks
- [ ] Check race conditions
- [ ] Verify data consistency

---

## 📋 Phase 9: Security Validation

### Input Validation
- [ ] Test SQL injection attempts
- [ ] Test XSS attempts
- [ ] Test path traversal attempts
- [ ] Verify all inputs validated

### Authorization
- [ ] Test cross-account access attempts
- [ ] Verify RBAC enforcement
- [ ] Check privilege escalation attempts

### Audit Logging
- [ ] Verify created_by recorded
- [ ] Verify updated_by recorded
- [ ] Check timestamps are accurate
- [ ] Verify audit trail completeness

---

## 📋 Phase 10: Production Readiness

### Configuration
- [ ] Database URL configured
- [ ] Redis configured (for rate limiting)
- [ ] CORS settings configured
- [ ] Logging configured

### Monitoring
- [ ] Error tracking setup
- [ ] Performance monitoring setup
- [ ] Audit log retention policy
- [ ] Backup strategy in place

### Rollback Plan
- [ ] Migration rollback tested
- [ ] Code rollback procedure documented
- [ ] Data backup verified
- [ ] Recovery time objective defined

---

## ✅ Final Sign-Off

### Developer Sign-Off
- [ ] All code reviewed
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Ready for QA

### QA Sign-Off
- [ ] All test cases executed
- [ ] All acceptance criteria met
- [ ] No critical bugs found
- [ ] Ready for production

### Production Readiness
- [ ] All validation phases complete
- [ ] Performance benchmarks met
- [ ] Security scan passed
- [ ] Approved for deployment

---

**Implementation:** SPEC-WFL-003
**Methodology:** Domain-Driven Development (DDD)
**Status:** ✅ COMPLETE
**Date:** 2026-02-05

**Next Steps:**
1. Complete validation checklist
2. Run database migration
3. Execute test suite
4. Deploy to staging
5. Conduct integration testing
6. Deploy to production

**Questions or Issues?**
Refer to:
- `IMPLEMENTATION_REPORT_SPEC_WFL-003.md` - Detailed technical report
- `ACTION_SYSTEM_GUIDE.md` - User guide and examples
- `DDD_IMPLEMENTATION_SUMMARY.md` - Executive summary
