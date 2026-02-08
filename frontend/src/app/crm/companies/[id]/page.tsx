'use client';

import { use } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Building2, Users, DollarSign, Globe, Phone, Mail } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { NoteEditor } from '@/components/crm/note-editor';
import { ActivityTimeline } from '@/components/crm/activity-timeline';
import { CustomFieldsDisplay } from '@/components/crm/custom-fields-display';
import { getCompany, getCompanyContacts, getCompanyDeals, getEntityActivities, getCustomFields } from '@/lib/api/crm';
import { formatCurrency, formatNumber } from '@/lib/utils';
import Link from 'next/link';
import type { Contact, Deal } from '@/lib/types/crm';

export default function CompanyDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const { data: company, isLoading } = useQuery({
    queryKey: ['company', id],
    queryFn: () => getCompany(id),
  });

  const { data: contacts } = useQuery({
    queryKey: ['company-contacts', id],
    queryFn: () => getCompanyContacts(id),
  });

  const { data: deals } = useQuery({
    queryKey: ['company-deals', id],
    queryFn: () => getCompanyDeals(id),
  });

  const { data: activities } = useQuery({
    queryKey: ['company-activities', id],
    queryFn: () => getEntityActivities('company', id),
  });

  const { data: customFields } = useQuery({
    queryKey: ['custom-fields', 'company'],
    queryFn: () => getCustomFields('company'),
  });

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!company) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold">Company not found</h2>
        <Button className="mt-4" asChild>
          <Link href="/crm/companies">Back to Companies</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/crm/companies">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        {company.logo_url && (
          <img
            src={company.logo_url}
            alt={company.name}
            className="h-16 w-16 rounded"
          />
        )}
        <div className="flex-1">
          <h1 className="text-3xl font-bold">{company.name}</h1>
          {company.domain && (
            <p className="text-muted-foreground">{company.domain}</p>
          )}
        </div>
        <Button>Edit</Button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Contacts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-muted-foreground" />
              <span className="text-2xl font-bold">{formatNumber(company.contacts_count)}</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Deals</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <DollarSign className="h-4 w-4 text-muted-foreground" />
              <span className="text-2xl font-bold">{formatNumber(company.deals_count)}</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Value</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(company.total_deal_value)}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Industry</CardTitle>
          </CardHeader>
          <CardContent>
            {company.industry ? (
              <Badge variant="secondary" className="capitalize">
                {company.industry}
              </Badge>
            ) : (
              <span className="text-muted-foreground">—</span>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="contacts">Contacts</TabsTrigger>
          <TabsTrigger value="deals">Deals</TabsTrigger>
          <TabsTrigger value="activities">Activities</TabsTrigger>
          <TabsTrigger value="notes">Notes</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            {/* Company Information */}
            <Card>
              <CardHeader>
                <CardTitle>Company Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {company.website && (
                  <div className="flex items-center gap-3">
                    <Globe className="h-4 w-4 text-muted-foreground" />
                    <a
                      href={company.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm hover:underline"
                    >
                      {company.website}
                    </a>
                  </div>
                )}
                {company.phone && (
                  <div className="flex items-center gap-3">
                    <Phone className="h-4 w-4 text-muted-foreground" />
                    <a
                      href={`tel:${company.phone}`}
                      className="text-sm hover:underline"
                    >
                      {company.phone}
                    </a>
                  </div>
                )}
                {company.email && (
                  <div className="flex items-center gap-3">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <a
                      href={`mailto:${company.email}`}
                      className="text-sm hover:underline"
                    >
                      {company.email}
                    </a>
                  </div>
                )}
                {company.size && (
                  <div className="text-sm">
                    <p className="text-muted-foreground">Company Size</p>
                    <p>{company.size} employees</p>
                  </div>
                )}
                {company.annual_revenue && (
                  <div className="text-sm">
                    <p className="text-muted-foreground">Annual Revenue</p>
                    <p>{formatCurrency(company.annual_revenue)}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Description */}
            {company.description && (
              <Card>
                <CardHeader>
                  <CardTitle>About</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">{company.description}</p>
                </CardContent>
              </Card>
            )}
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
                  values={company.custom_fields}
                />
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="contacts" className="space-y-4">
          {contacts && contacts.items.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2">
              {contacts.items.map((contact: Contact) => (
                <Card key={contact.id}>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                        <span className="text-sm font-medium">
                          {contact.first_name[0]}{contact.last_name[0]}
                        </span>
                      </div>
                      <div>
                        <p className="font-medium">
                          {contact.first_name} {contact.last_name}
                        </p>
                        <p className="text-sm text-muted-foreground">{contact.email}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center text-sm text-muted-foreground">
                No contacts associated with this company
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="deals" className="space-y-4">
          {deals && deals.items.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2">
              {deals.items.map((deal: Deal) => (
                <Card key={deal.id}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <p className="font-medium">{deal.title}</p>
                      <Badge variant="outline">{deal.status}</Badge>
                    </div>
                    <p className="text-2xl font-bold">{formatCurrency(deal.value)}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center text-sm text-muted-foreground">
                No deals associated with this company
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="activities">
          <ActivityTimeline activities={activities?.items || []} />
        </TabsContent>

        <TabsContent value="notes">
          <NoteEditor notes={[]} onAdd={() => {}} disabled />
        </TabsContent>
      </Tabs>
    </div>
  );
}
