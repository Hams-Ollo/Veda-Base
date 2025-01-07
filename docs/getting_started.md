# Getting Started with Veda Base

This guide will help you set up and run Veda Base on your local machine for development and testing purposes.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher
- Node.js 18 or higher
- npm or yarn
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/veda-base.git
cd veda-base
```

### 2. Backend Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install backend dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory:

```env
DEBUG=True
API_KEY=your_api_key
DATABASE_URL=sqlite:///./veda_base.db
```

4. Start the backend server:

```bash
uvicorn app.main:app --reload
```

The backend API will be available at `http://localhost:8000`.

### 3. Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install frontend dependencies:

```bash
npm install
```

3. Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

4. Start the development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`.

## Basic Usage

### Document Upload

1. Navigate to the upload page
2. Drag and drop files or click to select
3. Supported formats: PDF, Markdown, HTML
4. Monitor upload progress in real-time

### Processing Status

- View real-time processing status via WebSocket
- Check document processing metrics
- Monitor system performance

### Search and Retrieval

1. Use the search bar for basic searches
2. Advanced search with filters and facets
3. View and navigate the knowledge graph

## Configuration

### Backend Configuration

Key environment variables:

- `DEBUG`: Enable/disable debug mode
- `API_KEY`: Your API key for authentication
- `DATABASE_URL`: Database connection string
- `CACHE_URL`: Cache server connection string
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Frontend Configuration

Key environment variables:

- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXT_PUBLIC_WS_URL`: WebSocket server URL
- `NEXT_PUBLIC_ENVIRONMENT`: Development/production environment

## Development Workflow

1. Create a new branch for your feature
2. Make your changes
3. Run tests
4. Submit a pull request

## Troubleshooting

Common issues and solutions:

1. **Backend won't start**
   - Check Python version
   - Verify virtual environment is activated
   - Confirm all dependencies are installed

2. **Frontend build fails**
   - Clear npm cache
   - Delete node_modules and reinstall
   - Check Node.js version

3. **WebSocket connection issues**
   - Verify WebSocket URL
   - Check browser console for errors
   - Ensure backend is running

## Next Steps

- Read the [Architecture Overview](architecture/overview.md)
- Check the [API Documentation](api/api_reference.md)
- Review [Development Guidelines](development/development_guide.md)
- Learn about [Deployment](deployment/deployment_guide.md)

## Support

If you need help:

1. Check the documentation
2. Search existing issues
3. Create a new issue
4. Join our community channels

## Contributing

We welcome contributions! Please see our [Contributing Guide](development/contributing.md) for details.
