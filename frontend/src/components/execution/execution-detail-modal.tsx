'use client';

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { WorkflowExecution, ExecutionStep } from '@/lib/types/workflow';
import { format } from 'date-fns';
import { CheckCircle2, XCircle, Clock, AlertCircle, ChevronRight } from 'lucide-react';
import { clsx } from 'clsx';

interface ExecutionDetailModalProps {
  execution: WorkflowExecution | null;
  open: boolean;
  onClose: () => void;
}

interface StepTimelineProps {
  steps: ExecutionStep[];
}

function StepTimeline({ steps }: StepTimelineProps) {
  return (
    <div className="relative">
      <div className="absolute left-[15px] top-0 bottom-0 w-0.5 bg-border" aria-hidden="true" />
      <div className="space-y-4">
        {steps.map((step, index) => {
          const getStatusIcon = () => {
            switch (step.status) {
              case 'success':
                return (
                  <div className="relative z-10">
                    <CheckCircle2 className="h-8 w-8 text-green-500 bg-background rounded-full p-1" />
                  </div>
                );
              case 'error':
                return (
                  <div className="relative z-10">
                    <XCircle className="h-8 w-8 text-red-500 bg-background rounded-full p-1" />
                  </div>
                );
              case 'pending':
                return (
                  <div className="relative z-10">
                    <Clock className="h-8 w-8 text-muted-foreground bg-background rounded-full p-1" />
                  </div>
                );
              case 'in_progress':
                return (
                  <div className="relative z-10">
                    <RefreshCw className="h-8 w-8 text-blue-500 bg-background rounded-full p-1 animate-spin" />
                  </div>
                );
            }
          };

          return (
            <div key={step.id} className="flex gap-4">
              {getStatusIcon()}
              <div className="flex-1 pb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <h4 className="font-semibold">{step.action_type}</h4>
                    <Badge
                      variant={
                        step.status === 'success'
                          ? 'default'
                          : step.status === 'error'
                          ? 'destructive'
                          : 'secondary'
                      }
                    >
                      {step.status}
                    </Badge>
                  </div>
                  {step.completed_at && (
                    <span className="text-sm text-muted-foreground">
                      {format(new Date(step.completed_at), 'HH:mm:ss')}
                    </span>
                  )}
                </div>

                {step.error_message && (
                  <div className="mt-2 p-3 bg-red-50 dark:bg-red-950 rounded border border-red-200 dark:border-red-800">
                    <p className="text-sm font-medium text-red-800 dark:text-red-200">Error:</p>
                    <p className="text-sm text-red-600 dark:text-red-400 mt-1">{step.error_message}</p>
                  </div>
                )}

                {(step.input_data && Object.keys(step.input_data).length > 0) ||
                (step.output_data && Object.keys(step.output_data).length > 0) ? (
                  <details className="mt-2">
                    <summary className="cursor-pointer text-sm text-muted-foreground hover:text-foreground">
                      View data
                    </summary>
                    <div className="mt-2 space-y-2">
                      {step.input_data && Object.keys(step.input_data).length > 0 && (
                        <div>
                          <p className="text-xs font-semibold text-muted-foreground mb-1">Input:</p>
                          <pre className="text-xs bg-muted p-2 rounded overflow-x-auto">
                            {JSON.stringify(step.input_data, null, 2)}
                          </pre>
                        </div>
                      )}
                      {step.output_data && Object.keys(step.output_data).length > 0 && (
                        <div>
                          <p className="text-xs font-semibold text-muted-foreground mb-1">Output:</p>
                          <pre className="text-xs bg-muted p-2 rounded overflow-x-auto">
                            {JSON.stringify(step.output_data, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  </details>
                ) : null}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function ExecutionDetailModal({ execution, open, onClose }: ExecutionDetailModalProps) {
  if (!execution) return null;

  const duration = execution.completed_at
    ? formatDistanceToNow(new Date(execution.started_at), new Date(execution.completed_at))
    : null;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle>Execution Details</DialogTitle>
        </DialogHeader>

        <ScrollArea className="max-h-[calc(80vh-120px)]">
          <div className="space-y-6 p-4">
            {/* Contact Information */}
            <div>
              <h3 className="text-sm font-semibold text-muted-foreground mb-2">Contact</h3>
              <div className="space-y-1">
                <p className="font-medium">{execution.contact_name}</p>
                <p className="text-sm text-muted-foreground">{execution.contact_email}</p>
              </div>
            </div>

            <Separator />

            {/* Execution Information */}
            <div>
              <h3 className="text-sm font-semibold text-muted-foreground mb-2">Execution Info</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Status:</span>
                  <Badge
                    variant={
                      execution.status === 'success'
                        ? 'default'
                        : execution.status === 'error'
                        ? 'destructive'
                        : 'secondary'
                    }
                    className="ml-2"
                  >
                    {execution.status.replace('_', ' ')}
                  </Badge>
                </div>
                <div>
                  <span className="text-muted-foreground">Started:</span>{' '}
                  {format(new Date(execution.started_at), 'PPp')}
                </div>
                {execution.completed_at && (
                  <>
                    <div>
                      <span className="text-muted-foreground">Completed:</span>{' '}
                      {format(new Date(execution.completed_at), 'PPp')}
                    </div>
                    <div>
                      <span className="text-muted-foreground">Duration:</span>{' '}
                      {duration}
                    </div>
                  </>
                )}
              </div>
            </div>

            {execution.error_message && (
              <>
                <Separator />
                <div>
                  <h3 className="text-sm font-semibold text-red-500 mb-2">Error</h3>
                  <p className="text-sm bg-red-50 dark:bg-red-950 p-3 rounded border border-red-200 dark:border-red-800">
                    {execution.error_message}
                  </p>
                </div>
              </>
            )}

            <Separator />

            {/* Step Timeline */}
            <div>
              <h3 className="text-sm font-semibold text-muted-foreground mb-4">
                Execution Steps
              </h3>
              <StepTimeline steps={execution.steps} />
            </div>
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}

function formatDistanceToNow(start: Date, end: Date): string {
  const seconds = Math.floor((end.getTime() - start.getTime()) / 1000);
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ${seconds % 60}s`;
  const hours = Math.floor(minutes / 60);
  return `${hours}h ${minutes % 60}m`;
}
