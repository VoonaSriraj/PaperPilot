"""Data models and Pydantic schemas for the API."""

from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class ExplanationLevel(str, Enum):
    """Explanation complexity levels."""
    BEGINNER = "beginner"
    STUDENT = "student"
    RESEARCHER = "researcher"


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    document_id: str = Field(..., description="ID of the uploaded document")
    question: str = Field(..., description="User's question about the paper")
    explanation_level: ExplanationLevel = Field(
        default=ExplanationLevel.STUDENT,
        description="Desired explanation complexity level"
    )
    chat_history: Optional[List[ChatMessage]] = Field(
        default=None,
        description="Previous chat messages for context"
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str = Field(..., description="AI-generated answer")
    sources: List[str] = Field(default_factory=list, description="Relevant source chunks")
    document_id: str = Field(..., description="ID of the document")


class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    pages: int = Field(..., description="Number of pages in the document")
    chunks: int = Field(..., description="Number of text chunks created")
    message: str = Field(..., description="Success message")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

