# SPEC-FRN-001: Workflows Module - Frontend User Interface

## Metadata

| Field | Value |
|-------|-------|
| **SPEC ID** | SPEC-FRN-001 |
| **Title** | Workflows Module - Frontend User Interface |
| **Module** | workflows-frontend |
| **Domain** | frontend-automation |
| **Priority** | Critical |
| **Status** | Planned |
| **Created** | 2026-02-07 |
| **Version** | 1.0.0 |
| **Backend References** | SPEC-WFL-001 through SPEC-WFL-012 |

---

## Overview

This specification defines the comprehensive frontend user interface for the GoHighLevel Clone Workflows Module. The frontend provides a visual, drag-and-drop workflow builder enabling users to create, configure, and manage automation workflows with 50+ triggers and 25+ actions through an intuitive node-based canvas interface.

**Scope:** Complete frontend implementation connecting to 70+ backend API endpoints across 12 workflow SPECs.

**Target Users:** Marketing agencies, SMBs, and SaaS businesses requiring automation capabilities.

---

## Environment

### Technical Environment

**Frontend Framework:**
- Next.js 14+ with App Router
- React 19+ with Server Components
- TypeScript 5+

**UI Component Library:**
- Shadcn UI (Radix UI primitives + Tailwind CSS)
- Lucide React for icons
- Recharts/Tremor for analytics charts

**State Management:**
- Zustand for global client state
- React Context for component-level state
- TanStack Query (React Query) for server state

**Forms & Validation:**
- React Hook Form for form management
- Zod for schema validation

**Data Fetching:**
- TanStack Query (React Query) for API calls
- Axios or Fetch API for HTTP requests

**Drag & Drop:**
- @dnd-kit/core for drag-and-drop functionality
- React Flow Library for visual node canvas

**Animation:**
- Framer Motion for micro-interactions
- Shadcn UI animations for transitions

**Development Tools:**
- ESLint for linting
- Prettier for code formatting
- TypeScript for type safety

### Runtime Environment

**Browser Support:**
- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile: iOS Safari 14+, Chrome Android 14+

**Authentication:**
- Clerk for user authentication
- Protected routes via middleware
- JWT token management

**API Integration:**
- REST API endpoints at /api/v1/
- Base URL configurable via environment variable
- Bearer token authentication

### Deployment Environment

**Target Platforms:**
- Vercel (primary)
- AWS S3 + CloudFront (alternative)
- Docker containers (self-hosted)

**Performance Targets:**
- First Contentful Paint (FCP): < 1.5s
- Largest Contentful Paint (LCP): < 2.5s
- Time to Interactive (TTI): < 3.5s
- Cumulative Layout Shift (CLS): < 0.1

---

## Assumptions

### Backend Assumptions

**Assumption 1:** All 70+ backend API endpoints documented in SPEC-WFL-001 through SPEC-WFL-012 are fully implemented and operational.

**Confidence Level:** High

**Evidence Basis:** Backend SPECs are marked as 100% complete.

**Risk if Wrong:** Frontend implementation blocked by missing or non-functional endpoints.

**Validation Method:** API health check and endpoint availability verification before frontend development begins.

**Assumption 2:** Backend API follows OpenAPI 3.0 specification with consistent error response format (RFC 7807 Problem Details).

**Confidence Level:** High

**Evidence Basis:** Tech.md states OpenAPI 3.0 documentation requirement.

**Risk if Wrong:** Inconsistent error handling increases frontend complexity and error rates.

**Validation Method:** Review OpenAPI specification and test error responses for sample endpoints.

**Assumption 3:** Real-time updates for workflow execution logs are provided via Server-Sent Events (SSE) endpoint at GET /api/v1/workflows/{id}/analytics/stream.

**Confidence Level:** Medium

**Evidence Basis:** SPEC-WFL-009 mentions SSE for real-time analytics.

**Risk if Wrong:** Real-time features require polling fallback implementation.

**Validation Method:** Test SSE endpoint connectivity and message format.

### User Experience Assumptions

**Assumption 4:** Target users have experience with marketing automation platforms (e.g., GoHighLevel, HubSpot, ActiveCampaign).

**Confidence Level:** Medium

**Evidence Basis:** Product.md targets agencies and SMBs likely familiar with automation tools.

**Risk if Wrong:** Onboarding and tutorial requirements increase significantly.

**Validation Method:** User interviews and usability testing with target audience.

**Assumption 5:** Users primarily access workflows module on desktop screens (1920x1080 and 1366x768).

**Confidence Level:** High

**Evidence Basis:** Complex workflow builder requires screen real estate typical of desktop use.

**Risk if Wrong:** Mobile responsive design requires additional iteration.

**Validation Method:** Analytics data from similar platforms showing device distribution.

**Assumption 6:** Users expect visual drag-and-drop interface similar to Zapier/Make rather than form-based configuration.

**Confidence Level:** High

**Evidence Basis:** Product.md mentions "visual automation building" and industry standard.

**Risk if Wrong:** Form-based fallback UI required as alternative.

**Validation Method:** Competitive analysis and user preference surveys.

### Technical Assumptions

**Assumption 7:** Clerk authentication provides user context including account_id for multi-tenancy.

**Confidence Level:** High

**Evidence Basis:** Tech.md specifies Clerk for authentication with account_id in JWT claims.

**Risk if Wrong:** Tenant isolation fails causing data access violations.

**Validation Method:** Authentication flow testing with Clerk integration.

**Assumption 8:** Browser localStorage can store workflow draft state up to 5MB without performance degradation.

**Confidence Level:** High

**Evidence Basis:** Modern browsers support 5-10MB localStorage quota.

**Risk if Wrong:** Draft auto-save fails requiring IndexedDB implementation.

