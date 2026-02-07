'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Search, RefreshCw, Clock, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import { WorkflowExecution } from '@/lib/types/workflow';
import { formatDistanceToNow } from 'date-fns';

interface ExecutionListProps {
  workflowId: string;
  onSelectExecution: (execution: WorkflowExecution) => void;
  selectedExecutionId?: string;
  className?: string;
}

interface ExecutionFilters {
  status?: WorkflowExecution['status'];
  search: string;
}

export function ExecutionList({
  workflowId,
  onSelectExecution,
  selectedExecutionId,
  className,
}: ExecutionListProps) {
  const [executions, setExecutions] = useState<WorkflowExecution[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filters, setFilters] = useState<ExecutionFilters>({ search: '' });
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchExecutions = async () => {
    try {
      const response = await fetch(`/api/workflows/${workflowId}/executions`);
      if (!response.ok) throw new Error('Failed to fetch executions');
      const data = await response.json();
      setExecutions(data);
    } catch (error) {
      console.error('Error fetching executions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchExecutions();

    if (autoRefresh) {
      const interval = setInterval(fetchExecutions, 5000); // Refresh every 5 seconds
      return () => clearInterval(interval);
    }
  }, [workflowId, autoRefresh]);

  // SSE for real-time updates
  useEffect(() => {
    const eventSource = new EventSource(`/api/workflows/${workflowId}/executions/stream`);

    eventSource.onmessage = (event) => {
      const updatedExecution = JSON.parse(event.data);
      setExecutions((prev) => {
        const index = prev.findIndex((e) => e.id === updatedExecution.id);
        if (index !== -1) {
          const updated = [...prev];
          updated[index] = updatedExecution;
          return updated;
        }
        return [updatedExecution, ...prev];
      });
    };

    eventSource.onerror = (error) => {
      console.error('SSE error:', error);
      eventSource.close();
    };

    return () => eventSource.close();
  }, [workflowId]);

  const filteredExecutions = executions.filter((execution) => {
    const matchesStatus = !filters.status || execution.status === filters.status;
    const matchesSearch =
      !filters.search ||
      execution.contact_name.toLowerCase().includes(filters.search.toLowerCase()) ||
      execution.contact_email.toLowerCase().includes(filters.search.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  const getStatusIcon = (status: WorkflowExecution['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircle2 className="h-4 w-4 text-green-500" aria-hidden="true" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" aria-hidden="true" />;
      case 'in_progress':
        return <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" aria-hidden="true" />;
      case 'cancelled':
        return <AlertCircle className="h-4 w-4 text-yellow-500" aria-hidden="true" />;
    }
  };

  const getStatusVariant = (status: WorkflowExecution['status']) => {
    switch (status) {
      case 'success':
        return 'default';
      case 'error':
        return 'destructive';
      case 'in_progress':
        return 'secondary';
      case 'cancelled':
        return 'outline';
    }
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Execution Logs</CardTitle>
        <div className="flex gap-2 mt-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by contact name or email..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="pl-9"
              aria-label="Search executions"
            />
          </div>
          <Select
            value={filters.status || 'all'}
            onValueChange={(value) =>
              setFilters({ ...filters, status: value === 'all' ? undefined : (value as any) })
            }
          >
            <SelectTrigger className="w-[140px]" aria-label="Filter by status">
              <SelectValue placeholder="All Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="success">Success</SelectItem>
              <SelectItem value="error">Error</SelectItem>
              <SelectItem value="in_progress">In Progress</SelectItem>
              <SelectItem value="cancelled">Cancelled</SelectItem>
            </SelectContent>
          </Select>
          <Button
            variant="outline"
            size="icon"
            onClick={() => setAutoRefresh(!autoRefresh)}
            aria-label={autoRefresh ? 'Disable auto-refresh' : 'Enable auto-refresh'}
            className={autoRefresh ? 'bg-green-50 dark:bg-green-950' : ''}
          >
            <RefreshCw className={`h-4 w-4 ${autoRefresh ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center h-[400px]">Loading executions...</div>
        ) : filteredExecutions.length === 0 ? (
          <div className="flex items-center justify-center h-[400px] text-muted-foreground">
            No executions found
          </div>
        ) : (
          <ScrollArea className="h-[500px]">
            <div className="space-y-2">
              {filteredExecutions.map((execution) => (
                <button
                  key={execution.id}
                  onClick={() => onSelectExecution(execution)}
                  className={`w-full text-left p-4 rounded-lg border transition-colors hover:bg-accent ${
                    selectedExecutionId === execution.id
                      ? 'bg-accent border-primary'
                      : 'bg-background'
                  }`}
                  aria-label={`View execution details for ${execution.contact_name}`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3 flex-1 min-w-0">
                      {getStatusIcon(execution.status)}
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate" title={execution.contact_name}>
                          {execution.contact_name}
                        </p>
                        <p className="text-sm text-muted-foreground truncate" title={execution.contact_email}>
                          {execution.contact_email}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          <Clock className="h-3 w-3 text-muted-foreground" aria-hidden="true" />
                          <span className="text-xs text-muted-foreground">
                            {formatDistanceToNow(new Date(execution.started_at), { addSuffix: true })}
                          </span>
                        </div>
                      </div>
                    </div>
                    <Badge variant={getStatusVariant(execution.status)} className="shrink-0">
                      {execution.status.replace('_', ' ')}
                    </Badge>
                  </div>
                  {execution.error_message && (
                    <p className="text-sm text-red-500 mt-2 truncate" title={execution.error_message}>
                      {execution.error_message}
                    </p>
                  )}
                </button>
              ))}
            </div>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  );
}
