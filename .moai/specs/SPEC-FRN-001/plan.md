# Implementation Plan: SPEC-FRN-001

**SPEC:** Workflows Module - Frontend User Interface
**Plan Version:** 1.0.0
**Last Updated:** 2026-02-07

---

## Overview

This implementation plan outlines the systematic development of the Workflows Module frontend using Next.js 14, Shadcn UI, and TypeScript. The implementation follows a priority-based milestone approach with clear dependencies between features.

**Total Estimated Effort:** 80-120 developer hours
**Target Completion:** 6-8 weeks with 1-2 frontend developers

---

## Primary Milestone: Foundation and Core Workflow Management

**Goal:** Establish project foundation and implement basic workflow CRUD operations with list and detail views.

**Estimated Effort:** 20-30 hours

### Phase 1: Project Setup (Priority High)

**Tasks:**
1. Initialize Next.js 14 project with TypeScript
   - Install dependencies: Next.js 14, React 19, TypeScript 5
   - Configure Shadcn UI with Tailwind CSS
   - Set up ESLint and Prettier
   - Configure absolute imports

2. Configure Clerk authentication
   - Install Clerk SDK
   - Set up authentication middleware
   - Configure protected routes
   - Implement authentication context

3. Set up state management
   - Install Zustand for client state
   - Install TanStack Query for server state
   - Configure query client with defaults
   - Create base API client with interceptors

4. Establish project structure
   - Create app/workflows directory structure
   - Create components/workflows directory
   - Create hooks, lib/stores, lib/types, lib/api directories
   - Set up barrel exports for clean imports

**Deliverables:**
- Functional Next.js project with Shadcn UI configured
- Authentication flow working with Clerk
- Base API client with JWT token management
- Project directory structure established

**Acceptance Criteria:**
- All dependencies installed and configured
- Authentication redirects unauthenticated users to Clerk login
- API client successfully makes authenticated requests
- TypeScript compilation with zero errors

---

### Phase 2: Workflow List Page (Priority High)

**Tasks:**
1. Create workflow list page component
   - Implement app/workflows/page.tsx
   - Set up page-level metadata and SEO

2. Build workflow list table component
   - Create WorkflowListTable component
   - Implement columns: Name, Status, Trigger, Active Contacts, Completion Rate, Last Modified
   - Add status badges with color coding
   - Implement row click navigation

3. Implement search and filtering
   - Add search input with debouncing (300ms)
   - Implement status filter dropdown
   - Add sort by column with direction toggle

4. Create pagination component
   - Build Pagination component (or use Shadcn Table pagination)
   - Implement configurable page size (10, 25, 50, 100)
   - Add page navigation buttons

5. Create empty state and error state components
   - Build EmptyState component with illustration
   - Build ErrorState component with retry button
   - Build LoadingSkeleton component

6. Integrate TanStack Query for data fetching
   - Create useWorkflows hook
   - Implement caching and invalidation
   - Handle loading, error, and success states

**Deliverables:**
- Functional workflow list page at /workflows
- Search, filter, sort, and pagination working
- Loading, empty, and error states implemented
- API integration with workflow list endpoint

**Acceptance Criteria:**
- Table displays workflows with correct data
- Search filters table by workflow name
- Status filter shows only selected status workflows
- Pagination displays correct page of data
- Empty state shows when no workflows exist
- Clicking row navigates to workflow detail page
- Loading skeleton displays during data fetch
- Error state displays with retry button on API failure

---

### Phase 3: Workflow Detail View (Priority High)

**Tasks:**
1. Create workflow detail page component
   - Implement app/workflows/[id]/page.tsx
   - Set up dynamic routing with workflow ID

2. Build workflow detail header
   - Display workflow name and description
   - Implement status toggle (Active/Paused)
   - Add action buttons: Edit, Delete, Duplicate, Export

3. Create workflow metrics cards
   - Build WorkflowMetrics component
   - Display: Enrolled, Active, Completed, Drop-off Rate
   - Add sparkline charts for trends

4. Implement workflow actions
   - Create delete confirmation modal
   - Implement duplicate workflow functionality
   - Add export workflow as JSON

5. Create tab navigation
   - Build tab component (Overview, Executions, Analytics, Versions, Settings)
   - Implement tab state management
   - Handle browser back button with tab state

