"""Tests for the message bus and inter-agent communication."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.agents import (
    MessageBus,
    AgentMessage,
    MessageType,
    Priority
)

@pytest.mark.asyncio
async def test_agent_registration(message_bus, librarian_prime, content_curator):
    """Test agent registration and unregistration."""
    # Verify initial registration
    assert "librarian_prime" in message_bus.registered_agents
    assert "content_curator" in message_bus.registered_agents

    # Test unregistration
    await message_bus.unregister_agent(librarian_prime)
    assert "librarian_prime" not in message_bus.registered_agents
    assert "content_curator" in message_bus.registered_agents

    # Test re-registration
    await message_bus.register_agent(librarian_prime)
    assert "librarian_prime" in message_bus.registered_agents

@pytest.mark.asyncio
async def test_message_routing(message_bus, librarian_prime, content_curator):
    """Test message routing between agents."""
    # Create test message
    test_message = AgentMessage(
        message_id="test-message",
        message_type=MessageType.TASK,
        sender="librarian_prime",
        receiver="content_curator",
        content={"task": "process_document"},
        priority=Priority.MEDIUM
    )

    # Set up message handler
    received_messages = []
    async def message_handler(message):
        received_messages.append(message)
    content_curator.handle_message = message_handler

    # Send message
    await message_bus.send_message(test_message)
    
    # Verify message delivery
    assert len(received_messages) == 1
    received = received_messages[0]
    assert received.message_id == "test-message"
    assert received.sender == "librarian_prime"
    assert received.receiver == "content_curator"

@pytest.mark.asyncio
async def test_broadcast_messages(
    message_bus,
    librarian_prime,
    content_curator,
    taxonomy_master
):
    """Test broadcasting messages to multiple agents."""
    # Create test broadcast message
    broadcast_message = AgentMessage(
        message_id="test-broadcast",
        message_type=MessageType.NOTIFICATION,
        sender="librarian_prime",
        receiver="broadcast",
        content={"notification": "system_update"},
        priority=Priority.HIGH
    )

    # Set up message handlers
    curator_messages = []
    taxonomy_messages = []

    async def curator_handler(message):
        curator_messages.append(message)
    async def taxonomy_handler(message):
        taxonomy_messages.append(message)

    content_curator.handle_message = curator_handler
    taxonomy_master.handle_message = taxonomy_handler

    # Broadcast message
    await message_bus.broadcast_message(broadcast_message)

    # Verify message delivery
    assert len(curator_messages) == 1
    assert len(taxonomy_messages) == 1
    assert curator_messages[0].message_id == "test-broadcast"
    assert taxonomy_messages[0].message_id == "test-broadcast"

@pytest.mark.asyncio
async def test_priority_handling(message_bus, librarian_prime, content_curator):
    """Test message priority handling."""
    # Create test messages with different priorities
    high_priority = AgentMessage(
        message_id="high-priority",
        message_type=MessageType.TASK,
        sender="librarian_prime",
        receiver="content_curator",
        content={"task": "urgent_process"},
        priority=Priority.HIGH
    )

    low_priority = AgentMessage(
        message_id="low-priority",
        message_type=MessageType.TASK,
        sender="librarian_prime",
        receiver="content_curator",
        content={"task": "background_process"},
        priority=Priority.LOW
    )

    # Set up message handler
    received_messages = []
    async def message_handler(message):
        received_messages.append(message)
    content_curator.handle_message = message_handler

    # Send messages in reverse priority order
    await message_bus.send_message(low_priority)
    await message_bus.send_message(high_priority)

    # Verify priority handling
    assert len(received_messages) == 2
    assert received_messages[0].message_id == "high-priority"
    assert received_messages[1].message_id == "low-priority"

@pytest.mark.asyncio
async def test_message_filtering(message_bus, librarian_prime, content_curator):
    """Test message filtering based on type and content."""
    # Create test messages of different types
    task_message = AgentMessage(
        message_id="test-task",
        message_type=MessageType.TASK,
        sender="librarian_prime",
        receiver="content_curator",
        content={"task": "process_document"},
        priority=Priority.MEDIUM
    )

    query_message = AgentMessage(
        message_id="test-query",
        message_type=MessageType.QUERY,
        sender="librarian_prime",
        receiver="content_curator",
        content={"query": "document_status"},
        priority=Priority.MEDIUM
    )

    # Set up filtered message handler
    task_messages = []
    async def task_handler(message):
        if message.message_type == MessageType.TASK:
            task_messages.append(message)
    content_curator.handle_message = task_handler

    # Send messages
    await message_bus.send_message(task_message)
    await message_bus.send_message(query_message)

    # Verify message filtering
    assert len(task_messages) == 1
    assert task_messages[0].message_id == "test-task"

@pytest.mark.asyncio
async def test_error_handling(message_bus, librarian_prime, content_curator):
    """Test error handling in message delivery."""
    # Create test message
    error_message = AgentMessage(
        message_id="test-error",
        message_type=MessageType.ERROR,
        sender="content_curator",
        receiver="librarian_prime",
        content={"error": "processing_failed"},
        priority=Priority.HIGH
    )

    # Set up error handler
    error_messages = []
    async def error_handler(message):
        if message.message_type == MessageType.ERROR:
            error_messages.append(message)
    librarian_prime.handle_message = error_handler

    # Send error message
    await message_bus.send_message(error_message)

    # Verify error handling
    assert len(error_messages) == 1
    assert error_messages[0].message_id == "test-error"
    assert error_messages[0].content["error"] == "processing_failed" 