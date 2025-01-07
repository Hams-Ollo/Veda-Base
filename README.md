# 🧠 Veda Base

A modern knowledge management system powered by AI agents for intelligent document processing and information retrieval.

## ✨ Features

- 🤖 Multi-agent system for intelligent document processing
- 📄 Support for multiple document formats (PDF, Markdown, HTML)
- 🔍 Advanced search and knowledge extraction
- 🌐 Real-time processing status via WebSocket
- 📊 Processing metrics and performance monitoring
- 🔄 Automatic document categorization and taxonomy
- 🎯 REST API with FastAPI backend
- ⚛️ Modern React frontend with Next.js

## 🛠️ Tech Stack

### 🔧 Backend

- 🐍 Python 3.8+
- ⚡ FastAPI
- 🔌 Socket.IO
- 📝 Pydantic
- 🗃️ SQLAlchemy
- 🧪 Various AI/ML libraries

### 🎨 Frontend

- ⚛️ Next.js 14
- 🔄 React 18
- 📘 TypeScript
- 🔌 Socket.IO Client
- 🎨 TailwindCSS
- 🔄 React Query

## 🚀 Getting Started

### 📋 Prerequisites

- 🐍 Python 3.8+
- 📦 Node.js 18+
- 📥 npm/yarn
- 🔧 Virtual environment (recommended)

### ⚙️ Backend Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn app.main:app --reload
```

### 🎨 Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The application will be available at:

- 🌐 Frontend: <http://localhost:3000>
- 🔧 Backend API: <http://localhost:8000>
- 📚 API Documentation: <http://localhost:8000/docs>

## ⚙️ Environment Variables

### 🔧 Application Backend

Create a `.env` file in the root directory:

```env
DEBUG=True
API_KEY=your_api_key
DATABASE_URL=sqlite:///./veda_base.db
```

### 🎨 React Frontend

Create a `.env.local` file in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## 📚 Documentation

- 📖 [API Documentation](docs/api/api_reference.md)
- 🏗️ [Architecture Overview](docs/architecture/overview.md)
- 💻 [Development Guide](docs/development/development_guide.md)
- 🚀 [Deployment Guide](docs/deployment/deployment_guide.md)

## 🤝 Contributing

1. 🍴 Fork the repository
2. 🌿 Create your feature branch (`git checkout -b feature/amazing-feature`)
3. 💾 Commit your changes (`git commit -m 'Add some amazing feature'`)
4. 📤 Push to the branch (`git push origin feature/amazing-feature`)
5. 🔄 Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
