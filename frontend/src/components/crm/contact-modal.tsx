'use client';

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ContactForm } from './contact-form';
import { NoteEditor } from './note-editor';
import { ActivityTimeline } from './activity-timeline';
import { TagsManager } from './tags-manager';
import { useQuery } from '@tanstack/react-query';
import { getEntityActivities } from '@/lib/api/crm';
import type { Contact, CreateContactDto, Note } from '@/lib/types/crm';

interface ContactModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  contact?: Contact;
  mode: 'create' | 'edit' | 'view';
  onSave?: (data: CreateContactDto) => void;
  isSaving?: boolean;
}

export function ContactModal({
  open,
  onOpenChange,
  contact,
  mode,
  onSave,
  isSaving = false,
}: ContactModalProps) {
  const { data: activities } = useQuery({
    queryKey: ['contact-activities', contact?.id],
    queryFn: () => getEntityActivities('contact', contact!.id),
    enabled: mode === 'view' && !!contact?.id,
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {mode === 'create'
              ? 'Create Contact'
              : mode === 'edit'
              ? 'Edit Contact'
              : contact?.first_name + ' ' + contact?.last_name}
          </DialogTitle>
          {mode === 'create' && (
            <DialogDescription>
              Add a new contact to your CRM
            </DialogDescription>
          )}
        </DialogHeader>

        {mode === 'view' && contact ? (
          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="notes">Notes</TabsTrigger>
              <TabsTrigger value="activities">Activities</TabsTrigger>
              <TabsTrigger value="tags">Tags</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-4 mt-4">
              {/* Contact details overview */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium">Email</p>
                  <p className="text-sm text-muted-foreground">{contact.email}</p>
                </div>
                {contact.phone && (
                  <div>
                    <p className="text-sm font-medium">Phone</p>
                    <p className="text-sm text-muted-foreground">{contact.phone}</p>
                  </div>
                )}
                <div>
                  <p className="text-sm font-medium">Status</p>
                  <p className="text-sm capitalize">{contact.status}</p>
                </div>
                <div>
                  <p className="text-sm font-medium">Lifecycle Stage</p>
                  <p className="text-sm capitalize">{contact.lifecycle_stage}</p>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="notes" className="mt-4">
              <NoteEditor
                notes={contact.notes || []}
                onAdd={(content) => {
                  // TODO: Implement add note
                }}
                disabled
              />
            </TabsContent>

            <TabsContent value="activities" className="mt-4">
              <ActivityTimeline activities={activities?.items || []} />
            </TabsContent>

            <TabsContent value="tags" className="mt-4">
              <TagsManager
                tags={contact.tags}
                availableTags={[]}
                onUpdate={() => {}}
                disabled
              />
            </TabsContent>
          </Tabs>
        ) : (
          <ContactForm
            initialData={contact}
            onSubmit={(data) => onSave?.(data)}
            isLoading={isSaving}
            submitLabel={mode === 'create' ? 'Create Contact' : 'Save Changes'}
          />
        )}
      </DialogContent>
    </Dialog>
  );
}
