# SPEC-WFL-008: Workflow Templates - Acceptance Criteria

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-008 |
| **Title** | Workflow Templates |
| **Module** | workflows |
| **Domain** | automation |
| **Priority** | Medium |
| **Status** | Planned |

---

## Test Scenarios

### Feature: Template Library Access

#### Scenario: AC-001 - View Template Library

```gherkin
Feature: Template Library Access
  As a marketing user
  I want to browse available workflow templates
  So that I can quickly create automation workflows

  Scenario: View all templates in the library
    Given I am authenticated as a user with workflow permissions
    And the system has pre-built workflow templates
    When I navigate to the workflow templates page
    Then I should see a grid of available templates
    And each template card should display:
      | Field | Required |
      | Template name | Yes |
      | Description | Yes |
      | Category badge | Yes |
      | Usage count | Yes |
      | Preview button | Yes |
      | Use Template button | Yes |
```

#### Scenario: AC-002 - Filter Templates by Category

```gherkin
  Scenario: Filter templates by category
    Given I am on the template library page
    And templates exist in multiple categories
    When I click on the "Lead Nurturing" category tab
    Then I should only see templates in the "lead_nurturing" category
    And the category count should match the displayed templates
    And other category templates should be hidden
```

#### Scenario: AC-003 - Search Templates

```gherkin
  Scenario: Search templates by keyword
    Given I am on the template library page
    And a template named "Welcome Email Sequence" exists
    When I type "welcome" in the search input
    And I wait for search results to load
    Then I should see templates matching "welcome" in name or description
    And the "Welcome Email Sequence" template should be visible
    And non-matching templates should be filtered out
```

---

### Feature: Template Preview

#### Scenario: AC-004 - Preview Template Details

```gherkin
Feature: Template Preview
  As a marketing user
  I want to preview a template before using it
  So that I can understand if it meets my needs

  Scenario: View template preview modal
    Given I am on the template library page
    And I see the "New Lead Follow-up" template
    When I click the "Preview" button on the template card
    Then a preview modal should open
    And I should see the complete workflow visualization
    And I should see the trigger configuration
    And I should see all action steps with their content
    And I should see conditional branches if present
    And I should see timing/wait steps
    And I should see required integrations listed
```

#### Scenario: AC-005 - Preview Shows Action Details

```gherkin
  Scenario: View action step details in preview
    Given I have opened a template preview
    And the template contains an "Send Email" action
    When I click on the email action step in the visualization
    Then I should see the email subject line
    And I should see a preview of the email content
    And I should see any personalization tags used
```

---

### Feature: Template Cloning

#### Scenario: AC-006 - Clone Template to New Workflow

```gherkin
Feature: Template Cloning
  As a marketing user
  I want to create a new workflow from a template
  So that I can quickly set up automation without starting from scratch

  Scenario: Successfully clone a template
    Given I am viewing the "Appointment Reminder" template
    And I have permission to create workflows
    And my account has not reached the workflow limit
    When I click "Use Template"
    And I enter "My Appointment Reminders" as the workflow name
    And I click "Create Workflow"
    Then a new workflow should be created with status "draft"
    And the workflow should contain all steps from the template
    And I should be redirected to the workflow editor
    And the workflow name should be "My Appointment Reminders"
    And a success notification should appear
```

#### Scenario: AC-007 - Clone Preserves Workflow Configuration

```gherkin
  Scenario: Cloned workflow preserves all configuration
    Given I have cloned the "Lead Nurturing Sequence" template
    When I open the cloned workflow in the editor
    Then the trigger should match the template's trigger
    And all action steps should be present in the correct order
    And all conditional branches should be preserved
    And all wait/timing steps should have correct durations
    And all email/SMS content should be copied
    And all goal settings should be preserved
```

#### Scenario: AC-008 - Clone Fails Without Required Integration

```gherkin
  Scenario: Cannot clone template with missing integration
    Given I am viewing a template that requires "Twilio SMS"
    And my account does not have Twilio connected
    When I click "Use Template"
    Then I should see an error message
    And the message should indicate "This template requires Twilio SMS which is not connected"
    And I should see a link to connect the integration
    And no workflow should be created
```

