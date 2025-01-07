"""Taxonomy Master Agent for managing content classification and categorization."""

import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import asyncio
import json

from .base import BaseAgent, AgentMessage, MessageType, Priority, TaskStatus

logger = logging.getLogger(__name__)

class TaxonomyLevel(Enum):
    """Levels in the taxonomy hierarchy."""
    DOMAIN = "domain"
    CATEGORY = "category"
    SUBCATEGORY = "subcategory"
    TAG = "tag"

class TagType(Enum):
    """Types of tags in the taxonomy."""
    TOPIC = "topic"
    CONCEPT = "concept"
    SKILL = "skill"
    TECHNOLOGY = "technology"
    METHOD = "method"
    TOOL = "tool"
    DOMAIN_SPECIFIC = "domain_specific"

@dataclass
class TaxonomyNode:
    """Represents a node in the taxonomy tree."""
    node_id: str
    name: str
    level: TaxonomyLevel
    parent_id: Optional[str]
    children: Set[str]
    properties: Dict
    metadata: Dict
    created_at: str
    updated_at: str

@dataclass
class Tag:
    """Represents a tag in the taxonomy."""
    tag_id: str
    name: str
    tag_type: TagType
    category_id: str
    aliases: Set[str]
    properties: Dict
    metadata: Dict
    created_at: str
    updated_at: str

