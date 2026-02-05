# GoHighLevel Clone - Workflows Automation SPECs
# Format: EARS (Event-Actions-Result-State)
# Framework: Moai-ADK

module: workflows
domain: automation
version: "1.0.0"
skills_required:
  - moai-workflow-tdd
  - moai-lib-fastapi
  - moai-context7-integration
  - moai-domain-database

specs:
  - id: SPEC-WFL-001
    title: Create Workflow
    priority: critical
    ears:
      event: When a user creates a new automation workflow
      action: the system shall initialize workflow with trigger and blank canvas
      result: new workflow ready for configuration
      state: draft
    workflow_config:
      - name
      - description
      - trigger_type
      - status: [draft, active, paused]
    tests:
      - test_create_workflow
      - test_workflow_naming

  - id: SPEC-WFL-002
    title: Configure Trigger
    priority: critical
    ears:
      event: When setting a workflow trigger
      action: the system shall configure trigger conditions and filters
      result: workflow with active trigger listening
      state: configured
    trigger_types:
      contact_triggers:
        - contact_created
        - contact_updated
        - tag_added
        - tag_removed
        - custom_field_changed
      form_triggers:
        - form_submitted
        - survey_completed
      pipeline_triggers:
        - stage_changed
        - deal_created
        - deal_won
        - deal_lost
      appointment_triggers:
        - appointment_booked
        - appointment_cancelled
        - appointment_completed
        - appointment_no_show
      payment_triggers:
        - payment_received
        - subscription_created
        - subscription_cancelled
      communication_triggers:
        - email_opened
        - email_clicked
        - sms_received
        - call_completed
      time_triggers:
        - scheduled_date
        - recurring_schedule
        - birthday
        - anniversary
    tests:
      - test_contact_trigger
      - test_form_trigger
      - test_time_trigger
      - test_trigger_filters

  - id: SPEC-WFL-003
    title: Add Action Step
    priority: critical
    ears:
      event: When adding an action to workflow
      action: the system shall configure action settings and link to flow
      result: action step added to workflow sequence
      state: added
    action_types:
      communication:
        - send_email
        - send_sms
        - send_voicemail
        - send_messenger
        - make_call
      crm:
        - create_contact
        - update_contact
        - add_tag
        - remove_tag
        - add_to_campaign
        - remove_from_campaign
        - move_pipeline_stage
        - assign_to_user
        - create_task
        - add_note
      timing:
        - wait_time
        - wait_until_date
        - wait_for_event
      internal:
        - send_notification
        - create_opportunity
        - webhook_call
        - custom_code
      membership:
        - grant_course_access
        - revoke_course_access
    tests:
      - test_add_action
      - test_action_config
      - test_action_linking

  - id: SPEC-WFL-004
    title: Add Condition/Branch
    priority: critical
    ears:
      event: When adding conditional logic to workflow
      action: the system shall create if/else branches based on criteria
      result: workflow with conditional paths
      state: branched
    condition_types:
      - contact_field_equals
      - contact_has_tag
      - pipeline_stage_is
      - custom_field_value
      - email_was_opened
      - link_was_clicked
      - time_based
    branch_types:
      - if_else
      - multi_branch
      - split_test
    tests:
      - test_if_else_branch
      - test_multi_branch
      - test_condition_evaluation

  - id: SPEC-WFL-005
    title: Execute Workflow
    priority: critical
    ears:
      event: When a workflow is triggered for a contact
      action: the system shall execute actions in sequence with error handling
      result: workflow execution completed or queued
      state: executed
    execution_config:
      - queue_processing
      - retry_on_failure: 3
      - error_notification: true
      - execution_logging: true
    tests:
      - test_workflow_execution
      - test_action_sequence
      - test_error_handling
      - test_retry_logic

  - id: SPEC-WFL-006
    title: Wait Step Processing
    priority: high
    ears:
      event: When workflow reaches a wait step
      action: the system shall schedule resume and pause execution
      result: workflow paused until wait condition met
      state: waiting
    wait_types:
      - wait_fixed_time: [minutes, hours, days, weeks]
      - wait_until_date
      - wait_until_time_of_day
      - wait_for_event: [email_open, reply, click]
    tests:
      - test_wait_time
      - test_wait_until
      - test_wait_for_event

  - id: SPEC-WFL-007
    title: Goal Tracking
    priority: medium
    ears:
      event: When configuring workflow goal
      action: the system shall monitor for goal completion and exit workflow
      result: contact exits workflow upon goal achievement
      state: goal_set
    goal_types:
      - tag_added
      - purchase_made
      - appointment_booked
      - form_submitted
      - pipeline_stage_reached
    tests:
      - test_goal_configuration
      - test_goal_achievement
      - test_workflow_exit

  - id: SPEC-WFL-008
    title: Workflow Templates
    priority: medium
    ears:
      event: When using a workflow template
      action: the system shall clone template and allow customization
      result: new workflow based on template
      state: cloned
    template_categories:
      - lead_nurturing
      - appointment_reminder
      - onboarding
      - re_engagement
      - review_request
      - birthday_celebration
    tests:
      - test_template_library
      - test_template_clone
      - test_template_customization

  - id: SPEC-WFL-009
    title: Workflow Analytics
    priority: high
    ears:
      event: When viewing workflow performance
      action: the system shall display metrics on enrollment, completion, and conversions
      result: analytics dashboard with funnel visualization
      state: analyzed
    metrics:
      - total_enrolled
      - currently_active
      - completed
      - goals_achieved
      - conversion_rate
      - action_performance
      - drop_off_points
    tests:
      - test_enrollment_tracking
      - test_completion_metrics
      - test_conversion_tracking

  - id: SPEC-WFL-010
    title: Webhook Integration
    priority: high
    ears:
      event: When workflow calls external webhook
      action: the system shall send HTTP request with payload and handle response
      result: external system notified with response logged
      state: integrated
    webhook_config:
      methods: [GET, POST, PUT, PATCH, DELETE]
      headers: custom
      payload: json
      authentication: [none, basic, bearer, api_key]
      timeout_seconds: 30
      retry_on_failure: true
    tests:
      - test_webhook_call
      - test_webhook_response_handling
      - test_webhook_error_retry

  - id: SPEC-WFL-011
    title: Bulk Enrollment
    priority: medium
    ears:
      event: When bulk enrolling contacts into workflow
      action: the system shall queue contacts and process enrollment in batches
      result: multiple contacts enrolled with progress tracking
      state: enrolling
    bulk_config:
      max_contacts: 10000
      batch_size: 100
      processing: async
    tests:
      - test_bulk_selection
      - test_batch_processing
      - test_progress_tracking

  - id: SPEC-WFL-012
    title: Workflow Versioning
    priority: low
    ears:
      event: When modifying an active workflow
      action: the system shall create new version while maintaining active executions
      result: versioned workflow with execution continuity
      state: versioned
    versioning:
      - auto_version_on_edit
      - maintain_running_on_old
      - migration_option
    tests:
      - test_version_creation
      - test_execution_continuity
