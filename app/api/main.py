"""FastAPI main application module for the Library of Alexandria."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
from typing import Dict
import logging
from datetime import datetime

# Import routers
from app.api.routes import documents, processing
from app.api.websocket import processing_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Library of Alexandria API",
    description="API for document processing and knowledge management",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-here",  # TODO: Move to environment variable
    max_age=3600  # 1 hour
)

# Include routers
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(processing.router, prefix="/api/processing", tags=["processing"])

# WebSocket connection manager
processing_ws_manager = processing_manager.manager

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting Library of Alexandria API")
    # Initialize any required services here

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Library of Alexandria API")
    # Cleanup any resources here

@app.get("/api/health")
async def health_check() -> Dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": app.version
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 