**Validation Method:** localStorage quota testing across target browsers.

**Assumption 9:** Shadcn UI components provide sufficient accessibility (WCAG 2.1 AA) out of the box.

**Confidence Level:** Medium

**Evidence Basis:** Shadcn UI built on Radix UI with accessibility focus.

**Risk if Wrong:** Additional ARIA attributes and keyboard navigation required.

**Validation Method:** Accessibility audit with screen readers and keyboard-only navigation.

---

## EARS Requirements

### REQ-FRN-001-01: Workflow List Page (Event-Driven)

**WHEN** a user navigates to /workflows,
**THEN** the system shall display a paginated table of all workflows for the current account,
**RESULTING IN** an overview of workflow status and performance metrics,
**IN STATE** loaded.

**Acceptance Criteria:**
- Table displays columns: Name, Status, Trigger Type, Active Contacts, Completion Rate, Last Modified
- Status badges with color coding: Active (green), Draft (gray), Paused (yellow)
- Row click navigates to workflow detail view
- Search by workflow name with debounced input (300ms)
- Filter by status (All, Active, Draft, Paused)
- Sort by Name, Status, Last Modified (ascending/descending)
- Pagination with configurable page size (10, 25, 50, 100)
- Create Workflow button (primary CTA) opens creation wizard

### REQ-FRN-001-02: Workflow List Loading States (State-Driven)

**IF** the workflow list is loading,
**THEN** the system shall display a skeleton loader with 10 row placeholders.

**IF** the workflow list is empty,
**THEN** the system shall display an empty state with illustration and "Create your first workflow" CTA.

**IF** the workflow list fails to load,
**THEN** the system shall display an error state with retry button and error message.

### REQ-FRN-001-03: Workflow Detail View (Event-Driven)

**WHEN** a user clicks on a workflow row from the list view,
**THEN** the system shall navigate to /workflows/{id} and display:
- Workflow name and description
- Current status indicator with toggle (Active/Paused)
- Trigger configuration summary
- Visual workflow canvas with all steps
- Performance metrics (enrolled, active, completed, drop-off rate)
- Action buttons: Edit, Delete, Duplicate, Export

**RESULTING IN** comprehensive workflow overview and management interface,
**IN STATE** loaded.

### REQ-FRN-001-04: Visual Workflow Canvas (Ubiquitous)

The system shall **always** provide a node-based visual canvas for workflow configuration with:

**Canvas Features:**
- Drag-and-drop step addition from sidebar palette
- Connection lines between steps with directional arrows
- Pan and zoom functionality (mouse wheel to zoom, click-drag to pan)
- Mini-map navigation in bottom-right corner
- Auto-layout button to organize steps vertically
- Fit-to-screen button to center workflow
- Undo/redo toolbar with keyboard shortcuts (Ctrl+Z, Ctrl+Shift+Z)
- Save button with unsaved changes indicator
- Test workflow button with execution panel

**Node Representation:**
- Trigger node: Distinct shape/color at workflow start
- Action nodes: Rectangular cards with icon, title, and summary
- Condition nodes: Diamond shape with branch indicators
- Wait nodes: Clock icon with duration display
- Goal nodes: Flag icon with completion criteria

**Node Interactions:**
- Click to select and open configuration panel
- Drag to reposition (snap to grid)
- Delete with keyboard (Delete/Backspace) or context menu
- Copy/paste with keyboard shortcuts (Ctrl+C, Ctrl+V)
- Hover displays step summary tooltip

### REQ-FRN-001-05: Workflow Builder Sidebar (Event-Driven)

**WHEN** a user opens the workflow builder,
**THEN** the system shall display a collapsible sidebar with step categories:

**Categories:**
- **Triggers** (26 types): Contact Created, Form Submitted, Pipeline Changed, Appointment Booked, Payment Received, etc.
- **Actions** (25+ types): Send Email, Send SMS, Add Tag, Update Field, Wait, Webhook, etc.
- **Logic** (3 types): If/Else Condition, Split Test, Goal
- **Advanced** (4 types): Custom Code, API Call, Wait Until, Loop

**Interaction:**
- Expandable accordion categories
- Search input to filter steps
- Drag step from sidebar to canvas to add
- Click step to add to end of workflow
- Hover displays step description and required fields

### REQ-FRN-001-06: Trigger Configuration Panel (Event-Driven)

**WHEN** a user clicks on the trigger node,
**THEN** the system shall open a configuration panel with:

**Panel Structure:**
- Trigger type dropdown (26 options)
- Configuration fields based on selected trigger type
- Trigger test button to simulate execution
- Save and Cancel buttons

**Trigger-Specific Configurations:**

*Contact Triggers:*
- Contact Created: Filter by tag, source, or custom field
- Contact Updated: Field change conditions
- Tag Added: Tag selector with multi-select
- Tag Removed: Tag selector with multi-select

*Form Triggers:*
- Form Submitted: Form selector, field filters

*Pipeline Triggers:*
- Pipeline Stage Changed: Pipeline selector, stage selector
- Pipeline Stage Entered: Pipeline selector, stage selector

*Appointment Triggers:*
- Appointment Booked: Calendar selector, appointment type filter
- Appointment Cancelled: Calendar selector
- Appointment Completed: Calendar selector
- Appointment No-Show: Calendar selector

*Payment Triggers:*
- Payment Received: Product/service filter, amount threshold
- Payment Failed: Product/service filter
- Subscription Created: Product selector
- Subscription Cancelled: Product selector

*Communication Triggers:*
- Email Opened: Campaign/message selector
- Email Clicked: Campaign/message selector, link filter
- SMS Replied: Message selector
- Call Completed: Call outcome filter

