"""HTML document extraction with structured content support."""

from pathlib import Path
from typing import Dict, Any, List
import logging
from bs4 import BeautifulSoup
import trafilatura

logger = logging.getLogger(__name__)

class HTMLExtractor:
    """Handles extraction of content from HTML documents."""
    
    async def extract(self, file_path: Path) -> Dict[str, Any]:
        """Extract content and structure from an HTML document."""
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract main content using trafilatura for better content extraction
            extracted_text = trafilatura.extract(html_content)
            
            # Extract metadata
            metadata = {
                "title": soup.title.string if soup.title else None,
                "meta_description": soup.find("meta", {"name": "description"})["content"]
                if soup.find("meta", {"name": "description"}) else None,
                "meta_keywords": soup.find("meta", {"name": "keywords"})["content"]
                if soup.find("meta", {"name": "keywords"}) else None
            }
            
            # Extract structure
            structure = {
                "headings": self._extract_headings(soup),
                "links": self._extract_links(soup),
                "images": self._extract_images(soup),
                "tables": self._extract_tables(soup)
            }
            
            return {
                "metadata": metadata,
                "main_content": extracted_text,
                "structure": structure,
                "html_content": html_content
            }
            
        except Exception as e:
            logger.error(f"HTML extraction error: {str(e)}")
            raise
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract hierarchical heading structure."""
        return [
            {
                "level": int(h.name[1]),
                "text": h.get_text(strip=True),
                "id": h.get("id", "")
            }
            for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        ]
    
    def _extract_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract links with text and targets."""
        return [
            {
                "text": a.get_text(strip=True),
                "href": a.get("href", ""),
                "title": a.get("title", ""),
                "is_external": a.get("href", "").startswith(("http", "https"))
            }
            for a in soup.find_all("a")
        ]
    
    def _extract_images(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract image information."""
        return [
            {
                "src": img.get("src", ""),
                "alt": img.get("alt", ""),
                "title": img.get("title", ""),
                "width": img.get("width", ""),
                "height": img.get("height", "")
            }
            for img in soup.find_all("img")
        ]
    
    def _extract_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract table structures."""
        tables = []
        for table in soup.find_all("table"):
            headers = []
            rows = []
            
            # Extract headers
            for th in table.find_all("th"):
                headers.append(th.get_text(strip=True))
            
            # Extract rows
            for tr in table.find_all("tr"):
                row = [td.get_text(strip=True) for td in tr.find_all("td")]
                if row:  # Skip empty rows
                    rows.append(row)
            
            tables.append({
                "headers": headers,
                "rows": rows,
                "caption": table.caption.get_text(strip=True) if table.caption else None
            })
        
        return tables 