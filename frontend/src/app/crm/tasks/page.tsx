'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { TaskCard } from '@/components/crm/task-card';
import { TaskModal } from '@/components/crm/task-modal';
import { BulkActionsBar } from '@/components/crm/bulk-actions-bar';
import { PaginationControls } from '@/components/crm/pagination-controls';
import { EmptyState } from '@/components/common/empty-state';
import { getTasks, getTodayTasks, getOverdueTasks } from '@/lib/api/crm';
import { useTaskStore } from '@/lib/stores/task-store';
import { CheckCircle, Clock, AlertCircle, Plus, Search, Calendar } from 'lucide-react';
import { format } from 'date-fns';

export default function TasksPage() {
  const {
    tasks,
    selectedTaskId,
    isLoading,
    page,
    pageSize,
    filters,
    setTasks,
    setLoading,
    setPage,
    setPageSize,
    setFilters,
  } = useTaskStore();

  const [searchQuery, setSearchQuery] = useState('');
  const [isTaskModalOpen, setIsTaskModalOpen] = useState(false);
  const [selectedTaskId, setSelectedTaskId] = useState<string | undefined>();
  const [taskModalMode, setTaskModalMode] = useState<'create' | 'edit'>('create');

  // Fetch all tasks
  const { data: tasksData, refetch } = useQuery({
    queryKey: ['tasks', page, pageSize, filters],
    queryFn: async () => {
      setLoading(true);
      const data = await getTasks({ page, pageSize, ...filters });
      setTasks(data.items, data.total);
      setLoading(false);
      return data;
    },
  });

  // Fetch today's tasks
  const { data: todayTasks } = useQuery({
    queryKey: ['today-tasks'],
    queryFn: getTodayTasks,
  });

  // Fetch overdue tasks
  const { data: overdueTasks } = useQuery({
    queryKey: ['overdue-tasks'],
    queryFn: getOverdueTasks,
  });

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    setFilters({ ...filters, search: value || undefined });
  };

  const handleCompleteTask = async (id: string) => {
    // TODO: Implement complete task
    await refetch();
  };

  const handleCreateTask = () => {
    setSelectedTaskId(undefined);
    setTaskModalMode('create');
    setIsTaskModalOpen(true);
  };

  const handleEditTask = (id: string) => {
    setSelectedTaskId(id);
    setTaskModalMode('edit');
    setIsTaskModalOpen(true);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Tasks</h1>
          <p className="text-muted-foreground">
            Manage your tasks and reminders
          </p>
        </div>
        <Button onClick={handleCreateTask}>
          <Plus className="mr-2 h-4 w-4" />
          Add Task
        </Button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Today's Tasks</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{todayTasks?.length || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {format(new Date(), 'PPP')}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Overdue</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">
              {overdueTasks?.length || 0}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Need attention</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {tasks.filter((t) => t.status === 'completed').length}
            </div>
            <p className="text-xs text-muted-foreground mt-1">This week</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Tasks</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{tasks.length}</div>
            <p className="text-xs text-muted-foreground mt-1">All tasks</p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="all" className="w-full">
        <div className="flex items-center justify-between mb-4">
          <TabsList>
            <TabsTrigger value="all">All Tasks</TabsTrigger>
            <TabsTrigger value="today">Today</TabsTrigger>
            <TabsTrigger value="overdue">Overdue</TabsTrigger>
            <TabsTrigger value="upcoming">Upcoming</TabsTrigger>
            <TabsTrigger value="completed">Completed</TabsTrigger>
          </TabsList>

          <div className="relative max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search tasks..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="pl-9"
            />
          </div>
        </div>

        <TabsContent value="all" className="space-y-4">
          {tasks.length === 0 ? (
            <EmptyState
              icon={CheckCircle}
              title="No tasks found"
              description="Create your first task to get started."
              action={{
                label: 'Add Task',
                onClick: handleCreateTask,
              }}
            />
          ) : (
            <>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {tasks.map((task) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    onComplete={handleCompleteTask}
                    onClick={() => handleEditTask(task.id)}
                  />
                ))}
              </div>

              <PaginationControls
                page={page}
                pageSize={pageSize}
                total={tasks.length}
                onPageChange={setPage}
                onPageSizeChange={setPageSize}
              />
            </>
          )}
        </TabsContent>

        <TabsContent value="today" className="space-y-4">
          {todayTasks && todayTasks.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {todayTasks.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onComplete={handleCompleteTask}
                  onClick={() => handleEditTask(task.id)}
                />
              ))}
            </div>
          ) : (
            <EmptyState
              icon={Calendar}
              title="No tasks for today"
              description="You're all caught up!"
            />
          )}
        </TabsContent>

        <TabsContent value="overdue" className="space-y-4">
          {overdueTasks && overdueTasks.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {overdueTasks.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onComplete={handleCompleteTask}
                  onClick={() => handleEditTask(task.id)}
                />
              ))}
            </div>
          ) : (
            <EmptyState
              icon={CheckCircle}
              title="No overdue tasks"
              description="Great job staying on top of things!"
            />
          )}
        </TabsContent>

        <TabsContent value="upcoming" className="space-y-4">
          <EmptyState
            icon={Clock}
            title="Upcoming tasks"
            description="Tasks scheduled for the future will appear here."
          />
        </TabsContent>

        <TabsContent value="completed" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {tasks
              .filter((t) => t.status === 'completed')
              .map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onClick={() => handleEditTask(task.id)}
                />
              ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Task Modal */}
      <TaskModal
        open={isTaskModalOpen}
        onOpenChange={setIsTaskModalOpen}
        task={tasks.find((t) => t.id === selectedTaskId)}
        mode={taskModalMode}
        onSave={async () => {
          await refetch();
        }}
      />
    </div>
  );
}
