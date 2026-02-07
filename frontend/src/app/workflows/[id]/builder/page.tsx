'use client';

import { useEffect } from 'react';
import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { getWorkflow } from '@/lib/api/workflows';
import { useWorkflowStore } from '@/lib/stores/workflow-store';
import { useCanvasStore } from '@/lib/stores/canvas-store';
import { WorkflowBuilder } from '@/components/workflows/builder/WorkflowBuilder';
import { WorkflowSkeleton } from '@/components/workflows/workflow-skeleton';

export default function WorkflowBuilderPage() {
  const params = useParams();
  const workflowId = params.id as string;

  const { setWorkflow, setLoading, setError } = useWorkflowStore();
  const { reset } = useCanvasStore();

  const { data: workflow, isLoading, error } = useQuery({
    queryKey: ['workflow', workflowId],
    queryFn: () => getWorkflow(workflowId),
  });

  useEffect(() => {
    if (workflow) {
      setWorkflow(workflow);
    }

    if (error) {
      setError(error instanceof Error ? error.message : 'Failed to load workflow');
    }

    setLoading(isLoading);
  }, [workflow, error, isLoading, setWorkflow, setLoading, setError]);

  // Reset canvas state on unmount
  useEffect(() => {
    return () => {
      reset();
    };
  }, [reset]);

  if (isLoading) {
    return <WorkflowSkeleton />;
  }

  if (error || !workflow) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold">Workflow not found</h2>
          <p className="text-muted-foreground">
            The workflow you're looking for doesn't exist or has been deleted.
          </p>
        </div>
      </div>
    );
  }

  return <WorkflowBuilder />;
}
