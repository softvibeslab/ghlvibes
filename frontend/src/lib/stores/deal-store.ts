import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Deal, CreateDealDto, UpdateDealDto, DealFilters, Pipeline } from '@/lib/types/crm';

interface DealStore {
  // Pipeline state
  pipelines: Pipeline[];
  selectedPipelineId: string | null;
  isLoadingPipelines: boolean;

  // Deals list state
  deals: Deal[];
  isLoading: boolean;
  error: string | null;
  total: number;
  page: number;
  pageSize: number;
  filters: DealFilters;

  // Kanban state
  kanbanDeals: Record<string, Deal[]>;
  isLoadingKanban: boolean;
  kanbanError: string | null;

  // Single deal state
  currentDeal: Deal | null;
  isDealLoading: boolean;
  dealError: string | null;

  // Drag and drop state
  draggedDealId: string | null;

  // Actions
  setPipelines: (pipelines: Pipeline[]) => void;
  setSelectedPipelineId: (pipelineId: string | null) => void;
  setLoadingPipelines: (loading: boolean) => void;

  setDeals: (deals: Deal[], total: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setPage: (page: number) => void;
  setPageSize: (pageSize: number) => void;
  setFilters: (filters: Partial<DealFilters>) => void;
  resetFilters: () => void;

  setKanbanDeals: (deals: Record<string, Deal[]>) => void;
  setLoadingKanban: (loading: boolean) => void;
  setKanbanError: (error: string | null) => void;
  updateDealStage: (dealId: string, newStageId: string) => void;

  setCurrentDeal: (deal: Deal | null) => void;
  setDealLoading: (loading: boolean) => void;
  setDealError: (error: string | null) => void;
  updateCurrentDeal: (updates: Partial<Deal>) => void;
  addDeal: (deal: Deal) => void;
  removeDeal: (id: string) => void;

  setDraggedDealId: (dealId: string | null) => void;

  reset: () => void;
  resetDeal: () => void;
}

const initialFilters: DealFilters = {
  page: 1,
  pageSize: 20,
  sortBy: 'updated_at',
  sortOrder: 'desc',
};

export const useDealStore = create<DealStore>()(
  persist(
    (set, get) => ({
      // Initial state
      pipelines: [],
      selectedPipelineId: null,
      isLoadingPipelines: false,

      deals: [],
      isLoading: false,
      error: null,
      total: 0,
      page: 1,
      pageSize: 20,
      filters: initialFilters,

      kanbanDeals: {},
      isLoadingKanban: false,
      kanbanError: null,

      currentDeal: null,
      isDealLoading: false,
      dealError: null,

      draggedDealId: null,

      // Pipeline actions
      setPipelines: (pipelines) => set({ pipelines }),

      setSelectedPipelineId: (pipelineId) =>
        set({
          selectedPipelineId: pipelineId,
          filters: { ...get().filters, pipeline_id: pipelineId || undefined },
        }),

      setLoadingPipelines: (isLoadingPipelines) => set({ isLoadingPipelines }),

      // List actions
      setDeals: (deals, total) => set({ deals, total, isLoading: false }),

      setLoading: (isLoading) => set({ isLoading }),

      setError: (error) => set({ error, isLoading: false }),

      setPage: (page) => set({ page }),

      setPageSize: (pageSize) => set({ pageSize, page: 1 }),

      setFilters: (newFilters) =>
        set((state) => ({
          filters: { ...state.filters, ...newFilters },
          page: 1,
        })),

      resetFilters: () =>
        set({
          filters: initialFilters,
          page: 1,
        }),

      // Kanban actions
      setKanbanDeals: (kanbanDeals) => set({ kanbanDeals, isLoadingKanban: false }),

      setLoadingKanban: (isLoadingKanban) => set({ isLoadingKanban }),

      setKanbanError: (kanbanError) => set({ kanbanError, isLoadingKanban: false }),

      updateDealStage: (dealId, newStageId) =>
        set((state) => {
          const updatedKanban = { ...state.kanbanDeals };
          let dealToUpdate: Deal | null = null;

          // Find and remove deal from current stage
          for (const stageId in updatedKanban) {
            const stageDeals = updatedKanban[stageId];
            const dealIndex = stageDeals.findIndex((d) => d.id === dealId);
            if (dealIndex !== -1) {
              dealToUpdate = stageDeals[dealIndex];
              updatedKanban[stageId] = stageDeals.filter((d) => d.id !== dealId);
              break;
            }
          }

          // Add deal to new stage
          if (dealToUpdate) {
            const updatedDeal = { ...dealToUpdate, stage_id: newStageId };
            updatedKanban[newStageId] = [updatedDeal, ...(updatedKanban[newStageId] || [])];
          }

          return { kanbanDeals: updatedKanban };
        }),

      // Deal detail actions
      setCurrentDeal: (currentDeal) => set({ currentDeal }),

      setDealLoading: (isDealLoading) => set({ isDealLoading }),

      setDealError: (dealError) => set({ dealError }),

      updateCurrentDeal: (updates) =>
        set((state) => ({
          currentDeal: state.currentDeal
            ? { ...state.currentDeal, ...updates }
            : null,
        })),

      addDeal: (deal) =>
        set((state) => ({
          deals: [deal, ...state.deals],
          total: state.total + 1,
        })),

      removeDeal: (id) =>
        set((state) => ({
          deals: state.deals.filter((d) => d.id !== id),
          total: state.total - 1,
        })),

      // Drag and drop actions
      setDraggedDealId: (draggedDealId) => set({ draggedDealId }),

      reset: () =>
        set({
          deals: [],
          isLoading: false,
          error: null,
          total: 0,
          page: 1,
          pageSize: 20,
          filters: initialFilters,
          kanbanDeals: {},
          isLoadingKanban: false,
          kanbanError: null,
        }),

      resetDeal: () =>
        set({
          currentDeal: null,
          isDealLoading: false,
          dealError: null,
        }),
    }),
    {
      name: 'deal-storage',
      partialize: (state) => ({
        selectedPipelineId: state.selectedPipelineId,
        filters: state.filters,
        pageSize: state.pageSize,
      }),
    }
  )
);
