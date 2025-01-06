"""Tests for core agent functionality."""

import uuid
import pytest
from unittest.mock import AsyncMock

from app.agents import (
    AgentMessage,
    AgentTask,
    MessageType,
    Priority,
    BaseAgent
)
from app.core.logging import AgentLogContext

pytestmark = pytest.mark.asyncio

async def test_agent_initialization(test_agent: BaseAgent):
    """Test basic agent initialization."""
    assert test_agent.agent_id == "test_agent"
    assert test_agent.capabilities == []

async def test_message_handling(test_agent: BaseAgent):
    """Test agent message handling."""
    # Create a mock handler
    mock_handler = AsyncMock()
    test_agent.register_message_handler(MessageType.QUERY, mock_handler)
    
    # Create a test message
    message = AgentMessage(
        message_id=str(uuid.uuid4()),
        message_type=MessageType.QUERY,
        sender="test_sender",
        receiver="test_agent",
        content={"query": "test query"}
    )
    
    # Handle the message
    await test_agent.handle_message(message)
    
    # Verify handler was called
    mock_handler.assert_called_once_with(message)

async def test_task_handling(test_agent: BaseAgent):
    """Test agent task handling."""
    # Create a mock handler
    mock_handler = AsyncMock(return_value={"status": "success"})
    test_agent.register_task_handler("test_task", mock_handler)
    
    # Create a test task
    task = AgentTask(
        task_id=str(uuid.uuid4()),
        task_type="test_task",
        parameters={"param": "value"}
    )
    
    # Handle the task
    result = await test_agent.handle_task(task)
    
    # Verify handler was called and result is correct
    mock_handler.assert_called_once_with(task)
    assert result == {"status": "success"}

async def test_invalid_task_type(test_agent: BaseAgent):
    """Test handling of invalid task types."""
    task = AgentTask(
        task_id=str(uuid.uuid4()),
        task_type="invalid_task",
        parameters={}
    )
    
    with pytest.raises(ValueError, match="No handler for task type: invalid_task"):
        await test_agent.handle_task(task)

async def test_message_priority(test_agent: BaseAgent):
    """Test message priority handling."""
    messages = []
    
    async def handler(message: AgentMessage):
        messages.append(message)
    
    test_agent.register_message_handler(MessageType.TASK, handler)
    
    # Create messages with different priorities
    high_priority = AgentMessage(
        message_id=str(uuid.uuid4()),
        message_type=MessageType.TASK,
        sender="test_sender",
        receiver="test_agent",
        content={"task": "urgent"},
        priority=Priority.HIGH
    )
    
    low_priority = AgentMessage(
        message_id=str(uuid.uuid4()),
        message_type=MessageType.TASK,
        sender="test_sender",
        receiver="test_agent",
        content={"task": "routine"},
        priority=Priority.LOW
    )
    
    # Handle messages
    await test_agent.handle_message(low_priority)
    await test_agent.handle_message(high_priority)
    
    # Verify messages were handled
    assert len(messages) == 2
    assert [m.priority for m in messages] == [Priority.LOW, Priority.HIGH]

async def test_agent_logging(test_agent: BaseAgent, caplog):
    """Test agent logging functionality."""
    ctx = AgentLogContext(
        agent_id=test_agent.agent_id,
        operation="test_operation"
    )
    
    # Create and handle a message
    message = AgentMessage(
        message_id=str(uuid.uuid4()),
        message_type=MessageType.STATUS,
        sender="test_sender",
        receiver=test_agent.agent_id,
        content={"status": "test"}
    )
    
    await test_agent.handle_message(message)
    
    # Verify logs were created
    assert any(
        record.message.startswith("Agent Operation")
        for record in caplog.records
    ) 