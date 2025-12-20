"""
Web crawler with focused, ethical crawling.

Features:
- Same-domain restriction
- Depth limiting
- Robots.txt respect
- Rate limiting
- Smart filtering based on website type
"""
import logging
import time
import requests
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from typing import List, Set, Dict, Optional
from bs4 import BeautifulSoup

from config import settings
from utils.url_utils import (
    normalize_url, is_valid_url, is_same_domain, should_skip_url,
    detect_website_type, is_github_relevant_path, get_domain
)


class WebCrawler:
    """
    Focused web crawler that respects robots.txt and crawls ethically.
    Adapts behavior based on website type (GitHub, news, normal).
    Uses ThreadPoolExecutor for parallel crawling.
    """
    
    def __init__(self, start_url: str):
        """
        Initialize crawler for a specific website.
        
        Args:
            start_url: Starting URL to crawl from
        """
        self.start_url = normalize_url(start_url)
        self.domain = get_domain(self.start_url)
        self.website_type = detect_website_type(self.start_url)
        
        # Crawling state (Thread-safe)
        import threading
        self.lock = threading.Lock()
        self.visited: Set[str] = set()
        self.to_visit: List[tuple] = [(self.start_url, 0)]  # (url, depth)
        self.discovered_urls: List[str] = []
        self.content_cache: Dict[str, str] = {}  # Cache for raw HTML
        self.edges: Set[tuple] = set()  # (source, target) tuples for graph visualization
        
        # Robots.txt parser
        self.robot_parser = RobotFileParser()
        self._init_robots_txt()
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RAGBot/1.0; Educational)'
        })
    
    def _init_robots_txt(self):
        """Initialize robots.txt parser."""
        try:
            robots_url = f"{urlparse(self.start_url).scheme}://{self.domain}/robots.txt"
            self.robot_parser.set_url(robots_url)
            self.robot_parser.read()
        except Exception:
            pass
    
    def _can_fetch(self, url: str) -> bool:
        """Check if URL can be fetched according to robots.txt."""
        try:
            return self.robot_parser.can_fetch("*", url)
        except Exception:
            return True
    
    def _should_crawl_url(self, url: str, depth: int) -> bool:
        """Determine if URL should be crawled based on all filters."""
        with self.lock:
            # Already visited check inside lock
            if url in self.visited:
                # print(f"[DEBUG] Skipping {url} - Already visited")
                return False
            
            # Page limit check inside lock
            if len(self.visited) >= settings.MAX_PAGES_PER_SITE:
                # logger.info(f"[CRAWL] Reached max pages ({settings.MAX_PAGES_PER_SITE})")
                return False
        
        # Depth limit
        if depth > settings.MAX_CRAWL_DEPTH:
            logger.debug(f"[DEBUG] Skipping {url} - Max depth exceeded ({depth})")
            return False
        
        # Invalid URL
        if not is_valid_url(url):
            logger.debug(f"[DEBUG] Skipping {url} - Invalid URL")
            return False
        
        # Different domain
        if not is_same_domain(url, self.start_url):
            logger.debug(f"[DEBUG] Skipping {url} - Different domain (Start: {self.start_url})")
            return False
        
        # Robots.txt check
        if not self._can_fetch(url):
            logger.debug(f"[DEBUG] Skipping {url} - Disallowed by robots.txt")
            return False
        
        # URL blacklist patterns
        if should_skip_url(url):
            logger.debug(f"[DEBUG] Skipping {url} - Blacklisted pattern/scheme")
            return False
        
        # Website-type specific filtering
        if self.website_type == 'github':
            if not is_github_relevant_path(url):
                return False
        
        return True
    
    def _extract_links(self, html: str, base_url: str) -> List[str]:
        """
        Extract and normalize links from HTML.
        Also tracks edges for graph visualization.
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            links = []
            
            for link_tag in soup.find_all('a', href=True):
                href = link_tag['href']
                absolute_url = urljoin(base_url, href)
                normalized = normalize_url(absolute_url)
                
                # Track global edges even if we don't crawl them (for visualization)
                # But only if it's generally same domain to avoid clutter
                if normalized and is_same_domain(normalized, self.start_url):
                     with self.lock:
                         self.edges.add((base_url, normalized))

                if normalized and normalized not in links:
                    links.append(normalized)
            
            return links
        except Exception:
            return []
    
    def _adjust_depth_for_website_type(self) -> int:
        """Adjust max depth based on website type."""
        if self.website_type == 'github':
            return 1
        elif self.website_type == 'news':
            return 3  # Increased for news coverage
        else:
            return settings.MAX_CRAWL_DEPTH
    
    def _process_url(self, item: tuple) -> List[tuple]:
        """
        Process a single URL: fetch, extract links, return new links to visit.
        Result is a list of (url, depth) tuples.
        """
        url, depth = item
        
        # Check strict filters (robots, blacklist, scheme, etc)
        # This prevents crawling mailto:, tel:, and other invalid URLs
        if not self._should_crawl_url(url, depth):
            return []
        
        # Final check with lock
        with self.lock:
            if url in self.visited or len(self.visited) >= settings.MAX_PAGES_PER_SITE:
                return []
            self.visited.add(url)
            self.discovered_urls.append(url)
        
        try:
            # Tiny delay if configured (usually 0.0 now)
            if settings.CRAWL_DELAY_SECONDS > 0:
                time.sleep(settings.CRAWL_DELAY_SECONDS)
            
            response = self.session.get(url, timeout=30)
            
            # content type check
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                return []
            
            response.raise_for_status()
            
            # Cache content
            with self.lock:
                self.content_cache[url] = response.text
            
            # Extract links
            new_items = []
            max_depth = self._adjust_depth_for_website_type()
            
            if depth < max_depth:
                links = self._extract_links(response.text, url)
                for link in links:
                    new_items.append((link, depth + 1))
            
            return new_items
            
        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")
            return []

    def crawl(self) -> List[str]:
        """
        Execute parallel crawl.
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        # Max threads = 10 for reasonable speed without ban risk
        max_workers = 10
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # We need to manage the queue manually because we discover links dynamically
            # Submit initial URL
            futures = {executor.submit(self._process_url, (self.start_url, 0))}
            
            while futures and len(self.visited) < settings.MAX_PAGES_PER_SITE:
                # Wait for at least one future to complete
                done, _ = as_completed(futures, timeout=None) # Wait for any
                
                # If "done" is empty but futures is not, it means as_completed returned iterator.
                # Actually as_completed yields futures as they complete.
                # We can't iterate simply because we add new futures.
                
                # Better approach: Manage a set of active futures
                # Since as_completed is an iterator, we can't easily add to it.
                # So we iterate manual list of futures.
                pass
                
    def _try_fetch_sitemap(self) -> List[str]:
        """Attempt to fetch URLs from sitemap.xml."""
        sitemap_urls = [
            f"{urlparse(self.start_url).scheme}://{self.domain}/sitemap.xml",
            f"{urlparse(self.start_url).scheme}://{self.domain}/sitemap_index.xml",
            f"{urlparse(self.start_url).scheme}://{self.domain}/wp-sitemap.xml" # Common for WordPress
        ]
        
        found_urls = []
        
        for sitemap_url in sitemap_urls:
            try:
                logger.info(f"[CRAWL] Checking sitemap: {sitemap_url}")
                response = self.session.get(sitemap_url, timeout=10)
                if response.status_code == 200:
                    # Parse XML
                    soup = BeautifulSoup(response.content, 'lxml-xml')
                    urls = [loc.text for loc in soup.find_all('loc')]
                    
                    # Filter valid URLs
                    valid_urls = [
                        u for u in urls 
                        if is_valid_url(u) and is_same_domain(u, self.start_url)
                    ]
                    
                    if valid_urls:
                        logger.info(f"[CRAWL] Found {len(valid_urls)} URLs in sitemap")
                        found_urls.extend(valid_urls)
                        # If we found a working sitemap, stop looking for others
                        if len(found_urls) > 10: 
                             break
            except Exception as e:
                logger.warning(f"[CRAWL] Sitemap check failed for {sitemap_url}: {str(e)}")
                continue
                
        return list(set(found_urls))

    def crawl(self) -> List[str]:
        """
        Execute parallel crawl.
        """
        # Try sitemap first for speed
        sitemap_urls = self._try_fetch_sitemap()
        
        if sitemap_urls:
            logger.info(f"[CRAWL] Using Sitemap mode. Processing {len(sitemap_urls)} URLs...")
            # If we generally trust the sitemap, we can just process these
            # Use a larger queue if needed, but for now replace to_visit
            # We treat them as depth 0 since they are 'root' discovered
            self.to_visit = [(u, 0) for u in sitemap_urls[:settings.MAX_PAGES_PER_SITE]]
            
        return self._crawl_parallel_logic()

    def _crawl_parallel_logic(self) -> List[str]:
        from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
        
        # Super fast mode: 50 threads
        max_workers = 50
        executor = ThreadPoolExecutor(max_workers=max_workers)
        futures = set()
        
        # Submit first
        futures.add(executor.submit(self._process_url, (self.start_url, 0)))
        
        while futures and len(self.visited) < settings.MAX_PAGES_PER_SITE:
            done, not_done = wait(futures, return_when=FIRST_COMPLETED)
            
            for future in done:
                try:
                    new_items = future.result()
                    for item in new_items:
                        url, depth = item
                        should_add = False
                        with self.lock:
                            if url not in self.visited and len(self.visited) < settings.MAX_PAGES_PER_SITE:
                                should_add = True
                        
                        if should_add:
                            # Avoid duplicates in queue - heuristic
                            # Ideally we need a 'queued' set too, but for now this is okay
                            futures.add(executor.submit(self._process_url, item))
                            
                except Exception as e:
                    print(f"Worker exception: {e}")
            
            futures = not_done
            
        executor.shutdown(wait=False)
        return self.discovered_urls

    def crawl(self) -> List[str]:
        return self._crawl_parallel_logic()

    def get_content(self, url: str) -> Optional[str]:
        """Get cached content for a URL."""
        return self.content_cache.get(url)

    def close(self):
        """Close the session."""
        self.session.close()
