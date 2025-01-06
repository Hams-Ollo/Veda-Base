"""Document Processor Agent for handling document processing and content extraction."""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio

from .base import BaseAgent, AgentMessage, MessageType, Priority, TaskStatus

logger = logging.getLogger(__name__)

class DocumentType(Enum):
    """Types of documents that can be processed."""
    MARKDOWN = "markdown"
    PDF = "pdf"
    TEXT = "text"
    HTML = "html"
    CODE = "code"
    UNKNOWN = "unknown"

class ProcessingStage(Enum):
    """Stages of document processing."""
    INITIALIZATION = "initialization"
    VALIDATION = "validation"
    EXTRACTION = "extraction"
    ANALYSIS = "analysis"
    ENRICHMENT = "enrichment"
    COMPLETION = "completion"
    ERROR = "error"

@dataclass
class ProcessingContext:
    """Context information for document processing."""
    document_type: DocumentType
    content_length: int
    processing_stage: ProcessingStage
    metadata: Dict
    validation_results: Dict
    extraction_results: Dict
    analysis_results: Dict

class DocumentProcessor(BaseAgent):
    """Agent responsible for processing documents and extracting content."""

    def __init__(self, agent_id: str):
        """Initialize the document processor agent."""
        super().__init__(agent_id)
        self.active_processes: Dict[str, ProcessingContext] = {}
        self._setup_handlers()

    def _setup_handlers(self):
        """Set up message handlers for different message types."""
        self.register_handler(MessageType.DOCUMENT_PROCESS, self._handle_document_process)
        self.register_handler(MessageType.PROCESS_STATUS, self._handle_process_status)
        self.register_handler(MessageType.PROCESS_CANCEL, self._handle_process_cancel)

    async def _handle_document_process(self, message: AgentMessage) -> None:
        """Handle document processing requests."""
        try:
            content = message.content.get('document', '')
            doc_type = DocumentType(message.content.get('type', 'unknown'))
            
            if not content:
                await self._send_error_response(message, "No document content provided")
                return

            process_id = f"process_{message.message_id}"
            context = ProcessingContext(
                document_type=doc_type,
                content_length=len(content),
                processing_stage=ProcessingStage.INITIALIZATION,
                metadata={},
                validation_results={},
                extraction_results={},
                analysis_results={}
            )
            
            self.active_processes[process_id] = context
            
            # Start processing pipeline
            asyncio.create_task(self._process_document(process_id, content, message))
            
            # Send acknowledgment
            response = AgentMessage(
                message_type=MessageType.PROCESS_STATUS,
                sender=self.agent_id,
                receiver=message.sender,
                content={
                    'process_id': process_id,
                    'status': 'initiated',
                    'stage': ProcessingStage.INITIALIZATION.value
                },
                priority=Priority.NORMAL,
                parent_message_id=message.message_id
            )
            
            await self.send_message(response)
            
        except Exception as e:
            logger.error(f"Error in document processing: {e}")
            await self._send_error_response(message, str(e))

    async def _handle_process_status(self, message: AgentMessage) -> None:
        """Handle process status requests."""
        try:
            process_id = message.content.get('process_id', '')
            if not process_id or process_id not in self.active_processes:
                await self._send_error_response(message, f"Invalid process ID: {process_id}")
                return

            context = self.active_processes[process_id]
            response = AgentMessage(
                message_type=MessageType.PROCESS_STATUS,
                sender=self.agent_id,
                receiver=message.sender,
                content={
                    'process_id': process_id,
                    'stage': context.processing_stage.value,
                    'metadata': context.metadata
                },
                priority=Priority.NORMAL,
                parent_message_id=message.message_id
            )
            
            await self.send_message(response)
            
        except Exception as e:
            logger.error(f"Error in process status: {e}")
            await self._send_error_response(message, str(e))

    async def _handle_process_cancel(self, message: AgentMessage) -> None:
        """Handle process cancellation requests."""
        try:
            process_id = message.content.get('process_id', '')
            if not process_id or process_id not in self.active_processes:
                await self._send_error_response(message, f"Invalid process ID: {process_id}")
                return

            del self.active_processes[process_id]
            
            response = AgentMessage(
                message_type=MessageType.PROCESS_STATUS,
                sender=self.agent_id,
                receiver=message.sender,
                content={
                    'process_id': process_id,
                    'status': 'cancelled'
                },
                priority=Priority.HIGH,
                parent_message_id=message.message_id
            )
            
            await self.send_message(response)
            
        except Exception as e:
            logger.error(f"Error in process cancellation: {e}")
            await self._send_error_response(message, str(e))

    async def _process_document(self, process_id: str, content: str, original_message: AgentMessage) -> None:
        """Process a document through the pipeline."""
        try:
            context = self.active_processes[process_id]
            
            # Validation stage
            context.processing_stage = ProcessingStage.VALIDATION
            await self._update_status(process_id, original_message)
            context.validation_results = await self._validate_document(content, context.document_type)
            
            if not context.validation_results.get('is_valid', False):
                await self._send_error_response(
                    original_message,
                    f"Document validation failed: {context.validation_results.get('error', 'Unknown error')}"
                )
                return

            # Extraction stage
            context.processing_stage = ProcessingStage.EXTRACTION
            await self._update_status(process_id, original_message)
            context.extraction_results = await self._extract_content(content, context.document_type)
            
            # Analysis stage
            context.processing_stage = ProcessingStage.ANALYSIS
            await self._update_status(process_id, original_message)
            context.analysis_results = await self._analyze_content(context.extraction_results)
            
            # Enrichment stage
            context.processing_stage = ProcessingStage.ENRICHMENT
            await self._update_status(process_id, original_message)
            enriched_content = await self._enrich_content(context)
            
            # Completion
            context.processing_stage = ProcessingStage.COMPLETION
            completion_message = AgentMessage(
                message_type=MessageType.PROCESS_COMPLETE,
                sender=self.agent_id,
                receiver=original_message.sender,
                content={
                    'process_id': process_id,
                    'result': enriched_content,
                    'metadata': context.metadata
                },
                priority=Priority.NORMAL,
                parent_message_id=original_message.message_id
            )
            
            await self.send_message(completion_message)
            
        except Exception as e:
            logger.error(f"Error in document processing pipeline: {e}")
            context.processing_stage = ProcessingStage.ERROR
            await self._send_error_response(original_message, str(e))
        finally:
            if process_id in self.active_processes:
                del self.active_processes[process_id]

    async def _validate_document(self, content: str, doc_type: DocumentType) -> Dict:
        """Validate document content and structure."""
        # TODO: Implement document validation
        return {
            'is_valid': True,
            'format_check': True,
            'size_check': True,
            'content_check': True
        }

    async def _extract_content(self, content: str, doc_type: DocumentType) -> Dict:
        """Extract structured content from document."""
        # TODO: Implement content extraction
        return {
            'text': content,
            'metadata': {},
            'structure': {}
        }

    async def _analyze_content(self, extracted_content: Dict) -> Dict:
        """Analyze extracted content."""
        # TODO: Implement content analysis
        return {
            'summary': '',
            'key_points': [],
            'entities': [],
            'relationships': []
        }

    async def _enrich_content(self, context: ProcessingContext) -> Dict:
        """Enrich processed content with additional information."""
        # TODO: Implement content enrichment
        return {
            'processed_content': context.extraction_results,
            'analysis': context.analysis_results,
            'metadata': context.metadata,
            'enrichments': {}
        }

    async def _update_status(self, process_id: str, original_message: AgentMessage) -> None:
        """Send status update message."""
        context = self.active_processes[process_id]
        status_message = AgentMessage(
            message_type=MessageType.PROCESS_STATUS,
            sender=self.agent_id,
            receiver=original_message.sender,
            content={
                'process_id': process_id,
                'stage': context.processing_stage.value,
                'metadata': context.metadata
            },
            priority=Priority.LOW,
            parent_message_id=original_message.message_id
        )
        await self.send_message(status_message)

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
            "document_processing",
            "content_extraction",
            "document_validation",
            "content_analysis",
            "content_enrichment"
        ] 