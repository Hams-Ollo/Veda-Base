'use client';

import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import DocumentUpload from '@/components/DocumentUpload';
import ProcessingProgress from '@/components/ProcessingProgress';
import type { UploadResponse } from '@/services/api';

const queryClient = new QueryClient();

export default function Home() {
  const [activeBatch, setActiveBatch] = useState<string | null>(null);
  const [uploadComplete, setUploadComplete] = useState(false);

  const handleUploadComplete = (response: UploadResponse) => {
    setActiveBatch(response.batch_id);
    setUploadComplete(true);
  };

  const handleProcessingComplete = () => {
    setUploadComplete(false);
    setActiveBatch(null);
  };

  const handleProcessingCancel = () => {
    setUploadComplete(false);
    setActiveBatch(null);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <main className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">
              Library of Alexandria
            </h1>
            <p className="mt-2 text-sm text-gray-600">
              Upload and process your documents with advanced knowledge management
            </p>
          </div>

          {/* Content */}
          <div className="space-y-8">
            {/* Upload Section */}
            <section className="bg-white rounded-lg shadow">
              <div className="p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">
                  Document Upload
                </h2>
                <DocumentUpload
                  onUploadComplete={handleUploadComplete}
                  maxFiles={10}
                />
              </div>
            </section>

            {/* Processing Section */}
            {activeBatch && (
              <section className="bg-white rounded-lg shadow">
                <div className="p-6">
                  <h2 className="text-lg font-medium text-gray-900 mb-4">
                    Processing Status
                  </h2>
                  <ProcessingProgress
                    batchId={activeBatch}
                    onComplete={handleProcessingComplete}
                    onCancel={handleProcessingCancel}
                  />
                </div>
              </section>
            )}

            {/* Upload Complete Message */}
            {uploadComplete && !activeBatch && (
              <div className="rounded-md bg-green-50 p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg
                      className="h-5 w-5 text-green-400"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-green-800">
                      Upload complete! Processing will begin shortly.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </QueryClientProvider>
  );
}
