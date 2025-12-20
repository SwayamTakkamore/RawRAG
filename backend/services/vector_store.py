"""
Vector store using FAISS for efficient similarity search.

Stores embeddings and enables retrieval of relevant chunks.
"""
import pickle
import numpy as np
import faiss
from pathlib import Path
from typing import List, Tuple, Optional

from config import settings
from models.schemas import Chunk


class VectorStore:
    """
    FAISS-based vector store for efficient semantic search.
    Each website gets its own isolated index.
    """
    
    def __init__(self, session_id: str):
        """
        Initialize vector store for a session.
        
        Args:
            session_id: Unique identifier for this website/session
        """
        self.session_id = session_id
        self.index: Optional[faiss.Index] = None
        self.chunks: List[Chunk] = []
        self.dimension: Optional[int] = None  # Will be set dynamically from embeddings
        
        # Storage paths
        self.index_path = settings.VECTOR_STORE_PATH / f"{session_id}.index"
        self.chunks_path = settings.VECTOR_STORE_PATH / f"{session_id}.chunks"
    
    def add_chunks(self, chunks: List[Chunk], embeddings: List[List[float]]):
        """
        Add chunks and their embeddings to the vector store.
        
        Args:
            chunks: List of Chunk objects
            embeddings: Corresponding embedding vectors
        """
        if not chunks or not embeddings:
            return
        
        # Convert embeddings to numpy array
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        # Set dimension from actual embeddings if not set
        if self.dimension is None:
            self.dimension = embeddings_array.shape[1]
            print(f"[VECTOR_STORE] Detected embedding dimension: {self.dimension}")
        
        # Initialize index if needed
        if self.index is None:
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product (cosine similarity)
            print(f"[VECTOR_STORE] Created FAISS index with dimension: {self.dimension}")
        
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings_array)
        
        # Add to index
        self.index.add(embeddings_array)
        
        # Store chunks
        self.chunks.extend(chunks)
    
    def search(self, query_embedding: List[float], top_k: int = None) -> List[Tuple[Chunk, float]]:
        """
        Search for most similar chunks to query.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return (default: from config)
            
        Returns:
            List of (Chunk, similarity_score) tuples
        """
        if self.index is None or len(self.chunks) == 0:
            return []
        
        if top_k is None:
            top_k = settings.TOP_K_RESULTS
        
        # Ensure top_k doesn't exceed number of chunks
        top_k = min(top_k, len(self.chunks))
        
        # Convert query to numpy array and normalize
        query_array = np.array([query_embedding], dtype=np.float32)
        faiss.normalize_L2(query_array)
        
        # Search
        scores, indices = self.index.search(query_array, top_k)
        
        # Build results
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.chunks):  # Safety check
                results.append((self.chunks[idx], float(score)))
        
        return results
    
    def save(self):
        """Save index and chunks to disk."""
        if self.index is None:
            return
        
        # Save FAISS index
        faiss.write_index(self.index, str(self.index_path))
        
        # Save chunks
        with open(self.chunks_path, 'wb') as f:
            pickle.dump(self.chunks, f)
    
    def load(self) -> bool:
        """
        Load index and chunks from disk.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if not self.index_path.exists() or not self.chunks_path.exists():
            return False
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(str(self.index_path))
            
            # Load chunks
            with open(self.chunks_path, 'rb') as f:
                self.chunks = pickle.load(f)
            
            return True
        except Exception as e:
            print(f"Error loading vector store: {str(e)}")
            return False
    
    def exists(self) -> bool:
        """
        Check if vector store exists on disk.
        
        Returns:
            True if exists, False otherwise
        """
        return self.index_path.exists() and self.chunks_path.exists()
    
    def get_stats(self) -> dict:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'session_id': self.session_id,
            'num_chunks': len(self.chunks),
            'index_size': self.index.ntotal if self.index else 0,
            'dimension': self.dimension
        }
