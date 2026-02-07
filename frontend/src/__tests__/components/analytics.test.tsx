import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MetricsCards } from '@/components/analytics/metrics-cards';
import { FunnelChart } from '@/components/analytics/funnel-chart';
import { ActionPerformance } from '@/components/analytics/action-performance';
import { DateRangePicker } from '@/components/analytics/date-range-picker';
import { ExportButton } from '@/components/analytics/export-button';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('MetricsCards', () => {
  const mockMetrics = {
    totalEnrolled: 1000,
    currentlyActive: 500,
    completed: 400,
    dropOffRate: 10,
    avgCompletionTime: 30,
    goalAchievementRate: 75,
  };

  it('should render all metrics', () => {
    render(<MetricsCards metrics={mockMetrics} />);

    expect(screen.getByText('Total Enrolled')).toBeInTheDocument();
    expect(screen.getByText('Currently Active')).toBeInTheDocument();
    expect(screen.getByText('Completed')).toBeInTheDocument();
    expect(screen.getByText('Drop-off Rate')).toBeInTheDocument();
    expect(screen.getByText('Avg. Completion Time')).toBeInTheDocument();
    expect(screen.getByText('Goal Achievement Rate')).toBeInTheDocument();
  });

  it('should display metric values correctly', () => {
    render(<MetricsCards metrics={mockMetrics} />);

    expect(screen.getByText('1,000')).toBeInTheDocument();
    expect(screen.getByText('500')).toBeInTheDocument();
    expect(screen.getByText('400')).toBeInTheDocument();
    expect(screen.getByText('10%')).toBeInTheDocument();
    expect(screen.getByText('30 min')).toBeInTheDocument();
    expect(screen.getByText('75%')).toBeInTheDocument();
  });

  it('should show loading skeleton when isLoading is true', () => {
    const { container } = render(<MetricsCards metrics={mockMetrics} isLoading={true} />);

    const skeletons = container.querySelectorAll('[role="status"]');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('should not have accessibility violations', async () => {
    const { container } = render(<MetricsCards metrics={mockMetrics} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});

describe('FunnelChart', () => {
  const mockFunnelData = [
    {
      step_id: '1',
      step_name: 'Step 1',
      step_order: 1,
      contacts_entered: 1000,
      contacts_completed: 800,
      drop_off_count: 200,
      drop_off_rate: 20,
    },
    {
      step_id: '2',
      step_name: 'Step 2',
      step_order: 2,
      contacts_entered: 800,
      contacts_completed: 600,
      drop_off_count: 200,
      drop_off_rate: 25,
    },
  ];

  it('should render funnel chart', () => {
    render(<FunnelChart data={mockFunnelData} />);

    expect(screen.getByText('Workflow Funnel')).toBeInTheDocument();
  });

  it('should show empty state when no data', () => {
    render(<FunnelChart data={[]} />);

    expect(screen.getByText('No funnel data available')).toBeInTheDocument();
  });

  it('should show loading skeleton when isLoading', () => {
    const { container } = render(<FunnelChart data={mockFunnelData} isLoading={true} />);

    const skeleton = container.querySelector('.animate-pulse');
    expect(skeleton).toBeInTheDocument();
  });
});

describe('ActionPerformance', () => {
  const mockPerformanceData = [
    {
      step_name: 'Send Email',
      drop_off_count: 50,
      drop_off_rate: 5,
    },
    {
      step_name: 'Wait 24 Hours',
      drop_off_count: 100,
      drop_off_rate: 10,
    },
  ];

  it('should render performance list', () => {
    render(<ActionPerformance data={mockPerformanceData} />);

    expect(screen.getByText('Action Performance')).toBeInTheDocument();
    expect(screen.getByText('Send Email')).toBeInTheDocument();
    expect(screen.getByText('Wait 24 Hours')).toBeInTheDocument();
  });

  it('should display drop-off rates correctly', () => {
    render(<ActionPerformance data={mockPerformanceData} />);

    expect(screen.getByText('5.0%')).toBeInTheDocument();
    expect(screen.getByText('10.0%')).toBeInTheDocument();
  });

  it('should show empty state when no data', () => {
    render(<ActionPerformance data={[]} />);

    expect(screen.getByText('No performance data available')).toBeInTheDocument();
  });
});

describe('DateRangePicker', () => {
  it('should render date range picker', () => {
    const mockValue = { start: new Date('2025-01-01'), end: new Date('2025-01-31') };
    const handleChange = vi.fn();

    render(<DateRangePicker value={mockValue} onChange={handleChange} />);

    expect(screen.getByLabelText('Select date range')).toBeInTheDocument();
  });

  it('should call onChange when date is selected', async () => {
    const user = userEvent.setup();
    const mockValue = { start: new Date('2025-01-01'), end: new Date('2025-01-31') };
    const handleChange = vi.fn();

    render(<DateRangePicker value={mockValue} onChange={handleChange} />);

    const button = screen.getByLabelText('Select date range');
    await user.click(button);

    // Calendar should open
    expect(screen.getByRole('grid')).toBeInTheDocument();
  });
});

describe('ExportButton', () => {
  const mockAnalytics = {
    workflow_id: '123',
    date_range: { start: '2025-01-01', end: '2025-01-31' },
    overview: {
      total_enrolled: 1000,
      currently_active: 500,
      completed: 400,
      drop_off_rate: 10,
      avg_completion_time: 30,
      goal_achievement_rate: 75,
    },
    funnel: [],
    enrollments_over_time: [],
    completions_over_time: [],
    drop_off_by_step: [],
    goal_completion_rate: [],
  };

  it('should render export button', () => {
    render(<ExportButton data={mockAnalytics} />);

    expect(screen.getByText('Export')).toBeInTheDocument();
  });

  it('should open dropdown menu when clicked', async () => {
    const user = userEvent.setup();

    render(<ExportButton data={mockAnalytics} />);

    const button = screen.getByRole('button', { name: /export/i });
    await user.click(button);

    expect(screen.getByText('Export as CSV')).toBeInTheDocument();
    expect(screen.getByText('Export as JSON')).toBeInTheDocument();
    expect(screen.getByText('Print / PDF')).toBeInTheDocument();
  });
});
