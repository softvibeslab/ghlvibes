// Workflow Builder - Main Component with Auto-Save

'use client';

import React, { useEffect, useCallback, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { WorkflowCanvas } from './WorkflowCanvas';
import { BuilderSidebar } from './BuilderSidebar';
import { ConfigurationPanel } from './ConfigurationPanel';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useWorkflowStore } from '@/lib/stores/workflow-store';
import { useCanvasStore } from '@/lib/stores/canvas-store';
import { Save, RotateCcw, AlertCircle } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

const AUTO_SAVE_INTERVAL = 30000; // 30 seconds

export function WorkflowBuilder() {
  const params = useParams();
  const router = useRouter();
  const workflowId = params.id as string;
  const { toast } = useToast();

  const {
    workflow,
    hasUnsavedChanges,
    setHasUnsavedChanges,
    saveDraft,
    restoreDraft,
    clearDraft,
  } = useWorkflowStore();

  const { sidebarOpen, configPanelOpen, nodes, edges, reset } = useCanvasStore();

  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [showUnsavedWarning, setShowUnsavedWarning] = useState(false);

  // Auto-save effect
  useEffect(() => {
    const interval = setInterval(async () => {
      if (hasUnsavedChanges && workflow) {
        await handleAutoSave();
      }
    }, AUTO_SAVE_INTERVAL);

    return () => clearInterval(interval);
  }, [hasUnsavedChanges, workflow]);

  // Warn before leaving with unsaved changes
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = ''; // Chrome requires returnValue to be set
        setShowUnsavedWarning(true);
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [hasUnsavedChanges]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = async (e: KeyboardEvent) => {
      // Ctrl/Cmd + S: Save
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        await handleManualSave();
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [workflow, nodes, edges]);

  const handleAutoSave = useCallback(async () => {
    if (!workflow) return;

    setIsSaving(true);
    try {
      // Save to local storage as draft
      saveDraft();

      // TODO: Implement API call to save to backend
      // await workflowApi.updateWorkflow(workflowId, {
      //   ...workflow,
      //   nodes,
      //   edges,
      // });

      setLastSaved(new Date());
      setHasUnsavedChanges(false);

      toast({
        title: 'Auto-saved',
        description: 'Your workflow has been saved automatically.',
      });
    } catch (error) {
      console.error('Auto-save failed:', error);
      toast({
        title: 'Auto-save failed',
        description: 'Could not save your workflow. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  }, [workflow, nodes, edges, saveDraft, setHasUnsavedChanges, toast]);

  const handleManualSave = useCallback(async () => {
    if (!workflow) return;

    setIsSaving(true);
    try {
      // TODO: Implement API call
      // await workflowApi.updateWorkflow(workflowId, {
      //   ...workflow,
      //   nodes,
      //   edges,
      // });

      setLastSaved(new Date());
      setHasUnsavedChanges(false);

      toast({
        title: 'Workflow saved',
        description: 'Your workflow has been saved successfully.',
      });
    } catch (error) {
      console.error('Save failed:', error);
      toast({
        title: 'Save failed',
        description: 'Could not save your workflow. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  }, [workflow, nodes, edges, setHasUnsavedChanges, toast]);

  const handleDiscardChanges = useCallback(() => {
    if (confirm('Are you sure you want to discard all unsaved changes?')) {
      restoreDraft();
      setHasUnsavedChanges(false);
      setShowUnsavedWarning(false);

      toast({
        title: 'Changes discarded',
        description: 'Your workflow has been restored to the last saved state.',
      });
    }
  }, [restoreDraft, setHasUnsavedChanges, toast]);

  const handleBack = useCallback(() => {
    if (hasUnsavedChanges) {
      setShowUnsavedWarning(true);
    } else {
      router.push('/workflows');
    }
  }, [hasUnsavedChanges, router]);

  const handleConfirmLeave = useCallback(() => {
    // Save before leaving
    handleManualSave().then(() => {
      setShowUnsavedWarning(false);
      router.push('/workflows');
    });
  }, [handleManualSave, router]);

  if (!workflow) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <p className="text-lg text-gray-600">Loading workflow...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-gray-50 dark:bg-gray-950">
      {/* Header */}
      <header className="flex items-center justify-between border-b bg-white px-4 py-3 dark:border-gray-800 dark:bg-gray-900">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleBack}
          >
            ← Back
          </Button>
          <div>
            <h1 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {workflow.name}
            </h1>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Badge variant="outline">{workflow.status}</Badge>
              {lastSaved && (
                <span>Last saved: {lastSaved.toLocaleTimeString()}</span>
              )}
              {isSaving && (
                <span className="flex items-center gap-1">
                  <Save className="h-3 w-3 animate-pulse" />
                  Saving...
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {hasUnsavedChanges && (
            <Badge variant="outline" className="flex items-center gap-1">
              <AlertCircle className="h-3 w-3" />
              Unsaved changes
            </Badge>
          )}

          <Button
            variant="outline"
            size="sm"
            onClick={handleDiscardChanges}
            disabled={!hasUnsavedChanges}
          >
            <RotateCcw className="mr-2 h-4 w-4" />
            Discard
          </Button>

          <Button
            variant="default"
            size="sm"
            onClick={handleManualSave}
            disabled={!hasUnsavedChanges || isSaving}
          >
            <Save className="mr-2 h-4 w-4" />
            Save (Ctrl+S)
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <BuilderSidebar />

        {/* Canvas */}
        <div
          className={cn(
            'flex-1 transition-all',
            sidebarOpen && 'ml-80',
            configPanelOpen && 'mr-96'
          )}
        >
          <WorkflowCanvas workflowId={workflowId} />
        </div>

        {/* Configuration Panel */}
        <ConfigurationPanel />
      </div>

      {/* Unsaved Changes Warning Modal */}
      {showUnsavedWarning && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl dark:bg-gray-900">
            <div className="mb-4 flex items-center gap-3">
              <AlertCircle className="h-8 w-8 text-orange-500" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  Unsaved Changes
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  You have unsaved changes. What would you like to do?
                </p>
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <Button
                variant="default"
                onClick={handleConfirmLeave}
                className="w-full"
              >
                Save and Leave
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setShowUnsavedWarning(false);
                  router.push('/workflows');
                }}
                className="w-full"
              >
                Leave Without Saving
              </Button>
              <Button
                variant="ghost"
                onClick={() => setShowUnsavedWarning(false)}
                className="w-full"
              >
                Stay
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
