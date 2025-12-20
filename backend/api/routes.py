"""
FastAPI routes for crawling and chatting.

Endpoints:
- POST /crawl: Crawl and index a website
- POST /chat: Chat with indexed website
- GET /status/{session_id}: Get indexing status
"""
import logging
import uuid
from fastapi import APIRouter, HTTPException
from typing import Dict

from models.schemas import CrawlRequest, CrawlResponse, ChatRequest, ChatResponse, DebateRequest, DebateResponse, DebateTurn, PodcastResponse, DiagramResponse
from services.crawler import WebCrawler
from services.scraper import ContentScraper
from services.chunker import TextChunker
from services.embeddings import EmbeddingService
from services.vector_store import VectorStore
from services.rag import RAGService


router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory session storage (use Redis in production)
active_sessions: Dict[str, dict] = {}


@router.post("/crawl", response_model=CrawlResponse)
async def crawl_website(request: CrawlRequest, ai_mode: str = "api"):
    """
    Crawl and index a website for RAG.
    
    Args:
        request: CrawlRequest with URL
        ai_mode: 'api' or 'local' (query parameter)
    
    Steps:
    1. Crawl website (respecting robots.txt, depth limits)
    2. Scrape and clean content
    3. Chunk text
    4. Generate embeddings (API or local based on ai_mode)
    5. Store in vector database
    
    Returns:
        CrawlResponse with session_id for chatting
    """
    try:
        # Temporarily set AI mode for this request
        import config
        original_mode = config.settings.AI_MODE
        config.settings.AI_MODE = ai_mode
        logger.info(f"[CRAWL] Using AI mode: {ai_mode}")
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Initialize services
        crawler = WebCrawler(request.url)
        scraper = ContentScraper()
        chunker = TextChunker()
        embedding_service = EmbeddingService()
        vector_store = VectorStore(session_id)
        
        # Step 1: Crawl
        logger.info(f"[{session_id}] Starting crawl of {request.url}")
        discovered_urls = crawler.crawl()
        logger.info(f"[{session_id}] Discovered {len(discovered_urls)} URLs")
        
        if not discovered_urls:
            raise HTTPException(
                status_code=400,
                detail="Failed to crawl website. Please check the URL and try again."
            )
        
        # Step 2: Scrape
        pages = []
        for url in discovered_urls:
            # Use cached content if available to double speed
            cached_html = crawler.get_content(url)
            page = scraper.scrape(url, html_content=cached_html)
            if page:
                pages.append(page)
        
        logger.info(f"[{session_id}] Scraped {len(pages)} pages successfully")
        
        if not pages:
            raise HTTPException(
                status_code=400,
                detail="No meaningful content found on the website."
            )
        
        # Step 3: Chunk
        all_chunks = []
        for page in pages:
            chunks = chunker.chunk_page(page)
            all_chunks.extend(chunks)
        
        logger.info(f"[{session_id}] Created {len(all_chunks)} chunks")
        
        # Step 4: Generate embeddings (batch process)
        chunk_texts = [chunk.text for chunk in all_chunks]
        embeddings = embedding_service.embed_texts(chunk_texts)
        
        print(f"[{session_id}] Generated embeddings")
        
        # Step 5: Store in vector database
        vector_store.add_chunks(all_chunks, embeddings)
        vector_store.save()
        
        print(f"[{session_id}] Saved vector store")
        
        # Store session metadata
        # Store session metadata
        active_sessions[session_id] = {
            'url': request.url,
            'pages_indexed': len(pages),
            'chunks': len(all_chunks),
            'status': 'ready',
            'graph_data': {
                'nodes': [{'id': p.url, 'name': p.title or p.url} for p in pages],
                'links': [{'source': s, 'target': t} for s, t in crawler.edges if s in [p.url for p in pages] and t in [p.url for p in pages]]
            }
        }
        
        # Cleanup
        crawler.close()
        scraper.close()
        
        # Determine status
        status = 'success' if len(pages) > 0 else 'partial'
        message = f"Successfully indexed {len(pages)} pages from the website."
        
        if len(discovered_urls) > len(pages):
            status = 'partial'
            message += f" ({len(discovered_urls) - len(pages)} pages could not be processed)"
        
        # Get website title from first page
        website_title = pages[0].title if pages else "Unknown Website"
        
        return CrawlResponse(
            session_id=session_id,
            status=status,
            pages_indexed=len(pages),
            website_title=website_title,
            total_links_found=len(discovered_urls),
            message=message
        )
        
    except HTTPException:
        # Restore original mode
        if 'original_mode' in locals():
            config.settings.AI_MODE = original_mode
        raise
    except Exception as e:
        # Restore original mode
        if 'original_mode' in locals():
            config.settings.AI_MODE = original_mode
        import traceback
        error_details = traceback.format_exc()
        print(f"Error during crawl: {str(e)}")
        print(f"Traceback: {error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the website: {str(e)}"
        )


