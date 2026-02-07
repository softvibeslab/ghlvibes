'use client';

import { useState, useCallback } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Upload, FileSpreadsheet, Download } from 'lucide-react';
import { importContacts, exportContacts } from '@/lib/api/crm';
import type { ImportConfig } from '@/lib/types/crm';

interface ContactImportModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onImportComplete?: () => void;
}

export function ContactImportModal({
  open,
  onOpenChange,
  onImportComplete,
}: ContactImportModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isImporting, setIsImporting] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  }, []);

  const handleImport = async () => {
    if (!file) return;

    setIsImporting(true);
    try {
      const config: ImportConfig = {
        entity_type: 'contact',
        column_mapping: {
          'First Name': 'first_name',
          'Last Name': 'last_name',
          'Email': 'email',
          'Phone': 'phone',
          'Company': 'company_id',
        },
        skip_duplicates: true,
        update_existing: false,
      };

      await importContacts(file, config);
      onImportComplete?.();
      onOpenChange(false);
      setFile(null);
    } catch (error) {
      console.error('Import failed:', error);
      // TODO: Show error toast
    } finally {
      setIsImporting(false);
    }
  };

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const blob = await exportContacts();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `contacts-export-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
      // TODO: Show error toast
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Import Contacts</DialogTitle>
          <DialogDescription>
            Import contacts from a CSV file. Download the template to see the required format.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          <div className="flex items-center justify-center">
            <Button
              variant="outline"
              onClick={handleExport}
              disabled={isExporting}
            >
              <Download className="mr-2 h-4 w-4" />
              {isExporting ? 'Downloading...' : 'Download Template'}
            </Button>
          </div>

          <div className="border-2 border-dashed rounded-lg p-8">
            <div className="flex flex-col items-center gap-4 text-center">
              <div className="p-4 bg-primary/10 rounded-full">
                <FileSpreadsheet className="h-8 w-8 text-primary" />
              </div>
              <div>
                <Label
                  htmlFor="file-upload"
                  className="cursor-pointer text-sm font-medium hover:underline"
                >
                  Click to upload or drag and drop
                </Label>
                <p className="text-xs text-muted-foreground mt-1">
                  CSV files only, max 5MB
                </p>
              </div>
              <Input
                id="file-upload"
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="hidden"
              />
              {file && (
                <div className="flex items-center gap-2 text-sm">
                  <FileSpreadsheet className="h-4 w-4" />
                  {file.name}
                </div>
              )}
            </div>
          </div>

          <div className="space-y-2 text-sm text-muted-foreground">
            <p className="font-medium">Import options:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Skip duplicate contacts (same email)</li>
              <li>Update existing contacts by email</li>
              <li>Map columns automatically</li>
            </ul>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleImport}
            disabled={!file || isImporting}
          >
            <Upload className="mr-2 h-4 w-4" />
            {isImporting ? 'Importing...' : 'Import Contacts'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
