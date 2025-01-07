"""Routes for document processing and WebSocket connections."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from app.api.websocket.processing_manager import manager
from typing import Dict, Any
import uuid

router = APIRouter(prefix="/processing", tags=["processing"])

@router.websocket("/ws/{batch_id}")
async def websocket_endpoint(websocket: WebSocket, batch_id: str):
    """WebSocket endpoint for real-time processing updates."""
    await manager.connect(websocket, batch_id)
    try:
        while True:
            # Keep connection alive and handle any client messages
            data = await websocket.receive_json()
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, batch_id)
    except Exception:
        manager.disconnect(websocket, batch_id)

@router.get("/status/{batch_id}")
async def get_processing_status(batch_id: str) -> Dict[str, Any]:
    """Get the current status of a processing batch."""
    return manager.get_status(batch_id)

@router.post("/cancel/{batch_id}")
async def cancel_processing(batch_id: str):
    """Cancel an ongoing processing batch."""
    status = manager.get_status(batch_id)
    if status["status"] == "not_found":
        raise HTTPException(status_code=404, detail="Batch not found")
    
    await manager.broadcast_status(batch_id, {
        "status": "cancelled",
        "message": "Processing cancelled by user"
    })
    return {"status": "cancelled", "batch_id": batch_id} 