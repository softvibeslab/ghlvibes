# SPEC-WFL-009: Workflow Analytics - Acceptance Criteria

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-WFL-009 |
| **Title** | Workflow Analytics |
| **Related SPEC** | [spec.md](./spec.md) |
| **Implementation Plan** | [plan.md](./plan.md) |

---

## Acceptance Criteria Overview

This document defines the acceptance criteria for SPEC-WFL-009: Workflow Analytics using Given/When/Then (Gherkin) format. Each criterion maps to a specific requirement in the specification.

---

## AC-WFL-009-01: Analytics Dashboard Display

**Requirement:** REQ-WFL-009-01

### Scenario: View workflow analytics dashboard

```gherkin
Given a user is authenticated and has access to a workflow
And the workflow has at least 100 contacts enrolled
When the user navigates to the workflow analytics page
Then the system shall display the analytics dashboard within 2 seconds
And the dashboard shall show the following summary metrics:
  | Metric | Description |
  | Total Enrolled | Count of all contacts ever enrolled |
  | Currently Active | Count of contacts currently in workflow |
  | Completed | Count of contacts who finished workflow |
  | Conversion Rate | Percentage of enrolled who achieved goal |
And the dashboard shall display a funnel visualization
And the dashboard shall show trend charts for the selected time period
```

### Scenario: Analytics dashboard with empty workflow

```gherkin
Given a user is authenticated and has access to a workflow
And the workflow has zero contacts enrolled
When the user navigates to the workflow analytics page
Then the system shall display the analytics dashboard
And all metrics shall show zero values
And the funnel visualization shall display an empty state message
And the system shall suggest enabling the workflow or enrolling contacts
```

### Scenario: Analytics dashboard performance under load

```gherkin
Given a workflow has 100,000 contacts enrolled
When the user requests the analytics dashboard
Then the dashboard shall load completely within 2 seconds
And all charts shall render without freezing the UI
And pagination shall be available for detailed data tables
```

---

## AC-WFL-009-02: Enrollment Tracking

**Requirement:** REQ-WFL-009-02

### Scenario: Track new workflow enrollment

```gherkin
Given a workflow is active with existing enrollments
When a new contact is enrolled via trigger activation
Then the system shall record the enrollment event with:
  | Field | Value |
  | contact_id | The enrolled contact's ID |
  | workflow_id | The target workflow ID |
  | enrolled_at | Current UTC timestamp |
  | enrollment_source | "trigger" |
  | status | "active" |
And the total_enrolled metric shall increment by 1
And the currently_active metric shall increment by 1
And the new_enrollments metric for the current period shall increment by 1
```

### Scenario: Track bulk enrollment

```gherkin
Given a workflow is active
And a user selects 500 contacts for bulk enrollment
When the bulk enrollment is processed
Then the system shall record 500 enrollment events
And each event shall have enrollment_source = "bulk"
And the total_enrolled metric shall increment by 500
And the currently_active metric shall increment by 500
```

### Scenario: Enrollment source attribution

```gherkin
Given a workflow tracks enrollment sources
When viewing enrollment metrics
Then the system shall display enrollment breakdown by source:
  | Source | Description |
  | trigger | Automatic trigger-based enrollment |
  | bulk | Bulk enrollment by user |
  | api | Enrollment via REST API |
  | manual | Single contact manual enrollment |
And percentages shall sum to 100%
```

---

## AC-WFL-009-03: Completion Metrics

**Requirement:** REQ-WFL-009-03

### Scenario: Track workflow completion

```gherkin
Given a contact is enrolled in a workflow
And the contact has progressed through all workflow steps
When the contact reaches the final step and completes it
Then the system shall update the execution status to "completed"
And the system shall record completed_at timestamp
And the completed metric shall increment by 1
And the currently_active metric shall decrement by 1
And the completion_rate shall be recalculated
```

### Scenario: Calculate completion rate

```gherkin
Given a workflow has:
  | Metric | Value |
  | total_enrolled | 1000 |
  | completed | 600 |
When the completion rate is calculated
Then the completion_rate shall equal 60.0%
And the formula used shall be (completed / total_enrolled) * 100
```

### Scenario: Track average completion duration

```gherkin
Given multiple contacts have completed a workflow
And their completion times are:
  | Contact | Duration (hours) |
  | A | 48 |
  | B | 72 |
  | C | 24 |
When the average duration is calculated
Then the average_duration_hours shall equal 48
And the duration shall be measured from enrolled_at to completed_at
```