*Time Triggers:*
- Specific Date/Time: Date picker, time picker
- Recurring: Schedule builder (daily, weekly, monthly)
- Birthday: Contact birthday field
- Anniversary: Date field selector, interval (yearly)

**Validation:**
- Required fields marked with asterisk
- Real-time validation with error messages
- Save button disabled until valid

### REQ-FRN-001-07: Action Configuration Panel (Event-Driven)

**WHEN** a user clicks on an action node,
**THEN** the system shall open a configuration panel with action-specific settings:

**Communication Actions:**

*Send Email:*
- Template selector or custom email builder
- Subject line with personalization variables {{contact.name}}
- Body editor with rich text or HTML
- From name and email dropdown
- Attachment upload (max 25MB)
- Test send button

*Send SMS:*
- Message template selector or custom message
- Personalization variables support
- Character counter (160 per segment)
- Test send button

*Send Voice Broadcast:*
- Audio file upload or text-to-speech
- Recipient filter

*Send Facebook Message:*
- Message template or custom message
- Image attachment

*Make Call:*
- Phone number field (dynamic variable support)
- Call script display

**CRM Actions:**

*Add Tag:*
- Tag selector with multi-select
- Create new tag option

*Remove Tag:*
- Tag selector with multi-select

*Set Custom Field:*
- Field selector
- Value input (text, number, date, dropdown)
- Dynamic variable support

*Add to Pipeline:*
- Pipeline selector
- Stage selector

*Change Pipeline Stage:*
- Pipeline selector
- Stage selector

*Assign to User:*
- User selector dropdown
- Assignment notification toggle

**Timing Actions:**

*Wait:*
- Duration input
- Unit selector (minutes, hours, days, weeks)
- Maximum wait duration cap

*Wait Until:*
- Date field selector
- Specific date/time picker
- Timezone selector

*Schedule:*
- Date and time picker
- Timezone selector

**Logic Actions:**

*If/Else Condition:*
- Field selector
- Operator dropdown (equals, not equals, contains, greater than, less than)
- Value input
- Branch path configuration
- Add multiple conditions with AND/OR logic

*Split Test:*
- Number of branches (2-5)
- Branch percentage distribution
- Branch names

*Goal:*
- Goal completion criteria
- Success path configuration
- Goal timeout setting

**Internal Actions:**

*Create Task:*
- Task title
- Description
- Assigned user
- Due date
- Priority

*Send Internal Notification:*
- User selector
- Notification message

**Webhook Actions:**

*Webhook Call:*
- HTTP method (GET, POST, PUT, PATCH, DELETE)
- URL field with variable support
- Headers (key-value pairs)
- Body JSON builder
- Authentication type (None, Bearer Token, Basic Auth, Custom)
- Retry configuration (count, interval)
- Test webhook button

**Validation:**
- Field validation based on action type
- Real-time preview with sample data
- Required field indicators

### REQ-FRN-001-08: Workflow Creation Wizard (Event-Driven)

**WHEN** a user clicks "Create Workflow" from the list view,
**THEN** the system shall launch a multi-step creation wizard:

**Step 1: Choose Starting Point**
- Start from scratch
- Use template (pre-built workflow templates)
- Import from existing workflow (duplicate)

**Step 2: Configure Basic Settings** (if starting from scratch)
- Workflow name input (3-100 characters)
- Description textarea (optional, max 1000 characters)
- Name uniqueness validation

**Step 3: Select Trigger** (if starting from scratch)
- Trigger type selection with search and categories
- Trigger configuration based on selection

**Step 4: Review and Create**
- Summary of workflow configuration
- Create and start editing button
- Create as draft button

**Navigation:**
- Back button between steps
- Progress indicator (Step 1 of 4)
- Cancel button with confirmation dialog
- Save draft option available on all steps

### REQ-FRN-001-09: Workflow Template Marketplace (Event-Driven)

**WHEN** a user selects "Use template" from the creation wizard,
**THEN** the system shall display template marketplace with:

**Template Gallery:**
- Grid layout with template cards
- Template preview (name, description, preview image, use case)
- Category filters (Lead Nurturing, Customer Onboarding, Appointment Reminders, etc.)
- Search by template name or use case
- Template rating and usage count

**Template Preview:**
- Click template card to open preview modal
- Visual workflow diagram preview
- Step-by-step breakdown
- Required integrations list
- One-click instantiation button
- Customize before creating option

**Template Categories:**

*Lead Nurturing:*
- New lead welcome series
- Re-engagement campaign
- Lead qualification workflow

*Customer Onboarding:*
- New customer onboarding
- Product training sequence
- Check-in workflow

*Appointment Management:*
- Appointment confirmation
- Reminder sequence (24hr, 2hr, 15min)
- No-show follow-up

*Sales Pipeline:*
- New lead to pipeline
- Stage change notifications
- Deal won/lost workflows

*E-commerce:*
- Abandoned cart recovery
- Purchase confirmation
- Post-purchase follow-up

### REQ-FRN-001-10: Workflow Analytics Dashboard (Event-Driven)

**WHEN** a user opens the Analytics tab for a workflow,
**THEN** the system shall display comprehensive performance metrics:

**Overview Metrics:**
- Total enrolled contacts
- Currently active contacts
- Completed workflows
- Drop-off rate
- Average completion time
- Goal achievement rate

**Funnel Visualization:**
- Visual funnel chart showing drop-off at each step
- Hover displays step name and drop-off percentage
- Click step to view detailed analytics

**Performance Charts:**
- Enrollments over time (line chart)
- Completions over time (line chart)
- Drop-off by step (bar chart)
- Goal completion rate (pie chart)

**Real-Time Updates:**
- Live execution log with auto-refresh (SSE or polling)
- Filter by status (success, error, in-progress)
- Search by contact name or email
- Expand log entry to view step details

