'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { ArrowUpTrayIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { useMutation } from '@tanstack/react-query';
import clsx from 'clsx';

import { documents } from '@/services/api';
import type { UploadResponse } from '@/services/api';

interface DocumentUploadProps {
  onUploadStart?: () => void;
  onUploadComplete?: (response: UploadResponse) => void;
  onUploadError?: (error: Error) => void;
  maxFiles?: number;
  acceptedFileTypes?: string[];
}

export function DocumentUpload({
  onUploadStart,
  onUploadComplete,
  onUploadError,
  maxFiles = 10,
  acceptedFileTypes = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/markdown',
    'text/plain',
    'text/html',
    'application/x-tex',
    'application/x-bibtex'
  ]
}: DocumentUploadProps) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  
  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: documents.upload,
    onSuccess: (data) => {
      setSelectedFiles([]);
      onUploadComplete?.(data);
    },
    onError: (error: Error) => {
      onUploadError?.(error);
    }
  });
  
  // Dropzone configuration
  const onDrop = useCallback((acceptedFiles: File[]) => {
    setSelectedFiles(prev => [...prev, ...acceptedFiles].slice(0, maxFiles));
  }, [maxFiles]);
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedFileTypes.reduce((acc, type) => ({ ...acc, [type]: [] }), {}),
    maxFiles,
    multiple: true
  });
  
  // Remove file from selection
  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };
  
  // Start upload
  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;
    
    onUploadStart?.();
    uploadMutation.mutate(selectedFiles);
  };
  
  return (
    <div className="space-y-4">
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={clsx(
          'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
          {
            'border-blue-500 bg-blue-50': isDragActive,
            'border-gray-300 hover:border-blue-500': !isDragActive
          }
        )}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center gap-2">
          <ArrowUpTrayIcon className="w-8 h-8 text-gray-400" />
          
          {isDragActive ? (
            <p className="text-blue-500">Drop the files here...</p>
          ) : (
            <>
              <p className="text-gray-600">
                Drag and drop files here, or click to select
              </p>
              <p className="text-sm text-gray-400">
                Supported formats: PDF, DOCX, Markdown, Text, HTML, LaTeX, BibTeX
              </p>
            </>
          )}
        </div>
      </div>
      
      {/* Selected files */}
      {selectedFiles.length > 0 && (
        <div className="space-y-2">
          <h3 className="font-medium">Selected Files ({selectedFiles.length})</h3>
          
          <ul className="divide-y">
            {selectedFiles.map((file, index) => (
              <li
                key={`${file.name}-${index}`}
                className="flex items-center justify-between py-2"
              >
                <div>
                  <p className="font-medium">{file.name}</p>
                  <p className="text-sm text-gray-500">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                
                <button
                  onClick={() => removeFile(index)}
                  className="p-1 text-gray-400 hover:text-red-500"
                >
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </li>
            ))}
          </ul>
          
          {/* Upload button */}
          <button
            onClick={handleUpload}
            disabled={uploadMutation.isPending}
            className={clsx(
              'w-full py-2 px-4 rounded-lg text-white font-medium transition-colors',
              {
                'bg-blue-500 hover:bg-blue-600': !uploadMutation.isPending,
                'bg-gray-400 cursor-not-allowed': uploadMutation.isPending
              }
            )}
          >
            {uploadMutation.isPending ? 'Uploading...' : 'Upload Files'}
          </button>
        </div>
      )}
      
      {/* Error message */}
      {uploadMutation.error && (
        <div className="p-4 rounded-lg bg-red-50 text-red-500">
          {uploadMutation.error.message}
        </div>
      )}
    </div>
  );
}

export default DocumentUpload; 