**Deliverables:**
- Functional workflow detail page at /workflows/[id]
- Metrics cards displaying real-time data
- Action buttons working (delete, duplicate, export)
- Tab navigation for sub-pages

**Acceptance Criteria:**
- Page loads workflow data by ID
- Metrics display accurate numbers
- Status toggle updates workflow status
- Delete button shows confirmation modal
- Duplicate action creates workflow copy
- Export button downloads JSON file
- Tab navigation works correctly

---

## Secondary Milestone: Visual Workflow Builder

**Goal:** Implement the core visual drag-and-drop workflow builder with canvas, sidebar, and configuration panel.

**Estimated Effort:** 40-60 hours

### Phase 4: Workflow Canvas (Priority High)

**Tasks:**
1. Install and configure React Flow
   - Install @xyflow/react (React Flow library)
   - Configure flow canvas with custom node types
   - Set up viewport controls (pan, zoom, fit-to-screen)

2. Create workflow node components
   - Build TriggerNode component (distinct shape/color)
   - Build ActionNode component (rectangular card)
   - Build ConditionNode component (diamond shape)
   - Build WaitNode component (clock icon)
   - Build GoalNode component (flag icon)

3. Implement node interactions
   - Add click to select functionality
   - Implement drag to reposition
   - Add delete with keyboard and context menu
   - Implement copy/paste with keyboard shortcuts

4. Create connection lines (edges)
   - Configure edge types (default, conditional, success, failure)
   - Add directional arrows
   - Implement edge labels
   - Add edge deletion

5. Build canvas toolbar
   - Add undo/redo buttons with keyboard shortcuts
   - Implement auto-layout button
   - Add fit-to-screen button
   - Create save button with unsaved changes indicator
   - Add test workflow button

6. Implement mini-map navigation
   - Add minimap component in bottom-right corner
   - Sync minimap with main canvas
   - Allow click on minimap to navigate canvas

**Deliverables:**
- Functional visual canvas at /workflows/[id]/edit
- Custom node components for all step types
- Drag-and-drop functionality working
- Canvas toolbar with all controls

**Acceptance Criteria:**
- Canvas displays workflow nodes visually
- Nodes can be dragged to reposition
- Connections display between nodes with arrows
- Pan and zoom work with mouse wheel and drag
- Mini-map shows workflow overview
- Undo/redo maintains history stack
- Auto-layout organizes nodes vertically
- Fit-to-screen centers and scales workflow
- Save button persists workflow to backend
- Unsaved changes indicator shows when dirty

---

### Phase 5: Workflow Builder Sidebar (Priority High)

**Tasks:**
1. Create sidebar component
   - Build collapsible sidebar panel
   - Implement accordion for step categories

2. Organize step categories
   - Triggers: List 26 trigger types
   - Actions: List 25+ action types
   - Logic: If/Else, Split Test, Goal
   - Advanced: Custom Code, API Call, Wait Until, Loop

3. Add step search functionality
   - Implement search input
   - Filter steps by search term
   - Highlight matching text

4. Implement step interactions
   - Add drag from sidebar to canvas
   - Add click to append to workflow
   - Show step description on hover

**Deliverables:**
- Functional sidebar with step palette
- Search and filter working
- Drag-and-drop to canvas working

**Acceptance Criteria:**
- Sidebar displays all step types organized by category
- Categories expand/collapse with accordion
- Search filters steps in real-time
- Dragging step from sidebar adds to canvas
- Clicking step appends to workflow end
- Hover displays step description tooltip

---

### Phase 6: Configuration Panel (Priority High)

**Tasks:**
1. Create configuration panel component
   - Build slide-over panel from right
   - Implement backdrop with click-outside-to-close
   - Add close button (X) and ESC key support

2. Build trigger configuration forms
   - Create TriggerConfig component
   - Implement forms for all 26 trigger types
   - Add trigger test button
   - Implement validation with error messages

3. Build action configuration forms
   - Create ActionConfig component
   - Implement forms for all action categories:
     * Communication actions (email, SMS, voice, etc.)
     * CRM actions (tags, fields, pipeline, etc.)
     * Timing actions (wait, wait until, schedule)
     * Logic actions (if/else, split test, goal)
     * Internal actions (tasks, notifications)
     * Webhook actions

4. Implement form validation
   - Integrate React Hook Form
   - Add Zod schema validation
   - Display inline error messages
   - Disable save until valid

