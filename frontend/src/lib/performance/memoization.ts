'use client';

import { useMemo, useCallback, useRef, useEffect } from 'react';

// Custom hook for memoized expensive calculations
export function useMemoized<T>(
  factory: () => T,
  deps: any[],
  debugKey?: string
): T {
  return useMemo(factory, deps);
}

// Custom hook for memoized callbacks with debug support
export function useMemoizedCallback<T extends (...args: any[]) => any>(
  callback: T,
  deps: any[],
  debugKey?: string
): T {
  return useCallback(callback, deps);
}

// Debounce hook
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
}

// Throttle hook
export function useThrottle<T>(value: T, limit: number): T {
  const [throttledValue, setThrottledValue] = useState(value);
  const lastRan = useRef(Date.now());

  useEffect(() => {
    const handler = setTimeout(() => {
      if (Date.now() - lastRan.current >= limit) {
        setThrottledValue(value);
        lastRan.current = Date.now();
      }
    }, limit - (Date.now() - lastRan.current));

    return () => clearTimeout(handler);
  }, [value, limit]);

  return throttledValue;
}

// Memoized component wrapper with debug support
export function withMemo<P extends object>(
  Component: React.ComponentType<P>,
  customComparison?: (prevProps: P, nextProps: P) => boolean
) {
  const MemoizedComponent = React.memo(Component, customComparison);

  MemoizedComponent.displayName = `Memo(${
    Component.displayName || Component.name || 'Component'
  })`;

  return MemoizedComponent;
}

// Use previous value hook
export function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>();
  useEffect(() => {
    ref.current = value;
  }, [value]);
  return ref.current;
}

// Use deep comparison for useMemo
export function useDeepMemo<T>(factory: () => T, deps: any[]): T {
  const ref = useRef<{ deps: any[]; value: T }>();

  if (!ref.current || !deepEqual(ref.current.deps, deps)) {
    ref.current = { deps, value: factory() };
  }

  return ref.current.value;
}

// Deep equal function
function deepEqual(a: any, b: any): boolean {
  if (a === b) return true;

  if (typeof a !== typeof b) return false;

  if (typeof a !== 'object' || a === null || b === null) {
    return a === b;
  }

  const keysA = Object.keys(a);
  const keysB = Object.keys(b);

  if (keysA.length !== keysB.length) return false;

  return keysA.every((key) => deepEqual(a[key], b[key]));
}
