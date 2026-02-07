'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { PipelineForecast } from '@/lib/types/crm';
import { formatCurrency } from '@/lib/utils';

interface DealForecastCardProps {
  forecast: PipelineForecast;
}

export function DealForecastCard({ forecast }: DealForecastCardProps) {
  const totalValue = forecast.stages.reduce((sum, stage) => sum + stage.total_value, 0);
  const weightedValue = forecast.stages.reduce((sum, stage) => sum + stage.weighted_value, 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle>{forecast.pipeline_name} - Forecast</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Total Value</p>
            <p className="text-2xl font-bold">{formatCurrency(totalValue)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Weighted Value</p>
            <p className="text-2xl font-bold text-green-600">
              {formatCurrency(weightedValue)}
            </p>
          </div>
        </div>

        <div className="space-y-4">
          {forecast.stages.map((stage) => (
            <div key={stage.stage_id} className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">{stage.stage_name}</span>
                <div className="text-right">
                  <span className="font-semibold">{formatCurrency(stage.total_value)}</span>
                  <span className="text-muted-foreground ml-2">
                    ({stage.deal_count} deals)
                  </span>
                </div>
              </div>
              <Progress value={stage.probability} className="h-2" />
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>Probability: {stage.probability}%</span>
                <span>Weighted: {formatCurrency(stage.weighted_value)}</span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
