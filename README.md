# 📚 Library of Alexandria

> 🌟 A multi-agent system for knowledge management and document processing, powered by advanced AI and semantic analysis.

## ✨ Features

- 🤖 Multi-Agent System Architecture
- 📄 Document Processing and Analysis
- 🕸️ Knowledge Graph Generation
- 🏷️ Taxonomy Management
- 📊 Interactive Visualization
- 📈 Real-time System Monitoring
- 🚌 Asynchronous Message Bus
- 🔍 Semantic Search and Analysis
- 🎯 Automated Tag Suggestions
- 🔄 Dynamic Content Processing
- 🧠 Context-Aware Categorization
- 📱 Modern Streamlit Interface
- 🔮 Vector Similarity Search

## 🧩 Components

- **👨‍💼 Librarian Prime**: Main orchestrator agent for system coordination
- **🧠 Domain Specialists**: Specialized knowledge processing agents for different domains
- **📝 Document Processors**: Document handling and analysis with multi-format support
- **🌐 Knowledge Graph**: Semantic relationship management with graph visualization
- **🗂️ Taxonomy Master**: Hierarchical classification and tagging system
- **🚌 Message Bus**: Asynchronous communication system between agents
- **📊 Performance Monitor**: System-wide metrics and resource tracking
- **🔒 Security Manager**: Access control and data protection
- **💾 Vector Store**: ChromaDB-powered semantic search and retrieval

## 📋 Prerequisites

- 🐍 Python 3.8 or higher
- 🌱 Virtual environment (recommended)
- 🔑 Groq API key for AI capabilities
- 🗄 ChromaDB (v0.4.22 or higher)
- 🗄️ PostgreSQL (optional, for advanced storage)
- 📦 Docker (recommended for deployment)

## 🚀 Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/library-of-alexandria.git
cd library-of-alexandria
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
# Install the package
pip install -e .

# Then install additional dependencies
pip install -r requirements.txt

# For development (includes testing and documentation tools)
pip install -r test-requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:

- `🔐 GROQ_API_KEY`: Your Groq API key
- `🐛 DEBUG`: Set to false in production
- `📝 LOG_LEVEL`: Recommended INFO in production
- `🔒 SECURITY_KEY`: For secure communications
- `📊 MONITORING_ENABLED`: Enable performance tracking
- `💾 CHROMA_DB_DIR`: ChromaDB storage directory
- Other variables as specified in .env.example

## 🎮 Running the Application

### Development Mode

```bash
python -m streamlit run app/frontend/streamlit_app.py
```

### Production Mode (with Docker)

```bash
docker-compose up -d
```

Access the application at: `http://localhost:8501`

## 🏗️ System Architecture

### 🤖 Multi-Agent System

- 🚌 Asynchronous message bus with priority routing
- 🧩 Modular agent system with specialized capabilities
- ⚖️ Dynamic agent scaling and load balancing
- 🔄 Fault tolerance and error recovery
- 📊 Performance monitoring and metrics

### 📄 Document Processing

- 📦 Multi-format support (Markdown, PDF, DOCX, etc.)
- 🔄 Parallel processing capabilities
- 📑 Content extraction and analysis
- 🔗 Semantic relationship detection
- 🏷️ Automatic tagging and classification

### 🌐 Knowledge Graph

- 📊 Interactive visualization
- 🔍 Optimized query patterns
- 🛣️ Path finding and relationship analysis
- 💾 Caching for frequently accessed nodes
- 🔄 Real-time graph updates

### 🗂️ Taxonomy System

- 📚 Hierarchical classification
- 🤖 AI-powered tag suggestions
- 🧠 Context-aware categorization
- 🔗 Dynamic relationship management

### 💾 Vector Store

- 📚 ChromaDB-powered semantic storage
- 🔍 Efficient similarity search
- 📊 Vector embeddings management
- 🔄 Real-time updates and indexing
- 🎯 Contextual retrieval

## 👨‍💻 Development

### Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit
pytest tests/integration
pytest tests/performance
```

### Code Quality

```bash
# Format code
black .
isort .

# Static analysis
flake8
mypy .

# Security checks
bandit -r .
```

### Performance Testing

```bash
# Run performance benchmarks
python run_performance_tests.py

# Run stress tests
python run_stress_tests.py
```

## 📁 Project Structure

```curl
library-of-alexandria/
├── app/
│   ├── agents/          # 🤖 Multi-agent system
│   ├── core/           # ⚙️ Core functionality
│   ├── frontend/       # 🎨 Streamlit interface
│   └── utils/          # 🔧 Utility functions
├── docs/               # 📚 Documentation
│   ├── api/           # 📘 API documentation
│   └── architecture/  # 🏗️ Design decisions
├── tests/             # 🧪 Test suites
│   ├── unit/         # 🔬 Unit tests
│   ├── integration/  # 🔗 Integration tests
│   └── performance/  # ⚡ Performance tests
└── monitoring/        # 📊 Performance metrics
```

## 🚧 Current Development Focus

1. 🎯 Priority 1 (Immediate)
   - Comprehensive error handling
   - Performance monitoring system
   - Code optimization
   - Test coverage enhancement

2. 🔄 Priority 2 (Short-term)
   - Docker containerization
   - Caching implementation
   - API documentation
   - Automated testing

3. 🔮 Priority 3 (Long-term)
   - Automated scaling
   - Monitoring dashboard
   - CI/CD pipeline
   - Security enhancements

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- 📚 Inspired by the Great Library of Alexandria
- 🎨 Built with Streamlit's amazing framework
- 🧠 Powered by Groq's LLM capabilities
- 💫 Special thanks to the open-source community

## 💬 Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](../../issues)
- 📧 [Contact Team](mailto:team@libraryofalexandria.ai)

---

Made with ❤️ by the Knowledge Factory Team
