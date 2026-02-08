'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

interface KeyboardNavProps {
  children: React.ReactNode;
  orientation?: 'horizontal' | 'vertical' | 'both';
  loop?: boolean;
  className?: string;
}

export function KeyboardNav({
  children,
  orientation = 'both',
  loop = true,
  className,
}: KeyboardNavProps) {
  const containerRef = React.useRef<HTMLDivElement>(null);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    const container = containerRef.current;
    if (!container) return;

    const focusableElements = Array.from(
      container.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
    ) as HTMLElement[];

    const currentIndex = focusableElements.indexOf(
      document.activeElement as HTMLElement
    );

    if (currentIndex === -1) return;

    let nextIndex = currentIndex;

    switch (e.key) {
      case 'ArrowDown':
      case 'ArrowRight':
        if (orientation === 'vertical' && e.key === 'ArrowRight') return;
        if (orientation === 'horizontal' && e.key === 'ArrowDown') return;
        e.preventDefault();
        nextIndex = currentIndex + 1;
        if (loop && nextIndex >= focusableElements.length) {
          nextIndex = 0;
        }
        break;

      case 'ArrowUp':
      case 'ArrowLeft':
        if (orientation === 'vertical' && e.key === 'ArrowLeft') return;
        if (orientation === 'horizontal' && e.key === 'ArrowUp') return;
        e.preventDefault();
        nextIndex = currentIndex - 1;
        if (loop && nextIndex < 0) {
          nextIndex = focusableElements.length - 1;
        }
        break;

      case 'Home':
        if (orientation !== 'vertical') {
          e.preventDefault();
          nextIndex = 0;
        }
        break;

      case 'End':
        if (orientation !== 'vertical') {
          e.preventDefault();
          nextIndex = focusableElements.length - 1;
        }
        break;

      default:
        return;
    }

    focusableElements[nextIndex]?.focus();
  };

  return (
    <div
      ref={containerRef}
      onKeyDown={handleKeyDown}
      className={className}
      role="presentation"
    >
      {children}
    </div>
  );
}

interface UseKeyboardNavProps {
  itemCount: number;
  orientation?: 'horizontal' | 'vertical';
  loop?: boolean;
}

export function useKeyboardNav({
  itemCount,
  orientation = 'vertical',
  loop = true,
}: UseKeyboardNavProps) {
  const [focusedIndex, setFocusedIndex] = React.useState(0);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    let nextIndex = focusedIndex;

    switch (e.key) {
      case 'ArrowDown':
      case 'ArrowRight':
        if (orientation === 'vertical' && e.key === 'ArrowRight') return;
        if (orientation === 'horizontal' && e.key === 'ArrowDown') return;
        e.preventDefault();
        nextIndex = focusedIndex + 1;
        if (loop && nextIndex >= itemCount) {
          nextIndex = 0;
        }
        break;

      case 'ArrowUp':
      case 'ArrowLeft':
        if (orientation === 'vertical' && e.key === 'ArrowLeft') return;
        if (orientation === 'horizontal' && e.key === 'ArrowUp') return;
        e.preventDefault();
        nextIndex = focusedIndex - 1;
        if (loop && nextIndex < 0) {
          nextIndex = itemCount - 1;
        }
        break;

      case 'Home':
        e.preventDefault();
        nextIndex = 0;
        break;

      case 'End':
        e.preventDefault();
        nextIndex = itemCount - 1;
        break;

      default:
        return;
    }

    setFocusedIndex(nextIndex);
  };

  return {
    focusedIndex,
    setFocusedIndex,
    handleKeyDown,
  };
}
