'use client';

import dynamic from 'next/dynamic';
import { ComponentType } from 'react';

// Heavy components that should be code-split
export const WorkflowBuilder = dynamic(
  () => import('@/components/workflows/builder/WorkflowBuilder'),
  {
    loading: () => <div>Loading builder...</div>,
    ssr: false,
  }
);

export const AnalyticsDashboard = dynamic(
  () => import('@/components/analytics/metrics-cards'),
  {
    loading: () => <div>Loading analytics...</div>,
    ssr: true,
  }
);

export const TemplateGallery = dynamic(
  () => import('@/components/templates/template-gallery'),
  {
    loading: () => <div>Loading templates...</div>,
    ssr: true,
  }
);

export const ExecutionDetailModal = dynamic(
  () => import('@/components/execution/execution-detail-modal'),
  {
    loading: () => <div>Loading details...</div>,
    ssr: false,
  }
);

export const BulkEnrollmentModal = dynamic(
  () => import('@/components/bulk/bulk-enrollment-modal'),
  {
    loading: () => <div>Opening bulk enrollment...</div>,
    ssr: false,
  }
);

export const VersionComparisonModal = dynamic(
  () => import('@/components/version/version-comparison-modal'),
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
