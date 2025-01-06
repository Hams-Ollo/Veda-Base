"""Tests for the Connection Weaver agent."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.agents import (
    ConnectionWeaver,
    AgentMessage,
    AgentTask,
    MessageType,
    Priority
)
from app.core import KnowledgeGraph, RelationshipTypes

@pytest.mark.asyncio
async def test_relationship_mapping(connection_weaver: ConnectionWeaver):
    """Test relationship mapping capabilities."""
    # Create test mapping task
    mapping_task = AgentTask(
        task_id="test-mapping",
        task_type="map_relationships",
        parameters={
            "source_node": "concept_a",
            "target_node": "concept_b",
            "context": "academic",
            "options": {
                "relationship_types": ["is_related_to", "depends_on", "influences"],
                "bidirectional": True,
                "min_confidence": 0.7
            }
        }
    )

    # Map relationships
    result = await connection_weaver._map_relationships(mapping_task)

    # Verify mapping results
    assert result["status"] == "completed"
    assert "relationships" in result
    assert "confidence_scores" in result
    assert "bidirectional_links" in result
    assert all(score >= 0.7 for score in result["confidence_scores"])

@pytest.mark.asyncio
async def test_cluster_identification(connection_weaver: ConnectionWeaver):
    """Test cluster identification capabilities."""
    # Create test cluster task
    cluster_task = AgentTask(
        task_id="test-cluster",
        task_type="identify_clusters",
        parameters={
            "nodes": ["node1", "node2", "node3", "node4"],
            "options": {
                "algorithm": "community_detection",
                "min_cluster_size": 2,
                "max_distance": 0.5
            }
        }
    )

    # Identify clusters
    result = await connection_weaver._identify_clusters(cluster_task)

    # Verify cluster results
    assert result["status"] == "completed"
    assert "clusters" in result
    assert "cluster_metrics" in result
    assert "visualization_data" in result

@pytest.mark.asyncio
async def test_pattern_recognition(connection_weaver: ConnectionWeaver):
    """Test pattern recognition capabilities."""
    # Create test pattern task
    pattern_task = AgentTask(
        task_id="test-pattern",
        task_type="recognize_patterns",
        parameters={
            "graph_segment": {
                "nodes": ["node1", "node2", "node3"],
                "edges": [("node1", "node2"), ("node2", "node3")]
            },
            "pattern_types": ["linear", "circular", "hub_spoke"]
        }
    )

    # Recognize patterns
    result = await connection_weaver._recognize_patterns(pattern_task)

    # Verify pattern results
    assert result["status"] == "completed"
    assert "patterns" in result
    assert "pattern_strengths" in result
    assert "recommendations" in result

@pytest.mark.asyncio
async def test_knowledge_path_finding(connection_weaver: ConnectionWeaver):
    """Test knowledge path finding capabilities."""
    # Create test path task
    path_task = AgentTask(
        task_id="test-path",
        task_type="find_paths",
        parameters={
            "start_node": "concept_a",
            "end_node": "concept_z",
            "options": {
                "max_length": 5,
                "min_confidence": 0.6,
                "path_types": ["direct", "indirect"]
            }
        }
    )

    # Find paths
    result = await connection_weaver._find_paths(path_task)

    # Verify path results
    assert result["status"] == "completed"
    assert "paths" in result
    assert "path_scores" in result
    assert "visualization_data" in result

@pytest.mark.asyncio
async def test_graph_maintenance(connection_weaver: ConnectionWeaver):
    """Test graph maintenance capabilities."""
    # Create test maintenance task
    maintenance_task = AgentTask(
        task_id="test-maintenance",
        task_type="maintain_graph",
        parameters={
            "operation": "prune_edges",
            "criteria": {
                "min_weight": 0.3,
                "max_age": 90,
                "min_usage": 5
            }
        }
    )

    # Maintain graph
    result = await connection_weaver._maintain_graph(maintenance_task)

    # Verify maintenance results
    assert result["status"] == "completed"
    assert "pruned_edges" in result
    assert "graph_metrics" in result
    assert "health_status" in result

@pytest.mark.asyncio
async def test_error_handling(connection_weaver: ConnectionWeaver):
    """Test error handling capabilities."""
    # Create test error message
    error_message = AgentMessage(
        message_id="test-error",
        message_type=MessageType.ERROR,
        sender="graph_processor",
        receiver="connection_weaver",
        content={"error": "Graph operation failed"},
        priority=Priority.HIGH
    )

    # Handle error
    response = await connection_weaver._handle_error(error_message)

    # Verify error handling
    assert response.message_type == MessageType.RESPONSE
    assert response.sender == "connection_weaver"
    assert response.content["status"] == "error_handled"
    assert "recovery_action" in response.content 