**Export:**
- Export analytics as CSV
- Export analytics as PDF report
- Date range selector

### REQ-FRN-001-11: Workflow Execution Logs Viewer (Event-Driven)

**WHEN** a user opens the Executions tab for a workflow,
**THEN** the system shall display a paginated table of execution logs:

**Table Columns:**
- Execution ID (clickable for details)
- Contact name/email
- Status (Success, Error, In Progress, Cancelled)
- Started At
- Completed At / Current Step
- Duration

**Status Indicators:**
- Success: Green checkmark
- Error: Red X with error message
- In Progress: Blue spinner
- Cancelled: Grey stop icon

**Filters:**
- Date range picker
- Status filter
- Search by contact name/email

**Execution Detail Modal:**
- Click execution ID to view detailed execution
- Step-by-step execution timeline
- Step status and timestamps
- Error messages and stack traces
- Retry failed step button
- Cancel execution button (for in-progress)

### REQ-FRN-001-12: Workflow Version History Viewer (Event-Driven)

**WHEN** a user opens the Versions tab for a workflow,
**THEN** the system shall display version history with:

**Version List:**
- Version number
- Created at timestamp
- Created by user
- Change description
- Actions: View, Restore, Compare

**Version Comparison:**
- Select two versions to compare
- Side-by-side diff view
- Highlighted changes (additions in green, deletions in red)

**Version Restore:**
- Restore button with confirmation
- Restore as new version option
- Impact warning if workflow is active

### REQ-FRN-001-13: Bulk Enrollment Interface (Event-Driven)

**WHEN** a user clicks "Enroll Contacts" from workflow detail,
**THEN** the system shall display bulk enrollment interface:

**Contact Selection:**
- Search contacts by name/email
- Filter by tags, pipeline stage, or custom field
- Multi-select with checkboxes
- Select all from current filter option
- Deselect all option

**Enrollment Options:**
- Starting step selector
- Skip existing enrollments toggle
- Schedule enrollment for later (date/time picker)

**Review:**
- Selected contacts count display
- Preview of enrollment settings
- Confirm and enroll button
- Progress bar during enrollment
- Success/error summary after completion

**Limits:**
- Maximum 10,000 contacts per bulk enrollment
- Progress updates every 100 contacts
- Error log for failed enrollments

### REQ-FRN-001-14: Workflow Settings Panel (Event-Driven)

**WHEN** a user opens the Settings tab for a workflow,
**THEN** the system shall display configuration options:

**General Settings:**
- Workflow name and description (editable)
- Workflow status toggle (Active/Paused/Archived)

**Execution Settings:**
- Max execution duration (with warning for long-running workflows)
- Retry policy (number of retries, backoff interval)
- Error handling (stop on error, continue to next step, skip to step X)

**Notification Settings:**
- Email notification on error (toggle, recipient field)
- Webhook notification on completion (URL field)

**Advanced Settings:**
- Frequency limits (max executions per time period)
- Contact re-enrollment policy (allow/deny, cooldown period)
- Goal timeout setting

**Danger Zone:**
- Delete workflow button (with confirmation dialog)
- Archive workflow button
- Export workflow as JSON

### REQ-FRN-001-15: Goal Tracking Dashboard (Event-Driven)

**WHEN** a workflow has one or more goal steps,
**THEN** the system shall display goal tracking in the workflow detail view:

**Goal Overview Cards:**
- Goal name
- Goal completion criteria
- Contacts who reached goal
- Goal completion rate
- Average time to goal

**Goal Progress List:**
- Contacts currently progressing toward goal
- Current step for each contact
- Time since entering goal path

**Goal Achievement Timeline:**
- Visual timeline showing goal achievements over time
- Filter by date range

### REQ-FRN-001-16: Form State Management (Ubiquitous)

The system shall **always** maintain form state with:

**Auto-Save:**
- Draft workflows auto-save every 30 seconds to localStorage
- Unsaved changes indicator (dot next to workflow name)
- "You have unsaved changes" warning on navigation away
- Restore from draft option on page reload

**Validation:**
- Real-time field validation with error display
- Disable save button until form is valid
- Display validation errors inline with fields
- Show form-level errors at top of form

**Dirty State:**
- Track changes vs. last saved state
- Reset changes button with confirmation
- Compare with current live version if editing active workflow

### REQ-FRN-001-17: Error Handling and User Feedback (Event-Driven)

**WHEN** an API error occurs,
**THEN** the system shall display appropriate user feedback:

**Error Types:**

*Validation Errors (400):*
- Inline field error messages
- Form summary at top with scroll to first error
- Highlighted invalid fields

*Authentication Errors (401):*
- Redirect to login page
- "Session expired. Please log in again." toast notification

*Authorization Errors (403):*
- "You don't have permission to perform this action." toast
- Disable unauthorized actions

*Not Found Errors (404):*
- "Workflow not found. It may have been deleted." message
- Back to workflow list button

*Conflict Errors (409):*
- "This name is already in use. Please choose another." message
- Suggest unique name

*Rate Limit Errors (429):*
- "Too many requests. Please wait and try again." toast
- Retry after countdown

*Server Errors (500):*
- "Something went wrong. Please try again." toast
- Retry button
- Report issue link

**Network Errors:**
- "Unable to connect. Please check your internet connection." toast
- Offline indicator in header
- Retry on reconnect

### REQ-FRN-001-18: Loading States and Skeletons (State-Driven)

**IF** a component is loading data,
**THEN** the system shall display a skeleton loader matching the component structure.

**IF** an action is in progress,
**THEN** the system shall display a loading spinner on the button and disable interaction.

**IF** a page is loading,
**THEN** the system shall display a full-page loader with workflow animation.

### REQ-FRN-001-19: Responsive Design (Ubiquitous)

The system shall **always** provide responsive layout across screen sizes:

