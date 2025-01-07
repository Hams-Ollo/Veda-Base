"""Document processor agent for handling document processing tasks."""

from typing import Dict, Any, Optional
import logging
import uuid
from datetime import datetime

from app.core.agents.base import BaseAgent, Message
from app.core.document.processor import DocumentProcessor
from app.core.knowledge.graph import KnowledgeGraph, Entity, Relationship
from app.core.knowledge.taxonomy import TaxonomyManager, Category, Tag
from app.utils.performance_utils import track_performance, monitor

logger = logging.getLogger(__name__)

class DocumentProcessorAgent(BaseAgent):
    """Agent responsible for document processing and knowledge extraction."""
    
    def __init__(self, knowledge_graph: KnowledgeGraph, taxonomy: TaxonomyManager):
        super().__init__(
            agent_id=f"doc_processor_{uuid.uuid4().hex[:8]}",
            name="Document Processor Agent"
        )
        self.processor = DocumentProcessor()
        self.knowledge_graph = knowledge_graph
        self.taxonomy = taxonomy
        
        # Register message handlers
        self.register_handler("process_document", self.handle_process_document)
        self.register_handler("extract_knowledge", self.handle_extract_knowledge)
        self.register_handler("suggest_tags", self.handle_suggest_tags)
    
    async def initialize(self):
        """Initialize the agent."""
        logger.info(f"Initializing {self.name}")
        # Any additional initialization can go here
    
    async def shutdown(self):
        """Cleanup and shutdown."""
        logger.info(f"Shutting down {self.name}")
        # Any cleanup can go here
    
    @track_performance("process_document")
    async def handle_process_document(self, message: Message):
        """Handle document processing request."""
        try:
            content = message.content
            file_path = content["file_path"]
            batch_id = content.get("batch_id")
            
            # Process the document
            result = await self.processor.process_single_file(file_path, batch_id)
            
            if result["success"]:
                # Extract knowledge and create entities
                await self.extract_and_store_knowledge(result)
                
                # Suggest and apply tags
                await self.suggest_and_apply_tags(result)
            
            # Send response
            await self.send_message(
                content={
                    "success": result["success"],
                    "file_path": str(file_path),
                    "processing_time": result.get("processing_time"),
                    "error": result.get("error")
                },
                msg_type="document_processed",
                recipient=message.sender,
                correlation_id=message.correlation_id
            )
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            await self.send_message(
                content={"error": str(e)},
                msg_type="error",
                recipient=message.sender,
                correlation_id=message.correlation_id
            )
    
    @track_performance("extract_knowledge")
    async def handle_extract_knowledge(self, message: Message):
        """Handle knowledge extraction request."""
        try:
            content = message.content
            doc_content = content["content"]
            doc_id = content["doc_id"]
            
            # Extract entities and relationships
            entities = await self._extract_entities(doc_content)
            relationships = await self._extract_relationships(entities)
            
            # Store in knowledge graph
            for entity in entities:
                await self.knowledge_graph.add_entity(entity)
            
            for rel in relationships:
                await self.knowledge_graph.add_relationship(rel)
            
            # Send response
            await self.send_message(
                content={
                    "success": True,
                    "doc_id": doc_id,
                    "num_entities": len(entities),
                    "num_relationships": len(relationships)
                },
                msg_type="knowledge_extracted",
                recipient=message.sender,
                correlation_id=message.correlation_id
            )
            
        except Exception as e:
            logger.error(f"Error extracting knowledge: {str(e)}")
            await self.send_message(
                content={"error": str(e)},
                msg_type="error",
                recipient=message.sender,
                correlation_id=message.correlation_id
            )
    
    @track_performance("suggest_tags")
    async def handle_suggest_tags(self, message: Message):
        """Handle tag suggestion request."""
        try:
            content = message.content
            doc_content = content["content"]
            doc_id = content["doc_id"]
            
            # Generate tag suggestions
            suggested_tags = await self._suggest_tags(doc_content)
            
            # Apply tags if requested
            if content.get("auto_apply", False):
                await self.taxonomy.tag_content(doc_id, suggested_tags)
            
            # Send response
            await self.send_message(
                content={
                    "success": True,
                    "doc_id": doc_id,
                    "suggested_tags": suggested_tags
                },
                msg_type="tags_suggested",
                recipient=message.sender,
                correlation_id=message.correlation_id
            )
            
        except Exception as e:
            logger.error(f"Error suggesting tags: {str(e)}")
            await self.send_message(
                content={"error": str(e)},
                msg_type="error",
                recipient=message.sender,
                correlation_id=message.correlation_id
            )
    
    async def _extract_entities(self, content: Dict[str, Any]) -> list[Entity]:
        """Extract entities from document content."""
        entities = []
        
        # Extract concepts and terms
        if "text_content" in content:
            # Add document as entity
            doc_entity = Entity(
                id=f"doc_{uuid.uuid4().hex}",
                type="document",
                name=content.get("title", "Untitled Document"),
                attributes={
                    "content_type": content.get("type", "unknown"),
                    "created_at": datetime.utcnow().isoformat()
                }
            )
            entities.append(doc_entity)
            
            # TODO: Add more sophisticated entity extraction
            # This is a placeholder for demonstration
        
        return entities
    
    async def _extract_relationships(self, entities: list[Entity]) -> list[Relationship]:
        """Extract relationships between entities."""
        relationships = []
        
        # TODO: Add relationship extraction logic
        # This is a placeholder for demonstration
        
        return relationships
    
    async def _suggest_tags(self, content: Dict[str, Any]) -> list[str]:
        """Generate tag suggestions for document content."""
        suggested_tags = []
        
        # TODO: Add tag suggestion logic
        # This is a placeholder for demonstration
        
        return suggested_tags
    
    async def extract_and_store_knowledge(self, processing_result: Dict[str, Any]):
        """Extract and store knowledge from processing result."""
        if not processing_result.get("content"):
            return
        
        entities = await self._extract_entities(processing_result["content"])
        relationships = await self._extract_relationships(entities)
        
        # Store in knowledge graph
        for entity in entities:
            await self.knowledge_graph.add_entity(entity)
        
        for relationship in relationships:
            await self.knowledge_graph.add_relationship(relationship)
    
    async def suggest_and_apply_tags(self, processing_result: Dict[str, Any]):
        """Suggest and apply tags to processed document."""
        if not processing_result.get("content"):
            return
        
        doc_id = processing_result.get("file_path")
        if not doc_id:
            return
        
        suggested_tags = await self._suggest_tags(processing_result["content"])
        if suggested_tags:
            await self.taxonomy.tag_content(str(doc_id), suggested_tags)