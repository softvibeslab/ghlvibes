// CRM Type Definitions

// ============= CONTACT TYPES =============

export type ContactStatus = 'lead' | 'prospect' | 'customer' | 'churned';
export type ContactLifecycle = 'subscriber' | 'lead' | 'opportunity' | 'customer' | 'evangelist';
export type ContactSource = 'website' | 'referral' | 'social_media' | 'email' | 'phone' | 'other';

export interface Contact {
  id: string;
  account_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  mobile?: string;
  status: ContactStatus;
  lifecycle_stage: ContactLifecycle;
  source: ContactSource;
  company_id?: string;
  avatar_url?: string;
  date_of_birth?: string;
  anniversary?: string;
  address?: ContactAddress;
  tags: string[];
  custom_fields: Record<string, unknown>;
  assigned_user_id?: string;
  created_at: string;
  updated_at: string;
  converted_deal_id?: string;
  last_contacted_at?: string;
  notes_count: number;
  tasks_count: number;
  deals_count: number;
}

export interface ContactAddress {
  street?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
}

export interface CreateContactDto {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  mobile?: string;
  status?: ContactStatus;
  lifecycle_stage?: ContactLifecycle;
  source?: ContactSource;
  company_id?: string;
  date_of_birth?: string;
  anniversary?: string;
  address?: ContactAddress;
  tags?: string[];
  custom_fields?: Record<string, unknown>;
  assigned_user_id?: string;
}

export interface UpdateContactDto {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  status?: ContactStatus;
  lifecycle_stage?: ContactLifecycle;
  source?: ContactSource;
  company_id?: string;
  avatar_url?: string;
  date_of_birth?: string;
  anniversary?: string;
  address?: ContactAddress;
  tags?: string[];
  custom_fields?: Record<string, unknown>;
  assigned_user_id?: string;
}

