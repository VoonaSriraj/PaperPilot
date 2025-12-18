"""Groq LLaMA-3 integration service."""

from groq import Groq
from typing import List, Dict, Optional
import os
import logging
from app.models.schemas import ExplanationLevel

logger = logging.getLogger(__name__)


class GroqService:
    """Service for interacting with Groq LLaMA-3 API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Groq service.
        
        Args:
            api_key: Groq API key (if None, will try to get from environment)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"  # Primary model
        self.fallback_model = "llama-3.1-8b-instant"  # Fallback model
    
    def _get_system_prompt(self, explanation_level: ExplanationLevel) -> str:
        """
        Get system prompt based on explanation level.
        
        Args:
            explanation_level: Desired explanation complexity
            
        Returns:
            System prompt string
        """
        base_prompt = """You are an expert AI research paper explainer assistant. Your role is to help users understand research papers by providing accurate, well-structured explanations based ONLY on the provided context from the paper.

CRITICAL RULES:
1. ONLY use information from the provided context chunks. Do NOT make up or hallucinate information.
2. If the context doesn't contain enough information to answer a question, clearly state that the information is not available in the provided context.
3. Always cite specific sections or pages when possible using references from the context.
4. Be precise and accurate - maintain academic rigor.
5. If you're unsure about something, say so rather than guessing.
"""
        
        level_specific = {
            ExplanationLevel.BEGINNER: """
EXPLANATION STYLE: BEGINNER LEVEL
- Use simple, everyday language
- Avoid jargon or explain it when necessary
- Use analogies and examples
- Break down complex concepts into smaller parts
- Focus on "what" and "why" rather than technical details
- Make it accessible to someone with no background in the field
""",
            ExplanationLevel.STUDENT: """
EXPLANATION STYLE: STUDENT LEVEL
- Use appropriate academic terminology but define key terms
- Provide context and background when needed
- Explain methodology and approach
- Connect concepts to broader knowledge
- Suitable for undergraduate or graduate students
- Balance simplicity with technical accuracy
""",
            ExplanationLevel.RESEARCHER: """
EXPLANATION STYLE: RESEARCHER LEVEL
- Use precise technical and academic terminology
- Assume familiarity with the field
- Focus on methodology, implementation details, and technical nuances
- Discuss implications, limitations, and connections to other work
- Provide implementation insights and technical details
- Suitable for researchers and practitioners in the field
"""
        }
        
        return base_prompt + level_specific.get(explanation_level, level_specific[ExplanationLevel.STUDENT])
    
    def _format_context(self, chunks: List[Dict]) -> str:
        """
        Format retrieved chunks into context string.
        
        Args:
            chunks: List of chunk dictionaries with 'content' and optionally 'metadata'
            
        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant context found."
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            content = chunk.get('content', '')
            metadata = chunk.get('metadata', {})
            page_info = metadata.get('page', '')
            
            context_parts.append(f"[Context {i}]")
            if page_info:
                context_parts.append(f"Source: {page_info}")
            context_parts.append(content)
            context_parts.append("")  # Empty line between chunks
        
        return "\n".join(context_parts)
    
    def generate_answer(
        self,
        question: str,
        context_chunks: List[Dict],
        explanation_level: ExplanationLevel = ExplanationLevel.STUDENT,
        chat_history: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate answer using Groq LLaMA-3.
        
        Args:
            question: User's question
            context_chunks: Retrieved relevant chunks from the document
            explanation_level: Desired explanation complexity
            chat_history: Optional previous conversation messages
            
        Returns:
            Generated answer string
        """
        try:
            # Format context
            context = self._format_context(context_chunks)
            system_prompt = self._get_system_prompt(explanation_level)
            
            # Build messages
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add chat history if provided
            if chat_history:
                for msg in chat_history[-5:]:  # Last 5 messages for context
                    if isinstance(msg, dict):
                        messages.append({
                            "role": msg.get("role", "user"),
                            "content": msg.get("content", "")
                        })
            
            # Add context and question
            user_message = f"""Based on the following context from a research paper, please answer the question.

CONTEXT FROM PAPER:
{context}

QUESTION: {question}

Please provide a clear, accurate answer based only on the context provided above."""
            
            messages.append({"role": "user", "content": user_message})
            
            # Call Groq API
            logger.info(f"Calling Groq API with model {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Lower temperature for more factual responses
                max_tokens=2048,
                top_p=0.9
            )
            
            answer = response.choices[0].message.content
            logger.info("Successfully generated answer from Groq")
            return answer
            
        except Exception as e:
            logger.error(f"Error calling Groq API: {str(e)}")
            # Try fallback model
            if self.model != self.fallback_model:
                logger.info(f"Trying fallback model {self.fallback_model}")
                try:
                    response = self.client.chat.completions.create(
                        model=self.fallback_model,
                        messages=messages,
                        temperature=0.3,
                        max_tokens=2048,
                        top_p=0.9
                    )
                    answer = response.choices[0].message.content
                    return answer
                except Exception as fallback_error:
                    logger.error(f"Fallback model also failed: {str(fallback_error)}")
            
            raise Exception(f"Failed to generate answer: {str(e)}")

