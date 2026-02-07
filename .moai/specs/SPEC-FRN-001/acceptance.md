# Acceptance Criteria: SPEC-FRN-001

**SPEC:** Workflows Module - Frontend User Interface
**Acceptance Version:** 1.0.0
**Last Updated:** 2026-02-07

---

## Overview

This document defines comprehensive acceptance criteria for the Workflows Module frontend implementation. Criteria are organized by feature area using Given-When-Then (Gherkin) format for clarity and testability.

**Definition of Done:**
- All acceptance criteria pass verification
- Unit tests achieve 80%+ coverage
- Component tests achieve 70%+ coverage
- E2E tests cover all critical user flows
- Lighthouse scores: Performance 90+, Accessibility 90+, Best Practices 90+
- Application deployed to staging environment and verified

---

## AC-001: Workflow List Page

### AC-001-01: View All Workflows

**GIVEN** a user is logged in with appropriate permissions
**WHEN** they navigate to /workflows
**THEN** they see a paginated table of all workflows for their account
**AND** the table displays columns: Name, Status, Trigger Type, Active Contacts, Completion Rate, Last Modified
**AND** workflows are sorted by Last Modified descending (most recent first)

**Verification:**
- Table renders with correct number of rows (respects page size)
- Each row displays correct data for each column
- Default sort order is Last Modified descending
- Status badges show correct colors: Active (green), Draft (gray), Paused (yellow)

---

### AC-001-02: Search Workflows

**GIVEN** a user is on the workflow list page with 50+ workflows
**WHEN** they type "welcome" in the search input
**THEN** the table filters to show only workflows with "welcome" in the name
**AND** search is debounced (300ms delay)
**AND** a clear search button (X) appears in the input

**Verification:**
- Typing triggers debounced API call after 300ms
- Results display workflows matching search term
- Clear button removes search term and resets list
- Search is case-insensitive

---

### AC-001-03: Filter by Status

**GIVEN** a user is on the workflow list page
**WHEN** they select "Active" from the status filter dropdown
**THEN** the table displays only workflows with status "active"
**AND** a "Active" filter chip appears below the search bar
**AND** the chip can be clicked to remove the filter

**Verification:**
- Status filter dropdown shows: All, Active, Draft, Paused
- Selecting a status filters the table
- Filter chip displays with remove button (X)
- Clicking X removes filter and shows "All" workflows

---

### AC-001-04: Sort Workflows

**GIVEN** a user is on the workflow list page
**WHEN** they click the "Name" column header
**THEN** the table sorts by Name ascending (A-Z)
**AND** an up arrow indicator appears next to "Name"
**WHEN** they click "Name" again
**THEN** the table sorts by Name descending (Z-A)
**AND** a down arrow indicator appears

**Verification:**
- All column headers are clickable except "Active Contacts" and "Completion Rate"
- Click toggles between ascending and descending
- Sort indicator displays current direction
- Sort persists across page navigation

---

### AC-001-05: Paginate Workflows

**GIVEN** a user is on the workflow list page with 100+ workflows
**WHEN** the page size is set to 25
**THEN** only 25 workflows display on the first page
**AND** pagination controls show: Previous, 1, 2, 3, 4, Next
**WHEN** they click "Next" or page 2
**THEN** workflows 26-50 display
**AND** the URL updates to ?page=2

**Verification:**
- Page size selector offers: 10, 25, 50, 100
- Changing page size updates table immediately
- Pagination buttons disable when at first/last page
- URL query params sync with current page and page size

---

### AC-001-06: Create Workflow Button

**GIVEN** a user is on the workflow list page
**WHEN** they click the "Create Workflow" button
**THEN** they are navigated to the workflow creation wizard at /workflows/create
**AND** the wizard displays Step 1 of 4: Choose Starting Point

**Verification:**
- Button is prominent (primary color, large size)
- Button displays in top-right of page
- Click navigates to /workflows/create
- Creation wizard loads with Step 1 active

---

### AC-001-07: Loading State

**GIVEN** a user navigates to /workflows
**WHEN** the workflow list API call is in progress
**THEN** a skeleton loader displays with 10 row placeholders
**AND** each placeholder matches the structure of a table row

**Verification:**
- Skeleton displays immediately on page load
- Skeleton rows pulse with animation
- Skeleton disappears when data loads
- No actual data displays during loading

---

### AC-001-08: Empty State

**GIVEN** a user has no workflows in their account
**WHEN** they navigate to /workflows
**THEN** an empty state displays with:
- Illustration or icon
- "No workflows yet" heading
- "Create your first workflow to automate your marketing" description
- "Create Workflow" button