### Scenario: Track exit reasons

```gherkin
Given contacts exit a workflow for various reasons
When viewing completion metrics
Then the system shall display exit reason distribution:
  | Reason | Description |
  | completed | Reached final step |
  | goal_achieved | Achieved workflow goal |
  | manual_removal | Removed by user |
  | unsubscribed | Contact unsubscribed |
  | error | Execution error |
And percentages shall reflect actual exit distribution
```

---

## AC-WFL-009-04: Conversion Tracking

**Requirement:** REQ-WFL-009-04

### Scenario: Track goal achievement

```gherkin
Given a workflow has a goal configured (e.g., "tag_added: customer")
And a contact is enrolled in the workflow
When the contact achieves the goal (tag is added)
Then the system shall update execution status to "goal_achieved"
And the system shall record goal_achieved_at timestamp
And the goals_achieved metric shall increment by 1
And the conversion_rate shall be recalculated
```

### Scenario: Calculate conversion rate

```gherkin
Given a workflow has:
  | Metric | Value |
  | total_enrolled | 1000 |
  | goals_achieved | 250 |
When the conversion rate is calculated
Then the conversion_rate shall equal 25.0%
And the formula used shall be (goals_achieved / total_enrolled) * 100
```

### Scenario: Track time to conversion

```gherkin
Given contacts achieve goals at different times
When viewing conversion metrics
Then the system shall display:
  | Metric | Description |
  | average_time_to_conversion | Mean time from enrollment to goal |
  | median_time_to_conversion | Median time from enrollment to goal |
  | fastest_conversion | Minimum time to goal |
  | slowest_conversion | Maximum time to goal |
```

### Scenario: Multiple goals tracking

```gherkin
Given a workflow has multiple goals configured:
  | Goal ID | Goal Type | Goal Value |
  | G1 | tag_added | prospect |
  | G2 | appointment_booked | any |
When viewing conversion metrics
Then the system shall display goal breakdown:
  | Goal | Achieved | Rate |
  | prospect tag | 200 | 20% |
  | appointment | 150 | 15% |
And the overall conversion shall be based on first goal achieved
```

---

## AC-WFL-009-05: Action Performance Metrics

**Requirement:** REQ-WFL-009-05

### Scenario: Track action execution success

```gherkin
Given a workflow has an "Send Email" action
And the action has executed 1000 times
And 980 executions succeeded and 20 failed
When viewing action performance metrics
Then the system shall display:
  | Metric | Value |
  | executions | 1000 |
  | successes | 980 |
  | failures | 20 |
  | success_rate | 98.0% |
```

### Scenario: Track action execution duration

```gherkin
Given multiple action executions have completed
When viewing action performance metrics
Then the system shall display:
  | Metric | Value |
  | average_duration_ms | Average execution time |
  | p95_duration_ms | 95th percentile execution time |
  | p99_duration_ms | 99th percentile execution time |
```

### Scenario: Identify problematic actions

```gherkin
Given a workflow has multiple actions
When analyzing action performance
Then the system shall highlight actions with:
  | Condition | Indicator |
  | success_rate < 95% | Warning badge |
  | success_rate < 80% | Error badge |
  | average_duration > 5s | Slow indicator |
And problematic actions shall appear at the top of the list
```

---

## AC-WFL-009-06: Drop-off Analysis

**Requirement:** REQ-WFL-009-06

### Scenario: Identify drop-off points in funnel

```gherkin
Given a workflow has the following steps:
  | Step | Entered | Completed |
  | Step 1 | 1000 | 950 |
  | Step 2 | 950 | 800 |
  | Step 3 | 800 | 400 |
  | Step 4 | 400 | 380 |
When viewing funnel analysis
Then the system shall identify Step 3 as the primary drop-off point
And the drop-off rate for Step 3 shall be 50%
And the system shall highlight Step 3 visually in the funnel
```

### Scenario: Calculate step conversion rates

```gherkin
Given a workflow funnel with sequential steps
When viewing the funnel visualization
Then each step shall display:
  | Metric | Description |
  | entered | Contacts who reached this step |
  | completed | Contacts who completed this step |
  | dropped_off | Contacts who exited at this step |
  | conversion_rate | completed / entered * 100 |
And the funnel shall visually narrow based on conversion rates
```

