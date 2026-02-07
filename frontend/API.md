# API Documentation

This document describes the frontend API client and available endpoints for the GoHighLevel Clone Workflow Automation platform.

## Base URL

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Authentication

All API requests (except public endpoints) require authentication:

```typescript
const response = await fetch('/api/workflows', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
});
```

## Workflows API

### Get All Workflows

```typescript
GET /api/workflows
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `pageSize`: Items per page (default: 20)
- `status`: Filter by status (draft, active, paused, archived)
- `search`: Search in name/description
- `sortBy`: Field to sort by
- `sortOrder`: asc or desc

**Response:**
```typescript
{
  workflows: Workflow[];
  total: number;
  page: number;
  pageSize: number;
}
```

### Get Workflow by ID

```typescript
GET /api/workflows/:id
```

**Response:**
```typescript
Workflow
```

### Create Workflow

```typescript
POST /api/workflows
```

**Request Body:**
```typescript
{
  name: string;
  description?: string;
  trigger_type?: TriggerType;
  trigger_config?: Record<string, unknown>;
}
```

**Response:**
```typescript
Workflow
```

### Update Workflow

```typescript
PUT /api/workflows/:id
```

**Request Body:**
```typescript
{
  name?: string;
  description?: string;
  status?: WorkflowStatus;
  trigger_type?: TriggerType;
  trigger_config?: Record<string, unknown>;
}
```

**Response:**
```typescript
Workflow
```

### Delete Workflow

```typescript
DELETE /api/workflows/:id
```

**Response:**
```typescript
{ success: true }
```

## Workflow Execution API

### Get Workflow Executions

```typescript
GET /api/workflows/:id/executions
```

**Query Parameters:**
- `status`: Filter by status
- `limit`: Number of results
- `offset`: Pagination offset

**Response:**
```typescript
WorkflowExecution[]
```

### Get Execution by ID

```typescript
GET /api/workflows/:workflowId/executions/:executionId
```

**Response:**
```typescript
WorkflowExecution
```

### Retry Execution

```typescript
POST /api/workflows/:workflowId/executions/:executionId/retry
```

**Response:**
```typescript
WorkflowExecution
```

### Cancel Execution

```typescript
POST /api/workflows/:workflowId/executions/:executionId/cancel
```

**Response:**
```typescript
{ success: true }
```

## Real-Time Updates

### Server-Sent Events (SSE)

Stream workflow execution updates in real-time:

```typescript
const eventSource = new EventSource('/api/workflows/:id/executions/stream');

eventSource.onmessage = (event) => {
  const update = JSON.parse(event.data);
  // Handle update
};
```

**Event Data:**
```typescript
{
  type: 'execution.started' | 'execution.updated' | 'execution.completed';
  data: WorkflowExecution;
}
```

## Analytics API

### Get Workflow Analytics

```typescript
GET /api/workflows/:id/analytics
```

**Query Parameters:**
- `start`: Start date (ISO 8601)
- `end`: End date (ISO 8601)

**Response:**
```typescript
{
  workflow_id: string;
  date_range: { start: string; end: string };
  overview: {
    total_enrolled: number;
    currently_active: number;
    completed: number;
    drop_off_rate: number;
    avg_completion_time: number;
    goal_achievement_rate: number;
  };
  funnel: FunnelStep[];
  enrollments_over_time: AnalyticsDataPoint[];
  completions_over_time: AnalyticsDataPoint[];
  drop_off_by_step: DropOffData[];
  goal_completion_rate: GoalCompletionData[];
}
```

## Templates API

### Get All Templates

```typescript
GET /api/templates
```

**Query Parameters:**
- `category`: Filter by category
- `featured`: Show only featured templates
- `search`: Search query

**Response:**
```typescript
WorkflowTemplate[]
```

### Get Template by ID

```typescript
GET /api/templates/:id
```

**Response:**
```typescript
WorkflowTemplate
```

### Instantiate Template

```typescript
POST /api/templates/:id/instantiate
```

**Request Body:**
```typescript
{
  name?: string;
  customizations?: Record<string, unknown>;
}
```

**Response:**
```typescript
Workflow
```

## Bulk Enrollment API

### Bulk Enroll Contacts

```typescript
POST /api/workflows/:id/bulk-enroll
```

**Request Body:**
```multipart/form-data>
file: CSV file
```

**CSV Format:**
```csv
email,first_name,last_name,phone
john@example.com,John,Doe,555-1234
jane@example.com,Jane,Smith,555-5678
```

**Response:**
```typescript
{
  jobId: string;
  totalContacts: number;
  status: 'processing' | 'completed' | 'failed';
}
```

### Get Bulk Job Status

```typescript
GET /api/bulk-jobs/:jobId
```

**Response:**
```typescript
{
  jobId: string;
  status: string;
  totalContacts: number;
  processedContacts: number;
  successful: number;
  failed: number;
  errors: string[];
}
```

## Version History API

### Get Workflow Versions

```typescript
GET /api/workflows/:id/versions
```

**Response:**
```typescript
WorkflowVersion[]
```

### Create Version

```typescript
POST /api/workflows/:id/versions
```

**Request Body:**
```typescript
{
  change_description: string;
}
```

**Response:**
```typescript
WorkflowVersion
```

### Rollback to Version

```typescript
POST /api/workflows/:id/versions/:versionId/rollback
```

**Response:**
```typescript
Workflow
```

## Error Handling

All errors follow this format:

```typescript
{
  error: string;
  message: string;
  details?: Record<string, unknown>;
}
```

**HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Server Error

## Type Definitions

```typescript
// Workflow Types
type WorkflowStatus = 'draft' | 'active' | 'paused' | 'archived';

type TriggerType =
  | 'contact.created'
  | 'contact.updated'
  | 'email.opened'
  | 'webhook.received'
  // ... more types

type ActionType =
  | 'communication.sendEmail'
  | 'crm.addTag'
  | 'timing.wait'
  // ... more types

interface Workflow {
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

interface WorkflowExecution {
  id: string;
  workflow_id: string;
  contact_id: string;
  contact_name: string;
  contact_email: string;
  status: 'success' | 'error' | 'in_progress' | 'cancelled';
  started_at: string;
  completed_at: string | null;
  current_step: string | null;
  error_message: string | null;
  steps: ExecutionStep[];
}

interface WorkflowAnalytics {
  workflow_id: string;
  date_range: { start: string; end: string };
  overview: {
    total_enrolled: number;
    currently_active: number;
    completed: number;
    drop_off_rate: number;
    avg_completion_time: number;
    goal_achievement_rate: number;
  };
  funnel: FunnelStep[];
  enrollments_over_time: AnalyticsDataPoint[];
  completions_over_time: AnalyticsDataPoint[];
  drop_off_by_step: DropOffData[];
  goal_completion_rate: GoalCompletionData[];
}
```

## Rate Limiting

API requests are rate limited:
- 100 requests per minute per user
- 1000 requests per hour per user

Rate limit headers are included:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination:

```typescript
{
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}
```

## Webhooks

### Configure Webhook

```typescript
POST /api/webhooks
```

**Request Body:**
```typescript
{
  url: string;
  events: string[];
  secret?: string;
}
```

### Test Webhook

```typescript
POST /api/webhooks/:id/test
```

## Support

For API issues or questions, contact api-support@example.com