5. Add variable support
   - Implement variable picker ({{contact.name}})
   - Show available variables for each step type
   - Add variable preview with sample data

**Deliverables:**
- Functional configuration panel for all step types
- Forms with validation working
- Variable support implemented

**Acceptance Criteria:**
- Panel opens when clicking node
- Panel closes with X button, ESC key, or backdrop click
- Forms display correct fields based on step type
- Validation shows errors inline
- Save button disabled until form valid
- Variables insert correctly with {{variable}} syntax
- Trigger test button simulates execution
- Save persists step configuration

---

### Phase 7: Auto-Save and Draft Management (Priority Medium)

**Tasks:**
1. Implement auto-save functionality
   - Create useWorkflowAutoSave hook
   - Save draft to localStorage every 30 seconds
   - Show unsaved changes indicator

2. Handle draft state
   - Save draft on form changes
   - Restore draft on page reload
   - Clear draft on successful save

3. Add navigation protection
   - Warn user when navigating with unsaved changes
   - Provide "Leave page" or "Stay and save" options

**Deliverables:**
- Auto-save working with localStorage
- Draft restore on reload
- Navigation warnings implemented

**Acceptance Criteria:**
- Draft saves every 30 seconds automatically
- Unsaved changes indicator (dot) displays
- Reloading page restores draft from localStorage
- Navigating away shows warning dialog
- Manual save clears draft and indicator

---

## Tertiary Milestone: Analytics and Advanced Features

**Goal:** Implement analytics dashboard, execution logs, template marketplace, and advanced workflow management features.

**Estimated Effort:** 20-30 hours

### Phase 8: Analytics Dashboard (Priority Medium)

**Tasks:**
1. Create analytics page component
   - Implement app/workflows/[id]/analytics/page.tsx
   - Set up tab for analytics view

2. Build overview metrics cards
   - Create metrics for: Total Enrolled, Active, Completed, Drop-off Rate
   - Add trend indicators (up/down arrows)

3. Implement funnel visualization
   - Build WorkflowFunnel component using Recharts
   - Display drop-off at each step
   - Add hover tooltips with details

4. Create performance charts
   - Enrollments over time (line chart)
   - Completions over time (line chart)
   - Drop-off by step (bar chart)
   - Goal completion rate (pie chart)

5. Implement real-time execution log
   - Create ExecutionLog component
   - Integrate SSE for real-time updates
   - Add filter by status
   - Implement search by contact

**Deliverables:**
- Functional analytics dashboard
- Charts displaying performance data
- Real-time execution log with SSE

**Acceptance Criteria:**
- Analytics page loads at /workflows/[id]/analytics
- Metrics cards display correct data
- Funnel chart shows visual drop-off
- Performance charts render correctly
- Real-time log updates via SSE
- Filter and search work on execution log

---

### Phase 9: Execution Logs and Version History (Priority Medium)

**Tasks:**
1. Create execution logs page
   - Implement app/workflows/[id]/executions/page.tsx
   - Build execution log table component

2. Implement execution detail modal
   - Create ExecutionDetailModal component
   - Display step-by-step execution timeline
   - Show error messages and stack traces
   - Add retry failed step button

3. Create version history page
   - Implement app/workflows/[id]/versions/page.tsx
   - Build version list component

4. Implement version comparison
   - Create VersionCompareView component
   - Display side-by-side diff
   - Highlight additions (green) and deletions (red)

5. Add version restore functionality
   - Implement restore button with confirmation
   - Add "restore as new version" option

**Deliverables:**
- Functional execution logs page
- Execution detail modal working
- Version history with comparison
- Version restore functionality

**Acceptance Criteria:**
- Execution logs display paginated table
- Clicking execution ID opens detail modal
- Modal shows step-by-step timeline
- Retry button retries failed steps
- Version history lists all versions
- Comparison view shows diff
- Restore button restores version with confirmation

---

### Phase 10: Template Marketplace (Priority Medium)

**Tasks:**
1. Create template marketplace page
   - Implement app/workflows/templates/page.tsx
   - Build template grid with cards

2. Build template card component
   - Display template name, description, preview image
   - Show rating and usage count
   - Add category filter

3. Implement template preview modal
   - Create TemplatePreviewModal component
   - Show visual workflow diagram
   - Display step-by-step breakdown
   - Add required integrations list

