'use client';

import dynamic from 'next/dynamic';
import { ComponentType, useState, useEffect } from 'react';

// Heavy components that should be code-split
// Using lazy loading for better performance
export const WorkflowBuilder = dynamic(
  () => import('@/components/workflows/builder/WorkflowBuilder').then(mod => ({ default: mod.WorkflowBuilder })),
  {
    loading: () => <div>Loading builder...</div>,
    ssr: false,
  }
);

// Note: These components may need adjustment based on their actual export patterns
export const MetricsCards = dynamic(
  () => import('@/components/analytics/metrics-cards').then(mod => ({ default: mod.MetricsCards })),
  {
    loading: () => <div>Loading analytics...</div>,
    ssr: true,
  }
);

export const ExecutionDetailModal = dynamic(
  () => import('@/components/execution/execution-detail-modal').then(mod => ({ default: mod.ExecutionDetailModal })),
  {
    loading: () => <div>Loading details...</div>,
    ssr: false,
  }
);

export const BulkEnrollmentModal = dynamic(
  () => import('@/components/bulk/bulk-enrollment-modal').then(mod => ({ default: mod.BulkEnrollmentModal })),
  {
    loading: () => <div>Opening bulk enrollment...</div>,
    ssr: false,
  }
);

export const VersionComparisonModal = dynamic(
  () => import('@/components/version/version-comparison-modal').then(mod => ({ default: mod.VersionComparisonModal })),
  {
    loading: () => <div>Loading comparison...</div>,
    ssr: false,
  }
);

// Hook for lazy loading components
export function useLazyComponent<T>(
  importFn: () => Promise<{ default: ComponentType<T> }>,
  deps: any[] = []
) {
  const [component, setComponent] = useState<ComponentType<T> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    importFn()
      .then((module) => {
        setComponent(() => module.default);
        setLoading(false);
      })
      .catch((err) => {
        setError(err);
        setLoading(false);
      });
  }, deps);

  return { component, loading, error };
}
