import { Badge } from '@/components/ui/badge';
import type { ContactLifecycle } from '@/lib/types/crm';

interface ContactLifecycleBadgeProps {
  lifecycle: ContactLifecycle;
}

const lifecycleConfig: Record<
  ContactLifecycle,
  { label: string; color: string }
> = {
  subscriber: { label: 'Subscriber', color: 'bg-gray-500' },
  lead: { label: 'Lead', color: 'bg-blue-500' },
  opportunity: { label: 'Opportunity', color: 'bg-yellow-500' },
  customer: { label: 'Customer', color: 'bg-green-500' },
  evangelist: { label: 'Evangelist', color: 'bg-purple-500' },
};

export function ContactLifecycleBadge({ lifecycle }: ContactLifecycleBadgeProps) {
  const config = lifecycleConfig[lifecycle];

  return (
    <Badge variant="outline" className="whitespace-nowrap">
      <div className={`mr-1.5 h-2 w-2 rounded-full ${config.color}`} />
      {config.label}
    </Badge>
  );
}