**Verification:**
- Empty state displays centered on page
- Illustration is visually appealing
- CTA button navigates to creation wizard
- No table displays in empty state

---

### AC-001-09: Error State

**GIVEN** a user is on the workflow list page
**WHEN** the API call fails with a 500 error
**THEN** an error state displays with:
- Error icon
- "Unable to load workflows" heading
- "Something went wrong. Please try again." message
- "Retry" button

**Verification:**
- Error state displays immediately on failure
- Retry button triggers API call again
- Multiple retries work correctly
- After successful retry, normal list displays

---

### AC-001-10: Navigate to Workflow Detail

**GIVEN** a user is on the workflow list page
**WHEN** they click on any row in the workflow table
**THEN** they are navigated to /workflows/{id} where {id} is the workflow ID
**AND** the workflow detail page loads with the selected workflow's data

**Verification:**
- Clicking any row navigates to correct detail page
- URL updates with workflow ID
- Detail page displays correct workflow data
- Browser back button returns to list page

---

## AC-002: Workflow Detail View

### AC-002-01: View Workflow Overview

**GIVEN** a user is on the workflow detail page at /workflows/{id}
**THEN** they see:
- Workflow name and description
- Current status badge (Active/Paused/Draft)
- Trigger type and configuration summary
- Visual workflow canvas with all steps
- Performance metrics cards
- Action buttons: Edit, Delete, Duplicate, Export

**Verification:**
- All sections display correct data from API
- Status badge shows correct color
- Canvas renders workflow steps visually
- Metrics show real-time numbers
- All action buttons are present

---

### AC-002-02: Toggle Workflow Status

**GIVEN** a user is viewing an active workflow
**WHEN** they click the status toggle switch
**THEN** a confirmation dialog appears: "Pause this workflow?"
**AND** if they confirm, the workflow status changes to "paused"
**AND** the status badge updates to yellow "Paused"

**Verification:**
- Toggle switch shows current status
- Confirmation dialog prevents accidental toggles
- API call updates status on backend
- Status badge updates immediately
- Toggle switch position updates
- Toast notification confirms status change

---

### AC-002-03: Delete Workflow

**GIVEN** a user is viewing a workflow
**WHEN** they click the "Delete" button
**THEN** a confirmation modal appears with:
- "Delete this workflow?" heading
- "This action cannot be undone." warning
- "Cancel" and "Delete" buttons
**AND** if they confirm, the workflow is deleted
**AND** they are redirected to /workflows

**Verification:**
- Delete button shows warning color (red)
- Confirmation modal prevents accidental deletion
- API call deletes workflow on backend
- Redirect to list page occurs
- Toast notification confirms deletion
- Deleted workflow no longer appears in list

---

### AC-002-04: Duplicate Workflow

**GIVEN** a user is viewing a workflow
**WHEN** they click the "Duplicate" button
**THEN** a copy of the workflow is created
**AND** the copy has name "{Original Name} - Copy"
**AND** the user is navigated to the duplicated workflow's detail page

**Verification:**
- Duplicate button triggers API call
- New workflow created with all same steps
- Name has " - Copy" suffix
- User navigated to new workflow detail
- Toast notification confirms duplication

---

### AC-002-05: Export Workflow

**GIVEN** a user is viewing a workflow
**WHEN** they click the "Export" button
**THEN** a JSON file is downloaded with filename "{workflow-name}.json"
**AND** the file contains the complete workflow configuration including:
- Workflow metadata (name, description, status)
- Trigger configuration
- All action steps with configurations
- Conditions and goals

**Verification:**
- Export button triggers file download
- File downloads with correct name
- JSON file is valid and complete
- File can be used for import (future feature)

---

## AC-003: Visual Workflow Canvas

### AC-003-01: View Workflow Canvas

**GIVEN** a user is on the workflow edit page at /workflows/{id}/edit
**THEN** they see a visual canvas displaying:
- Trigger node at the top (distinct shape/color)
- Action nodes as rectangular cards below
- Connection lines between nodes with directional arrows
- Mini-map in bottom-right corner
- Toolbar at top with: Undo, Redo, Auto-Layout, Fit-to-Screen, Save, Test

**Verification:**
- Canvas renders all workflow steps
- Nodes display with correct icons and labels
- Connections show proper parent-child relationships
- Mini-map shows workflow overview
- All toolbar buttons present and enabled

---

### AC-003-02: Pan Canvas

