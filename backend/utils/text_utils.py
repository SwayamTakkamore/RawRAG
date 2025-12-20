"""
Text processing and cleaning utilities.
"""
import re
import hashlib
from typing import List


def clean_html_text(text: str) -> str:
    """
    Clean extracted HTML text.
    
    - Remove excessive whitespace
    - Normalize line breaks
    - Remove special characters
    
    Args:
        text: Raw text from HTML
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Replace multiple whitespaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    return text


def is_low_content(text: str, min_words: int = 30) -> bool:
    """
    Check if text has too little meaningful content.
    
    Args:
        text: Text to check
        min_words: Minimum word count threshold
        
    Returns:
        True if content is too low, False otherwise
    """
    if not text:
        return True
    
    words = text.split()
    return len(words) < min_words


def compute_content_hash(text: str) -> str:
    """
    Compute hash of text content for deduplication.
    
    Args:
        text: Text content
        
    Returns:
        MD5 hash of normalized content
    """
    # Normalize text for hashing (remove whitespace variations)
    normalized = re.sub(r'\s+', ' ', text.lower().strip())
    return hashlib.md5(normalized.encode()).hexdigest()


def extract_main_headings(text: str) -> List[str]:
    """
    Extract main headings from text (simple heuristic).
    
    Looks for lines that:
    - Are short (< 100 chars)
    - End with no punctuation or colon
    - Are followed by longer content
    
    Args:
        text: Text content
        
    Returns:
        List of potential headings
    """
    headings = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if len(line) > 10 and len(line) < 100:
            # Check if it looks like a heading
            if line[0].isupper() and not line.endswith('.'):
                headings.append(line)
    
    return headings[:5]  # Return top 5


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences (simple approach).
    
    Args:
        text: Input text
        
    Returns:
        List of sentences
    """
    # Simple sentence splitter
    sentences = re.split(r'[.!?]+\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to maximum length, breaking at word boundaries.
    
    Args:
        text: Text to truncate
        max_length: Maximum character length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length]
    # Break at last space to avoid cutting words
    last_space = truncated.rfind(' ')
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return truncated + '...'
