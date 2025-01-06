"""Integration tests for the multi-agent system."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path

from app.agents import (
    AgentMessage,
    AgentTask,
    MessageType,
    Priority
)

@pytest.mark.asyncio
async def test_document_processing_workflow(
    message_bus,
    librarian_prime,
    content_curator,
    taxonomy_master,
    connection_weaver,
    knowledge_guardian
):
    """Test the complete document processing workflow."""
    # Create test document processing request
    document_request = AgentMessage(
        message_id="test-doc-process",
        message_type=MessageType.QUERY,
        sender="user",
        receiver="librarian_prime",
        content={
            "action": "process_document",
            "document_path": "test_data/sample_document.pdf",
            "options": {
                "extract_content": True,
                "generate_tags": True,
                "validate_content": True,
                "create_connections": True
            }
        },
        priority=Priority.HIGH
    )

    # Set up result collectors
    processing_results = []
    tagging_results = []
    validation_results = []
    connection_results = []

    # Set up message handlers
    async def curator_handler(message):
        if message.message_type == MessageType.TASK:
            processing_results.append(message)
            # Simulate processing completion
            await message_bus.send_message(AgentMessage(
                message_id=f"response-{message.message_id}",
                message_type=MessageType.RESPONSE,
                sender="content_curator",
                receiver="librarian_prime",
                content={"status": "completed", "processed_content": "test_content"},
                priority=Priority.HIGH
            ))

    async def taxonomy_handler(message):
        if message.message_type == MessageType.TASK:
            tagging_results.append(message)
            # Simulate tagging completion
            await message_bus.send_message(AgentMessage(
                message_id=f"response-{message.message_id}",
                message_type=MessageType.RESPONSE,
                sender="taxonomy_master",
                receiver="librarian_prime",
                content={"status": "completed", "tags": ["test_tag"]},
                priority=Priority.HIGH
            ))

    async def guardian_handler(message):
        if message.message_type == MessageType.TASK:
            validation_results.append(message)
            # Simulate validation completion
            await message_bus.send_message(AgentMessage(
                message_id=f"response-{message.message_id}",
                message_type=MessageType.RESPONSE,
                sender="knowledge_guardian",
                receiver="librarian_prime",
                content={"status": "completed", "validation_result": "valid"},
                priority=Priority.HIGH
            ))

    async def weaver_handler(message):
        if message.message_type == MessageType.TASK:
            connection_results.append(message)
            # Simulate connection creation completion
            await message_bus.send_message(AgentMessage(
                message_id=f"response-{message.message_id}",
                message_type=MessageType.RESPONSE,
                sender="connection_weaver",
                receiver="librarian_prime",
                content={"status": "completed", "connections": ["test_connection"]},
                priority=Priority.HIGH
            ))

    # Register message handlers
    content_curator.handle_message = curator_handler
    taxonomy_master.handle_message = taxonomy_handler
    knowledge_guardian.handle_message = guardian_handler
    connection_weaver.handle_message = weaver_handler

    # Process document request
    await librarian_prime.handle_message(document_request)

    # Verify workflow completion
    assert len(processing_results) == 1
    assert len(tagging_results) == 1
    assert len(validation_results) == 1
    assert len(connection_results) == 1

@pytest.mark.asyncio
async def test_learning_path_creation_workflow(
    message_bus,
    librarian_prime,
    learning_companion,
    content_curator,
    analytics_sage
):
    """Test the learning path creation workflow."""
    # Create test learning path request
    learning_request = AgentMessage(
        message_id="test-learning-path",
        message_type=MessageType.QUERY,
        sender="user",
        receiver="librarian_prime",
        content={
            "action": "create_learning_path",
            "user_profile": {
                "interests": ["machine_learning"],
                "level": "intermediate",
                "goals": ["master_deep_learning"]
            },
            "options": {
                "duration": "3_months",
                "include_assessments": True
            }
        },
        priority=Priority.HIGH
    )

    # Set up result collectors
    companion_results = []
    curator_results = []
    analytics_results = []

    # Set up message handlers
    async def companion_handler(message):
        if message.message_type == MessageType.TASK:
            companion_results.append(message)
            # Simulate learning path creation completion
            await message_bus.send_message(AgentMessage(
                message_id=f"response-{message.message_id}",
                message_type=MessageType.RESPONSE,
                sender="learning_companion",
                receiver="librarian_prime",
                content={"status": "completed", "learning_path": "test_path"},
                priority=Priority.HIGH
            ))

    async def curator_handler(message):
        if message.message_type == MessageType.TASK:
            curator_results.append(message)
            # Simulate content curation completion
            await message_bus.send_message(AgentMessage(
                message_id=f"response-{message.message_id}",
                message_type=MessageType.RESPONSE,
                sender="content_curator",
                receiver="librarian_prime",
                content={"status": "completed", "curated_content": "test_content"},
                priority=Priority.HIGH
            ))

    async def analytics_handler(message):
        if message.message_type == MessageType.TASK:
            analytics_results.append(message)
            # Simulate analytics completion
            await message_bus.send_message(AgentMessage(
                message_id=f"response-{message.message_id}",
                message_type=MessageType.RESPONSE,
                sender="analytics_sage",
                receiver="librarian_prime",
                content={"status": "completed", "recommendations": "test_recommendations"},
                priority=Priority.HIGH
            ))

    # Register message handlers
    learning_companion.handle_message = companion_handler
    content_curator.handle_message = curator_handler
    analytics_sage.handle_message = analytics_handler

    # Process learning path request
    await librarian_prime.handle_message(learning_request)

    # Verify workflow completion
    assert len(companion_results) == 1
    assert len(curator_results) == 1
    assert len(analytics_results) == 1

@pytest.mark.asyncio
async def test_knowledge_graph_update_workflow(
    message_bus,
    librarian_prime,
    connection_weaver,
    taxonomy_master,
    analytics_sage
):
    """Test the knowledge graph update workflow."""
    # Create test graph update request
    graph_request = AgentMessage(
        message_id="test-graph-update",
        message_type=MessageType.QUERY,
        sender="user",
        receiver="librarian_prime",
        content={
            "action": "update_knowledge_graph",
            "changes": {
                "add_nodes": ["concept_a", "concept_b"],
                "add_edges": [("concept_a", "concept_b", "relates_to")]
            },
            "options": {
                "analyze_impact": True,
                "update_taxonomy": True
            }
        },
        priority=Priority.HIGH
    )

    # Set up result collectors
    weaver_results = []
    taxonomy_results = []
    analytics_results = []

    # Set up message handlers
    async def weaver_handler(message):
        if message.message_type == MessageType.TASK:
            weaver_results.append(message)
            # Simulate graph update completion
            await message_bus.send_message(AgentMessage(
                message_id=f"response-{message.message_id}",
                message_type=MessageType.RESPONSE,
                sender="connection_weaver",
                receiver="librarian_prime",
                content={"status": "completed", "graph_updates": "test_updates"},
                priority=Priority.HIGH
            ))

    async def taxonomy_handler(message):
        if message.message_type == MessageType.TASK:
            taxonomy_results.append(message)
            # Simulate taxonomy update completion
            await message_bus.send_message(AgentMessage(
                message_id=f"response-{message.message_id}",
                message_type=MessageType.RESPONSE,
                sender="taxonomy_master",
                receiver="librarian_prime",
                content={"status": "completed", "taxonomy_updates": "test_updates"},
                priority=Priority.HIGH
            ))

    async def analytics_handler(message):
        if message.message_type == MessageType.TASK:
            analytics_results.append(message)
            # Simulate impact analysis completion
            await message_bus.send_message(AgentMessage(
                message_id=f"response-{message.message_id}",
                message_type=MessageType.RESPONSE,
                sender="analytics_sage",
                receiver="librarian_prime",
                content={"status": "completed", "impact_analysis": "test_analysis"},
                priority=Priority.HIGH
            ))

    # Register message handlers
    connection_weaver.handle_message = weaver_handler
    taxonomy_master.handle_message = taxonomy_handler
    analytics_sage.handle_message = analytics_handler

    # Process graph update request
    await librarian_prime.handle_message(graph_request)

    # Verify workflow completion
    assert len(weaver_results) == 1
    assert len(taxonomy_results) == 1
    assert len(analytics_results) == 1 