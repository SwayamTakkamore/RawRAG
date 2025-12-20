"""
Test script to verify OpenRouter API setup.
Run this to check if your API key and models are working.
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    print("❌ ERROR: OPENROUTER_API_KEY not found in .env file")
    print("\nPlease:")
    print("1. Get your key from https://openrouter.ai/keys")
    print("2. Add it to backend/.env:")
    print("   OPENROUTER_API_KEY=sk-or-v1-your-key-here")
    exit(1)

print("✅ API key found!")
print(f"Key: {api_key[:15]}...{api_key[-5:]}")

# Initialize client
client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

# Test 1: Chat model
print("\n" + "="*50)
print("TEST 1: Testing Chat Model")
print("="*50)

chat_model = os.getenv("CHAT_MODEL", "meta-llama/llama-3.1-8b-instruct:free")
print(f"Model: {chat_model}")

try:
    response = client.chat.completions.create(
        model=chat_model,
        messages=[
            {"role": "user", "content": "Say 'Hello, I am working!' and nothing else."}
        ],
        max_tokens=50,
        extra_headers={
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "RAG Test"
        }
    )
    answer = response.choices[0].message.content
    print(f"✅ Chat model working!")
    print(f"Response: {answer}")
except Exception as e:
    print(f"❌ Chat model failed: {e}")
    print("\nTry these free alternatives in .env:")
    print("  CHAT_MODEL=google/gemini-flash-1.5-8b:free")
    print("  CHAT_MODEL=microsoft/phi-3-mini-128k-instruct:free")

# Test 2: Embedding model
print("\n" + "="*50)
print("TEST 2: Testing Embedding Model")
print("="*50)

embedding_model = os.getenv("EMBEDDING_MODEL", "openai/text-embedding-3-small")
print(f"Model: {embedding_model}")

try:
    response = client.embeddings.create(
        model=embedding_model,
        input=["test"],
        extra_headers={
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "RAG Test"
        }
    )
    embedding = response.data[0].embedding
    print(f"✅ Embedding model working!")
    print(f"Embedding dimension: {len(embedding)}")
except Exception as e:
    print(f"❌ Embedding model failed: {e}")
    print("\nNote: This model requires credits (~$0.0001 per test)")
    print("If you don't have credits, embeddings will fail but chat still works")

print("\n" + "="*50)
print("SUMMARY")
print("="*50)
print("\nIf both tests passed:")
print("  ✅ Your setup is complete! Restart the backend.")
print("\nIf chat failed:")
print("  ❌ Check your API key and try a different free model")
print("\nIf embedding failed:")
print("  ⚠️  Add credits to OpenRouter, or the crawl will fail")
print("     (Embeddings need ~$0.02 for 10,000 pages)")