@router.post("/chat", response_model=ChatResponse)
async def chat_with_website(request: ChatRequest, ai_mode: str = "api"):
    """
    Chat with an indexed website using RAG.
    
    Args:
        request: ChatRequest with session_id and question
        ai_mode: 'api' or 'local' (query parameter)
    
    Retrieves relevant context and generates grounded answers.
    Supports follow-up questions via conversation memory.
    
    Returns:
        ChatResponse with answer and sources
    """
    try:
        # Temporarily set AI mode for this request
        import config
        original_mode = config.settings.AI_MODE
        config.settings.AI_MODE = ai_mode
        print(f"[CHAT] Using AI mode: {ai_mode}")
        # Check if session exists
        if request.session_id not in active_sessions:
            # Try to load from disk
            vector_store = VectorStore(request.session_id)
            if not vector_store.exists():
                raise HTTPException(
                    status_code=404,
                    detail="Session not found. Please crawl the website first."
                )
            
            # Load and add to active sessions
            vector_store.load()
            stats = vector_store.get_stats()
            active_sessions[request.session_id] = {
                'status': 'ready',
                'chunks': stats['num_chunks']
            }
        
        # Initialize RAG service
        rag_service = RAGService(request.session_id)
        
        # Load vector store if not already loaded
        if not rag_service.vector_store.index:
            rag_service.vector_store.load()
        
        # Answer query
        answer, sources, confidence = rag_service.answer_query(request.message)
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            confidence=confidence
        )
        
    except HTTPException:
        # Restore original mode
        if 'original_mode' in locals():
            config.settings.AI_MODE = original_mode
        raise
    except Exception as e:
        # Restore original mode
        if 'original_mode' in locals():
            config.settings.AI_MODE = original_mode
        import traceback
        error_details = traceback.format_exc()
        print(f"Error during chat: {str(e)}")
        print(f"Traceback: {error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your question: {str(e)}"
        )
    finally:
        # Restore original mode
        if 'original_mode' in locals():
            config.settings.AI_MODE = original_mode


@router.get("/status/{session_id}")
async def get_status(session_id: str):
    """
    Get status of a crawling/indexing session.
    
    Returns:
        Session status information
    """
    if session_id in active_sessions:
        return active_sessions[session_id]
    
    # Check if exists on disk
    vector_store = VectorStore(session_id)
    if vector_store.exists():
        vector_store.load()
        stats = vector_store.get_stats()
        return {
            'status': 'ready',
            'chunks': stats['num_chunks']
        }
    
    raise HTTPException(
        status_code=404,
        detail="Session not found"
    )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "RAG Website Chatbot"}


@router.get("/graph/{session_id}")
async def get_knowledge_graph(session_id: str):
    """
    Get graph data for 3D visualization.
    """
    if session_id in active_sessions:
        graph = active_sessions[session_id].get('graph_data', {'nodes': [], 'links': []})
        return graph
        
    raise HTTPException(status_code=404, detail="Graph data not found")