**GIVEN** a user is viewing the workflow canvas
**WHEN** they click and drag on an empty area
**THEN** the canvas pans in the direction of the drag
**AND** the mini-map updates to show current viewport

**Verification:**
- Mouse drag on empty space pans canvas
- Pan is smooth and responsive
- Mini-map viewport indicator moves
- Panning works beyond canvas boundaries

---

### AC-003-03: Zoom Canvas

**GIVEN** a user is viewing the workflow canvas
**WHEN** they scroll the mouse wheel up
**THEN** the canvas zooms in (up to 200%)
**WHEN** they scroll the mouse wheel down
**THEN** the canvas zooms out (down to 25%)
**AND** the mini-map scales accordingly

**Verification:**
- Mouse wheel zooms canvas smoothly
- Zoom center is at mouse pointer position
- Zoom limits enforced (25% - 200%)
- Mini-map updates scale
- Zoom level indicator displays

---

### AC-003-04: Select Node

**GIVEN** a user is viewing the workflow canvas
**WHEN** they click on a node
**THEN** the node becomes selected with a highlight border
**AND** the configuration panel slides in from the right
**AND** the panel displays the configuration form for that step

**Verification:**
- Clicking node selects it (highlight border)
- Only one node selected at a time
- Configuration panel opens with correct form
- Panel title matches node type
- Clicking empty space deselects node and closes panel

---

### AC-003-05: Drag Node

**GIVEN** a user is viewing the workflow canvas
**WHEN** they click and drag a node
**THEN** the node moves following the mouse
**AND** the node snaps to a grid (20px grid)
**AND** connections update to follow the node

**Verification:**
- Dragging node updates position in real-time
- Node snaps to grid when released
- Connections stay attached to node
- Node cannot be dragged outside canvas bounds
- Mini-map updates node position

---

### AC-003-06: Delete Node

**GIVEN** a user has selected a node on the canvas
**WHEN** they press the Delete key
**THEN** the node is removed from the canvas
**AND** all connections to/from the node are removed
**AND** unsaved changes indicator appears

**Verification:**
- Delete key removes selected node
- Connections to deleted node are removed
- Child nodes reattach to parent (if applicable)
- Unsaved changes dot appears next to workflow name
- Delete can be undone with Ctrl+Z

---

### AC-003-07: Undo and Redo

**GIVEN** a user has made changes to the workflow canvas
**WHEN** they press Ctrl+Z
**THEN** the last change is undone
**WHEN** they press Ctrl+Shift+Z
**THEN** the undone change is redone

**Verification:**
- Undo reverses: node added, node deleted, node moved, connection added
- Redo reapplies undone changes
- History stack maintains up to 50 actions
- Undo button in toolbar also works
- Redo button in toolbar also works
- Keyboard shortcuts work consistently

---

### AC-003-08: Auto-Layout

**GIVEN** a user has a workflow with nodes positioned randomly
**WHEN** they click the "Auto-Layout" button
**THEN** the nodes are reorganized in a vertical hierarchy
**AND** the trigger node is at the top
**AND** child nodes are positioned below their parents
**AND** connections flow vertically downward

**Verification:**
- Auto-Layout button triggers automatic positioning
- Nodes organize in clean vertical layout
- Hierarchy is preserved (parent above children)
- No overlapping nodes
- Connections display without crossing (when possible)

---

### AC-003-09: Fit-to-Screen

**GIVEN** a user is viewing a workflow that is larger than the viewport
**WHEN** they click the "Fit-to-Screen" button
**THEN** the canvas zooms and pans to center all nodes
**AND** all nodes are visible within the viewport
**AND** there is minimal whitespace padding

**Verification:**
- Fit-to-Screen button centers workflow
- All nodes visible after click
- Zoom level adjusts to fit workflow
- Padding is roughly 50px around all nodes
- Mini-map viewport covers entire workflow

---

### AC-003-10: Mini-Map Navigation

**GIVEN** a user is viewing the workflow canvas
**WHEN** they click on a position in the mini-map
**THEN** the main canvas pans to center that position
**AND** the viewport indicator in the mini-map updates

**Verification:**
- Clicking mini-map pans main canvas
- Clicked position becomes center of viewport
- Viewport indicator rectangle updates
- Mini-map shows relative positions of all nodes
- Mini-map updates when nodes are moved

---

## AC-004: Workflow Builder Sidebar

### AC-004-01: View Sidebar

**GIVEN** a user is on the workflow edit page
**THEN** they see a sidebar on the left with:
- Search input at top
- Accordion categories: Triggers, Actions, Logic, Advanced
- List of steps within each category
- Each step shows icon and name

