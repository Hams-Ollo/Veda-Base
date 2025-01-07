"""Document processing routes for the Library of Alexandria API."""

from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, WebSocket
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
import uuid
import asyncio
from datetime import datetime
import logging
from pathlib import Path
import tempfile
import shutil

from app.core.document_processor import DocumentProcessor
from app.api.websocket.processing_manager import ProcessingWebSocketManager
from app.utils.performance_utils import timer, memory_usage

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize document processor
document_processor = DocumentProcessor(
    max_workers=8,  # Configurable
    chunk_size=1024 * 1024,  # 1MB chunks
    cache_enabled=True
)

@router.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None
) -> Dict:
    """
    Handle document upload and initiate processing.
    
    Args:
        files: List of files to process
        background_tasks: FastAPI background tasks handler
        
    Returns:
        Dict containing batch_id and initial status
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
        
    # Generate batch ID
    batch_id = str(uuid.uuid4())
    
    # Create temporary directory for batch
    temp_dir = Path(tempfile.mkdtemp())
    saved_files = []
    
    try:
        # Save files to temporary directory
        for upload_file in files:
            file_path = temp_dir / upload_file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)
            saved_files.append(file_path)
            
        # Start processing in background
        background_tasks.add_task(
            process_documents_batch,
            batch_id,
            saved_files,
            temp_dir
        )
        
        return {
            "batch_id": batch_id,
            "status": "processing",
            "total_files": len(files),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        # Cleanup on error
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        logger.error(f"Error processing upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{batch_id}")
async def get_processing_status(batch_id: str) -> Dict:
    """
    Get current status of document processing batch.
    
    Args:
        batch_id: Unique identifier for the processing batch
        
    Returns:
        Dict containing current processing status
    """
    status = document_processor.get_statistics()
    if not status:
        raise HTTPException(status_code=404, detail="Batch not found")
    return status

@router.delete("/cancel/{batch_id}")
async def cancel_processing(batch_id: str) -> Dict:
    """
    Cancel ongoing document processing.
    
    Args:
        batch_id: Unique identifier for the processing batch
        
    Returns:
        Dict containing cancellation status
    """
    success = await ProcessingWebSocketManager().cancel_processing(batch_id)
    if not success:
        raise HTTPException(status_code=404, detail="Batch not found or already completed")
        
    return {
        "batch_id": batch_id,
        "status": "cancelled",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.websocket("/ws/{batch_id}")
async def processing_websocket(websocket: WebSocket, batch_id: str):
    """
    WebSocket endpoint for real-time processing updates.
    
    Args:
        websocket: WebSocket connection
        batch_id: Unique identifier for the processing batch
    """
    manager = ProcessingWebSocketManager()
    await manager.connect(websocket, batch_id)
    
    try:
        while True:
            # Keep connection alive and handle any client messages
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        manager.disconnect(websocket, batch_id)

async def process_documents_batch(
    batch_id: str,
    files: List[Path],
    temp_dir: Path
):
    """
    Process a batch of documents and send progress updates.
    
    Args:
        batch_id: Unique identifier for the processing batch
        files: List of file paths to process
        temp_dir: Temporary directory containing the files
    """
    manager = ProcessingWebSocketManager()
    await manager.start_processing(batch_id, len(files))
    
    try:
        for idx, file_path in enumerate(files, 1):
            try:
                # Process single file
                with timer(), memory_usage():
                    await document_processor.process_single_file(file_path)
                
                # Update progress
                await manager.update_progress(
                    batch_id,
                    idx,
                    current_file=file_path.name
                )
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
                await manager.update_progress(
                    batch_id,
                    idx,
                    current_file=file_path.name,
                    error=str(e)
                )
                
        # Mark processing as complete
        await manager.complete_processing(batch_id, success=True)
        
    except Exception as e:
        logger.error(f"Batch processing error: {str(e)}")
        await manager.complete_processing(batch_id, success=False)
        
    finally:
        # Cleanup temporary directory
        try:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        except Exception as e:
            logger.error(f"Error cleaning up temporary directory: {str(e)}") 