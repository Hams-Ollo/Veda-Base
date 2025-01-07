# API Reference

## Overview

Veda Base provides a comprehensive RESTful API built with FastAPI. The API enables document management, knowledge extraction, search capabilities, and system administration. This reference details all available endpoints, their parameters, and expected responses.

## Base URL

```curl
https://api.vedabase.com/v1
```

## Authentication

All API requests require authentication using JWT tokens or API keys. Include the token in the Authorization header:

```http
Authorization: Bearer <token>
```

## Rate Limiting

- 100 requests per minute per IP
- 1000 requests per hour per API key
- Bulk operations have separate limits

## Common Headers

```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer <token>
X-Request-ID: <uuid>
```

## Endpoints

### Document Management

#### Upload Document

```http
POST /documents/upload
Content-Type: multipart/form-data

Parameters:
- file: File (required)
- metadata: JSON object (optional)
- process_options: JSON object (optional)

Response: 201 Created
{
    "document_id": "string",
    "status": "processing",
    "metadata": {...},
    "process_id": "string"
}
```

#### Get Document Status

```http
GET /documents/{document_id}/status

Response: 200 OK
{
    "document_id": "string",
    "status": "string",
    "progress": number,
    "metadata": {...},
    "error": string | null
}
```

#### List Documents

```http
GET /documents
Parameters:
- page: integer (default: 1)
- limit: integer (default: 20)
- status: string
- type: string
- sort: string

Response: 200 OK
{
    "documents": [...],
    "total": integer,
    "page": integer,
    "pages": integer
}
```

### Search & Retrieval

#### Semantic Search

```http
POST /search/semantic
{
    "query": "string",
    "filters": {...},
    "limit": integer,
    "offset": integer
}

Response: 200 OK
{
    "results": [...],
    "total": integer,
    "metadata": {...}
}
```

#### Knowledge Graph Query

```http
POST /graph/query
{
    "query": "string",
    "depth": integer,
    "filters": {...}
}

Response: 200 OK
{
    "nodes": [...],
    "edges": [...],
    "metadata": {...}
}
```

### Agent System

#### Initiate Task

```http
POST /agents/tasks
{
    "type": "string",
    "parameters": {...},
    "priority": integer
}

Response: 202 Accepted
{
    "task_id": "string",
    "status": "queued",
    "agent": "string"
}
```

#### Get Task Status

```http
GET /agents/tasks/{task_id}

Response: 200 OK
{
    "task_id": "string",
    "status": "string",
    "progress": number,
    "result": {...} | null,
    "error": string | null
}
```

### Analytics & Monitoring

#### System Status

```http
GET /system/status

Response: 200 OK
{
    "status": "string",
    "components": {...},
    "metrics": {...}
}
```

#### Usage Statistics

```http
GET /analytics/usage
Parameters:
- start_date: string
- end_date: string
- metrics: string[]

Response: 200 OK
{
    "metrics": {...},
    "trends": [...],
    "summary": {...}
}
```

## WebSocket API

### Real-time Updates

```curl
WSS /ws/updates

Message Format:
{
    "type": "string",
    "data": {...},
    "timestamp": string
}
```

### Document Processing Stream

```curl
WSS /ws/documents/{document_id}/stream

Message Format:
{
    "event": "string",
    "progress": number,
    "data": {...},
    "timestamp": string
}
```

## Error Handling

### Error Response Format

```json
{
    "error": {
        "code": "string",
        "message": "string",
        "details": {...},
        "request_id": "string"
    }
}
```

### Common Error Codes

- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

## Pagination

### Request Parameters

- page: Page number (1-based)
- limit: Items per page
- sort: Sort field and direction

### Response Format

```json
{
    "items": [...],
    "metadata": {
        "total": integer,
        "page": integer,
        "pages": integer,
        "has_next": boolean,
        "has_prev": boolean
    }
}
```

## Data Models

### Document

```json
{
    "id": "string",
    "title": "string",
    "content_type": "string",
    "size": integer,
    "created_at": "string",
    "updated_at": "string",
    "metadata": {...},
    "status": "string",
    "tags": [...]
}
```

### SearchResult

```json
{
    "id": "string",
    "score": number,
    "highlight": {...},
    "document": {...},
    "metadata": {...}
}
```

### Task

```json
{
    "id": "string",
    "type": "string",
    "status": "string",
    "created_at": "string",
    "updated_at": "string",
    "progress": number,
    "result": {...},
    "error": string | null
}
```

## Best Practices

### API Rate Limiting

- Implement exponential backoff
- Cache responses when possible
- Use bulk operations for multiple items

### API Error Handling

- Always check error responses
- Implement retry logic with backoff
- Log request IDs for debugging

### API Performance

- Use compression for large requests
- Implement request batching
- Cache frequently accessed data

### API Security

- Rotate API keys regularly
- Use HTTPS for all requests
- Validate all input data

## SDK Examples

### Python

```python
from vedabase_client import VedaBaseClient

client = VedaBaseClient(api_key="your-api-key")

# Upload document
response = client.documents.upload(
    file_path="document.pdf",
    metadata={"category": "research"}
)

# Search documents
results = client.search.semantic(
    query="quantum computing",
    limit=10
)
```

### JavaScript

```javascript
import { VedaBaseClient } from '@vedabase/client';

const client = new VedaBaseClient({
    apiKey: 'your-api-key'
});

// Upload document
const response = await client.documents.upload({
    file: documentFile,
    metadata: { category: 'research' }
});

// Search documents
const results = await client.search.semantic({
    query: 'quantum computing',
    limit: 10
});
```
