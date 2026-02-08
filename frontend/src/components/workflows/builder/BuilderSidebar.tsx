// Builder Sidebar - Step Palette

'use client';

import React, { useState, useMemo } from 'react';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { useCanvasStore } from '@/lib/stores/canvas-store';
import { useWorkflowStore } from '@/lib/stores/workflow-store';
import {
  TRIGGER_DEFINITIONS,
  ACTION_DEFINITIONS,
  TRIGGER_CATEGORIES,
  ACTION_CATEGORIES,
  type StepDefinition,
} from '@/lib/constants/step-types';
import { cn } from '@/lib/utils';
import * as Icons from 'lucide-react';
import { ChevronDown, Search } from 'lucide-react';

const IconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  UserPlus: Icons.UserPlus,
  UserEdit: Icons.UserPen,
  Tag: Icons.Tag,
  Cake: Icons.Cake,
  Heart: Icons.Heart,
  FileText: Icons.FileText,
  GitBranch: Icons.GitBranch,
  GitCommit: Icons.GitCommit,
  CalendarPlus: Icons.CalendarPlus,
  CalendarX: Icons.CalendarX,
  CalendarCheck: Icons.CalendarCheck,
  UserX: Icons.UserX,
  DollarSign: Icons.DollarSign,
  XCircle: Icons.XCircle,
  CreditCard: Icons.CreditCard,
  UserMinus: Icons.UserMinus,
  MailOpen: Icons.MailOpen,
  MousePointerClick: Icons.MousePointerClick,
  MessageSquareReply: Icons.MessageSquareReply,
  Phone: Icons.Phone,
  Clock: Icons.Clock,
  RefreshCw: Icons.RefreshCw,
  Target: Icons.Target,
  Webhook: Icons.Webhook,
  Mail: Icons.Mail,
  MessageSquare: Icons.MessageSquare,
  PhoneCall: Icons.PhoneCall,
  MessageCircle: Icons.MessageCircle,
  PhoneOutgoing: Icons.PhoneOutgoing,
  Settings: Icons.Settings,
  GitMerge: Icons.GitMerge,
  UserCheck: Icons.UserCheck,
  CalendarClock: Icons.CalendarClock,
  Calendar: Icons.Calendar,
  GitCompare: Icons.GitCompare,
  CheckSquare: Icons.CheckSquare,
  Bell: Icons.Bell,
  X: Icons.X,
};

interface StepCategory {
  id: string;
  label: string;
  description: string;
  color: string;
}

interface CategoryGroup {
  category: StepCategory;
  steps: StepDefinition[];
}

