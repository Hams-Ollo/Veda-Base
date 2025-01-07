export interface ProcessingError {
  file: string;
  error: string;
}

export interface BatchProcessingStatus {
  batch_id: string;
  total_files: number;
  processed_files: number;
  success_count: number;
  error_count: number;
  current_file?: string;
  status: 'pending' | 'processing' | 'completed' | 'error' | 'cancelled';
  errors: ProcessingError[];
  start_time?: string;
  end_time?: string;
} 