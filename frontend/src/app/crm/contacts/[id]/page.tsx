'use client';

import { use } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Edit, Mail, Phone, MapPin, Calendar } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { ContactStatusBadge } from '@/components/crm/contact-status-badge';
import { ContactLifecycleBadge } from '@/components/crm/contact-lifecycle-badge';
import { NoteEditor } from '@/components/crm/note-editor';
import { ActivityTimeline } from '@/components/crm/activity-timeline';
import { TagsManager } from '@/components/crm/tags-manager';
import { CustomFieldsDisplay } from '@/components/crm/custom-fields-display';
import { getContact, getEntityActivities, getCustomFields } from '@/lib/api/crm';
import Link from 'next/link';
import { format } from 'date-fns';

export default function ContactDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const { data: contact, isLoading } = useQuery({
    queryKey: ['contact', id],
    queryFn: () => getContact(id),
  });

  const { data: activities } = useQuery({
    queryKey: ['contact-activities', id],
    queryFn: () => getEntityActivities('contact', id),
  });

  const { data: customFields } = useQuery({
    queryKey: ['custom-fields', 'contact'],
    queryFn: () => getCustomFields('contact'),
  });

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!contact) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold">Contact not found</h2>
        <Button className="mt-4" asChild>
          <Link href="/crm/contacts">Back to Contacts</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/crm/contacts">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <Avatar className="h-16 w-16">
          <AvatarImage src={contact.avatar_url} />
          <AvatarFallback className="text-xl">
            {contact.first_name[0]}
            {contact.last_name[0]}
          </AvatarFallback>
        </Avatar>
        <div className="flex-1">
          <h1 className="text-3xl font-bold">
            {contact.first_name} {contact.last_name}
          </h1>
          <p className="text-muted-foreground">{contact.email}</p>
        </div>
        <Button>
          <Edit className="mr-2 h-4 w-4" />
          Edit
        </Button>
      </div>

      {/* Status Badges */}
      <div className="flex gap-2">
        <ContactStatusBadge status={contact.status} />
        <ContactLifecycleBadge lifecycle={contact.lifecycle_stage} />
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="activities">Activities</TabsTrigger>
          <TabsTrigger value="notes">Notes</TabsTrigger>
          <TabsTrigger value="tags">Tags</TabsTrigger>
          <TabsTrigger value="deals">Deals</TabsTrigger>
          <TabsTrigger value="tasks">Tasks</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            {/* Contact Information */}
            <Card>
              <CardHeader>
                <CardTitle>Contact Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-3">
                  <Mail className="h-4 w-4 text-muted-foreground" />
                  <a
                    href={`mailto:${contact.email}`}
                    className="text-sm hover:underline"
                  >
                    {contact.email}
                  </a>
                </div>
                {contact.phone && (
                  <div className="flex items-center gap-3">
                    <Phone className="h-4 w-4 text-muted-foreground" />
                    <a
                      href={`tel:${contact.phone}`}
                      className="text-sm hover:underline"
                    >
                      {contact.phone}
                    </a>
                  </div>
                )}
                {contact.mobile && (
                  <div className="flex items-center gap-3">
                    <Phone className="h-4 w-4 text-muted-foreground" />
                    <a
                      href={`tel:${contact.mobile}`}
                      className="text-sm hover:underline"
                    >
                      {contact.mobile}
                    </a>
                  </div>
                )}
                {contact.address && (
                  <div className="flex items-start gap-3">
                    <MapPin className="h-4 w-4 text-muted-foreground mt-0.5" />
                    <div className="text-sm">
                      {contact.address.street && <p>{contact.address.street}</p>}
                      {contact.address.city && contact.address.state && (
                        <p>
                          {contact.address.city}, {contact.address.state}{' '}
                          {contact.address.postal_code}
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Other Details */}
            <Card>
              <CardHeader>
                <CardTitle>Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {contact.date_of_birth && (
                  <div className="flex items-center gap-3">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <div className="text-sm">
                      <p className="text-muted-foreground">Date of Birth</p>
                      <p>{format(new Date(contact.date_of_birth), 'PPP')}</p>
                    </div>
                  </div>
                )}
                {contact.anniversary && (
                  <div className="flex items-center gap-3">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <div className="text-sm">
                      <p className="text-muted-foreground">Anniversary</p>
                      <p>{format(new Date(contact.anniversary), 'PPP')}</p>
                    </div>
                  </div>
                )}
                <div className="text-sm">
                  <p className="text-muted-foreground">Source</p>
                  <p className="capitalize">{contact.source.replace('_', ' ')}</p>
                </div>
                {contact.company_id && (
                  <div className="text-sm">
                    <p className="text-muted-foreground">Company</p>
                    <Badge variant="outline">Company ID: {contact.company_id}</Badge>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Custom Fields */}
          {customFields && customFields.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Custom Fields</CardTitle>
              </CardHeader>
              <CardContent>
                <CustomFieldsDisplay
                  fields={customFields}
                  values={contact.custom_fields}
                />
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="activities">
          <ActivityTimeline activities={activities?.items || []} />
        </TabsContent>

        <TabsContent value="notes">
          <NoteEditor
            notes={[]}
            onAdd={() => {}}
            disabled
          />
        </TabsContent>

        <TabsContent value="tags">
          <Card>
            <CardContent className="pt-6">
              <TagsManager
                tags={contact.tags}
                availableTags={[]}
                onUpdate={() => {}}
                disabled
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="deals">
          <Card>
            <CardContent className="pt-6">
              <p className="text-center text-sm text-muted-foreground">
                {contact.deals_count} deal{contact.deals_count !== 1 ? 's' : ''} associated
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tasks">
          <Card>
            <CardContent className="pt-6">
              <p className="text-center text-sm text-muted-foreground">
                {contact.tasks_count} task{contact.tasks_count !== 1 ? 's' : ''} associated
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
