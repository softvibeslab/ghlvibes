'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { ActivityTimeline } from '@/components/crm/activity-timeline';
import { PaginationControls } from '@/components/crm/pagination-controls';
import { getActivities } from '@/lib/api/crm';
import { Search, Filter } from 'lucide-react';
import type { ActivityType } from '@/lib/types/crm';

export default function ActivitiesPage() {
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState<ActivityType | undefined>();

  const { data: activitiesData, isLoading } = useQuery({
    queryKey: ['activities', page, pageSize, searchQuery, selectedType],
    queryFn: () =>
      getActivities({
        page,
        pageSize,
        search: searchQuery || undefined,
        type: selectedType,
      }),
  });

  const activities = activitiesData?.items || [];
  const total = activitiesData?.total || 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Activities</h1>
        <p className="text-muted-foreground">
          Track all your customer interactions and communications
        </p>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search activities..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select
          value={selectedType}
          onValueChange={(value) =>
            setSelectedType(value === 'all' ? undefined : (value as ActivityType))
          }
        >
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Filter by type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="call">Calls</SelectItem>
            <SelectItem value="email">Emails</SelectItem>
            <SelectItem value="sms">SMS</SelectItem>
            <SelectItem value="meeting">Meetings</SelectItem>
            <SelectItem value="note">Notes</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Activities Timeline */}
      {isLoading ? (
        <Card>
          <CardContent className="p-8">Loading...</CardContent>
        </Card>
      ) : activities.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <Filter className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No activities found</h3>
            <p className="text-sm text-muted-foreground">
              {searchQuery || selectedType
                ? 'Try adjusting your filters'
                : 'Activities will appear here as you interact with contacts'}
            </p>
          </CardContent>
        </Card>
      ) : (
        <>
          <ActivityTimeline activities={activities} />

          {/* Pagination */}
          <PaginationControls
            page={page}
            pageSize={pageSize}
            total={total}
            onPageChange={setPage}
            onPageSizeChange={() => {}}
          />
        </>
      )}
    </div>
  );
}
