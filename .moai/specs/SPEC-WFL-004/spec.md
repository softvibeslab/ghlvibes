# SPEC-WFL-004: Add Condition/Branch

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-004 |
| **Title** | Add Condition/Branch |
| **Module** | workflows |
| **Domain** | automation |
| **Priority** | Critical |
| **Status** | Planned |
| **Created** | 2026-01-26 |
| **Version** | 1.0.0 |

## Overview

This specification defines the conditional branching functionality for the workflow automation system. It enables users to create intelligent workflow paths based on contact data, engagement metrics, and temporal conditions.

---

## EARS Requirements

### REQ-001: If/Else Branch Creation (Event-Driven)

**WHEN** a user adds conditional logic to a workflow canvas
**THEN** the system shall create an if/else branch node with configurable condition criteria
**RESULTING IN** a workflow with two divergent paths (true/false)
**STATE:** branched

**Acceptance Criteria:**
- Branch node appears on canvas with true/false output connectors
- Default condition placeholder prompts configuration
- Both paths allow action step connections
- Visual distinction between true and false branches

---

### REQ-002: Multi-Branch Decision Tree (Event-Driven)

**WHEN** a user creates a multi-branch condition with more than two outcomes
**THEN** the system shall render a decision tree node supporting up to 10 conditional branches plus a default fallback
**RESULTING IN** a workflow with multiple conditional paths evaluated in priority order
**STATE:** multi-branched

**Acceptance Criteria:**
- Support for 2-10 named conditional branches
- Default/else branch for unmatched conditions
- Priority ordering of condition evaluation (top to bottom)
- Visual representation of all branch paths

---

### REQ-003: Split Test Branch (Event-Driven)

**WHEN** a user creates a split test within a workflow
**THEN** the system shall create A/B or multi-variant branches with configurable traffic distribution percentages
**RESULTING IN** contacts randomly distributed across test variants
**STATE:** testing

**Acceptance Criteria:**
- Support 2-5 test variants
- Percentage allocation per variant (must sum to 100%)
- Random distribution algorithm with seed for reproducibility
- Variant performance tracking integration

---

### REQ-004: Contact Field Condition Evaluation (Event-Driven)

**WHEN** the workflow engine evaluates a contact_field_equals condition
**THEN** the system shall compare the contact's field value against the configured target value using the specified operator
**RESULTING IN** routing to the appropriate branch based on comparison result
**STATE:** evaluated

**Supported Operators:**
- `equals` / `not_equals`
- `contains` / `not_contains`
- `starts_with` / `ends_with`
- `is_empty` / `is_not_empty`
- `greater_than` / `less_than` (numeric fields)
- `in_list` / `not_in_list`

**Acceptance Criteria:**
- All standard and custom contact fields accessible
- Case-insensitive string comparisons (configurable)
- Null/empty value handling
- Type coercion for numeric comparisons

---

### REQ-005: Tag-Based Condition (Event-Driven)

**WHEN** the workflow engine evaluates a contact_has_tag condition
**THEN** the system shall check the contact's tag list against the configured tag(s)
**RESULTING IN** routing based on tag presence or absence
**STATE:** evaluated

**Supported Modes:**
- `has_any_tag` - Contact has at least one specified tag
- `has_all_tags` - Contact has all specified tags
- `has_no_tags` - Contact has none of the specified tags
- `has_only_tags` - Contact has exactly the specified tags

**Acceptance Criteria:**
- Multi-tag selection support
- Real-time tag state evaluation
- Tag autocomplete in configuration UI

---

### REQ-006: Pipeline Stage Condition (Event-Driven)

**WHEN** the workflow engine evaluates a pipeline_stage_is condition
**THEN** the system shall check the contact's current pipeline position against the configured stage(s)
**RESULTING IN** routing based on pipeline stage match
**STATE:** evaluated

**Supported Modes:**
- `is_in_stage` - Contact is in specified stage
- `is_not_in_stage` - Contact is not in specified stage
- `is_before_stage` - Contact is in an earlier stage
- `is_after_stage` - Contact is in a later stage

