"""
RAG (Retrieval-Augmented Generation) service.

Core brain of the chatbot:
- Retrieves relevant context from vector store
- Builds strict prompts to minimize hallucination
- Generates answers using OpenAI Chat API
- Manages conversation memory
"""
import json
from typing import List, Dict, Optional, Tuple
from openai import OpenAI
from pathlib import Path

from config import settings
from services.vector_store import VectorStore
from services.embeddings import EmbeddingService


class RAGService:
    """
    RAG service that enforces strict grounding to website content.
    """
    
    def __init__(self, session_id: str):
        """
        Initialize RAG service for a session.
        
        Args:
            session_id: Session identifier
        """
        self.session_id = session_id
        self.mode = settings.AI_MODE
        self.vector_store = VectorStore(session_id)
        self.embedding_service = EmbeddingService()
        
        if self.mode == "api":
            # API mode: Use OpenRouter
            self.client = OpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            )
            print(f"[RAG] Using API mode")
        else:
            # Local mode: Use HuggingFace
            from services.local_models import get_local_model_service
            self.local_service = get_local_model_service()
            print(f"[RAG] Using local mode")
        
        # Conversation memory (stored per session)
        self.conversation_history: List[Dict[str, str]] = []
        self.memory_path = settings.SESSION_STORE_PATH / f"{session_id}_memory.json"
        self._load_memory()
    
    def _load_memory(self):
        """Load conversation memory from disk."""
        if self.memory_path.exists():
            try:
                with open(self.memory_path, 'r', encoding='utf-8') as f:
                    self.conversation_history = json.load(f)
            except Exception:
                self.conversation_history = []
    
    def _save_memory(self):
        """Save conversation memory to disk."""
        try:
            with open(self.memory_path, 'w', encoding='utf-8') as f:
                # Keep last 10 turns only to avoid context overflow
                recent_history = self.conversation_history[-10:]
                json.dump(recent_history, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {str(e)}")
    
    def answer_query(self, query: str) -> Tuple[str, List[str], str]:
        """
        Answer a user query using RAG.
        
        Args:
            query: User's question
            
        Returns:
            Tuple of (answer, source_urls, confidence)
        """
        # Generate query embedding
        query_embedding = self.embedding_service.embed_query(query)
        
        # Retrieve relevant chunks (balanced approach)
        top_k = settings.TOP_K_RESULTS + 2 if settings.AI_MODE == "local" else settings.TOP_K_RESULTS
        results = self.vector_store.search(query_embedding, top_k=top_k)
        
        if not results:
            return (
                "I could not find this information on the website.",
                [],
                "low"
            )
        
        # Build context from retrieved chunks
        context_parts = []
        source_urls = []
        seen_urls = set()
        
        for chunk, score in results:
            context_parts.append(f"[Source: {chunk.page_title}]\n{chunk.text}")
            
            # Collect unique source URLs
            if chunk.source_url not in seen_urls:
                source_urls.append(chunk.source_url)
                seen_urls.add(chunk.source_url)
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Calculate confidence based on similarity scores
        avg_score = sum(score for _, score in results) / len(results)
        confidence = self._calculate_confidence(avg_score)
        
        # Build prompt with strict grounding instructions
        is_local = (settings.AI_MODE == "local")
        prompt = self._build_prompt(query, context, for_local=is_local)
        
        # Generate answer
        answer = self._generate_answer(prompt, query)
        
        # Update conversation memory
        self.conversation_history.append({
            'query': query,
            'answer': answer,
            'sources': source_urls[:3]  # Store top 3 sources
        })
        self._save_memory()
        
        return answer, source_urls, confidence
    
    def _build_prompt(self, query: str, context: str, for_local: bool = False) -> str:
        """
        Build a strict RAG prompt that minimizes hallucination.
        
        Args:
            query: User query
            context: Retrieved context from website
            for_local: If True, use simpler format for FLAN-T5
            
        Returns:
            Complete prompt for LLM
        """
        # For local models (FLAN-T5), use concise format with truncation
        if for_local:
            # Truncate context to prevent memory issues (max ~1500 chars)
            max_context_length = 1500
            if len(context) > max_context_length:
                context = context[:max_context_length] + "..."
            
            return f"""Based on the website content below, answer the question. If not found, say "Not found in the website."

Website Content:
{context}

Question: {query}
Answer:"""
        
        # For API models, use detailed format
        system_prompt = """You are a helpful AI assistant that answers questions STRICTLY based on the provided website content.

CRITICAL RULES:
1. Answer ONLY using information from the provided context below
2. If the answer is not in the context, respond with: "I could not find this information on the website."
3. Do NOT use your general knowledge or training data
4. Do NOT make assumptions or inferences beyond what's explicitly stated
5. Always cite which part of the context you used
6. Be concise and factual
7. If the question is unclear, ask for clarification

Remember: It's better to say "I don't know" than to provide incorrect information."""

        # Include conversation context if exists
        conversation_context = ""
        if len(self.conversation_history) > 0:
            recent = self.conversation_history[-3:]  # Last 3 turns
            conversation_context = "\n\nPrevious conversation:\n"
            for turn in recent:
                conversation_context += f"User: {turn['query']}\nAssistant: {turn['answer']}\n"
        
        # Combine everything
        full_prompt = f"""{system_prompt}

{conversation_context}

WEBSITE CONTENT:
{context}

USER QUESTION: {query}

ANSWER (based ONLY on the website content above):"""
        
        return full_prompt
    
    def _generate_answer(self, prompt: str, query: str) -> str:
        """
        Generate answer using API or local model.
        
        Args:
            prompt: Full prompt with context
            query: Original user query
            
        Returns:
            Generated answer
        """
        if self.mode == "api":
            return self._generate_answer_api(prompt)
        else:
            return self._generate_answer_local(prompt)
    
    def _generate_answer_api(self, prompt: str) -> str:
        """Generate answer using OpenRouter API."""
        try:
            print(f"[RAG] Attempting model: {settings.CHAT_MODEL}")
            
            # OpenRouter-specific headers and configuration
            response = self.client.chat.completions.create(
                model=settings.CHAT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions strictly based on provided context. Never use external knowledge."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for factual answers
                max_tokens=1000,   # Increased for 70B model
                # OpenRouter-specific parameters
                extra_headers={
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "RAG Website Chatbot"
                }
            )
            
            answer = response.choices[0].message.content.strip()
            print(f"[RAG] ✅ Model {settings.CHAT_MODEL} succeeded")
            return answer
            
        except Exception as e:
            import traceback
            print(f"[RAG ERROR] Model {settings.CHAT_MODEL} failed")
            print(f"[RAG ERROR] Exception: {str(e)}")
            print(f"[RAG ERROR] Traceback: {traceback.format_exc()}")
            return f"Error: Unable to generate answer using {settings.CHAT_MODEL}. Details: {str(e)}"
        
        # All models failed
        import traceback
        print(f"[RAG ERROR] All models failed")
        print(f"[RAG ERROR] Last error: {str(last_error)}")
        print(f"[RAG ERROR] Traceback: {traceback.format_exc()}")
        
        return "I encountered an error while processing your question. Please check the backend logs for details."
    
    def _generate_answer_local(self, prompt: str) -> str:
        """Generate answer using local HuggingFace model."""
        try:
            print(f"[RAG] Using local model: {settings.LOCAL_LLM_MODEL}")
            answer = self.local_service.generate_answer(prompt, max_tokens=500)
            print(f"[RAG] ✅ Local model succeeded")
            return answer
        except Exception as e:
            import traceback
            print(f"[RAG ERROR] Local model failed: {str(e)}")
            print(f"[RAG ERROR] Traceback: {traceback.format_exc()}")
            return "I encountered an error while processing your question."
    
    def _calculate_confidence(self, avg_score: float) -> str:
        """
        Calculate confidence level based on retrieval scores.
        
        Args:
            avg_score: Average similarity score
            
        Returns:
            Confidence level: 'high', 'medium', or 'low'
        """
        if avg_score > 0.8:
            return "high"
        elif avg_score > 0.6:
            return "medium"
        else:
            return "low"
    
    def clear_memory(self):
        """Clear conversation memory."""
        self.conversation_history = []
        if self.memory_path.exists():
            self.memory_path.unlink()
