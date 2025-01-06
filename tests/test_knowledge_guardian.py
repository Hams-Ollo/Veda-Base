"""Tests for the Knowledge Guardian agent."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.agents import (
    KnowledgeGuardian,
    AgentMessage,
    AgentTask,
    MessageType,
    Priority
)
from app.core import ContentValidator, QualityMetrics

@pytest.mark.asyncio
async def test_content_validation(knowledge_guardian: KnowledgeGuardian):
    """Test content validation capabilities."""
    # Create test validation task
    validation_task = AgentTask(
        task_id="test-validation",
        task_type="validate_content",
        parameters={
            "content": "Test content for validation",
            "metadata": {
                "source": "user_submission",
                "timestamp": "2024-01-01T12:00:00Z",
                "author": "test_user"
            },
            "validation_rules": {
                "check_accuracy": True,
                "check_completeness": True,
                "check_consistency": True,
                "check_citations": True
            }
        }
    )

    # Validate content
    result = await knowledge_guardian._validate_content(validation_task)

    # Verify validation results
    assert result["status"] == "completed"
    assert "validation_score" in result
    assert "issues" in result
    assert "recommendations" in result
    assert "validation_details" in result

@pytest.mark.asyncio
async def test_fact_checking(knowledge_guardian: KnowledgeGuardian):
    """Test fact checking capabilities."""
    # Create test fact-checking task
    fact_check_task = AgentTask(
        task_id="test-fact-check",
        task_type="check_facts",
        parameters={
            "statements": [
                "Python was created by Guido van Rossum",
                "The Earth is flat",
                "Water boils at 100 degrees Celsius at sea level"
            ],
            "options": {
                "confidence_threshold": 0.8,
                "require_sources": True,
                "check_context": True
            }
        }
    )

    # Check facts
    result = await knowledge_guardian._check_facts(fact_check_task)

    # Verify fact-checking results
    assert result["status"] == "completed"
    assert "verified_statements" in result
    assert "false_statements" in result
    assert "confidence_scores" in result
    assert "sources" in result

@pytest.mark.asyncio
async def test_duplicate_detection(knowledge_guardian: KnowledgeGuardian):
    """Test duplicate detection capabilities."""
    # Create test duplicate detection task
    duplicate_task = AgentTask(
        task_id="test-duplicate",
        task_type="detect_duplicates",
        parameters={
            "content": "Test content for duplicate detection",
            "options": {
                "similarity_threshold": 0.8,
                "check_semantic_duplicates": True,
                "check_partial_matches": True
            }
        }
    )

    # Detect duplicates
    result = await knowledge_guardian._detect_duplicates(duplicate_task)

    # Verify duplicate detection results
    assert result["status"] == "completed"
    assert "duplicates" in result
    assert "similarity_scores" in result
    assert "recommendations" in result

@pytest.mark.asyncio
async def test_consistency_enforcement(knowledge_guardian: KnowledgeGuardian):
    """Test consistency enforcement capabilities."""
    # Create test consistency task
    consistency_task = AgentTask(
        task_id="test-consistency",
        task_type="enforce_consistency",
        parameters={
            "content_items": [
                {"id": "item1", "content": "First version of content"},
                {"id": "item2", "content": "Second version of content"}
            ],
            "rules": {
                "terminology": True,
                "formatting": True,
                "citations": True,
                "metadata": True
            }
        }
    )

    # Enforce consistency
    result = await knowledge_guardian._enforce_consistency(consistency_task)

    # Verify consistency results
    assert result["status"] == "completed"
    assert "inconsistencies" in result
    assert "corrections" in result
    assert "enforcement_log" in result

@pytest.mark.asyncio
async def test_quality_monitoring(knowledge_guardian: KnowledgeGuardian):
    """Test quality monitoring capabilities."""
    # Create test quality monitoring task
    quality_task = AgentTask(
        task_id="test-quality",
        task_type="monitor_quality",
        parameters={
            "content_type": "article",
            "metrics": [
                "accuracy",
                "completeness",
                "readability",
                "relevance"
            ],
            "thresholds": {
                "min_quality_score": 0.7,
                "min_completeness": 0.8,
                "max_complexity": 0.6
            }
        }
    )

    # Monitor quality
    result = await knowledge_guardian._monitor_quality(quality_task)

    # Verify quality monitoring results
    assert result["status"] == "completed"
    assert "quality_scores" in result
    assert "alerts" in result
    assert "trends" in result
    assert "recommendations" in result

@pytest.mark.asyncio
async def test_error_handling(knowledge_guardian: KnowledgeGuardian):
    """Test error handling capabilities."""
    # Create test error message
    error_message = AgentMessage(
        message_id="test-error",
        message_type=MessageType.ERROR,
        sender="content_validator",
        receiver="knowledge_guardian",
        content={"error": "Validation failed"},
        priority=Priority.HIGH
    )

    # Handle error
    response = await knowledge_guardian._handle_error(error_message)

    # Verify error handling
    assert response.message_type == MessageType.RESPONSE
    assert response.sender == "knowledge_guardian"
    assert response.content["status"] == "error_handled"
    assert "recovery_action" in response.content 