from config import settings
from openai import OpenAI

class LLMService:
    """
    General purpose LLM service for tasks like Debate, Quiz, Podcast.
    """
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.mode = settings.AI_MODE
        
        if self.mode == "api":
             self.client = OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1"
            )
        else:
             from services.local_models import get_local_model_service
             self.local_service = get_local_model_service()

    def generate_response(self, messages: list) -> str:
        """
        Generate a response from the LLM.
        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
        """
        if self.mode == "api":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                extra_headers={
                        "HTTP-Referer": "http://localhost:3000",
                        "X-Title": "RAG Website Chatbot"
                    }
            )
            return response.choices[0].message.content.strip()
        else:
            # Simple wrapper for local model
            # Local service takes a string prompt, so we extract the last user message
            prompt = messages[-1]["content"]
            return self.local_service.generate_answer(prompt, max_tokens=1000)
