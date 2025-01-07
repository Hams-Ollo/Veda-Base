import { useEffect, useRef, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';

export interface WebSocketMessage {
  type: string;
  batch_id: string;
  data: Record<string, unknown>;
}

interface UseWebSocketOptions {
  onProgress?: (data: WebSocketMessage) => void;
  onComplete?: (data: WebSocketMessage) => void;
  onError?: (error: Error) => void;
  autoReconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export function useWebSocket(batchId: string, options: UseWebSocketOptions = {}) {
  const socket = useRef<Socket | undefined>(undefined);
  const reconnectAttempts = useRef<number>(0);
  const reconnectTimer = useRef<NodeJS.Timeout | undefined>(undefined);
  
  const {
    onProgress,
    onComplete,
    onError,
    autoReconnect = true,
    reconnectInterval = 5000,
    maxReconnectAttempts = 5
  } = options;
  
  const connect = useCallback(() => {
    if (socket.current?.connected) return;
    
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
    
    socket.current = io(`${wsUrl}/documents/ws/${batchId}`, {
      transports: ['websocket'],
      reconnection: false, // We'll handle reconnection ourselves
    });
    
    // Setup event listeners
    socket.current.on('connect', () => {
      console.log('WebSocket connected');
      reconnectAttempts.current = 0;
    });
    
    socket.current.on('disconnect', () => {
      console.log('WebSocket disconnected');
      if (autoReconnect && reconnectAttempts.current < maxReconnectAttempts) {
        reconnectTimer.current = setTimeout(() => {
          reconnectAttempts.current++;
          connect();
        }, reconnectInterval);
      }
    });
    
    socket.current.on('processing_progress', (data: WebSocketMessage) => {
      if (onProgress) onProgress(data);
    });
    
    socket.current.on('processing_complete', (data: WebSocketMessage) => {
      if (onComplete) onComplete(data);
    });
    
    socket.current.on('error', (error: Error) => {
      console.error('WebSocket error:', error);
      onError?.(error);
    });
    
    // Start connection
    socket.current.connect();
  }, [
    batchId,
    onProgress,
    onComplete,
    onError,
    autoReconnect,
    reconnectInterval,
    maxReconnectAttempts
  ]);
  
  const disconnect = useCallback(() => {
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current);
    }
    
    if (socket.current) {
      socket.current.removeAllListeners();
      socket.current.disconnect();
    }
  }, []);
  
  // Connect on mount, disconnect on unmount
  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);
  
  // Expose socket methods
  const send = useCallback((message: WebSocketMessage) => {
    socket.current?.emit('message', message);
  }, []);
  
  const isConnected = useCallback(() => {
    return socket.current?.connected || false;
  }, []);
  
  return {
    send,
    isConnected,
    disconnect,
    reconnect: connect,
  };
}

export default useWebSocket; 