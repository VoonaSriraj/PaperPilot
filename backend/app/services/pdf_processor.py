"""PDF processing service using PyMuPDF."""

import fitz  # PyMuPDF
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Service for extracting and processing text from PDF documents."""
    
    def __init__(self):
        """Initialize the PDF processor."""
        pass
    
    def extract_text(self, pdf_path: str) -> Tuple[str, int]:
        """
        Extract text from PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Tuple of (full_text, page_count)
            
        Raises:
            Exception: If PDF cannot be processed
        """
        try:
            doc = fitz.open(pdf_path)
            full_text = []
            page_count = len(doc)
            
            for page_num in range(page_count):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    # Add page marker for context
                    full_text.append(f"[Page {page_num + 1}]\n{text}")
            
            doc.close()
            combined_text = "\n\n".join(full_text)
            
            logger.info(f"Extracted text from {page_count} pages")
            return combined_text, page_count
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise Exception(f"Failed to process PDF: {str(e)}")
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List[str]:
        """
        Split text into chunks with overlap.
        
        Uses sentence-aware chunking to avoid breaking sentences.
        
        Args:
            text: Full text to chunk
            chunk_size: Target size for each chunk (characters)
            chunk_overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []
        
        # Split by paragraphs first
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If adding this paragraph would exceed chunk size, save current chunk
            if current_chunk and len(current_chunk) + len(para) > chunk_size:
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap from previous chunk
                if chunk_overlap > 0 and current_chunk:
                    overlap_text = current_chunk[-chunk_overlap:]
                    current_chunk = overlap_text + "\n\n" + para
                else:
                    current_chunk = para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # If chunks are still too large, split further by sentences
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= chunk_size:
                final_chunks.append(chunk)
            else:
                # Split by sentences
                sentences = self._split_sentences(chunk)
                temp_chunk = ""
                for sentence in sentences:
                    if temp_chunk and len(temp_chunk) + len(sentence) > chunk_size:
                        final_chunks.append(temp_chunk.strip())
                        temp_chunk = sentence
                    else:
                        temp_chunk += (" " if temp_chunk else "") + sentence
                if temp_chunk.strip():
                    final_chunks.append(temp_chunk.strip())
        
        logger.info(f"Created {len(final_chunks)} chunks from text")
        return final_chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences (simple implementation)."""
        import re
        # Simple sentence splitting - can be improved with NLP libraries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