**Acceptance Criteria:**
- Pipeline and stage selection dropdowns
- Multi-stage support for is_in_stage/is_not_in_stage
- Stage ordering awareness for before/after comparisons

---

### REQ-007: Custom Field Value Condition (Event-Driven)

**WHEN** the workflow engine evaluates a custom_field_value condition
**THEN** the system shall retrieve and compare the contact's custom field value using type-appropriate operators
**RESULTING IN** routing based on custom field evaluation
**STATE:** evaluated

**Supported Field Types and Operators:**
| Field Type | Operators |
|------------|-----------|
| Text | equals, contains, starts_with, ends_with, is_empty |
| Number | equals, greater_than, less_than, between |
| Date | equals, before, after, between, in_last_days, in_next_days |
| Dropdown | equals, in_list |
| Checkbox | is_true, is_false |
| Multi-select | has_any, has_all, has_none |

**Acceptance Criteria:**
- Dynamic operator list based on field type
- Date relative expressions (e.g., "in last 7 days")
- Numeric range support for "between" operator

---

### REQ-008: Email Engagement Condition (Event-Driven)

**WHEN** the workflow engine evaluates an email_was_opened or link_was_clicked condition
**THEN** the system shall check the contact's email engagement history for the specified email or campaign
**RESULTING IN** routing based on engagement status
**STATE:** evaluated

**Configuration Options:**
- Specific email reference (by ID or name)
- Campaign-wide engagement check
- Time window for engagement (e.g., "opened in last 24 hours")
- Link URL pattern matching for click tracking

**Acceptance Criteria:**
- Email/campaign selector in configuration
- Time-bounded engagement checks
- Multiple link tracking support
- Engagement count thresholds (e.g., "clicked at least 3 times")

---

### REQ-009: Time-Based Condition (Event-Driven)

**WHEN** the workflow engine evaluates a time_based condition
**THEN** the system shall compare the current time or contact-specific dates against configured criteria
**RESULTING IN** routing based on temporal evaluation
**STATE:** evaluated

**Supported Time Conditions:**
- `current_day_of_week` - Monday, Tuesday, etc.
- `current_time_between` - Time range (e.g., 9:00 AM - 5:00 PM)
- `current_date_between` - Date range
- `contact_date_field` - Compare contact's date field (birthday, anniversary, signup date)
- `days_since_event` - Days since specific contact event

**Acceptance Criteria:**
- Timezone-aware evaluations (account/contact timezone)
- Business hours support
- Holiday calendar integration (optional)

---

### REQ-010: Condition Combination Logic (State-Driven)

**WHILE** a condition node has multiple criteria configured
**THEN** the system shall evaluate criteria using AND/OR logic as specified
**RESULTING IN** combined evaluation result determining branch path
**STATE:** complex_evaluation

**Logic Options:**
- `ALL` (AND) - All conditions must be true
- `ANY` (OR) - At least one condition must be true
- `Custom` - Nested AND/OR groups

**Acceptance Criteria:**
- Visual logic builder for complex conditions
- Condition grouping with parenthetical logic
- Maximum 10 conditions per group
- Maximum 3 nesting levels

---

### REQ-011: Condition Validation (Ubiquitous)

The system **shall** validate all condition configurations before workflow activation to ensure evaluability and prevent runtime errors.

**Validation Rules:**
- Required fields must be populated
- Referenced fields must exist in contact schema
- Referenced tags/pipelines/campaigns must exist
- Numeric values must be valid numbers
- Date values must be valid date formats
- Percentage distributions must sum to 100% for split tests

**Acceptance Criteria:**
- Real-time validation feedback in UI
- Clear error messages with field highlighting
- Block workflow activation on validation failure

---

### REQ-012: Branch Execution Logging (Ubiquitous)

The system **shall** log all condition evaluations and branch decisions for every workflow execution with full audit trail.

