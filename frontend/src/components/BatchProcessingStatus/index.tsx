'use client';

import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  ExclamationCircleIcon,
  DocumentIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';
import clsx from 'clsx';
import { getProcessingStatus, cancelProcessing } from '@/services/api';
import { useWebSocket } from '@/hooks/useWebSocket';
import type { BatchProcessingStatus as BatchStatus, ProcessingError } from '@/types/processing';

interface BatchStatusProps {
  batchId: string;
  onComplete?: () => void;
  onCancel?: () => void;
}

export function BatchProcessingStatus({
  batchId,
  onComplete,
  onCancel,
}: BatchStatusProps) {
  const [status, setStatus] = useState<BatchStatus | null>(null);

  // WebSocket connection for real-time updates
  useWebSocket(batchId, {
    onProgress: (data) => {
      setStatus((data as unknown as { data: BatchStatus }).data);
    },
    onComplete: () => {
      onComplete?.();
    },
  });

  // Initial status fetch
  const { data: initialStatus } = useQuery({
    queryKey: ['batchStatus', batchId],
    queryFn: () => getProcessingStatus(batchId),
    enabled: !status,
  });

  useEffect(() => {
    if (initialStatus && !status) {
      setStatus(initialStatus);
    }
  }, [initialStatus, status]);

  const handleCancel = async () => {
    try {
      await cancelProcessing(batchId);
      onCancel?.();
    } catch (error) {
      console.error('Failed to cancel processing:', error);
    }
  };

  if (!status) {
    return (
      <div className="flex justify-center items-center p-4">
        <ArrowPathIcon className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  const progress = status.total_files > 0
    ? Math.round((status.processed_files / status.total_files) * 100)
    : 0;

  return (
    <div className="space-y-6 bg-white rounded-lg shadow p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <DocumentIcon className="w-6 h-6 text-blue-500" />
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              Batch Processing
            </h3>
            <p className="text-sm text-gray-500">
              {status.current_file || 'Preparing files...'}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className={clsx(
            'px-3 py-1 text-sm font-medium rounded-full',
            {
              'bg-blue-100 text-blue-800': status.status === 'processing',
              'bg-green-100 text-green-800': status.status === 'completed',
              'bg-red-100 text-red-800': status.status === 'error',
              'bg-gray-100 text-gray-800': status.status === 'cancelled',
            }
          )}>
            {status.status.charAt(0).toUpperCase() + status.status.slice(1)}
          </span>
        </div>
      </div>

      {/* Progress */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Progress</span>
          <span className="text-gray-900 font-medium">{progress}%</span>
        </div>
        <div className="relative w-full h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={clsx(
              'absolute h-full transition-all duration-500 rounded-full',
              {
                'bg-blue-500': status.status === 'processing',
                'bg-green-500': status.status === 'completed',
                'bg-red-500': status.status === 'error',
              }
            )}
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="bg-gray-50 p-4 rounded-lg">
          <dt className="text-sm font-medium text-gray-500">Total Files</dt>
          <dd className="mt-1 text-2xl font-semibold text-gray-900">
            {status.total_files}
          </dd>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <dt className="text-sm font-medium text-gray-500">Processed</dt>
          <dd className="mt-1 text-2xl font-semibold text-gray-900">
            {status.processed_files}
          </dd>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <dt className="text-sm font-medium text-gray-500">Successful</dt>
          <dd className="mt-1 text-2xl font-semibold text-green-600">
            {status.success_count}
          </dd>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <dt className="text-sm font-medium text-gray-500">Failed</dt>
          <dd className="mt-1 text-2xl font-semibold text-red-600">
            {status.error_count}
          </dd>
        </div>
      </div>

      {/* Errors */}
      {status.errors.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">
            Processing Errors
          </h4>
          <div className="bg-red-50 rounded-lg p-4 space-y-2">
            {status.errors.map((error: ProcessingError, index: number) => (
              <div
                key={index}
                className="flex items-start space-x-2 text-sm text-red-700"
              >
                <ExclamationCircleIcon className="w-5 h-5 flex-shrink-0" />
                <div>
                  <span className="font-medium">{error.file}:</span>{' '}
                  {error.error}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      {status.status === 'processing' && (
        <div className="flex justify-end">
          <button
            onClick={handleCancel}
            className="px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-100 rounded-md transition-colors"
          >
            Cancel Processing
          </button>
        </div>
      )}
    </div>
  );
} 