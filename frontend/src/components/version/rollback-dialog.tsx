'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle } from 'lucide-react';
import { WorkflowVersion } from '@/lib/types/workflow';

interface RollbackDialogProps {
  version: WorkflowVersion;
  open: boolean;
  onClose: () => void;
  onConfirm: () => Promise<void>;
}

export function RollbackDialog({
  version,
  open,
  onClose,
  onConfirm,
}: RollbackDialogProps) {
  const [isRollingBack, setIsRollingBack] = useState(false);

  const handleConfirm = async () => {
    setIsRollingBack(true);
    try {
      await onConfirm();
      onClose();
    } catch (error) {
      console.error('Rollback failed:', error);
    } finally {
      setIsRollingBack(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-yellow-500" />
            Confirm Rollback
          </DialogTitle>
          <DialogDescription>
            This action will create a new version with the content from version{' '}
            <Badge variant="outline">v{version.version_number}</Badge>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="p-4 bg-muted rounded-lg">
            <p className="text-sm font-medium mb-1">
              Version {version.version_number}
            </p>
            <p className="text-sm text-muted-foreground">
              {version.change_description}
            </p>
            <p className="text-xs text-muted-foreground mt-2">
              Created {new Date(version.created_at).toLocaleString()} by{' '}
              {version.created_by}
            </p>
          </div>

          <div className="space-y-2 text-sm">
            <p className="font-medium">What happens next:</p>
            <ul className="space-y-1 text-muted-foreground list-disc list-inside">
              <li>A new version will be created</li>
              <li>Current workflow configuration will be replaced</li>
              <li>All active enrollments will continue</li>
              <li>You can undo this rollback by creating a new version</li>
            </ul>
          </div>

          <div className="p-3 bg-yellow-50 dark:bg-yellow-950 border border-yellow-200 dark:border-yellow-800 rounded">
            <p className="text-sm text-yellow-800 dark:text-yellow-200">
              <strong>Warning:</strong> This action cannot be undone. Make sure to review the
              version details before proceeding.
            </p>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={isRollingBack}>
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleConfirm}
            disabled={isRollingBack}
          >
            {isRollingBack ? 'Rolling back...' : 'Confirm Rollback'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
