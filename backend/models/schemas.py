"""
Pydantic models for request/response validation.
"""
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field


class CrawlRequest(BaseModel):
    """Request to crawl and index a website."""
    url: str = Field(..., description="Website URL to crawl and index")
    

class CrawlResponse(BaseModel):
    """Response after crawling completion."""
    session_id: str = Field(..., description="Unique session ID for this website")
    status: str = Field(..., description="Crawl status: 'success', 'partial', or 'failed'")
    pages_indexed: int = Field(..., description="Number of pages successfully indexed")
    website_title: Optional[str] = Field(None, description="Title of the website")
    total_links_found: int = Field(0, description="Total number of links discovered")
    message: str = Field(..., description="Human-readable status message")


class ChatRequest(BaseModel):
    """Request to chat with the indexed website."""
    session_id: str = Field(..., description="Session ID from crawl response")
    message: str = Field(..., description="User's question")
    

class ChatResponse(BaseModel):
    """Response from the chatbot."""
    answer: str = Field(..., description="AI-generated answer")
    sources: List[str] = Field(default_factory=list, description="Source URLs used")
    confidence: str = Field(..., description="Confidence level: 'high', 'medium', 'low'")


class PageContent(BaseModel):
    """Represents a crawled and processed page."""
    url: str
    title: str
    content: str
    metadata: dict = Field(default_factory=dict)


class Chunk(BaseModel):
    """Text chunk with metadata for RAG."""
    text: str
    source_url: str
    page_title: str
    chunk_index: int
    metadata: dict = Field(default_factory=dict)


class DebateRequest(BaseModel):
    """Request to start a debate between two websites."""
    session_id_1: str = Field(..., description="Session ID for the first website (Agent A)")
    session_id_2: str = Field(..., description="Session ID for the second website (Agent B)")
    topic: str = Field(..., description="Topic of debate")
    rounds: int = Field(3, description="Number of rounds")


class DebateTurn(BaseModel):
    """A single turn in the debate."""
    speaker: str = Field(..., description="Agent A (Left) or Agent B (Right)")
    content: str = Field(..., description="The argument content")


class DebateResponse(BaseModel):
    """The full debate transcript."""
    transcript: List[DebateTurn]
    winner: str = Field(..., description="Declared winner")


class PodcastResponse(BaseModel):
    """Response containing the generated podcast script."""
    script: str = Field(..., description="The full spoken script for the podcast")
    script: str = Field(..., description="The full spoken script for the podcast")
    title: str = Field(..., description="Catchy title for the episode")


class DiagramResponse(BaseModel):
    """Response containing MermaidJS diagram code."""
    mermaid_code: str = Field(..., description="Valid MermaidJS syntax for the diagram")
    description: str = Field(..., description="Brief explaination of the diagram")




