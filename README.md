# 📚 Library of Alexandria - Knowledge Article Factory

A powerful AI-driven document processing and knowledge management system that transforms various document formats into an interconnected knowledge base with semantic search capabilities and an advanced tiered tagging system.

## 🎯 Features

- 🔄 Multi-format document conversion
- 🤖 AI-powered content analysis and tag suggestions
- 🏷️ Advanced 5-tier tagging system with controlled vocabulary
- 🕸️ Interactive knowledge graph visualization
- 📊 Semantic search capabilities
- 🎓 AI Librarian Assistant
- 🎨 Beautiful, responsive UI with Streamlit

## 🛠️ Technical Stack

- **Frontend**: Streamlit
- **Data Processing**: Python 3.11+
- **AI/ML**:
  - LangChain for document processing
  - Groq's Mixtral-8x7b for tag suggestions
  - Transformers for content analysis
- **Visualization**:
  - Plotly for data visualization
  - PyVis for knowledge graphs
- **Storage**: ChromaDB for vector storage
- **API Integration**: FastAPI
- **Document Processing**:
  - PyPDF for PDF files
  - python-docx for Word documents
  - python-pptx for PowerPoint files

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Virtual Environment (recommended)
- Groq API key (for AI features)

### 🔧 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/Library-of-Alexandria.git
   cd Library-of-Alexandria
   ```

2. **Set up virtual environment**

   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # Linux/MacOS
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   Create a `.env` file in the root directory:

   ```env
   GROQ_API_KEY=your_groq_api_key
   ```

### 🏃‍♂️ Running the Application

1. **Start the Streamlit app**

   ```bash
   streamlit run streamlit_app.py
   ```

2. **Access the web interface**
   - Open your browser and navigate to `http://localhost:8501`
   - The app will also provide a network URL for local network access

## 📁 Project Structure

```curl
Library-of-Alexandria/
├── streamlit_app.py              # Main Streamlit application
├── requirements.txt              # Project dependencies
├── .env                         # Environment variables
├── RAG_init/                   # Initial document storage
├── RAG_refined/                # Processed knowledge articles
└── app/
    ├── markdown_knowledge_object_factory.py
    ├── tagging_system.py        # Core tagging system implementation
    └── tag_suggester.py         # AI-powered tag suggestion system
```

## 🎮 Advanced Tagging System

The application implements a sophisticated 5-tier tagging system with controlled vocabulary and AI-powered suggestions.

### Tag Tiers and Categories

1. ⚪ **Common Tags** (Basic Categorization)
   - **Domain**: Primary field/discipline (e.g., ai, history, psychology)
   - **Era**: Time period (e.g., renaissance, 21st-century)
   - **Format**: Content type (e.g., article, book, podcast)

2. 🟢 **Fine Tags** (General Themes)
   - **Themes**: High-level ideas (e.g., innovation, ethics)
   - **Concepts**: Theoretical frameworks (e.g., neural-networks, stoicism)
   - **Patterns**: Recurring models (e.g., feedback-loops, fractals)

3. 🔵 **Rare Tags** (Specific Topics)
   - **Topics**: Specialized areas (e.g., adversarial-attacks)
   - **Terminology**: Key terms (e.g., rag, latent-space)
   - **Methods**: Techniques (e.g., lstm-optimization)

4. 🟣 **Epic Tags** (Insights & Connections)
   - **Insights**: Key realizations
   - **Connections**: Cross-disciplinary links
   - **Innovations**: Novel approaches

5. 🟡 **Legendary Tags** (Core Principles)
   - **Principles**: Universal truths (e.g., conservation-of-energy)
   - **Paradigms**: Foundational frameworks (e.g., heros-journey)

### AI-Powered Tag Suggestions

- Automatic tag generation using Groq's Mixtral-8x7b model
- Confidence scores for suggested tags
- Explanations for tag relevance
- Tag validation and cleaning
- Controlled vocabulary enforcement

### Tag Network Features

- Bidirectional linking between related content
- Interactive knowledge graph visualization
- Tag relationship discovery
- Content recommendation based on tag relationships

## 🔧 Troubleshooting

Common issues and solutions:

1. **Installation Issues**

   ```bash
   # If you encounter SSL errors
   pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
   ```

2. **Memory Errors**
   - Reduce batch size in processing
   - Clear RAG directories
   - Restart the application

3. **Graph Visualization Issues**
   - Clear browser cache
   - Try a different browser
   - Reduce number of displayed nodes

4. **Tag Suggestion Issues**
   - Ensure GROQ_API_KEY is properly set
   - Check API rate limits
   - Verify content length is within model limits

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by the Great Library of Alexandria
- Built with Streamlit's amazing framework
- Powered by Groq's LLM capabilities
- Special thanks to the open-source community

## 📞 Support

For support and questions:

- 📧 Open an issue in the repository
- 💬 Contact the development team
- 📚 Check the documentation

---

Made with ❤️ by the Knowledge Factory Team
