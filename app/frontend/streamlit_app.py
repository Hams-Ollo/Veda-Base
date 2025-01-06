#-------------------------------------------------------------------------------------#
# streamlit_app.py
#-------------------------------------------------------------------------------------#
# SETUP:
#
# Setup venv and install the requirements
# 1. Create a virtual environment -> python -m venv venv
# 2. Activate the virtual environment -> .\venv\Scripts\Activate
# 3. Install the requirements -> pip install -r requirements.txt
# 4. Run the streamlit app -> streamlit run app/frontend/streamlit_app.py
#
# Git Commands:
# 1. Initialize repository -> git init
# 2. Add files to staging -> git add .
# 3. Commit changes -> git commit -m "your message"
# 4. Create new branch -> git checkout -b branch-name
# 5. Switch branches -> git checkout branch-name
# 6. Push to remote -> git push -u origin branch-name
# 7. Pull latest changes -> git pull origin branch-name
# 8. Check status -> git status
# 9. View commit history -> git log
#-------------------------------------------------------------------------------------#

"""Streamlit frontend for the Library of Alexandria multi-agent system."""

import streamlit as st
import asyncio
from typing import Dict, List, Optional
import plotly.graph_objects as go
import networkx as nx
from datetime import datetime

# Import our agent factories and message bus
from app.agents.message_bus import MessageBus
from app.agents.librarian_prime import LibrarianPrime
from app.agents.domain_specialist_factory import DomainSpecialistFactory
from app.agents.document_processor_factory import DocumentProcessorFactory
from app.agents.knowledge_graph_factory import KnowledgeGraphFactory
from app.agents.taxonomy_master_factory import TaxonomyMasterFactory

print("🚀 Starting Library of Alexandria Multi-Agent System...")

# Initialize session state
if 'initialized' not in st.session_state:
    print("🔧 Initializing session state...")
    st.session_state.initialized = False
    st.session_state.message_bus = None
    st.session_state.librarian = None
    st.session_state.domain_specialist_factory = None
    st.session_state.document_processor_factory = None
    st.session_state.knowledge_graph_factory = None
    st.session_state.taxonomy_master_factory = None

def initialize_system():
    """Initialize the multi-agent system components."""
    if not st.session_state.initialized:
        print("🌟 Creating Message Bus...")
        st.session_state.message_bus = MessageBus()
        
        print("👨‍💼 Initializing Librarian Prime Agent...")
        st.session_state.librarian = LibrarianPrime("librarian_prime")
        
        print("🏭 Setting up Domain Specialist Factory...")
        st.session_state.domain_specialist_factory = DomainSpecialistFactory(st.session_state.message_bus)
        
        print("📄 Creating Document Processor Factory...")
        st.session_state.document_processor_factory = DocumentProcessorFactory(st.session_state.message_bus)
        
        print("🕸️ Initializing Knowledge Graph Factory...")
        st.session_state.knowledge_graph_factory = KnowledgeGraphFactory(st.session_state.message_bus)
        
        print("🏷️ Setting up Taxonomy Master Factory...")
        st.session_state.taxonomy_master_factory = TaxonomyMasterFactory(st.session_state.message_bus)
        
        # Start the message bus
        print("🚦 Starting Message Bus...")
        asyncio.run(st.session_state.message_bus.start())
        st.session_state.initialized = True
        print("✅ System initialization complete!")

def main():
    """Main Streamlit application."""
    print("📚 Loading Library of Alexandria interface...")
    st.title("Library of Alexandria")
    st.sidebar.title("Navigation")

    # Initialize the system
    initialize_system()

    # Navigation
    pages = {
        "Dashboard": show_dashboard,
        "Documents": show_documents,
        "Knowledge Graph": show_knowledge_graph,
        "Taxonomy": show_taxonomy,
        "Agent Status": show_agent_status,
        "System Metrics": show_system_metrics
    }
    
    selection = st.sidebar.radio("Go to", list(pages.keys()))
    print(f"🔄 Navigating to {selection} page...")
    pages[selection]()

