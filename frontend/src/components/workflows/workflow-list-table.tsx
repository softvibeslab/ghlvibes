'use client';

import Link from 'next/link';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Workflow } from '@/lib/types/workflow';
import { WorkflowStatusBadge } from './workflow-status-badge';
import { formatRelativeTime, formatNumber, formatPercentage } from '@/lib/utils';
import { MoreHorizontal, Edit, Trash2, Copy } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface WorkflowListTableProps {
  workflows: Workflow[];
  onEdit?: (id: string) => void;
  onDelete?: (id: string) => void;
  onDuplicate?: (id: string) => void;
}

export function WorkflowListTable({
  workflows,
  onEdit,
  onDelete,
  onDuplicate,
}: WorkflowListTableProps) {
  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Trigger</TableHead>
            <TableHead className="text-right">Active Contacts</TableHead>
            <TableHead className="text-right">Completion Rate</TableHead>
            <TableHead>Last Modified</TableHead>
            <TableHead className="w-[70px]"></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {workflows.map((workflow) => (
            <TableRow key={workflow.id} className="cursor-pointer">
              <TableCell className="font-medium">
                <Link
                  href={`/workflows/${workflow.id}`}
                  className="hover:underline"
                >
                  {workflow.name}
                </Link>
              </TableCell>
              <TableCell>
                <WorkflowStatusBadge status={workflow.status} />
              </TableCell>
              <TableCell>
                <Badge variant="outline">
                  {workflow.trigger_type || 'Not configured'}
                </Badge>
              </TableCell>
              <TableCell className="text-right">
                {formatNumber(workflow.stats.currently_active)}
              </TableCell>
              <TableCell className="text-right">
                {formatPercentage(
                  (workflow.stats.completed / workflow.stats.total_enrolled) * 100 || 0
                )}
              </TableCell>
              <TableCell>
                {formatRelativeTime(workflow.updated_at)}
              </TableCell>
              <TableCell>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="h-8 w-8 p-0">
                      <span className="sr-only">Open menu</span>
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => onEdit?.(workflow.id)}>
                      <Edit className="mr-2 h-4 w-4" />
                      Edit
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => onDuplicate?.(workflow.id)}>
                      <Copy className="mr-2 h-4 w-4" />
                      Duplicate
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      onClick={() => onDelete?.(workflow.id)}
                      className="text-destructive"
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
