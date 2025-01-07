"""Factory for creating and managing taxonomy master agents."""

import logging
from typing import Dict, Optional, List
from .taxonomy_master import TaxonomyMaster
from .message_bus import MessageBus

logger = logging.getLogger(__name__)

class TaxonomyMasterFactory:
    """Factory class for creating and managing taxonomy master agents."""

    def __init__(self, message_bus: MessageBus):
        """Initialize the factory with a message bus."""
        self.message_bus = message_bus
        self._taxonomy_masters: Dict[str, TaxonomyMaster] = {}
        self._master_counter: int = 0

    def create_taxonomy_master(self) -> TaxonomyMaster:
        """Create a new taxonomy master agent."""
        self._master_counter += 1
        agent_id = f"taxonomy_master_{self._master_counter}"
        
        taxonomy_master = TaxonomyMaster(agent_id)
        self._taxonomy_masters[agent_id] = taxonomy_master
        
        # Register with message bus
        self.message_bus.register_agent(taxonomy_master)
        logger.info(f"Created new taxonomy master: {agent_id}")
        
        return taxonomy_master

    def get_taxonomy_master(self, agent_id: str) -> Optional[TaxonomyMaster]:
        """Get a taxonomy master by agent ID."""
        return self._taxonomy_masters.get(agent_id)

    def get_primary_taxonomy_master(self) -> Optional[TaxonomyMaster]:
        """Get the primary taxonomy master (first created)."""
        if not self._taxonomy_masters:
            return None
        return self._taxonomy_masters[f"taxonomy_master_1"]

    def remove_taxonomy_master(self, agent_id: str) -> bool:
        """Remove a taxonomy master from the factory."""
        if agent_id not in self._taxonomy_masters:
            return False

        taxonomy_master = self._taxonomy_masters[agent_id]
        self.message_bus.unregister_agent(taxonomy_master)
        del self._taxonomy_masters[agent_id]
        logger.info(f"Removed taxonomy master: {agent_id}")
        
        return True

    @property
    def active_taxonomy_masters(self) -> List[str]:
        """Get list of active taxonomy master agent IDs."""
        return list(self._taxonomy_masters.keys())

    @property
    def taxonomy_stats(self) -> Dict[str, Dict]:
        """Get statistics for all taxonomy masters."""
        return {
            agent_id: {
                'nodes': len(master._taxonomy_nodes),
                'tags': len(master._tags),
                'indexed_terms': len(master._tag_index)
            }
            for agent_id, master in self._taxonomy_masters.items()
        } 