**Log Data:**
- Timestamp of evaluation
- Contact ID
- Workflow ID and version
- Condition node ID
- Evaluation inputs (field values at time of evaluation)
- Evaluation result (true/false/branch name)
- Branch path taken

**Acceptance Criteria:**
- Queryable execution logs
- 90-day log retention
- Export capability for compliance

---

### REQ-013: Condition Node Error Handling (Unwanted)

The system **shall not** halt workflow execution when a condition evaluation encounters an error. Instead, the system shall:
- Log the error with full context
- Route to a configured error branch (if defined)
- Route to default/false branch (if no error branch)
- Notify workflow administrator

**Acceptance Criteria:**
- Graceful degradation on evaluation errors
- Error notification to workflow owner
- Error branch configuration option

---

## Technical Specifications

### Database Schema

#### Table: `workflow_conditions`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique condition identifier |
| workflow_id | UUID | FOREIGN KEY | Reference to parent workflow |
| node_id | UUID | NOT NULL | Canvas node identifier |
| condition_type | VARCHAR(50) | NOT NULL | Type of condition |
| branch_type | VARCHAR(20) | NOT NULL | if_else, multi_branch, split_test |
| configuration | JSONB | NOT NULL | Condition-specific settings |
| position_x | INTEGER | NOT NULL | Canvas X position |
| position_y | INTEGER | NOT NULL | Canvas Y position |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |
| created_by | UUID | FOREIGN KEY | Creator user ID |

#### Table: `workflow_branches`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique branch identifier |
| condition_id | UUID | FOREIGN KEY | Parent condition node |
| branch_name | VARCHAR(100) | NOT NULL | Branch display name |
| branch_order | INTEGER | NOT NULL | Evaluation priority |
| is_default | BOOLEAN | DEFAULT FALSE | Default/else branch flag |
| percentage | DECIMAL(5,2) | NULL | Split test percentage |
| next_node_id | UUID | NULL | Connected next node |
| criteria | JSONB | NULL | Branch-specific criteria |

#### Table: `workflow_condition_logs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Log entry identifier |
| execution_id | UUID | FOREIGN KEY | Workflow execution reference |
| condition_id | UUID | FOREIGN KEY | Evaluated condition |
| contact_id | UUID | FOREIGN KEY | Contact being evaluated |
| evaluation_inputs | JSONB | NOT NULL | Input values snapshot |
| evaluation_result | VARCHAR(100) | NOT NULL | Result/branch taken |
| evaluated_at | TIMESTAMP | DEFAULT NOW() | Evaluation timestamp |
| duration_ms | INTEGER | NOT NULL | Evaluation duration |

### API Endpoints

#### Create Condition Node

```
POST /api/v1/workflows/{workflow_id}/conditions
```

**Request Body:**
```json
{
  "node_id": "uuid",
  "condition_type": "contact_field_equals",
  "branch_type": "if_else",
  "configuration": {
    "field": "email",
    "operator": "contains",
    "value": "@gmail.com"
  },
  "position": { "x": 200, "y": 300 }
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "workflow_id": "uuid",
  "node_id": "uuid",
  "condition_type": "contact_field_equals",
  "branch_type": "if_else",
  "branches": [
    { "id": "uuid", "name": "True", "is_default": false },
    { "id": "uuid", "name": "False", "is_default": true }
  ],
  "created_at": "2026-01-26T12:00:00Z"
}
```

#### Update Condition Configuration

```
PATCH /api/v1/workflows/{workflow_id}/conditions/{condition_id}
```

#### Delete Condition Node

```
DELETE /api/v1/workflows/{workflow_id}/conditions/{condition_id}
```

#### Evaluate Condition (Internal)

```
POST /api/v1/internal/conditions/{condition_id}/evaluate
```

**Request Body:**
```json
{
  "contact_id": "uuid",
  "execution_id": "uuid"
}
```

**Response:**
```json
{
  "result": "branch_name",
  "branch_id": "uuid",
  "next_node_id": "uuid",
  "evaluation_details": {
    "inputs": { "field_value": "test@gmail.com" },
    "operator": "contains",
    "target": "@gmail.com",
    "match": true
  }
}
```

