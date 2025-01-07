"""Factory for creating and managing domain specialist agents."""

import logging
from typing import Dict, Optional, List
from .domain_specialist import DomainSpecialist, DomainType
from .message_bus import MessageBus

logger = logging.getLogger(__name__)

class DomainSpecialistFactory:
    """Factory class for creating and managing domain specialist agents."""

    def __init__(self, message_bus: MessageBus):
        """Initialize the factory with a message bus."""
        self.message_bus = message_bus
        self._specialists: Dict[str, DomainSpecialist] = {}
        self._domain_counters: Dict[DomainType, int] = {
            domain_type: 0 for domain_type in DomainType
        }

    def create_specialist(self, domain_type: DomainType) -> DomainSpecialist:
        """Create a new domain specialist agent."""
        self._domain_counters[domain_type] += 1
        agent_id = f"specialist_{domain_type.value}_{self._domain_counters[domain_type]}"
        
        specialist = DomainSpecialist(agent_id, domain_type)
        self._specialists[agent_id] = specialist
        
        # Register with message bus
        self.message_bus.register_agent(specialist)
        logger.info(f"Created new domain specialist: {agent_id}")
        
        return specialist

    def get_specialist(self, agent_id: str) -> Optional[DomainSpecialist]:
        """Get a specialist by agent ID."""
        return self._specialists.get(agent_id)

    def get_specialists_by_domain(self, domain_type: DomainType) -> List[DomainSpecialist]:
        """Get all specialists of a specific domain type."""
        return [
            specialist for specialist in self._specialists.values()
            if specialist.domain_type == domain_type
        ]

    def remove_specialist(self, agent_id: str) -> bool:
        """Remove a specialist from the factory."""
        if agent_id not in self._specialists:
            return False

        specialist = self._specialists[agent_id]
        self.message_bus.unregister_agent(specialist)
        del self._specialists[agent_id]
        logger.info(f"Removed domain specialist: {agent_id}")
        
        return True

    @property
    def active_specialists(self) -> List[str]:
        """Get list of active specialist agent IDs."""
        return list(self._specialists.keys())

    @property
    def specialist_count(self) -> Dict[DomainType, int]:
        """Get count of specialists by domain type."""
        counts = {domain_type: 0 for domain_type in DomainType}
        for specialist in self._specialists.values():
            counts[specialist.domain_type] += 1
        return counts 