class TaxonomyMaster(BaseAgent):
    """Agent responsible for managing the taxonomy system."""

    def __init__(self, agent_id: str):
        """Initialize the taxonomy master agent."""
        super().__init__(agent_id)
        self._taxonomy_nodes: Dict[str, TaxonomyNode] = {}
        self._tags: Dict[str, Tag] = {}
        self._tag_index: Dict[str, Set[str]] = {}  # name/alias -> set of tag_ids
        self._setup_handlers()

    def _setup_handlers(self):
        """Set up message handlers for different message types."""
        self.register_handler(MessageType.TAXONOMY_QUERY, self._handle_taxonomy_query)
        self.register_handler(MessageType.TAXONOMY_UPDATE, self._handle_taxonomy_update)
        self.register_handler(MessageType.TAG_SUGGESTION, self._handle_tag_suggestion)
        self.register_handler(MessageType.TAG_VALIDATION, self._handle_tag_validation)

    async def _handle_taxonomy_query(self, message: AgentMessage) -> None:
        """Handle taxonomy query requests."""
        try:
            query = message.content.get('query', {})
            if not query:
                await self._send_error_response(message, "No query provided")
                return

            results = await self._query_taxonomy(query)
            
            response = AgentMessage(
                message_type=MessageType.TAXONOMY_RESULT,
                sender=self.agent_id,
                receiver=message.sender,
                content={
                    'results': results,
                    'query': query
                },
                priority=Priority.NORMAL,
                parent_message_id=message.message_id
            )
            
            await self.send_message(response)
            
        except Exception as e:
            logger.error(f"Error in taxonomy query: {e}")
            await self._send_error_response(message, str(e))

    async def _handle_taxonomy_update(self, message: AgentMessage) -> None:
        """Handle taxonomy update requests."""
        try:
            updates = message.content.get('updates', [])
            if not updates:
                await self._send_error_response(message, "No updates provided")
                return

            results = await self._apply_updates(updates)
            
            response = AgentMessage(
                message_type=MessageType.UPDATE_CONFIRMATION,
                sender=self.agent_id,
                receiver=message.sender,
                content={
                    'status': 'success',
                    'results': results
                },
                priority=Priority.NORMAL,
                parent_message_id=message.message_id
            )
            
            await self.send_message(response)
            
        except Exception as e:
            logger.error(f"Error in taxonomy update: {e}")
            await self._send_error_response(message, str(e))

    async def _handle_tag_suggestion(self, message: AgentMessage) -> None:
        """Handle tag suggestion requests."""
        try:
            content = message.content.get('content', '')
            context = message.content.get('context', {})
            
            if not content:
                await self._send_error_response(message, "No content provided")
                return

            suggestions = await self._suggest_tags(content, context)
            
            response = AgentMessage(
                message_type=MessageType.TAG_SUGGESTIONS,
                sender=self.agent_id,
                receiver=message.sender,
                content={
                    'suggestions': suggestions,
                    'context': context
                },
                priority=Priority.NORMAL,
                parent_message_id=message.message_id
            )
            
            await self.send_message(response)
            
        except Exception as e:
            logger.error(f"Error in tag suggestion: {e}")
            await self._send_error_response(message, str(e))

    async def _handle_tag_validation(self, message: AgentMessage) -> None:
        """Handle tag validation requests."""
        try:
            tags = message.content.get('tags', [])
            context = message.content.get('context', {})
            
            if not tags:
                await self._send_error_response(message, "No tags provided")
                return

            validation_results = await self._validate_tags(tags, context)
            
            response = AgentMessage(
                message_type=MessageType.TAG_VALIDATION_RESULT,
                sender=self.agent_id,
                receiver=message.sender,
                content={
                    'results': validation_results,
                    'context': context
                },
                priority=Priority.NORMAL,
                parent_message_id=message.message_id
            )
            
            await self.send_message(response)
            
        except Exception as e:
            logger.error(f"Error in tag validation: {e}")
            await self._send_error_response(message, str(e))

    async def _query_taxonomy(self, query: Dict) -> Dict:
        """Execute a query on the taxonomy."""
        # TODO: Implement taxonomy querying logic
        return {
            'nodes': [],
            'tags': [],
            'metadata': {}
        }

    async def _apply_updates(self, updates: List[Dict]) -> Dict:
        """Apply updates to the taxonomy."""
        results = {
            'nodes_added': 0,
            'nodes_updated': 0,
            'tags_added': 0,
            'tags_updated': 0
        }
        
        for update in updates:
            update_type = update.get('type')
            if update_type == 'add_node':
                await self._add_taxonomy_node(update.get('data', {}))
                results['nodes_added'] += 1
            elif update_type == 'update_node':
                await self._update_taxonomy_node(update.get('data', {}))
                results['nodes_updated'] += 1
            elif update_type == 'add_tag':
                await self._add_tag(update.get('data', {}))
                results['tags_added'] += 1
            elif update_type == 'update_tag':
                await self._update_tag(update.get('data', {}))
                results['tags_updated'] += 1
        
        return results

    async def _suggest_tags(self, content: str, context: Dict) -> List[Dict]:
        """Suggest tags for content based on context."""
        # TODO: Implement tag suggestion logic
        return []

    async def _validate_tags(self, tags: List[str], context: Dict) -> Dict:
        """Validate a list of tags against the taxonomy."""
        # TODO: Implement tag validation logic
        return {
            'valid_tags': [],
            'invalid_tags': [],
            'suggested_alternatives': {}
        }

    async def _add_taxonomy_node(self, node_data: Dict) -> None:
        """Add a new node to the taxonomy."""
        node_id = node_data.get('node_id')
        if not node_id:
            raise ValueError("Node ID is required")
        
        self._taxonomy_nodes[node_id] = TaxonomyNode(
            node_id=node_id,
            name=node_data.get('name', ''),
            level=TaxonomyLevel(node_data.get('level')),
            parent_id=node_data.get('parent_id'),
            children=set(),
            properties=node_data.get('properties', {}),
            metadata=node_data.get('metadata', {}),
            created_at=node_data.get('created_at', ''),
            updated_at=node_data.get('updated_at', '')
        )
        
        if parent_id := node_data.get('parent_id'):
            if parent_id in self._taxonomy_nodes:
                self._taxonomy_nodes[parent_id].children.add(node_id)

    async def _update_taxonomy_node(self, node_data: Dict) -> None:
        """Update an existing taxonomy node."""
        node_id = node_data.get('node_id')
        if not node_id or node_id not in self._taxonomy_nodes:
            raise ValueError(f"Invalid node ID: {node_id}")
        
        node = self._taxonomy_nodes[node_id]
        node.name = node_data.get('name', node.name)
        node.properties.update(node_data.get('properties', {}))
        node.metadata.update(node_data.get('metadata', {}))
        node.updated_at = node_data.get('updated_at', '')

    async def _add_tag(self, tag_data: Dict) -> None:
        """Add a new tag to the taxonomy."""
        tag_id = tag_data.get('tag_id')
        if not tag_id:
            raise ValueError("Tag ID is required")
        
        name = tag_data.get('name', '')
        aliases = set(tag_data.get('aliases', []))
        
        self._tags[tag_id] = Tag(
            tag_id=tag_id,
            name=name,
            tag_type=TagType(tag_data.get('tag_type')),
            category_id=tag_data.get('category_id', ''),
            aliases=aliases,
            properties=tag_data.get('properties', {}),
            metadata=tag_data.get('metadata', {}),
            created_at=tag_data.get('created_at', ''),
            updated_at=tag_data.get('updated_at', '')
        )
        
        # Update tag index
        self._tag_index.setdefault(name.lower(), set()).add(tag_id)
        for alias in aliases:
            self._tag_index.setdefault(alias.lower(), set()).add(tag_id)

    async def _update_tag(self, tag_data: Dict) -> None:
        """Update an existing tag."""
        tag_id = tag_data.get('tag_id')
        if not tag_id or tag_id not in self._tags:
            raise ValueError(f"Invalid tag ID: {tag_id}")
        
        tag = self._tags[tag_id]
        
        # Remove old index entries
        if 'name' in tag_data:
            self._tag_index[tag.name.lower()].discard(tag_id)
        if 'aliases' in tag_data:
            for alias in tag.aliases:
                self._tag_index[alias.lower()].discard(tag_id)
        
        # Update tag
        if 'name' in tag_data:
            tag.name = tag_data['name']
            self._tag_index.setdefault(tag.name.lower(), set()).add(tag_id)
        if 'aliases' in tag_data:
            tag.aliases = set(tag_data['aliases'])
            for alias in tag.aliases:
                self._tag_index.setdefault(alias.lower(), set()).add(tag_id)
        
        tag.properties.update(tag_data.get('properties', {}))
        tag.metadata.update(tag_data.get('metadata', {}))
        tag.updated_at = tag_data.get('updated_at', '')

    async def _send_error_response(self, original_message: AgentMessage, error_message: str) -> None:
        """Send an error response message."""
        error_response = AgentMessage(
            message_type=MessageType.ERROR,
            sender=self.agent_id,
            receiver=original_message.sender,
            content={'error': error_message},
            priority=Priority.HIGH,
            parent_message_id=original_message.message_id
        )
        await self.send_message(error_response)

    @property
    def capabilities(self) -> List[str]:
        """Get the list of agent capabilities."""
        return [
            "taxonomy_management",
            "tag_suggestion",
            "tag_validation",
            "classification",
            "categorization"
        ] 