**Desktop (1920x1080):**
- Full-width workflow canvas
- Three-column layout (sidebar, canvas, configuration panel)
- Maximum content utilization

**Laptop (1366x768):**
- Collapsible sidebar
- Two-column layout (canvas + configuration panel)
- Optimized vertical space

**Tablet (768x1024):**
- Single-column layout with tab navigation
- Full-width canvas
- Slide-over configuration panel

**Mobile (375x667):**
- Vertical workflow list view (canvas disabled)
- Step-by-step configuration instead of canvas
- Bottom navigation bar

### REQ-FRN-001-20: Accessibility (WCAG 2.1 AA) (Ubiquitous)

The system shall **always** meet WCAG 2.1 AA accessibility standards:

**Keyboard Navigation:**
- Tab order follows logical flow
- Enter/Space to activate buttons and links
- Escape to close modals and panels
- Arrow keys for navigation within lists and grids
- Focus indicators visible on all interactive elements

**Screen Reader Support:**
- ARIA labels on all interactive elements
- ARIA live regions for dynamic content updates
- Semantic HTML elements
- Alt text for all images
- Descriptive link text

**Color Contrast:**
- Minimum 4.5:1 contrast ratio for normal text
- Minimum 3:1 contrast ratio for large text
- Color not used as sole indicator of state

**Visual Alternatives:**
- Icons accompanied by text labels
- Status indicated by text + icon + color
- Error messages displayed as text (not color only)

**Focus Management:**
- Focus trapped in modals
- Focus returned to trigger after modal close
- Skip to main content link
- Focus visible at all times

### REQ-FRN-001-21: Performance Optimization (Ubiquitous)

The system shall **always** optimize for performance:

**Code Splitting:**
- Route-based code splitting with Next.js dynamic imports
- Component-based lazy loading for large components
- Vendor chunking for third-party libraries

**Image Optimization:**
- Next.js Image component for all images
- Responsive images with srcset
- Lazy loading images below fold
- WebP format with PNG fallback

**Data Caching:**
- TanStack Query caching with stale-while-revalidate
- Cache invalidation on mutation
- Prefetching on hover for navigation links

**Bundle Size:**
- Tree-shaking for unused code
- Analyze bundle size with next-bundle-analyzer
- Target: < 250KB initial bundle

**Runtime Performance:**
- React.memo for expensive components
- useMemo and useCallback for expensive computations
- Virtualization for long lists (react-window)

### REQ-FRN-001-22: Internationalization (Optional)

**WHERE POSSIBLE**, the system shall support internationalization:

**Date/Time Formats:**
- Localized date formatting based on user locale
- Timezone-aware timestamps
- Relative time display (e.g., "2 hours ago")

**Number Formats:**
- Localized number formatting (thousands separators, decimals)
- Currency formatting based on user locale

**Language Support:**
- Initial implementation: English only
- Architecture prepared for future i18n with next-intl
- Externalized user-facing strings

### REQ-FRN-001-23: Search and Filtering (Event-Driven)

**WHEN** a user interacts with a searchable list,
**THEN** the system shall provide:

**Search:**
- Debounced search input (300ms delay)
- Highlight matching text in results
- Clear search button (X icon)
- Search history (recent searches)

**Filters:**
- Multi-select filters with checkboxes
- Active filter chips with remove button
- Clear all filters button
- Filter count badge

**Sorting:**
- Sort dropdown with direction indicator
- Toggle sort direction on column header click
- Maintain sort on navigation

### REQ-FRN-001-24: Modal and Slide-Over Panels (Event-Driven)

**WHEN** a user opens a modal or slide-over panel,
**THEN** the system shall:

**Modals:**
- Overlay backdrop with click-outside-to-close
- Close button (X) in top-right
- Escape key to close
- Focus trap within modal
- Scrollable content if height exceeds viewport
- Footer with primary and secondary actions

**Slide-Over Panels:**
- Slide in from right side
- Backdrop with click-outside-to-close
- Close button (X) in top-right
- Escape key to close
- Full-height panel with internal scrolling
- Fixed header with title
- Collapsible sidebar for workflow builder

### REQ-FRN-001-25: Toast Notifications (Event-Driven)

**WHEN** a system event occurs,
**THEN** the system shall display toast notifications:

**Notification Types:**
- Success: Green checkmark, auto-dismiss after 5s
- Error: Red X, manual dismiss, shows error message
- Warning: Yellow triangle, auto-dismiss after 10s
- Info: Blue info icon, auto-dismiss after 5s

**Notification Behavior:**
- Stack multiple notifications vertically
- Maximum 5 notifications visible
- Newest notifications at bottom
- Progress bar indicating auto-dismiss time
- Click to dismiss manually
- Undo action button for destructive operations

---

## Technical Specifications

### Component Architecture

