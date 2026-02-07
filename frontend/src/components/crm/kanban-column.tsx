'use client';

import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Deal } from '@/lib/types/crm';
import { DealCard } from './deal-card';
import { formatCurrency } from '@/lib/utils';

interface KanbanColumnProps {
  id: string;
  title: string;
  deals: Deal[];
  probability?: number;
  totalValue?: number;
  onDealClick?: (deal: Deal) => void;
}

export function KanbanColumn({
  id,
  title,
  deals,
  probability,
  totalValue,
  onDealClick,
}: KanbanColumnProps) {
  const columnTotal = totalValue || deals.reduce((sum, deal) => sum + deal.value, 0);

  return (
    <div className="flex flex-col w-[320px] min-w-[320px] h-full bg-muted/50 rounded-lg">
      <div className="p-4 border-b bg-background rounded-t-lg">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold">{title}</h3>
          <Badge variant="secondary">{deals.length}</Badge>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="font-medium">{formatCurrency(columnTotal)}</span>
          {probability && (
            <span className="text-muted-foreground">{probability}%</span>
          )}
        </div>
      </div>

      <ScrollArea className="flex-1 p-3">
        <div className="space-y-3" data-stage-id={id}>
          {deals.map((deal) => (
            <div key={deal.id} data-id={deal.id}>
              <DealCard deal={deal} onClick={() => onDealClick?.(deal)} />
            </div>
          ))}
        </div>

        {deals.length === 0 && (
          <div className="text-center py-8 text-sm text-muted-foreground">
            No deals
          </div>
        )}
      </ScrollArea>
    </div>
  );
}
