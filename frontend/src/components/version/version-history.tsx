'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Clock,
  User,
  GitBranch,
  RotateCounterClockwise,
  Eye,
  GitCompare,
} from 'lucide-react';
import { WorkflowVersion } from '@/lib/types/workflow';
import { formatDistanceToNow } from 'date-fns';
import { VersionComparisonModal } from './version-comparison-modal';
import { RollbackDialog } from './rollback-dialog';

interface VersionHistoryProps {
  workflowId: string;
  currentVersion: number;
  versions: WorkflowVersion[];
  onRollback: (versionNumber: number) => Promise<void>;
  className?: string;
}

export function VersionHistory({
  workflowId,
  currentVersion,
  versions,
  onRollback,
  className,
}: VersionHistoryProps) {
  const [compareVersions, setCompareVersions] = useState<{
    from: WorkflowVersion | null;
    to: WorkflowVersion | null;
  }>({ from: null, to: null });
  const [rollbackVersion, setRollbackVersion] = useState<WorkflowVersion | null>(null);

  const sortedVersions = [...versions].sort(
    (a, b) => b.version_number - a.version_number
  );

  const handleCompare = (version: WorkflowVersion) => {
    if (!compareVersions.from) {
      setCompareVersions({ from: version, to: null });
    } else if (!compareVersions.to && version.id !== compareVersions.from.id) {
      setCompareVersions({ ...compareVersions, to: version });
    } else {
      setCompareVersions({ from: version, to: null });
    }
  };

  const clearCompare = () => {
    setCompareVersions({ from: null, to: null });
  };

  return (
    <>
      <Card className={className}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Version History</CardTitle>
            {compareVersions.from && compareVersions.to && (
              <Button
                variant="outline"
                size="sm"
                onClick={() =>
                  setCompareVersions({
                    from: compareVersions.from,
                    to: compareVersions.to,
                  })
                }
              >
                <GitCompare className="h-4 w-4 mr-2" />
                Compare Selected
              </Button>
            )}
            {(compareVersions.from || compareVersions.to) && (
              <Button variant="ghost" size="sm" onClick={clearCompare}>
                Clear Selection
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {sortedVersions.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
              <GitBranch className="h-12 w-12 mb-3" />
              <p>No version history available</p>
            </div>
          ) : (
            <ScrollArea className="h-[600px]">
              <div className="space-y-4 pr-4">
                {sortedVersions.map((version, index) => {
                  const isCurrentVersion = version.version_number === currentVersion;
                  const isSelectedForCompare =
                    compareVersions.from?.id === version.id ||
                    compareVersions.to?.id === version.id;

                  return (
                    <div
                      key={version.id}
                      className={`relative p-4 rounded-lg border transition-colors ${
                        isCurrentVersion
                          ? 'bg-primary/10 border-primary'
                          : 'bg-background hover:bg-muted/50'
                      } ${isSelectedForCompare ? 'ring-2 ring-primary' : ''}`}
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 space-y-2">
                          <div className="flex items-center gap-2">
                            <Badge variant={isCurrentVersion ? 'default' : 'outline'}>
                              v{version.version_number}
                            </Badge>
                            {isCurrentVersion && (
                              <Badge variant="secondary">Current</Badge>
                            )}
                          </div>

                          <p className="text-sm">{version.change_description}</p>

                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <User className="h-3 w-3" />
                              <span>{version.created_by}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              <span>
                                {formatDistanceToNow(new Date(version.created_at), {
                                  addSuffix: true,
                                })}
                              </span>
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleCompare(version)}
                            aria-label={`Select version ${version.version_number} for comparison`}
                          >
                            <GitCompare className="h-4 w-4" />
                          </Button>
                          {!isCurrentVersion && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setRollbackVersion(version)}
                              aria-label={`Rollback to version ${version.version_number}`}
                            >
                              <RotateCounterClockwise className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </div>

                      {index < sortedVersions.length - 1 && (
                        <div
                          className="absolute -bottom-4 left-1/2 transform -translate-x-1/2 w-0.5 h-4 bg-border"
                          aria-hidden="true"
                        />
                      )}
                    </div>
                  );
                })}
              </div>
            </ScrollArea>
          )}
        </CardContent>
      </Card>

      {/* Comparison Modal */}
      {compareVersions.from && compareVersions.to && (
        <VersionComparisonModal
          fromVersion={compareVersions.from}
          toVersion={compareVersions.to}
          open={!!compareVersions.from && !!compareVersions.to}
          onClose={clearCompare}
        />
      )}

      {/* Rollback Dialog */}
      {rollbackVersion && (
        <RollbackDialog
          version={rollbackVersion}
          open={!!rollbackVersion}
          onClose={() => setRollbackVersion(null)}
          onConfirm={() => onRollback(rollbackVersion.version_number)}
        />
      )}
    </>
  );
}
