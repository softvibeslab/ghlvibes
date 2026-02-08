// Custom Step Node Component for React Flow

'use client';

import React, { memo } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import type { WorkflowNode } from '@/lib/types/workflow';
import * as Icons from 'lucide-react';

// Icon mapping
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

interface StepNodeData {
  label: string;
  icon: string;
  type: 'trigger' | 'action' | 'condition' | 'wait' | 'goal';
  config: Record<string, unknown>;
  status: 'pending' | 'active' | 'completed' | 'error';
}

export const StepNode = memo(({ data, selected }: NodeProps<StepNodeData>) => {
  const nodeData = data as StepNodeData;
  const IconComponent = IconMap[nodeData.icon] || Icons.Box;

  // Color coding by node type
  const getTypeColor = () => {
    switch (nodeData.type) {
      case 'trigger':
        return 'border-blue-500 bg-blue-50 dark:bg-blue-950';
      case 'action':
        return 'border-green-500 bg-green-50 dark:bg-green-950';
      case 'condition':
        return 'border-orange-500 bg-orange-50 dark:bg-orange-950';
      case 'wait':
        return 'border-purple-500 bg-purple-50 dark:bg-purple-950';
      case 'goal':
        return 'border-pink-500 bg-pink-50 dark:bg-pink-950';
      default:
        return 'border-gray-500 bg-gray-50 dark:bg-gray-950';
    }
  };

  // Status indicator
  const getStatusColor = () => {
    switch (nodeData.status) {
      case 'active':
        return 'bg-blue-500';
      case 'completed':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-400';
    }
  };

  return (
    <div
      className={cn(
        'relative min-w-[200px] max-w-[280px] rounded-lg border-2 bg-white p-4 shadow-md transition-all dark:bg-gray-900',
        getTypeColor(),
        selected && 'ring-2 ring-blue-500 ring-offset-2'
      )}
    >
      {/* Status indicator */}
      <div className="absolute right-2 top-2 flex h-3 w-3">
        <div className={cn('h-full w-full rounded-full', getStatusColor())} />
      </div>

      {/* Icon and Title */}
      <div className="mb-3 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white shadow-sm dark:bg-gray-800">
          <IconComponent className="h-5 w-5 text-gray-700 dark:text-gray-300" />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-sm text-gray-900 dark:text-gray-100">
            {nodeData.label}
          </h3>
          <Badge variant="outline" className="mt-1 text-xs">
            {nodeData.type}
          </Badge>
        </div>
      </div>

      {/* Config summary */}
      {Object.keys(nodeData.config).length > 0 && (
        <div className="mt-2 rounded-md bg-gray-100 p-2 text-xs text-gray-600 dark:bg-gray-800 dark:text-gray-400">
          {Object.entries(nodeData.config)
            .slice(0, 3)
            .map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="capitalize">{key}:</span>
                <span className="ml-2 truncate text-gray-900 dark:text-gray-100">
                  {String(value)}
                </span>
              </div>
            ))}
          {Object.keys(nodeData.config).length > 3 && (
            <div className="mt-1 text-center text-gray-500">+ more</div>
          )}
        </div>
      )}

      {/* Input Handle (Top) */}
      {nodeData.type !== 'trigger' && (
        <Handle
          type="target"
          position={Position.Top}
          className="!h-3 !w-3 !border-2 !border-gray-400 !bg-white"
        />
      )}

      {/* Output Handle (Bottom) */}
      {nodeData.type !== 'goal' && (
        <Handle
          type="source"
          position={Position.Bottom}
          className="!h-3 !w-3 !border-2 !border-gray-400 !bg-white"
        />
      )}

      {/* Conditional handles for if/else */}
      {nodeData.type === 'condition' && (
        <>
          <Handle
            type="source"
            position={Position.Right}
            id="true"
            className="!h-3 !w-3 !border-2 !border-green-400 !bg-white"
            style={{ top: '50%' }}
          />
          <Handle
            type="source"
            position={Position.Left}
            id="false"
            className="!h-3 !w-3 !border-2 !border-red-400 !bg-white"
            style={{ top: '50%' }}
          />
        </>
      )}
    </div>
  );
});

StepNode.displayName = 'StepNode';
