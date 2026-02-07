import type {
  Workflow,
  CreateWorkflowDto,
  UpdateWorkflowDto,
  WorkflowFilters,
  PaginatedResponse,
} from '@/lib/types/workflow';

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

export async function getWorkflows(
  filters?: WorkflowFilters
): Promise<PaginatedResponse<Workflow>> {
  const params = new URLSearchParams();
  if (filters?.status) params.append('status', filters.status);
  if (filters?.search) params.append('search', filters.search);
  if (filters?.page) params.append('page', filters.page.toString());
  if (filters?.pageSize) params.append('page_size', filters.pageSize.toString());
  if (filters?.sortBy) params.append('sort_by', filters.sortBy);
  if (filters?.sortOrder) params.append('sort_order', filters.sortOrder);

  const query = params.toString();
  return apiRequest<PaginatedResponse<Workflow>>(`/workflows${query ? `?${query}` : ''}`);
}

export async function getWorkflow(id: string): Promise<Workflow> {
  return apiRequest<Workflow>(`/workflows/${id}`);
}

export async function createWorkflow(data: CreateWorkflowDto): Promise<Workflow> {
  return apiRequest<Workflow>('/workflows', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateWorkflow(
  id: string,
  data: UpdateWorkflowDto
): Promise<Workflow> {
  return apiRequest<Workflow>(`/workflows/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteWorkflow(id: string): Promise<void> {
  return apiRequest<void>(`/workflows/${id}`, {
    method: 'DELETE',
  });
}

export async function duplicateWorkflow(id: string): Promise<Workflow> {
  return apiRequest<Workflow>(`/workflows/${id}/duplicate`, {
    method: 'POST',
  });
}

export async function activateWorkflow(id: string): Promise<Workflow> {
  return apiRequest<Workflow>(`/workflows/${id}/activate`, {
    method: 'POST',
  });
}

export async function pauseWorkflow(id: string): Promise<Workflow> {
  return apiRequest<Workflow>(`/workflows/${id}/pause`, {
    method: 'POST',
  });
}

export async function archiveWorkflow(id: string): Promise<Workflow> {
  return apiRequest<Workflow>(`/workflows/${id}/archive`, {
    method: 'POST',
  });
}

export async function exportWorkflow(id: string): Promise<Workflow> {
  return apiRequest<Workflow>(`/workflows/${id}/export`, {
    method: 'GET',
  });
}
