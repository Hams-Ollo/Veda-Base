"""Knowledge graph management and operations."""

from typing import Dict, List, Any, Optional, Set
import logging
from datetime import datetime
import networkx as nx
from dataclasses import dataclass
import json
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class Entity:
    """Represents a node in the knowledge graph."""
    id: str
    type: str
    name: str
    attributes: Dict[str, Any]
    source_doc: Optional[str] = None
    created_at: str = datetime.utcnow().isoformat()

@dataclass
class Relationship:
    """Represents an edge in the knowledge graph."""
    source_id: str
    target_id: str
    type: str
    weight: float
    attributes: Dict[str, Any]
    created_at: str = datetime.utcnow().isoformat()

class KnowledgeGraph:
    """Manages the knowledge graph structure and operations."""
    
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.entity_types: Set[str] = set()
        self.relationship_types: Set[str] = set()
    
    async def add_entity(self, entity: Entity) -> str:
        """Add an entity to the graph."""
        self.graph.add_node(
            entity.id,
            type=entity.type,
            name=entity.name,
            attributes=entity.attributes,
            source_doc=entity.source_doc,
            created_at=entity.created_at
        )
        self.entity_types.add(entity.type)
        return entity.id
    
    async def add_relationship(self, relationship: Relationship) -> bool:
        """Add a relationship between entities."""
        if not (self.graph.has_node(relationship.source_id) and 
                self.graph.has_node(relationship.target_id)):
            return False
        
        self.graph.add_edge(
            relationship.source_id,
            relationship.target_id,
            type=relationship.type,
            weight=relationship.weight,
            attributes=relationship.attributes,
            created_at=relationship.created_at
        )
        self.relationship_types.add(relationship.type)
        return True
    
    async def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity details by ID."""
        if not self.graph.has_node(entity_id):
            return None
        return dict(self.graph.nodes[entity_id])
    
    async def get_relationships(
        self,
        entity_id: str,
        relationship_type: Optional[str] = None,
        direction: str = "both"
    ) -> List[Dict[str, Any]]:
        """Get relationships for an entity."""
        relationships = []
        
        if direction in ["out", "both"]:
            out_edges = self.graph.out_edges(entity_id, data=True)
            for source, target, data in out_edges:
                if relationship_type is None or data["type"] == relationship_type:
                    relationships.append({
                        "source_id": source,
                        "target_id": target,
                        **data
                    })
        
        if direction in ["in", "both"]:
            in_edges = self.graph.in_edges(entity_id, data=True)
            for source, target, data in in_edges:
                if relationship_type is None or data["type"] == relationship_type:
                    relationships.append({
                        "source_id": source,
                        "target_id": target,
                        **data
                    })
        
        return relationships
    
    async def search_entities(
        self,
        query: Dict[str, Any],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search entities based on criteria."""
        results = []
        for node_id, data in self.graph.nodes(data=True):
            match = all(
                key in data and data[key] == value
                for key, value in query.items()
            )
            if match:
                results.append({"id": node_id, **data})
                if len(results) >= limit:
                    break
        return results
    
    async def get_subgraph(
        self,
        entity_ids: List[str],
        depth: int = 1
    ) -> Dict[str, Any]:
        """Get a subgraph centered around specified entities."""
        nodes = set(entity_ids)
        for _ in range(depth):
            new_nodes = set()
            for node in nodes:
                neighbors = set(self.graph.predecessors(node))
                neighbors.update(self.graph.successors(node))
                new_nodes.update(neighbors)
            nodes.update(new_nodes)
        
        subgraph = self.graph.subgraph(nodes)
        return {
            "nodes": [
                {"id": node, **data}
                for node, data in subgraph.nodes(data=True)
            ],
            "edges": [
                {
                    "source": source,
                    "target": target,
                    **data
                }
                for source, target, data in subgraph.edges(data=True)
            ]
        }
    
    async def save(self, file_path: Path):
        """Save the knowledge graph to a file."""
        data = nx.node_link_data(self.graph)
        data["entity_types"] = list(self.entity_types)
        data["relationship_types"] = list(self.relationship_types)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    async def load(cls, file_path: Path) -> 'KnowledgeGraph':
        """Load a knowledge graph from a file."""
        with open(file_path) as f:
            data = json.load(f)
        
        graph = cls()
        graph.entity_types = set(data.pop("entity_types", []))
        graph.relationship_types = set(data.pop("relationship_types", []))
        graph.graph = nx.node_link_graph(data)
        return graph 