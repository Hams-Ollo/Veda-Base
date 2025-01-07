from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api.routes import processing, documents
from app.utils.logging_utils import setup_logging

# Setup logging
setup_logging()

app = FastAPI(
    title="Veda Base",
    description="A next-generation document processing and knowledge management platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(processing.router)
app.include_router(documents.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Veda Base API",
        "status": "operational"
    } 