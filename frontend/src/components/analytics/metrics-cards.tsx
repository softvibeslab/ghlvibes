'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Users, Activity, TrendingDown, Clock, Trophy, Target } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MetricsCardsProps {
  metrics: {
    totalEnrolled: number;
    currentlyActive: number;
    completed: number;
    dropOffRate: number;
    avgCompletionTime: number;
    goalAchievementRate: number;
  };
  isLoading?: boolean;
  className?: string;
}

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  isLoading?: boolean;
  variant?: 'default' | 'success' | 'warning' | 'danger';
}

function MetricCard({
  title,
  value,
  icon: Icon,
  trend,
  isLoading,
  variant = 'default',
}: MetricCardProps) {
  const variantStyles = {
    default: 'text-blue-600 bg-blue-50 dark:bg-blue-950',
    success: 'text-green-600 bg-green-50 dark:bg-green-950',
    warning: 'text-yellow-600 bg-yellow-50 dark:bg-yellow-950',
    danger: 'text-red-600 bg-red-50 dark:bg-red-950',
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <div className={cn('p-2 rounded-full', variantStyles[variant])}>
          <Icon className="h-4 w-4" aria-hidden="true" />
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <Skeleton className="h-8 w-24" />
        ) : (
          <>
            <div className="text-2xl font-bold" role="status">
              {typeof value === 'number' ? value.toLocaleString() : value}
            </div>
            {trend && (
              <p
                className={cn(
                  'text-xs mt-1',
                  trend.isPositive ? 'text-green-600' : 'text-red-600'
                )}
                aria-label={`Trend: ${trend.value > 0 ? '+' : ''}${trend.value}%`}
              >
                {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}% from last period
              </p>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}

export function MetricsCards({ metrics, isLoading, className }: MetricsCardsProps) {
  return (
    <div className={cn('grid gap-4 md:grid-cols-2 lg:grid-cols-3', className)}>
      <MetricCard
        title="Total Enrolled"
        value={metrics.totalEnrolled}
        icon={Users}
        isLoading={isLoading}
        variant="default"
      />
      <MetricCard
        title="Currently Active"
        value={metrics.currentlyActive}
        icon={Activity}
        isLoading={isLoading}
        variant="success"
      />
      <MetricCard
        title="Completed"
        value={metrics.completed}
        icon={Trophy}
        isLoading={isLoading}
        variant="success"
      />
      <MetricCard
        title="Drop-off Rate"
        value={`${metrics.dropOffRate}%`}
        icon={TrendingDown}
        isLoading={isLoading}
        variant={metrics.dropOffRate > 20 ? 'danger' : metrics.dropOffRate > 10 ? 'warning' : 'success'}
      />
      <MetricCard
        title="Avg. Completion Time"
        value={`${Math.round(metrics.avgCompletionTime)} min`}
        icon={Clock}
        isLoading={isLoading}
        variant="default"
      />
      <MetricCard
        title="Goal Achievement Rate"
        value={`${metrics.goalAchievementRate}%`}
        icon={Target}
        isLoading={isLoading}
        variant={metrics.goalAchievementRate > 70 ? 'success' : metrics.goalAchievementRate > 40 ? 'warning' : 'danger'}
      />
    </div>
  );
}
