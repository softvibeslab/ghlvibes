'use client';

import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Company } from '@/lib/types/crm';
import { formatNumber, formatCurrency } from '@/lib/utils';
import { Building2, Users, DollarSign } from 'lucide-react';
import Link from 'next/link';

interface CompanyCardProps {
  company: Company;
}

export function CompanyCard({ company }: CompanyCardProps) {
  return (
    <Link href={`/crm/companies/${company.id}`}>
      <Card className="transition-all hover:shadow-md cursor-pointer h-full">
        <CardHeader className="pb-3">
          <div className="flex items-start gap-3">
            {company.logo_url ? (
              <img
                src={company.logo_url}
                alt={company.name}
                className="h-12 w-12 rounded"
              />
            ) : (
              <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
                <Building2 className="h-6 w-6 text-primary" />
              </div>
            )}
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold truncate">{company.name}</h3>
              {company.industry && (
                <Badge variant="secondary" className="text-xs mt-1">
                  {company.industry}
                </Badge>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {company.description && (
            <p className="text-sm text-muted-foreground line-clamp-2">
              {company.description}
            </p>
          )}

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-muted-foreground" />
              <span>{formatNumber(company.contacts_count)} contacts</span>
            </div>
            <div className="flex items-center gap-2">
              <DollarSign className="h-4 w-4 text-muted-foreground" />
              <span>{formatNumber(company.deals_count)} deals</span>
            </div>
          </div>

          <div className="pt-3 border-t">
            <p className="text-lg font-bold">
              {formatCurrency(company.total_deal_value)}
            </p>
            <p className="text-xs text-muted-foreground">Total pipeline value</p>
          </div>

          {company.tags && company.tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {company.tags.slice(0, 2).map((tag) => (
                <Badge key={tag} variant="outline" className="text-xs">
                  {tag}
                </Badge>
              ))}
              {company.tags.length > 2 && (
                <Badge variant="outline" className="text-xs">
                  +{company.tags.length - 2}
                </Badge>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}
