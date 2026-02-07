'use client';

import { useState } from 'react';
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { DealCard } from './deal-card';
import { Deal } from '@/lib/types/crm';
import { useDealStore } from '@/lib/stores/deal-store';

interface PipelineKanbanBoardProps {
  deals: Deal[];
  onDealClick?: (deal: Deal) => void;
}

export function PipelineKanbanBoard({ deals, onDealClick }: PipelineKanbanBoardProps) {
  const { draggedDealId, setDraggedDealId, updateDealStage } = useDealStore();
  const [activeId, setActiveId] = useState<string | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  // Group deals by stage
  const dealsByStage = deals.reduce((acc, deal) => {
    if (!acc[deal.stage_id]) {
      acc[deal.stage_id] = [];
    }
    acc[deal.stage_id].push(deal);
    return acc;
  }, {} as Record<string, Deal[]>);

  const stages = Object.keys(dealsByStage).sort();

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as string);
    setDraggedDealId(event.active.id as string);
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveId(null);
    setDraggedDealId(null);

    if (!over) return;

    const dealId = active.id as string;
    const newStageId = over.id as string;

    if (dealId !== newStageId) {
      // Optimistic update
      updateDealStage(dealId, newStageId);

      // TODO: Call API to update deal stage
      // await updateDealStage(dealId, newStageId);
    }
  };

  const activeDeal = deals.find((d) => d.id === activeId);

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="flex gap-4 overflow-x-auto pb-4">
        {stages.map((stageId) => (
          <KanbanColumn
            key={stageId}
            stageId={stageId}
            deals={dealsByStage[stageId] || []}
            onDealClick={onDealClick}
          />
        ))}
      </div>

      <DragOverlay>
        {activeDeal ? (
          <div className="rotate-3 opacity-80">
            <DealCard deal={activeDeal} />
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  );
}

interface KanbanColumnProps {
  stageId: string;
  deals: Deal[];
  onDealClick?: (deal: Deal) => void;
}

function KanbanColumn({ stageId, deals, onDealClick }: KanbanColumnProps) {
  const totalValue = deals.reduce((sum, deal) => sum + deal.value, 0);

  return (
    <Card className="flex flex-col w-[320px] min-w-[320px] h-full">
      <div className="p-4 border-b">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold">Stage {stageId.slice(0, 8)}</h3>
          <span className="text-sm text-muted-foreground">{deals.length}</span>
        </div>
        <div className="text-sm font-medium">
          ${totalValue.toLocaleString()}
        </div>
      </div>
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-3">
          {deals.map((deal) => (
            <div key={deal.id} data-id={deal.id}>
              <DealCard deal={deal} onClick={() => onDealClick?.(deal)} />
            </div>
          ))}
          {deals.length === 0 && (
            <div className="text-center py-8 text-sm text-muted-foreground">
              No deals
            </div>
          )}
        </div>
      </ScrollArea>
    </Card>
  );
}
