# Development Guide

This guide provides detailed information for developers working on the Veda Base project.

## Development Environment Setup

### Prerequisites

1. Install required software:
   - Python 3.8+
   - Node.js 18+
   - Git
   - Visual Studio Code (recommended)

2. Install Python tools:

   ```bash
   pip install black isort mypy pytest
   ```

3. Install Node.js tools:

   ```bash
   npm install -g typescript eslint prettier
   ```

### Project Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/veda-base.git
   cd veda-base
   ```

2. Set up backend:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up frontend:

   ```bash
   cd frontend
   npm install
   ```

## Project Structure

```curl
veda-base/
├── app/                    # Backend application
│   ├── api/               # API endpoints
│   │   ├── routes/       # Route handlers
│   │   └── websocket/    # WebSocket handlers
│   ├── core/             # Core business logic
│   │   ├── agents/       # AI agents
│   │   ├── document/     # Document processing
│   │   └── knowledge/    # Knowledge management
│   └── utils/            # Utility functions
├── frontend/             # Frontend application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── hooks/       # Custom hooks
│   │   ├── services/    # API services
│   │   └── types/       # TypeScript types
└── docs/                 # Documentation
```

## Development Workflow

### Git Workflow

1. Create a feature branch:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make changes and commit:

   ```bash
   git add .
   git commit -m "feat: add your feature"
   ```

3. Push changes and create PR:

   ```bash
   git push origin feature/your-feature-name
   ```

### Code Style

#### Python

- Follow PEP 8 guidelines
- Use type hints
- Format with Black
- Sort imports with isort
- Use docstrings for functions and classes

#### TypeScript/JavaScript

- Follow ESLint configuration
- Use Prettier for formatting
- Use TypeScript types
- Write JSDoc comments for functions

### Testing

#### Backend Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_file.py

# Run with coverage
pytest --cov=app tests/
```

#### Frontend Tests

```bash
# Run all tests
npm test

# Run specific test file
npm test -- src/components/YourComponent.test.tsx

# Run with coverage
npm test -- --coverage
```

## Development Tools

### VS Code Extensions

- Python
- ESLint
- Prettier
- GitLens
- Docker

### Debugging

#### Backend Debugging

1. Set up launch configuration in VS Code
2. Add breakpoints
3. Start debugging session

#### Frontend Debugging

1. Use Chrome DevTools
2. Use React Developer Tools
3. Use console.log strategically

## API Development

### Adding New Endpoints

1. Create route in `app/api/routes/`:

```python
from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/endpoint")
async def endpoint(current_user = Depends(get_current_user)):
    return {"message": "Success"}
```

2. Register route in `app/api/__init__.py`

### WebSocket Development

1. Create handler in `app/api/websocket/`:

```python
from fastapi import WebSocket
from app.core.websocket import WebSocketManager

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            await websocket.send_json({"status": "received"})
    except:
        await websocket.close()
```

## Frontend Development

### Component Development

1. Create new component:

```tsx
import React from 'react';
import clsx from 'clsx';

interface Props {
  className?: string;
}

export function Component({ className }: Props) {
  return (
    <div className={clsx('base-class', className)}>
      Content
    </div>
  );
}
```

2. Add tests:

```tsx
import { render, screen } from '@testing-library/react';
import { Component } from './Component';

describe('Component', () => {
  it('renders correctly', () => {
    render(<Component />);
    expect(screen.getByText('Content')).toBeInTheDocument();
  });
});
```

### State Management

1. Use React Query for API state:

```tsx
import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';

export function useData() {
  return useQuery({
    queryKey: ['data'],
    queryFn: () => api.getData()
  });
}
```

2. Use local state when appropriate:

```tsx
const [state, setState] = useState<State>({});
```

## Performance Optimization

### Backend

- Use async/await for I/O operations
- Implement caching where appropriate
- Optimize database queries
- Use connection pooling

### Frontend

- Implement code splitting
- Use React.memo for expensive components
- Optimize images and assets
- Use proper loading states

## Error Handling

### Backend

```python
from fastapi import HTTPException
from app.core.exceptions import AppException

try:
    result = await process_data()
except AppException as e:
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(status_code=500)
```

### Frontend

```typescript
try {
  await api.processData();
} catch (error) {
  if (error instanceof ApiError) {
    toast.error(error.message);
  } else {
    toast.error('An unexpected error occurred');
  }
}
```

## Documentation

### Code Documentation

- Use descriptive variable names
- Write clear comments
- Document complex logic
- Keep README files updated

### API Documentation

- Document all endpoints
- Include request/response examples
- Document error responses
- Keep OpenAPI spec updated

## Deployment

### Development

```bash
# Backend
uvicorn app.main:app --reload

# Frontend
npm run dev
```

### Production Build

```bash
# Backend
uvicorn app.main:app

# Frontend
npm run build
npm start
```

## Contributing

1. Follow the git workflow
2. Write tests for new features
3. Update documentation
4. Follow code style guidelines
5. Request code reviews
