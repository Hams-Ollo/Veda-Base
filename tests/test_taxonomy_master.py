"""Tests for the Taxonomy Master agent."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.agents import (
    TaxonomyMaster,
    AgentMessage,
    AgentTask,
    MessageType,
    Priority
)
from app.core import TagRegistry, TaggingRules

@pytest.mark.asyncio
async def test_tag_suggestion(taxonomy_master: TaxonomyMaster):
    """Test tag suggestion capabilities."""
    # Create test suggestion task
    suggestion_task = AgentTask(
        task_id="test-suggest",
        task_type="suggest_tags",
        parameters={
            "content": "Test content for tag suggestion",
            "context": "academic",
            "options": {
                "max_tags": 10,
                "min_confidence": 0.8,
                "include_hierarchy": True
            }
        }
    )

    # Generate tag suggestions
    result = await taxonomy_master._suggest_tags(suggestion_task)

    # Verify suggestion results
    assert result["status"] == "completed"
    assert "tags" in result
    assert "confidence_scores" in result
    assert "hierarchy" in result
    assert len(result["tags"]) <= 10
    assert all(score >= 0.8 for score in result["confidence_scores"])

@pytest.mark.asyncio
async def test_tag_validation(taxonomy_master: TaxonomyMaster):
    """Test tag validation capabilities."""
    # Create test validation task
    validation_task = AgentTask(
        task_id="test-validate",
        task_type="validate_tags",
        parameters={
            "tags": ["test", "example", "validation"],
            "content": "Test content for validation",
            "rules": {
                "check_relevance": True,
                "check_consistency": True,
                "check_hierarchy": True
            }
        }
    )

    # Validate tags
    result = await taxonomy_master._validate_tags(validation_task)

    # Verify validation results
    assert result["status"] == "completed"
    assert "valid_tags" in result
    assert "invalid_tags" in result
    assert "validation_details" in result

@pytest.mark.asyncio
async def test_hierarchy_management(taxonomy_master: TaxonomyMaster):
    """Test tag hierarchy management."""
    # Create test hierarchy task
    hierarchy_task = AgentTask(
        task_id="test-hierarchy",
        task_type="manage_hierarchy",
        parameters={
            "operation": "add_relationship",
            "parent_tag": "parent",
            "child_tag": "child",
            "relationship_type": "is_a"
        }
    )

    # Manage hierarchy
    result = await taxonomy_master._manage_hierarchy(hierarchy_task)

    # Verify hierarchy results
    assert result["status"] == "completed"
    assert "relationship_added" in result
    assert "hierarchy_updated" in result
    assert "validation_status" in result

@pytest.mark.asyncio
async def test_tag_similarity(taxonomy_master: TaxonomyMaster):
    """Test tag similarity assessment."""
    # Create test similarity task
    similarity_task = AgentTask(
        task_id="test-similarity",
        task_type="assess_similarity",
        parameters={
            "tag1": "machine_learning",
            "tag2": "artificial_intelligence",
            "context": "computer_science"
        }
    )

    # Assess similarity
    result = await taxonomy_master._assess_similarity(similarity_task)

    # Verify similarity results
    assert result["status"] == "completed"
    assert "similarity_score" in result
    assert "relationship_type" in result
    assert "confidence" in result

@pytest.mark.asyncio
async def test_ontology_management(taxonomy_master: TaxonomyMaster):
    """Test ontology management capabilities."""
    # Create test ontology task
    ontology_task = AgentTask(
        task_id="test-ontology",
        task_type="manage_ontology",
        parameters={
            "operation": "add_concept",
            "concept": {
                "name": "test_concept",
                "properties": ["prop1", "prop2"],
                "relationships": ["rel1", "rel2"]
            }
        }
    )

    # Manage ontology
    result = await taxonomy_master._manage_ontology(ontology_task)

    # Verify ontology results
    assert result["status"] == "completed"
    assert "concept_added" in result
    assert "ontology_updated" in result
    assert "validation_status" in result

@pytest.mark.asyncio
async def test_error_handling(taxonomy_master: TaxonomyMaster):
    """Test error handling capabilities."""
    # Create test error message
    error_message = AgentMessage(
        message_id="test-error",
        message_type=MessageType.ERROR,
        sender="tag_processor",
        receiver="taxonomy_master",
        content={"error": "Tag processing failed"},
        priority=Priority.HIGH
    )

    # Handle error
    response = await taxonomy_master._handle_error(error_message)

    # Verify error handling
    assert response.message_type == MessageType.RESPONSE
    assert response.sender == "taxonomy_master"
    assert response.content["status"] == "error_handled"
    assert "recovery_action" in response.content 