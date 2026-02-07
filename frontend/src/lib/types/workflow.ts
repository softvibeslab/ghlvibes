// Workflow Type Definitions
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

export interface WorkflowAction {
  id: string;
  workflow_id: string;
  action_type: ActionType;
  action_config: Record<string, unknown>;
  order: number;
  parent_action_id: string | null;
  conditions: WorkflowCondition[] | null;
}

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

// Canvas Types
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

// Execution Types
export interface WorkflowExecution {
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

export interface ExecutionStep {
  id: string;
  execution_id: string;
  action_id: string;
  action_type: string;
  status: 'success' | 'error' | 'pending' | 'in_progress';
  started_at: string;
  completed_at: string | null;
  error_message: string | null;
  input_data: Record<string, unknown>;
  output_data: Record<string, unknown>;
}

// Analytics Types
export interface WorkflowAnalytics {
  workflow_id: string;
  date_range: {
    start: string;
    end: string;
  };
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

export interface FunnelStep {
  step_id: string;
  step_name: string;
  step_order: number;
  contacts_entered: number;
  contacts_completed: number;
  drop_off_count: number;
  drop_off_rate: number;
}

export interface AnalyticsDataPoint {
  date: string;
  count: number;
}

export interface DropOffData {
  step_name: string;
  drop_off_count: number;
  drop_off_rate: number;
}

export interface GoalCompletionData {
  goal_name: string;
  achieved: number;
  total: number;
  completion_rate: number;
}

// Template Types
export interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  use_case: string;
  preview_image_url: string;
  workflow_definition: Partial<Workflow>;
  rating: number;
  usage_count: number;
  required_integrations: string[];
  created_at: string;
  featured: boolean;
}

// Version Types
export interface WorkflowVersion {
  id: string;
  workflow_id: string;
  version_number: number;
  workflow_definition: Partial<Workflow>;
  change_description: string;
  created_at: string;
  created_by: string;
}