**Verification:**
- Sidebar is visible and collapsible
- All categories display in correct order
- Steps display with icons and names
- Search input focuses when sidebar opens
- Categories expand/collapse with smooth animation

---

### AC-004-02: Expand Category

**GIVEN** a user is viewing the sidebar with all categories collapsed
**WHEN** they click on the "Actions" category header
**THEN** the Actions category expands
**AND** all 25+ action types are listed
**AND** other categories remain collapsed

**Verification:**
- Clicking category header toggles expand/collapse
- Only one category can be expanded at a time (accordion)
- Expanded category shows all steps
- Collapse icon rotates when expanded
- Animation is smooth (300ms)

---

### AC-004-03: Search Steps

**GIVEN** a user is viewing the sidebar
**WHEN** they type "email" in the search input
**THEN** all categories expand
**AND** only steps matching "email" are highlighted
**AND** non-matching steps are dimmed

**Verification:**
- Search filters steps in real-time
- Matching steps remain fully visible
- Non-matching steps are dimmed (opacity 0.3)
- Clear button (X) appears in search input
- Clearing search resets all steps to normal visibility

---

### AC-004-04: Drag Step to Canvas

**GIVEN** a user is viewing the sidebar and the canvas
**WHEN** they drag a step from the sidebar onto the canvas
**THEN** a ghost element follows the mouse
**AND** the canvas highlights valid drop targets
**AND** when they release, the step is added as a new node
**AND** the node is automatically connected to the selected node or workflow end

**Verification:**
- Drag starts with mousedown on sidebar item
- Ghost element shows step icon and name
- Valid drop targets highlight with blue border
- Dropping on canvas adds node at mouse position
- Node auto-connects if dropped near existing connection
- Dropping near a node connects to that node

---

### AC-004-05: Click Step to Add

**GIVEN** a user is viewing the sidebar
**WHEN** they click on a step (not dragging)
**THEN** the step is added to the end of the workflow
**AND** the new node is selected and configuration panel opens

**Verification:**
- Click adds step to workflow
- Node appears at end of flow
- Node is automatically selected
- Configuration panel opens for new step
- Action can be undone with Ctrl+Z

---

## AC-005: Configuration Panel

### AC-005-01: View Trigger Configuration

**GIVEN** a user has selected the trigger node
**THEN** the configuration panel displays:
- Trigger type dropdown (26 options)
- Configuration fields based on selected trigger type
- Trigger test button
- Save and Cancel buttons

**Verification:**
- Panel title is "Configure Trigger"
- Trigger type dropdown shows all 26 trigger types
- Fields change based on selected type
- All required fields marked with asterisk
- Validation errors display inline
- Save button disabled when form invalid

---

### AC-005-02: Configure Contact Created Trigger

**GIVEN** a user is configuring a "Contact Created" trigger
**THEN** they see:
- Filter by tag (multi-select dropdown)
- Filter by source (dropdown: Manual, Import, Form, API)
- Filter by custom field (field selector, operator, value)

**Verification:**
- All filter fields display
- Multi-select allows selecting multiple tags
- Source dropdown shows all options
- Custom field filter shows available fields
- Validation enforces at least one filter or no filter (both valid)

---

### AC-005-03: Configure Send Email Action

**GIVEN** a user is configuring a "Send Email" action
**THEN** they see:
- Template selector (or "Custom Email" radio button)
- Subject line input (with variable picker)
- Body editor (rich text or HTML)
- From email dropdown
- From name input
- Attachment upload (max 25MB, max 10 files)
- Test send button

**Verification:**
- Template selector loads available templates
- Selecting template populates subject and body
- Variable picker button inserts {{variable}} syntax
- Body editor supports rich text formatting
- Attachment upload shows file name and size
- Test send opens modal with recipient input
- Validation enforces required fields

---

### AC-005-04: Configure Wait Action

**GIVEN** a user is configuring a "Wait" action
**THEN** they see:
- Duration input (number)
- Unit dropdown (Minutes, Hours, Days, Weeks)

**Verification:**
- Duration input accepts numbers only
- Duration range: 1-10080 minutes (max 1 week)
- Unit dropdown shows all options
- Validation enforces duration within range
- Preview shows "Wait for X [unit]"

---

### AC-005-05: Configure If/Else Condition

