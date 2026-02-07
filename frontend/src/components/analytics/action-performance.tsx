'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import { CheckCircle2, XCircle, Clock, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { DropOffData } from '@/lib/types/workflow';

interface ActionPerformanceProps {
  data: DropOffData[];
  isLoading?: boolean;
  className?: string;
}

interface ActionPerformanceItemProps {
  name: string;
  dropOffCount: number;
  dropOffRate: number;
}

function ActionPerformanceItem({ name, dropOffCount, dropOffRate }: ActionPerformanceItemProps) {
  const getPerformanceLevel = (rate: number) => {
    if (rate < 5) return { label: 'Excellent', color: 'bg-green-500', icon: CheckCircle2 };
    if (rate < 15) return { label: 'Good', color: 'bg-blue-500', icon: CheckCircle2 };
    if (rate < 30) return { label: 'Fair', color: 'bg-yellow-500', icon: AlertTriangle };
    return { label: 'Poor', color: 'bg-red-500', icon: XCircle };
  };

  const performance = getPerformanceLevel(dropOffRate);
  const Icon = performance.icon;

  return (
    <div className="flex items-center justify-between py-3 px-4 hover:bg-muted/50 rounded-lg transition-colors">
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <Icon className={cn('h-5 w-5', performance.color.replace('bg-', 'text-'))} aria-hidden="true" />
        <div className="flex-1 min-w-0">
          <p className="font-medium truncate" title={name}>
            {name}
          </p>
          <p className="text-sm text-muted-foreground">{dropOffCount.toLocaleString()} drop-offs</p>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <Badge
          variant={dropOffRate < 15 ? 'default' : dropOffRate < 30 ? 'secondary' : 'destructive'}
          className="shrink-0"
        >
          {dropOffRate.toFixed(1)}%
        </Badge>
        <Badge variant="outline" className="shrink-0">
          {performance.label}
        </Badge>
      </div>
    </div>
  );
}

export function ActionPerformance({ data, isLoading, className }: ActionPerformanceProps) {
  if (isLoading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Action Performance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-16 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const sortedData = [...data].sort((a, b) => b.drop_off_rate - a.drop_off_rate);

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Action Performance</CardTitle>
      </CardHeader>
      <CardContent>
        {sortedData.length === 0 ? (
          <div className="flex items-center justify-center h-[300px] text-muted-foreground">
            No performance data available
          </div>
        ) : (
          <ScrollArea className="h-[400px] pr-4">
            <div className="space-y-1">
              {sortedData.map((item, index) => (
                <ActionPerformanceItem
                  key={`${item.step_name}-${index}`}
                  name={item.step_name}
                  dropOffCount={item.drop_off_count}
                  dropOffRate={item.drop_off_rate}
                />
              ))}
            </div>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  );
}
