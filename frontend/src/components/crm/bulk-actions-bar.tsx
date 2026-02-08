'use client';

import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Trash2, Tag, User, Mail, FileText } from 'lucide-react';

interface BulkActionsBarProps {
  selectedCount: number;
  onClearSelection: () => void;
  onDelete?: () => void;
  onAddTags?: () => void;
  onAssignUser?: () => void;
  onSendEmail?: () => void;
  onExport?: () => void;
}

export function BulkActionsBar({
  selectedCount,
  onClearSelection,
  onDelete,
  onAddTags,
  onAssignUser,
  onSendEmail,
  onExport,
}: BulkActionsBarProps) {
  if (selectedCount === 0) {
    return null;
  }

  return (
    <div className="flex items-center gap-4 bg-primary/10 p-3 rounded-lg">
      <span className="text-sm font-medium">
        {selectedCount} item{selectedCount !== 1 ? 's' : ''} selected
      </span>

      <div className="flex-1" />

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm">
            <Tag className="mr-2 h-4 w-4" />
            Add Tags
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          {/* TODO: Load available tags */}
          <DropdownMenuItem>Add tag logic here</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {onAssignUser && (
        <Button variant="outline" size="sm" onClick={onAssignUser}>
          <User className="mr-2 h-4 w-4" />
          Assign User
        </Button>
      )}

      {onSendEmail && (
        <Button variant="outline" size="sm" onClick={onSendEmail}>
          <Mail className="mr-2 h-4 w-4" />
          Send Email
        </Button>
      )}

      {onExport && (
        <Button variant="outline" size="sm" onClick={onExport}>
          <FileText className="mr-2 h-4 w-4" />
          Export
        </Button>
      )}

      {onDelete && (
        <Button variant="destructive" size="sm" onClick={onDelete}>
          <Trash2 className="mr-2 h-4 w-4" />
          Delete
        </Button>
      )}

      <Button variant="ghost" size="sm" onClick={onClearSelection}>
        Clear selection
      </Button>
    </div>
  );
}
