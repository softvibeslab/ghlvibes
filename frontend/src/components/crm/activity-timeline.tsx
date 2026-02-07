'use client';

import { Activity } from '@/lib/types/crm';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { formatRelativeTime } from '@/lib/utils';
import { Mail, Phone, MessageSquare, FileText, Calendar, CheckCircle } from 'lucide-react';

interface ActivityTimelineProps {
  activities: Activity[];
}

const activityIcons = {
  email: Mail,
  call: Phone,
  sms: MessageSquare,
  meeting: Calendar,
  note: FileText,
  task_completed: CheckCircle,
  default: FileText,
};

const activityColors = {
  email: 'bg-blue-500',
  call: 'bg-green-500',
  sms: 'bg-purple-500',
  meeting: 'bg-yellow-500',
  note: 'bg-gray-500',
  task_completed: 'bg-emerald-500',
  default: 'bg-gray-500',
};

export function ActivityTimeline({ activities }: ActivityTimelineProps) {
  if (activities.length === 0) {
    return (
      <Card className="p-8 text-center">
        <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
        <h3 className="text-lg font-semibold mb-2">No activities yet</h3>
        <p className="text-sm text-muted-foreground">
          Activities will appear here as you interact with this record.
        </p>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {activities.map((activity, idx) => {
        const Icon = activityIcons[activity.type as keyof typeof activityIcons] || activityIcons.default;
        const colorClass = activityColors[activity.type as keyof typeof activityColors] || activityColors.default;

        return (
          <div key={activity.id} className="flex gap-4">
            <div className="flex flex-col items-center">
              <div className={`h-10 w-10 rounded-full ${colorClass} flex items-center justify-center`}>
                <Icon className="h-5 w-5 text-white" />
              </div>
              {idx < activities.length - 1 && (
                <div className="w-0.5 flex-1 bg-border mt-2" />
              )}
            </div>

            <Card className="flex-1 p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-semibold">{activity.title}</h4>
                    <Badge variant="outline" className="capitalize">
                      {activity.type.replace('_', ' ')}
                    </Badge>
                    {activity.direction && (
                      <Badge variant="secondary" className="capitalize">
                        {activity.direction}
                      </Badge>
                    )}
                  </div>

                  {activity.description && (
                    <p className="text-sm text-muted-foreground mb-2">
                      {activity.description}
                    </p>
                  )}

                  {activity.duration_minutes && (
                    <p className="text-sm text-muted-foreground">
                      Duration: {activity.duration_minutes} minutes
                    </p>
                  )}
                </div>

                <div className="flex flex-col items-end gap-2">
                  <span className="text-xs text-muted-foreground">
                    {formatRelativeTime(activity.created_at)}
                  </span>

                  {activity.created_by && (
                    <Avatar className="h-6 w-6">
                      <AvatarImage src="" />
                      <AvatarFallback className="text-xs">
                        {activity.created_by[0]}
                      </AvatarFallback>
                    </Avatar>
                  )}
                </div>
              </div>

              {activity.attachments && activity.attachments.length > 0 && (
                <div className="mt-3 pt-3 border-t">
                  <p className="text-xs font-medium mb-2">Attachments</p>
                  <div className="flex gap-2">
                    {activity.attachments.map((attachment) => (
                      <Badge key={attachment.id} variant="secondary">
                        {attachment.file_name}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </Card>
          </div>
        );
      })}
    </div>
  );
}
