'use client';

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ArrowPathIcon, XMarkIcon } from '@heroicons/react/24/outline';
import clsx from 'clsx';

import { documents } from '@/services/api';
import { useWebSocket } from '@/hooks/useWebSocket';
import type { ProcessingStatus } from '@/services/api';
import type { WebSocketMessage } from '@/hooks/useWebSocket';

interface ProcessingProgressProps {
  batchId: string;
  onComplete?: () => void;
  onCancel?: () => void;
}

export function ProcessingProgress({
  batchId,
  onComplete,
  onCancel
}: ProcessingProgressProps) {
  const [status, setStatus] = useState<ProcessingStatus | null>(null);
  
  // WebSocket connection for real-time updates
  useWebSocket(batchId, {
    onProgress: (message: WebSocketMessage) => {
      const processingStatus = message.data as unknown as ProcessingStatus;
      setStatus(processingStatus);
    },
    onComplete: () => {
      onComplete?.();
    }
  });
  
  // Initial status fetch
  const { data: initialStatus } = useQuery({
    queryKey: ['processing-status', batchId],
    queryFn: () => documents.getStatus(batchId),
    enabled: !status // Only fetch if we don't have status from WebSocket
  });
  
  // Use initial status if available
  useEffect(() => {
    if (initialStatus && !status) {
      setStatus(initialStatus);
    }
  }, [initialStatus, status]);
  
  // Handle cancellation
  const handleCancel = async () => {
    try {
      await documents.cancelProcessing(batchId);
      onCancel?.();
    } catch (error) {
      console.error('Failed to cancel processing:', error);
    }
  };
  
  if (!status) {
    return (
      <div className="flex items-center justify-center p-8">
        <ArrowPathIcon className="w-6 h-6 animate-spin text-blue-500" />
      </div>
    );
  }
  
  return (
    <div className="space-y-4 p-4 bg-white rounded-lg shadow">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="font-medium">Processing Documents</h3>
        <button
          onClick={handleCancel}
          className="p-1 text-gray-400 hover:text-red-500"
        >
          <XMarkIcon className="w-5 h-5" />
        </button>
      </div>
      
      {/* Progress bar */}
      <div className="relative pt-1">
        <div className="flex mb-2 items-center justify-between">
          <div>
            <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-blue-600 bg-blue-200">
              {status.processed_files} / {status.total_files} Files
            </span>
          </div>
          <div className="text-right">
            <span className="text-xs font-semibold inline-block text-blue-600">
              {((status.processed_files / status.total_files) * 100).toFixed(1)}%
            </span>
          </div>
        </div>
        <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-blue-100">
          <div
            style={{ width: `${(status.processed_files / status.total_files) * 100}%` }}
            className={clsx(
              'shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center transition-all duration-500',
              {
                'bg-blue-500': status.status === 'processing',
                'bg-green-500': status.status === 'completed',
                'bg-red-500': status.status === 'error'
              }
            )}
          />
        </div>
      </div>
      
      {/* Status details */}
      <div className="text-sm text-gray-500">
        <p>Files processed: {status.processed_files} of {status.total_files}</p>
        {status.errors.length > 0 && (
          <div className="mt-2">
            <p className="text-red-500">Errors ({status.errors.length}):</p>
            <ul className="list-disc list-inside">
              {status.errors.map((error, index) => (
                <li key={index} className="text-xs text-red-400">
                  {error.file}: {error.error}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default ProcessingProgress; 