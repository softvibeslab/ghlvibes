# SPEC-WFL-008: Workflow Templates

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-008 |
| **Title** | Workflow Templates |
| **Module** | workflows |
| **Domain** | automation |
| **Priority** | Medium |
| **Status** | Planned |
| **Created** | 2026-01-26 |
| **Version** | 1.0.0 |

---

## Overview

This specification defines the Workflow Templates system for the GoHighLevel Clone platform. The templates system enables users to quickly create new workflows from pre-built templates, reducing setup time and providing best-practice automation patterns for common marketing and sales scenarios.

### Business Value

- **Reduced Time-to-Value:** Users can deploy sophisticated automation workflows in minutes instead of hours
- **Best Practices Built-In:** Templates encode proven marketing automation patterns
- **Consistency:** Ensures standardized workflow structures across the organization
- **Onboarding Acceleration:** New users can immediately leverage automation without expertise

---

## EARS Requirements

### REQ-001: Template Library Access (Ubiquitous)

**Pattern:** Ubiquitous Requirement

The system shall always provide access to the workflow template library from the workflow creation interface, displaying available templates organized by category with preview capabilities.

**Rationale:** Users need immediate access to templates when creating workflows to accelerate their automation setup process.

---

### REQ-002: Template Selection (Event-Driven)

**Pattern:** Event-Driven Requirement

**WHEN** a user selects a workflow template from the library
**THEN** the system shall display a detailed preview including:
- Template name and description
- Trigger type and configuration
- Action sequence visualization
- Estimated completion rate
- Required integrations and dependencies

**Rationale:** Users need comprehensive information before committing to a template to ensure it meets their needs.

---

### REQ-003: Template Cloning (Event-Driven)

**Pattern:** Event-Driven Requirement

**WHEN** a user confirms template selection by clicking "Use Template"
**THEN** the system shall:
1. Create a new workflow instance copying all template configuration
2. Generate a unique workflow ID (UUID v4)
3. Set the workflow status to "draft"
4. Preserve all action steps, conditions, and timing settings
5. Redirect user to the workflow editor with the cloned workflow loaded

**Result:** New workflow based on template ready for customization
**State:** cloned

**Rationale:** The cloning process must preserve all template complexity while creating an independent, editable workflow instance.

---

### REQ-004: Template Customization (Event-Driven)

**Pattern:** Event-Driven Requirement

**WHEN** a user edits a cloned template workflow
**THEN** the system shall allow modification of:
- Workflow name and description
- Trigger conditions and filters
- Action step content (email copy, SMS text, etc.)
- Timing delays and wait conditions
- Conditional branch criteria
- Goal tracking settings

**Rationale:** Templates serve as starting points; users must be able to fully customize to their specific needs.

---

### REQ-005: Template Category Filtering (Event-Driven)

**Pattern:** Event-Driven Requirement

**WHEN** a user selects a template category filter
**THEN** the system shall display only templates belonging to the selected category:

| Category | Description | Use Cases |
|----------|-------------|-----------|
| `lead_nurturing` | Multi-touch sequences for converting leads | New lead follow-up, drip campaigns |
| `appointment_reminder` | Automated appointment confirmation and reminders | Reduce no-shows, booking confirmations |
| `onboarding` | Welcome sequences for new customers | Product orientation, feature introduction |
| `re_engagement` | Win-back campaigns for inactive contacts | Dormant lead activation, churn prevention |
| `review_request` | Automated review solicitation | Post-service feedback, testimonial collection |
| `birthday_celebration` | Personalized birthday/anniversary outreach | Customer appreciation, loyalty building |

**Rationale:** Category filtering helps users quickly find relevant templates among potentially large template libraries.

---

### REQ-006: Template Search (Event-Driven)

**Pattern:** Event-Driven Requirement

**WHEN** a user enters a search query in the template library
**THEN** the system shall return templates matching:
- Template name (fuzzy match)
- Template description (full-text search)
- Template tags and keywords
- Action types included in template

**Rationale:** Search functionality enables efficient template discovery beyond category browsing.

---

### REQ-007: Template Preview Mode (Event-Driven)

**Pattern:** Event-Driven Requirement

**WHEN** a user clicks "Preview" on a template
**THEN** the system shall display a read-only visualization showing:
- Complete workflow canvas with all steps
- Trigger configuration details
- Each action step with sample content
- Conditional branches and their criteria
- Wait steps with timing information
- Goal settings if configured

**Rationale:** Visual preview helps users understand template complexity and flow before cloning.

---

### REQ-008: Template Metadata Persistence (State-Driven)

**Pattern:** State-Driven Requirement

**IF** a workflow was created from a template
**THEN** the system shall maintain a reference to the source template including:
- Original template ID
- Template version at time of cloning
- Clone timestamp
- Original template category

**Rationale:** Tracking template lineage enables analytics on template usage and potential update notifications.

---

### REQ-009: Custom Template Creation (Event-Driven)

**Pattern:** Event-Driven Requirement

**WHEN** a user clicks "Save as Template" on an existing workflow
**THEN** the system shall:
1. Prompt for template name and description
2. Prompt for category selection
3. Create a template copy with sanitized content (remove PII)
4. Store template in account's custom template library
5. Optionally share with sub-accounts (agency feature)

**Rationale:** Users should be able to create reusable templates from their successful workflows.

---

### REQ-010: Template Validation (Event-Driven)

**Pattern:** Event-Driven Requirement

**WHEN** a template is being saved (system or custom)
**THEN** the system shall validate:
- At least one trigger is configured
- At least one action step exists
- All referenced integrations are specified
- No broken references or orphaned steps
- All required fields have default values or placeholders

**Rationale:** Templates must be complete and functional to provide value when cloned.

