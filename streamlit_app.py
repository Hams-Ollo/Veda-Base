#-------------------------------------------------------------------------------------#
# streamlit_app.py
#-------------------------------------------------------------------------------------#
# SETUP:
#
# Setup venv and install the requirements
# 1. Create a virtual environment -> python -m venv venv
# 2. Activate the virtual environment -> .\venv\Scripts\Activate
# 3. Install the requirements -> pip install -r requirements.txt
# 4. Run the streamlit app -> streamlit run streamlit_app.py
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

import streamlit as st
import asyncio
from pathlib import Path
import shutil
import time
from app.markdown_knowledge_object_factory import process_files
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from pyvis.network import Network
import streamlit.components.v1 as components
import json
import hashlib
from typing import Tuple, Optional

def get_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of file content"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def is_duplicate_file(new_file_path: Path, existing_files: list) -> Tuple[bool, Optional[str]]:
    """Check if file is a duplicate based on content hash"""
    new_hash = get_file_hash(new_file_path)
    
    # Check against existing files
    for existing_file in existing_files:
        if existing_file.exists():
            existing_hash = get_file_hash(existing_file)
            if new_hash == existing_hash:
                return True, existing_file.name
    return False, None

def create_knowledge_graph(articles_data):
    """Create an interactive knowledge graph visualization"""
    G = nx.Graph()
    
    # Create nodes for articles and concepts
    for article in articles_data:
        # Add article node
        G.add_node(article['title'], 
                  node_type='article',
                  color='#4CAF50',
                  size=20)
        
        # Add concept nodes and edges
        if 'knowledge_graph' in article:
            for node in article['knowledge_graph']['nodes']:
                if not G.has_node(node):
                    G.add_node(node, 
                             node_type='concept',
                             color='#2196F3',
                             size=15)
                G.add_edge(article['title'], node)
            
            # Add relationships between concepts
            for edge in article['knowledge_graph']['edges']:
                G.add_edge(edge['from'], edge['to'], 
                          relationship=edge['relationship'])
    
    # Convert to Pyvis network for interactive visualization
    net = Network(height="600px", width="100%", 
                 bgcolor="#1E1E1E", font_color="white")
    
    # Add nodes and edges to Pyvis
    for node, attr in G.nodes(data=True):
        net.add_node(node,
                    title=node,
                    color=attr.get('color', '#FFFFFF'),
                    size=attr.get('size', 10))
    
    for edge in G.edges():
        net.add_edge(edge[0], edge[1])
    
    # Generate HTML file
    net.save_graph("knowledge_graph.html")
    
    return G

def librarian_assistant(query: str, knowledge_base: dict) -> str:
    """Simulate a helpful librarian assistant"""
    prompt = f"""As a knowledgeable librarian assistant, help the user with their query about the knowledge base.
    Query: {query}
    
    Knowledge Base Contents:
    {json.dumps(knowledge_base, indent=2)}
    
    Provide a helpful response that:
    1. Answers the user's query
    2. Suggests relevant articles and connections
    3. Offers research directions or insights
    4. Maintains a friendly, scholarly tone
    """
    
    # TODO: Implement actual LLM call here
    # For now, return a placeholder response
    return f"I'd be happy to help you explore that topic. Based on our knowledge base..."

