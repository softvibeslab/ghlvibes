import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Task, CreateTaskDto, UpdateTaskDto, TaskFilters } from '@/lib/types/crm';

interface TaskStore {
  // Tasks state
  tasks: Task[];
  isLoading: boolean;
  error: string | null;
  total: number;
  page: number;
  pageSize: number;
  filters: TaskFilters;

  // Calendar state
  calendarTasks: Task[];
  isLoadingCalendar: boolean;

  // Single task state
  currentTask: Task | null;
  isTaskLoading: boolean;
  taskError: string | null;

  // Task stats
  overdueCount: number;
  todayCount: number;
  upcomingCount: number;

  // Actions
  setTasks: (tasks: Task[], total: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setPage: (page: number) => void;
  setPageSize: (pageSize: number) => void;
  setFilters: (filters: Partial<TaskFilters>) => void;
  resetFilters: () => void;

  setCalendarTasks: (tasks: Task[]) => void;
  setLoadingCalendar: (loading: boolean) => void;

  setCurrentTask: (task: Task | null) => void;
  setTaskLoading: (loading: boolean) => void;
  setTaskError: (error: string | null) => void;
  updateCurrentTask: (updates: Partial<Task>) => void;
  addTask: (task: Task) => void;
  updateTask: (id: string, updates: Partial<Task>) => void;
  removeTask: (id: string) => void;

  setTaskStats: (overdue: number, today: number, upcoming: number) => void;

  reset: () => void;
  resetTask: () => void;
}

const initialFilters: TaskFilters = {
  page: 1,
  pageSize: 20,
  sortBy: 'due_date',
  sortOrder: 'asc',
};

export const useTaskStore = create<TaskStore>()(
  persist(
    (set, get) => ({
      // Initial state
      tasks: [],
      isLoading: false,
      error: null,
      total: 0,
      page: 1,
      pageSize: 20,
      filters: initialFilters,

      calendarTasks: [],
      isLoadingCalendar: false,

      currentTask: null,
      isTaskLoading: false,
      taskError: null,

      overdueCount: 0,
      todayCount: 0,
      upcomingCount: 0,

      // List actions
      setTasks: (tasks, total) => set({ tasks, total, isLoading: false }),

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

      // Calendar actions
      setCalendarTasks: (calendarTasks) => set({ calendarTasks, isLoadingCalendar: false }),

      setLoadingCalendar: (isLoadingCalendar) => set({ isLoadingCalendar }),

      // Task detail actions
      setCurrentTask: (currentTask) => set({ currentTask }),

      setTaskLoading: (isTaskLoading) => set({ isTaskLoading }),

      setTaskError: (taskError) => set({ taskError }),

      updateCurrentTask: (updates) =>
        set((state) => ({
          currentTask: state.currentTask
            ? { ...state.currentTask, ...updates }
            : null,
        })),

      addTask: (task) =>
        set((state) => ({
          tasks: [task, ...state.tasks],
          total: state.total + 1,
        })),

      updateTask: (id, updates) =>
        set((state) => ({
          tasks: state.tasks.map((t) =>
            t.id === id ? { ...t, ...updates } : t
          ),
          currentTask:
            state.currentTask?.id === id
              ? { ...state.currentTask, ...updates }
              : state.currentTask,
        })),

      removeTask: (id) =>
        set((state) => ({
          tasks: state.tasks.filter((t) => t.id !== id),
          total: state.total - 1,
        })),

      setTaskStats: (overdueCount, todayCount, upcomingCount) =>
        set({ overdueCount, todayCount, upcomingCount }),

      reset: () =>
        set({
          tasks: [],
          isLoading: false,
          error: null,
          total: 0,
          page: 1,
          pageSize: 20,
          filters: initialFilters,
          calendarTasks: [],
          isLoadingCalendar: false,
        }),

      resetTask: () =>
        set({
          currentTask: null,
          isTaskLoading: false,
          taskError: null,
        }),
    }),
    {
      name: 'task-storage',
      partialize: (state) => ({
        filters: state.filters,
        pageSize: state.pageSize,
      }),
    }
  )
);
