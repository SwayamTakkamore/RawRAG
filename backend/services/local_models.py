"""
Local HuggingFace model service for embeddings and chat.
No API needed - runs completely on your machine!
"""
from typing import List
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

from config import settings


class LocalModelService:
    """
    Service for local HuggingFace models (no API needed).
    """
    
    def __init__(self):
        """Initialize local models."""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[LOCAL] Using device: {self.device}")
        
        # Load embedding model
        print(f"[LOCAL] Loading embedding model: {settings.LOCAL_EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(
            settings.LOCAL_EMBEDDING_MODEL, 
            device=self.device
        )
        
        # Load LLM model
        print(f"[LOCAL] Loading LLM model: {settings.LOCAL_LLM_MODEL}")
        self.tokenizer = AutoTokenizer.from_pretrained(settings.LOCAL_LLM_MODEL)
        self.llm_model = AutoModelForSeq2SeqLM.from_pretrained(
            settings.LOCAL_LLM_MODEL
        ).to(self.device)
        
        self.llm_pipeline = pipeline(
            "text2text-generation",
            model=self.llm_model,
            tokenizer=self.tokenizer,
            device=0 if self.device == "cuda" else -1
        )
        
        print("[LOCAL] ✅ All models loaded successfully!")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local model."""
        embeddings = self.embedding_model.encode(
            texts, 
            show_progress_bar=False,
            convert_to_numpy=True
        )
        return embeddings.tolist()
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text."""
        return self.embed_texts([text])[0]
    
    def generate_answer(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate answer using local LLM."""
        try:
            # Clear CUDA cache before generation
            if self.device == "cuda":
                torch.cuda.empty_cache()
            
            output = self.llm_pipeline(
                prompt,
                max_new_tokens=max_tokens,
                temperature=0.3,  # Slightly higher for more natural answers
                top_p=0.9,  # Nucleus sampling
                do_sample=True,  # Enable sampling for better quality
                repetition_penalty=1.2,  # Reduce repetition
                clean_up_tokenization_spaces=True
            )[0]["generated_text"]
            
            # Clear CUDA cache after generation
            if self.device == "cuda":
                torch.cuda.empty_cache()
            
            return output.strip()
        except torch.cuda.OutOfMemoryError:
            print("[LOCAL ERROR] CUDA out of memory - trying with reduced settings")
            # Clear cache and retry with smaller settings
            if self.device == "cuda":
                torch.cuda.empty_cache()
            try:
                output = self.llm_pipeline(
                    prompt[:2000],  # Truncate prompt
                    max_new_tokens=200,  # Reduce tokens
                    temperature=0.3,
                    do_sample=False,  # Disable sampling to save memory
                    clean_up_tokenization_spaces=True
                )[0]["generated_text"]
                return output.strip()
            except Exception:
                return "The question is too complex for the available GPU memory. Please try a simpler question or switch to API mode."
        except Exception as e:
            print(f"[LOCAL ERROR] {str(e)}")
            return "I encountered an error while processing your question."


# Global instance (lazy initialization)
_local_model_service = None

def get_local_model_service() -> LocalModelService:
    """Get or create local model service instance."""
    global _local_model_service
    if _local_model_service is None:
        _local_model_service = LocalModelService()
    return _local_model_service
