"""Tests for the Content Curator agent."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path

from app.agents import (
    ContentCurator,
    AgentMessage,
    AgentTask,
    MessageType,
    Priority
)
from app.core import DocumentProcessor, ContentAnalyzer

@pytest.mark.asyncio
async def test_document_processing(content_curator: ContentCurator):
    """Test document processing capabilities."""
    # Create test document task
    doc_task = AgentTask(
        task_id="test-doc",
        task_type="process_document",
        parameters={
            "path": "test.pdf",
            "format": "pdf",
            "options": {
                "extract_text": True,
                "extract_metadata": True
            }
        }
    )

    # Process document
    result = await content_curator._process_document(doc_task)

    # Verify processing results
    assert result["status"] == "completed"
    assert "content" in result
    assert "metadata" in result
    assert "summary" in result

@pytest.mark.asyncio
async def test_content_analysis(content_curator: ContentCurator):
    """Test content analysis capabilities."""
    # Create test analysis task
    analysis_task = AgentTask(
        task_id="test-analysis",
        task_type="analyze_content",
        parameters={
            "content": "Test content for analysis",
            "analysis_type": "comprehensive",
            "options": {
                "extract_concepts": True,
                "generate_summary": True,
                "identify_topics": True
            }
        }
    )

    # Analyze content
    result = await content_curator._analyze_content(analysis_task)

    # Verify analysis results
    assert result["status"] == "completed"
    assert "concepts" in result
    assert "summary" in result
    assert "topics" in result
    assert "quality_score" in result

@pytest.mark.asyncio
async def test_metadata_extraction(content_curator: ContentCurator):
    """Test metadata extraction capabilities."""
    # Create test metadata task
    metadata_task = AgentTask(
        task_id="test-metadata",
        task_type="extract_metadata",
        parameters={
            "content": "Test content for metadata extraction",
            "options": {
                "extract_authors": True,
                "extract_dates": True,
                "extract_references": True
            }
        }
    )

    # Extract metadata
    result = await content_curator._extract_metadata(metadata_task)

    # Verify metadata results
    assert result["status"] == "completed"
    assert "authors" in result
    assert "dates" in result
    assert "references" in result

@pytest.mark.asyncio
async def test_quality_assessment(content_curator: ContentCurator):
    """Test content quality assessment."""
    # Create test quality task
    quality_task = AgentTask(
        task_id="test-quality",
        task_type="assess_quality",
        parameters={
            "content": "Test content for quality assessment",
            "criteria": {
                "completeness": True,
                "accuracy": True,
                "relevance": True
            }
        }
    )

    # Assess quality
    result = await content_curator._assess_quality(quality_task)

    # Verify quality results
    assert result["status"] == "completed"
    assert "quality_score" in result
    assert "assessment_details" in result
    assert "recommendations" in result

@pytest.mark.asyncio
async def test_error_handling(content_curator: ContentCurator):
    """Test error handling capabilities."""
    # Create test error message
    error_message = AgentMessage(
        message_id="test-error",
        message_type=MessageType.ERROR,
        sender="document_processor",
        receiver="content_curator",
        content={"error": "Processing failed"},
        priority=Priority.HIGH
    )

    # Handle error
    response = await content_curator._handle_error(error_message)

    # Verify error handling
    assert response.message_type == MessageType.RESPONSE
    assert response.sender == "content_curator"
    assert response.content["status"] == "error_handled"
    assert "recovery_action" in response.content 