```
app/
├── workflows/
│   ├── page.tsx                          # Workflow list page
│   ├── [id]/
│   │   ├── page.tsx                      # Workflow detail view
│   │   ├── edit/
│   │   │   └── page.tsx                  # Workflow builder
│   │   ├── analytics/
│   │   │   └── page.tsx                  # Analytics dashboard
│   │   ├── executions/
│   │   │   └── page.tsx                  # Execution logs
│   │   ├── versions/
│   │   │   └── page.tsx                  # Version history
│   │   └── settings/
│   │       └── page.tsx                  # Workflow settings
│   ├── templates/
│   │   ├── page.tsx                      # Template marketplace
│   │   └── [id]/
│   │       └── page.tsx                  # Template preview
│   └── create/
│       └── page.tsx                      # Creation wizard
│
├── components/
│   ├── workflows/
│   │   ├── workflow-list-table.tsx       # Workflow list table
│   │   ├── workflow-card.tsx             # Workflow card (mobile)
│   │   ├── workflow-canvas.tsx           # Visual node canvas
│   │   ├── workflow-node.tsx             # Individual node component
│   │   ├── workflow-sidebar.tsx          # Step palette sidebar
│   │   ├── workflow-config-panel.tsx     # Configuration panel
│   │   ├── trigger-config.tsx            # Trigger configuration form
│   │   ├── action-config.tsx             # Action configuration form
│   │   ├── condition-builder.tsx         # If/else condition builder
│   │   ├── wait-config.tsx               # Wait step configuration
│   │   ├── goal-config.tsx               # Goal configuration
│   │   ├── workflow-status-badge.tsx     # Status badge component
│   │   ├── workflow-metrics.tsx          # Metrics cards
│   │   ├── workflow-funnel.tsx           # Funnel visualization
│   │   ├── execution-log-table.tsx       # Execution logs table
│   │   ├── execution-detail-modal.tsx    # Execution detail modal
│   │   ├── version-history-list.tsx      # Version history
│   │   ├── version-compare-view.tsx      # Version diff view
│   │   ├── bulk-enrollment-modal.tsx     # Bulk enrollment interface
│   │   ├── template-card.tsx             # Template card
│   │   ├── template-preview-modal.tsx    # Template preview
│   │   └── workflow-skeleton.tsx         # Loading skeleton
│   │
│   ├── ui/                                # Shadcn UI components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── select.tsx
│   │   ├── dialog.tsx
│   │   ├── dropdown-menu.tsx
│   │   ├── toast.tsx
│   │   └── ... (other Shadcn components)
│   │
│   ├── layout/
│   │   ├── header.tsx                    # App header
│   │   ├── sidebar.tsx                   # App sidebar
│   │   └── footer.tsx                    # App footer
│   │
│   └── common/
│       ├── loading-spinner.tsx           # Loading spinner
│       ├── error-boundary.tsx            # Error boundary
│       ├── empty-state.tsx               # Empty state component
│       └── pagination.tsx                # Pagination component
│
├── hooks/
│   ├── use-workflows.ts                  # Workflow data fetching
│   ├── use-workflow-detail.ts            # Single workflow fetching
│   ├── use-workflow-executions.ts        # Execution logs fetching
│   ├── use-workflow-analytics.ts         # Analytics data fetching
│   ├── use-workflow-versions.ts          # Version history fetching
│   ├── use-workflow-templates.ts         # Templates fetching
│   ├── use-workflow-canvas.ts            # Canvas state management
│   ├── use-workflow-auto-save.ts         # Auto-save hook
│   └── use-toast.ts                      # Toast notifications
│
├── lib/
│   ├── api/
│   │   ├── workflows.ts                  # Workflow API calls
│   │   ├── triggers.ts                   # Trigger API calls
│   │   ├── actions.ts                    # Action API calls
│   │   ├── executions.ts                 # Execution API calls
│   │   ├── analytics.ts                  # Analytics API calls
│   │   └── versions.ts                   # Version API calls
│   │
│   ├── stores/
│   │   ├── workflow-store.ts             # Zustand workflow store
│   │   └── canvas-store.ts               # Zustand canvas store
│   │
│   ├── types/
│   │   ├── workflow.ts                   # Workflow TypeScript types
│   │   ├── trigger.ts                    # Trigger types
│   │   ├── action.ts                     # Action types
│   │   └── execution.ts                  # Execution types
│   │
│   ├── validations/
│   │   ├── workflow-schema.ts            # Zod validation schemas
│   │   ├── trigger-schema.ts             # Trigger validation
│   │   └── action-schema.ts              # Action validation
│   │
│   └── utils/
│       ├── canvas-layout.ts              # Canvas layout algorithms
│       ├── node-positioning.ts           # Node positioning utils
│       └── workflow-export.ts            # Export/import utilities
│
└── styles/
    └── workflows.css                     # Workflow-specific styles
```

### State Management Architecture

**Zustand Store Structure:**

```typescript
// stores/canvas-store.ts
interface CanvasStore {
  // Canvas state
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  selectedNodeId: string | null;

  // Viewport state
  viewport: { x: number; y: number; zoom: number };

  // UI state
  sidebarOpen: boolean;
  configPanelOpen: boolean;
  minimapOpen: boolean;

  // Actions
  addNode: (node: WorkflowNode) => void;
  removeNode: (nodeId: string) => void;
  updateNode: (nodeId: string, data: Partial<WorkflowNode>) => void;
  addEdge: (edge: WorkflowEdge) => void;
  removeEdge: (edgeId: string) => void;
  setSelectedNode: (nodeId: string | null) => void;
  setViewport: (viewport: { x: number; y: number; zoom: number }) => void;
  toggleSidebar: () => void;
  toggleConfigPanel: () => void;
  autoLayout: () => void;
  fitToScreen: () => void;
  undo: () => void;
  redo: () => void;
}

// stores/workflow-store.ts
interface WorkflowStore {
  // Workflow data
  workflow: Workflow | null;
  isLoading: boolean;
  error: string | null;
  hasUnsavedChanges: boolean;

  // Draft state
  draftWorkflow: Workflow | null;

  // Actions
  loadWorkflow: (id: string) => Promise<void>;
  createWorkflow: (data: CreateWorkflowDto) => Promise<Workflow>;
  updateWorkflow: (id: string, data: UpdateWorkflowDto) => Promise<void>;
  deleteWorkflow: (id: string) => Promise<void>;
  duplicateWorkflow: (id: string) => Promise<Workflow>;
  saveDraft: () => void;
  restoreDraft: () => void;
  clearDraft: () => void;
}
```

### API Integration Layer

**TanStack Query Configuration:**

```typescript
// lib/api/query-client.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});
```

