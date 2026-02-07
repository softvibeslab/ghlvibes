// Configuration Panel - Step Configuration

'use client';

import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { useCanvasStore } from '@/lib/stores/canvas-store';
import { useWorkflowStore } from '@/lib/stores/workflow-store';
import {
  getTriggerDefinition,
  getActionDefinition,
  type StepDefinition,
  type ConfigField,
} from '@/lib/constants/step-types';
import { X, Save, Test, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export function ConfigurationPanel() {
  const {
    configPanelOpen,
    toggleConfigPanel,
    selectedNodeId,
    nodes,
    updateNode,
  } = useCanvasStore();
  const { setHasUnsavedChanges } = useWorkflowStore();
  const [isLoading, setIsLoading] = useState(false);
  const [isTesting, setIsTesting] = useState(false);

  const selectedNode = nodes.find((n) => n.id === selectedNodeId);

  // Get step definition based on node data
  const stepDefinition: StepDefinition | undefined = React.useMemo(() => {
    if (!selectedNode) return undefined;

    // Try trigger definitions first
    const triggerDef = getTriggerDefinition(selectedNode.data.config?.type as any);
    if (triggerDef) return triggerDef;

    // Try action definitions
    const actionDef = getActionDefinition(selectedNode.data.config?.type as any);
    if (actionDef) return actionDef;

    return undefined;
  }, [selectedNode]);

  // Build dynamic schema based on config fields
  const schema = React.useMemo(() => {
    if (!stepDefinition) return z.object({});

    const shape: Record<string, z.ZodTypeAny> = {};

    stepDefinition.configFields.forEach((field) => {
      let fieldSchema: z.ZodTypeAny;

      switch (field.type) {
        case 'email':
          fieldSchema = z.string().email();
          break;
        case 'number':
          fieldSchema = z.number();
          if (field.validation?.min !== undefined) {
            fieldSchema = (fieldSchema as z.ZodNumber).min(field.validation.min);
          }
          if (field.validation?.max !== undefined) {
            fieldSchema = (fieldSchema as z.ZodNumber).max(field.validation.max);
          }
          break;
        case 'toggle':
          fieldSchema = z.boolean();
          break;
        case 'multiselect':
        case 'tags':
          fieldSchema = z.array(z.string());
          break;
        default:
          fieldSchema = z.string();
          if (field.validation?.pattern) {
            fieldSchema = (fieldSchema as z.ZodString).regex(
              new RegExp(field.validation.pattern),
              'Invalid format'
            );
          }
          if (field.validation?.min && typeof field.validation.min === 'number') {
            fieldSchema = (fieldSchema as z.ZodString).min(field.validation.min);
          }
          if (field.validation?.max && typeof field.validation.max === 'number') {
            fieldSchema = (fieldSchema as z.ZodString).max(field.validation.max);
          }
      }

      if (!field.required) {
        fieldSchema = fieldSchema.optional();
      }

      shape[field.name] = fieldSchema;
    });

    return z.object(shape);
  }, [stepDefinition]);

  type FormData = z.infer<typeof schema>;

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
    reset,
    setValue,
    watch,
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: selectedNode?.data.config as FormData,
  });

  // Reset form when selected node changes
  useEffect(() => {
    if (selectedNode) {
      reset(selectedNode.data.config as FormData);
    }
  }, [selectedNode, reset]);

  const onSubmit = async (data: FormData) => {
    if (!selectedNodeId) return;

    setIsLoading(true);
    try {
      // Update node with new config
      updateNode(selectedNodeId, {
        data: {
          ...selectedNode?.data,
          config: data,
        },
      });
      setHasUnsavedChanges(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTest = async () => {
    if (!selectedNode) return;

    setIsTesting(true);
    try {
      // Simulate testing the step
      await new Promise((resolve) => setTimeout(resolve, 1500));
      // TODO: Implement actual test API call
      console.log('Testing step:', selectedNode);
    } finally {
      setIsTesting(false);
    }
  };

  const renderField = (field: ConfigField) => {
    const error = errors[field.name];

    switch (field.type) {
      case 'textarea':
        return (
          <div key={field.name} className="space-y-2">
            <Label htmlFor={field.name} className="flex items-center gap-2">
              {field.label}
              {field.required && <span className="text-red-500">*</span>}
            </Label>
            <Textarea
              id={field.name}
              placeholder={field.placeholder}
              {...register(field.name)}
              className={cn(error && 'border-red-500')}
              rows={4}
            />
            {field.helpText && (
              <p className="text-xs text-gray-500">{field.helpText}</p>
            )}
            {error && (
              <p className="text-sm text-red-500">{error.message as string}</p>
            )}
          </div>
        );

      case 'select':
        return (
          <div key={field.name} className="space-y-2">
            <Label htmlFor={field.name} className="flex items-center gap-2">
              {field.label}
              {field.required && <span className="text-red-500">*</span>}
            </Label>
            <Select
              onValueChange={(value) => setValue(field.name, value)}
              defaultValue={watch(field.name) as string}
            >
              <SelectTrigger className={cn(error && 'border-red-500')}>
                <SelectValue placeholder={field.placeholder} />
              </SelectTrigger>
              <SelectContent>
                {field.options?.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {field.helpText && (
              <p className="text-xs text-gray-500">{field.helpText}</p>
            )}
            {error && (
              <p className="text-sm text-red-500">{error.message as string}</p>
            )}
          </div>
        );

      case 'toggle':
        return (
          <div key={field.name} className="flex items-center justify-between">
            <div className="space-y-1">
              <Label htmlFor={field.name} className="flex items-center gap-2">
                {field.label}
                {field.required && <span className="text-red-500">*</span>}
              </Label>
              {field.helpText && (
                <p className="text-xs text-gray-500">{field.helpText}</p>
              )}
            </div>
            <Switch
              id={field.name}
              checked={watch(field.name) as boolean}
              onCheckedChange={(checked) => setValue(field.name, checked)}
            />
          </div>
        );

      case 'number':
        return (
          <div key={field.name} className="space-y-2">
            <Label htmlFor={field.name} className="flex items-center gap-2">
              {field.label}
              {field.required && <span className="text-red-500">*</span>}
            </Label>
            <Input
              id={field.name}
              type="number"
              placeholder={field.placeholder}
              {...register(field.name, { valueAsNumber: true })}
              className={cn(error && 'border-red-500')}
            />
            {field.helpText && (
              <p className="text-xs text-gray-500">{field.helpText}</p>
            )}
            {error && (
              <p className="text-sm text-red-500">{error.message as string}</p>
            )}
          </div>
        );

      case 'date':
        return (
          <div key={field.name} className="space-y-2">
            <Label htmlFor={field.name} className="flex items-center gap-2">
              {field.label}
              {field.required && <span className="text-red-500">*</span>}
            </Label>
            <Input
              id={field.name}
              type="date"
              {...register(field.name)}
              className={cn(error && 'border-red-500')}
            />
            {field.helpText && (
              <p className="text-xs text-gray-500">{field.helpText}</p>
            )}
            {error && (
              <p className="text-sm text-red-500">{error.message as string}</p>
            )}
          </div>
        );

      case 'time':
        return (
          <div key={field.name} className="space-y-2">
            <Label htmlFor={field.name} className="flex items-center gap-2">
              {field.label}
              {field.required && <span className="text-red-500">*</span>}
            </Label>
            <Input
              id={field.name}
              type="time"
              {...register(field.name)}
              className={cn(error && 'border-red-500')}
            />
            {field.helpText && (
              <p className="text-xs text-gray-500">{field.helpText}</p>
            )}
            {error && (
              <p className="text-sm text-red-500">{error.message as string}</p>
            )}
          </div>
        );

      case 'datetime':
        return (
          <div key={field.name} className="space-y-2">
            <Label htmlFor={field.name} className="flex items-center gap-2">
              {field.label}
              {field.required && <span className="text-red-500">*</span>}
            </Label>
            <Input
              id={field.name}
              type="datetime-local"
              {...register(field.name)}
              className={cn(error && 'border-red-500')}
            />
            {field.helpText && (
              <p className="text-xs text-gray-500">{field.helpText}</p>
            )}
            {error && (
              <p className="text-sm text-red-500">{error.message as string}</p>
            )}
          </div>
        );

      default:
        return (
          <div key={field.name} className="space-y-2">
            <Label htmlFor={field.name} className="flex items-center gap-2">
              {field.label}
              {field.required && <span className="text-red-500">*</span>}
            </Label>
            <Input
              id={field.name}
              type={field.type}
              placeholder={field.placeholder}
              {...register(field.name)}
              className={cn(error && 'border-red-500')}
            />
            {field.helpText && (
              <p className="text-xs text-gray-500">{field.helpText}</p>
            )}
            {error && (
              <p className="text-sm text-red-500">{error.message as string}</p>
            )}
          </div>
        );
    }
  };

  if (!configPanelOpen) {
    return null;
  }

  return (
    <div className="fixed right-0 top-0 z-20 h-full w-96 border-l bg-white shadow-xl dark:border-gray-800 dark:bg-gray-900">
      {/* Header */}
      <div className="flex items-center justify-between border-b p-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {stepDefinition?.label || 'Configure Step'}
          </h2>
          <p className="text-sm text-gray-500">
            {selectedNode?.data.type && (
              <span className="capitalize">{selectedNode.data.type}</span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={handleTest}
            disabled={isTesting}
            title="Test Step"
          >
            {isTesting ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Test className="h-4 w-4" />
            )}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleConfigPanel}
            title="Close Panel"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Content */}
      {selectedNode && stepDefinition ? (
        <form onSubmit={handleSubmit(onSubmit)} className="flex h-full flex-col">
          <ScrollArea className="flex-1 p-4">
            <div className="space-y-6">
              {stepDefinition.description && (
                <div className="rounded-lg bg-gray-50 p-3 dark:bg-gray-800">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {stepDefinition.description}
                  </p>
                </div>
              )}

              {stepDefinition.configFields.length > 0 ? (
                stepDefinition.configFields.map((field) => renderField(field))
              ) : (
                <div className="text-center text-sm text-gray-500">
                  No configuration required for this step.
                </div>
              )}
            </div>
          </ScrollArea>

          {/* Footer */}
          <div className="flex items-center justify-between border-t p-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => reset()}
              disabled={!isDirty}
            >
              Reset
            </Button>
            <Button
              type="submit"
              disabled={!isDirty || isLoading}
              className="min-w-[100px]"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Save
                </>
              )}
            </Button>
          </div>
        </form>
      ) : (
        <div className="flex h-full items-center justify-center p-8 text-center">
          <div>
            <p className="text-sm text-gray-500">No step selected</p>
            <p className="mt-2 text-xs text-gray-400">
              Click on a step in the canvas to configure it
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
