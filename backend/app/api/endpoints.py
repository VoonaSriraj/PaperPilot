"""API endpoints for the research paper explainer."""

import os
import uuid
import tempfile
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional

from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    DocumentUploadResponse,
    ErrorResponse
)
from app.services.pdf_processor import PDFProcessor
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)

router = APIRouter()

# Global services (initialized in main.py)
pdf_processor: Optional[PDFProcessor] = None
rag_service: Optional[RAGService] = None

# Maximum file size: 50MB
MAX_FILE_SIZE = 50 * 1024 * 1024


def initialize_services(
    pdf_proc: PDFProcessor,
    rag_svc: RAGService
):
    """Initialize services for endpoints."""
    global pdf_processor, rag_service
    pdf_processor = pdf_proc
    rag_service = rag_svc


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a research paper PDF.
    
    - **file**: PDF file to upload (max 50MB)
    
    Returns document ID and processing statistics.
    """
    global pdf_processor, rag_service
    
    if not pdf_processor or not rag_service:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service not initialized"
        )
    
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024):.1f}MB"
        )
    
    # Generate unique document ID
    document_id = str(uuid.uuid4())
    
    # Save file temporarily
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        # Extract text from PDF
        logger.info(f"Processing PDF: {file.filename} (ID: {document_id})")
        text, page_count = pdf_processor.extract_text(temp_file_path)
        
        if not text or not text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from PDF. Please ensure the PDF contains readable text."
            )
        
        # Chunk text
        chunks = pdf_processor.chunk_text(text)
        
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to chunk document text"
            )
        
        # Add to RAG system
        rag_service.add_document(document_id, chunks)
        
        logger.info(f"Successfully processed document {document_id}: {page_count} pages, {len(chunks)} chunks")
        
        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            pages=page_count,
            chunks=len(chunks),
            message="Document processed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {str(e)}")


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def chat(request: ChatRequest):
    """
    Ask a question about an uploaded research paper.
    
    - **document_id**: ID of the uploaded document
    - **question**: User's question about the paper
    - **explanation_level**: Desired complexity (beginner/student/researcher)
    - **chat_history**: Optional previous messages for context
    """
    global rag_service
    
    if not rag_service:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service not initialized"
        )
    
    # Validate request
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty"
        )
    
    if not request.document_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document ID is required"
        )
    
    try:
        # Query RAG system
        logger.info(f"Processing chat query for document {request.document_id}")
        result = rag_service.query(
            document_id=request.document_id,
            question=request.question,
            explanation_level=request.explanation_level,
            chat_history=request.chat_history
        )
        
        return ChatResponse(
            answer=result['answer'],
            sources=result['sources'],
            document_id=request.document_id
        )
        
    except Exception as e:
        logger.error(f"Error processing chat query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str):
    """
    Delete an uploaded document from the system.
    
    - **document_id**: ID of the document to delete
    """
    global rag_service
    
    if not rag_service:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service not initialized"
        )
    
    try:
        success = rag_service.delete_document(document_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        logger.info(f"Deleted document {document_id}")
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "paper-lens-api"
    }