**API Client Pattern:**

```typescript
// lib/api/workflows.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from '@/components/ui/use-toast';
import type { Workflow, CreateWorkflowDto, UpdateWorkflowDto } from '@/lib/types/workflow';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export function useWorkflows(filters?: WorkflowFilters) {
  return useQuery({
    queryKey: ['workflows', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.status) params.append('status', filters.status);
      if (filters?.search) params.append('search', filters.search);
      if (filters?.page) params.append('page', filters.page.toString());
      if (filters?.pageSize) params.append('page_size', filters.pageSize.toString());

      const response = await fetch(`${API_BASE}/workflows?${params}`, {
        headers: {
          Authorization: `Bearer ${getToken()}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) throw new Error('Failed to fetch workflows');

      return response.json();
    },
  });
}

export function useWorkflow(id: string) {
  return useQuery({
    queryKey: ['workflow', id],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/workflows/${id}`, {
        headers: {
          Authorization: `Bearer ${getToken()}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) throw new Error('Failed to fetch workflow');

      return response.json();
    },
  });
}

export function useCreateWorkflow() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CreateWorkflowDto) => {
      const response = await fetch(`${API_BASE}/workflows`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${getToken()}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) throw new Error('Failed to create workflow');

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
      toast({
        title: 'Workflow created',
        description: 'Your workflow has been created successfully.',
      });
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      });
    },
  });
}
```

### TypeScript Type Definitions

**Workflow Types:**

```typescript
// lib/types/workflow.ts
export interface Workflow {
  id: string;
  account_id: string;
  name: string;
  description: string;
  trigger_type: TriggerType | null;
  trigger_config: Record<string, unknown>;
  status: WorkflowStatus;
  version: number;
  created_at: string;
  updated_at: string;
  created_by: string;
  updated_by: string;
  actions: WorkflowAction[];
  goals: WorkflowGoal[];
  stats: WorkflowStats;
}

export type WorkflowStatus = 'draft' | 'active' | 'paused' | 'archived';

export type TriggerType =
  | 'contact.created'
  | 'contact.updated'
  | 'contact.tagAdded'
  | 'contact.tagRemoved'
  | 'form.submitted'
  | 'pipeline.stageChanged'
  | 'pipeline.stageEntered'
  | 'appointment.booked'
  | 'appointment.cancelled'
  | 'appointment.completed'
  | 'appointment.noShow'
  | 'payment.received'
  | 'payment.failed'
  | 'subscription.created'
  | 'subscription.cancelled'
  | 'email.opened'
  | 'email.clicked'
  | 'sms.replied'
  | 'call.completed'
  | 'specific.datetime'
  | 'recurring.schedule'
  | 'contact.birthday'
  | 'contact.anniversary'
  | 'goal.completed'
  | 'webhook.received';

export interface WorkflowAction {
  id: string;
  workflow_id: string;
  action_type: ActionType;
  action_config: Record<string, unknown>;
  order: number;
  parent_action_id: string | null;
  conditions: WorkflowCondition[] | null;
}

export type ActionType =
  | 'communication.sendEmail'
  | 'communication.sendSms'
  | 'communication.sendVoice'
  | 'communication.sendFacebookMessage'
  | 'communication.makeCall'
  | 'crm.addTag'
  | 'crm.removeTag'
  | 'crm.setCustomField'
  | 'crm.addToPipeline'
  | 'crm.changePipelineStage'
  | 'crm.assignToUser'
  | 'timing.wait'
  | 'timing.waitUntil'
  | 'timing.schedule'
  | 'logic.ifElse'
  | 'logic.splitTest'
  | 'logic.goal'
  | 'internal.createTask'
  | 'internal.sendNotification'
  | 'webhook.call';

export interface WorkflowCondition {
  id: string;
  field: string;
  operator: 'equals' | 'notEquals' | 'contains' | 'greaterThan' | 'lessThan';
  value: string | number | boolean;
  logic: 'AND' | 'OR';
}

export interface WorkflowGoal {
  id: string;
  workflow_id: string;
  goal_criteria: Record<string, unknown>;
  success_action_id: string | null;
  timeout_minutes: number | null;
}

export interface WorkflowStats {
  total_enrolled: number;
  currently_active: number;
  completed: number;
  drop_off_rate: number;
  avg_completion_time_minutes: number;
}

export interface CreateWorkflowDto {
  name: string;
  description?: string;
  trigger_type?: TriggerType;
  trigger_config?: Record<string, unknown>;
}

export interface UpdateWorkflowDto {
  name?: string;
  description?: string;
  status?: WorkflowStatus;
  trigger_type?: TriggerType;
  trigger_config?: Record<string, unknown>;
}

export interface WorkflowFilters {
  status?: WorkflowStatus;
  search?: string;
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}
```

**Canvas Types:**

```typescript
// lib/types/canvas.ts
export interface WorkflowNode {
  id: string;
  type: 'trigger' | 'action' | 'condition' | 'wait' | 'goal';
  position: { x: number; y: number };
  data: {
    label: string;
    icon: string;
    config: Record<string, unknown>;
    status: 'pending' | 'active' | 'completed' | 'error';
  };
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  type: 'default' | 'conditional' | 'success' | 'failure';
  label?: string;
}

export interface Viewport {
  x: number;
  y: number;
  zoom: number;
}
```

### Zod Validation Schemas

```typescript
// lib/validations/workflow-schema.ts
import { z } from 'zod';

export const createWorkflowSchema = z.object({
  name: z.string()
    .min(3, 'Name must be at least 3 characters')
    .max(100, 'Name must be less than 100 characters')
    .regex(/^[a-zA-Z0-9\s\-_]+$/, 'Name can only contain letters, numbers, spaces, hyphens, and underscores'),
  description: z.string().max(1000).optional().default(''),
  trigger_type: z.enum([
    'contact.created',
    'contact.updated',
    // ... all trigger types
  ]).optional(),
  trigger_config: z.record(z.unknown()).optional().default({}),
});

