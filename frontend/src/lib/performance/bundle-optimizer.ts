'use client';

import { useEffect, useState } from 'react';

// Performance metrics interface
interface PerformanceMetrics {
  bundleSize: number;
  loadTime: number;
  renderTime: number;
  interactionTime: number;
}

// Hook to measure performance
export function usePerformanceMetrics() {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    bundleSize: 0,
    loadTime: 0,
    renderTime: 0,
    interactionTime: 0,
  });

  useEffect(() => {
    if (typeof window === 'undefined' || !window.performance) return;

    const measurePerformance = () => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      const paint = performance.getEntriesByType('paint');

      const loadTime = navigation?.loadEventEnd - navigation?.fetchStart || 0;
      const renderTime = paint.find((entry) => entry.name === 'first-contentful-paint')?.startTime || 0;

      setMetrics({
        bundleSize: 0, // Calculated separately
        loadTime,
        renderTime,
        interactionTime: 0,
      });
    };

    // Wait for page to fully load
    if (document.readyState === 'complete') {
      measurePerformance();
    } else {
      window.addEventListener('load', measurePerformance);
      return () => window.removeEventListener('load', measurePerformance);
    }
  }, []);

  return metrics;
}

// Web Vitals tracking
export function useWebVitals() {
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const trackWebVitals = async () => {
      try {
        const { getCLS, getFID, getFCP, getLCP, getTTFB } = await import('web-vitals');

        getCLS(console.log);
        getFID(console.log);
        getFCP(console.log);
        getLCP(console.log);
        getTTFB(console.log);
      } catch (error) {
        console.warn('Failed to load web-vitals:', error);
      }
    };

    trackWebVitals();
  }, []);

  return null;
}

// Resource hint helper
export function useResourceHints() {
  useEffect(() => {
    if (typeof document === 'undefined') return;

    // Preconnect to important origins
    const preconnectOrigins = [
      'https://api.example.com',
      'https://cdn.example.com',
    ];

    preconnectOrigins.forEach((origin) => {
      const link = document.createElement('link');
      link.rel = 'preconnect';
      link.href = origin;
      document.head.appendChild(link);
    });

    return () => {
      preconnectOrigins.forEach((origin) => {
        const link = document.querySelector(`link[rel="preconnect"][href="${origin}"]`);
        if (link) link.remove();
      });
    };
  }, []);
}

// Image optimization helper
export function useOptimizedImage(src: string, width: number, quality: number = 75) {
  const optimizedSrc = useMemo(() => {
    if (typeof window === 'undefined') return src;

    // Add image optimization parameters for Next.js Image
    const url = new URL(src, window.location.origin);
    url.searchParams.set('w', width.toString());
    url.searchParams.set('q', quality.toString());

    return url.toString();
  }, [src, width, quality]);

  return optimizedSrc;
}

// Lazy load images hook
export function useLazyImage(src: string) {
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const img = new Image();

    img.onload = () => {
      setImageSrc(src);
      setIsLoading(false);
    };

    img.onerror = () => {
      setError(new Error('Failed to load image'));
      setIsLoading(false);
    };

    // Load image
    img.src = src;

    return () => {
      img.onload = null;
      img.onerror = null;
    };
  }, [src]);

  return { imageSrc, isLoading, error };
}

import { useMemo } from 'react';
