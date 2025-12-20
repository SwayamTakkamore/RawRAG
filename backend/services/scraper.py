"""
Content scraper that extracts clean, meaningful text from HTML pages.

Focuses on main content while filtering out:
- Navigation bars
- Footers
- Ads
- Scripts
- Low-value elements
"""
import requests
from bs4 import BeautifulSoup, Comment
from typing import Optional, Dict
import hashlib

from models.schemas import PageContent
from utils.text_utils import clean_html_text, is_low_content, compute_content_hash
from utils.url_utils import detect_website_type


class ContentScraper:
    """
    Scrapes and cleans content from web pages.
    Adapts extraction strategy based on website type.
    """
    
    def __init__(self):
        """Initialize scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RAGBot/1.0; Educational)'
        })
        self.content_hashes: set = set()  # For deduplication
    
    def scrape(self, url: str, html_content: Optional[str] = None) -> Optional[PageContent]:
        """
        Scrape and extract content from a URL.
        
        Args:
            url: URL to scrape
            html_content: Optional cached HTML content to avoid re-fetching
            
        Returns:
            PageContent object or None if scraping fails
        """
        try:
            if html_content:
                text = html_content
            else:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                text = response.text
            
            # Parse HTML
            soup = BeautifulSoup(text, 'lxml')
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract main content
            content = self._extract_content(soup, url)
            
            # Clean content
            content = clean_html_text(content)
            
            # Check if content is meaningful
            if is_low_content(content):
                return None
            
            # Check for duplicates
            content_hash = compute_content_hash(content)
            if content_hash in self.content_hashes:
                return None  # Duplicate content
            
            self.content_hashes.add(content_hash)
            
            # Detect website type for metadata
            website_type = detect_website_type(url)
            
            return PageContent(
                url=url,
                title=title,
                content=content,
                metadata={
                    'website_type': website_type,
                    'content_length': len(content),
                    'word_count': len(content.split())
                }
            )
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """
        Extract page title.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Page title
        """
        # Try <title> tag
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        
        # Try <h1> tag
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        return "Untitled Page"
    
    def _extract_content(self, soup: BeautifulSoup, url: str) -> str:
        """
        Extract main content from page.
        
        Strategy:
        1. Remove unwanted elements (nav, footer, script, style, ads)
        2. Look for main content containers
        3. Extract text from relevant tags
        
        Args:
            soup: BeautifulSoup object
            url: Page URL (for type detection)
            
        Returns:
            Extracted text content
        """
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 
                            'aside', 'form', 'iframe', 'noscript']):
            element.decompose()
        
        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        # Remove common ad/tracking containers
        ad_classes = ['ad', 'advertisement', 'sponsor', 'popup', 'modal', 
                     'cookie', 'gdpr', 'sidebar', 'related', 'trending']
        for ad_class in ad_classes:
            for element in soup.find_all(class_=lambda x: x and ad_class in x.lower()):
                element.decompose()
        
        # Website-type specific extraction
        website_type = detect_website_type(url)
        
        if website_type == 'github':
            return self._extract_github_content(soup)
        elif website_type == 'news':
            return self._extract_news_content(soup)
        else:
            return self._extract_normal_content(soup)
    
    def _extract_github_content(self, soup: BeautifulSoup) -> str:
        """Extract content from GitHub pages (README, docs, wiki)."""
        # GitHub uses specific containers
        readme = soup.find('article', class_=lambda x: x and 'markdown' in x.lower())
        if readme:
            return readme.get_text(separator='\n', strip=True)
        
        # Fallback to main content
        main = soup.find('main') or soup.find('div', id='readme')
        if main:
            return main.get_text(separator='\n', strip=True)
        
        # Last resort: get all paragraphs and headings
        return self._extract_text_from_tags(soup, ['h1', 'h2', 'h3', 'p', 'li', 'code'])
    
    def _extract_news_content(self, soup: BeautifulSoup) -> str:
        """Extract content from news articles."""
        # Common news article containers
        article = soup.find('article')
        if article:
            # Remove author, date, share buttons within article
            for unwanted in article.find_all(['time', 'a'], class_=lambda x: x and any(
                term in x.lower() for term in ['share', 'author', 'byline']
            )):
                unwanted.decompose()
            
            return article.get_text(separator='\n', strip=True)
        
        # Fallback: look for main content
        main = soup.find('main') or soup.find('div', class_=lambda x: x and 'content' in x.lower())
        if main:
            return main.get_text(separator='\n', strip=True)
        
        return self._extract_text_from_tags(soup, ['h1', 'h2', 'h3', 'p'])
    
    def _extract_normal_content(self, soup: BeautifulSoup) -> str:
        """Extract content from normal websites."""
        # Try to find main content container
        main = soup.find('main') or soup.find('article') or soup.find('div', class_=lambda x: x and 'content' in x.lower())
        
        if main:
            return main.get_text(separator='\n', strip=True)
        
        # Fallback: extract from relevant tags
        return self._extract_text_from_tags(soup, ['h1', 'h2', 'h3', 'h4', 'p', 'li', 'td'])
    
    def _extract_text_from_tags(self, soup: BeautifulSoup, tags: list) -> str:
        """
        Extract text from specific HTML tags.
        
        Args:
            soup: BeautifulSoup object
            tags: List of tag names
            
        Returns:
            Concatenated text
        """
        texts = []
        for tag in tags:
            for element in soup.find_all(tag):
                text = element.get_text(strip=True)
                if text and len(text) > 10:  # Skip very short snippets
                    texts.append(text)
        
        return '\n'.join(texts)
    
    def close(self):
        """Close the session."""
        self.session.close()
