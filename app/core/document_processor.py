"""Document processor implementation for handling various document types."""

import fitz  # PyMuPDF
import logging
from typing import Dict, List, Optional, BinaryIO, Set
from dataclasses import dataclass
from enum import Enum
import asyncio
from pathlib import Path
import tempfile
import os
import json
from datetime import datetime
import markdown
from bs4 import BeautifulSoup
import camelot  # For PDF table extraction
from concurrent.futures import ThreadPoolExecutor
import shutil
import hashlib
import aiofiles

logger = logging.getLogger(__name__)

class DocumentType(Enum):
    """Types of documents that can be processed."""
    PDF = "pdf"
    MARKDOWN = "markdown"
    TEXT = "text"
    HTML = "html"
    CODE = "code"
    UNKNOWN = "unknown"

@dataclass
class ProcessingStats:
    """Statistics for document processing."""
    total_documents: int = 0
    processed_documents: int = 0
    failed_documents: int = 0
    total_pages: int = 0
    processing_time: float = 0.0
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

@dataclass
class BatchProcessingStatus:
    """Status of batch document processing."""
    batch_id: str
    total_files: int
    processed_files: int = 0
    success_count: int = 0
    error_count: int = 0
    current_file: Optional[str] = None
    status: str = 'pending'  # pending, processing, completed, error
    errors: List[Dict[str, str]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class DocumentProcessor:
    """Handles document processing and content extraction."""

    def __init__(self, max_workers: int = 4, chunk_size: int = 1024*1024):
        """Initialize the document processor."""
        self.max_workers = max_workers
        self.chunk_size = chunk_size
        self.stats = ProcessingStats()
        self._processing_tasks = {}
        self._cleanup_tasks = set()
        self._temp_dirs: Set[Path] = set()
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._batch_statuses: Dict[str, BatchProcessingStatus] = {}

    async def process_document(self, file_path: Path) -> Dict:
        """Process a single document."""
        try:
            doc_type = self._determine_document_type(file_path)
            
            # Validate document
            validation_result = await self._validate_document(file_path, doc_type)
            if not validation_result['is_valid']:
                raise ValueError(f"Document validation failed: {validation_result['error']}")

            # Extract content based on document type
            content = await self._extract_content(file_path, doc_type)

            # Extract metadata
            metadata = await self._extract_metadata(file_path, doc_type)

            return {
                'content': content,
                'metadata': metadata,
                'doc_type': doc_type.value,
                'validation': validation_result
            }

        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            self.stats.failed_documents += 1
            self.stats.errors.append(f"{file_path}: {str(e)}")
            raise

    async def _validate_document(self, file_path: Path, doc_type: DocumentType) -> Dict:
        """Validate document before processing."""
        try:
            if not file_path.exists():
                return {'is_valid': False, 'error': 'File does not exist'}

            # Check file size
            file_size = file_path.stat().st_size
            if file_size == 0:
                return {'is_valid': False, 'error': 'File is empty'}

            # Validate based on document type
            if doc_type == DocumentType.PDF:
                return await self._validate_pdf(file_path)
            # TODO: Add validation for other document types

            return {'is_valid': True}

        except Exception as e:
            return {'is_valid': False, 'error': str(e)}

    async def _validate_pdf(self, file_path: Path) -> Dict:
        """Validate PDF document."""
        try:
            doc = fitz.open(file_path)
            if doc.is_encrypted:
                return {'is_valid': False, 'error': 'PDF is encrypted'}
            if doc.page_count == 0:
                return {'is_valid': False, 'error': 'PDF has no pages'}
            
            # Basic structure validation
            toc = doc.get_toc()
            metadata = doc.metadata
            
            return {
                'is_valid': True,
                'pages': doc.page_count,
                'has_toc': len(toc) > 0,
                'has_metadata': bool(metadata)
            }

        except Exception as e:
            return {'is_valid': False, 'error': f'PDF validation failed: {str(e)}'}

    async def _extract_pdf_content(self, file_path: Path) -> Dict:
        """Extract content from PDF document."""
        doc = fitz.open(file_path)
        content = {
            'pages': [],
            'text': '',
            'images': [],
            'tables': [],
            'metadata': {}
        }

        try:
            # Extract metadata
            content['metadata'] = doc.metadata

            # Process each page
            for page_num in range(doc.page_count):
                page = doc[page_num]
                page_content = {
                    'number': page_num + 1,
                    'text': page.get_text(),
                    'images': [],
                    'tables': []
                }

                # Extract images
                for img_index, img in enumerate(page.get_images(full=True)):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    if base_image:
                        image_info = {
                            'index': img_index,
                            'width': base_image['width'],
                            'height': base_image['height'],
                            'format': base_image['ext']
                        }
                        page_content['images'].append(image_info)
                
                content['pages'].append(page_content)
                content['text'] += page_content['text'] + "\n\n"
                content['images'].extend(page_content['images'])

            # Extract tables using camelot
            content['tables'] = await self._extract_pdf_tables(file_path)

            return content

        finally:
            doc.close()

    async def _extract_metadata(self, file_path: Path, doc_type: DocumentType) -> Dict:
        """Extract metadata from document."""
        metadata = {
            'filename': file_path.name,
            'file_size': file_path.stat().st_size,
            'created_time': datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
            'modified_time': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            'doc_type': doc_type.value
        }

        if doc_type == DocumentType.PDF:
            doc = fitz.open(file_path)
            try:
                pdf_metadata = doc.metadata
                metadata.update({
                    'title': pdf_metadata.get('title', ''),
                    'author': pdf_metadata.get('author', ''),
                    'subject': pdf_metadata.get('subject', ''),
                    'keywords': pdf_metadata.get('keywords', ''),
                    'page_count': doc.page_count
                })
            finally:
                doc.close()

        return metadata

    def _determine_document_type(self, file_path: Path) -> DocumentType:
        """Determine document type from file extension and content."""
        extension = file_path.suffix.lower()
        if extension == '.pdf':
            return DocumentType.PDF
        elif extension in ['.md', '.markdown']:
            return DocumentType.MARKDOWN
        elif extension in ['.txt', '.text']:
            return DocumentType.TEXT
        elif extension in ['.html', '.htm']:
            return DocumentType.HTML
        elif extension in ['.py', '.js', '.java', '.cpp']:
            return DocumentType.CODE
        return DocumentType.UNKNOWN

    def get_stats(self) -> ProcessingStats:
        """Get current processing statistics."""
        return self.stats

    async def _extract_content(self, file_path: Path, doc_type: DocumentType) -> Dict:
        """Extract content based on document type."""
        if doc_type == DocumentType.PDF:
            return await self._extract_pdf_content(file_path)
        elif doc_type == DocumentType.MARKDOWN:
            return await self._extract_markdown_content(file_path)
        elif doc_type == DocumentType.HTML:
            return await self._extract_html_content(file_path)
        elif doc_type == DocumentType.TEXT:
            return await self._extract_text_content(file_path)
        elif doc_type == DocumentType.CODE:
            return await self._extract_code_content(file_path)
        else:
            raise ValueError(f"Unsupported document type: {doc_type}")

    async def _extract_markdown_content(self, file_path: Path) -> Dict:
        """Extract content from Markdown document."""
        content = {
            'text': '',
            'html': '',
            'headers': [],
            'links': [],
            'code_blocks': []
        }

        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                markdown_text = await f.read()

            # Convert Markdown to HTML
            html = markdown.markdown(markdown_text, extensions=['fenced_code', 'tables'])
            soup = BeautifulSoup(html, 'html.parser')

            # Extract headers
            for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                content['headers'].append({
                    'level': int(header.name[1]),
                    'text': header.get_text()
                })

            # Extract links
            for link in soup.find_all('a'):
                content['links'].append({
                    'text': link.get_text(),
                    'url': link.get('href')
                })

            # Extract code blocks
            for code in soup.find_all('code'):
                content['code_blocks'].append({
                    'language': code.get('class', ['text'])[0],
                    'code': code.get_text()
                })

            content['text'] = markdown_text
            content['html'] = html

            return content

        except Exception as e:
            logger.error(f"Error processing Markdown file {file_path}: {str(e)}")
            raise

    async def _extract_html_content(self, file_path: Path) -> Dict:
        """Extract content from HTML document."""
        content = {
            'text': '',
            'title': '',
            'headers': [],
            'links': [],
            'images': [],
            'tables': []
        }

        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                html_content = await f.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract title
            title_tag = soup.find('title')
            content['title'] = title_tag.get_text() if title_tag else ''

            # Extract headers
            for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                content['headers'].append({
                    'level': int(header.name[1]),
                    'text': header.get_text()
                })

            # Extract links
            for link in soup.find_all('a'):
                content['links'].append({
                    'text': link.get_text(),
                    'url': link.get('href')
                })

            # Extract images
            for img in soup.find_all('img'):
                content['images'].append({
                    'src': img.get('src'),
                    'alt': img.get('alt', ''),
                    'title': img.get('title', '')
                })

            # Extract tables
            for table in soup.find_all('table'):
                table_data = []
                for row in table.find_all('tr'):
                    row_data = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                    table_data.append(row_data)
                content['tables'].append(table_data)

            # Extract text content
            content['text'] = soup.get_text(separator='\n', strip=True)

            return content

        except Exception as e:
            logger.error(f"Error processing HTML file {file_path}: {str(e)}")
            raise

    async def _extract_text_content(self, file_path: Path) -> Dict:
        """Extract content from text document."""
        content = {
            'text': '',
            'lines': [],
            'paragraphs': [],
            'word_count': 0,
            'line_count': 0
        }

        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                text = await f.read()

            # Split into lines and paragraphs
            lines = text.splitlines()
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

            content['text'] = text
            content['lines'] = lines
            content['paragraphs'] = paragraphs
            content['word_count'] = len(text.split())
            content['line_count'] = len(lines)

            return content

        except Exception as e:
            logger.error(f"Error processing text file {file_path}: {str(e)}")
            raise

    async def _extract_code_content(self, file_path: Path) -> Dict:
        """Extract content from code document."""
        content = {
            'text': '',
            'language': '',
            'imports': [],
            'functions': [],
            'classes': [],
            'comments': [],
            'loc': 0  # Lines of code
        }

        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                code = await f.read()

            # Determine language from file extension
            content['language'] = file_path.suffix[1:]  # Remove the dot
            content['text'] = code

            lines = code.splitlines()
            content['loc'] = len([line for line in lines if line.strip()])

            # Basic parsing (can be extended based on language)
            for line in lines:
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    content['imports'].append(line)
                elif line.startswith('def '):
                    content['functions'].append(line)
                elif line.startswith('class '):
                    content['classes'].append(line)
                elif line.startswith('#') or line.startswith('//'):
                    content['comments'].append(line)

            return content

        except Exception as e:
            logger.error(f"Error processing code file {file_path}: {str(e)}")
            raise

    async def _extract_pdf_tables(self, file_path: Path) -> List[Dict]:
        """Extract tables from PDF document using camelot."""
        tables = []
        try:
            # Run table extraction in thread pool to avoid blocking
            def extract_tables():
                return camelot.read_pdf(str(file_path), pages='all')

            pdf_tables = await asyncio.get_event_loop().run_in_executor(
                self._executor, extract_tables
            )

            for idx, table in enumerate(pdf_tables):
                tables.append({
                    'index': idx,
                    'page': table.page,
                    'data': table.data,
                    'shape': table.shape,
                    'accuracy': table.accuracy,
                    'whitespace': table.whitespace
                })

        except Exception as e:
            logger.error(f"Error extracting tables from PDF {file_path}: {str(e)}")

        return tables

    async def cleanup(self):
        """Clean up temporary files and resources."""
        for temp_dir in self._temp_dirs:
            try:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                self._temp_dirs.remove(temp_dir)
            except Exception as e:
                logger.error(f"Error cleaning up temporary directory {temp_dir}: {str(e)}")

        # Shutdown thread pool executor
        self._executor.shutdown(wait=True)

    def _create_temp_dir(self) -> Path:
        """Create a temporary directory for processing."""
        temp_dir = Path(tempfile.mkdtemp())
        self._temp_dirs.add(temp_dir)
        return temp_dir

    async def process_batch(
        self,
        files: List[Path],
        batch_id: str,
        progress_callback: Optional[callable] = None
    ) -> BatchProcessingStatus:
        """Process a batch of documents with progress tracking.
        
        Args:
            files: List of file paths to process
            batch_id: Unique identifier for the batch
            progress_callback: Optional callback function for progress updates
            
        Returns:
            BatchProcessingStatus object
        """
        # Initialize batch status
        status = BatchProcessingStatus(
            batch_id=batch_id,
            total_files=len(files),
            start_time=datetime.utcnow()
        )
        self._batch_statuses[batch_id] = status
        status.status = 'processing'

        # Create temporary directory for batch
        temp_dir = self._create_temp_dir()

        try:
            # Process files concurrently with semaphore to limit concurrency
            semaphore = asyncio.Semaphore(self.max_workers)
            tasks = []

            async def process_with_semaphore(file_path: Path):
                async with semaphore:
                    return await self._process_batch_file(file_path, status, progress_callback)

            for file_path in files:
                task = asyncio.create_task(process_with_semaphore(file_path))
                tasks.append(task)

            # Wait for all tasks to complete
            await asyncio.gather(*tasks)

            # Update final status
            status.status = 'completed'
            status.end_time = datetime.utcnow()

            return status

        except Exception as e:
            logger.error(f"Error processing batch {batch_id}: {str(e)}")
            status.status = 'error'
            status.errors.append({
                'file': 'batch',
                'error': str(e)
            })
            raise

        finally:
            # Cleanup temporary directory
            await self.cleanup()

    async def _process_batch_file(
        self,
        file_path: Path,
        status: BatchProcessingStatus,
        progress_callback: Optional[callable]
    ) -> Dict:
        """Process a single file in a batch."""
        try:
            # Update status
            status.current_file = file_path.name
            if progress_callback:
                await progress_callback(status)

            # Process document
            result = await self.process_document(file_path)

            # Update status
            status.processed_files += 1
            status.success_count += 1
            if progress_callback:
                await progress_callback(status)

            return result

        except Exception as e:
            # Update error status
            status.processed_files += 1
            status.error_count += 1
            status.errors.append({
                'file': str(file_path),
                'error': str(e)
            })
            if progress_callback:
                await progress_callback(status)
            raise

    def get_batch_status(self, batch_id: str) -> Optional[BatchProcessingStatus]:
        """Get the status of a batch processing task."""
        return self._batch_statuses.get(batch_id)

    def get_active_batches(self) -> Dict[str, BatchProcessingStatus]:
        """Get all active batch processing tasks."""
        return {
            batch_id: status
            for batch_id, status in self._batch_statuses.items()
            if status.status == 'processing'
        }

    async def cancel_batch(self, batch_id: str) -> bool:
        """Cancel a batch processing task."""
        if batch_id not in self._batch_statuses:
            return False

        status = self._batch_statuses[batch_id]
        if status.status == 'processing':
            status.status = 'cancelled'
            status.end_time = datetime.utcnow()
            return True

        return False
