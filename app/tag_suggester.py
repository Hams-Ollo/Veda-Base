from typing import List, Dict, Tuple, Set
from .tagging_system import Tag, TagTier, TaggingRules, TagRegistry
from groq import AsyncGroq
from pydantic import BaseModel
import json

class TagSuggestion(BaseModel):
    """Represents a suggested tag with confidence score."""
    name: str
    tier: TagTier
    category: str
    confidence: float
    explanation: str

class TagSuggester:
    """Handles AI-powered tag suggestions using LLM."""
    
    def __init__(self, groq_client: AsyncGroq, tagging_rules: TaggingRules):
        self.groq_client = groq_client
        self.rules = tagging_rules
        self.registry = TagRegistry()

    async def suggest_tags(self, content: str, title: str, source_file: str = None) -> List[TagSuggestion]:
        """Generate tag suggestions for content using LLM and existing tag registry."""
        
        # Create the prompt for the LLM
        prompt = self._create_tagging_prompt(content, title)
        
        # Get LLM response
        response = await self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert knowledge curator and information architect. Your task is to analyze content and suggest highly specific, contextual tags that accurately represent the key concepts, themes, and insights present in the text.

Your suggestions should:
1. Be directly grounded in the content
2. Provide meaningful context and categorization
3. Follow a clear progression from common to legendary tiers
4. Use precise, domain-appropriate terminology
5. Avoid generic or speculative tags"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="mixtral-8x7b-32768",
            temperature=0.3,
            max_tokens=1000
        )

        try:
            # Parse LLM suggestions
            suggestions_data = json.loads(response.choices[0].message.content)
            new_suggestions = self._parse_suggestions(suggestions_data)
            
            # Find similar existing tags
            final_suggestions = []
            for suggestion in new_suggestions:
                similar_tags = self.registry.find_similar_tags(
                    suggestion.explanation,
                    suggestion.tier,
                    suggestion.category,
                    threshold=0.8
                )
                
                if similar_tags:
                    # Use the most similar existing tag
                    best_match, similarity = similar_tags[0]
                    final_suggestions.append(TagSuggestion(
                        name=best_match,
                        tier=suggestion.tier,
                        category=suggestion.category,
                        confidence=similarity,
                        explanation=f"Reusing existing tag (similarity: {similarity:.2f})"
                    ))
                else:
                    # Use the new suggestion
                    final_suggestions.append(suggestion)
                    # Add to registry if source_file is provided
                    if source_file:
                        self.registry.add_tag(
                            suggestion.name,
                            suggestion.explanation,
                            suggestion.tier,
                            suggestion.category,
                            source_file
                        )
            
            return final_suggestions
            
        except json.JSONDecodeError:
            return []

    def get_related_content(self, tags: List[str]) -> Set[str]:
        """Get related content based on tag similarity."""
        return self.registry.get_related_files(tags)

    def _create_tagging_prompt(self, content: str, title: str) -> str:
        """Create a detailed prompt for the LLM."""
        return f"""Analyze the following content and suggest highly specific, contextual tags that accurately represent the key concepts, themes, and insights present in the text.

Title: {title}

Content:
{content}

For each tier, suggest appropriate tags following these rules:

1. ⚪ Common Tags (Basic Categorization):
   - Domain: Primary field/discipline (e.g., computer-science, history, psychology)
   - Era: Time period or context (e.g., modern-era, classical-period)
   - Format: Content type (e.g., research-paper, case-study, tutorial)

2. 🟢 Fine Tags (General Themes):
   - Themes: High-level ideas explored in depth
   - Concepts: Key theoretical frameworks discussed
   - Patterns: Recurring models or approaches identified

3. 🔵 Rare Tags (Specific Topics):
   - Topics: Specialized areas covered in detail
   - Terminology: Domain-specific terms used
   - Methods: Specific techniques or methodologies described

4. 🟣 Epic Tags (Insights & Connections):
   - Insights: Key realizations or findings
   - Connections: Cross-disciplinary relationships
   - Innovations: Novel approaches or ideas presented

5. 🟡 Legendary Tags (Core Principles):
   - Principles: Fundamental truths or axioms demonstrated
   - Paradigms: Overarching frameworks or models revealed

Provide your response in the following JSON format:
{{
    "suggestions": [
        {{
            "name": "tag-name",
            "tier": "COMMON|FINE|RARE|EPIC|LEGENDARY",
            "category": "category-name",
            "confidence": 0.0-1.0,
            "explanation": "Brief explanation of why this tag is relevant"
        }}
    ]
}}

CRITICAL GUIDELINES:
1. ONLY suggest tags that are EXPLICITLY present or directly implied in the text
2. Each tag must be specific and unique to this particular content
3. Use precise terminology from the text's domain
4. Ensure confidence scores reflect the strength of evidence in the text
5. Provide clear explanations that reference specific content
6. Use kebab-case format (lowercase-with-hyphens)
7. Keep tags concise but meaningful
8. Ensure higher tier tags (Epic, Legendary) are truly significant insights or principles"""

    def _parse_suggestions(self, suggestions_data: Dict) -> List[TagSuggestion]:
        """Parse and validate LLM suggestions."""
        valid_suggestions = []
        
        for suggestion in suggestions_data.get("suggestions", []):
            try:
                # Validate tier
                tier = TagTier[suggestion["tier"]]
                
                # Validate category exists for this tier
                tier_categories = getattr(self.rules, f"{tier.name.lower()}_categories")
                if suggestion["category"] not in tier_categories:
                    continue
                
                # Create validated suggestion
                valid_suggestions.append(
                    TagSuggestion(
                        name=suggestion["name"],
                        tier=tier,
                        category=suggestion["category"],
                        confidence=float(suggestion["confidence"]),
                        explanation=suggestion["explanation"]
                    )
                )
            except (KeyError, ValueError):
                continue
                
        return valid_suggestions

    def filter_suggestions(
        self, 
        suggestions: List[TagSuggestion], 
        min_confidence: float = 0.7
    ) -> List[TagSuggestion]:
        """Filter suggestions based on confidence threshold."""
        return [s for s in suggestions if s.confidence >= min_confidence] 