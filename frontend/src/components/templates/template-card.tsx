'use client';

import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Eye, Star, Users } from 'lucide-react';
import { WorkflowTemplate } from '@/lib/types/workflow';
import Image from 'next/image';
import { cn } from '@/lib/utils';

interface TemplateCardProps {
  template: WorkflowTemplate;
  onSelect: () => void;
  className?: string;
}

export function TemplateCard({ template, onSelect, className }: TemplateCardProps) {
  return (
    <Card
      className={cn(
        'group cursor-pointer transition-all hover:shadow-lg hover:-translate-y-1',
        className
      )}
      onClick={onSelect}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onSelect();
        }
      }}
      aria-label={`Preview ${template.name} template`}
    >
      {/* Preview Image */}
      <div className="relative h-48 bg-muted overflow-hidden">
        {template.preview_image_url ? (
          <Image
            src={template.preview_image_url}
            alt={template.name}
            fill
            className="object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <Eye className="h-12 w-12" />
          </div>
        )}
        {template.featured && (
          <Badge className="absolute top-3 right-3 bg-yellow-500 hover:bg-yellow-600">
            <Star className="h-3 w-3 mr-1" />
            Featured
          </Badge>
        )}
      </div>

      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-semibold line-clamp-1">{template.name}</h3>
        </div>
        <p className="text-sm text-muted-foreground line-clamp-2">
          {template.description}
        </p>
      </CardHeader>

      <CardContent className="pb-3">
        <div className="flex flex-wrap gap-2">
          <Badge variant="outline">{template.category}</Badge>
          {template.required_integrations.slice(0, 2).map((integration) => (
            <Badge key={integration} variant="secondary" className="text-xs">
              {integration}
            </Badge>
          ))}
          {template.required_integrations.length > 2 && (
            <Badge variant="secondary" className="text-xs">
              +{template.required_integrations.length - 2}
            </Badge>
          )}
        </div>
      </CardContent>

      <CardFooter className="flex items-center justify-between pt-3 border-t">
        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <Users className="h-4 w-4" aria-hidden="true" />
            <span>{template.usage_count}</span>
          </div>
          {template.rating > 0 && (
            <div className="flex items-center gap-1">
              <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" aria-hidden="true" />
              <span>{template.rating.toFixed(1)}</span>
            </div>
          )}
        </div>
        <Button variant="ghost" size="sm">
          <Eye className="h-4 w-4 mr-2" />
          Preview
        </Button>
      </CardFooter>
    </Card>
  );
}
