'use client';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Plus, Search, Filter, SlidersHorizontal } from 'lucide-react';
import { ReactNode } from 'react';

interface CRMToolbarProps {
  title: string;
  description?: string;
  searchValue?: string;
  onSearchChange?: (value: string) => void;
  searchPlaceholder?: string;
  actions?: ReactNode;
  filters?: ReactNode;
  children?: ReactNode;
}

export function CRMToolbar({
  title,
  description,
  searchValue,
  onSearchChange,
  searchPlaceholder = 'Search...',
  actions,
  filters,
  children,
}: CRMToolbarProps) {
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
          {description && (
            <p className="text-muted-foreground">{description}</p>
          )}
        </div>
        {actions}
      </div>

      {/* Toolbar */}
      <div className="flex items-center gap-4">
        {onSearchChange && (
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder={searchPlaceholder}
              value={searchValue}
              onChange={(e) => onSearchChange(e.target.value)}
              className="pl-9"
            />
          </div>
        )}

        {filters}

        {children}
      </div>
    </div>
  );
}

interface CRMToolbarActionProps {
  label: string;
  icon?: ReactNode;
  onClick?: () => void;
  variant?: 'default' | 'outline' | 'ghost' | 'destructive';
}

export function CRMToolbarAction({
  label,
  icon,
  onClick,
  variant = 'default',
}: CRMToolbarActionProps) {
  return (
    <Button variant={variant} onClick={onClick}>
      {icon}
      {label}
    </Button>
  );
}
