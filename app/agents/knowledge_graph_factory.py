"""Factory for creating and managing knowledge graph agents."""

import logging
from typing import Dict, Optional, List
from .knowledge_graph import KnowledgeGraph
from .message_bus import MessageBus

logger = logging.getLogger(__name__)

class KnowledgeGraphFactory:
    """Factory class for creating and managing knowledge graph agents."""

    def __init__(self, message_bus: MessageBus):
        """Initialize the factory with a message bus."""
        self.message_bus = message_bus
        self._graphs: Dict[str, KnowledgeGraph] = {}
        self._graph_counter: int = 0

    def create_graph(self) -> KnowledgeGraph:
        """Create a new knowledge graph agent."""
        self._graph_counter += 1
        agent_id = f"graph_{self._graph_counter}"
        
        graph = KnowledgeGraph(agent_id)
        self._graphs[agent_id] = graph
        
        # Register with message bus
        self.message_bus.register_agent(graph)
        logger.info(f"Created new knowledge graph: {agent_id}")
        
        return graph

    def get_graph(self, agent_id: str) -> Optional[KnowledgeGraph]:
        """Get a graph by agent ID."""
        return self._graphs.get(agent_id)

    def get_primary_graph(self) -> Optional[KnowledgeGraph]:
        """Get the primary knowledge graph (first created)."""
        if not self._graphs:
            return None
        return self._graphs[f"graph_1"]

    def remove_graph(self, agent_id: str) -> bool:
        """Remove a graph from the factory."""
        if agent_id not in self._graphs:
            return False

        graph = self._graphs[agent_id]
        self.message_bus.unregister_agent(graph)
        del self._graphs[agent_id]
        logger.info(f"Removed knowledge graph: {agent_id}")
        
        return True

    @property
    def active_graphs(self) -> List[str]:
        """Get list of active graph agent IDs."""
        return list(self._graphs.keys())

    @property
    def graph_stats(self) -> Dict[str, Dict]:
        """Get statistics for all graphs."""
        return {
            agent_id: {
                'nodes': len(graph._nodes),
                'relationships': len(graph._relationships)
            }
            for agent_id, graph in self._graphs.items()
        } 