**GIVEN** a user is configuring an "If/Else Condition" action
**THEN** they see:
- Field selector (dropdown)
- Operator dropdown (equals, not equals, contains, greater than, less than)
- Value input
- "Add condition" button
- Logic selector (AND/OR)
- Branch configuration (Yes path, No path)

**Verification:**
- Field selector shows available contact fields
- Operator dropdown shows all options
- Value input type changes based on field (text, number, date)
- Multiple conditions can be added
- Conditions can be removed
- Logic selector applies to all conditions
- Branch paths display as separate nodes on canvas

---

### AC-005-06: Insert Variables

**GIVEN** a user is configuring an action that supports variables (e.g., Send Email)
**WHEN** they click the "Variable" button
**THEN** a variable picker dropdown appears
**AND** it shows available variables: {{contact.name}}, {{contact.email}}, {{contact.phone}}, etc.
**WHEN** they click a variable
**THEN** the variable is inserted at cursor position in the field

**Verification:**
- Variable button appears on text fields
- Dropdown shows all relevant variables for the step
- Clicking variable inserts at cursor position
- Variables display with {{variable}} syntax
- Variable preview shows sample data on hover

---

### AC-005-07: Test Trigger

**GIVEN** a user is configuring a trigger
**WHEN** they click the "Test Trigger" button
**THEN** the system simulates the trigger with sample data
**AND** a result modal displays:
- "Trigger executed successfully" message
- Sample contact data that would trigger the workflow
- "View matched contacts" link

**Verification:**
- Test button calls backend test endpoint
- Modal displays with success or error
- Sample data shows realistic contact information
- View matched contacts opens search with filter applied
- Modal can be closed with X or ESC key

---

### AC-005-08: Save Step Configuration

**GIVEN** a user has modified a step's configuration
**WHEN** they click the "Save" button
**THEN** the step configuration is saved
**AND** the configuration panel closes
**AND** the node on the canvas updates its label to reflect changes
**AND** unsaved changes indicator disappears
**AND** a toast notification confirms "Step saved"

**Verification:**
- Save button calls backend API
- Loading state shows on button during save
- Panel closes on successful save
- Node label updates with new summary
- Success toast displays
- Error toast displays if save fails
- Panel remains open if save fails

---

## AC-006: Workflow Creation Wizard

### AC-006-01: Start Creation Wizard

**GIVEN** a user clicks "Create Workflow" from the list page
**THEN** they see the creation wizard at /workflows/create
**AND** Step 1 displays: "Choose Starting Point"
**AND** Three options show: "Start from scratch", "Use template", "Import from existing"

**Verification:**
- Wizard displays centered on page
- Progress indicator shows "Step 1 of 4"
- Three options display as cards with icons
- Back button is disabled (first step)
- Next button is disabled (option required)
- Cancel button shows with X icon

---

### AC-006-02: Start from Scratch

**GIVEN** a user is on Step 1 of the creation wizard
**WHEN** they click "Start from scratch"
**THEN** they advance to Step 2: "Configure Basic Settings"
**AND** they see:
- Workflow name input (required, 3-100 characters)
- Description textarea (optional, max 1000 characters)
- Name uniqueness validation

**Verification:**
- Name input validates on blur
- Error shows if name < 3 or > 100 characters
- Error shows if name already exists in account
- Description shows character count
- Next button enables when name is valid
- Back button returns to Step 1

---

### AC-006-03: Select Template

**GIVEN** a user is on Step 1 of the creation wizard
**WHEN** they click "Use template"
**THEN** they advance to the template marketplace
**AND** they see a grid of template cards
**AND** filters for: Lead Nurturing, Customer Onboarding, Appointment Reminders, Sales Pipeline, E-commerce

**Verification:**
- Template marketplace loads with all templates
- Templates display as cards with preview image
- Category filters work correctly
- Search filters templates by name or use case
- Clicking template opens preview modal
- "Use this template" button advances to Step 4

---

### AC-006-04: Configure Trigger

**GIVEN** a user is on Step 2: "Configure Basic Settings" (starting from scratch)
**WHEN** they click "Next" (with valid name)
**THEN** they advance to Step 3: "Select Trigger"
**AND** they see:
- Trigger type selector with search and categories
- Trigger configuration based on selected type
- Trigger test button

**Verification:**
- Trigger selector shows all 26 trigger types
- Categories organize triggers
- Search filters triggers
- Selecting trigger shows configuration fields
- Test button simulates trigger
- Next button enables when trigger configured

---

### AC-006-05: Review and Create

**GIVEN** a user has completed Steps 1-3 of the creation wizard
**WHEN** they click "Next" on Step 3
**THEN** they advance to Step 4: "Review and Create"
**AND** they see:
- Summary of workflow configuration
- "Create and start editing" button
- "Create as draft" button

