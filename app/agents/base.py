"""Base classes and types for the multi-agent system."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

# Shared Dependencies
@dataclass
class SharedDependencies:
    """Shared resources and dependencies for all agents."""
    vector_store: Any  # ChromaDB instance
    document_store: Any  # Document storage system
    tag_registry: Any  # Tag management system
    knowledge_graph: Any  # NetworkX graph instance

class MessageType(str, Enum):
    """Types of messages that can be exchanged between agents."""
    TASK = "task"
    RESPONSE = "response"
    ERROR = "error"
    STATUS = "status"
    QUERY = "query"
    RESULT = "result"

class Priority(int, Enum):
    """Priority levels for agent tasks."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class TaskStatus(str, Enum):
    """Status values for agent tasks."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING = "waiting"

class AgentMessage(BaseModel):
    """Base message format for inter-agent communication."""
    message_id: str = Field(..., description="Unique message identifier")
    message_type: MessageType
    sender: str = Field(..., description="ID of the sending agent")
    receiver: str = Field(..., description="ID of the receiving agent")
    content: Dict[str, Any] = Field(..., description="Message payload")
    priority: Priority = Field(default=Priority.MEDIUM)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    parent_message_id: Optional[str] = Field(None, description="ID of the parent message if this is a response")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentTask(BaseModel):
    """Structure for tasks that can be assigned to agents."""
    task_id: str = Field(..., description="Unique task identifier")
    task_type: str = Field(..., description="Type of task to be performed")
    parameters: Dict[str, Any] = Field(..., description="Task parameters")
    priority: Priority = Field(default=Priority.MEDIUM)
    dependencies: List[str] = Field(default_factory=list, description="IDs of tasks that must complete before this one")
    timeout: Optional[float] = Field(None, description="Task timeout in seconds")

class BaseAgent:
    """Base class for all agents in the system."""
    
    def __init__(
        self,
        agent_id: str,
        model_name: str = "groq:mixtral-8x7b",
        system_prompt: str = "",
        deps: Optional[SharedDependencies] = None
    ):
        self.agent_id = agent_id
        self.agent = Agent(
            model_name,
            deps_type=SharedDependencies,
            system_prompt=system_prompt
        )
        self.deps = deps
        self._message_handlers = {}
        self._task_handlers = {}

    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle incoming messages."""
        handler = self._message_handlers.get(message.message_type)
        if handler:
            return await handler(message)
        return None

    async def handle_task(self, task: AgentTask) -> Dict[str, Any]:
        """Handle assigned tasks."""
        handler = self._task_handlers.get(task.task_type)
        if handler:
            return await handler(task)
        raise ValueError(f"No handler for task type: {task.task_type}")

    def register_message_handler(self, message_type: MessageType, handler):
        """Register a handler for a specific message type."""
        self._message_handlers[message_type] = handler

    def register_task_handler(self, task_type: str, handler):
        """Register a handler for a specific task type."""
        self._task_handlers[task_type] = handler

    async def send_message(self, message: AgentMessage) -> None:
        """Send a message to another agent."""
        # To be implemented by the message bus system
        pass

    @property
    def capabilities(self) -> List[str]:
        """List of tasks this agent can handle."""
        return list(self._task_handlers.keys()) 