### Scenario: Compare drop-off to benchmarks

```gherkin
Given historical workflow performance data exists
When viewing current funnel analysis
Then the system shall display:
  | Comparison | Description |
  | vs_previous_period | Comparison to same period last cycle |
  | vs_workflow_average | Comparison to workflow's historical average |
And improvements shall be shown in green
And declines shall be shown in red
```

---

## AC-WFL-009-07: Time-Based Filtering

**Requirement:** REQ-WFL-009-07

### Scenario: Filter analytics by date range

```gherkin
Given a user is viewing the analytics dashboard
When the user selects a date range filter:
  | Start Date | End Date |
  | 2026-01-01 | 2026-01-31 |
Then all metrics shall reflect only data within that range
And the trend charts shall show data for the selected period
And the date range shall be displayed in the dashboard header
```

### Scenario: Use preset date ranges

```gherkin
Given a user is viewing the analytics dashboard
When the user clicks the date range selector
Then the following presets shall be available:
  | Preset | Description |
  | Today | Current date only |
  | Last 7 days | Past 7 days including today |
  | Last 30 days | Past 30 days including today |
  | Last 90 days | Past 90 days including today |
  | This month | Current calendar month |
  | Last month | Previous calendar month |
  | Custom | User-defined range |
```

### Scenario: Compare periods

```gherkin
Given a user has selected "Last 30 days" as the primary period
When the user enables comparison mode
Then the system shall compare to the previous 30 days
And each metric shall show:
  | Display | Example |
  | Current value | 1,200 enrollments |
  | Change | +15% vs previous period |
  | Direction indicator | Green up arrow for increase |
```

### Scenario: Respect user timezone

```gherkin
Given a user's timezone is set to "America/New_York" (UTC-5)
And the user selects "Today" as the date filter
When viewing analytics at 10:00 AM local time
Then the date range shall be from midnight to current time in user's timezone
And all displayed times shall be in the user's local timezone
```

---

## AC-WFL-009-08: Data Export

**Requirement:** REQ-WFL-009-08

### Scenario: Export analytics as CSV

```gherkin
Given a user is viewing workflow analytics
When the user clicks "Export" and selects "CSV"
Then the system shall generate a CSV file containing:
  | Column | Description |
  | date | Data date |
  | total_enrolled | Cumulative enrollments |
  | new_enrollments | New enrollments for period |
  | completed | Cumulative completions |
  | goals_achieved | Cumulative conversions |
  | conversion_rate | Period conversion rate |
And the file shall download with name format: "workflow-analytics-{workflow_id}-{date}.csv"
```

### Scenario: Export analytics as PDF

```gherkin
Given a user is viewing workflow analytics
When the user clicks "Export" and selects "PDF"
Then the system shall generate a PDF report containing:
  | Section | Content |
  | Header | Workflow name, date range, generated date |
  | Summary | Key metrics with comparison |
  | Funnel | Funnel visualization as image |
  | Trends | Trend charts as images |
  | Actions | Action performance table |
And the file shall download with name format: "workflow-analytics-{workflow_id}-{date}.pdf"
```

### Scenario: Export analytics as JSON

```gherkin
Given a user is viewing workflow analytics
When the user clicks "Export" and selects "JSON"
Then the system shall generate a JSON file matching the API response schema
And the file shall be valid JSON
And the file shall download with name format: "workflow-analytics-{workflow_id}-{date}.json"
```

### Scenario: Handle large export requests

```gherkin
Given a workflow has 500,000 enrolled contacts
When the user requests a CSV export of detailed execution data
Then the system shall:
  | Step | Action |
  | 1 | Display "Export in progress" message |
  | 2 | Queue export job for background processing |
  | 3 | Show progress indicator (percentage complete) |
  | 4 | Notify user when export is ready |
  | 5 | Provide download link valid for 24 hours |
And the export shall complete within 5 minutes
```

---

## AC-WFL-009-09: Real-time Updates

**Requirement:** REQ-WFL-009-09

### Scenario: Receive real-time metric updates

```gherkin
Given a user is viewing the analytics dashboard
And the workflow is actively receiving new enrollments
When a new contact is enrolled in the workflow
Then the dashboard shall update within 5 seconds
And only the changed metrics shall be updated (not full page refresh)
And the updated values shall briefly highlight to indicate change
```

