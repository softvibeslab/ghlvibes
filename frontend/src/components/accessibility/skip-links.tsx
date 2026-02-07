'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

interface SkipLinksProps {
  className?: string;
}

export function SkipLinks({ className }: SkipLinksProps) {
  return (
    <div
      className={cn(
        'sr-only focus-within:not-sr-only focus-within:absolute focus-within:top-4 focus-within:left-4 focus-within:z-50',
        className
      )}
    >
      <a
        href="#main-content"
        className="inline-flex items-center px-4 py-2 bg-primary text-primary-foreground rounded-md shadow-lg focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
      >
        Skip to main content
      </a>
      <a
        href="#navigation"
        className="inline-flex items-center px-4 py-2 bg-primary text-primary-foreground rounded-md shadow-lg focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 ml-2"
      >
        Skip to navigation
      </a>
    </div>
  );
}

interface MainContentProps {
  children: React.ReactNode;
  className?: string;
}

export function MainContent({ children, className }: MainContentProps) {
  return (
    <main id="main-content" tabIndex={-1} className={className}>
      {children}
    </main>
  );
}
