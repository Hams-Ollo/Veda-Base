# 📚 Library of Alexandria

> 🌟 A multi-agent system for knowledge management and document processing, featuring an advanced React frontend and FastAPI backend.

## ✨ Features

- 🤖 Multi-Agent System Architecture
- 📄 Document Processing and Analysis
- 🕸️ Knowledge Graph Generation
- 🏷️ Taxonomy Management
- 📱 Interactive React-based UI
- 🔄 Real-time Processing Updates via WebSocket
- 📨 Asynchronous Message Bus
- 🔍 Semantic Search and Analysis

## 🛠️ Tech Stack

### Backend

- 🐍 Python 3.8+
- ⚡ FastAPI
- 🗃️ ChromaDB for vector storage
- 🔄 AsyncIO for concurrent processing
- 🔌 WebSocket support for real-time updates

### Frontend

- ⚛️ Next.js 14
- 🎨 React 18
- 💅 TailwindCSS
- 🔄 React Query for data fetching
- 🔌 WebSocket integration
- 📥 Drag-and-drop file upload

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

1. 🐍 Python 3.8 or higher
2. 🌱 Node.js 18 or higher
3. 🐋 Docker (recommended for deployment)
4. 🔄 Redis (optional, for caching)

## 📁 Project Structure

```curl
library-of-alexandria/
├── app/                    # Backend application
│   ├── api/               # FastAPI routes and WebSocket
│   ├── agents/            # Multi-agent system components
│   ├── core/              # Core processing logic
│   └── utils/             # Shared utilities
├── frontend/              # React frontend application
│   ├── src/
│   │   ├── app/          # Next.js pages
│   │   ├── components/   # React components
│   │   ├── services/     # API integration
│   │   └── hooks/        # Custom React hooks
└── docs/                  # Documentation
```

## 🚀 Installation

### Backend Setup

1. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

### Frontend Setup

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Configure environment variables:

   ```bash
   cp .env.example .env.local
   # Edit .env.local with your settings
   ```

## 💻 Development

### Running the Backend

```bash
uvicorn app.main:app --reload
```

### Running the Frontend

```bash
cd frontend
npm run dev
```

The application will be available at:

- 🌐 Frontend: <http://localhost:3000>
- 🔌 Backend API: <http://localhost:8000>
- 📚 API Documentation: <http://localhost:8000/docs>

## 🎯 Features in Detail

### Document Processing

- 📄 Support for multiple document formats (PDF, DOCX, MD, TEX, HTML)
- ⚡ Real-time processing status updates
- 📦 Batch processing capabilities
- 📊 Progress tracking and error handling

### User Interface

- 🎨 Modern, responsive design
- 📥 Drag-and-drop file upload
- 📊 Real-time processing progress
- 📈 Interactive visualizations
- ⚠️ Error handling and feedback

### API Integration

- 🔌 RESTful endpoints for document management
- 🔄 WebSocket connections for real-time updates
- 🛡️ Type-safe API integration with TypeScript
- 🚨 Comprehensive error handling

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💬 Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](../../issues)
- 📧 [Contact Team](mailto:team@libraryofalexandria.ai)
- 💻 Open an issue in the GitHub repository or contact the maintainers

## 🙏 Acknowledgments

- 📚 Inspired by the Great Library of Alexandria
- 🎨 Built with Streamlit's amazing framework
- 🧠 Powered by Groq's LLM capabilities
- 💫 Special thanks to the open-source community

---

Made with ❤️ by the Knowledge Factory Team
