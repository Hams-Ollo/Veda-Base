# 📚 Library of Alexandria

> 🌟 A modern document processing and knowledge management system with real-time processing capabilities, featuring a React-based frontend and FastAPI backend.

## ✨ Features

### Document Processing
- 📄 Multi-format document support (PDF, DOCX, MD, TEX, HTML)
- 📊 Table detection and extraction from PDFs
- 🖼️ Image extraction and processing
- 📝 Semantic content analysis
- 🔄 Real-time processing status updates
- 📦 Batch processing with progress tracking

### Knowledge Management
- 🤖 Multi-Agent System Architecture
- 🕸️ Knowledge Graph Generation
- 🏷️ Taxonomy Management
- 🔍 Semantic Search and Analysis
- 📨 Asynchronous Message Bus

### User Interface
- ⚛️ Modern React-based UI
- 🔄 Real-time updates via WebSocket
- 📱 Responsive design
- 📊 Live processing statistics
- 🎯 Interactive progress tracking
- ❌ Error handling and recovery

## 🛠️ Tech Stack

### Frontend
- ⚛️ Next.js 14
- 💅 React 18 with TypeScript
- 🎨 TailwindCSS
- 🔄 React Query
- 🔌 Socket.io Client
- 📊 Real-time data visualization

### Backend
- 🐍 Python 3.8+
- ⚡ FastAPI
- 🔄 WebSocket support
- 🗃️ ChromaDB for vector storage
- 🔄 AsyncIO for concurrent processing
- 📝 PyMuPDF for PDF processing
- 📊 Camelot for table extraction

## 🧩 Core Components

### Document Processing
- 📑 Multi-format document handler
- 📊 Table detection system
- 🖼️ Image extraction
- 📝 Content analysis
- 🔄 Batch processing manager

### Agent System
- 👨‍💼 Librarian Prime (System Orchestrator)
- 🧠 Domain Specialists
- 📝 Document Processors
- 🌐 Knowledge Graph Manager
- 🗂️ Taxonomy Master

### Real-time Processing
- 🔄 WebSocket Manager
- 📊 Progress Tracking
- 🚦 Status Updates
- ❌ Error Handling
- 🧹 Cleanup Management

## 📋 Prerequisites

1. 🐍 Python 3.8 or higher
2. 🌱 Node.js 18 or higher
3. 📦 npm or yarn
4. 🗃️ ChromaDB
5. 🐘 PostgreSQL (optional)

## 🚀 Quick Start

### Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at:
- 🌐 Frontend: http://localhost:3000
- 🔌 Backend API: http://localhost:8000
- 📚 API Documentation: http://localhost:8000/docs

## 📁 Project Structure
```
library-of-alexandria/
├── app/                    # Backend application
│   ├── api/               # FastAPI routes and WebSocket
│   │   ├── routes/       # API endpoints
│   │   └── websocket/    # WebSocket handlers
│   ├── agents/           # Multi-agent system
│   ├── core/             # Core processing logic
│   │   ├── document_processor.py
│   │   └── knowledge_graph.py
│   └── utils/            # Shared utilities
├── frontend/             # React frontend
│   ├── src/
│   │   ├── app/         # Next.js pages
│   │   ├── components/  # React components
│   │   ├── hooks/       # Custom hooks
│   │   ├── services/    # API integration
│   │   └── types/       # TypeScript types
└── docs/                 # Documentation
```

## 🎯 Key Features in Detail

### Document Processing
- 📄 Support for multiple document formats
- 📊 Automatic table detection and extraction
- 🔍 Content analysis and metadata extraction
- 📦 Concurrent batch processing
- 📈 Progress tracking and statistics

### Real-time Updates
- 🔄 WebSocket-based status updates
- 📊 Live progress visualization
- 📈 Processing statistics
- ❌ Error reporting and handling
- 🔄 Cancellation support

### User Interface
- 📱 Responsive design
- 📤 Drag-and-drop file upload
- 📊 Progress tracking
- 📈 Statistics visualization
- ❌ Error handling and recovery

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

## 🙏 Acknowledgments

- 📚 Inspired by the Great Library of Alexandria
- 🤖 Powered by modern AI capabilities
- 💫 Built with cutting-edge web technologies

---

Made with ❤️ by the Knowledge Factory Team
