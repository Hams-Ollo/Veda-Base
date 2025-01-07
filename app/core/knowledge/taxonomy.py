"""Taxonomy management and categorization."""

from typing import Dict, List, Any, Optional, Set
import logging
from datetime import datetime
from dataclasses import dataclass
import json
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class Category:
    """Represents a category in the taxonomy."""
    id: str
    name: str
    description: str
    parent_id: Optional[str] = None
    attributes: Dict[str, Any] = None
    created_at: str = datetime.utcnow().isoformat()

@dataclass
class Tag:
    """Represents a tag associated with content."""
    id: str
    name: str
    category_id: str
    weight: float = 1.0
    attributes: Dict[str, Any] = None
    created_at: str = datetime.utcnow().isoformat()

class TaxonomyManager:
    """Manages hierarchical categorization and tagging."""
    
    def __init__(self):
        self.categories: Dict[str, Category] = {}
        self.tags: Dict[str, Tag] = {}
        self.category_hierarchy: Dict[str, Set[str]] = defaultdict(set)
        self.content_tags: Dict[str, Set[str]] = defaultdict(set)
    
    async def add_category(self, category: Category) -> str:
        """Add a category to the taxonomy."""
        self.categories[category.id] = category
        if category.parent_id:
            self.category_hierarchy[category.parent_id].add(category.id)
        return category.id
    
    async def add_tag(self, tag: Tag) -> str:
        """Add a tag to the taxonomy."""
        if tag.category_id not in self.categories:
            raise ValueError(f"Category {tag.category_id} does not exist")
        self.tags[tag.id] = tag
        return tag.id
    
    async def tag_content(
        self,
        content_id: str,
        tag_ids: List[str],
        replace: bool = False
    ):
        """Tag content with specified tags."""
        if replace:
            self.content_tags[content_id] = set()
        
        for tag_id in tag_ids:
            if tag_id in self.tags:
                self.content_tags[content_id].add(tag_id)
    
    async def get_content_tags(
        self,
        content_id: str,
        include_categories: bool = False
    ) -> List[Dict[str, Any]]:
        """Get tags for specific content."""
        if content_id not in self.content_tags:
            return []
        
        result = []
        for tag_id in self.content_tags[content_id]:
            tag = self.tags[tag_id]
            tag_info = {
                "id": tag.id,
                "name": tag.name,
                "weight": tag.weight,
                "attributes": tag.attributes
            }
            
            if include_categories:
                category = self.categories[tag.category_id]
                tag_info["category"] = {
                    "id": category.id,
                    "name": category.name,
                    "description": category.description
                }
            
            result.append(tag_info)
        
        return result
    
    async def get_category_tree(
        self,
        root_id: Optional[str] = None,
        include_tags: bool = False
    ) -> Dict[str, Any]:
        """Get hierarchical category structure."""
        def build_tree(category_id: str) -> Dict[str, Any]:
            category = self.categories[category_id]
            tree = {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "attributes": category.attributes,
                "children": []
            }
            
            if include_tags:
                tree["tags"] = [
                    {
                        "id": tag.id,
                        "name": tag.name,
                        "weight": tag.weight
                    }
                    for tag in self.tags.values()
                    if tag.category_id == category_id
                ]
            
            for child_id in self.category_hierarchy[category_id]:
                tree["children"].append(build_tree(child_id))
            
            return tree
        
        if root_id:
            if root_id not in self.categories:
                raise ValueError(f"Category {root_id} does not exist")
            return build_tree(root_id)
        
        # Build forest of all root categories
        return {
            "roots": [
                build_tree(cat_id)
                for cat_id, category in self.categories.items()
                if not category.parent_id
            ]
        }
    
    async def search_tags(
        self,
        query: Dict[str, Any],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search tags based on criteria."""
        results = []
        for tag in self.tags.values():
            match = all(
                hasattr(tag, key) and getattr(tag, key) == value
                for key, value in query.items()
            )
            if match:
                results.append({
                    "id": tag.id,
                    "name": tag.name,
                    "category_id": tag.category_id,
                    "weight": tag.weight,
                    "attributes": tag.attributes
                })
                if len(results) >= limit:
                    break
        return results
    
    async def save(self, file_path: Path):
        """Save the taxonomy to a file."""
        data = {
            "categories": {
                cat_id: vars(category)
                for cat_id, category in self.categories.items()
            },
            "tags": {
                tag_id: vars(tag)
                for tag_id, tag in self.tags.items()
            },
            "category_hierarchy": {
                parent_id: list(children)
                for parent_id, children in self.category_hierarchy.items()
            },
            "content_tags": {
                content_id: list(tags)
                for content_id, tags in self.content_tags.items()
            }
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    async def load(cls, file_path: Path) -> 'TaxonomyManager':
        """Load a taxonomy from a file."""
        with open(file_path) as f:
            data = json.load(f)
        
        manager = cls()
        
        # Restore categories
        for cat_id, cat_data in data["categories"].items():
            manager.categories[cat_id] = Category(**cat_data)
        
        # Restore tags
        for tag_id, tag_data in data["tags"].items():
            manager.tags[tag_id] = Tag(**tag_data)
        
        # Restore hierarchy
        for parent_id, children in data["category_hierarchy"].items():
            manager.category_hierarchy[parent_id] = set(children)
        
        # Restore content tags
        for content_id, tags in data["content_tags"].items():
            manager.content_tags[content_id] = set(tags)
        
        return manager 