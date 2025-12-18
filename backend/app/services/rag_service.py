"""Main RAG service orchestrating vector store and LLM."""

from typing import List, Dict, Optional
import logging
from app.rag.vector_store import VectorStore
from app.rag.groq_service import GroqService
from app.models.schemas import ExplanationLevel, ChatMessage

logger = logging.getLogger(__name__)


class RAGService:
    """Orchestrates RAG pipeline: retrieval + generation."""
    
    def __init__(
        self,
        vector_store: VectorStore,
        groq_service: GroqService,
        top_k: int = 5
    ):
        """
        Initialize RAG service.
        
        Args:
            vector_store: VectorStore instance
            groq_service: GroqService instance
            top_k: Number of top chunks to retrieve
        """
        self.vector_store = vector_store
        self.groq_service = groq_service
        self.top_k = top_k
    
    def add_document(
        self,
        document_id: str,
        chunks: List[str]
    ) -> None:
        """
        Add a document to the RAG system.
        
        Args:
            document_id: Unique document identifier
            chunks: Text chunks from the document
        """
        logger.info(f"Adding document {document_id} to RAG system")
        self.vector_store.add_documents(document_id, chunks)
    
    def query(
        self,
        document_id: str,
        question: str,
        explanation_level: ExplanationLevel = ExplanationLevel.STUDENT,
        chat_history: Optional[List[ChatMessage]] = None
    ) -> Dict[str, any]:
        """
        Query the RAG system with a question.
        
        Args:
            document_id: Document to query
            question: User's question
            explanation_level: Desired explanation complexity
            chat_history: Optional conversation history
            
        Returns:
            Dictionary with 'answer' and 'sources' keys
        """
        logger.info(f"Processing query for document {document_id}")
        
        # Retrieve relevant chunks
        relevant_chunks = self.vector_store.search(
            document_id=document_id,
            query=question,
            top_k=self.top_k
        )
        
        if not relevant_chunks:
            return {
                'answer': "I couldn't find relevant information in the document to answer your question. Please try rephrasing or asking about a different aspect of the paper.",
                'sources': []
            }
        
        # Convert chat history to dict format if needed
        history_dict = None
        if chat_history:
            history_dict = [
                {"role": msg.role, "content": msg.content}
                for msg in chat_history
            ]
        
        # Generate answer using LLM
        answer = self.groq_service.generate_answer(
            question=question,
            context_chunks=relevant_chunks,
            explanation_level=explanation_level,
            chat_history=history_dict
        )
        
        # Extract source information
        sources = [
            chunk.get('content', '')[:200] + "..."
            for chunk in relevant_chunks[:3]  # Top 3 sources
        ]
        
        return {
            'answer': answer,
            'sources': sources
        }
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the RAG system.
        
        Args:
            document_id: Document to delete
            
        Returns:
            True if successful
        """
        return self.vector_store.delete_document(document_id)

