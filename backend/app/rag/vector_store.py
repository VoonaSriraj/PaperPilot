"""ChromaDB vector store integration."""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import os
import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class VectorStore:
    """ChromaDB vector store for document embeddings."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the vector store.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model
        logger.info("Loading sentence transformer model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Embedding model loaded")
        
        # Dictionary to store collections per document
        self.collections: Dict[str, chromadb.Collection] = {}
    
    def create_collection(self, document_id: str) -> chromadb.Collection:
        """
        Create or get a collection for a document.
        
        Args:
            document_id: Unique document identifier
            
        Returns:
            ChromaDB collection
        """
        if document_id not in self.collections:
            try:
                # Try to get existing collection
                collection = self.client.get_collection(name=document_id)
                logger.info(f"Retrieved existing collection for document {document_id}")
            except:
                # Create new collection if it doesn't exist
                collection = self.client.create_collection(
                    name=document_id,
                    metadata={"document_id": document_id}
                )
                logger.info(f"Created new collection for document {document_id}")
            
            self.collections[document_id] = collection
        
        return self.collections[document_id]
    
    def add_documents(
        self,
        document_id: str,
        chunks: List[str],
        metadatas: Optional[List[Dict]] = None
    ) -> None:
        """
        Add document chunks to the vector store.
        
        Args:
            document_id: Unique document identifier
            chunks: List of text chunks to embed and store
            metadatas: Optional metadata for each chunk
        """
        if not chunks:
            return
        
        collection = self.create_collection(document_id)
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(chunks)} chunks...")
        embeddings = self.embedding_model.encode(chunks).tolist()
        
        # Prepare IDs and metadata
        ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
        if metadatas is None:
            metadatas = [{"chunk_index": i, "document_id": document_id} 
                        for i in range(len(chunks))]
        
        # Add to collection
        collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(chunks)} chunks to vector store for document {document_id}")
    
    def search(
        self,
        document_id: str,
        query: str,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Search for relevant chunks in the document.
        
        Args:
            document_id: Document to search in
            query: Search query text
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries with 'content', 'score', and 'metadata' keys
        """
        try:
            collection = self.create_collection(document_id)
        except Exception as e:
            logger.error(f"Error accessing collection for document {document_id}: {str(e)}")
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()[0]
        
        # Search in collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count())
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'content': results['documents'][0][i],
                    'score': results['distances'][0][i] if results.get('distances') else None,
                    'metadata': results['metadatas'][0][i] if results.get('metadatas') else {}
                })
        
        logger.info(f"Retrieved {len(formatted_results)} relevant chunks for query")
        return formatted_results
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the vector store.
        
        Args:
            document_id: Document identifier to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if document_id in self.collections:
                del self.collections[document_id]
            
            self.client.delete_collection(name=document_id)
            logger.info(f"Deleted collection for document {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            return False

