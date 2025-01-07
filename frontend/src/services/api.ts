import axios from 'axios';
import type { AxiosInstance } from 'axios';

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Document processing endpoints
export const documents = {
  upload: async (files: File[]) => {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    
    const response = await apiClient.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  getStatus: async (batchId: string) => {
    const response = await apiClient.get(`/documents/status/${batchId}`);
    return response.data;
  },
  
  cancelProcessing: async (batchId: string) => {
    const response = await apiClient.delete(`/documents/cancel/${batchId}`);
    return response.data;
  },
};

// Processing metrics endpoints
export const processing = {
  getMetrics: async () => {
    const response = await apiClient.get('/processing/metrics');
    return response.data;
  },
  
  getActive: async () => {
    const response = await apiClient.get('/processing/active');
    return response.data;
  },
  
  getHistory: async (limit = 50, offset = 0) => {
    const response = await apiClient.get('/processing/history', {
      params: { limit, offset },
    });
    return response.data;
  },
  
  getPerformance: async () => {
    const response = await apiClient.get('/processing/performance');
    return response.data;
  },
  
  optimize: async () => {
    const response = await apiClient.post('/processing/optimize');
    return response.data;
  },
};

// Types
export interface UploadResponse {
  batch_id: string;
  message: string;
}

export interface ProcessingStatus {
  batch_id: string;
  total_files: number;
  processed_files: number;
  success_count: number;
  error_count: number;
  current_file?: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  errors: Array<{
    file: string;
    error: string;
  }>;
}

export interface PerformanceStats {
  processing_speed: {
    average_time_per_file: number;
    files_per_second: number;
  };
  memory_usage: {
    current: number;
    peak: number;
  };
  cache_stats: {
    hit_rate: number;
    size: number;
  };
  error_rates: {
    total_errors: number;
    error_rate: number;
  };
  timestamp: string;
}

export const uploadDocuments = documents.upload;
export const getProcessingStatus = documents.getStatus;
export const cancelProcessing = documents.cancelProcessing;
export const getWebSocketUrl = (batchId: string): string => {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsHost = process.env.NEXT_PUBLIC_WS_URL || window.location.host;
  return `${wsProtocol}//${wsHost}/api/ws/processing/${batchId}`;
};

const api = {
  documents,
  processing,
};

export default api; 