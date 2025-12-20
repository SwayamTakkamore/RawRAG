"""
Text chunking service for RAG pipeline.

Chunks text into overlapping segments optimized for embedding.
"""
import re
from typing import List
import tiktoken

from config import settings
from models.schemas import Chunk, PageContent


class TextChunker:
    """
    Chunks text into overlapping segments for RAG.
    Uses token-based chunking for accurate embedding optimization.
    """
    
    def __init__(self):
        """Initialize chunker with tokenizer."""
        # Use cl100k_base encoding (used by text-embedding-3-small/large)
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
    
    def chunk_page(self, page: PageContent) -> List[Chunk]:
        """
        Chunk a page's content into overlapping segments.
        
        Args:
            page: PageContent object
            
        Returns:
            List of Chunk objects
        """
        # Split content into paragraphs first (better semantic boundaries)
        paragraphs = self._split_into_paragraphs(page.content)
        
        chunks = []
        current_chunk = ""
        current_tokens = 0
        chunk_index = 0
        
        for paragraph in paragraphs:
            para_tokens = len(self.tokenizer.encode(paragraph))
            
            # If single paragraph exceeds chunk size, split it
            if para_tokens > self.chunk_size:
                # Save current chunk if exists
                if current_chunk:
                    chunks.append(self._create_chunk(
                        current_chunk, page, chunk_index
                    ))
                    chunk_index += 1
                
                # Split large paragraph
                large_chunks = self._split_large_text(paragraph, page, chunk_index)
                chunks.extend(large_chunks)
                chunk_index += len(large_chunks)
                
                current_chunk = ""
                current_tokens = 0
            
            # If adding paragraph exceeds chunk size, save current chunk
            elif current_tokens + para_tokens > self.chunk_size:
                if current_chunk:
                    chunks.append(self._create_chunk(
                        current_chunk, page, chunk_index
                    ))
                    chunk_index += 1
                
                # Start new chunk with overlap
                if chunks and self.chunk_overlap > 0:
                    overlap_text = self._get_overlap_text(current_chunk)
                    current_chunk = overlap_text + "\n\n" + paragraph
                    current_tokens = len(self.tokenizer.encode(current_chunk))
                else:
                    current_chunk = paragraph
                    current_tokens = para_tokens
            
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
                current_tokens += para_tokens
        
        # Save final chunk
        if current_chunk:
            chunks.append(self._create_chunk(current_chunk, page, chunk_index))
        
        return chunks
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """
        Split text into paragraphs.
        
        Args:
            text: Input text
            
        Returns:
            List of paragraphs
        """
        # Split by double newlines or multiple spaces
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _split_large_text(self, text: str, page: PageContent, start_index: int) -> List[Chunk]:
        """
        Split text that's larger than chunk size.
        
        Args:
            text: Large text to split
            page: Source page
            start_index: Starting chunk index
            
        Returns:
            List of chunks
        """
        chunks = []
        tokens = self.tokenizer.encode(text)
        
        start = 0
        chunk_idx = start_index
        
        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            
            chunks.append(self._create_chunk(chunk_text, page, chunk_idx))
            chunk_idx += 1
            
            # Move start with overlap
            start = end - self.chunk_overlap
        
        return chunks
    
    def _get_overlap_text(self, text: str) -> str:
        """
        Get overlap text from end of chunk.
        
        Args:
            text: Full text
            
        Returns:
            Overlap text (last N tokens)
        """
        tokens = self.tokenizer.encode(text)
        if len(tokens) <= self.chunk_overlap:
            return text
        
        overlap_tokens = tokens[-self.chunk_overlap:]
        return self.tokenizer.decode(overlap_tokens)
    
    def _create_chunk(self, text: str, page: PageContent, index: int) -> Chunk:
        """
        Create a Chunk object.
        
        Args:
            text: Chunk text
            page: Source page
            index: Chunk index
            
        Returns:
            Chunk object
        """
        return Chunk(
            text=text,
            source_url=page.url,
            page_title=page.title,
            chunk_index=index,
            metadata={
                'website_type': page.metadata.get('website_type', 'normal'),
                'token_count': len(self.tokenizer.encode(text))
            }
        )
