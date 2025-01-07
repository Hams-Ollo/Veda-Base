"""Core document processing functionality."""

from typing import List, Dict, Any, Callable, Optional
from pathlib import Path
import asyncio
from datetime import datetime
import logging
from enum import Enum

from app.core.document.extractors.pdf import PDFExtractor
from app.core.document.extractors.markdown import MarkdownExtractor
from app.core.document.extractors.html import HTMLExtractor
from app.utils.file_utils import get_file_type, cleanup_temp_files
from app.utils.cache_utils import cache_result
from app.utils.performance_utils import timer, memory_usage

logger = logging.getLogger(__name__)

class DocumentType(Enum):
    """Supported document types."""
    PDF = "pdf"
    MARKDOWN = "md"
    HTML = "html"
    TEXT = "txt"
    CODE = "code"

class ProcessingError(Exception):
    """Custom exception for document processing errors."""
    pass

class DocumentProcessor:
    """Handles processing of various document types."""
    
    def __init__(
        self,
        max_concurrent: int = 5,
        cache_enabled: bool = True
    ):
        self.max_concurrent = max_concurrent
        self.cache_enabled = cache_enabled
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # Initialize extractors
        self.extractors = {
            DocumentType.PDF: PDFExtractor(),
            DocumentType.MARKDOWN: MarkdownExtractor(),
            DocumentType.HTML: HTMLExtractor()
        }
    
    @cache_result
    async def process_single_file(
        self,
        file_path: Path,
        batch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a single document file."""
        try:
            doc_type = get_file_type(file_path)
            if doc_type not in DocumentType.__members__:
                raise ProcessingError(f"Unsupported file type: {doc_type}")
            
            extractor = self.extractors[DocumentType[doc_type]]
            with timer(), memory_usage():
                content = await extractor.extract(file_path)
            
            return {
                "file_path": str(file_path),
                "doc_type": doc_type,
                "content": content,
                "success": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return {
                "file_path": str(file_path),
                "error": str(e),
                "success": False,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def process_batch(
        self,
        file_paths: List[Path],
        batch_id: str,
        status_callback: Callable[[str, Dict[str, Any]], None]
    ) -> Dict[str, Any]:
        """Process a batch of documents with progress tracking."""
        total_files = len(file_paths)
        processed = 0
        success_count = 0
        error_count = 0
        results = []
        
        try:
            async def process_with_semaphore(file_path: Path):
                async with self.semaphore:
                    return await self.process_single_file(file_path, batch_id)
            
            tasks = [process_with_semaphore(path) for path in file_paths]
            for future in asyncio.as_completed(tasks):
                result = await future
                processed += 1
                if result["success"]:
                    success_count += 1
                else:
                    error_count += 1
                
                results.append(result)
                await status_callback(batch_id, {
                    "status": "processing",
                    "total_files": total_files,
                    "processed_files": processed,
                    "success_count": success_count,
                    "error_count": error_count,
                    "current_file": result["file_path"],
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            return {
                "batch_id": batch_id,
                "total_files": total_files,
                "processed_files": processed,
                "success_count": success_count,
                "error_count": error_count,
                "results": results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        finally:
            # Cleanup temporary files
            await cleanup_temp_files(file_paths) 