'use client';

import { use } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Edit, Trash2, Copy, Play, Pause } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { WorkflowMetrics } from '@/components/workflows/workflow-metrics';
import { WorkflowStatusBadge } from '@/components/workflows/workflow-status-badge';
import { getWorkflow } from '@/lib/api/workflows';
import { Workflow } from '@/lib/types/workflow';
import Link from 'next/link';

export default function WorkflowDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const { data: workflow, isLoading, error } = useQuery({
    queryKey: ['workflow', id],
    queryFn: () => getWorkflow(id),
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/workflows">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div className="h-8 w-64 animate-pulse rounded bg-muted" />
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          {Array.from({ length: 5 }).map((_, i) => (
            <div
              key={i}
              className="h-32 animate-pulse rounded-lg bg-muted"
            />
          ))}
        </div>
      </div>
    );
  }

  if (error || !workflow) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/workflows">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
        </div>
        <div className="text-center">
          <h2 className="text-2xl font-bold">Workflow not found</h2>
          <p className="text-muted-foreground">
            The workflow you're looking for doesn't exist or has been deleted.
          </p>
          <Button className="mt-4" asChild>
            <Link href="/workflows">Back to Workflows</Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/workflows">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold tracking-tight">
                {workflow.name}
              </h1>
              <WorkflowStatusBadge status={workflow.status} />
            </div>
            {workflow.description && (
              <p className="text-muted-foreground">{workflow.description}</p>
            )}
          </div>
        </div>

        <div className="flex gap-2">
          <Button variant="outline" size="sm" asChild>
            <Link href={`/workflows/${id}/builder`}>
              <Edit className="mr-2 h-4 w-4" />
              Edit in Builder
            </Link>
          </Button>
          <Button variant="outline" size="sm">
            <Copy className="mr-2 h-4 w-4" />
            Duplicate
          </Button>
          <Button
            variant={workflow.status === 'active' ? 'destructive' : 'default'}
            size="sm"
          >
            {workflow.status === 'active' ? (
              <>
                <Pause className="mr-2 h-4 w-4" />
                Pause
              </>
            ) : (
              <>
                <Play className="mr-2 h-4 w-4" />
                Activate
              </>
            )}
          </Button>
          <Button variant="outline" size="sm">
            <Trash2 className="mr-2 h-4 w-4 text-destructive" />
          </Button>
        </div>
      </div>

      {/* Metrics */}
      <WorkflowMetrics stats={workflow.stats} />

      {/* Workflow Overview */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Trigger Configuration */}
        <div className="rounded-lg border bg-card p-6">
          <h2 className="text-lg font-semibold mb-4">Trigger</h2>
          {workflow.trigger_type ? (
            <div className="space-y-2">
              <div className="text-sm text-muted-foreground">Trigger Type</div>
              <div className="font-medium capitalize">
                {workflow.trigger_type.replace('.', ' ')}
              </div>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">No trigger configured</p>
          )}
        </div>

        {/* Actions Summary */}
        <div className="rounded-lg border bg-card p-6">
          <h2 className="text-lg font-semibold mb-4">Actions</h2>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Total Actions</span>
              <span className="font-medium">{workflow.actions.length}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Goals</span>
              <span className="font-medium">{workflow.goals.length}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs for additional details */}
      <div className="rounded-lg border bg-card">
        <div className="border-b">
          <div className="flex gap-4 px-6">
            <button className="py-4 text-sm font-medium border-b-2 border-primary">
              Overview
            </button>
            <button className="py-4 text-sm font-medium text-muted-foreground hover:text-foreground">
              Analytics
            </button>
            <button className="py-4 text-sm font-medium text-muted-foreground hover:text-foreground">
              Executions
            </button>
            <button className="py-4 text-sm font-medium text-muted-foreground hover:text-foreground">
              Versions
            </button>
            <button className="py-4 text-sm font-medium text-muted-foreground hover:text-foreground">
              Settings
            </button>
          </div>
        </div>
        <div className="p-6">
          <p className="text-sm text-muted-foreground">
            Select a tab to view more details about this workflow.
          </p>
        </div>
      </div>
    </div>
  );
}
