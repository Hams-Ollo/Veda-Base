"""Processing management routes for the Library of Alexandria API."""

from fastapi import APIRouter, HTTPException
from typing import Dict, List
import logging
from datetime import datetime, timedelta

from app.core.document_processor import DocumentProcessor
from app.utils.performance_utils import get_system_metrics

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/metrics")
async def get_processing_metrics() -> Dict:
    """
    Get current processing metrics including system stats.
    
    Returns:
        Dict containing processing metrics and system stats
    """
    processor = DocumentProcessor()
    system_metrics = get_system_metrics()
    
    return {
        "processing_stats": processor.get_statistics(),
        "system_metrics": system_metrics,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/active")
async def get_active_processes() -> List[Dict]:
    """
    Get list of currently active processing batches.
    
    Returns:
        List of active processing batches with their status
    """
    processor = DocumentProcessor()
    active_batches = []
    
    for batch_id, stats in processor.get_active_batches().items():
        active_batches.append({
            "batch_id": batch_id,
            "status": stats["status"],
            "progress": stats["progress_percentage"],
            "started_at": stats["start_time"],
            "files_processed": stats["processed_files"],
            "total_files": stats["total_files"],
            "duration": str(timedelta(seconds=stats["duration_seconds"]))
        })
    
    return active_batches

@router.get("/history")
async def get_processing_history(
    limit: int = 50,
    offset: int = 0
) -> List[Dict]:
    """
    Get processing history with pagination.
    
    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        List of historical processing records
    """
    processor = DocumentProcessor()
    history = processor.get_processing_history(limit, offset)
    
    return [{
        "batch_id": record["batch_id"],
        "status": record["status"],
        "started_at": record["start_time"],
        "completed_at": record.get("end_time"),
        "files_processed": record["processed_files"],
        "total_files": record["total_files"],
        "success_rate": record["success_rate"],
        "errors": record["errors"],
        "duration": str(timedelta(seconds=record["duration_seconds"]))
    } for record in history]

@router.get("/performance")
async def get_performance_stats() -> Dict:
    """
    Get detailed performance statistics.
    
    Returns:
        Dict containing performance metrics
    """
    processor = DocumentProcessor()
    performance_stats = processor.get_performance_stats()
    
    return {
        "processing_speed": {
            "average_time_per_file": performance_stats["avg_time_per_file"],
            "files_per_second": performance_stats["files_per_second"]
        },
        "memory_usage": {
            "current": performance_stats["current_memory"],
            "peak": performance_stats["peak_memory"]
        },
        "cache_stats": {
            "hit_rate": performance_stats["cache_hit_rate"],
            "size": performance_stats["cache_size"]
        },
        "error_rates": {
            "total_errors": performance_stats["total_errors"],
            "error_rate": performance_stats["error_rate"]
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/optimize")
async def optimize_processing() -> Dict:
    """
    Trigger processing optimization (cache cleanup, memory optimization).
    
    Returns:
        Dict containing optimization results
    """
    processor = DocumentProcessor()
    
    try:
        # Perform optimization
        optimization_results = await processor.optimize()
        
        return {
            "success": True,
            "optimizations": optimization_results,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Optimization error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Optimization failed: {str(e)}"
        ) 