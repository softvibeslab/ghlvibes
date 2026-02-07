import type {
  Contact,
  CreateContactDto,
  UpdateContactDto,
  ContactFilters,
  ContactStats,
  Company,
  CreateCompanyDto,
  UpdateCompanyDto,
  CompanyFilters,
  Pipeline,
  Deal,
  CreateDealDto,
  UpdateDealDto,
  DealFilters,
  DealStats,
  PipelineForecast,
  Task,
  CreateTaskDto,
  UpdateTaskDto,
  TaskFilters,
  Activity,
  CreateActivityDto,
  ActivityFilters,
  Note,
  CreateNoteDto,
  UpdateNoteDto,
  Tag,
  CreateTagDto,
  UpdateTagDto,
  CustomField,
  CreateCustomFieldDto,
  UpdateCustomFieldDto,
  ImportJob,
  ImportConfig,
  CRMDashboardStats,
  RecentActivity,
  PaginatedResponse,
} from '@/lib/types/crm';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function getAuthToken(): Promise<string> {
  // TODO: Integrate with Clerk to get JWT token
  if (typeof window !== 'undefined') {
    return localStorage.getItem('auth_token') || '';
  }
  return '';
}

async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const token = await getAuthToken();

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      message: 'An error occurred',
    }));
    throw new Error(error.message || error.detail || 'API request failed');
  }

  return response.json();
}

// ============= CONTACTS =============

export async function getContacts(
  filters?: ContactFilters
): Promise<PaginatedResponse<Contact>> {
  const params = new URLSearchParams();
  if (filters?.status) params.append('status', filters.status);
  if (filters?.lifecycle_stage) params.append('lifecycle_stage', filters.lifecycle_stage);
  if (filters?.source) params.append('source', filters.source);
  if (filters?.tags?.length) params.append('tags', filters.tags.join(','));
  if (filters?.company_id) params.append('company_id', filters.company_id);
  if (filters?.assigned_user_id) params.append('assigned_user_id', filters.assigned_user_id);
  if (filters?.search) params.append('search', filters.search);
  if (filters?.date_from) params.append('date_from', filters.date_from);
  if (filters?.date_to) params.append('date_to', filters.date_to);
  if (filters?.page) params.append('page', filters.page.toString());
  if (filters?.pageSize) params.append('page_size', filters.pageSize.toString());
  if (filters?.sortBy) params.append('sort_by', filters.sortBy);
  if (filters?.sortOrder) params.append('sort_order', filters.sortOrder);

  const query = params.toString();
  return apiRequest<PaginatedResponse<Contact>>(`/crm/contacts${query ? `?${query}` : ''}`);
}

export async function getContact(id: string): Promise<Contact> {
  return apiRequest<Contact>(`/crm/contacts/${id}`);
}

