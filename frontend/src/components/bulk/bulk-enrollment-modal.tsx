'use client';

import { useState, useCallback } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent } from '@/components/ui/card';
import { Upload, FileSpreadsheet, X, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import { clsx } from 'clsx';

interface BulkEnrollmentModalProps {
  open: boolean;
  onClose: () => void;
  workflowId: string;
  workflowName: string;
}

interface UploadProgress {
  stage: 'idle' | 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  totalContacts: number;
  processedContacts: number;
  successful: number;
  failed: number;
  errors: string[];
}

const INITIAL_PROGRESS: UploadProgress = {
  stage: 'idle',
  progress: 0,
  totalContacts: 0,
  processedContacts: 0,
  successful: 0,
  failed: 0,
  errors: [],
};

export function BulkEnrollmentModal({
  open,
  onClose,
  workflowId,
  workflowName,
}: BulkEnrollmentModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>(INITIAL_PROGRESS);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === 'text/csv' || droppedFile.name.endsWith('.csv')) {
        setFile(droppedFile);
        setUploadProgress(INITIAL_PROGRESS);
      }
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setUploadProgress(INITIAL_PROGRESS);
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setUploadProgress(INITIAL_PROGRESS);
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploadProgress({ ...INITIAL_PROGRESS, stage: 'uploading' });

    const formData = new FormData();
    formData.append('file', file);
    formData.append('workflowId', workflowId);

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev.progress >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return { ...prev, progress: prev.progress + 10 };
        });
      }, 200);

      const response = await fetch('/api/workflows/bulk-enroll', {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const result = await response.json();

      setUploadProgress({
        stage: 'completed',
        progress: 100,
        totalContacts: result.totalContacts,
        processedContacts: result.processedContacts,
        successful: result.successful,
        failed: result.failed,
        errors: result.errors || [],
      });
    } catch (error) {
      setUploadProgress((prev) => ({
        ...prev,
        stage: 'error',
        errors: ['Failed to upload file. Please try again.'],
      }));
    }
  };

  const handleDownloadTemplate = () => {
    const csvContent =
      'email,first_name,last_name,phone\njohn@example.com,John,Doe,555-1234\njane@example.com,Jane,Smith,555-5678';
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'bulk-enrollment-template.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleClose = () => {
    setFile(null);
    setUploadProgress(INITIAL_PROGRESS);
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Bulk Enrollment - {workflowName}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Instructions */}
          <Card>
            <CardContent className="pt-4">
              <h3 className="font-semibold mb-2">How to use bulk enrollment</h3>
              <ol className="text-sm text-muted-foreground space-y-1 list-decimal list-inside">
                <li>Download the CSV template</li>
                <li>Fill in the contact information</li>
                <li>Upload the completed CSV file</li>
                <li>Review the results after processing</li>
              </ol>
              <Button
                variant="outline"
                size="sm"
                className="mt-3"
                onClick={handleDownloadTemplate}
              >
                <FileSpreadsheet className="h-4 w-4 mr-2" />
                Download Template
              </Button>
            </CardContent>
          </Card>

          {/* Upload Area */}
          {uploadProgress.stage === 'idle' && (
            <div>
              <Label htmlFor="file-upload">Upload CSV File</Label>
              <div
                className={clsx(
                  'mt-2 border-2 border-dashed rounded-lg p-8 text-center transition-colors',
                  dragActive ? 'border-primary bg-primary/5' : 'border-muted-foreground/25',
                  'hover:border-primary hover:bg-primary/5'
                )}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                {file ? (
                  <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <div className="flex items-center gap-3">
                      <FileSpreadsheet className="h-8 w-8 text-green-600" />
                      <div className="text-left">
                        <p className="font-medium">{file.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {(file.size / 1024).toFixed(1)} KB
                        </p>
                      </div>
                    </div>
                    <Button variant="ghost" size="icon" onClick={handleRemoveFile}>
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ) : (
                  <>
                    <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                    <p className="text-sm text-muted-foreground mb-2">
                      Drag and drop your CSV file here, or click to browse
                    </p>
                    <Input
                      id="file-upload"
                      type="file"
                      accept=".csv"
                      onChange={handleFileChange}
                      className="hidden"
                      aria-label="Upload CSV file"
                    />
                    <Label
                      htmlFor="file-upload"
                      className="cursor-pointer text-sm text-primary hover:underline"
                    >
                      Browse files
                    </Label>
                  </>
                )}
              </div>
            </div>
          )}

          {/* Progress */}
          {uploadProgress.stage !== 'idle' && uploadProgress.stage !== 'error' && (
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label>
                    {uploadProgress.stage === 'uploading'
                      ? 'Uploading...'
                      : uploadProgress.stage === 'processing'
                      ? 'Processing contacts...'
                      : 'Completed'}
                  </Label>
                  <span className="text-sm text-muted-foreground">
                    {uploadProgress.progress}%
                  </span>
                </div>
                <Progress value={uploadProgress.progress} />
              </div>

              {uploadProgress.processedContacts > 0 && (
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-green-600">
                      {uploadProgress.successful}
                    </p>
                    <p className="text-sm text-muted-foreground">Successful</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-red-600">{uploadProgress.failed}</p>
                    <p className="text-sm text-muted-foreground">Failed</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{uploadProgress.totalContacts}</p>
                    <p className="text-sm text-muted-foreground">Total</p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Errors */}
          {uploadProgress.errors.length > 0 && (
            <Card className="border-red-200 dark:border-red-800">
              <CardContent className="pt-4">
                <div className="flex items-start gap-2">
                  <AlertCircle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <p className="font-medium text-red-500">Errors occurred</p>
                    <ul className="mt-2 space-y-1 text-sm text-red-600 dark:text-red-400">
                      {uploadProgress.errors.map((error, index) => (
                        <li key={index}>• {error}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Success Message */}
          {uploadProgress.stage === 'completed' && uploadProgress.failed === 0 && (
            <Card className="border-green-200 dark:border-green-800">
              <CardContent className="pt-4">
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="h-8 w-8 text-green-500" />
                  <div>
                    <p className="font-medium text-green-600">Enrollment Complete!</p>
                    <p className="text-sm text-muted-foreground">
                      All {uploadProgress.successful} contacts have been enrolled successfully.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={handleClose}
            disabled={uploadProgress.stage === 'uploading' || uploadProgress.stage === 'processing'}
          >
            {uploadProgress.stage === 'completed' ? 'Close' : 'Cancel'}
          </Button>
          {uploadProgress.stage === 'idle' && (
            <Button onClick={handleUpload} disabled={!file}>
              Upload & Process
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
