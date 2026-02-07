import { Badge } from '@/components/ui/badge';
import type { DealPriority } from '@/lib/types/crm';

interface DealPriorityBadgeProps {
  priority: DealPriority;
}

const priorityConfig: Record<
  DealPriority,
  { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline' }
> = {
  low: { label: 'Low', variant: 'secondary' },
  medium: { label: 'Medium', variant: 'outline' },
  high: { label: 'High', variant: 'default' },
};

export function DealPriorityBadge({ priority }: DealPriorityBadgeProps) {
  const config = priorityConfig[priority];

  return (
    <Badge variant={config.variant} className="whitespace-nowrap">
      {config.label}
    </Badge>
  );
}