### Scenario: Handle connection interruption

```gherkin
Given a user is viewing the analytics dashboard with real-time updates
When the network connection is temporarily lost
Then the system shall display a "Connection lost" indicator
And the system shall attempt to reconnect automatically
When the connection is restored
Then the system shall resume real-time updates
And any missed updates shall be fetched and applied
```

### Scenario: Graceful degradation without real-time support

```gherkin
Given a user's browser does not support Server-Sent Events
When the user views the analytics dashboard
Then the system shall fall back to polling-based updates
And the polling interval shall be 30 seconds
And a message shall indicate "Updates every 30 seconds"
```

### Scenario: Pause updates when tab is inactive

```gherkin
Given a user is viewing the analytics dashboard
When the user switches to a different browser tab
Then the system shall pause real-time updates to save resources
When the user returns to the analytics tab
Then the system shall resume real-time updates
And immediately fetch current data to ensure accuracy
```

---

## AC-WFL-009-10: Data Retention

**Requirement:** REQ-WFL-009-10

### Scenario: Retain detailed data for 90 days

```gherkin
Given a workflow execution event occurred 89 days ago
When the data retention job runs
Then the detailed execution record shall be retained
And all associated step-level data shall be retained
```

### Scenario: Archive data after 90 days

```gherkin
Given a workflow execution event occurred 91 days ago
When the data retention job runs
Then the detailed execution record shall be archived/deleted
And the aggregated daily metrics shall be retained
And the contact can still see they were in the workflow (via contact history)
```

### Scenario: Retain aggregated data for 2 years

```gherkin
Given aggregated analytics data is 18 months old
When the data retention job runs
Then the daily aggregated metrics shall be retained
And the monthly summaries shall be retained
```

### Scenario: Indefinite monthly summary retention

```gherkin
Given monthly summary data is 3 years old
When the data retention job runs
Then the monthly summary shall be retained indefinitely
And the summary shall include:
  | Field | Description |
  | month | YYYY-MM |
  | total_enrolled | Month total |
  | completed | Month total |
  | conversion_rate | Month average |
```

---

## Test Scenarios

### test_enrollment_tracking

```python
def test_enrollment_tracking():
    """
    Test that enrollment events are properly tracked.

    Requirements: REQ-WFL-009-02
    Acceptance Criteria: AC-WFL-009-02
    """
    # Given a workflow exists
    workflow = create_workflow()

    # When a contact is enrolled
    contact = create_contact()
    enroll_contact(workflow.id, contact.id, source="trigger")

    # Then enrollment is recorded
    analytics = get_workflow_analytics(workflow.id)
    assert analytics.total_enrolled == 1
    assert analytics.currently_active == 1

    # And the execution record exists
    execution = get_execution(workflow.id, contact.id)
    assert execution.status == "active"
    assert execution.enrollment_source == "trigger"
    assert execution.enrolled_at is not None
```

### test_completion_metrics

```python
def test_completion_metrics():
    """
    Test that completion metrics are calculated correctly.

    Requirements: REQ-WFL-009-03
    Acceptance Criteria: AC-WFL-009-03
    """
    # Given a workflow with enrolled contacts
    workflow = create_workflow_with_enrollments(count=100)

    # When 60 contacts complete the workflow
    complete_contacts(workflow.id, count=60)

    # Then completion metrics are accurate
    analytics = get_workflow_analytics(workflow.id)
    assert analytics.completed == 60
    assert analytics.completion_rate == 60.0
    assert analytics.currently_active == 40
```

### test_conversion_tracking

```python
def test_conversion_tracking():
    """
    Test that conversion/goal tracking works correctly.

    Requirements: REQ-WFL-009-04
    Acceptance Criteria: AC-WFL-009-04
    """
    # Given a workflow with a goal
    workflow = create_workflow_with_goal(goal_type="tag_added", goal_value="customer")
    contact = enroll_contact(workflow.id)

    # When the contact achieves the goal
    add_tag_to_contact(contact.id, "customer")
    process_goal_achievement(workflow.id, contact.id)

    # Then conversion is tracked
    analytics = get_workflow_analytics(workflow.id)
    assert analytics.goals_achieved == 1

    execution = get_execution(workflow.id, contact.id)
    assert execution.status == "goal_achieved"
    assert execution.goal_achieved_at is not None
```

### test_funnel_analysis