@router.post("/debate", response_model=DebateResponse)
async def start_debate(request: DebateRequest):
    """
    Orchestrate a debate between two websites.
    """
    try:
        # Load both RAG services
        rag1 = RAGService(request.session_id_1)
        rag2 = RAGService(request.session_id_2)
        
        # Ensure indices are loaded
        if not rag1.vector_store.index: rag1.vector_store.load()
        if not rag2.vector_store.index: rag2.vector_store.load()
        
        transcript = []
        conversation_history = f"Topic: {request.topic}\n"
        
        # Get names (from metadata or default)
        name1 = "Agent A"
        name2 = "Agent B"
        if request.session_id_1 in active_sessions:
             meta = active_sessions[request.session_id_1]
             name1 = f"Agent ({meta.get('url', 'Site A')})"
        if request.session_id_2 in active_sessions:
             meta = active_sessions[request.session_id_2]
             name2 = f"Agent ({meta.get('url', 'Site B')})"
        
        # Round 1: Opening Statement (Agent A)
        print("[DEBATE] Round 1: Agent A")
        prompt_1 = f"""
        You are representing {name1}. You are debating against {name2}.
        The topic is: {request.topic}.
        Draft a strong, grounded opening argument based strictly on the provided context.
        Be concise, professional, but competitive.
        """
        response_1, _, _ = rag1.answer_query(prompt_1)
        transcript.append(DebateTurn(speaker="Agent A", content=response_1))
        conversation_history += f"\nAgent A: {response_1}\n"
        
        # Rounds
        current_speaker = "Agent B"
        for i in range(request.rounds * 2 - 1): # -1 because we did opening
             rag_service = rag2 if current_speaker == "Agent B" else rag1
             opponent = "Agent A" if current_speaker == "Agent B" else "Agent B"
             my_name = name2 if current_speaker == "Agent B" else name1
             
             print(f"[DEBATE] Turn: {current_speaker}")
             
             prompt = f"""
             You are debating against {opponent}.
             The topic is: {request.topic}.
             
             Conversation so far:
             {conversation_history}
             
             Respond to the last point made by your opponent.
             Refute their claims using evidence from YOUR knowledge base.
             Be sharp and persuasive.
             """
             
             resp, _, _ = rag_service.answer_query(prompt)
             transcript.append(DebateTurn(speaker=current_speaker, content=resp))
             conversation_history += f"\n{current_speaker}: {resp}\n"
             
             # Switch
             current_speaker = "Agent A" if current_speaker == "Agent B" else "Agent B"
             
        # Judge
        print("[DEBATE] Judging...")
        from services.llm import LLMService # Import here to avoid circular
        import config
        llm = LLMService(api_key=config.settings.OPENROUTER_API_KEY, model=config.settings.CHAT_MODEL)
        
        judge_prompt = f"""
        Review the following debate on "{request.topic}":
        {conversation_history}
        
        Who won? Declare a winner and explain why in 1 sentence.
        Format: "Winner: [Agent A/B] because..."
        """
        winner = llm.generate_response([{"role": "user", "content": judge_prompt}])
        
        return DebateResponse(transcript=transcript, winner=winner)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/podcast", response_model=PodcastResponse)
