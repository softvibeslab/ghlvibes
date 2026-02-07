'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { PipelineKanbanBoard } from '@/components/crm/pipeline-kanban-board';
import { DealModal } from '@/components/crm/deal-modal';
import { CRMSkeleton } from '@/components/crm/crm-skeleton';
import { EmptyState } from '@/components/common/empty-state';
import { getPipelines, getPipelineDeals } from '@/lib/api/crm';
import { useDealStore } from '@/lib/stores/deal-store';
import { Plus, Columns } from 'lucide-react';
import type { Deal } from '@/lib/types/crm';

export default function PipelinesPage() {
  const {
    pipelines,
    selectedPipelineId,
    isLoadingPipelines,
    setPipelines,
    setSelectedPipelineId,
    setLoadingPipelines,
    kanbanDeals,
    isLoadingKanban,
    setKanbanDeals,
    setLoadingKanban,
    setKanbanError,
  } = useDealStore();

  const [isDealModalOpen, setIsDealModalOpen] = useState(false);
  const [selectedDealId, setSelectedDealId] = useState<string | undefined>();
  const [dealModalMode, setDealModalMode] = useState<'create' | 'edit' | 'view'>('create');

  // Fetch pipelines
  const { data: pipelinesData, refetch: refetchPipelines } = useQuery({
    queryKey: ['pipelines'],
    queryFn: async () => {
      setLoadingPipelines(true);
      const data = await getPipelines();
      setPipelines(data);
      setLoadingPipelines(false);
      return data;
    },
  });

  // Fetch deals for selected pipeline
  const { data: deals, refetch: refetchDeals } = useQuery({
    queryKey: ['pipeline-deals', selectedPipelineId],
    queryFn: async () => {
      if (!selectedPipelineId) return [];
      setLoadingKanban(true);
      try {
        const data = await getPipelineDeals(selectedPipelineId);

        // Group by stage
        const grouped = data.reduce((acc, deal) => {
          if (!acc[deal.stage_id]) {
            acc[deal.stage_id] = [];
          }
          acc[deal.stage_id].push(deal);
          return acc;
        }, {} as Record<string, Deal[]>);

        setKanbanDeals(grouped);
        setLoadingKanban(false);
        return data;
      } catch (err) {
        setKanbanError(err instanceof Error ? err.message : 'Failed to load deals');
        setLoadingKanban(false);
        return [];
      }
    },
    enabled: !!selectedPipelineId,
  });

  // Set default pipeline
  if (pipelines.length > 0 && !selectedPipelineId) {
    setSelectedPipelineId(pipelines[0].id);
  }

  const handleCreateDeal = () => {
    setSelectedDealId(undefined);
    setDealModalMode('create');
    setIsDealModalOpen(true);
  };

  const handleDealClick = (deal: Deal) => {
    setSelectedDealId(deal.id);
    setDealModalMode('view');
    setIsDealModalOpen(true);
  };

  if (isLoadingPipelines) {
    return <CRMSkeleton />;
  }

  if (pipelines.length === 0) {
    return (
      <EmptyState
        icon={Columns}
        title="No pipelines found"
        description="Create your first pipeline to start managing your deals."
        action={{
          label: 'Create Pipeline',
          onClick: () => {
            // TODO: Implement pipeline creation
          },
        }}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Pipelines</h1>
          <p className="text-muted-foreground">
            Manage your deals and sales pipeline
          </p>
        </div>
        <Button onClick={handleCreateDeal}>
          <Plus className="mr-2 h-4 w-4" />
          Add Deal
        </Button>
      </div>

      {/* Pipeline Selector */}
      <div className="flex items-center gap-4">
        <div className="flex-1 max-w-sm">
          <Select
            value={selectedPipelineId || ''}
            onValueChange={(value) => setSelectedPipelineId(value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select a pipeline" />
            </SelectTrigger>
            <SelectContent>
              {pipelines.map((pipeline) => (
                <SelectItem key={pipeline.id} value={pipeline.id}>
                  {pipeline.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Kanban Board */}
      {selectedPipelineId && deals && deals.length > 0 ? (
        <PipelineKanbanBoard
          deals={deals}
          onDealClick={handleDealClick}
        />
      ) : (
        <EmptyState
          icon={Columns}
          title="No deals in this pipeline"
          description="Add your first deal to get started."
          action={{
            label: 'Add Deal',
            onClick: handleCreateDeal,
          }}
        />
      )}

      {/* Deal Modal */}
      <DealModal
        open={isDealModalOpen}
        onOpenChange={setIsDealModalOpen}
        deal={deals?.find((d) => d.id === selectedDealId)}
        mode={dealModalMode}
        onSave={async () => {
          await refetchDeals();
          await refetchPipelines();
        }}
      />
    </div>
  );
}