**Verification:**
- Summary displays all configured settings
- Summary shows workflow name, description, trigger type
- "Create and start editing" creates workflow and opens editor
- "Create as draft" creates workflow and returns to list
- Both buttons create workflow successfully
- Toast notification confirms creation

---

### AC-006-06: Cancel Creation

**GIVEN** a user is on any step of the creation wizard
**WHEN** they click the "Cancel" button
**THEN** a confirmation dialog appears: "Discard workflow creation?"
**AND** if they confirm, they are redirected to /workflows

**Verification:**
- Cancel button shows on all steps
- Confirmation dialog prevents accidental cancellation
- Confirming redirects to workflow list
- No workflow is created
- Dialog can be cancelled (returns to wizard)

---

## AC-007: Workflow Analytics

### AC-007-01: View Analytics Dashboard

**GIVEN** a user is on the workflow detail page
**WHEN** they click the "Analytics" tab
**THEN** they see the analytics dashboard with:
- Overview metrics cards: Total Enrolled, Currently Active, Completed, Drop-off Rate
- Funnel visualization chart
- Performance charts: Enrollments over time, Completions over time
- Real-time execution log

**Verification:**
- All metrics cards display correct numbers
- Metrics update with real-time data
- Funnel chart shows drop-off at each step
- Line charts show trends over time
- Charts are interactive (hover tooltips)
- Date range selector filters all charts

---

### AC-007-02: View Funnel Visualization

**GIVEN** a user is viewing the analytics dashboard
**THEN** the funnel chart displays:
- Each workflow step as a horizontal bar
- Bar width proportional to contacts who reached that step
- Drop-off percentage displayed between steps
- Color coding: Green (high completion), Yellow (medium), Red (high drop-off)

**Verification:**
- Funnel chart displays all steps vertically
- Bar widths show relative volumes
- Hover displays step name and exact counts
- Clicking step highlights in execution log below
- Drop-off percentage calculated correctly

---

### AC-007-03: View Real-Time Execution Log

**GIVEN** a user is viewing the analytics dashboard
**THEN** the execution log displays:
- Table of recent executions
- Columns: Execution ID, Contact, Status, Started At, Current Step, Duration
- Status indicators: Success (green check), Error (red X), In Progress (blue spinner)
- Auto-refresh every 5 seconds via SSE

**Verification:**
- Execution log updates in real-time
- New executions appear at top
- In Progress executions update current step
- Completed executions stop updating
- SSE connection reconnects if dropped
- Filter by status works correctly

---

### AC-007-04: Export Analytics

**GIVEN** a user is viewing the analytics dashboard
**WHEN** they click the "Export" button
**THEN** a dropdown appears with: "Export as CSV", "Export as PDF"
**WHEN** they select "Export as CSV"
**THEN** a CSV file downloads with all execution data

**Verification:**
- Export button shows with download icon
- CSV download includes all visible data
- CSV format is valid and opens in Excel
- PDF export generates formatted report
- Date range filter applies to export
- Export filename includes date range

---

## AC-008: Execution Logs

### AC-008-01: View Execution Logs

**GIVEN** a user is on the workflow detail page
**WHEN** they click the "Executions" tab
**THEN** they see a paginated table of execution logs
**AND** columns display: Execution ID, Contact Name/Email, Status, Started At, Completed At/Current Step, Duration

**Verification:**
- Table displays 25 executions per page
- Status icons show correct colors
- Execution IDs are clickable links
- Date/time formats are readable
- Duration shows in human-readable format (e.g., "2h 15m")

---

### AC-008-02: Filter Execution Logs

**GIVEN** a user is viewing the execution logs table
**WHEN** they select "Error" from the status filter
**THEN** the table displays only executions with status "Error"
**AND** a "Error" filter chip appears

**Verification:**
- Status filter shows: All, Success, Error, In Progress, Cancelled
- Selecting status filters table
- Filter chip appears with remove button
- Date range picker filters by date
- Filters work together (combined)

---

### AC-008-03: View Execution Detail

**GIVEN** a user is viewing the execution logs table
**WHEN** they click on an execution ID
**THEN** a modal opens with:
- Execution summary (contact info, status, duration)
- Step-by-step execution timeline
- Each step shows: name, status, timestamp, duration
- Error messages and stack traces (if failed)
- Retry failed step button (if error)
- Cancel execution button (if in progress)