# Configure Streamlit page
st.set_page_config(
    page_title="Knowledge Article Factory",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main app styling */
    .stApp {
        background-color: #1E1E1E;
    }
    
    /* Article view styling */
    .markdown-view {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    
    /* Tag colors */
    .tag-common { color: #ffffff; }
    .tag-fine { color: #4CAF50; }
    .tag-rare { color: #2196F3; }
    .tag-epic { color: #9C27B0; }
    .tag-legendary { color: #FFD700; }
    
    /* Article content container */
    .stMarkdown {
        max-width: 100%;
    }
    
    /* Metadata section styling */
    .metadata-section {
        background-color: #2A2A2A;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 30px;
    }

    /* Remove extra padding */
    .main .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: none;
    }

    /* Clean up sidebar */
    .css-1d391kg {
        padding: 1rem;
    }
    
    /* Style sidebar buttons */
    .stButton > button {
        width: 100%;
        border: none;
        background-color: #2A2A2A;
        color: white;
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 4px;
        text-align: left;
    }
    
    .stButton > button:hover {
        background-color: #3A3A3A;
    }
    
    /* Improve section spacing */
    h2 {
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    
    /* Style dividers */
    hr {
        margin: 2rem 0;
        border-color: #3A3A3A;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state and directory setup
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = []
if 'selected_file' not in st.session_state:
    st.session_state.selected_file = None
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "welcome"

RAG_INIT = Path("RAG_init")
RAG_REFINED = Path("RAG_refined")
RAG_INIT.mkdir(exist_ok=True)
RAG_REFINED.mkdir(exist_ok=True)

# Sidebar
with st.sidebar:
    st.title("📁 Document Management")
    
    # File uploader section
    st.subheader("Upload Files")
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
            is_duplicate, duplicate_name = is_duplicate_file(file_path, existing_files)
            
            if is_duplicate:
                duplicates.append((file.name, duplicate_name))
            else:
                new_files.append(file_path)
        
        # Report duplicate findings and show processing options
        if duplicates:
            st.warning("⚠️ Duplicate files detected:")
            for new_name, existing_name in duplicates:
                st.write(f"- '{new_name}' matches existing file '{existing_name}'")
            
            # Processing options
            st.write("Choose processing option:")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚀 Process New Files Only", help="Process only non-duplicate files", use_container_width=True):
                    with st.spinner("Processing new files..."):
                        success, result = asyncio.run(process_files())
                        if success:
                            st.session_state.processed_files = list(RAG_REFINED.glob("*.md"))
                            st.session_state.processing_complete = True
                            st.session_state.current_view = "article"
                            st.success(f"✅ Processed {result['stats']['successful']} new files successfully!")
            with col2:
                if st.button("🚀 Process All Files", help="Process all files including duplicates", use_container_width=True):
                    # Keep all files including duplicates
                    for file_path in all_files:
                        if not file_path.exists():  # Recreate any removed duplicate files
                            with open(file_path, "wb") as f:
                                f.write(uploaded_files[next(i for i, f in enumerate(uploaded_files) if f.name == file_path.name)].getvalue())
                    with st.spinner("Processing all files..."):
                        success, result = asyncio.run(process_files())
                        if success:
                            st.session_state.processed_files = list(RAG_REFINED.glob("*.md"))
                            st.session_state.processing_complete = True
                            st.session_state.current_view = "article"
                            st.success(f"✅ Processed {result['stats']['successful']} files successfully!")
        
        elif new_files:  # No duplicates found
            if st.button("🚀 Process Documents", type="primary", use_container_width=True):
                with st.spinner("Processing your documents..."):
                    success, result = asyncio.run(process_files())
                    if success:
                        st.session_state.processed_files = list(RAG_REFINED.glob("*.md"))
                        st.session_state.processing_complete = True
                        st.session_state.current_view = "article"
                        st.success(f"✅ Processed {result['stats']['successful']} files successfully!")
                        if result['stats']['failed'] > 0:
                            st.warning(f"⚠️ {result['stats']['failed']} files failed to process")
                    else:
                        st.error("❌ Processing failed. Please try again.")

    # Cleanup buttons
    st.divider()
    st.subheader("🧹 Cleanup Options")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Uploads", use_container_width=True, help="Remove all files from RAG_init folder"):
            try:
                files = list(RAG_INIT.glob("*"))
                for f in files:
                    f.unlink()
                st.session_state.uploaded_files = []
                st.session_state.duplicates = []
                st.session_state.new_files = []
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
                st.session_state.selected_file = None
                st.session_state.current_view = "welcome"
                st.success(f"✅ Removed {len(files)} processed files")
            except Exception as e:
                st.error(f"❌ Error clearing processed files: {str(e)}")
    
    # Show processed files
    if st.session_state.processed_files:
        st.divider()
        st.subheader("📑 Processed Articles")
        for file in st.session_state.processed_files:
            if st.button(f"📄 {file.stem}", key=file.name, use_container_width=True):
                st.session_state.selected_file = file
                st.session_state.current_view = "article"

# Main content area
if st.session_state.processed_files:
    # Add tabs for different views at the top
    tab1, tab2, tab3 = st.tabs(["📑 Article View", "🕸️ Knowledge Graph", "🎓 Librarian Assistant"])
    
    with tab1:
        if st.session_state.selected_file:
            # Article display code here
            content = st.session_state.selected_file.read_text(encoding='utf-8')
            parts = content.split('---')
            if len(parts) >= 2:
                metadata = parts[0]
                body = '---'.join(parts[1:])
                
                with st.container():
                    st.markdown('<div class="metadata-section">', unsafe_allow_html=True)
                    st.markdown("## 📌 Article Metadata")
                    for line in metadata.strip().split('\n'):
                        if line.startswith('Tags:'):
                            st.markdown("### 🏷️ Tags")
                            tags_section = '\n'.join(line.strip() for line in metadata.split('Tags:')[1].strip().split('\n'))
                            st.markdown(f"```\n{tags_section}\n```")
                        elif line.strip():
                            st.markdown(f"**{line.strip()}**")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("## 📝 Knowledge Article")
                body_lines = body.split('\n')
                cleaned_body = []
                skip_next = False
                for line in body_lines:
                    if "Knowledge Article" in line:
                        skip_next = True
                        continue
                    if skip_next and line.strip() == "":
                        skip_next = False
                        continue
                    cleaned_body.append(line)
                
                st.markdown('\n'.join(cleaned_body))
            else:
                st.markdown(content)
        else:
            st.info("👈 Select an article from the sidebar to view its contents")
    
    with tab2:
        st.header("Knowledge Graph Visualization")
        st.markdown("""
        Explore connections between articles, concepts, and themes in your knowledge base.
        - 🟢 Green nodes are articles
        - 🔵 Blue nodes are concepts
        - Lines show relationships between nodes
        """)
        
        # Create and display knowledge graph
        articles_data = []
        for file in st.session_state.processed_files:
            content = file.read_text(encoding='utf-8')
            try:
                metadata_section = content.split('---')[0]
                articles_data.append({
                    'title': file.stem,
                    'content': content,
                })
            except Exception as e:
                st.warning(f"Could not parse {file.name}: {str(e)}")
        
        if articles_data:
            graph = create_knowledge_graph(articles_data)
            components.html(open("knowledge_graph.html").read(), height=600)
            
            # Add filters and controls
            st.sidebar.subheader("Graph Controls")
            filter_type = st.sidebar.multiselect(
                "Filter by Type",
                ["Articles", "Concepts", "Themes"],
                default=["Articles", "Concepts"]
            )
    
    with tab3:
        st.header("📚 Librarian Assistant")
        st.markdown("""
        Ask me anything about your knowledge base! I can help you:
        - Find relevant articles and connections
        - Explore themes and concepts
        - Suggest research directions
        - Explain complex relationships
        """)
        
        query = st.text_input("What would you like to know?")
        if query:
            knowledge_base = {
                'articles': articles_data,
                'graph': nx.node_link_data(graph) if 'graph' in locals() else None
            }
            
            response = librarian_assistant(query, knowledge_base)
            
            st.markdown(f"### 🤔 Analysis & Suggestions")
            st.write(response)
            
            st.markdown("### 🔗 Related Content")

else:
    # Welcome screen
    st.title("📚 Knowledge Article Factory")
    st.markdown("Transform your documents into interconnected knowledge articles with AI-powered insights.")
    
    # Main features in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 What It Does
        
        This tool helps you:
        - Convert various document formats into beautiful markdown
        - Automatically generate smart tags and categories
        - Find connections between your documents
        - Create a personal knowledge database
        
        ### 📄 Supported Formats
        - Microsoft Word (`.docx`)
        - PDF documents (`.pdf`)
        - Text files (`.txt`)
        - Markdown files (`.md`)
        - Excel spreadsheets (`.xlsx`, `.csv`)
        - PowerPoint presentations (`.pptx`)
        """)
    
    with col2:
        st.markdown("""
        ### 🎮 RPG-Style Tags
        Your content gets tagged with different rarity levels:
        
        ⚪ **Common** - Basic categories
        🟢 **Fine** - General themes
        🔵 **Rare** - Specific topics
        🟣 **Epic** - Unique insights
        🟡 **Legendary** - Core principles
        
        ### 🔍 Smart Features
        - **Auto-tagging**: AI identifies key themes
        - **Cross-referencing**: Finds related content
        - **Clean formatting**: Consistent, beautiful output
        - **Knowledge Graph**: Builds connections automatically
        """)
    
    # Getting started section
    st.markdown("""
    ---
    ### 🚀 Getting Started
    
    1. **Upload Your Files**
       - Click the upload box in the sidebar
       - Select one or more files
       - Supported formats will be highlighted
    
    2. **Process Your Documents**
       - Click the "Process Documents" button
       - Wait for the AI to analyze your content
       - Watch the progress bar for status
    
    3. **Explore Your Knowledge Base**
       - Click on processed articles to view them
       - Explore tags and connections
       - Use the generated insights
    
    ### 💡 Tips
    - For best results, upload related documents together
    - The AI works better with clear, well-structured content
    - Tags help organize and find your content later
    - Use the cross-references to discover connections
    """)
    
    # Example output preview
    with st.expander("👀 See Example Output"):
        st.markdown("""
        ```markdown
        Title: 📎 Understanding Ancient Wisdom
        Created: ⏰ 2024-03-20 14:30
        Tags: 🏷️
        ⚪ #philosophy #ancient-texts #wisdom  # Common
        🟢 #moral-teachings #life-lessons  # Fine
        🔵 #vedic-knowledge #dharmic-principles  # Rare
        🟣 #karmic-cycle #duty-and-destiny  # Epic
        🟡 #universal-truth  # Legendary

        ## 📝 Knowledge Article
        [Your transformed content appears here...]

        ## 🔗 References
        - Connected to 3 related documents
        - Original source preserved
        ```
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Made with ❤️ by Your Knowledge Factory Team</p>
    <p style='font-size: 0.8em'>Powered by AI • Inspired by the Great Library of Alexandria</p>
</div>
""", unsafe_allow_html=True) 