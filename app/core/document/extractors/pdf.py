"""PDF document extraction with table detection."""

from pathlib import Path
from typing import Dict, List, Any
import fitz  # PyMuPDF
import camelot
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PDFTable:
    """Represents a table extracted from a PDF."""
    page: int
    content: List[List[str]]
    bbox: tuple  # x1, y1, x2, y2
    confidence: float

class PDFExtractor:
    """Handles extraction of content from PDF documents."""
    
    async def extract(self, file_path: Path) -> Dict[str, Any]:
        """Extract text and tables from a PDF document."""
        try:
            doc = fitz.open(str(file_path))
            
            # Extract text content
            text_content = []
            tables = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text_content.append(page.get_text())
                
                # Extract tables using camelot
                if page.get_text().strip():  # Only process pages with content
                    try:
                        page_tables = camelot.read_pdf(
                            str(file_path),
                            pages=str(page_num + 1),
                            flavor='stream'
                        )
                        
                        for table in page_tables:
                            tables.append(PDFTable(
                                page=page_num,
                                content=table.data,
                                bbox=table._bbox,
                                confidence=table.parsing_report['accuracy']
                            ).__dict__)
                    except Exception as e:
                        logger.warning(f"Table extraction failed for page {page_num + 1}: {str(e)}")
            
            # Extract metadata
            metadata = doc.metadata
            
            return {
                "text_content": text_content,
                "tables": tables,
                "metadata": metadata,
                "total_pages": len(doc),
                "has_tables": len(tables) > 0
            }
            
        except Exception as e:
            logger.error(f"PDF extraction error: {str(e)}")
            raise
        
        finally:
            if 'doc' in locals():
                doc.close() 