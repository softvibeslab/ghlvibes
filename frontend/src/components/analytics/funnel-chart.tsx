'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  FunnelChart as RechartsFunnelChart,
  Funnel,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  Cell,
} from 'recharts';
import { Skeleton } from '@/components/ui/skeleton';
import { FunnelStep } from '@/lib/types/workflow';

interface FunnelChartProps {
  data: FunnelStep[];
  isLoading?: boolean;
  className?: string;
}

const COLORS = [
  '#3b82f6', // blue
  '#8b5cf6', // violet
  '#a855f7', // purple
  '#d946ef', // fuchsia
  '#ec4899', // pink
  '#f43f5e', // rose
];

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-background border rounded-lg shadow-lg p-3">
        <p className="font-semibold">{data.step_name}</p>
        <p className="text-sm text-muted-foreground">
          Entered: {data.contacts_entered.toLocaleString()}
        </p>
        <p className="text-sm text-muted-foreground">
          Completed: {data.contacts_completed.toLocaleString()}
        </p>
        <p className="text-sm text-muted-foreground">
          Drop-off: {data.drop_off_count.toLocaleString()} ({data.drop_off_rate.toFixed(1)}%)
        </p>
      </div>
    );
  }
  return null;
};

export function FunnelChart({ data, isLoading, className }: FunnelChartProps) {
  const chartData = data.map((step) => ({
    name: step.step_name,
    value: step.contacts_entered,
    completed: step.contacts_completed,
    dropOff: step.drop_off_count,
    dropOffRate: step.drop_off_rate,
  }));

  if (isLoading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Workflow Funnel</CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[400px] w-full" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Workflow Funnel</CardTitle>
      </CardHeader>
      <CardContent>
        {chartData.length === 0 ? (
          <div className="flex items-center justify-center h-[400px] text-muted-foreground">
            No funnel data available
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={400}>
            <RechartsFunnelChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <Funnel
                data={chartData}
                dataKey="value"
                isAnimationActive
                lastShapeType="rectangle"
                label={(item) => `${item.name}: ${item.value.toLocaleString()}`}
                labelLine={{ stroke: '#ccc' }}
              >
                {chartData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
                <LabelList
                  dataKey="name"
                  position="center"
                  fill="#fff"
                  fontSize={12}
                  fontWeight="bold"
                />
                <Tooltip content={<CustomTooltip />} />
              </Funnel>
            </RechartsFunnelChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
