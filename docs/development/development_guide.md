# Development Guide

## Overview

This guide provides instructions for setting up the development environment and working with the Veda Base codebase. The project uses a modern development stack with Python (FastAPI) for the backend and Next.js for the frontend.

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+
- Docker & Docker Compose
- Git
- Poetry (Python dependency management)
- pnpm (Node.js package manager)
- Visual Studio Code (recommended)

### Development Tools

```bash
# Install development tools
pip install poetry pre-commit black isort mypy pytest
npm install -g pnpm typescript @typescript-eslint/parser
```

### Repository Setup

```bash
# Clone repository
git clone https://github.com/yourusername/veda-base.git
cd veda-base

# Install pre-commit hooks
pre-commit install

# Install Python dependencies
poetry install

# Install Node.js dependencies
cd frontend
pnpm install
```

## Project Structure

### Directory Layout

```curl
veda-base/
├── app/                    # Backend application
│   ├── api/               # API endpoints
│   ├── core/              # Core business logic
│   ├── models/            # Data models
│   ├── services/          # Business services
│   ├── utils/             # Utility functions
│   └── main.py           # Application entry point
├── frontend/              # Frontend application
│   ├── app/              # Next.js application
│   ├── components/       # React components
│   ├── lib/              # Utility functions
│   └── public/           # Static assets
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
├── docs/                  # Documentation
├── scripts/               # Development scripts
└── docker/               # Docker configuration
```

## Development Workflow

### Backend Development

#### Running the Backend

```bash
# Activate virtual environment
poetry shell

# Run development server
uvicorn app.main:app --reload

# Run with debugger
python -m debugpy --listen 5678 -m uvicorn app.main:app --reload
```

#### API Development

```python
# app/api/documents.py
from fastapi import APIRouter, Depends
from app.models import Document
from app.services import DocumentService

router = APIRouter()

@router.post("/documents")
async def create_document(
    document: Document,
    service: DocumentService = Depends()
):
    return await service.create(document)
```

### Frontend Development

#### Running the Frontend

```bash
# Start development server
cd frontend
pnpm dev

# Build for production
pnpm build
```

#### Component Development

```typescript
// frontend/components/DocumentViewer.tsx
import React from 'react';
import { Document } from '@/types';

interface Props {
  document: Document;
}

export const DocumentViewer: React.FC<Props> = ({ document }) => {
  return (
    <div className="document-viewer">
      <h1>{document.title}</h1>
      <div>{document.content}</div>
    </div>
  );
};
```

### Database Management

#### Running Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

#### Database Schema

```python
# app/models/document.py
from sqlalchemy import Column, String, DateTime
from app.db.base import Base

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(String)
    created_at = Column(DateTime, server_default=func.now())
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_documents.py

# Run with coverage
pytest --cov=app tests/
```

### Writing Tests

```python
# tests/unit/test_documents.py
import pytest
from app.services import DocumentService

@pytest.mark.asyncio
async def test_create_document():
    service = DocumentService()
    document = Document(title="Test", content="Content")
    result = await service.create(document)
    assert result.title == "Test"
```

## Code Quality

### Code Formatting

```bash
# Format Python code
black app/ tests/

# Sort imports
isort app/ tests/

# Type checking
mypy app/
```

### Linting Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.8
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
```

## Docker Development

### Local Development

```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile.dev
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/vedabase
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=vedabase
```

### Building Images

```bash
# Build development image
docker build -f docker/Dockerfile.dev -t veda-dev .

# Build production image
docker build -f docker/Dockerfile -t veda .
```

## Debugging

### VS Code Configuration

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload"],
      "jinja": true
    },
    {
      "name": "Next.js: Frontend",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/frontend/node_modules/next/dist/bin/next"
    }
  ]
}
```

### Logging Configuration

```python
# app/utils/logging.py
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Add custom handlers
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.DEBUG)
    
    # Configure loggers
    logger = logging.getLogger('app')
    logger.addHandler(file_handler)
```

## Environment Setup

### Environment Variables

```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost:5432/vedabase
REDIS_URL=redis://localhost:6379/0
GROQ_API_KEY=your-api-key
JWT_SECRET=your-secret-key
```

### Configuration Management

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Veda Base"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str
    REDIS_URL: str
    GROQ_API_KEY: str
    JWT_SECRET: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: |
          python -m pip install poetry
          poetry install
      - name: Run tests
        run: poetry run pytest
```

## Documentation

### API Documentation

```python
# app/api/documents.py
@router.post("/documents", response_model=Document)
async def create_document(
    document: Document,
    service: DocumentService = Depends()
) -> Document:
    """
    Create a new document.
    
    Args:
        document: Document data
        service: Document service instance
    
    Returns:
        Created document
    
    Raises:
        HTTPException: If document creation fails
    """
    return await service.create(document)
```

### Component Documentation

```typescript
// frontend/components/DocumentViewer.tsx
/**
 * DocumentViewer component displays a document with its content.
 * 
 * @component
 * @example
 * ```tsx
 * <DocumentViewer document={{ title: 'Test', content: 'Content' }} />
 * ```
 */
export const DocumentViewer: React.FC<Props> = ({ document }) => {
  // Component implementation
};
```

## Best Practices

### Code Style

- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Write descriptive variable and function names
- Add type hints and documentation
- Keep functions small and focused

### Git Workflow

- Use feature branches
- Write descriptive commit messages
- Squash commits before merging
- Review code before merging
- Keep PRs small and focused

### Security

- Never commit secrets
- Validate all inputs
- Use parameterized queries
- Implement rate limiting
- Keep dependencies updated

### Performance

- Use async/await for I/O operations
- Implement caching where appropriate
- Optimize database queries
- Lazy load components
- Monitor performance metrics
