# Getting Started

## Introduction

Welcome to Veda Base! This guide will help you get started with setting up and using the system. Veda Base is a modern document management and knowledge extraction system that uses AI to help you organize, analyze, and retrieve information from your documents.

## Quick Start

### Installation

#### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/veda-base.git
cd veda-base

# Start the application
docker-compose up -d
```

#### Manual Installation

```bash
# Backend setup
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd frontend
pnpm install
```

### Configuration

## 1. Create a `.env` file in the root directory

```env
# Application
APP_ENV=development
DEBUG=true

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/vedabase
REDIS_URL=redis://localhost:6379/0

# AI Services
GROQ_API_KEY=your-api-key

# Security
JWT_SECRET=your-secret-key
```

## 2. Start the services

```bash
# Start backend
uvicorn app.main:app --reload

# Start frontend (in a new terminal)
cd frontend
pnpm dev
```

## 3. Access the application

- Web UI: <http://localhost:3000>
- API Documentation: <http://localhost:8000/docs>
- Admin Interface: <http://localhost:8501>

## Basic Usage

### Document Management

#### Upload Documents

1. Navigate to <http://localhost:3000/upload>
2. Drag and drop files or click to select
3. Add metadata (optional)
4. Click "Upload"

```python
# Using the Python client
from vedabase_client import VedaBaseClient

client = VedaBaseClient(api_key="your-api-key")

# Upload a document
response = client.documents.upload(
    file_path="path/to/document.pdf",
    metadata={"category": "research"}
)
```

#### Search Documents

1. Go to <http://localhost:3000/search>
2. Enter your search query
3. Use filters to refine results
4. Click on documents to view

```python
# Using the Python client
results = client.search.semantic(
    query="quantum computing applications",
    limit=10
)

for result in results:
    print(f"Title: {result.title}")
    print(f"Relevance: {result.score}")
```

### Knowledge Extraction

#### Analyze Documents

1. Select a document
2. Click "Analyze"
3. View extracted information
4. Explore knowledge graph

```python
# Using the Python client
analysis = client.documents.analyze(
    document_id="doc123",
    analysis_type="full"
)

print("Key Concepts:", analysis.concepts)
print("Entities:", analysis.entities)
```

#### Generate Insights

1. Select multiple documents
2. Click "Generate Insights"
3. Review generated summary
4. Export findings

```python
# Using the Python client
insights = client.documents.generate_insights(
    document_ids=["doc123", "doc456"],
    insight_type="comparison"
)

print("Common Themes:", insights.themes)
print("Differences:", insights.differences)
```

## Features Overview

### Document Processing

- Multi-format support (PDF, DOCX, TXT, etc.)
- OCR for scanned documents
- Metadata extraction
- Content classification

### Search Capabilities

- Semantic search
- Faceted filtering
- Real-time suggestions
- Advanced query syntax

### AI Features

- Named entity recognition
- Topic modeling
- Relationship extraction
- Summary generation

### Knowledge Management

- Knowledge graph visualization
- Concept mapping
- Citation linking
- Cross-referencing

## API Integration

### Authentication

```python
# Get API token
token = client.auth.login(
    username="user@example.com",
    password="password"
)

# Use token for requests
client = VedaBaseClient(api_token=token)
```

### Basic Operations

```python
# Create collection
collection = client.collections.create(
    name="Research Papers",
    description="Academic research papers"
)

# Add document to collection
client.collections.add_document(
    collection_id=collection.id,
    document_id="doc123"
)

# Search within collection
results = client.collections.search(
    collection_id=collection.id,
    query="machine learning"
)
```

## Next Steps

### Explore Advanced Features

- [Multi-Agent System](./architecture/ai_ml_architecture.md)
- [Knowledge Graph](./features/knowledge_graph.md)
- [Document Processing Pipeline](./features/document_processing.md)

### Development

- [Development Guide](./development/development_guide.md)
- [API Reference](./api/api_reference.md)
- [Contributing Guidelines](./development/contributing.md)

### Deployment

- [Deployment Guide](./deployment/deployment_guide.md)
- [Security Best Practices](./deployment/security.md)
- [Monitoring](./deployment/monitoring.md)

## Troubleshooting

### Common Issues

#### Connection Problems

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f api
```

#### Search Issues

1. Verify document indexing status
2. Check vector store connection
3. Review search query syntax

#### Performance Issues

1. Monitor resource usage
2. Check cache configuration
3. Review database indexes

### Getting Help

- [Documentation](./README.md)
- [GitHub Issues](https://github.com/yourusername/veda-base/issues)
- [Community Forum](https://forum.vedabase.com)

## Best Practices

### Document Organization

- Use consistent metadata
- Organize documents in collections
- Regular backup important documents
- Monitor processing status

### Search Optimization

- Use specific search terms
- Leverage filters effectively
- Save common searches
- Review search analytics

### System Maintenance

- Monitor system health
- Regular backups
- Update dependencies
- Review security settings

## Security Recommendations

### Access Control

- Use strong passwords
- Enable 2FA
- Regular access review
- Role-based permissions

### Data Protection

- Encrypt sensitive data
- Regular security updates
- Monitor access logs
- Implement backup strategy

### Client Security

- Rotate API keys
- Rate limiting
- Input validation
- Security headers
