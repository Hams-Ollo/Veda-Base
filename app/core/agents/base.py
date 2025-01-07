"""Base agent functionality and interfaces."""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import asyncio
from abc import ABC, abstractmethod
import uuid

logger = logging.getLogger(__name__)

class Message:
    """Represents a message in the agent system."""
    
    def __init__(
        self,
        content: Dict[str, Any],
        msg_type: str,
        sender: str,
        recipient: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        self.id = str(uuid.uuid4())
        self.content = content
        self.type = msg_type
        self.sender = sender
        self.recipient = recipient
        self.correlation_id = correlation_id or self.id
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        return {
            "id": self.id,
            "content": self.content,
            "type": self.type,
            "sender": self.sender,
            "recipient": self.recipient,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary format."""
        msg = cls(
            content=data["content"],
            msg_type=data["type"],
            sender=data["sender"],
            recipient=data.get("recipient"),
            correlation_id=data.get("correlation_id")
        )
        msg.id = data["id"]
        msg.timestamp = data["timestamp"]
        return msg

class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, agent_id: str, name: str):
        self.id = agent_id
        self.name = name
        self.message_queue: asyncio.Queue[Message] = asyncio.Queue()
        self.running = False
        self.message_handlers: Dict[str, callable] = {}
    
    def register_handler(self, msg_type: str, handler: callable):
        """Register a handler for a specific message type."""
        self.message_handlers[msg_type] = handler
    
    async def send_message(
        self,
        content: Dict[str, Any],
        msg_type: str,
        recipient: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> Message:
        """Send a message to another agent."""
        message = Message(
            content=content,
            msg_type=msg_type,
            sender=self.id,
            recipient=recipient,
            correlation_id=correlation_id
        )
        await self.message_queue.put(message)
        return message
    
    async def handle_message(self, message: Message):
        """Handle an incoming message."""
        try:
            if message.type in self.message_handlers:
                await self.message_handlers[message.type](message)
            else:
                await self._default_handler(message)
        except Exception as e:
            logger.error(f"Error handling message {message.id}: {str(e)}")
            # Send error response if there's a recipient
            if message.recipient:
                await self.send_message(
                    content={"error": str(e)},
                    msg_type="error",
                    recipient=message.sender,
                    correlation_id=message.correlation_id
                )
    
    async def _default_handler(self, message: Message):
        """Default message handler."""
        logger.warning(f"No handler for message type: {message.type}")
    
    @abstractmethod
    async def initialize(self):
        """Initialize the agent."""
        pass
    
    @abstractmethod
    async def shutdown(self):
        """Cleanup and shutdown the agent."""
        pass
    
    async def run(self):
        """Main agent loop."""
        try:
            await self.initialize()
            self.running = True
            
            while self.running:
                message = await self.message_queue.get()
                await self.handle_message(message)
                self.message_queue.task_done()
                
        except Exception as e:
            logger.error(f"Agent {self.name} error: {str(e)}")
        finally:
            await self.shutdown()
    
    def stop(self):
        """Stop the agent."""
        self.running = False 