import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Contact, CreateContactDto, UpdateContactDto, ContactFilters } from '@/lib/types/crm';

interface ContactStore {
  // Contact list state
  contacts: Contact[];
  selectedContacts: Set<string>;
  isLoading: boolean;
  error: string | null;
  total: number;
  page: number;
  pageSize: number;
  filters: ContactFilters;

  // Single contact state
  currentContact: Contact | null;
  isContactLoading: boolean;
  contactError: string | null;

  // Actions
  setContacts: (contacts: Contact[], total: number) => void;
  setSelectedContacts: (ids: string[]) => void;
  toggleContactSelection: (id: string) => void;
  clearSelection: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setPage: (page: number) => void;
  setPageSize: (pageSize: number) => void;
  setFilters: (filters: Partial<ContactFilters>) => void;
  resetFilters: () => void;

  // Contact detail actions
  setCurrentContact: (contact: Contact | null) => void;
  setContactLoading: (loading: boolean) => void;
  setContactError: (error: string | null) => void;
  updateCurrentContact: (updates: Partial<Contact>) => void;
  addContact: (contact: Contact) => void;
  removeContact: (id: string) => void;

  // Reset
  reset: () => void;
  resetContact: () => void;
}

const initialFilters: ContactFilters = {
  page: 1,
  pageSize: 20,
  sortBy: 'updated_at',
  sortOrder: 'desc',
};

export const useContactStore = create<ContactStore>()(
  persist(
    (set, get) => ({
      // Initial state
      contacts: [],
      selectedContacts: new Set(),
      isLoading: false,
      error: null,
      total: 0,
      page: 1,
      pageSize: 20,
      filters: initialFilters,

      currentContact: null,
      isContactLoading: false,
      contactError: null,

      // List actions
      setContacts: (contacts, total) =>
        set({ contacts, total, isLoading: false }),

      setSelectedContacts: (ids) =>
        set({ selectedContacts: new Set(ids) }),

      toggleContactSelection: (id) => {
        const selectedContacts = new Set(get().selectedContacts);
        if (selectedContacts.has(id)) {
          selectedContacts.delete(id);
        } else {
          selectedContacts.add(id);
        }
        set({ selectedContacts });
      },

      clearSelection: () => set({ selectedContacts: new Set() }),

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
          selectedContacts: new Set(),
        }),

      // Contact detail actions
      setCurrentContact: (currentContact) => set({ currentContact }),

      setContactLoading: (isContactLoading) => set({ isContactLoading }),

      setContactError: (contactError) => set({ contactError }),

      updateCurrentContact: (updates) =>
        set((state) => ({
          currentContact: state.currentContact
            ? { ...state.currentContact, ...updates }
            : null,
        })),

      addContact: (contact) =>
        set((state) => ({
          contacts: [contact, ...state.contacts],
          total: state.total + 1,
        })),

      removeContact: (id) =>
        set((state) => ({
          contacts: state.contacts.filter((c) => c.id !== id),
          total: state.total - 1,
        })),

      reset: () =>
        set({
          contacts: [],
          selectedContacts: new Set(),
          isLoading: false,
          error: null,
          total: 0,
          page: 1,
          pageSize: 20,
          filters: initialFilters,
        }),

      resetContact: () =>
        set({
          currentContact: null,
          isContactLoading: false,
          contactError: null,
        }),
    }),
    {
      name: 'contact-storage',
      partialize: (state) => ({
        filters: state.filters,
        pageSize: state.pageSize,
      }),
    }
  )
);
