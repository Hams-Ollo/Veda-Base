# API Reference

This document provides detailed information about the Veda Base API endpoints, authentication, and usage.

## Base URL

```curl
http://localhost:8000/api
```

## Authentication

All API requests require authentication using an API key. Include the API key in the request header:

```curl
Authorization: Bearer your-api-key
```

## Endpoints

### Document Management

#### Upload Documents

```http
POST /documents/upload
Content-Type: multipart/form-data
```

Upload one or more documents for processing.

**Request Body:**

- `files`: Array of files (PDF, Markdown, HTML)

**Response:**

```json
{
  "batch_id": "string",
  "message": "string"
}
```

#### Get Processing Status

```http
GET /documents/status/{batch_id}
```

Get the processing status of a document batch.

**Response:**

```json
{
  "batch_id": "string",
  "total_files": 0,
  "processed_files": 0,
  "success_count": 0,
  "error_count": 0,
  "current_file": "string",
  "status": "pending",
  "errors": [
    {
      "file": "string",
      "error": "string"
    }
  ]
}
```

#### Cancel Processing

```http
DELETE /documents/cancel/{batch_id}
```

Cancel the processing of a document batch.

### Processing Metrics

#### Get Metrics

```http
GET /processing/metrics
```

Get current processing metrics.

**Response:**

```json
{
  "total_documents": 0,
  "processing_rate": 0,
  "success_rate": 0,
  "error_rate": 0
}
```

#### Get Active Processing

```http
GET /processing/active
```

Get information about currently processing documents.

#### Get Processing History

```http
GET /processing/history
```

Get processing history with pagination.

**Query Parameters:**

- `limit`: Number of records (default: 50)
- `offset`: Offset for pagination (default: 0)

#### Get Performance Stats

```http
GET /processing/performance
```

Get system performance statistics.

**Response:**

```json
{
  "processing_speed": {
    "average_time_per_file": 0,
    "files_per_second": 0
  },
  "memory_usage": {
    "current": 0,
    "peak": 0
  },
  "cache_stats": {
    "hit_rate": 0,
    "size": 0
  },
  "error_rates": {
    "total_errors": 0,
    "error_rate": 0
  },
  "timestamp": "string"
}
```

## WebSocket API

### Connection

Connect to the WebSocket server for real-time updates:

```javascript
const socket = io('ws://localhost:8000/api/ws/processing/{batch_id}');
```

### Events

#### processing_progress

Emitted when document processing progress is updated.

```javascript
socket.on('processing_progress', (data) => {
  console.log(data);
});
```

#### processing_complete

Emitted when document processing is completed.

```javascript
socket.on('processing_complete', (data) => {
  console.log(data);
});
```

## Error Handling

The API uses standard HTTP status codes and returns error messages in the following format:

```json
{
  "error": "string",
  "message": "string",
  "details": {}
}
```

Common status codes:

- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- 100 requests per minute per IP
- 1000 requests per hour per API key

Rate limit headers are included in responses:

```curl
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1640995200
```

## Pagination

Endpoints that return lists support pagination using `limit` and `offset` parameters:

```http
GET /processing/history?limit=10&offset=0
```

Response includes pagination metadata:

```json
{
  "data": [],
  "total": 0,
  "limit": 10,
  "offset": 0
}
```

## SDK Examples

### Python

```python
from veda_base_client import VedaBaseClient

client = VedaBaseClient(api_key="your-api-key")

# Upload documents
response = client.documents.upload(files=["document.pdf"])

# Check status
status = client.documents.get_status(batch_id=response.batch_id)
```

### JavaScript

```javascript
import { VedaBaseClient } from 'veda-base-client';

const client = new VedaBaseClient({ apiKey: 'your-api-key' });

# Upload documents
const response = await client.documents.upload(files);

# Check status
const status = await client.documents.getStatus(response.batchId);
```
