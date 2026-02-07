'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Download, FileSpreadsheet, FileCode, FileText } from 'lucide-react';
import { WorkflowAnalytics } from '@/lib/types/workflow';

interface ExportButtonProps {
  data: WorkflowAnalytics;
  filename?: string;
  className?: string;
}

export function ExportButton({ data, filename = 'analytics-export', className }: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);

  const exportToCSV = () => {
    setIsExporting(true);

    try {
      const rows = [
        ['Workflow Analytics Report'],
        [`Date Range: ${data.date_range.start} to ${data.date_range.end}`],
        [],
        ['Overview Metrics'],
        ['Total Enrolled', data.overview.total_enrolled],
        ['Currently Active', data.overview.currently_active],
        ['Completed', data.overview.completed],
        ['Drop-off Rate', `${data.overview.drop_off_rate}%`],
        ['Avg Completion Time (min)', data.overview.avg_completion_time],
        ['Goal Achievement Rate', `${data.overview.goal_achievement_rate}%`],
        [],
        ['Funnel Steps'],
        ['Step Name', 'Entered', 'Completed', 'Drop-offs', 'Drop-off Rate'],
        ...data.funnel.map(
          (step) => [
            step.step_name,
            step.contacts_entered,
            step.contacts_completed,
            step.drop_off_count,
            `${step.drop_off_rate}%`,
          ],
          []
        ),
        [],
        ['Enrollments Over Time'],
        ['Date', 'Count'],
        ...data.enrollments_over_time.map((point) => [point.date, point.count]),
      ];

      const csvContent = rows.map((row) => row.join(',')).join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `${filename}.csv`;
      link.click();
      URL.revokeObjectURL(link.href);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const exportToJSON = () => {
    setIsExporting(true);

    try {
      const jsonContent = JSON.stringify(data, null, 2);
      const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `${filename}.json`;
      link.click();
      URL.revokeObjectURL(link.href);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const exportToPDF = async () => {
    setIsExporting(true);

    try {
      // Simple text-based PDF export using window.print()
      // In production, you'd use jsPDF or react-pdf
      const printWindow = window.open('', '_blank');
      if (printWindow) {
        printWindow.document.write(`
          <html>
            <head>
              <title>Analytics Report - ${filename}</title>
              <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                h1 { color: #333; }
                h2 { color: #666; margin-top: 20px; }
                table { border-collapse: collapse; width: 100%; margin-top: 10px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .metric { margin: 10px 0; }
              </style>
            </head>
            <body>
              <h1>Workflow Analytics Report</h1>
              <p><strong>Date Range:</strong> ${data.date_range.start} to ${data.date_range.end}</p>

              <h2>Overview</h2>
              <div class="metric"><p>Total Enrolled: ${data.overview.total_enrolled}</p></div>
              <div class="metric"><p>Currently Active: ${data.overview.currently_active}</p></div>
              <div class="metric"><p>Completed: ${data.overview.completed}</p></div>
              <div class="metric"><p>Drop-off Rate: ${data.overview.drop_off_rate}%</p></div>
              <div class="metric"><p>Avg Completion Time: ${data.overview.avg_completion_time} min</p></div>
              <div class="metric"><p>Goal Achievement Rate: ${data.overview.goal_achievement_rate}%</p></div>

              <h2>Funnel Analysis</h2>
              <table>
                <thead>
                  <tr>
                    <th>Step Name</th>
                    <th>Entered</th>
                    <th>Completed</th>
                    <th>Drop-offs</th>
                    <th>Rate</th>
                  </tr>
                </thead>
                <tbody>
                  ${data.funnel.map(step => `
                    <tr>
                      <td>${step.step_name}</td>
                      <td>${step.contacts_entered}</td>
                      <td>${step.contacts_completed}</td>
                      <td>${step.drop_off_count}</td>
                      <td>${step.drop_off_rate}%</td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </body>
          </html>
        `);
        printWindow.document.close();
        printWindow.print();
      }
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className={className} disabled={isExporting}>
          <Download className="mr-2 h-4 w-4" aria-hidden="true" />
          Export
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={exportToCSV} disabled={isExporting}>
          <FileSpreadsheet className="mr-2 h-4 w-4" aria-hidden="true" />
          Export as CSV
        </DropdownMenuItem>
        <DropdownMenuItem onClick={exportToJSON} disabled={isExporting}>
          <FileCode className="mr-2 h-4 w-4" aria-hidden="true" />
          Export as JSON
        </DropdownMenuItem>
        <DropdownMenuItem onClick={exportToPDF} disabled={isExporting}>
          <FileText className="mr-2 h-4 w-4" aria-hidden="true" />
          Print / PDF
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
