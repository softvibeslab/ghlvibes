'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Search, Star, Filter } from 'lucide-react';
import { WorkflowTemplate } from '@/lib/types/workflow';
import { TemplateCard } from './template-card';
import { TemplatePreviewModal } from './template-preview-modal';

interface TemplateGalleryProps {
  templates: WorkflowTemplate[];
  onInstantiate: (templateId: string) => Promise<void>;
  isLoading?: boolean;
  className?: string;
}

interface Filters {
  category: string;
  search: string;
  featured: boolean;
}

const CATEGORIES = [
  'All',
  'Lead Nurturing',
  'Sales',
  'Onboarding',
  'Customer Retention',
  'Appointment Scheduling',
  'Follow-up',
  'Marketing',
];

export function TemplateGallery({
  templates,
  onInstantiate,
  isLoading,
  className,
}: TemplateGalleryProps) {
  const [filters, setFilters] = useState<Filters>({
    category: 'All',
    search: '',
    featured: false,
  });
  const [selectedTemplate, setSelectedTemplate] = useState<WorkflowTemplate | null>(null);
  const [instantiating, setInstantiating] = useState<string | null>(null);

  const filteredTemplates = templates.filter((template) => {
    const matchesCategory = filters.category === 'All' || template.category === filters.category;
    const matchesSearch =
      !filters.search ||
      template.name.toLowerCase().includes(filters.search.toLowerCase()) ||
      template.description.toLowerCase().includes(filters.search.toLowerCase());
    const matchesFeatured = !filters.featured || template.featured;
    return matchesCategory && matchesSearch && matchesFeatured;
  });

  const handleInstantiate = async (templateId: string) => {
    setInstantiating(templateId);
    try {
      await onInstantiate(templateId);
      setSelectedTemplate(null);
    } catch (error) {
      console.error('Failed to instantiate template:', error);
    } finally {
      setInstantiating(null);
    }
  };

  return (
    <div className={className}>
      {/* Filters */}
      <div className="flex flex-col gap-4 mb-6">
        <div className="flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search templates..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="pl-9"
              aria-label="Search templates"
            />
          </div>
          <Select
            value={filters.category}
            onValueChange={(value) => setFilters({ ...filters, category: value })}
          >
            <SelectTrigger className="w-[200px]" aria-label="Filter by category">
              <SelectValue placeholder="Category" />
            </SelectTrigger>
            <SelectContent>
              {CATEGORIES.map((category) => (
                <SelectItem key={category} value={category}>
                  {category}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button
            variant={filters.featured ? 'default' : 'outline'}
            onClick={() => setFilters({ ...filters, featured: !filters.featured })}
            aria-label="Toggle featured filter"
          >
            <Star className="h-4 w-4 mr-2" />
            Featured
          </Button>
        </div>
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            {filteredTemplates.length} template{filteredTemplates.length !== 1 ? 's' : ''} found
          </p>
        </div>
      </div>

      {/* Template Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="h-[320px]">
              <CardContent className="p-6">
                <div className="animate-pulse space-y-3">
                  <div className="h-4 bg-muted rounded w-3/4" />
                  <div className="h-3 bg-muted rounded w-full" />
                  <div className="h-3 bg-muted rounded w-1/2" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : filteredTemplates.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <Filter className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-lg font-medium">No templates found</p>
            <p className="text-sm text-muted-foreground">Try adjusting your filters</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTemplates.map((template) => (
            <TemplateCard
              key={template.id}
              template={template}
              onSelect={() => setSelectedTemplate(template)}
            />
          ))}
        </div>
      )}

      {/* Preview Modal */}
      {selectedTemplate && (
        <TemplatePreviewModal
          template={selectedTemplate}
          open={!!selectedTemplate}
          onClose={() => setSelectedTemplate(null)}
          onInstantiate={() => handleInstantiate(selectedTemplate.id)}
          isInstantiating={instantiating === selectedTemplate.id}
        />
      )}
    </div>
  );
}
