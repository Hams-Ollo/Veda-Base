'use client';

import { useEffect, useRef, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getProcessingStatus, cancelProcessing, getWebSocketUrl } from '@/services/api';
import type { ProcessingStatus } from '@/services/api';

interface ProcessingProgressProps {
  batchId: string;
  onComplete: () => void;
  onCancel: () => void;
}

export default function ProcessingProgress({
  batchId,
  onComplete,
  onCancel,
}: ProcessingProgressProps) {
  const [status, setStatus] = useState<ProcessingStatus | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Query for initial status
  const { data: initialStatus } = useQuery({
    queryKey: ['processingStatus', batchId],
    queryFn: () => getProcessingStatus(batchId),
    enabled: !status,
  });

  // WebSocket connection for real-time updates
  useEffect(() => {
    const ws = new WebSocket(getWebSocketUrl(batchId));
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const newStatus = JSON.parse(event.data) as ProcessingStatus;
      setStatus(newStatus);

      if (newStatus.status === 'completed') {
        onComplete();
        ws.close();
      }
    };

    ws.onerror = () => {
      console.error('WebSocket error occurred');
    };

    ws.onclose = () => {
      wsRef.current = null;
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [batchId, onComplete, status]);

  useEffect(() => {
    if (initialStatus) {
      setStatus(initialStatus);
    }
  }, [initialStatus]);

  const handleCancel = async () => {
    try {
      await cancelProcessing(batchId);
      onCancel();
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.close();
      }
    } catch (error) {
      console.error('Failed to cancel processing:', error);
    }
  };

  if (!status) {
    return (
      <div className="flex justify-center items-center p-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const progress = status.total_files > 0
    ? Math.round((status.processed_files / status.total_files) * 100)
    : 0;

  return (
    <div className="space-y-4">
      {/* Progress Bar */}
      <div className="relative pt-1">
        <div className="flex mb-2 items-center justify-between">
          <div>
            <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-blue-600 bg-blue-200">
              {status.status}
            </span>
          </div>
          <div className="text-right">
            <span className="text-xs font-semibold inline-block text-blue-600">
              {progress.toFixed(1)}%
            </span>
          </div>
        </div>
        <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-blue-200">
          <div
            style={{ width: `${progress}%` }}
            className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-500 transition-all duration-500"
          ></div>
        </div>
      </div>

      {/* Processing Stats */}
      <div className="bg-gray-50 rounded-lg p-4">
        <dl className="grid grid-cols-2 gap-4">
          <div>
            <dt className="text-sm font-medium text-gray-500">Files Processed</dt>
            <dd className="mt-1 text-sm text-gray-900">
              {status.processed_files} / {status.total_files}
            </dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Success Rate</dt>
            <dd className="mt-1 text-sm text-gray-900">
              {status.total_files > 0
                ? `${Math.round((status.success_count / status.total_files) * 100)}%`
                : '0%'}
            </dd>
          </div>
        </dl>
      </div>

      {/* Current File */}
      {status.current_file && (
        <div className="text-sm text-gray-600">
          Processing: {status.current_file}
        </div>
      )}

      {/* Errors */}
      {status.errors.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-medium text-red-800 mb-2">Errors</h4>
          <ul className="space-y-2">
            {status.errors.map((error, index) => (
              <li
                key={index}
                className="text-sm text-red-600 bg-red-50 rounded-md p-2"
              >
                <span className="font-medium">{error.file}:</span> {error.error}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Cancel Button */}
      {status.status !== 'completed' && (
        <div className="mt-4">
          <button
            type="button"
            onClick={handleCancel}
            className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            Cancel Processing
          </button>
        </div>
      )}
    </div>
  );
} 