export interface ContactFilters {
  status?: ContactStatus;
  lifecycle_stage?: ContactLifecycle;
  source?: ContactSource;
  tags?: string[];
  company_id?: string;
  assigned_user_id?: string;
  search?: string;
  date_from?: string;
  date_to?: string;
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface ContactStats {
  total_contacts: number;
  leads: number;
  prospects: number;
  customers: number;
  churned: number;
  new_this_month: number;
  conversion_rate: number;
}

// ============= COMPANY TYPES =============

export type CompanyIndustry =
  | 'technology'
  | 'healthcare'
  | 'finance'
  | 'retail'
  | 'manufacturing'
  | 'education'
  | 'consulting'
  | 'other';
export type CompanySize = '1-10' | '11-50' | '51-200' | '201-500' | '501-1000' | '1000+';

export interface Company {
  id: string;
  account_id: string;
  name: string;
  domain?: string;
  industry?: CompanyIndustry;
  size?: CompanySize;
  website?: string;
  phone?: string;
  email?: string;
  address?: ContactAddress;
  description?: string;
  logo_url?: string;
  annual_revenue?: number;
  employee_count?: number;
  tags: string[];
  custom_fields: Record<string, unknown>;
  assigned_user_id?: string;
  parent_company_id?: string;
  created_at: string;
  updated_at: string;
  contacts_count: number;
  deals_count: number;
  total_deal_value: number;
}

export interface CreateCompanyDto {
  name: string;
  domain?: string;
  industry?: CompanyIndustry;
  size?: CompanySize;
  website?: string;
  phone?: string;
  email?: string;
  address?: ContactAddress;
  description?: string;
  annual_revenue?: number;
  employee_count?: number;
  tags?: string[];
  custom_fields?: Record<string, unknown>;
  assigned_user_id?: string;
  parent_company_id?: string;
}

export interface UpdateCompanyDto {
  name?: string;
  domain?: string;
  industry?: CompanyIndustry;
  size?: CompanySize;
  website?: string;
  phone?: string;
  email?: string;
  address?: ContactAddress;
  description?: string;
  logo_url?: string;
  annual_revenue?: number;
  employee_count?: number;
  tags?: string[];
  custom_fields?: Record<string, unknown>;
  assigned_user_id?: string;
  parent_company_id?: string;
}

export interface CompanyFilters {
  industry?: CompanyIndustry;
  size?: CompanySize;
  tags?: string[];
  assigned_user_id?: string;
  search?: string;
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// ============= PIPELINE & DEAL TYPES =============

export type DealStage = 'prospecting' | 'qualification' | 'proposal' | 'negotiation' | 'closed_won' | 'closed_lost';
export type DealPriority = 'low' | 'medium' | 'high';

export interface Pipeline {
  id: string;
  account_id: string;
  name: string;
  description?: string;
  stages: PipelineStage[];
  deal_probability_enabled: boolean;
  created_at: string;
  updated_at: string;
  deals_count: number;
  total_value: number;
}

export interface PipelineStage {
  id: string;
  pipeline_id: string;
  name: string;
  order: number;
  probability?: number;
  color?: string;
}

export interface Deal {
  id: string;
  account_id: string;
  pipeline_id: string;
  stage_id: string;
  title: string;
  value: number;
  currency: string;
  priority: DealPriority;
  status: 'open' | 'won' | 'lost';
  contact_id?: string;
  company_id?: string;
  assigned_user_id?: string;
  expected_close_date?: string;
  actual_close_date?: string;
  lost_reason?: string;
  description?: string;
  tags: string[];
  custom_fields: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  contacts: Contact[];
  activities_count: number;
  next_activity_date?: string;
  probability?: number;
}

export interface CreateDealDto {
  title: string;
  value: number;
  currency?: string;
  priority?: DealPriority;
  pipeline_id: string;
  stage_id: string;
  contact_id?: string;
  company_id?: string;
  assigned_user_id?: string;
  expected_close_date?: string;
  description?: string;
  tags?: string[];
  custom_fields?: Record<string, unknown>;
}

export interface UpdateDealDto {
  title?: string;
  value?: number;
  currency?: string;
  priority?: DealPriority;
  stage_id?: string;
  status?: 'open' | 'won' | 'lost';
  contact_id?: string;
  company_id?: string;
  assigned_user_id?: string;
  expected_close_date?: string;
  actual_close_date?: string;
  lost_reason?: string;
  description?: string;
  tags?: string[];
  custom_fields?: Record<string, unknown>;
  probability?: number;
}

export interface DealFilters {
  pipeline_id?: string;
  stage_id?: string;
  status?: 'open' | 'won' | 'lost';
  priority?: DealPriority;
  contact_id?: string;
  company_id?: string;
  assigned_user_id?: string;
  tags?: string[];
  search?: string;
  value_min?: number;
  value_max?: number;
  date_from?: string;
  date_to?: string;
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface DealStats {
  total_deals: number;
  open_deals: number;
  won_deals: number;
  lost_deals: number;
  total_value: number;
  weighted_value: number;
  average_deal_size: number;
  conversion_rate: number;
}

export interface PipelineForecast {
  pipeline_id: string;
  pipeline_name: string;
  total_value: number;
  weighted_value: number;
  stages: StageForecast[];
}

export interface StageForecast {
  stage_id: string;
  stage_name: string;
  deal_count: number;
  total_value: number;
  weighted_value: number;
  probability: number;
}

// ============= TASK & ACTIVITY TYPES =============

export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled';
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';
export type TaskType =
  | 'call'
  | 'email'
  | 'meeting'
  | 'follow_up'
  | 'demo'
  | 'proposal'
  | 'task'
  | 'reminder';

export interface Task {
  id: string;
  account_id: string;
  title: string;
  description?: string;
  type: TaskType;
  status: TaskStatus;
  priority: TaskPriority;
  due_date?: string;
  due_time?: string;
  reminder_enabled: boolean;
  reminder_minutes?: number;
  completed_at?: string;
  related_entity_type?: 'contact' | 'company' | 'deal';
  related_entity_id?: string;
  assigned_user_id?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  contact?: Contact;
  company?: Company;
  deal?: Deal;
  recurring_enabled: boolean;
  recurring_pattern?: string;
  recurring_end_date?: string;
}

export interface CreateTaskDto {
  title: string;
  description?: string;
  type: TaskType;
  priority?: TaskPriority;
  due_date?: string;
  due_time?: string;
  reminder_enabled?: boolean;
  reminder_minutes?: number;
  related_entity_type?: 'contact' | 'company' | 'deal';
  related_entity_id?: string;
  assigned_user_id?: string;
  recurring_enabled?: boolean;
  recurring_pattern?: string;
  recurring_end_date?: string;
}

export interface UpdateTaskDto {
  title?: string;
  description?: string;
  type?: TaskType;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string;
  due_time?: string;
  reminder_enabled?: boolean;
  reminder_minutes?: number;
  completed_at?: string;
  related_entity_type?: 'contact' | 'company' | 'deal';
  related_entity_id?: string;
  assigned_user_id?: string;
  recurring_enabled?: boolean;
  recurring_pattern?: string;
  recurring_end_date?: string;
}

export interface TaskFilters {
  status?: TaskStatus;
  priority?: TaskPriority;
  type?: TaskType;
  assigned_user_id?: string;
  related_entity_type?: 'contact' | 'company' | 'deal';
  related_entity_id?: string;
  search?: string;
  date_from?: string;
  date_to?: string;
  overdue?: boolean;
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export type ActivityType =
  | 'call'
  | 'email'
  | 'sms'
  | 'meeting'
  | 'note'
  | 'task_completed'
  | 'status_change'
  | 'email_opened'
  | 'email_clicked'
  | 'web_visit'
  | 'other';

export interface Activity {
  id: string;
  account_id: string;
  type: ActivityType;
  title: string;
  description?: string;
  direction?: 'inbound' | 'outbound';
  duration_minutes?: number;
  related_entity_type?: 'contact' | 'company' | 'deal';
  related_entity_id?: string;
  created_by: string;
  created_at: string;
  contact?: Contact;
  company?: Company;
  deal?: Deal;
  attachments: ActivityAttachment[];
  metadata?: Record<string, unknown>;
}

export interface ActivityAttachment {
  id: string;
  activity_id: string;
  file_name: string;
  file_url: string;
  file_size: number;
  file_type: string;
  uploaded_at: string;
}

export interface CreateActivityDto {
  type: ActivityType;
  title: string;
  description?: string;
  direction?: 'inbound' | 'outbound';
  duration_minutes?: number;
  related_entity_type?: 'contact' | 'company' | 'deal';
  related_entity_id?: string;
  attachments?: CreateAttachmentDto[];
  metadata?: Record<string, unknown>;
}

export interface CreateAttachmentDto {
  file_name: string;
  file_url: string;
  file_size: number;
  file_type: string;
}

export interface ActivityFilters {
  type?: ActivityType;
  related_entity_type?: 'contact' | 'company' | 'deal';
  related_entity_id?: string;
  created_by?: string;
  date_from?: string;
  date_to?: string;
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// ============= NOTE TYPES =============

export interface Note {
  id: string;
  account_id: string;
  content: string;
  related_entity_type: 'contact' | 'company' | 'deal';
  related_entity_id: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  updated_by: string;
  attachments: ActivityAttachment[];
  mentions: string[];
  is_pinned: boolean;
}

export interface CreateNoteDto {
  content: string;
  related_entity_type: 'contact' | 'company' | 'deal';
  related_entity_id: string;
  attachments?: CreateAttachmentDto[];
  mentions?: string[];
  is_pinned?: boolean;
}

export interface UpdateNoteDto {
  content?: string;
  attachments?: CreateAttachmentDto[];
  mentions?: string[];
  is_pinned?: boolean;
}

// ============= TAG TYPES =============

export interface Tag {
  id: string;
  account_id: string;
  name: string;
  color: string;
  description?: string;
  usage_count: number;
  created_at: string;
}

export interface CreateTagDto {
  name: string;
  color: string;
  description?: string;
}

export interface UpdateTagDto {
  name?: string;
  color?: string;
  description?: string;
}

// ============= CUSTOM FIELD TYPES =============

export type CustomFieldType = 'text' | 'number' | 'date' | 'dropdown' | 'multiselect' | 'checkbox' | 'textarea';

export interface CustomField {
  id: string;
  account_id: string;
  name: string;
  type: CustomFieldType;
  entity_type: 'contact' | 'company' | 'deal';
  options?: string[];
  is_required: boolean;
  is_visible: boolean;
  placeholder?: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateCustomFieldDto {
  name: string;
  type: CustomFieldType;
  entity_type: 'contact' | 'company' | 'deal';
  options?: string[];
  is_required?: boolean;
  is_visible?: boolean;
  placeholder?: string;
  description?: string;
}

export interface UpdateCustomFieldDto {
  name?: string;
  type?: CustomFieldType;
  options?: string[];
  is_required?: boolean;
  is_visible?: boolean;
  placeholder?: string;
  description?: string;
}

// ============= IMPORT/EXPORT TYPES =============

export interface ImportJob {
  id: string;
  account_id: string;
  entity_type: 'contact' | 'company';
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'partial';
  file_name: string;
  total_rows: number;
  processed_rows: number;
  successful_rows: number;
  failed_rows: number;
  error_summary?: string;
  created_at: string;
  completed_at?: string;
  created_by: string;
}

export interface ImportConfig {
  entity_type: 'contact' | 'company';
  column_mapping: Record<string, string>;
  skip_duplicates: boolean;
  update_existing: boolean;
  tags?: string[];
}

export interface ExportConfig {
  entity_type: 'contact' | 'company' | 'deal';
  filters?: Record<string, unknown>;
  fields: string[];
  format: 'csv' | 'xlsx';
  include_relations?: boolean;
}

// ============= DASHBOARD TYPES =============

export interface CRMDashboardStats {
  contacts: ContactStats;
  companies: {
    total_companies: number;
    new_this_month: number;
  };
  deals: DealStats;
  tasks: {
    total_tasks: number;
    overdue_tasks: number;
    due_today: number;
    completed_this_week: number;
  };
  activities: {
    total_activities: number;
    today_activities: number;
    this_week_activities: number;
  };
  revenue: {
    won_this_month: number;
    pipeline_value: number;
    forecast_this_month: number;
  };
}

export interface RecentActivity {
  id: string;
  type: string;
  title: string;
  description?: string;
  created_at: string;
  user_name: string;
  avatar_url?: string;
  related_entity?: {
    type: 'contact' | 'company' | 'deal';
    id: string;
    name: string;
  };
}
