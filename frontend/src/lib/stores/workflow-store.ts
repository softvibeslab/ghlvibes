import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Workflow, CreateWorkflowDto, UpdateWorkflowDto } from '@/lib/types/workflow';

interface WorkflowStore {
  // Workflow data
  workflow: Workflow | null;
  isLoading: boolean;
  error: string | null;
  hasUnsavedChanges: boolean;

  // Draft state
  draftWorkflow: Workflow | null;

  // Actions
  setWorkflow: (workflow: Workflow | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setHasUnsavedChanges: (hasChanges: boolean) => void;
  updateWorkflow: (updates: Partial<Workflow>) => void;
  saveDraft: () => void;
  restoreDraft: () => void;
  clearDraft: () => void;
  reset: () => void;
}

const initialState = {
  workflow: null,
  isLoading: false,
  error: null,
  hasUnsavedChanges: false,
  draftWorkflow: null,
};

export const useWorkflowStore = create<WorkflowStore>()(
  persist(
    (set, get) => ({
      ...initialState,

      setWorkflow: (workflow) => set({ workflow, hasUnsavedChanges: false }),

      setLoading: (isLoading) => set({ isLoading }),

      setError: (error) => set({ error }),

      setHasUnsavedChanges: (hasUnsavedChanges) => set({ hasUnsavedChanges }),

      updateWorkflow: (updates) =>
        set((state) => ({
          workflow: state.workflow ? { ...state.workflow, ...updates } : null,
          hasUnsavedChanges: true,
        })),

      saveDraft: () =>
        set((state) => ({
          draftWorkflow: state.workflow,
          hasUnsavedChanges: false,
        })),

      restoreDraft: () =>
        set((state) => ({
          workflow: state.draftWorkflow,
          hasUnsavedChanges: true,
        })),

      clearDraft: () => set({ draftWorkflow: null }),

      reset: () => set(initialState),
    }),
    {
      name: 'workflow-storage',
      partialize: (state) => ({
        draftWorkflow: state.draftWorkflow,
      }),
    }
  )
);
