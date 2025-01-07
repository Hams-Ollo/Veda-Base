"""File handling utilities."""

from typing import List, Set, Optional
import logging
from pathlib import Path
import tempfile
import shutil
import aiofiles
import asyncio
from datetime import datetime, timedelta
import mimetypes
from fastapi import UploadFile

logger = logging.getLogger(__name__)

# Global set to track temporary files
temp_files: Set[Path] = set()
temp_cleanup_lock = asyncio.Lock()

def safe_file_ops(func):
    """Decorator for safe file operations with proper cleanup."""
    async def wrapper(*args, **kwargs):
        temp_path = None
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"File operation error in {func.__name__}: {str(e)}")
            raise
        finally:
            if temp_path and isinstance(temp_path, Path):
                try:
                    temp_path.unlink(missing_ok=True)
                except Exception as e:
                    logger.error(f"Error cleaning up temp file: {str(e)}")
    return wrapper

async def chunk_reader(file_path: Path, chunk_size: int = 8192):
    """Read file in chunks to handle large files efficiently."""
    async with aiofiles.open(file_path, 'rb') as f:
        while chunk := await f.read(chunk_size):
            yield chunk

def get_file_type(file_path: Path) -> str:
    """Get the type of a file based on its extension."""
    mime_type, _ = mimetypes.guess_type(str(file_path))
    
    if mime_type:
        if mime_type.startswith('text/markdown'):
            return 'md'
        elif mime_type.startswith('text/html'):
            return 'html'
        elif mime_type.startswith('application/pdf'):
            return 'pdf'
        elif mime_type.startswith('text/'):
            return 'txt'
        elif mime_type.startswith(('application/x-python', 'text/x-python')):
            return 'code'
    
    # Fallback to extension
    ext = file_path.suffix.lower().lstrip('.')
    if ext in ['md', 'markdown']:
        return 'md'
    elif ext in ['html', 'htm']:
        return 'html'
    elif ext == 'pdf':
        return 'pdf'
    elif ext in ['txt', 'text']:
        return 'txt'
    elif ext in ['py', 'js', 'java', 'cpp', 'c', 'rs', 'go', 'rb']:
        return 'code'
    
    raise ValueError(f"Unsupported file type: {file_path}")

async def save_upload_file_temporarily(upload_file: UploadFile) -> Path:
    """Save an uploaded file to a temporary location."""
    try:
        suffix = Path(upload_file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            # Read in chunks to handle large files
            async with aiofiles.open(tmp.name, 'wb') as f:
                while chunk := await upload_file.read(8192):
                    await f.write(chunk)
            
            tmp_path = Path(tmp.name)
            async with temp_cleanup_lock:
                temp_files.add(tmp_path)
            return tmp_path
            
    except Exception as e:
        logger.error(f"Error saving upload file: {str(e)}")
        raise

async def cleanup_temp_files(paths: Optional[List[Path]] = None):
    """Clean up temporary files."""
    async with temp_cleanup_lock:
        to_remove = set(paths) if paths else temp_files.copy()
        
        for path in to_remove:
            try:
                if path.exists():
                    path.unlink()
                temp_files.discard(path)
            except Exception as e:
                logger.error(f"Error cleaning up temp file {path}: {str(e)}")

async def ensure_directory(path: Path):
    """Ensure a directory exists."""
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Error creating directory {path}: {str(e)}")
        raise

async def safe_move_file(source: Path, dest: Path):
    """Safely move a file with error handling."""
    try:
        # Ensure destination directory exists
        await ensure_directory(dest.parent)
        
        # Move file
        shutil.move(str(source), str(dest))
        
        # Remove from temp files if it was one
        async with temp_cleanup_lock:
            temp_files.discard(source)
            
    except Exception as e:
        logger.error(f"Error moving file {source} to {dest}: {str(e)}")
        raise

async def get_file_info(path: Path) -> dict:
    """Get information about a file."""
    try:
        stats = path.stat()
        return {
            "name": path.name,
            "extension": path.suffix.lstrip('.'),
            "size": stats.st_size,
            "created": datetime.fromtimestamp(stats.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
            "type": get_file_type(path)
        }
    except Exception as e:
        logger.error(f"Error getting file info for {path}: {str(e)}")
        raise

class TempFileManager:
    """Context manager for temporary file handling."""
    
    def __init__(self, suffix: Optional[str] = None):
        self.suffix = suffix
        self.path: Optional[Path] = None
    
    async def __aenter__(self) -> Path:
        """Create and track temporary file."""
        try:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=self.suffix)
            self.path = Path(tmp.name)
            tmp.close()
            
            async with temp_cleanup_lock:
                temp_files.add(self.path)
            
            return self.path
            
        except Exception as e:
            logger.error(f"Error creating temp file: {str(e)}")
            raise
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up temporary file."""
        if self.path:
            await cleanup_temp_files([self.path])

async def periodic_temp_cleanup():
    """Periodically clean up old temporary files."""
    while True:
        try:
            current_time = datetime.now()
            async with temp_cleanup_lock:
                for path in temp_files.copy():
                    try:
                        if path.exists():
                            stats = path.stat()
                            created_time = datetime.fromtimestamp(stats.st_ctime)
                            if current_time - created_time > timedelta(hours=1):
                                path.unlink()
                                temp_files.discard(path)
                    except Exception as e:
                        logger.error(f"Error cleaning up temp file {path}: {str(e)}")
                        temp_files.discard(path)
        
        except Exception as e:
            logger.error(f"Error in periodic temp cleanup: {str(e)}")
        
        await asyncio.sleep(3600)  # Run every hour 