export const updateWorkflowSchema = z.object({
  name: z.string()
    .min(3, 'Name must be at least 3 characters')
    .max(100, 'Name must be less than 100 characters')
    .regex(/^[a-zA-Z0-9\s\-_]+$/, 'Name can only contain letters, numbers, spaces, hyphens, and underscores')
    .optional(),
  description: z.string().max(1000).optional(),
  status: z.enum(['draft', 'active', 'paused', 'archived']).optional(),
  trigger_type: z.enum([
    // ... all trigger types
  ]).optional(),
  trigger_config: z.record(z.unknown()).optional(),
});

export const sendEmailActionSchema = z.object({
  template_id: z.string().uuid().optional(),
  subject: z.string().min(1).max(255),
  body: z.string().min(1),
  from_email: z.string().email(),
  from_name: z.string().min(1).max(255),
  attachments: z.array(z.object({
    filename: z.string(),
    url: z.string().url(),
    size: z.number().max(25 * 1024 * 1024), // 25MB
  })).max(10).optional(),
});

export const waitActionSchema = z.object({
  duration: z.number().min(1).max(10080), // Max 1 week in minutes
  unit: z.enum(['minutes', 'hours', 'days', 'weeks']),
});

export const conditionSchema = z.object({
  field: z.string().min(1),
  operator: z.enum(['equals', 'notEquals', 'contains', 'greaterThan', 'lessThan']),
  value: z.union([z.string(), z.number(), z.boolean()]),
  logic: z.enum(['AND', 'OR']).default('AND'),
});
```

---

## Constraints

### Technical Constraints

- Must use Next.js 14+ with App Router
- Must use Shadcn UI for all UI components
- Must use TypeScript 5+ with strict mode
- Must integrate with Clerk for authentication
- Must follow React 19 best practices (Server Components where appropriate)
- Must be responsive across desktop, tablet, and mobile
- Must meet WCAG 2.1 AA accessibility standards

### Performance Constraints

- Initial page load: < 2.5s (LCP)
- Time to Interactive: < 3.5s (TTI)
- Cumulative Layout Shift: < 0.1 (CLS)
- First Input Delay: < 100ms (FID)
- Bundle size: < 250KB initial

### Business Constraints

- Maximum 500 workflows per account
- Maximum 100 steps per workflow
- Bulk enrollment limit: 10,000 contacts
- Maximum execution duration: 30 days
- Workflow name: 3-100 characters
- Workflow description: Max 1000 characters

### Integration Constraints

- Must consume backend API at /api/v1/
- Must handle JWT authentication via Clerk
- Must support real-time updates via SSE for execution logs
- Must implement retry logic for failed API calls

---

## Dependencies

### Internal Dependencies

| Module | Dependency Type | Description |
|--------|-----------------|-------------|
| Backend Workflows API | Hard | Frontend consumes 70+ backend endpoints |
| Authentication Module | Hard | Clerk integration required for protected routes |
| CRM Module | Soft | Contact selection and tag management |
| Marketing Module | Soft | Campaign integration for email actions |
| Analytics Module | Soft | Performance metrics and dashboards |

### External Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| Next.js | 14+ | React framework |
| React | 19+ | UI library |
| TypeScript | 5+ | Type safety |
| Shadcn UI | Latest | UI components |
| Tailwind CSS | 3+ | Styling |
| Zustand | Latest | State management |
| TanStack Query | Latest | Data fetching |
| React Hook Form | Latest | Form management |
| Zod | Latest | Validation |
| @dnd-kit | Latest | Drag and drop |
| React Flow | Latest | Node canvas |
| Framer Motion | Latest | Animations |
| Lucide React | Latest | Icons |
| Recharts/Tremor | Latest | Charts |
| Clerk | Latest | Authentication |

### Development Dependencies

| Library | Purpose |
|---------|---------|
| ESLint | Linting |
| Prettier | Code formatting |
| TypeScript | Type checking |
| Vitest | Unit testing |
| React Testing Library | Component testing |
| Playwright | E2E testing |

---

## Related SPECs

| SPEC ID | Title | Relationship |
|---------|-------|--------------|
| SPEC-WFL-001 | Create Workflow | Backend API for workflow creation |
| SPEC-WFL-002 | Configure Trigger | Backend API for trigger configuration |
| SPEC-WFL-003 | Add Action Step | Backend API for action steps |
| SPEC-WFL-004 | Conditions/Branching | Backend API for conditional logic |
| SPEC-WFL-005 | Execute Workflow | Backend API for workflow execution |
| SPEC-WFL-006 | Wait Steps | Backend API for wait functionality |
| SPEC-WFL-007 | Goal Tracking | Backend API for goal management |
| SPEC-WFL-008 | Templates | Backend API for template marketplace |
| SPEC-WFL-009 | Analytics | Backend API for performance analytics |
| SPEC-WFL-010 | Webhooks | Backend API for webhook actions |
| SPEC-WFL-011 | Bulk Enrollment | Backend API for bulk operations |
| SPEC-WFL-012 | Versioning | Backend API for workflow versioning |

---

## Traceability Tags

- TAG:SPEC-FRN-001
- TAG:MODULE-WORKFLOWS-FRONTEND
- TAG:DOMAIN-FRONTEND-AUTOMATION
- TAG:PRIORITY-CRITICAL
- TAG:UI-COMPONENTS
- TAG:REACT-19
- TAG:NEXTJS-14
- TAG:SHADCN-UI
- TAG:ACCESSIBILITY
- TAG:PERFORMANCE