**Verification:**
- Modal displays with correct execution data
- Timeline shows all steps in order
- Step statuses have color coding
- Hovering step shows details
- Error messages are clear and actionable
- Retry button triggers retry API call
- Cancel button cancels in-progress execution

---

## AC-009: Version History

### AC-009-01: View Version History

**GIVEN** a user is on the workflow detail page
**WHEN** they click the "Versions" tab
**THEN** they see a list of all workflow versions
**AND** each version shows: Version Number, Created At, Created By, Change Description, Actions (View, Restore, Compare)

**Verification:**
- Version list displays in reverse chronological order
- Current version highlighted
- All versions show correct metadata
- Action buttons work correctly

---

### AC-009-02: Compare Versions

**GIVEN** a user is viewing the version history
**WHEN** they select two versions and click "Compare"
**THEN** a side-by-side diff view displays
**AND** additions are highlighted in green
**AND** deletions are highlighted in red
**AND** unchanged content is shown in neutral color

**Verification:**
- Diff view loads selected versions
- Side-by-side layout shows both versions
- Highlighting is clear and readable
- Changes are easy to identify
- Scroll position syncs between panels

---

### AC-009-03: Restore Version

**GIVEN** a user is viewing the version history
**WHEN** they click "Restore" on a past version
**THEN** a confirmation dialog appears: "Restore this version?"
**AND** the dialog shows: "This will create a new version with the restored content."
**WHEN** they confirm
**THEN** a new version is created with the restored content
**AND** the user remains on the Versions tab
**AND** a toast confirms "Version restored as v{number}"

**Verification:**
- Restore button shows confirmation dialog
- Dialog explains restore behavior
- Confirming creates new version (not overwrites)
- New version appears at top of list
- Toast notification confirms restore
- Workflow detail page reflects restored content

---

## AC-010: Bulk Enrollment

### AC-010-01: Open Bulk Enrollment Modal

**GIVEN** a user is viewing a workflow detail page
**WHEN** they click the "Enroll Contacts" button
**THEN** a modal opens with:
- Contact search input
- Filters: Tags, Pipeline Stage, Custom Field
- Contact list with multi-select checkboxes
- "Select all from current filter" option
- Enrollment options: Starting step, Skip existing, Schedule for later
- Review summary with selected count
- "Enroll Contacts" button

**Verification:**
- Modal opens with full height and scrollable content
- Search input filters contacts in real-time
- Filters reduce contact list correctly
- Multi-select checkboxes work independently
- Select all selects all visible contacts
- Selected count updates dynamically
- Enrollment options show correct defaults

---

### AC-010-02: Select Contacts for Enrollment

**GIVEN** a user has the bulk enrollment modal open
**WHEN** they search for "john"
**THEN** the contact list filters to show contacts matching "john"
**WHEN** they select 5 contacts using checkboxes
**THEN** the selected count updates to "5 contacts selected"

**Verification:**
- Search filters by name or email
- Checkboxes toggle selection
- Selected contacts remain selected when filtering
- Select all selects all matching current filter
- Deselect all clears all selections
- Selected count updates immediately

---

### AC-010-03: Configure Enrollment Options

**GIVEN** a user has selected contacts for bulk enrollment
**WHEN** they configure:
- Starting step: "Wait 1 day" (not the trigger)
- Skip existing enrollments: Enabled
- Schedule for later: Disabled
**THEN** these options are applied when enrolling

**Verification:**
- Starting step dropdown shows all workflow steps
- Skip existing toggle shows current state
- Schedule for later shows date/time picker when enabled
- Options persist when switching between steps
- Validation enforces required options

---

### AC-010-04: Complete Bulk Enrollment

**GIVEN** a user has selected 100 contacts and configured options
**WHEN** they click "Enroll Contacts"
**THEN** a progress bar displays showing enrollment progress
**AND** contacts are enrolled in batches of 10
**AND** when complete, a summary displays: "Enrolled 95 contacts, 5 failed"
**AND** failed enrollments show error messages

**Verification:**
- Progress bar shows accurate percentage
- Enrollment happens in background
- Modal cannot be closed during enrollment
- Summary shows success and error counts
- Failed enrollments list errors
- Close button enabled after completion
- Toast notification confirms completion

---

## AC-011: Performance and Accessibility

### AC-011-01: Page Load Performance

**GIVEN** a user navigates to any workflows page
**THEN** the page loads within performance targets:
- First Contentful Paint (FCP): < 1.5s
- Largest Contentful Paint (LCP): < 2.5s
- Time to Interactive (TTI): < 3.5s
- Cumulative Layout Shift (CLS): < 0.1

