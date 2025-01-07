"""Routes for document upload and processing."""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import uuid
from datetime import datetime

from app.core.document_processor import DocumentProcessor
from app.api.websocket.processing_manager import manager
from app.utils.file_utils import save_upload_file_temporarily

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None
) -> Dict[str, Any]:
    """Upload and process multiple documents."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    batch_id = str(uuid.uuid4())
    processor = DocumentProcessor()
    
    # Save files temporarily
    temp_paths = []
    for file in files:
        temp_path = await save_upload_file_temporarily(file)
        temp_paths.append(temp_path)
    
    # Initialize processing status
    status = {
        "status": "initializing",
        "total_files": len(files),
        "processed_files": 0,
        "success_count": 0,
        "error_count": 0,
        "start_time": datetime.utcnow().isoformat()
    }
    await manager.broadcast_status(batch_id, status)
    
    # Start processing in background
    background_tasks.add_task(
        processor.process_batch,
        temp_paths,
        batch_id,
        manager.broadcast_status
    )
    
    return {
        "batch_id": batch_id,
        "message": "Processing started",
        "total_files": len(files)
    }

@router.get("/types")
async def get_supported_types() -> Dict[str, List[str]]:
    """Get list of supported document types."""
    return {
        "supported_types": [
            "pdf",
            "docx",
            "md",
            "txt",
            "html"
        ]
    } 