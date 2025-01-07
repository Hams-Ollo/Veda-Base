"""File handling utilities for the Library of Alexandria."""

import os
from pathlib import Path
from typing import Generator, BinaryIO, Union, Optional, List
import hashlib
from contextlib import contextmanager
import shutil
import logging
import mmap
from concurrent.futures import ThreadPoolExecutor
from functools import partial

logger = logging.getLogger(__name__)

class FileOperationError(Exception):
    """Custom exception for file operations."""
    pass

@contextmanager
def safe_file_ops(file_path: Union[str, Path], mode: str = 'r', encoding: Optional[str] = None):
    """Safe file operation context manager.
    
    Args:
        file_path: Path to the file
        mode: File open mode
        encoding: File encoding
    
    Yields:
        File object
    """
    file_path = Path(file_path)
    
    try:
        if 'w' in mode:
            # Create directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup if file exists
            if file_path.exists():
                backup_path = file_path.with_suffix(file_path.suffix + '.bak')
                shutil.copy2(file_path, backup_path)
        
        with open(file_path, mode, encoding=encoding) as f:
            yield f
            
    except Exception as e:
        logger.error(f"Error during file operation: {str(e)}")
        
        # Restore from backup if writing
        if 'w' in mode and file_path.exists():
            backup_path = file_path.with_suffix(file_path.suffix + '.bak')
            if backup_path.exists():
                shutil.copy2(backup_path, file_path)
                
        raise FileOperationError(f"File operation failed: {str(e)}")
        
    finally:
        # Clean up backup
        if 'w' in mode:
            backup_path = file_path.with_suffix(file_path.suffix + '.bak')
            if backup_path.exists():
                backup_path.unlink()

def chunk_reader(
    file_path: Union[str, Path],
    chunk_size: int = 1024 * 1024,  # 1MB
    use_mmap: bool = True
) -> Generator[bytes, None, None]:
    """Memory-efficient file reader that yields chunks of the file.
    
    Args:
        file_path: Path to the file
        chunk_size: Size of chunks to read
        use_mmap: Whether to use memory mapping for large files
    
    Yields:
        File chunks as bytes
    """
    file_path = Path(file_path)
    file_size = file_path.stat().st_size
    
    with open(file_path, 'rb') as f:
        if use_mmap and file_size > chunk_size * 10:  # Use mmap for large files
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                for i in range(0, file_size, chunk_size):
                    yield mm[i:min(i + chunk_size, file_size)]
        else:
            while chunk := f.read(chunk_size):
                yield chunk

def calculate_file_hash(
    file_path: Union[str, Path],
    hash_type: str = 'sha256',
    chunk_size: int = 1024 * 1024  # 1MB
) -> str:
    """Calculate file hash efficiently.
    
    Args:
        file_path: Path to the file
        hash_type: Hash algorithm to use
        chunk_size: Size of chunks to read
    
    Returns:
        File hash as string
    """
    hash_func = getattr(hashlib, hash_type)()
    
    for chunk in chunk_reader(file_path, chunk_size):
        hash_func.update(chunk)
        
    return hash_func.hexdigest()

def process_files_in_parallel(
    file_paths: List[Union[str, Path]],
    processor_func: callable,
    max_workers: Optional[int] = None
) -> List:
    """Process multiple files in parallel.
    
    Args:
        file_paths: List of file paths to process
        processor_func: Function to process each file
        max_workers: Maximum number of worker threads
    
    Returns:
        List of processing results
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(processor_func, file_paths))
    return results

def ensure_dir(path: Union[str, Path]) -> Path:
    """Ensure directory exists and create if it doesn't.
    
    Args:
        path: Directory path
    
    Returns:
        Path object for the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_file_info(file_path: Union[str, Path]) -> dict:
    """Get detailed file information.
    
    Args:
        file_path: Path to the file
    
    Returns:
        Dictionary containing file information
    """
    file_path = Path(file_path)
    stat = file_path.stat()
    
    return {
        'name': file_path.name,
        'extension': file_path.suffix,
        'size': stat.st_size,
        'created': stat.st_ctime,
        'modified': stat.st_mtime,
        'accessed': stat.st_atime,
        'is_file': file_path.is_file(),
        'is_dir': file_path.is_dir(),
        'absolute_path': str(file_path.absolute())
    }

def clean_directory(
    directory: Union[str, Path],
    pattern: str = '*',
    recursive: bool = False,
    exclude: Optional[List[str]] = None
) -> None:
    """Clean a directory by removing files matching pattern.
    
    Args:
        directory: Directory to clean
        pattern: Glob pattern for files to remove
        recursive: Whether to clean subdirectories
        exclude: List of patterns to exclude
    """
    directory = Path(directory)
    exclude = exclude or []
    
    for item in directory.glob(pattern):
        if any(item.match(exc) for exc in exclude):
            continue
            
        if item.is_file():
            item.unlink()
        elif item.is_dir() and recursive:
            shutil.rmtree(item)

def create_unique_filename(
    directory: Union[str, Path],
    base_name: str,
    extension: str
) -> Path:
    """Create a unique filename in the specified directory.
    
    Args:
        directory: Target directory
        base_name: Base filename
        extension: File extension
    
    Returns:
        Path object with unique filename
    """
    directory = Path(directory)
    counter = 1
    
    while True:
        if counter == 1:
            file_path = directory / f"{base_name}{extension}"
        else:
            file_path = directory / f"{base_name}_{counter}{extension}"
            
        if not file_path.exists():
            return file_path
            
        counter += 1 