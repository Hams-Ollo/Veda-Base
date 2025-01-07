"""WebSocket manager for document processing updates."""

from fastapi import WebSocket
from typing import Dict, Set
import asyncio
import json
from datetime import datetime

class ProcessingManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.processing_statuses: Dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, batch_id: str):
        await websocket.accept()
        if batch_id not in self.active_connections:
            self.active_connections[batch_id] = set()
        self.active_connections[batch_id].add(websocket)

    def disconnect(self, websocket: WebSocket, batch_id: str):
        self.active_connections[batch_id].remove(websocket)
        if not self.active_connections[batch_id]:
            del self.active_connections[batch_id]
            if batch_id in self.processing_statuses:
                del self.processing_statuses[batch_id]

    async def broadcast_status(self, batch_id: str, status: dict):
        """Broadcast processing status to all connected clients for a specific batch."""
        if batch_id not in self.active_connections:
            return
        
        status["timestamp"] = datetime.utcnow().isoformat()
        self.processing_statuses[batch_id] = status
        
        dead_connections = set()
        for connection in self.active_connections[batch_id]:
            try:
                await connection.send_json(status)
            except:
                dead_connections.add(connection)
        
        # Clean up dead connections
        for dead in dead_connections:
            self.active_connections[batch_id].remove(dead)

    def get_status(self, batch_id: str) -> dict:
        """Get the current processing status for a batch."""
        return self.processing_statuses.get(batch_id, {
            "status": "not_found",
            "message": "No processing status found for this batch ID"
        })

    async def mark_complete(self, batch_id: str, success: bool = True):
        """Mark a batch as complete and notify all clients."""
        status = {
            "status": "completed" if success else "failed",
            "message": "Processing completed successfully" if success else "Processing failed",
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_status(batch_id, status)
        
        # Clean up after a delay
        await asyncio.sleep(60)  # Keep status for 1 minute after completion
        if batch_id in self.processing_statuses:
            del self.processing_statuses[batch_id]

# Global instance of the processing manager
manager = ProcessingManager() 