"""Markdown document extraction with metadata support."""

from pathlib import Path
from typing import Dict, Any
import markdown
import frontmatter
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class MarkdownExtractor:
    """Handles extraction of content from Markdown documents."""
    
    async def extract(self, file_path: Path) -> Dict[str, Any]:
        """Extract content and metadata from a Markdown document."""
        try:
            # Read the file content
            content = frontmatter.load(file_path)
            
            # Convert markdown to HTML for structured content
            html_content = markdown.markdown(
                content.content,
                extensions=[
                    'extra',
                    'codehilite',
                    'tables',
                    'toc',
                    'fenced_code',
                    'sane_lists'
                ]
            )
            
            # Parse HTML for structure
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract structure
            headings = [
                {
                    "level": int(h.name[1]),
                    "text": h.get_text(),
                    "id": h.get("id", "")
                }
                for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            ]
            
            code_blocks = [
                {
                    "language": block.get("class", [""])[0].replace("language-", "")
                    if block.get("class") else "text",
                    "content": block.get_text()
                }
                for block in soup.find_all("code")
            ]
            
            links = [
                {
                    "text": a.get_text(),
                    "href": a.get("href", "")
                }
                for a in soup.find_all("a")
            ]
            
            return {
                "metadata": dict(content.metadata),
                "content": content.content,
                "html_content": html_content,
                "structure": {
                    "headings": headings,
                    "code_blocks": code_blocks,
                    "links": links
                }
            }
            
        except Exception as e:
            logger.error(f"Markdown extraction error: {str(e)}")
            raise 