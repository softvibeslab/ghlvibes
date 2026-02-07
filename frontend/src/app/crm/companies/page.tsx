'use client';

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Plus, Search, Building2, Users, DollarSign } from 'lucide-react';
import { PaginationControls } from '@/components/crm/pagination-controls';
import { EmptyState } from '@/components/common/empty-state';
import { getCompanies } from '@/lib/api/crm';
import { formatCurrency, formatNumber, formatRelativeTime } from '@/lib/utils';
import Link from 'next/link';
import type { Company } from '@/lib/types/crm';

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [total, setTotal] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch companies
  const { data: companiesData, refetch } = useQuery({
    queryKey: ['companies', page, pageSize, searchQuery],
    queryFn: async () => {
      setIsLoading(true);
      const data = await getCompanies({
        page,
        pageSize,
        search: searchQuery || undefined,
      });
      setCompanies(data.items);
      setTotal(data.total);
      setIsLoading(false);
      return data;
    },
  });

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    setPage(1);
  };

  const handleCreateCompany = () => {
    // TODO: Implement company creation
    console.log('Create company');
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Companies</h1>
          <p className="text-muted-foreground">
            Manage your company accounts and relationships
          </p>
        </div>
        <Button onClick={handleCreateCompany}>
          <Plus className="mr-2 h-4 w-4" />
          Add Company
        </Button>
      </div>

      {/* Search */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search companies..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      {/* Companies List */}
      {companies.length === 0 ? (
        <EmptyState
          icon={Building2}
          title="No companies found"
          description="Get started by adding your first company."
          action={{
            label: 'Add Company',
            onClick: handleCreateCompany,
          }}
        />
      ) : (
        <>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Industry</TableHead>
                  <TableHead>Size</TableHead>
                  <TableHead>Contacts</TableHead>
                  <TableHead>Deals</TableHead>
                  <TableHead>Total Value</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="w-[70px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {companies.map((company) => (
                  <TableRow key={company.id} className="cursor-pointer">
                    <TableCell className="font-medium">
                      <Link
                        href={`/crm/companies/${company.id}`}
                        className="flex items-center gap-3 hover:underline"
                      >
                        {company.logo_url && (
                          <img
                            src={company.logo_url}
                            alt={company.name}
                            className="h-8 w-8 rounded"
                          />
                        )}
                        <span>{company.name}</span>
                      </Link>
                    </TableCell>
                    <TableCell>
                      {company.industry ? (
                        <Badge variant="secondary" className="capitalize">
                          {company.industry}
                        </Badge>
                      ) : (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {company.size || <span className="text-muted-foreground">—</span>}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Users className="h-4 w-4 text-muted-foreground" />
                        <span>{formatNumber(company.contacts_count)}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <DollarSign className="h-4 w-4 text-muted-foreground" />
                        <span>{formatNumber(company.deals_count)}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <span className="font-medium">
                        {formatCurrency(company.total_deal_value)}
                      </span>
                    </TableCell>
                    <TableCell>
                      {formatRelativeTime(company.created_at)}
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm">
                        View
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

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
