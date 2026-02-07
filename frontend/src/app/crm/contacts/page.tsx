'use client';

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Plus, Search } from 'lucide-react';
import { ContactListTable } from '@/components/crm/contact-list-table';
import { ContactFilters } from '@/components/crm/contact-filters';
import { BulkActionsBar } from '@/components/crm/bulk-actions-bar';
import { PaginationControls } from '@/components/crm/pagination-controls';
import { ContactImportModal } from '@/components/crm/contact-import-modal';
import { ContactModal } from '@/components/crm/contact-modal';
import { CRMSkeleton } from '@/components/crm/crm-skeleton';
import { EmptyState } from '@/components/common/empty-state';
import { getContacts, getContactStats } from '@/lib/api/crm';
import { useContactStore } from '@/lib/stores/crm-store';
import { Users } from 'lucide-react';

export default function ContactsPage() {
  const {
    contacts,
    selectedContacts,
    isLoading,
    error,
    total,
    page,
    pageSize,
    filters,
    setContacts,
    setSelectedContacts,
    setLoading,
    setError,
    setPage,
    setPageSize,
    setFilters,
    clearSelection,
  } = useContactStore();

  const [searchQuery, setSearchQuery] = useState('');
  const [isContactModalOpen, setIsContactModalOpen] = useState(false);
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);
  const [selectedContactId, setSelectedContactId] = useState<string | undefined>();
  const [contactModalMode, setContactModalMode] = useState<'create' | 'edit' | 'view'>('create');

  // Fetch contacts
  const { data: contactsData, refetch } = useQuery({
    queryKey: ['contacts', page, pageSize, filters],
    queryFn: () => getContacts({ ...filters, page, pageSize }),
    onSuccess: (data) => {
      setContacts(data.items, data.total);
    },
    onError: (err) => {
      setError(err.message);
    },
  });

  // Update store when data changes
  useEffect(() => {
    if (contactsData) {
      setContacts(contactsData.items, contactsData.total);
    }
  }, [contactsData, setContacts]);

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    setFilters({ ...filters, search: value || undefined });
  };

  const handleDeleteContacts = async () => {
    // TODO: Implement bulk delete
    console.log('Delete contacts:', Array.from(selectedContacts));
    clearSelection();
  };

  const handleExportContacts = async () => {
    // TODO: Implement export
    console.log('Export contacts:', Array.from(selectedContacts));
  };

  const handleCreateContact = () => {
    setSelectedContactId(undefined);
    setContactModalMode('create');
    setIsContactModalOpen(true);
  };

  const handleEditContact = (id: string) => {
    setSelectedContactId(id);
    setContactModalMode('edit');
    setIsContactModalOpen(true);
  };

  const handleViewContact = (id: string) => {
    setSelectedContactId(id);
    setContactModalMode('view');
    setIsContactModalOpen(true);
  };

  const handleDeleteContact = async (id: string) => {
    // TODO: Implement delete
    console.log('Delete contact:', id);
  };

  if (isLoading) {
    return <CRMSkeleton />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Contacts</h1>
          <p className="text-muted-foreground">
            Manage your contacts and relationships
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setIsImportModalOpen(true)}>
            Import
          </Button>
          <Button onClick={handleCreateContact}>
            <Plus className="mr-2 h-4 w-4" />
            Add Contact
          </Button>
        </div>
      </div>

      {/* Bulk Actions Bar */}
      <BulkActionsBar
        selectedCount={selectedContacts.size}
        onClearSelection={clearSelection}
        onDelete={handleDeleteContacts}
        onExport={handleExportContacts}
      />

      {/* Filters and Search */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search contacts..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <ContactFilters
          filters={filters}
          onFiltersChange={setFilters}
          resultCount={total}
        />
      </div>

      {/* Contacts List */}
      {contacts.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No contacts found"
          description="Get started by adding your first contact or importing from a CSV file."
          action={{
            label: 'Add Contact',
            onClick: handleCreateContact,
          }}
        />
      ) : (
        <>
          <ContactListTable
            contacts={contacts}
            selectedIds={selectedContacts}
            onSelectionChange={setSelectedContacts}
            onEdit={handleEditContact}
            onDelete={handleDeleteContact}
          />

          {/* Pagination */}
          <PaginationControls
            page={page}
            pageSize={pageSize}
            total={total}
            onPageChange={setPage}
            onPageSizeChange={setPageSize}
          />
        </>
      )}

      {/* Modals */}
      <ContactModal
        open={isContactModalOpen}
        onOpenChange={setIsContactModalOpen}
        contact={contacts.find((c) => c.id === selectedContactId)}
        mode={contactModalMode}
        onSave={async () => {
          await refetch();
        }}
      />

      <ContactImportModal
        open={isImportModalOpen}
        onOpenChange={setIsImportModalOpen}
        onImportComplete={refetch}
      />
    </div>
  );
}
