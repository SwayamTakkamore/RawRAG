"""
FastAPI main application entry point.

Hackathon-ready RAG-based website chatbot backend.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import settings
from api.routes import router
import logging
import colorlog

# Configure Logging
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S',
    reset=True,
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
))

logger = colorlog.getLogger()
if not logger.handlers:
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Quiet down noisy libs
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


# Initialize FastAPI app
app = FastAPI(
    title="RAG Website Chatbot API",
    description="Convert any website into an AI chatbot using RAG",
    version="1.0.0"
)

# CORS middleware (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api", tags=["RAG"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RAG Website Chatbot API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    # Run the server
    print(f"Starting server on {settings.HOST}:{settings.PORT}")
    print(f"API docs available at http://{settings.HOST}:{settings.PORT}/docs")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True  # Enable auto-reload for development
    )
