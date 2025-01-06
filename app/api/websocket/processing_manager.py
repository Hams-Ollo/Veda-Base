"""WebSocket manager for document processing updates."""

from fastapi import WebSocket
from typing import Dict, Set, Optional
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ProcessingWebSocketManager:
    """Manages WebSocket connections for document processing updates."""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.processing_tasks: Dict[str, asyncio.Task] = {}
        
    async def connect(self, websocket: WebSocket, batch_id: str):
        """Connect a new WebSocket client."""
        await websocket.accept()
        if batch_id not in self.active_connections:
            self.active_connections[batch_id] = set()
        self.active_connections[batch_id].add(websocket)
        logger.info(f"New WebSocket connection for batch {batch_id}")
        
    def disconnect(self, websocket: WebSocket, batch_id: str):
        """Disconnect a WebSocket client."""
        if batch_id in self.active_connections:
            self.active_connections[batch_id].discard(websocket)
            if not self.active_connections[batch_id]:
                del self.active_connections[batch_id]
        logger.info(f"WebSocket disconnected for batch {batch_id}")
        
    async def broadcast_to_batch(self, batch_id: str, message: dict):
        """Broadcast a message to all connections for a specific batch."""
        if batch_id not in self.active_connections:
            return
            
        dead_connections = set()
        for connection in self.active_connections[batch_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {str(e)}")
                dead_connections.add(connection)
                
        # Cleanup dead connections
        for dead in dead_connections:
            self.active_connections[batch_id].discard(dead)
            
    async def start_processing(self, batch_id: str, total_files: int):
        """Start tracking processing for a batch."""
        if batch_id in self.processing_tasks:
            return
            
        self.processing_tasks[batch_id] = {
            'start_time': datetime.utcnow(),
            'total_files': total_files,
            'processed_files': 0,
            'status': 'processing',
            'errors': []
        }
        
        await self.broadcast_to_batch(batch_id, {
            'type': 'processing_started',
            'batch_id': batch_id,
            'total_files': total_files,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    async def update_progress(
        self,
        batch_id: str,
        files_processed: int,
        current_file: Optional[str] = None,
        error: Optional[str] = None
    ):
        """Update processing progress for a batch."""
        if batch_id not in self.processing_tasks:
            return
            
        task = self.processing_tasks[batch_id]
        task['processed_files'] = files_processed
        
        if error:
            task['errors'].append(error)
            
        progress = {
            'type': 'processing_progress',
            'batch_id': batch_id,
            'files_processed': files_processed,
            'total_files': task['total_files'],
            'current_file': current_file,
            'progress_percentage': (files_processed / task['total_files']) * 100,
            'error': error,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.broadcast_to_batch(batch_id, progress)
        
    async def complete_processing(self, batch_id: str, success: bool = True):
        """Mark processing as complete for a batch."""
        if batch_id not in self.processing_tasks:
            return
            
        task = self.processing_tasks[batch_id]
        task['status'] = 'completed' if success else 'failed'
        task['end_time'] = datetime.utcnow()
        
        completion_message = {
            'type': 'processing_complete',
            'batch_id': batch_id,
            'success': success,
            'total_processed': task['processed_files'],
            'total_files': task['total_files'],
            'errors': task['errors'],
            'duration_seconds': (task['end_time'] - task['start_time']).total_seconds(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.broadcast_to_batch(batch_id, completion_message)
        
        # Cleanup after a delay to ensure clients receive the completion message
        await asyncio.sleep(5)
        if batch_id in self.processing_tasks:
            del self.processing_tasks[batch_id]
            
    async def cancel_processing(self, batch_id: str):
        """Cancel processing for a batch."""
        if batch_id not in self.processing_tasks:
            return False
            
        task = self.processing_tasks[batch_id]
        task['status'] = 'cancelled'
        
        await self.broadcast_to_batch(batch_id, {
            'type': 'processing_cancelled',
            'batch_id': batch_id,
            'files_processed': task['processed_files'],
            'total_files': task['total_files'],
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Cleanup
        if batch_id in self.processing_tasks:
            del self.processing_tasks[batch_id]
            
        return True
        
    def get_processing_status(self, batch_id: str) -> Optional[dict]:
        """Get current processing status for a batch."""
        if batch_id not in self.processing_tasks:
            return None
            
        task = self.processing_tasks[batch_id]
        return {
            'batch_id': batch_id,
            'status': task['status'],
            'files_processed': task['processed_files'],
            'total_files': task['total_files'],
            'progress_percentage': (task['processed_files'] / task['total_files']) * 100,
            'errors': task['errors'],
            'start_time': task['start_time'].isoformat(),
            'duration_seconds': (datetime.utcnow() - task['start_time']).total_seconds()
        } 