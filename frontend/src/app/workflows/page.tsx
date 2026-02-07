'use client';

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Plus, Search, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { WorkflowListTable } from '@/components/workflows/workflow-list-table';
import { WorkflowTableSkeleton } from '@/components/workflows/workflow-skeleton';
import { EmptyState } from '@/components/common/empty-state';
import { getWorkflows } from '@/lib/api/workflows';
import { Workflow } from '@/lib/types/workflow';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { WorkflowStatus } from '@/lib/types/workflow';

export default function WorkflowsPage() {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [debouncedSearch, setDebouncedSearch] = useState('');

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  // Fetch workflows with filters
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['workflows', statusFilter, debouncedSearch],
    queryFn: () =>
      getWorkflows({
        search: debouncedSearch || undefined,
        status: statusFilter === 'all' ? undefined : (statusFilter as WorkflowStatus),
        page: 1,
        pageSize: 50,
      }),
  });

  const workflows = data?.items || [];

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this workflow?')) {
      // TODO: Implement delete functionality
      console.log('Delete workflow:', id);
    }
  };

  const handleDuplicate = async (id: string) => {
    // TODO: Implement duplicate functionality
    console.log('Duplicate workflow:', id);
  };

  const handleEdit = (id: string) => {
    window.location.href = `/workflows/${id}/edit`;
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Workflows</h1>
            <p className="text-muted-foreground">
              Manage and automate your business processes
            </p>
          </div>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Workflow
          </Button>
        </div>
        <WorkflowTableSkeleton />
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Workflows</h1>
            <p className="text-muted-foreground">
              Manage and automate your business processes
            </p>
          </div>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Workflow
          </Button>
        </div>
        <EmptyState
          icon={AlertCircle}
          title="Error loading workflows"
          description={error.message}
          action={{
            label: 'Retry',
            onClick: () => refetch(),
          }}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Workflows</h1>
          <p className="text-muted-foreground">
            Manage and automate your business processes
          </p>
        </div>
        <Button asChild>
          <a href="/workflows/create">
            <Plus className="mr-2 h-4 w-4" />
            Create Workflow
          </a>
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search workflows..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="draft">Draft</SelectItem>
            <SelectItem value="paused">Paused</SelectItem>
            <SelectItem value="archived">Archived</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Workflow List */}
      {workflows.length === 0 ? (
        <EmptyState
          icon={Workflow}
          title="No workflows found"
          description="Get started by creating your first workflow automation"
          action={{
            label: 'Create Workflow',
            onClick: () => (window.location.href = '/workflows/create'),
          }}
        />
      ) : (
        <WorkflowListTable
          workflows={workflows}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onDuplicate={handleDuplicate}
        />
      )}
    </div>
  );
}
