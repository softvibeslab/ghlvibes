'use client';

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { DealForm } from './deal-form';
import { NoteEditor } from './note-editor';
import { ActivityTimeline } from './activity-timeline';
import { useQuery } from '@tanstack/react-query';
import { getEntityActivities, getPipelines } from '@/lib/api/crm';
import type { Deal, CreateDealDto } from '@/lib/types/crm';

interface DealModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  deal?: Deal;
  mode: 'create' | 'edit' | 'view';
  onSave?: (data: CreateDealDto) => void;
  isSaving?: boolean;
}

export function DealModal({
  open,
  onOpenChange,
  deal,
  mode,
  onSave,
  isSaving = false,
}: DealModalProps) {
  const { data: pipelines } = useQuery({
    queryKey: ['pipelines'],
    queryFn: getPipelines,
  });

  const { data: activities } = useQuery({
    queryKey: ['deal-activities', deal?.id],
    queryFn: () => getEntityActivities('deal', deal!.id),
    enabled: mode === 'view' && !!deal?.id,
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {mode === 'create'
              ? 'Create Deal'
              : mode === 'edit'
              ? 'Edit Deal'
              : deal?.title}
          </DialogTitle>
          {mode === 'create' && (
            <DialogDescription>
              Add a new deal to your pipeline
            </DialogDescription>
          )}
        </DialogHeader>

        {mode === 'view' && deal ? (
          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="notes">Notes</TabsTrigger>
              <TabsTrigger value="activities">Activities</TabsTrigger>
              <TabsTrigger value="details">Details</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-4 mt-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium">Value</p>
                  <p className="text-2xl font-bold">
                    ${deal.value.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium">Priority</p>
                  <p className="text-sm capitalize">{deal.priority}</p>
                </div>
                {deal.expected_close_date && (
                  <div>
                    <p className="text-sm font-medium">Expected Close</p>
                    <p className="text-sm">
                      {new Date(deal.expected_close_date).toLocaleDateString()}
                    </p>
                  </div>
                )}
                <div>
                  <p className="text-sm font-medium">Status</p>
                  <p className="text-sm capitalize">{deal.status}</p>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="notes" className="mt-4">
              <NoteEditor notes={[]} onAdd={() => {}} disabled />
            </TabsContent>

            <TabsContent value="activities" className="mt-4">
              <ActivityTimeline activities={activities?.items || []} />
            </TabsContent>

            <TabsContent value="details" className="space-y-4 mt-4">
              {deal.description && (
                <div>
                  <p className="text-sm font-medium">Description</p>
                  <p className="text-sm text-muted-foreground">{deal.description}</p>
                </div>
              )}
            </TabsContent>
          </Tabs>
        ) : (
          <DealForm
            initialData={deal}
            pipelines={pipelines || []}
            onSubmit={(data) => onSave?.(data)}
            isLoading={isSaving}
            submitLabel={mode === 'create' ? 'Create Deal' : 'Save Changes'}
          />
        )}
      </DialogContent>
    </Dialog>
  );
}