#### Scenario: AC-009 - Clone Fails at Workflow Limit

```gherkin
  Scenario: Cannot clone template when workflow limit reached
    Given I am viewing a template
    And my account has reached the maximum workflow limit
    When I click "Use Template"
    Then I should see an error message
    And the message should indicate "You have reached your workflow limit"
    And I should see upgrade options if available
    And no workflow should be created
```

---

### Feature: Template Customization

#### Scenario: AC-010 - Customize Cloned Workflow

```gherkin
Feature: Template Customization
  As a marketing user
  I want to customize a cloned workflow
  So that I can adapt it to my specific needs

  Scenario: Modify workflow name and description
    Given I have cloned a template and am in the workflow editor
    When I click on the workflow settings
    And I change the name to "Q1 Lead Campaign"
    And I change the description to "Lead nurturing for Q1 prospects"
    And I save the changes
    Then the workflow should be updated with the new name
    And the workflow should be updated with the new description
```

#### Scenario: AC-011 - Modify Email Content

```gherkin
  Scenario: Edit email action content
    Given I have a cloned workflow with an email action
    When I click on the email action step
    And I edit the subject line to "Welcome to Our Service, {{first_name}}!"
    And I edit the email body content
    And I save the action
    Then the email action should be updated with the new content
    And personalization tags should be preserved
```

#### Scenario: AC-012 - Modify Wait Timing

```gherkin
  Scenario: Change wait step duration
    Given I have a cloned workflow with a wait step of 2 days
    When I click on the wait step
    And I change the duration to 3 days
    And I save the action
    Then the wait step should be updated to 3 days
```

---

### Feature: Custom Template Creation

#### Scenario: AC-013 - Save Workflow as Template

```gherkin
Feature: Custom Template Creation
  As a marketing user
  I want to save my workflow as a template
  So that I can reuse it for future campaigns

  Scenario: Create custom template from workflow
    Given I have an active workflow with multiple steps
    And I have permission to create templates
    And my account has not reached the template limit
    When I click "Save as Template" in the workflow editor
    And I enter "My Lead Workflow" as the template name
    And I enter "Effective lead nurturing sequence" as the description
    And I select "Lead Nurturing" as the category
    And I click "Save Template"
    Then a new template should be created
    And the template should appear in my custom templates
    And a success notification should appear
```

#### Scenario: AC-014 - Custom Template Sanitization

```gherkin
  Scenario: Template content is sanitized
    Given I have a workflow with email containing customer names
    When I save it as a template
    Then specific customer names should be replaced with placeholders
    And email addresses should be anonymized
    And phone numbers should be masked
    And the template should still be functional
```

#### Scenario: AC-015 - Share Template with Sub-accounts (Agency)

```gherkin
  Scenario: Agency shares template with sub-accounts
    Given I am an agency admin
    And I have a custom template
    When I click "Share" on the template
    And I select sub-accounts to share with
    And I confirm the sharing
    Then the template should be visible to selected sub-accounts
    And sub-accounts should be able to clone the template
```

---

### Feature: Template Validation

#### Scenario: AC-016 - Validate Template Before Save

```gherkin
Feature: Template Validation
  As a system administrator
  I want templates to be validated before saving
  So that users only see functional templates

  Scenario: Invalid template fails validation
    Given I am saving a workflow as a template
    And the workflow has an action with missing configuration
    When I attempt to save the template
    Then I should see a validation error
    And the error should indicate which step is incomplete
    And the template should not be saved
```

#### Scenario: AC-017 - Valid Template Passes Validation

```gherkin
  Scenario: Complete template passes validation
    Given I am saving a workflow as a template
    And all workflow steps are properly configured
    And at least one trigger is defined
    And at least one action is defined
    When I save the template
    Then validation should pass
    And the template should be saved successfully
```

---

### Feature: Template Usage Tracking

#### Scenario: AC-018 - Track Template Usage

```gherkin
Feature: Template Usage Tracking
  As a platform administrator
  I want to track template usage
  So that I can understand which templates are most valuable

  Scenario: Usage count increments on clone
    Given a template has been cloned 5 times
    When I clone the template
    Then the template usage count should be 6
    And the clone event should be recorded with timestamp
    And the account ID should be recorded
```