async def generate_podcast(request: ChatRequest):
    """
    Generate a podcast script summarizing the website.
    """
    try:
        rag_service = RAGService(request.session_id)
        if not rag_service.vector_store.index: 
            rag_service.vector_store.load()
            
        # Get random chunks for coverage
        import random
        chunks = []
        if rag_service.vector_store.chunks:
             # Pick up to 8 chunks for a good summary
             sample_size = min(8, len(rag_service.vector_store.chunks))
             chunks = random.sample(rag_service.vector_store.chunks, sample_size)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="Not enough content to generate podcast.")
            
        context_text = "\n\n".join([c.text for c in chunks])
        
        # Generate script
        prompt = f"""
        You are the host of a popular tech podcast called "The Daily Briefing".
        Based on the following website content, write a lively, engaging 2-minute podcast script.
        
        Content:
        {context_text[:5000]}
        
        Requirements:
        1. Start with a catchy hook and welcome the listeners.
        2. Summarize the key value/purpose of the website.
        3. Mention 2-3 interesting details or features you found.
        4. End with a smooth sign-off.
        5. Tone: Energetic, professional, easy to listen to.
        6. NO speaker labels (like "Host:"), just the raw spoken text.
        
        Also, suggest a catchy title for this episode.
        
        Format your response as a valid JSON object:
        {{
            "title": "The Title",
            "script": "The full script text..."
        }}
        """
        
        from services.llm import LLMService
        import config
        import json
        llm = LLMService(api_key=config.settings.OPENROUTER_API_KEY, model=config.settings.CHAT_MODEL)
        
        response = llm.generate_response([{"role": "user", "content": prompt}])
        
        # Parse JSON
        try:
            clean_json = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            return PodcastResponse(**data)
        except:
             # Fallback
             print(f"[PODCAST] Failed to parse: {response}")
             # If partial failure, just return the raw text as script
             return PodcastResponse(title="The Daily Briefing", script=response)

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/diagram", response_model=DiagramResponse)
async def generate_diagram(request: ChatRequest):
    """
    Generate a MermaidJS diagram from the website content.
    """
    try:
        rag_service = RAGService(request.session_id)
        if not rag_service.vector_store.index: 
            rag_service.vector_store.load()
            
        # For diagrams, we want structural info. 
        # If user provided a message (e.g. "timeline"), use it to search.
        # Otherwise, pick random chunks to show "Structure".
        
        chunks = []
        if request.message and "diagram" not in request.message.lower() and len(request.message) > 5:
             # Search for specific topic
             embedding_service = rag_service.embedding_service
             q_emb = embedding_service.embed_query(request.message)
             results = rag_service.vector_store.search(q_emb, top_k=6)
             chunks = [c for c, _ in results]
        else:
             # General Overview
             import random
             if rag_service.vector_store.chunks:
                 sample_size = min(6, len(rag_service.vector_store.chunks))
                 chunks = random.sample(rag_service.vector_store.chunks, sample_size)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="Not enough content to generate diagram.")
            
        context_text = "\n\n".join([c.text for c in chunks])
        
        prompt = f"""
        Based on the technical content below, generate a MermaidJS diagram code.
        
        Content:
        {context_text[:4000]}
        
        Task: Create a flowchart or mindmap that best represents the structure, timeline, or logic in this text.
        
        Rules:
        1. Output ONLY the MermaidJS code directly.
        2. Do NOT use markdown code blocks (```).
        3. Use 'graph TD' (Top-Down) or 'graph LR' (Left-Right).
        4. Keep labels short.
        5. Ensure syntax is valid (no special characters that break Mermaid).
        
        Format your response as a valid JSON object:
        {{
            "mermaid_code": "graph TD\\nA[Start] --> B[End]",
            "description": "A flowchart showing..."
        }}
        """
        
        from services.llm import LLMService
        import config
        import json
        llm = LLMService(api_key=config.settings.OPENROUTER_API_KEY, model=config.settings.CHAT_MODEL)
        
        response = llm.generate_response([{"role": "user", "content": prompt}])
        
        try:
            clean_json = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            return DiagramResponse(**data)
        except Exception:
             print(f"[DIAGRAM] Failed to parse: {response}")
             # Attempt to extract just code if JSON fails
             if "graph " in response:
                 # Poor man's extraction
                 return DiagramResponse(mermaid_code=response, description="Generated Diagram")
             raise HTTPException(status_code=500, detail="AI failed to generate valid diagram JSON.")

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        import traceback
        error_msg = traceback.format_exc()
        print(f"[DIAGRAM ERROR] {error_msg}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}\n\nTraceback:\n{error_msg}")
