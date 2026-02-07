'use client';

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { TaskForm } from './task-form';
import { useQuery } from '@tanstack/react-query';
import type { Task, CreateTaskDto } from '@/lib/types/crm';

interface TaskModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  task?: Task;
  mode: 'create' | 'edit';
  onSave?: (data: CreateTaskDto) => void;
  isSaving?: boolean;
}

export function TaskModal({
  open,
  onOpenChange,
  task,
  mode,
  onSave,
  isSaving = false,
}: TaskModalProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {mode === 'create' ? 'Create Task' : 'Edit Task'}
          </DialogTitle>
          {mode === 'create' && (
            <DialogDescription>
              Create a new task or reminder
            </DialogDescription>
          )}
        </DialogHeader>

        <TaskForm
          initialData={task}
          onSubmit={(data) => onSave?.(data)}
          isLoading={isSaving}
          submitLabel={mode === 'create' ? 'Create Task' : 'Save Changes'}
        />
      </DialogContent>
    </Dialog>
  );
}
