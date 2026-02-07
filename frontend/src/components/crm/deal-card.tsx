'use client';

import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Deal } from '@/lib/types/crm';
import { DealPriorityBadge } from './deal-priority-badge';
import { formatCurrency, formatRelativeTime } from '@/lib/utils';
import { Building2, Calendar, Users } from 'lucide-react';

interface DealCardProps {
  deal: Deal;
  onClick?: () => void;
}

export function DealCard({ deal, onClick }: DealCardProps) {
  return (
    <Card
      className="cursor-pointer transition-all hover:shadow-md"
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1">
            <h3 className="font-semibold truncate">{deal.title}</h3>
            {deal.company_id && (
              <div className="flex items-center gap-1 mt-1 text-sm text-muted-foreground">
                <Building2 className="h-3 w-3" />
                <span className="truncate">Company</span>
              </div>
            )}
          </div>
          <DealPriorityBadge priority={deal.priority} />
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-2xl font-bold">
            {formatCurrency(deal.value)}
          </span>
          {deal.probability && (
            <Badge variant="outline">{deal.probability}%</Badge>
          )}
        </div>

        {deal.expected_close_date && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar className="h-4 w-4" />
            <span>{formatRelativeTime(deal.expected_close_date)}</span>
          </div>
        )}

        {deal.contacts && deal.contacts.length > 0 && (
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-muted-foreground" />
            <div className="flex -space-x-2">
              {deal.contacts.slice(0, 3).map((contact) => (
                <Avatar key={contact.id} className="h-6 w-6 border-2 border-background">
                  <AvatarImage src={contact.avatar_url} />
                  <AvatarFallback className="text-xs">
                    {contact.first_name[0]}
                    {contact.last_name[0]}
                  </AvatarFallback>
                </Avatar>
              ))}
            </div>
            {deal.contacts.length > 3 && (
              <span className="text-xs text-muted-foreground">
                +{deal.contacts.length - 3}
              </span>
            )}
          </div>
        )}

        {deal.tags && deal.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {deal.tags.slice(0, 2).map((tag) => (
              <Badge key={tag} variant="secondary" className="text-xs">
                {tag}
              </Badge>
            ))}
            {deal.tags.length > 2 && (
              <Badge variant="secondary" className="text-xs">
                +{deal.tags.length - 2}
              </Badge>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
