"""Message bus for agent communication."""

from typing import Dict, Set, Optional, List, Any
import asyncio
import logging
from datetime import datetime, timedelta
from collections import defaultdict

from app.core.agents.base import Message, BaseAgent

logger = logging.getLogger(__name__)

class MessageBus:
    """Manages communication between agents."""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.subscriptions: Dict[str, Set[str]] = defaultdict(set)
        self.message_history: List[Message] = []
        self.max_history = 1000  # Keep last 1000 messages
        self.running = False
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the message bus."""
        self.agents[agent.id] = agent
        logger.info(f"Registered agent: {agent.name} ({agent.id})")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent from the message bus."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            # Remove from all subscriptions
            for subscribers in self.subscriptions.values():
                subscribers.discard(agent_id)
            logger.info(f"Unregistered agent: {agent_id}")
    
    def subscribe(self, agent_id: str, message_type: str):
        """Subscribe an agent to a message type."""
        if agent_id in self.agents:
            self.subscriptions[message_type].add(agent_id)
            logger.debug(f"Agent {agent_id} subscribed to {message_type}")
    
    def unsubscribe(self, agent_id: str, message_type: str):
        """Unsubscribe an agent from a message type."""
        if message_type in self.subscriptions:
            self.subscriptions[message_type].discard(agent_id)
            logger.debug(f"Agent {agent_id} unsubscribed from {message_type}")
    
    async def broadcast(
        self,
        message: Message,
        exclude_sender: bool = True
    ):
        """Broadcast a message to all subscribers."""
        if message.type in self.subscriptions:
            recipients = self.subscriptions[message.type]
            if exclude_sender:
                recipients = recipients - {message.sender}
            
            for recipient_id in recipients:
                if recipient_id in self.agents:
                    await self.agents[recipient_id].message_queue.put(message)
    
    async def send_message(
        self,
        sender_id: str,
        content: Dict[str, Any],
        msg_type: str,
        recipient_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> bool:
        """Send a message from one agent to another or broadcast."""
        if sender_id not in self.agents:
            logger.error(f"Unknown sender: {sender_id}")
            return False
        
        message = Message(
            content=content,
            msg_type=msg_type,
            sender=sender_id,
            recipient=recipient_id,
            correlation_id=correlation_id
        )
        
        if recipient_id:
            if recipient_id not in self.agents:
                logger.error(f"Unknown recipient: {recipient_id}")
                return False
            await self.agents[recipient_id].message_queue.put(message)
        else:
            await self.broadcast(message)
        
        # Store in history
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history.pop(0)
        
        return True
    
    def get_message_history(
        self,
        agent_id: Optional[str] = None,
        message_type: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get message history with optional filtering."""
        messages = self.message_history
        
        if agent_id:
            messages = [
                msg for msg in messages
                if msg.sender == agent_id or msg.recipient == agent_id
            ]
        
        if message_type:
            messages = [msg for msg in messages if msg.type == message_type]
        
        if since:
            messages = [
                msg for msg in messages
                if datetime.fromisoformat(msg.timestamp) > since
            ]
        
        return [msg.to_dict() for msg in messages[-limit:]]
    
    async def start(self):
        """Start the message bus and all registered agents."""
        self.running = True
        agent_tasks = []
        
        for agent in self.agents.values():
            task = asyncio.create_task(agent.run())
            agent_tasks.append(task)
        
        try:
            await asyncio.gather(*agent_tasks)
        except Exception as e:
            logger.error(f"Message bus error: {str(e)}")
        finally:
            self.running = False
    
    def stop(self):
        """Stop the message bus and all agents."""
        self.running = False
        for agent in self.agents.values():
            agent.stop()

# Global message bus instance
message_bus = MessageBus() 