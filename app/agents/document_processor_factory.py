"""Factory for creating and managing document processor agents."""

import logging
from typing import Dict, Optional, List
from .document_processor import DocumentProcessor
from .message_bus import MessageBus

logger = logging.getLogger(__name__)

class DocumentProcessorFactory:
    """Factory class for creating and managing document processor agents."""

    def __init__(self, message_bus: MessageBus):
        """Initialize the factory with a message bus."""
        self.message_bus = message_bus
        self._processors: Dict[str, DocumentProcessor] = {}
        self._processor_counter: int = 0

    def create_processor(self) -> DocumentProcessor:
        """Create a new document processor agent."""
        self._processor_counter += 1
        agent_id = f"processor_{self._processor_counter}"
        
        processor = DocumentProcessor(agent_id)
        self._processors[agent_id] = processor
        
        # Register with message bus
        self.message_bus.register_agent(processor)
        logger.info(f"Created new document processor: {agent_id}")
        
        return processor

    def get_processor(self, agent_id: str) -> Optional[DocumentProcessor]:
        """Get a processor by agent ID."""
        return self._processors.get(agent_id)

    def get_least_busy_processor(self) -> Optional[DocumentProcessor]:
        """Get the processor with the least active processes."""
        if not self._processors:
            return None

        return min(
            self._processors.values(),
            key=lambda p: len(p.active_processes)
        )

    def remove_processor(self, agent_id: str) -> bool:
        """Remove a processor from the factory."""
        if agent_id not in self._processors:
            return False

        processor = self._processors[agent_id]
        if processor.active_processes:
            logger.warning(f"Removing processor {agent_id} with active processes")

        self.message_bus.unregister_agent(processor)
        del self._processors[agent_id]
        logger.info(f"Removed document processor: {agent_id}")
        
        return True

    @property
    def active_processors(self) -> List[str]:
        """Get list of active processor agent IDs."""
        return list(self._processors.keys())

    @property
    def total_active_processes(self) -> int:
        """Get total number of active processes across all processors."""
        return sum(
            len(processor.active_processes)
            for processor in self._processors.values()
        )

    def get_processor_load(self) -> Dict[str, int]:
        """Get the number of active processes for each processor."""
        return {
            agent_id: len(processor.active_processes)
            for agent_id, processor in self._processors.items()
        } 