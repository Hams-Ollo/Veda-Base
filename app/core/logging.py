"""Logging configuration for the Library of Alexandria."""

import logging
from typing import Any, Optional
from datetime import datetime

import logfire
from pydantic import BaseModel

class AgentLogContext(BaseModel):
    """Context information for agent-related logs."""
    agent_id: str
    message_id: Optional[str] = None
    task_id: Optional[str] = None
    operation: str
    timestamp: datetime = datetime.utcnow()
    metadata: dict[str, Any] = {}

def setup_logging() -> None:
    """Configure logging for the application."""
    # Configure Logfire
    logfire.configure()
    
    # Instrument various components
    logfire.instrument_pydantic()  # Monitor Pydantic model validations
    logfire.instrument_openai()    # Monitor LLM API calls
    logfire.instrument_asyncio()   # Monitor async operations
    logfire.instrument_httpx()     # Monitor HTTP requests
    
    # Set up standard Python logging to work with Logfire
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def log_agent_operation(
    ctx: AgentLogContext,
    message: str,
    level: str = "info",
    **kwargs: Any
) -> None:
    """Log an agent operation with context."""
    log_data = {
        "agent_id": ctx.agent_id,
        "operation": ctx.operation,
        "timestamp": ctx.timestamp,
        **kwargs
    }
    
    if ctx.message_id:
        log_data["message_id"] = ctx.message_id
    if ctx.task_id:
        log_data["task_id"] = ctx.task_id
    if ctx.metadata:
        log_data["metadata"] = ctx.metadata

    getattr(logfire, level)(
        f"Agent Operation - {message}",
        **log_data
    )

def log_llm_request(
    agent_id: str,
    prompt: str,
    model: str,
    **kwargs: Any
) -> None:
    """Log an LLM request."""
    with logfire.span(
        "llm_request",
        agent_id=agent_id,
        model=model,
        **kwargs
    ) as span:
        span.set_data("prompt", prompt)

def log_llm_response(
    agent_id: str,
    response: str,
    tokens: int,
    duration: float,
    **kwargs: Any
) -> None:
    """Log an LLM response."""
    logfire.info(
        "LLM Response Received",
        agent_id=agent_id,
        tokens=tokens,
        duration=duration,
        response=response,
        **kwargs
    )

def log_message_bus_event(
    event_type: str,
    sender: str,
    receiver: str,
    message_type: str,
    **kwargs: Any
) -> None:
    """Log a message bus event."""
    logfire.info(
        f"MessageBus Event: {event_type}",
        sender=sender,
        receiver=receiver,
        message_type=message_type,
        **kwargs
    )

def log_error(
    error: Exception,
    context: dict[str, Any],
    level: str = "error"
) -> None:
    """Log an error with context."""
    getattr(logfire, level)(
        "Error Occurred",
        error=str(error),
        error_type=error.__class__.__name__,
        **context
    ) 