export async function createContact(data: CreateContactDto): Promise<Contact> {
  return apiRequest<Contact>('/crm/contacts', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateContact(
  id: string,
  data: UpdateContactDto
): Promise<Contact> {
  return apiRequest<Contact>(`/crm/contacts/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteContact(id: string): Promise<void> {
  return apiRequest<void>(`/crm/contacts/${id}`, {
    method: 'DELETE',
  });
}

export async function getContactStats(): Promise<ContactStats> {
  return apiRequest<ContactStats>('/crm/contacts/stats');
}

export async function bulkDeleteContacts(ids: string[]): Promise<void> {
  return apiRequest<void>('/crm/contacts/bulk-delete', {
    method: 'POST',
    body: JSON.stringify({ ids }),
  });
}

export async function bulkUpdateContacts(
  ids: string[],
  updates: Partial<UpdateContactDto>
): Promise<void> {
  return apiRequest<void>('/crm/contacts/bulk-update', {
    method: 'POST',
    body: JSON.stringify({ ids, updates }),
  });
}

export async function exportContacts(filters?: ContactFilters): Promise<Blob> {
  const token = await getAuthToken();
  const params = new URLSearchParams();
  if (filters?.search) params.append('search', filters.search);
  if (filters?.status) params.append('status', filters.status);

  const response = await fetch(`${API_BASE}/crm/contacts/export?${params.toString()}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Export failed');
  }

  return response.blob();
}

export async function importContacts(
  file: File,
  config: ImportConfig
): Promise<ImportJob> {
  const token = await getAuthToken();
  const formData = new FormData();
  formData.append('file', file);
  formData.append('config', JSON.stringify(config));

  const response = await fetch(`${API_BASE}/crm/contacts/import`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Import failed');
  }

  return response.json();
}

// ============= COMPANIES =============

export async function getCompanies(
  filters?: CompanyFilters
): Promise<PaginatedResponse<Company>> {
  const params = new URLSearchParams();
  if (filters?.industry) params.append('industry', filters.industry);
  if (filters?.size) params.append('size', filters.size);
  if (filters?.tags?.length) params.append('tags', filters.tags.join(','));
  if (filters?.assigned_user_id) params.append('assigned_user_id', filters.assigned_user_id);
  if (filters?.search) params.append('search', filters.search);
  if (filters?.page) params.append('page', filters.page.toString());
  if (filters?.pageSize) params.append('page_size', filters.pageSize.toString());
  if (filters?.sortBy) params.append('sort_by', filters.sortBy);
  if (filters?.sortOrder) params.append('sort_order', filters.sortOrder);

  const query = params.toString();
  return apiRequest<PaginatedResponse<Company>>(`/crm/companies${query ? `?${query}` : ''}`);
}

export async function getCompany(id: string): Promise<Company> {
  return apiRequest<Company>(`/crm/companies/${id}`);
}

export async function createCompany(data: CreateCompanyDto): Promise<Company> {
  return apiRequest<Company>('/crm/companies', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateCompany(
  id: string,
  data: UpdateCompanyDto
): Promise<Company> {
  return apiRequest<Company>(`/crm/companies/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteCompany(id: string): Promise<void> {
  return apiRequest<void>(`/crm/companies/${id}`, {
    method: 'DELETE',
  });
}

export async function getCompanyContacts(
  companyId: string,
  page = 1,
  pageSize = 20
): Promise<PaginatedResponse<Contact>> {
  return apiRequest<PaginatedResponse<Contact>>(
    `/crm/companies/${companyId}/contacts?page=${page}&page_size=${pageSize}`
  );
}

export async function getCompanyDeals(
  companyId: string,
  page = 1,
  pageSize = 20
): Promise<PaginatedResponse<Deal>> {
  return apiRequest<PaginatedResponse<Deal>>(
    `/crm/companies/${companyId}/deals?page=${page}&page_size=${pageSize}`
  );
}

// ============= PIPELINES & DEALS =============

export async function getPipelines(): Promise<Pipeline[]> {
  return apiRequest<Pipeline[]>('/crm/pipelines');
}

export async function getPipeline(id: string): Promise<Pipeline> {
  return apiRequest<Pipeline>(`/crm/pipelines/${id}`);
}

export async function createPipeline(
  name: string,
  description?: string
): Promise<Pipeline> {
  return apiRequest<Pipeline>('/crm/pipelines', {
    method: 'POST',
    body: JSON.stringify({ name, description }),
  });
}

export async function updatePipeline(
  id: string,
  name: string,
  description?: string
): Promise<Pipeline> {
  return apiRequest<Pipeline>(`/crm/pipelines/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({ name, description }),
  });
}

export async function deletePipeline(id: string): Promise<void> {
  return apiRequest<void>(`/crm/pipelines/${id}`, {
    method: 'DELETE',
  });
}

export async function getDeals(filters?: DealFilters): Promise<PaginatedResponse<Deal>> {
  const params = new URLSearchParams();
  if (filters?.pipeline_id) params.append('pipeline_id', filters.pipeline_id);
  if (filters?.stage_id) params.append('stage_id', filters.stage_id);
  if (filters?.status) params.append('status', filters.status);
  if (filters?.priority) params.append('priority', filters.priority);
  if (filters?.contact_id) params.append('contact_id', filters.contact_id);
  if (filters?.company_id) params.append('company_id', filters.company_id);
  if (filters?.assigned_user_id) params.append('assigned_user_id', filters.assigned_user_id);
  if (filters?.tags?.length) params.append('tags', filters.tags.join(','));
  if (filters?.search) params.append('search', filters.search);
  if (filters?.value_min) params.append('value_min', filters.value_min.toString());
  if (filters?.value_max) params.append('value_max', filters.value_max.toString());
  if (filters?.date_from) params.append('date_from', filters.date_from);
  if (filters?.date_to) params.append('date_to', filters.date_to);
  if (filters?.page) params.append('page', filters.page.toString());
  if (filters?.pageSize) params.append('page_size', filters.pageSize.toString());
  if (filters?.sortBy) params.append('sort_by', filters.sortBy);
  if (filters?.sortOrder) params.append('sort_order', filters.sortOrder);

  const query = params.toString();
  return apiRequest<PaginatedResponse<Deal>>(`/crm/deals${query ? `?${query}` : ''}`);
}

export async function getDeal(id: string): Promise<Deal> {
  return apiRequest<Deal>(`/crm/deals/${id}`);
}

export async function createDeal(data: CreateDealDto): Promise<Deal> {
  return apiRequest<Deal>('/crm/deals', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateDeal(id: string, data: UpdateDealDto): Promise<Deal> {
  return apiRequest<Deal>(`/crm/deals/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteDeal(id: string): Promise<void> {
  return apiRequest<void>(`/crm/deals/${id}`, {
    method: 'DELETE',
  });
}

export async function updateDealStage(
  id: string,
  stageId: string
): Promise<Deal> {
  return apiRequest<Deal>(`/crm/deals/${id}/stage`, {
    method: 'PATCH',
    body: JSON.stringify({ stage_id: stageId }),
  });
}

export async function getDealStats(filters?: DealFilters): Promise<DealStats> {
  const params = new URLSearchParams();
  if (filters?.pipeline_id) params.append('pipeline_id', filters.pipeline_id);

  const query = params.toString();
  return apiRequest<DealStats>(`/crm/deals/stats${query ? `?${query}` : ''}`);
}

export async function getPipelineForecast(
  pipelineId: string
): Promise<PipelineForecast> {
  return apiRequest<PipelineForecast>(`/crm/pipelines/${pipelineId}/forecast`);
}

export async function getPipelineDeals(pipelineId: string): Promise<Deal[]> {
  return apiRequest<Deal[]>(`/crm/pipelines/${pipelineId}/deals`);
}

// ============= TASKS =============

export async function getTasks(filters?: TaskFilters): Promise<PaginatedResponse<Task>> {
  const params = new URLSearchParams();
  if (filters?.status) params.append('status', filters.status);
  if (filters?.priority) params.append('priority', filters.priority);
  if (filters?.type) params.append('type', filters.type);
  if (filters?.assigned_user_id) params.append('assigned_user_id', filters.assigned_user_id);
  if (filters?.related_entity_type) params.append('related_entity_type', filters.related_entity_type);
  if (filters?.related_entity_id) params.append('related_entity_id', filters.related_entity_id);
  if (filters?.search) params.append('search', filters.search);
  if (filters?.date_from) params.append('date_from', filters.date_from);
  if (filters?.date_to) params.append('date_to', filters.date_to);
  if (filters?.overdue) params.append('overdue', 'true');
  if (filters?.page) params.append('page', filters.page.toString());
  if (filters?.pageSize) params.append('page_size', filters.pageSize.toString());
  if (filters?.sortBy) params.append('sort_by', filters.sortBy);
  if (filters?.sortOrder) params.append('sort_order', filters.sortOrder);

  const query = params.toString();
  return apiRequest<PaginatedResponse<Task>>(`/crm/tasks${query ? `?${query}` : ''}`);
}

export async function getTask(id: string): Promise<Task> {
  return apiRequest<Task>(`/crm/tasks/${id}`);
}

export async function createTask(data: CreateTaskDto): Promise<Task> {
  return apiRequest<Task>('/crm/tasks', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateTask(id: string, data: UpdateTaskDto): Promise<Task> {
  return apiRequest<Task>(`/crm/tasks/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteTask(id: string): Promise<void> {
  return apiRequest<void>(`/crm/tasks/${id}`, {
    method: 'DELETE',
  });
}

export async function completeTask(id: string): Promise<Task> {
  return apiRequest<Task>(`/crm/tasks/${id}/complete`, {
    method: 'POST',
  });
}

export async function getTasksCalendar(
  startDate: string,
  endDate: string
): Promise<Task[]> {
  return apiRequest<Task[]>(
    `/crm/tasks/calendar?start_date=${startDate}&end_date=${endDate}`
  );
}

// ============= ACTIVITIES =============

export async function getActivities(
  filters?: ActivityFilters
): Promise<PaginatedResponse<Activity>> {
  const params = new URLSearchParams();
  if (filters?.type) params.append('type', filters.type);
  if (filters?.related_entity_type) params.append('related_entity_type', filters.related_entity_type);
  if (filters?.related_entity_id) params.append('related_entity_id', filters.related_entity_id);
  if (filters?.created_by) params.append('created_by', filters.created_by);
  if (filters?.date_from) params.append('date_from', filters.date_from);
  if (filters?.date_to) params.append('date_to', filters.date_to);
  if (filters?.page) params.append('page', filters.page.toString());
  if (filters?.pageSize) params.append('page_size', filters.pageSize.toString());
  if (filters?.sortBy) params.append('sort_by', filters.sortBy);
  if (filters?.sortOrder) params.append('sort_order', filters.sortOrder);

  const query = params.toString();
  return apiRequest<PaginatedResponse<Activity>>(`/crm/activities${query ? `?${query}` : ''}`);
}

export async function getActivity(id: string): Promise<Activity> {
  return apiRequest<Activity>(`/crm/activities/${id}`);
}

export async function createActivity(data: CreateActivityDto): Promise<Activity> {
  return apiRequest<Activity>('/crm/activities', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function deleteActivity(id: string): Promise<void> {
  return apiRequest<void>(`/crm/activities/${id}`, {
    method: 'DELETE',
  });
}

export async function getEntityActivities(
  entityType: 'contact' | 'company' | 'deal',
  entityId: string,
  page = 1,
  pageSize = 20
): Promise<PaginatedResponse<Activity>> {
  return apiRequest<PaginatedResponse<Activity>>(
    `/crm/activities/${entityType}/${entityId}?page=${page}&page_size=${pageSize}`
  );
}

// ============= NOTES =============

export async function getNotes(
  entityType: 'contact' | 'company' | 'deal',
  entityId: string
): Promise<Note[]> {
  return apiRequest<Note[]>(`/crm/notes/${entityType}/${entityId}`);
}

export async function getNote(id: string): Promise<Note> {
  return apiRequest<Note>(`/crm/notes/${id}`);
}

export async function createNote(data: CreateNoteDto): Promise<Note> {
  return apiRequest<Note>('/crm/notes', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateNote(id: string, data: UpdateNoteDto): Promise<Note> {
  return apiRequest<Note>(`/crm/notes/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteNote(id: string): Promise<void> {
  return apiRequest<void>(`/crm/notes/${id}`, {
    method: 'DELETE',
  });
}

// ============= TAGS =============

export async function getTags(): Promise<Tag[]> {
  return apiRequest<Tag[]>('/crm/tags');
}

export async function getTag(id: string): Promise<Tag> {
  return apiRequest<Tag>(`/crm/tags/${id}`);
}

export async function createTag(data: CreateTagDto): Promise<Tag> {
  return apiRequest<Tag>('/crm/tags', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateTag(id: string, data: UpdateTagDto): Promise<Tag> {
  return apiRequest<Tag>(`/crm/tags/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteTag(id: string): Promise<void> {
  return apiRequest<void>(`/crm/tags/${id}`, {
    method: 'DELETE',
  });
}

// ============= CUSTOM FIELDS =============

export async function getCustomFields(
  entityType: 'contact' | 'company' | 'deal'
): Promise<CustomField[]> {
  return apiRequest<CustomField[]>(`/crm/custom-fields/${entityType}`);
}

export async function createCustomField(
  data: CreateCustomFieldDto
): Promise<CustomField> {
  return apiRequest<CustomField>('/crm/custom-fields', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateCustomField(
  id: string,
  data: UpdateCustomFieldDto
): Promise<CustomField> {
  return apiRequest<CustomField>(`/crm/custom-fields/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteCustomField(id: string): Promise<void> {
  return apiRequest<void>(`/crm/custom-fields/${id}`, {
    method: 'DELETE',
  });
}

// ============= DASHBOARD =============

export async function getCRMDashboardStats(): Promise<CRMDashboardStats> {
  return apiRequest<CRMDashboardStats>('/crm/dashboard/stats');
}

export async function getRecentActivities(limit = 10): Promise<RecentActivity[]> {
  return apiRequest<RecentActivity[]>(`/crm/dashboard/recent?limit=${limit}`);
}

export async function getUpcomingTasks(limit = 10): Promise<Task[]> {
  return apiRequest<Task[]>(`/crm/dashboard/upcoming-tasks?limit=${limit}`);
}

export async function getTodayTasks(): Promise<Task[]> {
  return apiRequest<Task[]>('/crm/dashboard/today-tasks');
}

export async function getOverdueTasks(): Promise<Task[]> {
  return apiRequest<Task[]>('/crm/dashboard/overdue-tasks');
}
