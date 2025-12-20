"""
Embedding service using OpenAI API or local HuggingFace models.

Generates semantic embeddings for text chunks.
"""
from typing import List
import openai
from openai import OpenAI

from config import settings


class EmbeddingService:
    """
    Service for generating text embeddings.
    Supports both API (OpenRouter) and local (HuggingFace) modes.
    """
    
    def __init__(self):
        """Initialize embedding service based on AI_MODE."""
        self.mode = settings.AI_MODE
        
        if self.mode == "api":
            # API mode: Use OpenRouter
            self.client = OpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            )
            self.model = settings.EMBEDDING_MODEL
            print(f"[EMBEDDING] Using API mode: {self.model}")
        else:
            # Local mode: Use HuggingFace
            from services.local_models import get_local_model_service
            self.local_service = get_local_model_service()
            print(f"[EMBEDDING] Using local mode: {settings.LOCAL_EMBEDDING_MODEL}")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        if self.mode == "api":
            return self._embed_texts_api(texts)
        else:
            return self._embed_texts_local(texts)
    
    def _embed_texts_api(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using API with batching."""
        all_embeddings = []
        batch_size = 100
        
        try:
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # OpenRouter API supports batch embedding
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                    # OpenRouter-specific headers
                    extra_headers={
                        "HTTP-Referer": "http://localhost:3000",
                        "X-Title": "RAG Website Chatbot"
                    }
                )
                
                # Extract embeddings in order
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                print(f"[EMBEDDING] Processed batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            
            return all_embeddings
            
        except Exception as e:
            import traceback
            print(f"[EMBEDDING ERROR] Model: {self.model}")
            print(f"[EMBEDDING ERROR] Exception: {str(e)}")
            print(f"[EMBEDDING ERROR] Traceback: {traceback.format_exc()}")
            raise
    
    def _embed_texts_local(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local model."""
        return self.local_service.embed_texts(texts)
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text string to embed
            
        Returns:
            Embedding vector
        """
        embeddings = self.embed_texts([text])
        return embeddings[0] if embeddings else []
    
    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.
        
        (Alias for embed_text for semantic clarity)
        
        Args:
            query: Query string
            
        Returns:
            Query embedding vector
        """
        return self.embed_text(query)