export function BuilderSidebar() {
  const { sidebarOpen, toggleSidebar, addNode } = useCanvasStore();
  const { setHasUnsavedChanges } = useWorkflowStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [openCategories, setOpenCategories] = useState<Set<string>>(new Set(['trigger', 'action']));

  // Group steps by category
  const groupedSteps = useMemo(() => {
    const groups: CategoryGroup[] = [];

    // Trigger groups
    Object.values(TRIGGER_CATEGORIES).forEach((cat) => {
      const steps = TRIGGER_DEFINITIONS.filter((step) =>
        step.color === cat.color
      );
      if (steps.length > 0) {
        groups.push({ category: cat, steps });
      }
    });

    // Action groups
    Object.values(ACTION_CATEGORIES).forEach((cat) => {
      const steps = ACTION_DEFINITIONS.filter((step) =>
        step.color === cat.color
      );
      if (steps.length > 0) {
        groups.push({ category: cat, steps });
      }
    });

    return groups;
  }, []);

  // Filter steps by search query
  const filteredGroups = useMemo(() => {
    if (!searchQuery.trim()) {
      return groupedSteps;
    }

    const query = searchQuery.toLowerCase();

    return groupedSteps
      .map((group) => ({
        ...group,
        steps: group.steps.filter(
          (step) =>
            step.label.toLowerCase().includes(query) ||
            step.description.toLowerCase().includes(query)
        ),
      }))
      .filter((group) => group.steps.length > 0);
  }, [groupedSteps, searchQuery]);

  const toggleCategory = (categoryId: string) => {
    setOpenCategories((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(categoryId)) {
        newSet.delete(categoryId);
      } else {
        newSet.add(categoryId);
      }
      return newSet;
    });
  };

  const handleAddStep = (step: StepDefinition) => {
    // Generate a unique ID for the new node
    const nodeId = `${step.type}-${Date.now()}`;

    // Calculate position based on existing nodes
    const existingNodes = useCanvasStore.getState().nodes;
    const yPos = existingNodes.length > 0 ? Math.max(...existingNodes.map((n) => n.position.y)) + 150 : 100;

    const newNode = {
      id: nodeId,
      type: step.category as any,
      position: { x: 400, y: yPos },
      data: {
        label: step.label,
        icon: step.icon,
        type: step.category,
        config: {},
        status: 'pending' as const,
      },
    };

    addNode(newNode);
    setHasUnsavedChanges(true);
  };

  if (!sidebarOpen) {
    return (
      <button
        onClick={toggleSidebar}
        className="fixed left-0 top-1/2 z-10 -translate-y-1/2 rounded-r-lg bg-gray-900 p-2 text-white transition-all hover:bg-gray-700"
        title="Open Sidebar"
      >
        <ChevronDown className="h-5 w-5 rotate-[-90deg]" />
      </button>
    );
  }

  return (
    <div className="flex h-full w-80 flex-col border-r bg-white dark:border-gray-800 dark:bg-gray-900">
      {/* Header */}
      <div className="border-b p-4">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Steps
          </h2>
          <button
            onClick={toggleSidebar}
            className="rounded p-1 hover:bg-gray-100 dark:hover:bg-gray-800"
            title="Close Sidebar"
          >
            <ChevronDown className="h-5 w-5 rotate-[-90deg]" />
          </button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <Input
            placeholder="Search steps..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      {/* Step List */}
      <ScrollArea className="flex-1">
        <div className="space-y-1 p-2">
          {filteredGroups.map((group) => (
            <Collapsible
              key={group.category.id}
              open={openCategories.has(group.category.id)}
              onOpenChange={() => toggleCategory(group.category.id)}
            >
              <CollapsibleTrigger className="flex w-full items-center justify-between rounded-lg p-3 hover:bg-gray-100 dark:hover:bg-gray-800">
                <div className="flex items-center gap-2">
                  <div className={cn('h-2 w-2 rounded-full', group.category.color)} />
                  <div className="text-left">
                    <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {group.category.label}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      {group.category.description}
                    </div>
                  </div>
                </div>
                <ChevronDown
                  className={cn(
                    'h-4 w-4 text-gray-400 transition-transform',
                    openCategories.has(group.category.id) && 'rotate-180'
                  )}
                />
              </CollapsibleTrigger>

              <CollapsibleContent className="space-y-1 p-2">
                {group.steps.map((step) => {
                  const IconComponent = IconMap[step.icon] || Icons.Box;
                  return (
                    <button
                      key={step.type}
                      onClick={() => handleAddStep(step)}
                      className="flex w-full items-start gap-3 rounded-lg border border-transparent p-3 text-left transition-all hover:border-gray-200 hover:bg-gray-50 dark:hover:border-gray-700 dark:hover:bg-gray-800"
                      title={step.description}
                    >
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-gray-100 dark:bg-gray-800">
                        <IconComponent className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {step.label}
                        </div>
                        <div className=" truncate text-xs text-gray-500 dark:text-gray-400">
                          {step.description}
                        </div>
                      </div>
                      <Badge variant="outline" className="shrink-0 text-xs">
                        {step.category}
                      </Badge>
                    </button>
                  );
                })}
              </CollapsibleContent>
            </Collapsible>
          ))}
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="border-t p-4">
        <div className="text-xs text-gray-500 dark:text-gray-400">
          <div className="flex justify-between">
            <span>Triggers:</span>
            <span className="font-semibold">{TRIGGER_DEFINITIONS.length}</span>
          </div>
          <div className="flex justify-between">
            <span>Actions:</span>
            <span className="font-semibold">{ACTION_DEFINITIONS.length}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
