'use client';

import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import type { CustomField } from '@/lib/types/crm';

interface CustomFieldsDisplayProps {
  fields: CustomField[];
  values: Record<string, unknown>;
  onEdit?: () => void;
}

export function CustomFieldsDisplay({
  fields,
  values,
  onEdit,
}: CustomFieldsDisplayProps) {
  if (fields.length === 0) {
    return (
      <div className="text-center py-4 text-sm text-muted-foreground">
        No custom fields defined
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {fields.map((field) => {
        const value = values[field.name];

        if (value === undefined || value === null || value === '') {
          return null;
        }

        return (
          <div key={field.id} className="flex items-start gap-3">
            <div className="flex-1 min-w-0">
              <Label className="text-sm text-muted-foreground">
                {field.name}
              </Label>
              <div className="mt-1">
                <CustomFieldValue field={field} value={value} />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

interface CustomFieldValueProps {
  field: CustomField;
  value: unknown;
}

function CustomFieldValue({ field, value }: CustomFieldValueProps) {
  switch (field.type) {
    case 'text':
    case 'textarea':
      return (
        <p className="text-sm">{String(value)}</p>
      );

    case 'number':
      return (
        <p className="text-sm font-medium">{Number(value).toLocaleString()}</p>
      );

    case 'date':
      return (
        <p className="text-sm">
          {new Date(String(value)).toLocaleDateString()}
        </p>
      );

    case 'checkbox':
      return (
        <Badge variant={value ? 'default' : 'secondary'}>
          {value ? 'Yes' : 'No'}
        </Badge>
      );

    case 'dropdown':
      return (
        <Badge variant="outline">{String(value)}</Badge>
      );

    case 'multiselect':
      return (
        <div className="flex flex-wrap gap-1">
          {(Array.isArray(value) ? value : [value]).map((v, idx) => (
            <Badge key={idx} variant="secondary">
              {String(v)}
            </Badge>
          ))}
        </div>
      );

    default:
      return <p className="text-sm">{String(value)}</p>;
  }
}
