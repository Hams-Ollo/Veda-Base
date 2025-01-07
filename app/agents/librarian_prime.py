"""Librarian Prime - Main orchestrator agent for the Library of Alexandria."""

from typing import Dict, Any, Optional
import uuid

from pydantic_ai import RunContext
from .base import (
    BaseAgent,
    AgentMessage,
    AgentTask,
    MessageType,
    Priority,
    SharedDependencies
)

class LibrarianPrime(BaseAgent):
    """Main orchestrator agent responsible for coordinating all other agents."""

    def __init__(self, deps: Optional[SharedDependencies] = None):
        super().__init__(
            agent_id="librarian_prime",
            model_name="groq:mixtral-8x7b",
            system_prompt="""You are the Librarian Prime, the central orchestrator of the Library of Alexandria.
Your role is to:
1. Understand user requests and break them down into manageable tasks
2. Delegate tasks to specialized agents
3. Coordinate complex workflows
4. Maintain context across interactions
5. Ensure quality and consistency of results
6. Adapt to user preferences and learning patterns""",
            deps=deps
        )
        self._setup_handlers()

    def _setup_handlers(self):
        """Set up message and task handlers."""
        self.register_message_handler(MessageType.QUERY, self._handle_user_query)
        self.register_message_handler(MessageType.RESPONSE, self._handle_agent_response)
        self.register_message_handler(MessageType.ERROR, self._handle_error)
        
        self.register_task_handler("process_document", self._handle_document_processing)
        self.register_task_handler("search_knowledge", self._handle_knowledge_search)
        self.register_task_handler("analyze_content", self._handle_content_analysis)

    @property
    def capabilities(self) -> list[str]:
        """List of tasks this agent can coordinate."""
        return [
            "document_processing",
            "knowledge_search",
            "content_analysis",
            "tag_management",
            "knowledge_graph_operations"
        ]

    async def _handle_user_query(self, message: AgentMessage) -> AgentMessage:
        """Handle incoming user queries."""
        ctx = RunContext(self.deps)
        
        # Use PydanticAI to analyze the query
        result = await self.agent.run(
            message.content["query"],
            deps=self.deps
        )

        # Create tasks based on the analysis
        tasks = self._create_tasks_from_analysis(result.data)
        
        # Return acknowledgment
        return AgentMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.RESPONSE,
            sender=self.agent_id,
            receiver=message.sender,
            content={"status": "processing", "tasks": len(tasks)},
            parent_message_id=message.message_id
        )

    async def _handle_agent_response(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle responses from other agents."""
        # Process the response and update task status
        # Coordinate next steps if needed
        return None

    async def _handle_error(self, message: AgentMessage) -> AgentMessage:
        """Handle error messages from other agents."""
        return AgentMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.RESPONSE,
            sender=self.agent_id,
            receiver=message.sender,
            content={"status": "error_handled", "original_error": message.content},
            parent_message_id=message.message_id
        )

    async def _handle_document_processing(self, task: AgentTask) -> Dict[str, Any]:
        """Handle document processing coordination."""
        # Coordinate document processing workflow
        return {"status": "completed", "result": "Document processed successfully"}

    async def _handle_knowledge_search(self, task: AgentTask) -> Dict[str, Any]:
        """Handle knowledge search coordination."""
        # Coordinate knowledge search workflow
        return {"status": "completed", "result": "Search completed"}

    async def _handle_content_analysis(self, task: AgentTask) -> Dict[str, Any]:
        """Handle content analysis coordination."""
        # Coordinate content analysis workflow
        return {"status": "completed", "result": "Analysis completed"}

    def _create_tasks_from_analysis(self, analysis: Any) -> list[AgentTask]:
        """Create task objects based on query analysis."""
        tasks = []
        # Implementation will depend on the analysis structure
        return tasks

    @property
    def agent_info(self) -> Dict[str, Any]:
        """Get information about the agent's current state."""
        return {
            "id": self.agent_id,
            "type": "orchestrator",
            "capabilities": self.capabilities,
            "status": "active"
        } 