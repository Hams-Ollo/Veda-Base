# Library of Alexandria

A multi-agent system for knowledge management and document processing, powered by advanced AI and semantic analysis.

## Features

- Multi-Agent System Architecture
- Document Processing and Analysis
- Knowledge Graph Generation
- Taxonomy Management
- Interactive Visualization
- Real-time System Monitoring
- Asynchronous Message Bus
- Semantic Search and Analysis

## Components

- **Librarian Prime**: Main orchestrator agent for system coordination
- **Domain Specialists**: Specialized knowledge processing agents for different domains
- **Document Processors**: Document handling and analysis with multi-format support
- **Knowledge Graph**: Semantic relationship management with graph visualization
- **Taxonomy Master**: Hierarchical classification and tagging system

## Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)
- Groq API key for AI capabilities
- PostgreSQL (optional, for advanced storage)

## Setup

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

First, install the package in development mode:

```bash
# Install the package
pip install -e .

# Then install additional dependencies
pip install -r requirements.txt
```

For development installation (includes testing and documentation tools):

```bash
pip install -e ".[dev]"
```

### 4. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:

- `GROQ_API_KEY`: Your Groq API key
- `DEBUG`: Set to false in production
- `LOG_LEVEL`: Recommended INFO in production
- Other variables as specified in .env.example

## Running the Application

### 1. Start the Streamlit frontend

```bash
python -m streamlit run app/frontend/streamlit_app.py
```

### 2. Access the application

Open your browser and navigate to:

```curl
http://localhost:8501
```

## System Architecture

### Multi-Agent System

- Asynchronous message bus for inter-agent communication
- Modular agent system with specialized capabilities
- Dynamic agent scaling and load balancing
- Fault tolerance and error recovery

### Document Processing Pipeline

- Multi-format document support (Markdown, PDF, DOCX, etc.)
- Content extraction and analysis
- Semantic relationship detection
- Automatic tagging and classification

### Knowledge Graph

- Semantic relationship visualization
- Interactive graph exploration
- Path finding and relationship analysis
- Dynamic graph updates

### Taxonomy System

- Hierarchical classification
- Automated tag suggestions
- Context-aware categorization
- Tag relationship management

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
black .
isort .
flake8
mypy .
```

### Documentation

```bash
mkdocs serve
```

## Project Structure

```curl
library-of-alexandria/
├── app/
│   ├── agents/             # Multi-agent system components
│   ├── core/              # Core functionality and utilities
│   └── frontend/          # Streamlit frontend application
├── docs/                  # Documentation
├── tests/                 # Test suite
└── data/                  # Data storage (git-ignored)
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by the Great Library of Alexandria
- Built with Streamlit's amazing framework
- Powered by Groq's LLM capabilities
- Special thanks to the open-source community

## Support

For support and questions:

- Open an issue in the repository
- Check the documentation
- Contact the development team

---

Made with ❤️ by the Knowledge Factory Team