**Verification:**
- Run Lighthouse audit on all major pages
- All Core Web Vitals meet targets
- No layout shifts during page load
- Page remains interactive during loading

---

### AC-011-02: Keyboard Navigation

**GIVEN** a user navigates the application using only a keyboard
**THEN** they can:
- Tab through all interactive elements in logical order
- Activate buttons and links with Enter/Space
- Close modals with Escape key
- Navigate lists with arrow keys
- Focus indicators are visible on all elements

**Verification:**
- Tab order follows visual layout
- No keyboard traps exist
- Focus is visible on all interactive elements
- All functionality accessible without mouse
- Skip to content link works

---

### AC-011-03: Screen Reader Support

**GIVEN** a user uses a screen reader (NVDA or JAWS)
**THEN** they can:
- Understand the purpose of all interactive elements
- Navigate the workflow canvas with spatial information
- Hear status updates and error messages
- Complete all tasks using only the screen reader

**Verification:**
- Test with NVDA (Windows) and VoiceOver (Mac)
- All images have alt text or are decorative
- ARIA labels describe all icons
- Live regions announce dynamic content
- Semantic HTML used throughout

---

### AC-011-04: Color Contrast

**GIVEN** a user views any page in the application
**THEN** all text meets WCAG AA contrast ratios:
- Normal text (< 18pt): Minimum 4.5:1 contrast
- Large text (≥ 18pt): Minimum 3:1 contrast
- Icons and graphics: Minimum 3:1 contrast

**Verification:**
- Run contrast checker on all pages
- No text fails contrast requirements
- Color is not the only indicator of state
- Focus indicators meet contrast requirements

---

### AC-011-05: Responsive Design

**GIVEN** a user views the application on different screen sizes
**THEN** the layout adapts correctly:
- Desktop (1920x1080): Full layout with canvas, sidebar, config panel
- Laptop (1366x768): Collapsible sidebar, canvas + config panel
- Tablet (768x1024): Single column with tab navigation
- Mobile (375x667): Vertical list view (canvas disabled)

**Verification:**
- Test on actual devices at each breakpoint
- Layout transitions are smooth
- All features remain accessible on tablet
- Mobile view shows warning for canvas features
- Touch targets are minimum 44x44px on mobile

---

## AC-012: Error Handling

### AC-012-01: Validation Errors

**GIVEN** a user submits a form with invalid data
**THEN** inline error messages display below each invalid field
**AND** a form summary displays at the top with links to each error
**AND** invalid fields are highlighted with red border
**AND** the save button is disabled until all errors are fixed

**Verification:**
- Validation triggers on blur and submit
- Error messages are clear and actionable
- Form summary scrolls to first error on click
- Focus moves to first invalid field
- Clearing errors re-enables save button

---

### AC-012-02: Network Errors

**GIVEN** a user is interacting with the application
**WHEN** a network error occurs (no connection)
**THEN** a toast notification appears: "Unable to connect. Please check your internet connection."
**AND** an offline indicator displays in the header
**AND** actions are queued when offline
**AND** queued actions retry when connection restores

**Verification:**
- Toast displays on network failure
- Offline indicator is visible in header
- Queued actions display in sidebar
- Reconnection triggers retry of queued actions
- Toast confirms successful retry

---

### AC-012-03: Server Errors

**GIVEN** a user is performing an action
**WHEN** the server returns a 500 error
**THEN** a toast notification appears: "Something went wrong. Please try again."
**AND** a retry button displays in the toast
**AND** if they retry, the action attempts again

**Verification:**
- Toast displays with error icon
- Retry button triggers action again
- Multiple retries work correctly
- If retry fails, toast suggests contacting support
- Error is logged for debugging

---

### AC-012-04: Authentication Errors

**GIVEN** a user's session has expired
**WHEN** they perform any action
**THEN** they are redirected to the Clerk login page
**AND** a toast displays: "Session expired. Please log in again."
**AND** after login, they are returned to their original location

**Verification:**
- 401 responses trigger redirect
- Toast notification displays before redirect
- Login page displays correctly
- Successful login returns to original page
- State is preserved if possible (draft data)

---

## Traceability Tags

- TAG:SPEC-FRN-001
- TAG:ACCEPTANCE-CRITERIA
- TAG:AC-001-THROUGH-AC-012
- TAG:GIVEN-WHEN-THEN
- TAG:DEFINITION-OF-DONE
- TAG:VERIFICATION-TEST-PLAN
