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
# 5. Run the streamlit app -> python -m streamlit run app/frontend/streamlit_app.py
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
from pathlib import Path
import shutil
import time
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from pyvis.network import Network
import streamlit.components.v1 as components
import json
import hashlib
from typing import Tuple, Optional, List, Dict

# Multi-agent system imports
from app.agents.message_bus import MessageBus
from app.agents.librarian_prime import LibrarianPrime
from app.agents.domain_specialist_factory import DomainSpecialistFactory
from app.agents.document_processor_factory import DocumentProcessorFactory
from app.agents.knowledge_graph_factory import KnowledgeGraphFactory
from app.agents.taxonomy_master_factory import TaxonomyMasterFactory

# Configure Streamlit page
st.set_page_config(
    page_title="Library of Alexandria",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Main app styling */
    .stApp {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #252526;
    }
    
    /* Global button styling */
    .stButton button {
        background-color: #0066B5 !important;
        color: white !important;
        border: none !important;
        padding: 10px 20px !important;
        border-radius: 5px !important;
        height: 42px !important;  /* Consistent height */
        transition: background-color 0.3s !important;
    }
    
    .stButton button:hover {
        background-color: #0077CC !important;
    }
    
    /* Custom button styling */
    .nav-button {
        width: 100%;
        padding: 10px 15px;
        background-color: #2D2D2D;
        border: none;
        border-radius: 5px;
        color: white;
        text-align: left;
        margin: 5px 0;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    
    .nav-button:hover {
        background-color: #3D3D3D;
    }
    
    .nav-button.active {
        background-color: #0066B5;
    }
    
    /* Container styling */
    .stMarkdown {
        color: #FFFFFF;
    }
    
    .content-container {
        background-color: #2D2D2D;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    /* Metric styling */
    .metric-container {
        background-color: #252526;
        padding: 15px;
        border-radius: 8px;
        margin: 5px;
    }
    
    /* Chat specific styling */
    .chat-container {
        margin-bottom: 100px;  /* Space for input box */
    }
    
    .chat-message {
        padding: 10px 15px;
        border-radius: 15px;
        margin: 10px 0;
        display: flex;
        align-items: center;
    }
    
    .user-message {
        background-color: #0066B5;
        margin-left: auto;
        margin-right: 0;
        max-width: 70%;
    }
    
    .assistant-message {
        background-color: #2D2D2D;
        margin-right: auto;
        margin-left: 0;
        max-width: 70%;
    }
    
    .chat-input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #1E1E1E;
        padding: 20px;
        z-index: 100;
    }
    
    .stTextInput input {
        background-color: #2D2D2D;
        color: white;
        border: 1px solid #3D3D3D;
        border-radius: 5px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

print("🚀 Starting Library of Alexandria Multi-Agent System...")

# Initialize session state and directory setup
if 'initialized' not in st.session_state:
    print("🔧 Initializing session state...")
    st.session_state.initialized = False
    st.session_state.message_bus = None
    st.session_state.librarian = None
    st.session_state.domain_specialist_factory = None
    st.session_state.document_processor_factory = None
    st.session_state.knowledge_graph_factory = None
    st.session_state.taxonomy_master_factory = None
    st.session_state.processed_files = []
    st.session_state.selected_file = None
    st.session_state.processing_complete = False
    st.session_state.current_page = "🏠 Dashboard"  # Set default page
    st.session_state.chat_history = []  # Initialize chat history
    st.session_state.session_id = hashlib.md5(str(time.time()).encode()).hexdigest()

async def initialize_system():
    """Initialize the multi-agent system components."""
    if not st.session_state.initialized:
        try:
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
            await st.session_state.message_bus.start()
            
            st.session_state.initialized = True
            print("✅ System initialization complete!")
            return True
        except Exception as e:
            print(f"❌ Error initializing system: {str(e)}")
            return False

RAG_INIT = Path("RAG_init")
RAG_REFINED = Path("RAG_refined")
RAG_INIT.mkdir(exist_ok=True)
RAG_REFINED.mkdir(exist_ok=True)

# Initialize the system if needed
if not st.session_state.initialized:
    asyncio.run(initialize_system())

def main():
    """Main Streamlit application."""
    st.title("Library of Alexandria")
    
    # Navigation
    pages = {
        "🏠 Dashboard": show_dashboard,
        "📄 Documents": show_documents,
        "🕸️ Knowledge Graph": show_knowledge_graph,
        "🤖 Librarian Chat": show_librarian_chat
    }
    
    # Create custom navigation buttons
    st.sidebar.title("Navigation")
    
    # Ensure current_page is set
    if "current_page" not in st.session_state:
        st.session_state.current_page = "🏠 Dashboard"
    
    # Create navigation buttons
    for page_name in pages:
        if st.sidebar.button(
            page_name, 
            key=page_name, 
            help=f"Go to {page_name}", 
            use_container_width=True,
            type="primary" if st.session_state.current_page == page_name else "secondary"
        ):
            st.session_state.current_page = page_name
            st.rerun()
    
    # Show selected page
    pages[st.session_state.current_page]()

def show_dashboard():
    """Show the main dashboard."""
    st.header("🏠 Welcome to Library of Alexandria")
    
    # Welcome message
    with st.container():
        st.markdown("""
        Welcome to your personal knowledge repository! This system helps you organize, analyze, and explore your documents 
        using advanced AI agents. Here's how to get started:
        
        1. 📄 **Upload Documents**: Use the Documents page to upload and process your files
        2. 🕸️ **Explore Connections**: View relationships between concepts in the Knowledge Graph
        3. 🤖 **Ask Questions**: Chat with our AI Librarian about your documents
        """)
    
    # System Status
    st.subheader("System Status")
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            with st.container():
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric("Active Agents", len(st.session_state.message_bus.registered_agents))
                st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            with st.container():
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric("Pending Messages", st.session_state.message_bus.queue_size)
                st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            with st.container():
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric("Active Processors", len(st.session_state.document_processor_factory.active_processors))
                st.markdown('</div>', unsafe_allow_html=True)

    # Recent Activity
    st.subheader("Recent Activity")
    with st.container():
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        if not st.session_state.processed_files:
            st.info("No recent activity. Start by uploading some documents!")
        else:
            for file in st.session_state.processed_files[-5:]:  # Show last 5 activities
                st.write(f"📄 Processed: {file.name}")
        st.markdown('</div>', unsafe_allow_html=True)

    # Quick Actions
    st.subheader("Quick Actions")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Process New Document", use_container_width=True):
                st.session_state.current_page = "📄 Documents"
                st.rerun()
        with col2:
            if st.button("🤖 Chat with Librarian", use_container_width=True):
                st.session_state.current_page = "🤖 Librarian Chat"
                st.rerun()

def show_documents():
    """Show document management interface."""
    st.header("📁 Document Management")
    
    # Upload Files section
    st.subheader("Upload Files")
    
    # Multi-file uploader with expanded file type support
    uploaded_files = st.file_uploader(
        "Drag and drop files here",
        accept_multiple_files=True,
        type=['txt', 'md', 'pdf', 'docx', 'csv', 'xlsx', 'pptx'],
        help="Supported formats: TXT, MD, PDF, DOCX, CSV, XLSX, PPTX"
    )
    
    if uploaded_files:
        st.write(f"📥 {len(uploaded_files)} files ready for processing")
        
        # Track duplicates and new files
        duplicates = []
        new_files = []
        all_files = []
        
        # Save and check uploaded files
        for file in uploaded_files:
            file_path = RAG_INIT / file.name
            
            # Save temporarily to check content
            with open(file_path, "wb") as f:
                f.write(file.getvalue())
            all_files.append(file_path)
            
            # Check for duplicates in both input and output directories
            existing_files = list(RAG_INIT.glob("*")) + list(RAG_REFINED.glob("*"))
            is_duplicate = any(
                existing.name == file.name 
                for existing in existing_files 
                if existing.name != file_path.name
            )
            
            if is_duplicate:
                duplicates.append(file.name)
            else:
                new_files.append(file_path)
        
        # Report duplicate findings and show processing options
        if duplicates:
            st.warning("⚠️ Duplicate files detected:")
            for duplicate in duplicates:
                st.write(f"- '{duplicate}' already exists")
            
            # Processing options
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚀 Process New Files Only", help="Process only non-duplicate files", use_container_width=True):
                    with st.spinner("Processing new files..."):
                        success, result = asyncio.run(process_files(new_files))
                        if success:
                            st.session_state.processed_files = list(RAG_REFINED.glob("*.md"))
                            st.success(f"✅ Processed {result['stats']['successful']} new files successfully!")
                            if result['stats']['failed'] > 0:
                                st.error(f"❌ {result['stats']['failed']} files failed to process")
            with col2:
                if st.button("🚀 Process All Files", help="Process all files including duplicates", use_container_width=True):
                    with st.spinner("Processing all files..."):
                        success, result = asyncio.run(process_files(all_files))
                        if success:
                            st.session_state.processed_files = list(RAG_REFINED.glob("*.md"))
                            st.success(f"✅ Processed {result['stats']['successful']} files successfully!")
                            if result['stats']['failed'] > 0:
                                st.error(f"❌ {result['stats']['failed']} files failed to process")
        
        elif new_files:  # No duplicates found
            if st.button("🚀 Process Documents", type="primary", use_container_width=True):
                with st.spinner("Processing your documents..."):
                    success, result = asyncio.run(process_files(new_files))
                    if success:
                        st.session_state.processed_files = list(RAG_REFINED.glob("*.md"))
                        st.success(f"✅ Processed {result['stats']['successful']} files successfully!")
                        if result['stats']['failed'] > 0:
                            st.error(f"❌ {result['stats']['failed']} files failed to process")
    
    # Cleanup Options
    st.divider()
    st.subheader("🧹 Cleanup Options")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Uploads", use_container_width=True, help="Remove all files from RAG_init folder"):
            try:
                files = list(RAG_INIT.glob("*"))
                for f in files:
                    f.unlink()
                st.success(f"✅ Removed {len(files)} files from uploads")
            except Exception as e:
                st.error(f"❌ Error clearing uploads: {str(e)}")
    
    with col2:
        if st.button("🗑️ Clear Processed", use_container_width=True, help="Remove all files from RAG_refined folder"):
            try:
                files = list(RAG_REFINED.glob("*"))
                for f in files:
                    f.unlink()
                st.session_state.processed_files = []
                st.success(f"✅ Removed {len(files)} processed files")
            except Exception as e:
                st.error(f"❌ Error clearing processed files: {str(e)}")
    
    # Show processed files
    if st.session_state.processed_files:
        st.divider()
        st.subheader("📑 Processed Articles")
        for file in st.session_state.processed_files:
            st.write(f"📄 {file.stem}")

async def process_files(files: List[Path]) -> Tuple[bool, Dict]:
    """Process multiple files using the document processor agent."""
    try:
        # Get document processor instance
        processor = st.session_state.document_processor_factory.create_processor()
        
        successful = []
        failed = []
        
        # Process each file
        for file_path in files:
            try:
                # Create processing task
                task = {
                    "file_path": str(file_path),
                    "output_path": str(RAG_REFINED / f"{file_path.stem}.md"),
                    "metadata": {
                        "original_name": file_path.name,
                        "timestamp": time.time()
                    }
                }
                
                # Process the document using process_document method
                result = await processor.process_document(task)
                
                if result and result.get("success", False):
                    successful.append(str(file_path))
                    print(f"✅ Successfully processed: {file_path.name}")
                else:
                    failed.append(str(file_path))
                    error_msg = result.get("error", "Unknown error") if result else "No result returned"
                    print(f"❌ Failed to process {file_path.name}: {error_msg}")
                    
            except Exception as e:
                print(f"❌ Error processing {file_path.name}: {str(e)}")
                failed.append(str(file_path))
        
        # Update session state with processed files
        st.session_state.processed_files = list(RAG_REFINED.glob("*.md"))
        
        return True, {
            "processed_files": successful,
            "failed_files": failed,
            "stats": {
                "total": len(files),
                "successful": len(successful),
                "failed": len(failed)
            }
        }
        
    except Exception as e:
        print(f"❌ Error in process_files: {str(e)}")
        return False, {"error": str(e)}

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

async def process_document(uploaded_file):
    """Process an uploaded document using the multi-agent system."""
    print(f"📥 Processing new document: {uploaded_file.name}")
    st.info("Processing document...")
    
    try:
        # Initialize document processor
        processor = st.session_state.document_processor_factory.create_processor()
        
        # Create processing task
        task = {
            "file_path": str(RAG_INIT / uploaded_file.name),
            "output_path": str(RAG_REFINED / uploaded_file.name),
            "metadata": {
                "original_name": uploaded_file.name,
                "timestamp": time.time()
            }
        }
        
        # Process the document
        print("⚙️ Document processing pipeline started...")
        result = await processor.process_document(task)
        
        if result.get("success"):
            print("✅ Document processing complete")
            return True, result
        else:
            print("❌ Document processing failed")
            return False, result
            
    except Exception as e:
        print(f"❌ Error processing document: {str(e)}")
        return False, {"error": str(e)}

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

def create_knowledge_graph(articles_data):
    """Create an interactive knowledge graph visualization using the Knowledge Graph agent."""
    print("🌐 Creating knowledge graph visualization...")
    
    try:
        # Get knowledge graph instance
        graph_manager = st.session_state.knowledge_graph_factory.create_graph()
        
        # Build graph from articles
        for article in articles_data:
            graph_manager.add_article(article)
        
        # Get the visualization
        net = graph_manager.create_visualization()
        net.save_graph("knowledge_graph.html")
        
        print("✨ Knowledge graph visualization complete")
        return graph_manager.get_graph()
        
    except Exception as e:
        print(f"❌ Error creating knowledge graph: {str(e)}")
        return nx.Graph()

async def librarian_assistant(query: str, knowledge_base: dict) -> str:
    """Use the Librarian Prime agent to assist with queries."""
    try:
        # Get response from Librarian Prime
        response = await st.session_state.librarian.handle_query({
            "query": query,
            "knowledge_base": knowledge_base,
            "context": {
                "timestamp": time.time(),
                "session_id": st.session_state.get("session_id", "default")
            }
        })
        
        return response.get("content", "I apologize, but I couldn't process your query at this time.")
        
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}"

def show_librarian_chat():
    """Show the Librarian Agent chat interface."""
    st.header("🤖 Chat with Your Librarian")
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Chat messages container
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(
                    f"""<div class="chat-message user-message">
                        {message["content"]}
                    </div>""",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""<div class="chat-message assistant-message">
                        {message["content"]}
                    </div>""",
                    unsafe_allow_html=True
                )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    with st.form(key="chat_form", clear_on_submit=True):
        cols = st.columns([8, 1])
        with cols[0]:
            user_input = st.text_input("", placeholder="Ask me anything about your documents...", 
                                     key="chat_input", label_visibility="collapsed")
        with cols[1]:
            submit_button = st.form_submit_button("Send", use_container_width=True)
        
        if submit_button and user_input:
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Get librarian response
            response = asyncio.run(librarian_assistant(
                user_input,
                {"documents": st.session_state.processed_files}
            ))
            
            # Add librarian response to history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            # Rerun to update chat display
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main() 