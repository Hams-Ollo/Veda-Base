from enum import Enum
from typing import List, Dict, Set, Optional, Tuple
from pydantic import BaseModel, Field
from dataclasses import dataclass
import re
import json
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class TagTier(Enum):
    """Enumeration of tag tiers with their corresponding symbols."""
    COMMON = "⚪"
    FINE = "🟢"
    RARE = "🔵"
    EPIC = "🟣"
    LEGENDARY = "🟡"

@dataclass
class TagCategory:
    """Represents a category of tags within a tier."""
    name: str
    description: str
    examples: List[str]

class TaggingRules(BaseModel):
    """Defines the controlled vocabulary and rules for each tag tier."""
    common_categories: Dict[str, TagCategory] = Field(default_factory=dict)
    fine_categories: Dict[str, TagCategory] = Field(default_factory=dict)
    rare_categories: Dict[str, TagCategory] = Field(default_factory=dict)
    epic_categories: Dict[str, TagCategory] = Field(default_factory=dict)
    legendary_categories: Dict[str, TagCategory] = Field(default_factory=dict)

    def __init__(self):
        super().__init__()
        self._initialize_categories()

    def _initialize_categories(self):
        """Initialize the predefined tag categories."""
        self.common_categories = {
            "domain": TagCategory("domain", "Primary field or discipline", ["ai", "history", "psychology"]),
            "era": TagCategory("era", "Temporal context or time period", ["renaissance", "21st-century", "prehistoric"]),
            "format": TagCategory("format", "Content type", ["article", "book", "podcast", "dataset"])
        }

        self.fine_categories = {
            "themes": TagCategory("themes", "High-level ideas explored", ["innovation", "ethics", "sustainability"]),
            "concepts": TagCategory("concepts", "Key theoretical frameworks", ["neural-networks", "stoicism", "karma"]),
            "patterns": TagCategory("patterns", "Recurrent ideas or models", ["feedback-loops", "fractals", "dichotomies"])
        }

        self.rare_categories = {
            "topics": TagCategory("topics", "Niche or specialized areas", ["adversarial-attacks", "dharmic-leadership"]),
            "terminology": TagCategory("terminology", "Key terms or jargon", ["rag", "latent-space"]),
            "methods": TagCategory("methods", "Techniques or methodologies", ["lstm-optimization", "shamanic-journeying"])
        }

        self.epic_categories = {
            "insights": TagCategory("insights", "Profound realizations", ["intelligence-emergence"]),
            "connections": TagCategory("connections", "Cross-disciplinary relationships", ["ai-and-zen", "stoicism-in-leadership"]),
            "innovations": TagCategory("innovations", "Groundbreaking ideas", ["multimodal-embeddings", "quantum-computing"])
        }

        self.legendary_categories = {
            "principles": TagCategory("principles", "Universal truths or axioms", ["conservation-of-energy", "dharma", "ockhams-razor"]),
            "paradigms": TagCategory("paradigms", "Foundational frameworks", ["heros-journey", "postmodernism"])
        }

class Tag(BaseModel):
    """Represents a single tag with its metadata."""
    name: str
    tier: TagTier
    category: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

class TaggedContent(BaseModel):
    """Represents content with its associated tags."""
    content_id: str
    title: str
    tags: List[Tag]
    metadata: Dict[str, str] = Field(default_factory=dict)

class TagContext:
    """Represents the context in which a tag is used."""
    tag: str
    explanation: str
    tier: 'TagTier'
    category: str
    usage_count: int = 0
    source_files: Set[str] = None
    embedding: np.ndarray = None

    def __post_init__(self):
        if self.source_files is None:
            self.source_files = set()