### Branch Evaluation Engine Architecture

```
+------------------+     +-------------------+     +------------------+
|  Workflow        |     |  Condition        |     |  Branch          |
|  Execution       |---->|  Evaluator        |---->|  Router          |
|  Engine          |     |  Service          |     |                  |
+------------------+     +-------------------+     +------------------+
                               |
                               v
                    +-------------------+
                    |  Condition        |
                    |  Strategy         |
                    |  Factory          |
                    +-------------------+
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
    +-----------+   +-----------+   +-----------+
    | Field     |   | Tag       |   | Time      |
    | Evaluator |   | Evaluator |   | Evaluator |
    +-----------+   +-----------+   +-----------+
```

**Design Pattern:** Strategy Pattern for condition type handlers

**Components:**
1. **ConditionEvaluatorService** - Orchestrates evaluation flow
2. **ConditionStrategyFactory** - Creates appropriate evaluator based on type
3. **BaseConditionEvaluator** - Abstract base class for evaluators
4. **Type-specific Evaluators** - Implement evaluation logic per condition type

---

## Dependencies

### Internal Dependencies
- SPEC-WFL-001: Create Workflow (workflow canvas foundation)
- SPEC-WFL-002: Configure Trigger (trigger system integration)
- SPEC-WFL-003: Add Action Step (action node connectivity)
- SPEC-WFL-005: Execute Workflow (execution engine integration)
- SPEC-CRM-004: Search and Filter Contacts (contact field access)
- SPEC-CRM-005: Tag Management (tag system access)

### External Dependencies
- PostgreSQL/Supabase for data persistence
- Redis for evaluation caching
- FastAPI for API layer

---

## Security Considerations

### Authorization
- RBAC permission: `workflows.conditions.create`, `workflows.conditions.update`, `workflows.conditions.delete`
- Workflow owner or admin can modify conditions
- Read access follows workflow visibility rules

### Data Protection
- Contact field values in logs should respect PII masking rules
- Condition configurations may contain sensitive business logic
- Audit logs must be tamper-proof

### Input Validation
- Sanitize all user inputs in condition configurations
- Validate field references against actual schema
- Prevent injection through field value comparisons

---

## Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| Condition evaluation latency | < 50ms | P95 |
| Concurrent evaluations | 1000/second | Throughput |
| Complex condition (10 criteria) | < 100ms | P95 |
| Log write latency | < 10ms | P95 |

### Caching Strategy
- Cache contact field values during workflow execution
- Cache tag lists with 5-minute TTL
- Cache pipeline stage definitions

---

## Traceability

| Requirement | Test Case | Component |
|-------------|-----------|-----------|
| REQ-001 | test_if_else_branch_creation | ConditionNodeService |
| REQ-002 | test_multi_branch_creation | ConditionNodeService |
| REQ-003 | test_split_test_distribution | SplitTestEvaluator |
| REQ-004 | test_contact_field_evaluation | FieldConditionEvaluator |
| REQ-005 | test_tag_condition_evaluation | TagConditionEvaluator |
| REQ-006 | test_pipeline_stage_evaluation | PipelineConditionEvaluator |
| REQ-007 | test_custom_field_evaluation | CustomFieldEvaluator |
| REQ-008 | test_email_engagement_evaluation | EngagementConditionEvaluator |
| REQ-009 | test_time_based_evaluation | TimeConditionEvaluator |
| REQ-010 | test_combined_logic_evaluation | CombinedConditionEvaluator |
| REQ-011 | test_condition_validation | ConditionValidator |
| REQ-012 | test_execution_logging | ConditionLogService |
| REQ-013 | test_error_handling | ConditionErrorHandler |

---

## References

- [EARS Syntax Guide](https://www.iaria.org/conferences2009/filesICCGI09/ICCGI_2009_Tutorial_Mavin.pdf)
- [GoHighLevel Workflow Documentation](https://help.gohighlevel.com/support/solutions/articles/48001154478)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [Supabase Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