4. Create workflow from template
   - Implement one-click instantiation
   - Add "customize before creating" option
   - Navigate to workflow editor after creation

**Deliverables:**
- Functional template marketplace
- Template preview modal working
- Template instantiation implemented

**Acceptance Criteria:**
- Template marketplace displays grid of templates
- Category filters work correctly
- Search filters templates by name or use case
- Clicking template opens preview modal
- Modal displays workflow preview
- One-click create button instantiates template
- Customize option opens creation wizard with pre-filled data

---

### Phase 11: Bulk Enrollment and Workflow Settings (Priority Low)

**Tasks:**
1. Create bulk enrollment modal
   - Build BulkEnrollmentModal component
   - Implement contact search and multi-select
   - Add filters (tags, pipeline, custom fields)

2. Implement enrollment options
   - Add starting step selector
   - Implement skip existing toggle
   - Add schedule for later option

3. Create workflow settings page
   - Implement app/workflows/[id]/settings/page.tsx
   - Build settings form with sections

4. Implement settings sections
   - General settings (name, description, status)
   - Execution settings (timeout, retry policy, error handling)
   - Notification settings (email on error, webhook)
   - Advanced settings (frequency limits, re-enrollment policy)

5. Add danger zone
   - Implement delete workflow button
   - Add archive workflow button
   - Create export as JSON button

**Deliverables:**
- Functional bulk enrollment modal
- Workflow settings page implemented
- All settings sections working

**Acceptance Criteria:**
- Bulk enrollment modal opens from workflow detail
- Contact search and multi-select work
- Filters reduce contact list correctly
- Maximum 10,000 contacts enforced
- Progress bar shows enrollment progress
- Success/error summary displays after completion
- Settings page loads at /workflows/[id]/settings
- All settings save to backend
- Delete workflow shows confirmation and deletes

---

## Final Milestone: Polish and Optimization

**Goal:** Ensure production-ready quality with accessibility, performance optimization, and comprehensive testing.

**Estimated Effort:** 10-15 hours

### Phase 12: Accessibility and Responsive Design (Priority High)

**Tasks:**
1. Audit with accessibility tools
   - Run Lighthouse accessibility audit
   - Test with screen reader (NVDA/JAWS)
   - Verify keyboard navigation
   - Check color contrast ratios

2. Fix accessibility issues
   - Add ARIA labels where missing
   - Ensure focus indicators visible
   - Implement skip to content link
   - Fix color contrast issues

3. Implement responsive design
   - Test on desktop (1920x1080, 1366x768)
   - Test on tablet (768x1024)
   - Test on mobile (375x667)
   - Adjust layouts for each breakpoint

**Deliverables:**
- WCAG 2.1 AA compliant application
- Responsive across all target screen sizes

**Acceptance Criteria:**
- Lighthouse accessibility score 90+
- All interactive elements keyboard accessible
- Screen reader announces all relevant information
- Color contrast ratios meet WCAG AA standards
- Application functions on desktop, tablet, and mobile

---

### Phase 13: Performance Optimization (Priority High)

**Tasks:**
1. Analyze bundle size
   - Run next-bundle-analyzer
   - Identify large dependencies
   - Implement code splitting

2. Optimize images and assets
   - Convert to Next.js Image component
   - Implement lazy loading
   - Use WebP format with fallback

3. Optimize data fetching
   - Configure TanStack Query caching
   - Implement prefetching on hover
   - Add request deduplication

4. Implement component optimizations
   - Add React.memo for expensive components
   - Use useMemo for expensive computations
   - Implement useCallback for event handlers
   - Add virtualization for long lists

**Deliverables:**
- Optimized bundle size (< 250KB initial)
- Core Web Vitals targets met
- Smooth 60fps interactions

**Acceptance Criteria:**
- LCP < 2.5s
- TTI < 3.5s
- CLS < 0.1
- FID < 100ms
- Initial bundle < 250KB

---

### Phase 14: Testing (Priority High)

**Tasks:**
1. Write unit tests with Vitest
   - Test utility functions
   - Test custom hooks
   - Test Zustand stores
   - Target: 80%+ coverage

2. Write component tests with React Testing Library
   - Test user interactions
   - Test form validation
   - Test error handling
   - Target: 70%+ coverage

3. Write E2E tests with Playwright
   - Test critical user flows:
     * Create workflow
     * Configure trigger and actions
     * Save and activate workflow
     * View analytics dashboard
   - Test cross-browser compatibility