---

### REQ-011: Template Import Protection (Unwanted Behavior)

**Pattern:** Unwanted Behavior Requirement

The system shall NOT allow template cloning when:
- Required integrations are not available in the account
- The user lacks permission to create workflows
- The template contains deprecated action types
- The account has reached workflow limits

**Rationale:** Preventing invalid template usage avoids user frustration and maintains system integrity.

---

### REQ-012: Template Versioning (Optional)

**Pattern:** Optional Requirement

**WHERE** template versioning is enabled
**THEN** the system shall:
- Track template version history
- Notify users of available template updates
- Provide option to diff current workflow against updated template
- Allow selective merge of template updates

**Rationale:** Template versioning enables continuous improvement of templates while respecting user customizations.

---

## Constraints

### Technical Constraints

| Constraint | Specification |
|------------|---------------|
| **Template Storage** | PostgreSQL/Supabase with JSONB for workflow configuration |
| **Clone Performance** | Template cloning must complete in under 2 seconds |
| **Preview Rendering** | Template preview must render in under 500ms |
| **Search Latency** | Template search must return results in under 200ms |
| **Max Template Size** | Single template limited to 100 action steps |

### Business Constraints

| Constraint | Specification |
|------------|---------------|
| **System Templates** | Platform provides minimum 20 pre-built templates |
| **Custom Templates** | Standard accounts limited to 10 custom templates |
| **Agency Templates** | Agency accounts can create unlimited shared templates |
| **Template Sharing** | Custom templates can only be shared within account hierarchy |

### Security Constraints

| Constraint | Specification |
|------------|---------------|
| **Content Sanitization** | Custom templates must have PII removed before sharing |
| **Access Control** | Template access follows account permission hierarchy |
| **Audit Logging** | All template operations logged for compliance |

---

## Dependencies

### Internal Dependencies

| Dependency | SPEC ID | Description |
|------------|---------|-------------|
| Create Workflow | SPEC-WFL-001 | Base workflow creation functionality |
| Configure Trigger | SPEC-WFL-002 | Trigger configuration system |
| Add Action Step | SPEC-WFL-003 | Action step management |
| Add Condition/Branch | SPEC-WFL-004 | Conditional logic support |
| Execute Workflow | SPEC-WFL-005 | Workflow execution engine |
| Goal Tracking | SPEC-WFL-007 | Goal configuration for templates |

### External Dependencies

| Dependency | Purpose |
|------------|---------|
| PostgreSQL/Supabase | Template storage and retrieval |
| Redis | Template caching for performance |
| Elasticsearch | Full-text template search |

---

## Data Model

### Template Entity

```
WorkflowTemplate {
    id: UUID (PK)
    account_id: UUID (FK, nullable for system templates)
    name: VARCHAR(255)
    description: TEXT
    category: ENUM(lead_nurturing, appointment_reminder, onboarding, re_engagement, review_request, birthday_celebration, custom)
    is_system_template: BOOLEAN
    is_shared: BOOLEAN (for agency sharing)
    version: INTEGER
    workflow_config: JSONB
    required_integrations: VARCHAR[]
    tags: VARCHAR[]
    usage_count: INTEGER
    average_completion_rate: DECIMAL
    created_at: TIMESTAMP
    updated_at: TIMESTAMP
    created_by: UUID (FK)
}
```

### Template Usage Tracking

```
TemplateUsage {
    id: UUID (PK)
    template_id: UUID (FK)
    workflow_id: UUID (FK)
    account_id: UUID (FK)
    cloned_at: TIMESTAMP
    template_version: INTEGER
}
```

### Template Category Statistics

```
TemplateCategoryStats {
    category: ENUM
    total_templates: INTEGER
    total_usage: INTEGER
    avg_completion_rate: DECIMAL
}
```

---

## API Endpoints

### Template Library

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/workflow-templates` | List all available templates |
| GET | `/api/v1/workflow-templates/:id` | Get template details |
| GET | `/api/v1/workflow-templates/:id/preview` | Get template preview data |
| POST | `/api/v1/workflow-templates/:id/clone` | Clone template to new workflow |

### Custom Templates

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/workflow-templates` | Create custom template |
| PUT | `/api/v1/workflow-templates/:id` | Update custom template |
| DELETE | `/api/v1/workflow-templates/:id` | Delete custom template |
| POST | `/api/v1/workflow-templates/:id/share` | Share template with sub-accounts |

### Template Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/workflow-templates/search` | Search templates |
| GET | `/api/v1/workflow-templates/categories` | List categories with counts |

---

## Error Handling

| Error Code | Condition | User Message |
|------------|-----------|--------------|
| TEMPLATE_NOT_FOUND | Template ID does not exist | "Template not found. It may have been removed." |
| TEMPLATE_CLONE_FAILED | Clone operation failed | "Unable to create workflow from template. Please try again." |
| MISSING_INTEGRATION | Required integration not available | "This template requires {integration} which is not connected." |
| TEMPLATE_LIMIT_REACHED | Custom template quota exceeded | "You have reached your template limit. Upgrade to create more." |
| WORKFLOW_LIMIT_REACHED | Workflow quota exceeded | "You have reached your workflow limit." |
| INVALID_TEMPLATE | Template validation failed | "Template is invalid and cannot be used." |

---

## Traceability

| Artifact | Reference |
|----------|-----------|
| Product Requirement | Workflows Module - Pre-built workflow templates |
| Technical Stack | FastAPI, PostgreSQL/Supabase, Redis |
| Quality Framework | TRUST 5 (Tested, Readable, Unified, Secured, Trackable) |
| Test Plan | acceptance.md |
| Implementation Plan | plan.md |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-26 | SPEC Builder | Initial specification |
