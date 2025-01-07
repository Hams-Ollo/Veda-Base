"""Multi-agent system for the Library of Alexandria."""

from .base import (
    BaseAgent,
    AgentMessage,
    AgentTask,
    MessageType,
    Priority,
    SharedDependencies
)
from .message_bus import MessageBus, MessageBusContext
from .librarian_prime import LibrarianPrime

__all__ = [
    'BaseAgent',
    'AgentMessage',
    'AgentTask',
    'MessageType',
    'Priority',
    'SharedDependencies',
    'MessageBus',
    'MessageBusContext',
    'LibrarianPrime',
]

__version__ = '0.1.0' 