**Deliverables:**
- Comprehensive test suite
- CI/CD pipeline with tests
- Test coverage reports

**Acceptance Criteria:**
- Unit tests pass with 80%+ coverage
- Component tests pass with 70%+ coverage
- E2E tests cover all critical flows
- All tests pass in CI/CD pipeline

---

### Phase 15: Documentation and Deployment (Priority Medium)

**Tasks:**
1. Write component documentation
   - Document props for all components
   - Add usage examples
   - Create Storybook stories (optional)

2. Write deployment documentation
   - Document environment variables
   - Create deployment guide
   - Document Vercel configuration

3. Set up CI/CD pipeline
   - Configure GitHub Actions
   - Add automated tests
   - Add deployment to Vercel

4. Deploy to staging
   - Deploy to Vercel staging environment
   - Run smoke tests
   - Verify all features work

**Deliverables:**
- Complete documentation
- CI/CD pipeline configured
- Application deployed to staging

**Acceptance Criteria:**
- All components documented with props
- Deployment guide is comprehensive
- CI/CD pipeline runs tests on PR
- Staging environment is accessible and functional

---

## Risk Assessment

### High Risk Items

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| React Flow library limitations | High | Medium | Evaluate alternative libraries early; build custom canvas if needed |
| Real-time SSE complexity | High | Medium | Implement polling fallback; test SSE thoroughly |
| Performance with large workflows | High | Medium | Implement virtualization; limit workflow size |
| Browser compatibility issues | Medium | Low | Test early on target browsers; use polyfills |

### Medium Risk Items

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| State management complexity | Medium | High | Keep stores simple; use Zustand devtools for debugging |
| Form validation for many step types | Medium | High | Create reusable validation schemas; use Zod composability |
| Backend API delays | Medium | Medium | Mock API for development; implement optimistic updates |

---

## Dependencies and Prerequisites

### External Dependencies

**Must Be Available Before Development Starts:**
1. Backend API endpoints fully implemented (SPEC-WFL-001 through SPEC-WFL-012)
2. Clerk authentication configured with test accounts
3. API documentation available (OpenAPI spec)
4. Test environment with sample data

**Recommended to Have:**
1. Figma designs or mockups for reference
2. Design system documentation (if customizing Shadcn UI)
3. Analytics and monitoring tools configured

### Internal Dependencies

**Phase Dependencies:**
- Phase 1 (Setup) must complete before all other phases
- Phase 2 (List Page) should complete before Phase 3 (Detail View)
- Phase 4 (Canvas) and Phase 5 (Sidebar) can proceed in parallel
- Phase 6 (Config Panel) depends on Phase 4 and 5
- Phase 8-11 depend on Phase 3 completion

**Skill Requirements:**
- Frontend developer experienced with React and TypeScript
- Experience with Next.js App Router preferred
- Familiarity with state management patterns required
- UI/UX sensibility for drag-and-drop interfaces helpful

---

## Success Metrics

### Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Lighthouse Performance Score | 90+ | Lighthouse audit |
| Lighthouse Accessibility Score | 90+ | Lighthouse audit |
| First Contentful Paint | < 1.5s | Lighthouse / Web Vitals |
| Largest Contentful Paint | < 2.5s | Lighthouse / Web Vitals |
| Cumulative Layout Shift | < 0.1 | Lighthouse / Web Vitals |
| Time to Interactive | < 3.5s | Lighthouse / Web Vitals |
| Initial Bundle Size | < 250KB | webpack-bundle-analyzer |
| Test Coverage (Unit) | 80%+ | Vitest coverage report |
| Test Coverage (Component) | 70%+ | React Testing Library coverage |

### User Experience Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Workflow Creation Time | < 2 minutes | User testing |
| Canvas Response Time | < 100ms | User testing |
| Error Recovery Rate | 95%+ | Analytics (error occurrence / recovery) |
| Task Completion Rate | 90%+ | User testing (complete workflow creation) |

---

## Traceability Tags

- TAG:SPEC-FRN-001
- TAG:IMPLEMENTATION-PLAN
- TAG:MILESTONE-FOUNDATION
- TAG:MILESTONE-VISUAL-BUILDER
- TAG:MILESTONE-ANALYTICS
- TAG:MILESTONE-POLISH
- TAG:PHASE-1-THROUGH-15
