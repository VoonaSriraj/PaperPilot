"""Main FastAPI application."""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from app.api.endpoints import router, initialize_services
from app.services.pdf_processor import PDFProcessor
from app.services.rag_service import RAGService
from app.rag.vector_store import VectorStore
from app.rag.groq_service import GroqService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    # Startup
    logger.info("Initializing services...")
    
    # Initialize services
    pdf_processor = PDFProcessor()
    
    # Initialize vector store
    persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    vector_store = VectorStore(persist_directory=persist_dir)
    
    # Initialize Groq service
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable is required")
    
    groq_service = GroqService(api_key=groq_api_key)
    
    # Initialize RAG service
    top_k = int(os.getenv("RAG_TOP_K", "5"))
    rag_service = RAGService(
        vector_store=vector_store,
        groq_service=groq_service,
        top_k=top_k
    )
    
    # Initialize endpoints with services
    initialize_services(pdf_processor, rag_service)
    
    logger.info("Services initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="PaperLens API",
    description="AI Research Paper Explainer Bot - RAG-powered Q&A system",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://localhost:5174"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1", tags=["api"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "PaperLens API - AI Research Paper Explainer",
        "version": "1.0.0",
        "docs": "/docs"
    }

