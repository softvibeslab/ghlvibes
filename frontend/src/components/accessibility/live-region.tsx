'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

type LiveRegionPoliteness = 'polite' | 'assertive' | 'off';

interface LiveRegionProps {
  children: React.ReactNode;
  politeness?: LiveRegionPoliteness;
  role?: 'status' | 'alert';
  className?: string;
}

export function LiveRegion({
  children,
  politeness = 'polite',
  role = 'status',
  className,
}: LiveRegionProps) {
  return (
    <div
      role={role}
      aria-live={politeness}
      aria-atomic="true"
      className={cn('sr-only', className)}
    >
      {children}
    </div>
  );
}

interface UseLiveRegionReturn {
  announce: (message: string, politeness?: LiveRegionPoliteness) => void;
  politeRegion: React.ReactNode;
  assertiveRegion: React.ReactNode;
}

export function useLiveRegion(): UseLiveRegionReturn {
  const [politeMessage, setPoliteMessage] = React.useState('');
  const [assertiveMessage, setAssertiveMessage] = React.useState('');

  const announce = React.useCallback(
    (message: string, politeness: LiveRegionPoliteness = 'polite') => {
      if (politeness === 'assertive') {
        setAssertiveMessage(message);
        // Clear after announcement
        setTimeout(() => setAssertiveMessage(''), 1000);
      } else {
        setPoliteMessage(message);
        setTimeout(() => setPoliteMessage(''), 1000);
      }
    },
    []
  );

  const politeRegion = (
    <LiveRegion key={politeMessage} politeness="polite" role="status">
      {politeMessage}
    </LiveRegion>
  );

  const assertiveRegion = (
    <LiveRegion key={assertiveMessage} politeness="assertive" role="alert">
      {assertiveMessage}
    </LiveRegion>
  );

  return {
    announce,
    politeRegion,
    assertiveRegion,
  };
}

interface VisuallyHiddenProps {
  children: React.ReactNode;
  className?: string;
}

export function VisuallyHidden({ children, className }: VisuallyHiddenProps) {
  return (
    <div
      className={cn(
        'sr-only absolute w-px h-px p-0 -m-px overflow-hidden whitespace-nowrap border-0',
        className
      )}
    >
      {children}
    </div>
  );
}
