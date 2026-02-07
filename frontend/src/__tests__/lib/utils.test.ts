import { describe, it, expect } from 'vitest';
import { cn } from '@/lib/utils';

describe('cn utility function', () => {
  it('should merge class names correctly', () => {
    expect(cn('class1', 'class2')).toBe('class1 class2');
  });

  it('should handle conditional classes', () => {
    expect(cn('class1', false && 'class2', 'class3')).toBe('class1 class3');
  });

  it('should handle Tailwind class conflicts', () => {
    expect(cn('p-4', 'p-2')).toBe('p-2');
  });

  it('should return empty string for no arguments', () => {
    expect(cn()).toBe('');
  });

  it('should handle undefined and null', () => {
    expect(cn('class1', undefined, null, 'class2')).toBe('class1 class2');
  });
});

describe('formatDate utility', () => {
  it('should format dates correctly', () => {
    const date = new Date('2025-01-01T10:00:00Z');
    const formatted = formatDate(date, 'PP');
    expect(formatted).toBe('January 1st, 2025');
  });

  it('should handle relative time formatting', () => {
    const date = new Date();
    date.setMinutes(date.getMinutes() - 5);
    const formatted = formatDistanceToNow(date, { addSuffix: true });
    expect(formatted).toContain('ago');
  });
});
