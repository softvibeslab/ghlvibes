import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { WorkflowStats } from '@/lib/types/workflow';
import { Users, Activity, CheckCircle2, TrendingDown, Clock } from 'lucide-react';

interface WorkflowMetricsProps {
  stats: WorkflowStats;
}

export function WorkflowMetrics({ stats }: WorkflowMetricsProps) {
  const metrics = [
    {
      title: 'Total Enrolled',
      value: stats.total_enrolled.toLocaleString(),
      icon: Users,
      color: 'text-blue-500',
    },
    {
      title: 'Currently Active',
      value: stats.currently_active.toLocaleString(),
      icon: Activity,
      color: 'text-green-500',
    },
    {
      title: 'Completed',
      value: stats.completed.toLocaleString(),
      icon: CheckCircle2,
      color: 'text-purple-500',
    },
    {
      title: 'Drop-off Rate',
      value: `${stats.drop_off_rate.toFixed(1)}%`,
      icon: TrendingDown,
      color: 'text-red-500',
    },
    {
      title: 'Avg. Completion Time',
      value: `${stats.avg_completion_time_minutes.toFixed(0)}m`,
      icon: Clock,
      color: 'text-orange-500',
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
      {metrics.map((metric) => {
        const Icon = metric.icon;
        return (
          <Card key={metric.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {metric.title}
              </CardTitle>
              <Icon className={`h-4 w-4 ${metric.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metric.value}</div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
