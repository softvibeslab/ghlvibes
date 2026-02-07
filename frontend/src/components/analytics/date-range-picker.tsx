'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Badge } from '@/components/ui/badge';
import { CalendarIcon, ChevronDown } from 'lucide-react';
import { format, subDays, subMonths, startOfDay, endOfDay } from 'date-fns';
import { cn } from '@/lib/utils';
import { es } from 'date-fns/locale';

interface DateRangePickerProps {
  value: { start: Date; end: Date };
  onChange: (range: { start: Date; end: Date }) => void;
  className?: string;
}

const presets = [
  { label: 'Last 7 days', days: 7 },
  { label: 'Last 30 days', days: 30 },
  { label: 'Last 90 days', days: 90 },
  { label: 'Last 3 months', months: 3 },
  { label: 'Last 6 months', months: 6 },
  { label: 'Last 12 months', months: 12 },
];

export function DateRangePicker({ value, onChange, className }: DateRangePickerProps) {
  const [open, setOpen] = useState(false);
  const [presetIndex, setPresetIndex] = useState(1); // Default to 30 days

  const handlePresetClick = (preset: typeof presets[0], index: number) => {
    const end = new Date();
    const start = preset.days
      ? subDays(end, preset.days)
      : subMonths(end, preset.months || 0);

    onChange({ start: startOfDay(start), end: endOfDay(end) });
    setPresetIndex(index);
  };

  const handleDateSelect = (date: Date | undefined) => {
    if (!date) return;

    // If start date is not set or is after end date, set it as start
    if (!value.start || value.start > value.end) {
      onChange({ start: startOfDay(date), end: value.end || endOfDay(new Date()) });
    } else {
      // Otherwise, set it as end
      onChange({
        start: value.start,
        end: date > value.start ? endOfDay(date) : startOfDay(date),
      });
    }
  };

  const formatDate = (date: Date) => format(date, 'MMM d, yyyy');

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            className={cn(
              'justify-start text-left font-normal min-w-[300px]',
              !value.start && 'text-muted-foreground'
            )}
            aria-label="Select date range"
          >
            <CalendarIcon className="mr-2 h-4 w-4" aria-hidden="true" />
            {value.start ? (
              <>
                {formatDate(value.start)} - {formatDate(value.end)}
                <ChevronDown className="ml-auto h-4 w-4" aria-hidden="true" />
              </>
            ) : (
              <>Pick a date range</>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <div className="p-3 border-b">
            <p className="text-sm font-medium mb-2">Quick select</p>
            <div className="flex flex-wrap gap-2">
              {presets.map((preset, index) => (
                <Badge
                  key={preset.label}
                  variant={presetIndex === index ? 'default' : 'outline'}
                  className="cursor-pointer hover:bg-accent"
                  onClick={() => handlePresetClick(preset, index)}
                >
                  {preset.label}
                </Badge>
              ))}
            </div>
          </div>
          <Calendar
            mode="single"
            selected={value.end}
            onSelect={handleDateSelect}
            numberOfMonths={2}
            disabled={(date) => date > new Date()}
            initialFocus
          />
        </PopoverContent>
      </Popover>
    </div>
  );
}
