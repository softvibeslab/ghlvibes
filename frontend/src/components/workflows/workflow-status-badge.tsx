import { Badge } from '@/components/ui/badge';
import { WorkflowStatus } from '@/lib/types/workflow';
import { CheckCircle2, PauseCircle, FileEdit, Archive } from 'lucide-react';

interface WorkflowStatusBadgeProps {
  status: WorkflowStatus;
}

export function WorkflowStatusBadge({ status }: WorkflowStatusBadgeProps) {
  const config = {
    active: {
      label: 'Active',
      variant: 'success' as const,
      icon: CheckCircle2,
    },
    draft: {
      label: 'Draft',
      variant: 'secondary' as const,
      icon: FileEdit,
    },
    paused: {
      label: 'Paused',
      variant: 'warning' as const,
      icon: PauseCircle,
    },
    archived: {
      label: 'Archived',
      variant: 'outline' as const,
      icon: Archive,
    },
  }[status];

  const Icon = config.icon;

  return (
    <Badge variant={config.variant} className="gap-1">
      <Icon className="h-3 w-3" />
      {config.label}
    </Badge>
  );
}