#### Scenario: AC-019 - Display Usage Statistics

```gherkin
  Scenario: View template popularity statistics
    Given I am viewing the template library
    When I look at a template card
    Then I should see how many times it has been used
    And I should see the average completion rate if available
```

---

## Non-Functional Requirements

### Performance Acceptance Criteria

#### AC-020 - Template List Load Time

```gherkin
Scenario: Template library loads within performance target
  Given the template library has 100+ templates
  When I navigate to the template library page
  Then the initial page load should complete in under 2 seconds
  And template cards should begin rendering within 500ms
```

#### AC-021 - Template Clone Performance

```gherkin
Scenario: Template cloning completes within performance target
  Given I am cloning a template with 50 action steps
  When I confirm the clone operation
  Then the new workflow should be created in under 2 seconds
  And I should be redirected to the editor immediately
```

#### AC-022 - Search Response Time

```gherkin
Scenario: Template search returns results quickly
  Given the template library has 500+ templates
  When I search for "email"
  Then search results should appear in under 200ms
```

### Security Acceptance Criteria

#### AC-023 - Template Access Control

```gherkin
Scenario: Users can only access permitted templates
  Given I am a user in Account A
  And Account B has custom templates
  When I view the template library
  Then I should not see Account B's custom templates
  And I should see system templates
  And I should see my account's custom templates
```

#### AC-024 - Audit Logging

```gherkin
Scenario: Template operations are logged
  Given I clone a template
  Then an audit log entry should be created
  And the log should include:
    | Field | Value |
    | action | template_cloned |
    | template_id | <UUID> |
    | workflow_id | <UUID> |
    | user_id | <UUID> |
    | timestamp | <ISO8601> |
```

---

## Test Cases Mapping

| Test ID | Scenario | EARS Requirement | Priority |
|---------|----------|------------------|----------|
| test_template_library | AC-001, AC-002, AC-003 | REQ-001, REQ-005, REQ-006 | Critical |
| test_template_preview | AC-004, AC-005 | REQ-007 | High |
| test_template_clone | AC-006, AC-007 | REQ-003 | Critical |
| test_template_clone_validation | AC-008, AC-009 | REQ-011 | High |
| test_template_customization | AC-010, AC-011, AC-012 | REQ-004 | High |
| test_custom_template_create | AC-013, AC-014 | REQ-009 | Medium |
| test_template_sharing | AC-015 | REQ-009 | Medium |
| test_template_validation | AC-016, AC-017 | REQ-010 | High |
| test_usage_tracking | AC-018, AC-019 | REQ-008 | Medium |
| test_performance | AC-020, AC-021, AC-022 | Performance SLA | High |
| test_security | AC-023, AC-024 | Security Constraints | Critical |

---

## Definition of Done

### Code Quality

- [ ] All acceptance criteria scenarios pass
- [ ] Unit test coverage >= 85%
- [ ] Integration tests for all API endpoints
- [ ] E2E tests for critical user flows
- [ ] Zero LSP errors (type errors, lint errors)
- [ ] Code reviewed and approved

### Documentation

- [ ] API endpoints documented in OpenAPI spec
- [ ] Repository methods have docstrings
- [ ] User-facing documentation updated
- [ ] Runbook for template seeding

### Security

- [ ] RLS policies implemented and tested
- [ ] Input validation on all endpoints
- [ ] PII sanitization verified
- [ ] Audit logging implemented

### Performance

- [ ] Template list loads < 2 seconds
- [ ] Clone operation < 2 seconds
- [ ] Search results < 200ms
- [ ] Load tested with 100+ concurrent users

### Deployment

- [ ] Database migrations ready
- [ ] System templates seeded
- [ ] Feature flags configured (if applicable)
- [ ] Monitoring dashboards updated

---

## Traceability

| Artifact | Reference |
|----------|-----------|
| Specification | spec.md |
| Implementation Plan | plan.md |
| Product Requirement | Workflows Module - Pre-built workflow templates |
| Quality Framework | TRUST 5 |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-26 | SPEC Builder | Initial acceptance criteria |
