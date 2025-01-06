"""Message bus implementation for inter-agent communication."""

import asyncio
import logging
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from .base import BaseAgent, AgentMessage, MessageType, Priority

logger = logging.getLogger(__name__)

@dataclass
class MessageBusContext:
    """Context information for message bus operations."""
    conversation_id: str
    session_id: str
    timestamp: datetime
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class MessageQueueItem:
    """Represents a message in the priority queue."""
    message: AgentMessage
    timestamp: datetime
    priority: int

    def __lt__(self, other):
        # Higher priority messages should come first
        if self.priority != other.priority:
            return self.priority > other.priority
        # For same priority, use FIFO ordering
        return self.timestamp < other.timestamp

class MessageBus:
    """Central message bus for agent communication."""

    def __init__(self):
        """Initialize the message bus."""
        self._registered_agents: Dict[str, BaseAgent] = {}
        self._subscriptions: Dict[MessageType, Set[str]] = {
            message_type: set() for message_type in MessageType
        }
        self._message_queue: asyncio.PriorityQueue[MessageQueueItem] = asyncio.PriorityQueue()
        self._running: bool = False
        self._processing_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the message bus."""
        if self._running:
            return

        self._running = True
        self._processing_task = asyncio.create_task(self._process_messages())
        logger.info("Message bus started")

    async def stop(self):
        """Stop the message bus."""
        if not self._running:
            return

        self._running = False
        if self._processing_task:
            await self._processing_task
            self._processing_task = None
        logger.info("Message bus stopped")

    def register_agent(self, agent: BaseAgent):
        """Register an agent with the message bus."""
        if agent.agent_id in self._registered_agents:
            raise ValueError(f"Agent with ID {agent.agent_id} is already registered")

        self._registered_agents[agent.agent_id] = agent
        logger.info(f"Agent {agent.agent_id} registered")

    def unregister_agent(self, agent: BaseAgent):
        """Unregister an agent from the message bus."""
        if agent.agent_id not in self._registered_agents:
            return

        del self._registered_agents[agent.agent_id]
        # Remove from all subscriptions
        for subscribers in self._subscriptions.values():
            subscribers.discard(agent.agent_id)
        logger.info(f"Agent {agent.agent_id} unregistered")

    def subscribe(self, agent_id: str, message_types: List[MessageType]):
        """Subscribe an agent to specific message types."""
        if agent_id not in self._registered_agents:
            raise ValueError(f"Agent {agent_id} is not registered")

        for message_type in message_types:
            self._subscriptions[message_type].add(agent_id)
        logger.debug(f"Agent {agent_id} subscribed to {message_types}")

    def unsubscribe(self, agent_id: str, message_types: List[MessageType]):
        """Unsubscribe an agent from specific message types."""
        for message_type in message_types:
            self._subscriptions[message_type].discard(agent_id)
        logger.debug(f"Agent {agent_id} unsubscribed from {message_types}")

    async def send_message(self, message: AgentMessage):
        """Send a message to a specific agent."""
        if not message.receiver or message.receiver not in self._registered_agents:
            logger.error(f"Invalid receiver: {message.receiver}")
            return

        # Ensure message has an ID
        if not message.message_id:
            message.message_id = str(uuid4())

        # Create queue item with priority
        queue_item = MessageQueueItem(
            message=message,
            timestamp=datetime.now(),
            priority=message.priority.value
        )

        await self._message_queue.put(queue_item)
        logger.debug(f"Message {message.message_id} queued for {message.receiver}")

    async def broadcast_message(self, message: AgentMessage):
        """Broadcast a message to all subscribed agents."""
        subscribers = self._subscriptions[message.message_type]
        if not subscribers:
            logger.debug(f"No subscribers for message type {message.message_type}")
            return

        # Create a copy of the message for each subscriber
        for subscriber_id in subscribers:
            broadcast_message = AgentMessage(
                message_id=f"{message.message_id}-{subscriber_id}",
                message_type=message.message_type,
                sender=message.sender,
                receiver=subscriber_id,
                content=message.content,
                priority=message.priority,
                parent_message_id=message.parent_message_id
            )

            await self.send_message(broadcast_message)

    async def _process_messages(self):
        """Process messages from the queue."""
        while self._running:
            try:
                # Get the next message from the queue
                queue_item = await self._message_queue.get()
                message = queue_item.message

                # Get the receiving agent
                receiver = self._registered_agents.get(message.receiver)
                if not receiver:
                    logger.error(f"Receiver {message.receiver} not found for message {message.message_id}")
                    continue

                try:
                    # Deliver the message
                    await receiver.handle_message(message)
                    logger.debug(f"Message {message.message_id} delivered to {message.receiver}")
                except Exception as e:
                    logger.error(f"Error delivering message {message.message_id} to {message.receiver}: {e}")

                # Mark the task as done
                self._message_queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing message queue: {e}")

    @property
    def registered_agents(self) -> List[str]:
        """Get list of registered agent IDs."""
        return list(self._registered_agents.keys())

    @property
    def queue_size(self) -> int:
        """Get current size of the message queue."""
        return self._message_queue.qsize()

    @property
    def is_running(self) -> bool:
        """Check if the message bus is running."""
        return self._running