'use client';

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { WorkflowVersion } from '@/lib/types/workflow';
import { GitCompare, ArrowRight } from 'lucide-react';

interface VersionComparisonModalProps {
  fromVersion: WorkflowVersion;
  toVersion: WorkflowVersion;
  open: boolean;
  onClose: () => void;
}

interface DiffSectionProps {
  label: string;
  fromValue: string | number | null;
  toValue: string | number | null;
}

function DiffSection({ label, fromValue, toValue }: DiffSectionProps) {
  const hasChanged = fromValue !== toValue;

  return (
    <div className="grid grid-cols-[140px_1fr_1fr] gap-3 py-2">
      <div className="text-sm font-medium text-muted-foreground">{label}</div>
      <div
        className={`text-sm ${
          hasChanged ? 'line-through text-muted-foreground' : ''
        }`}
      >
        {fromValue || '-'}
      </div>
      <div className={`text-sm ${hasChanged ? 'text-green-600 font-medium' : ''}`}>
        {toValue || '-'}
      </div>
    </div>
  );
}

export function VersionComparisonModal({
  fromVersion,
  toVersion,
  open,
  onClose,
}: VersionComparisonModalProps) {
  const fromDef = fromVersion.workflow_definition;
  const toDef = toVersion.workflow_definition;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <GitCompare className="h-5 w-5" />
            Version Comparison
          </DialogTitle>
        </DialogHeader>

        <ScrollArea className="flex-1">
          <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between pb-4">
              <div className="text-center">
                <Badge variant="outline" className="mb-2">
                  v{fromVersion.version_number}
                </Badge>
                <p className="text-xs text-muted-foreground">
                  {new Date(fromVersion.created_at).toLocaleDateString()}
                </p>
              </div>
              <ArrowRight className="h-5 w-5 text-muted-foreground" />
              <div className="text-center">
                <Badge variant="default" className="mb-2">
                  v{toVersion.version_number}
                </Badge>
                <p className="text-xs text-muted-foreground">
                  {new Date(toVersion.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>

            <Separator />

            {/* Basic Information */}
            <div>
              <h3 className="text-sm font-semibold mb-4">Basic Information</h3>
              <DiffSection
                label="Name"
                fromValue={fromDef.name || null}
                toValue={toDef.name || null}
              />
              <DiffSection
                label="Description"
                fromValue={fromDef.description || null}
                toValue={toDef.description || null}
              />
              <DiffSection
                label="Status"
                fromValue={fromDef.status || null}
                toValue={toDef.status || null}
              />
            </div>

            <Separator />

            {/* Trigger */}
            <div>
              <h3 className="text-sm font-semibold mb-4">Trigger Configuration</h3>
              <DiffSection
                label="Trigger Type"
                fromValue={fromDef.trigger_type || null}
                toValue={toDef.trigger_type || null}
              />
              <div className="grid grid-cols-[140px_1fr_1fr] gap-3 py-2">
                <div className="text-sm font-medium text-muted-foreground">Config</div>
                <div className="text-xs font-mono bg-muted p-2 rounded">
                  {fromDef.trigger_config
                    ? JSON.stringify(fromDef.trigger_config, null, 2)
                    : '-'}
                </div>
                <div className="text-xs font-mono bg-muted p-2 rounded">
                  {toDef.trigger_config
                    ? JSON.stringify(toDef.trigger_config, null, 2)
                    : '-'}
                </div>
              </div>
            </div>

            <Separator />

            {/* Actions */}
            <div>
              <h3 className="text-sm font-semibold mb-4">Actions</h3>
              <div className="grid grid-cols-[140px_1fr_1fr] gap-3">
                <div className="text-sm font-medium text-muted-foreground pt-2">
                  Action Count
                </div>
                <div className="text-sm pt-2">
                  {fromDef.actions?.length || 0} actions
                </div>
                <div className="text-sm pt-2">
                  {toDef.actions?.length || 0} actions
                </div>
              </div>

              {(fromDef.actions?.length || 0) > 0 || (toDef.actions?.length || 0) > 0 ? (
                <div className="mt-4 space-y-3">
                  {[
                    ...(fromDef.actions || []),
                    ...(toDef.actions || []),
                  ]
                    .filter(
                      (action, index, self) =>
                        index === self.findIndex((a) => a.id === action.id)
                    )
                    .map((action) => {
                      const fromAction = fromDef.actions?.find(
                        (a) => a.id === action.id
                      );
                      const toAction = toDef.actions?.find((a) => a.id === action.id);

                      return (
                        <div
                          key={action.id}
                          className="p-3 border rounded-lg bg-muted/50"
                        >
                          <div className="grid grid-cols-[140px_1fr_1fr] gap-3">
                            <div className="text-xs font-medium text-muted-foreground pt-1">
                              {fromAction?.order || toAction?.order}
                            </div>
                            <div className="text-sm">
                              <div className="font-medium">
                                {fromAction?.action_type || '-'}
                              </div>
                              {fromAction?.action_config && (
                                <details className="mt-1">
                                  <summary className="text-xs text-muted-foreground cursor-pointer">
                                    Config
                                  </summary>
                                  <pre className="text-xs bg-background p-2 rounded mt-1 overflow-x-auto">
                                    {JSON.stringify(fromAction.action_config, null, 2)}
                                  </pre>
                                </details>
                              )}
                            </div>
                            <div className="text-sm">
                              <div className="font-medium">
                                {toAction?.action_type || '-'}
                              </div>
                              {toAction?.action_config && (
                                <details className="mt-1">
                                  <summary className="text-xs text-muted-foreground cursor-pointer">
                                    Config
                                  </summary>
                                  <pre className="text-xs bg-background p-2 rounded mt-1 overflow-x-auto">
                                    {JSON.stringify(toAction.action_config, null, 2)}
                                  </pre>
                                </details>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                </div>
              ) : null}
            </div>

            <Separator />

            {/* Goals */}
            <div>
              <h3 className="text-sm font-semibold mb-4">Goals</h3>
              <div className="grid grid-cols-[140px_1fr_1fr] gap-3">
                <div className="text-sm font-medium text-muted-foreground pt-2">
                  Goal Count
                </div>
                <div className="text-sm pt-2">
                  {fromDef.goals?.length || 0} goals
                </div>
                <div className="text-sm pt-2">{toDef.goals?.length || 0} goals</div>
              </div>
            </div>
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}
