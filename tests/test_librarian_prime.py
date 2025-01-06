"""Tests for the Librarian Prime agent."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.agents import (
    LibrarianPrime,
    AgentMessage,
    AgentTask,
    MessageType,
    Priority
)
from app.core import AgentLogContext

@pytest.mark.asyncio
async def test_librarian_query_handling(librarian_prime: LibrarianPrime):
    """Test handling of user queries."""
    # Create test query message
    query_message = AgentMessage(
        message_id="test-query",
        message_type=MessageType.QUERY,
        sender="user",
        receiver="librarian_prime",
        content={"query": "Process this document"},
        priority=Priority.MEDIUM
    )

    # Handle query
    response = await librarian_prime._handle_user_query(query_message)

    # Verify response structure
    assert response.message_type == MessageType.RESPONSE
    assert response.sender == "librarian_prime"
    assert response.receiver == "user"
    assert "status" in response.content
    assert "tasks" in response.content
    assert response.parent_message_id == "test-query"

@pytest.mark.asyncio
async def test_librarian_error_handling(librarian_prime: LibrarianPrime):
    """Test handling of error messages."""
    # Create test error message
    error_message = AgentMessage(
        message_id="test-error",
        message_type=MessageType.ERROR,
        sender="content_curator",
        receiver="librarian_prime",
        content={"error": "Processing failed"},
        priority=Priority.HIGH
    )

    # Handle error
    response = await librarian_prime._handle_error(error_message)

    # Verify error handling
    assert response.message_type == MessageType.RESPONSE
    assert response.sender == "librarian_prime"
    assert response.receiver == "content_curator"
    assert "status" in response.content
    assert response.content["status"] == "error_handled"
    assert "original_error" in response.content

@pytest.mark.asyncio
async def test_librarian_task_handling(librarian_prime: LibrarianPrime):
    """Test handling of various task types."""
    # Test document processing task
    doc_task = AgentTask(
        task_id="test-doc",
        task_type="process_document",
        parameters={"path": "test.pdf"}
    )
    doc_result = await librarian_prime._handle_document_processing(doc_task)
    assert doc_result["status"] == "completed"

    # Test knowledge search task
    search_task = AgentTask(
        task_id="test-search",
        task_type="search_knowledge",
        parameters={"query": "test"}
    )
    search_result = await librarian_prime._handle_knowledge_search(search_task)
    assert search_result["status"] == "completed"

    # Test content analysis task
    analysis_task = AgentTask(
        task_id="test-analysis",
        task_type="analyze_content",
        parameters={"content": "test"}
    )
    analysis_result = await librarian_prime._handle_content_analysis(analysis_task)
    assert analysis_result["status"] == "completed"

@pytest.mark.asyncio
async def test_librarian_capabilities(librarian_prime: LibrarianPrime):
    """Test librarian capabilities reporting."""
    capabilities = librarian_prime.capabilities
    
    # Verify essential capabilities
    assert "document_processing" in capabilities
    assert "knowledge_search" in capabilities
    assert "content_analysis" in capabilities
    assert "tag_management" in capabilities
    assert "knowledge_graph_operations" in capabilities

@pytest.mark.asyncio
async def test_librarian_agent_info(librarian_prime: LibrarianPrime):
    """Test agent information reporting."""
    info = librarian_prime.agent_info
    
    assert info["id"] == "librarian_prime"
    assert info["type"] == "orchestrator"
    assert isinstance(info["capabilities"], list)
    assert info["status"] == "active" 