'use client';

import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Task } from '@/lib/types/crm';
import { TaskStatusBadge } from './task-status-badge';
import { TaskPriorityBadge } from './task-priority-badge';
import { formatRelativeTime } from '@/lib/utils';
import { Calendar, Clock, User } from 'lucide-react';

interface TaskCardProps {
  task: Task;
  onComplete?: (id: string) => void;
  onClick?: () => void;
}

export function TaskCard({ task, onComplete, onClick }: TaskCardProps) {
  const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== 'completed';

  return (
    <Card
      className={`transition-all hover:shadow-md ${isOverdue ? 'border-destructive' : ''}`}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start gap-3">
          <Checkbox
            checked={task.status === 'completed'}
            onCheckedChange={(checked) => {
              if (checked && onComplete) {
                onComplete(task.id);
              }
            }}
            onClick={(e) => e.stopPropagation()}
          />
          <div className="flex-1 min-w-0">
            <h3
              className={`font-semibold truncate ${
                task.status === 'completed' ? 'line-through text-muted-foreground' : ''
              }`}
            >
              {task.title}
            </h3>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="flex flex-wrap gap-2">
          <TaskStatusBadge status={task.status} />
          <TaskPriorityBadge priority={task.priority} />
        </div>

        {task.description && (
          <p className="text-sm text-muted-foreground line-clamp-2">
            {task.description}
          </p>
        )}

        <div className="space-y-1 text-sm text-muted-foreground">
          {task.due_date && (
            <div className={`flex items-center gap-2 ${isOverdue ? 'text-destructive' : ''}`}>
              <Calendar className="h-4 w-4" />
              <span>{formatRelativeTime(task.due_date)}</span>
              {task.due_time && <span>{task.due_time}</span>}
            </div>
          )}

          {task.assigned_user_id && (
            <div className="flex items-center gap-2">
              <User className="h-4 w-4" />
              <span>Assigned</span>
            </div>
          )}

          {task.reminder_enabled && (
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              <span>
                Reminder {task.reminder_minutes ? `${task.reminder_minutes}min before` : 'enabled'}
              </span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
