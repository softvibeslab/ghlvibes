'use client';

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { WorkflowTemplate } from '@/lib/types/workflow';
import { Star, Users, Eye, CheckCircle2, AlertCircle } from 'lucide-react';
import Image from 'next/image';

interface TemplatePreviewModalProps {
  template: WorkflowTemplate;
  open: boolean;
  onClose: () => void;
  onInstantiate: () => void;
  isInstantiating?: boolean;
}

export function TemplatePreviewModal({
  template,
  open,
  onClose,
  onInstantiate,
  isInstantiating = false,
}: TemplatePreviewModalProps) {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <DialogTitle className="text-2xl">{template.name}</DialogTitle>
              <p className="text-muted-foreground mt-2">{template.description}</p>
            </div>
            {template.featured && (
              <Badge className="bg-yellow-500 hover:bg-yellow-600 shrink-0">
                <Star className="h-3 w-3 mr-1" />
                Featured
              </Badge>
            )}
          </div>
        </DialogHeader>

        <ScrollArea className="flex-1 px-6">
          <div className="space-y-6 py-4">
            {/* Preview Image */}
            {template.preview_image_url && (
              <div className="relative h-64 bg-muted rounded-lg overflow-hidden">
                <Image
                  src={template.preview_image_url}
                  alt={template.name}
                  fill
                  className="object-cover"
                />
              </div>
            )}

            {/* Stats */}
            <div className="flex gap-6">
              <div className="flex items-center gap-2">
                <Users className="h-5 w-5 text-muted-foreground" />
                <span className="text-sm">{template.usage_count.toLocaleString()} uses</span>
              </div>
              {template.rating > 0 && (
                <div className="flex items-center gap-2">
                  <Star className="h-5 w-5 fill-yellow-400 text-yellow-400" />
                  <span className="text-sm">{template.rating.toFixed(1)} rating</span>
                </div>
              )}
            </div>

            <Separator />

            {/* Category & Use Case */}
            <div>
              <h3 className="font-semibold mb-2">Category & Use Case</h3>
              <div className="flex gap-2">
                <Badge variant="outline">{template.category}</Badge>
                <Badge variant="secondary">{template.use_case}</Badge>
              </div>
            </div>

            {/* Required Integrations */}
            {template.required_integrations.length > 0 && (
              <>
                <Separator />
                <div>
                  <h3 className="font-semibold mb-2">Required Integrations</h3>
                  <div className="flex flex-wrap gap-2">
                    {template.required_integrations.map((integration) => (
                      <Badge key={integration} variant="outline">
                        {integration}
                      </Badge>
                    ))}
                  </div>
                </div>
              </>
            )}

            {/* Workflow Definition */}
            {template.workflow_definition && (
              <>
                <Separator />
                <div>
                  <h3 className="font-semibold mb-2">Workflow Details</h3>
                  <dl className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <dt className="text-muted-foreground">Trigger:</dt>
                      <dd className="font-medium">
                        {template.workflow_definition.trigger_type || 'None specified'}
                      </dd>
                    </div>
                    {template.workflow_definition.actions && (
                      <div className="flex justify-between">
                        <dt className="text-muted-foreground">Actions:</dt>
                      </div>
                    )}
                    {template.workflow_definition.goals && template.workflow_definition.goals.length > 0 && (
                      <div className="flex justify-between">
                        <dt className="text-muted-foreground">Goals:</dt>
                        <dd className="font-medium">{template.workflow_definition.goals.length} defined</dd>
                      </div>
                    )}
                  </dl>
                </div>
              </>
            )}

            {/* Features */}
            <Separator />
            <div>
              <h3 className="font-semibold mb-2">Features</h3>
              <ul className="space-y-2 text-sm">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-500 shrink-0 mt-0.5" />
                  <span>Automated trigger system</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-500 shrink-0 mt-0.5" />
                  <span>Multi-step action sequences</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-500 shrink-0 mt-0.5" />
                  <span>Goal tracking and measurement</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-500 shrink-0 mt-0.5" />
                  <span>Customizable timing and conditions</span>
                </li>
              </ul>
            </div>
          </div>
        </ScrollArea>

        <DialogFooter className="px-6 pb-6 pt-4 border-t">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={onInstantiate} disabled={isInstantiating}>
            {isInstantiating ? 'Instantiating...' : 'Use This Template'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
