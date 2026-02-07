'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Contact } from '@/lib/types/crm';
import { ContactStatusBadge } from './contact-status-badge';
import { ContactLifecycleBadge } from './contact-lifecycle-badge';
import { Mail, Phone, MapPin, Calendar } from 'lucide-react';
import { format } from 'date-fns';
import Link from 'next/link';

interface ContactQuickViewProps {
  contact: Contact;
  onClose?: () => void;
}

export function ContactQuickView({ contact, onClose }: ContactQuickViewProps) {
  return (
    <Card className="w-80">
      <CardContent className="p-6">
        <div className="flex items-start gap-4 mb-4">
          <Avatar className="h-16 w-16">
            <AvatarImage src={contact.avatar_url} />
            <AvatarFallback className="text-xl">
              {contact.first_name[0]}
              {contact.last_name[0]}
            </AvatarFallback>
          </Avatar>

          <div className="flex-1 min-w-0">
            <h3 className="font-semibold truncate">
              {contact.first_name} {contact.last_name}
            </h3>
            <p className="text-sm text-muted-foreground truncate">{contact.email}</p>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mb-4">
          <ContactStatusBadge status={contact.status} />
          <ContactLifecycleBadge lifecycle={contact.lifecycle_stage} />
        </div>

        <div className="space-y-3 mb-4">
          <a
            href={`mailto:${contact.email}`}
            className="flex items-center gap-3 text-sm hover:underline"
          >
            <Mail className="h-4 w-4 text-muted-foreground" />
            <span className="truncate">{contact.email}</span>
          </a>

          {contact.phone && (
            <a
              href={`tel:${contact.phone}`}
              className="flex items-center gap-3 text-sm hover:underline"
            >
              <Phone className="h-4 w-4 text-muted-foreground" />
              <span>{contact.phone}</span>
            </a>
          )}

          {contact.date_of_birth && (
            <div className="flex items-center gap-3 text-sm">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span>Birthday: {format(new Date(contact.date_of_birth), 'MMM d')}</span>
            </div>
          )}

          {contact.company_id && (
            <Badge variant="outline">Company ID: {contact.company_id}</Badge>
          )}
        </div>

        <div className="space-y-2 text-sm text-muted-foreground">
          <div className="flex justify-between">
            <span>Notes:</span>
            <span className="font-medium">{contact.notes_count}</span>
          </div>
          <div className="flex justify-between">
            <span>Tasks:</span>
            <span className="font-medium">{contact.tasks_count}</span>
          </div>
          <div className="flex justify-between">
            <span>Deals:</span>
            <span className="font-medium">{contact.deals_count}</span>
          </div>
        </div>

        <Link href={`/crm/contacts/${contact.id}`} className="block mt-4">
          <Button variant="outline" className="w-full" size="sm">
            View Full Profile
          </Button>
        </Link>
      </CardContent>
    </Card>
  );
}
