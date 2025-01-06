"""Test configuration and fixtures for the multi-agent system."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path

from app.agents import (
    LibrarianPrime,
    ContentCurator,
    TaxonomyMaster,
    ConnectionWeaver,
    AnalyticsSage,
    KnowledgeGuardian,
    LearningCompanion,
    MediaMaestro,
    MessageBus
)
from app.core import (
    SharedDependencies,
    VectorStore,
    DocumentStore,
    TagRegistry,
    KnowledgeGraph,
    AnalyticsEngine,
    ContentValidator,
    LearningPathGenerator,
    MediaProcessor
)

@pytest.fixture
async def message_bus():
    """Create a message bus instance for testing."""
    bus = MessageBus()
    await bus.start()
    yield bus
    await bus.stop()

@pytest.fixture
def shared_dependencies():
    """Create shared dependencies for testing."""
    return SharedDependencies(
        vector_store=MagicMock(spec=VectorStore),
        document_store=MagicMock(spec=DocumentStore),
        tag_registry=MagicMock(spec=TagRegistry),
        knowledge_graph=MagicMock(spec=KnowledgeGraph)
    )

@pytest.fixture
async def librarian_prime(message_bus, shared_dependencies):
    """Create a Librarian Prime agent instance for testing."""
    agent = LibrarianPrime(
        agent_id="librarian_prime",
        model_name="gpt-4",
        shared_dependencies=shared_dependencies
    )
    await message_bus.register_agent(agent)
    yield agent
    await message_bus.unregister_agent(agent)

@pytest.fixture
async def content_curator(message_bus, shared_dependencies):
    """Create a Content Curator agent instance for testing."""
    agent = ContentCurator(
        agent_id="content_curator",
        model_name="gpt-4",
        shared_dependencies=shared_dependencies
    )
    await message_bus.register_agent(agent)
    yield agent
    await message_bus.unregister_agent(agent)

@pytest.fixture
async def taxonomy_master(message_bus, shared_dependencies):
    """Create a Taxonomy Master agent instance for testing."""
    agent = TaxonomyMaster(
        agent_id="taxonomy_master",
        model_name="gpt-4",
        shared_dependencies=shared_dependencies
    )
    await message_bus.register_agent(agent)
    yield agent
    await message_bus.unregister_agent(agent)

@pytest.fixture
async def connection_weaver(message_bus, shared_dependencies):
    """Create a Connection Weaver agent instance for testing."""
    agent = ConnectionWeaver(
        agent_id="connection_weaver",
        model_name="gpt-4",
        shared_dependencies=shared_dependencies
    )
    await message_bus.register_agent(agent)
    yield agent
    await message_bus.unregister_agent(agent)

@pytest.fixture
async def analytics_sage(message_bus, shared_dependencies):
    """Create an Analytics Sage agent instance for testing."""
    agent = AnalyticsSage(
        agent_id="analytics_sage",
        model_name="gpt-4",
        shared_dependencies=shared_dependencies
    )
    await message_bus.register_agent(agent)
    yield agent
    await message_bus.unregister_agent(agent)

@pytest.fixture
async def knowledge_guardian(message_bus, shared_dependencies):
    """Create a Knowledge Guardian agent instance for testing."""
    agent = KnowledgeGuardian(
        agent_id="knowledge_guardian",
        model_name="gpt-4",
        shared_dependencies=shared_dependencies
    )
    await message_bus.register_agent(agent)
    yield agent
    await message_bus.unregister_agent(agent)

@pytest.fixture
async def learning_companion(message_bus, shared_dependencies):
    """Create a Learning Companion agent instance for testing."""
    agent = LearningCompanion(
        agent_id="learning_companion",
        model_name="gpt-4",
        shared_dependencies=shared_dependencies
    )
    await message_bus.register_agent(agent)
    yield agent
    await message_bus.unregister_agent(agent)

@pytest.fixture
async def media_maestro(message_bus, shared_dependencies):
    """Create a Media Maestro agent instance for testing."""
    agent = MediaMaestro(
        agent_id="media_maestro",
        model_name="gpt-4",
        shared_dependencies=shared_dependencies
    )
    await message_bus.register_agent(agent)
    yield agent
    await message_bus.unregister_agent(agent)

@pytest.fixture
def test_data_dir():
    """Create a temporary directory for test data."""
    return Path(__file__).parent / "test_data"

@pytest.fixture(autouse=True)
async def setup_teardown():
    """Setup and teardown for each test."""
    # Setup test environment
    yield
    # Cleanup after test 