```python
def test_funnel_analysis():
    """
    Test funnel drop-off analysis.

    Requirements: REQ-WFL-009-06
    Acceptance Criteria: AC-WFL-009-06
    """
    # Given a workflow with multiple steps
    workflow = create_workflow_with_steps(step_count=4)

    # And contacts at various stages
    simulate_funnel_progression(
        workflow.id,
        step_1_entered=1000, step_1_completed=950,
        step_2_entered=950, step_2_completed=800,
        step_3_entered=800, step_3_completed=400,
        step_4_entered=400, step_4_completed=380
    )

    # When analyzing the funnel
    funnel = get_funnel_analysis(workflow.id)

    # Then drop-off points are identified
    assert funnel.bottleneck_step_id == workflow.steps[2].id  # Step 3
    assert funnel.steps[2].conversion_rate == 50.0
```

### test_realtime_updates

```python
async def test_realtime_updates():
    """
    Test real-time dashboard updates.

    Requirements: REQ-WFL-009-09
    Acceptance Criteria: AC-WFL-009-09
    """
    # Given a connected SSE client
    workflow = create_workflow()
    async with sse_client(workflow.id) as client:
        # When a new enrollment occurs
        enroll_contact(workflow.id, create_contact().id)

        # Then the update is received within 5 seconds
        event = await asyncio.wait_for(client.receive(), timeout=5.0)

        assert event.event == "metrics_update"
        assert event.data["changes"]["currently_active"] == 1
```

### test_data_export

```python
def test_data_export():
    """
    Test analytics data export.

    Requirements: REQ-WFL-009-08
    Acceptance Criteria: AC-WFL-009-08
    """
    # Given a workflow with analytics data
    workflow = create_workflow_with_analytics_data()

    # When exporting as CSV
    response = export_analytics(workflow.id, format="csv")

    # Then a valid CSV is returned
    assert response.status_code == 200
    assert "text/csv" in response.headers["Content-Type"]

    csv_data = parse_csv(response.content)
    assert len(csv_data) > 0
    assert "date" in csv_data[0]
    assert "total_enrolled" in csv_data[0]
```

---

## Definition of Done

- [ ] All acceptance criteria scenarios pass automated tests
- [ ] Unit test coverage >= 85%
- [ ] Integration tests for all API endpoints pass
- [ ] E2E tests for dashboard interactions pass
- [ ] Performance benchmarks met (2s dashboard load, 5s real-time updates)
- [ ] Export functionality tested with large datasets (100K+ records)
- [ ] Data retention policy verified in staging environment
- [ ] Security review completed (authorization, rate limiting)
- [ ] API documentation updated with examples
- [ ] User documentation for analytics features created
- [ ] Accessibility audit passed (WCAG 2.1 AA)

---

## Traceability Matrix

| Acceptance Criteria | Requirement | Test Cases |
|---------------------|-------------|------------|
| AC-WFL-009-01 | REQ-WFL-009-01 | test_dashboard_display, test_dashboard_empty_state, test_dashboard_performance |
| AC-WFL-009-02 | REQ-WFL-009-02 | test_enrollment_tracking, test_bulk_enrollment, test_enrollment_sources |
| AC-WFL-009-03 | REQ-WFL-009-03 | test_completion_metrics, test_completion_rate, test_average_duration, test_exit_reasons |
| AC-WFL-009-04 | REQ-WFL-009-04 | test_conversion_tracking, test_conversion_rate, test_time_to_conversion, test_multiple_goals |
| AC-WFL-009-05 | REQ-WFL-009-05 | test_action_performance, test_action_duration, test_problematic_actions |
| AC-WFL-009-06 | REQ-WFL-009-06 | test_funnel_analysis, test_step_conversion, test_benchmark_comparison |
| AC-WFL-009-07 | REQ-WFL-009-07 | test_date_filtering, test_preset_ranges, test_period_comparison, test_timezone |
| AC-WFL-009-08 | REQ-WFL-009-08 | test_csv_export, test_pdf_export, test_json_export, test_large_export |
| AC-WFL-009-09 | REQ-WFL-009-09 | test_realtime_updates, test_connection_recovery, test_fallback_polling, test_tab_inactive |
| AC-WFL-009-10 | REQ-WFL-009-10 | test_90_day_retention, test_archive_old_data, test_2_year_aggregate, test_monthly_summary |
