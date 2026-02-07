import { Badge } from '@/components/ui/badge';
import type { ContactStatus } from '@/lib/types/crm';

interface ContactStatusBadgeProps {
  status: ContactStatus;
}

const statusConfig: Record<
  ContactStatus,
  { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline' }
> = {
  lead: { label: 'Lead', variant: 'secondary' },
  prospect: { label: 'Prospect', variant: 'default' },
  customer: { label: 'Customer', variant: 'default' },
  churned: { label: 'Churned', variant: 'destructive' },
};

export function ContactStatusBadge({ status }: ContactStatusBadgeProps) {
  const config = statusConfig[status];

  return (
    <Badge variant={config.variant} className="whitespace-nowrap">
      {config.label}
    </Badge>
  );
}