def show_dashboard():
    """Show the main dashboard."""
    print("📊 Loading Dashboard...")
    st.header("Dashboard")
    
    # System Status
    print("📈 Updating system metrics...")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Active Agents", len(st.session_state.message_bus.registered_agents))
    with col2:
        st.metric("Pending Messages", st.session_state.message_bus.queue_size)
    with col3:
        st.metric("Active Processors", len(st.session_state.document_processor_factory.active_processors))

    # Recent Activity
    st.subheader("Recent Activity")
    # TODO: Implement activity feed

    # Quick Actions
    st.subheader("Quick Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Process New Document"):
            st.session_state.current_page = "Documents"
    with col2:
        if st.button("View Knowledge Graph"):
            st.session_state.current_page = "Knowledge Graph"

def show_documents():
    """Show document management interface."""
    print("📑 Loading Document Management interface...")
    st.header("Document Management")
    
    # Upload new document
    print("📤 Setting up document upload...")
    uploaded_file = st.file_uploader("Upload Document", type=['txt', 'md', 'pdf'])
    if uploaded_file:
        process_document(uploaded_file)

    # Document list
    print("📋 Loading document list...")
    st.subheader("Recent Documents")
    # TODO: Implement document list

def show_knowledge_graph():
    """Show knowledge graph visualization."""
    print("🌐 Loading Knowledge Graph visualization...")
    st.header("Knowledge Graph")
    
    # Graph controls
    print("🎮 Setting up graph controls...")
    st.sidebar.subheader("Graph Controls")
    layout = st.sidebar.selectbox("Layout", ["force", "circular", "random"])
    
    # Create graph visualization
    print(f"🎨 Creating graph visualization with {layout} layout...")
    graph = create_knowledge_graph_visualization(layout)
    st.plotly_chart(graph)

def show_taxonomy():
    """Show taxonomy management interface."""
    print("🌳 Loading Taxonomy Management interface...")
    st.header("Taxonomy Management")
    
    # Taxonomy tree
    print("🌲 Loading taxonomy tree...")
    st.subheader("Taxonomy Structure")
    # TODO: Implement taxonomy tree visualization
    
    # Tag management
    print("🏷️ Setting up tag management...")
    st.subheader("Tag Management")
    # TODO: Implement tag management interface

def show_agent_status():
    """Show agent status and management interface."""
    print("👥 Loading Agent Status interface...")
    st.header("Agent Status")
    
    # Agent list
    print("📊 Loading agent status list...")
    for agent_id in st.session_state.message_bus.registered_agents:
        st.subheader(f"Agent: {agent_id}")
        print(f"ℹ️ Loading status for agent: {agent_id}")
        # TODO: Show agent details and status

def show_system_metrics():
    """Show system performance metrics."""
    print("📊 Loading System Metrics interface...")
    st.header("System Metrics")
    
    # Performance metrics
    print("📈 Loading performance metrics...")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Message Processing Rate", "100/s")
    with col2:
        st.metric("Average Response Time", "150ms")
    
    # Charts
    print("📊 Loading system load charts...")
    st.subheader("System Load")
    # TODO: Implement system metrics charts

def process_document(uploaded_file):
    """Process an uploaded document."""
    print(f"📥 Processing new document: {uploaded_file.name}")
    st.info("Processing document...")
    # TODO: Implement document processing
    print("⚙️ Document processing pipeline started...")

def create_knowledge_graph_visualization(layout: str) -> go.Figure:
    """Create a visualization of the knowledge graph."""
    print(f"🔄 Creating knowledge graph with {layout} layout...")
    # TODO: Implement graph visualization
    # Placeholder implementation
    G = nx.Graph()
    pos = nx.spring_layout(G)
    
    fig = go.Figure()
    # Add nodes and edges
    print("✨ Graph visualization complete")
    return fig

if __name__ == "__main__":
    print("🎯 Starting main application loop...")
    main()
    print("👋 Application terminated.") 