class TagRegistry:
    """Manages a persistent registry of tags and their semantic relationships."""
    
    def __init__(self, registry_path: str = ".knowledge_base/tag_registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.tags: Dict[str, TagContext] = {}
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self._load_registry()

    def _load_registry(self):
        """Load existing tag registry from disk."""
        if self.registry_path.exists():
            data = json.loads(self.registry_path.read_text())
            for tag_data in data.values():
                context = TagContext(
                    tag=tag_data["tag"],
                    explanation=tag_data["explanation"],
                    tier=TagTier[tag_data["tier"]],
                    category=tag_data["category"],
                    usage_count=tag_data["usage_count"],
                    source_files=set(tag_data["source_files"])
                )
                if tag_data.get("embedding") is not None:
                    context.embedding = np.array(tag_data["embedding"])
                self.tags[context.tag] = context

    def _save_registry(self):
        """Save current tag registry to disk."""
        data = {}
        for tag, context in self.tags.items():
            data[tag] = {
                "tag": context.tag,
                "explanation": context.explanation,
                "tier": context.tier.name,
                "category": context.category,
                "usage_count": context.usage_count,
                "source_files": list(context.source_files),
                "embedding": context.embedding.tolist() if context.embedding is not None else None
            }
        self.registry_path.write_text(json.dumps(data, indent=2))

    def _compute_embedding(self, text: str) -> np.ndarray:
        """Compute embedding for text using sentence transformer."""
        return self.embedding_model.encode([text])[0]

    def add_tag(self, tag: str, explanation: str, tier: 'TagTier', 
                category: str, source_file: str):
        """Add or update a tag in the registry."""
        if tag not in self.tags:
            context = TagContext(tag=tag, explanation=explanation, 
                               tier=tier, category=category)
            context.embedding = self._compute_embedding(explanation)
            self.tags[tag] = context
        
        self.tags[tag].usage_count += 1
        self.tags[tag].source_files.add(source_file)
        self._save_registry()

    def find_similar_tags(self, explanation: str, tier: 'TagTier', 
                         category: str, threshold: float = 0.8) -> List[Tuple[str, float]]:
        """Find semantically similar existing tags."""
        if not self.tags:
            return []

        query_embedding = self._compute_embedding(explanation)
        
        # Filter tags by tier and category first
        relevant_tags = [
            (tag, context) for tag, context in self.tags.items()
            if context.tier == tier and context.category == category
        ]
        
        if not relevant_tags:
            return []
        
        # Compute similarities
        similarities = []
        for tag, context in relevant_tags:
            if context.embedding is not None:
                similarity = cosine_similarity(
                    [query_embedding], 
                    [context.embedding]
                )[0][0]
                if similarity >= threshold:
                    similarities.append((tag, similarity))
        
        return sorted(similarities, key=lambda x: x[1], reverse=True)

    def get_tag_suggestions(self, content: str, existing_tags: Set[str]) -> List[str]:
        """Get tag suggestions based on content similarity."""
        content_embedding = self._compute_embedding(content)
        
        suggestions = []
        for tag, context in self.tags.items():
            if tag not in existing_tags and context.embedding is not None:
                similarity = cosine_similarity(
                    [content_embedding], 
                    [context.embedding]
                )[0][0]
                if similarity >= 0.8:  # High similarity threshold for suggestions
                    suggestions.append((tag, similarity))
        
        return [tag for tag, _ in sorted(suggestions, key=lambda x: x[1], reverse=True)]

    def get_related_files(self, tags: List[str]) -> Set[str]:
        """Get files that share similar tags."""
        related_files = set()
        for tag in tags:
            if tag in self.tags:
                related_files.update(self.tags[tag].source_files)
        return related_files

class TaggingSystem:
    """Main class for handling the tiered tagging system."""
    def __init__(self):
        self.rules = TaggingRules()
        self.tagged_content: Dict[str, TaggedContent] = {}

    def clean_tag(self, tag: str) -> str:
        """Clean and normalize a tag string."""
        # Remove special characters and convert to lowercase
        tag = re.sub(r'[^\w\s-]', '', tag.lower())
        # Replace spaces with hyphens
        tag = re.sub(r'\s+', '-', tag.strip())
        return tag

    def validate_tag(self, tag: str, tier: TagTier, category: str) -> bool:
        """Validate if a tag follows the rules for its tier and category."""
        cleaned_tag = self.clean_tag(tag)
        
        # Get the appropriate category dictionary based on tier
        tier_categories = getattr(self.rules, f"{tier.name.lower()}_categories")
        
        if category not in tier_categories:
            return False
            
        # For now, just check if it's non-empty and properly formatted
        return bool(cleaned_tag and re.match(r'^[a-z0-9-]+$', cleaned_tag))

    def suggest_tags(self, content: str) -> List[Tag]:
        """Suggest tags for content using AI analysis."""
        # TODO: Implement AI-based tag suggestion using LLM
        # This is a placeholder for the AI implementation
        return []

    def add_tags(self, content_id: str, tags: List[Tag]) -> None:
        """Add tags to a piece of content."""
        if content_id not in self.tagged_content:
            raise ValueError(f"Content ID {content_id} not found")
            
        # Validate and clean each tag before adding
        valid_tags = []
        for tag in tags:
            if self.validate_tag(tag.name, tag.tier, tag.category):
                tag.name = self.clean_tag(tag.name)
                valid_tags.append(tag)
        
        self.tagged_content[content_id].tags.extend(valid_tags)

    def remove_tag(self, content_id: str, tag_name: str) -> None:
        """Remove a tag from a piece of content."""
        if content_id not in self.tagged_content:
            raise ValueError(f"Content ID {content_id} not found")
            
        cleaned_tag = self.clean_tag(tag_name)
        self.tagged_content[content_id].tags = [
            tag for tag in self.tagged_content[content_id].tags 
            if tag.name != cleaned_tag
        ]

    def get_related_content(self, tag: str) -> List[TaggedContent]:
        """Find content related to a specific tag."""
        cleaned_tag = self.clean_tag(tag)
        return [
            content for content in self.tagged_content.values()
            if any(t.name == cleaned_tag for t in content.tags)
        ]

    def get_tag_network(self) -> Dict[str, Set[str]]:
        """Generate a network of tag relationships."""
        network = {}
        for content in self.tagged_content.values():
            tag_names = [tag.name for tag in content.tags]
            for tag in tag_names:
                if tag not in network:
                    network[tag] = set()
                network[tag].update(t for t in tag_names if t != tag)
        return network 