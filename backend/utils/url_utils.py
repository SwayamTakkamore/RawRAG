"""
URL validation, parsing, and filtering utilities.
"""
import re
from urllib.parse import urlparse, urljoin, urlunparse
from typing import Optional


def normalize_url(url: str) -> str:
    """
    Normalize URL by removing fragments, common tracking parameters.
    
    Args:
        url: Raw URL string
        
    Returns:
        Normalized URL
    """
    parsed = urlparse(url)
    
    # Remove fragment
    parsed = parsed._replace(fragment='')
    
    # Remove common tracking parameters
    if parsed.query:
        query_params = parsed.query.split('&')
        filtered_params = [
            p for p in query_params 
            if not any(p.startswith(track) for track in [
                'utm_', 'fbclid', 'gclid', 'ref=', '_ga', 'mc_', 'campaign'
            ])
        ]
        parsed = parsed._replace(query='&'.join(filtered_params) if filtered_params else '')
    
    return urlunparse(parsed)


def is_valid_url(url: str) -> bool:
    """
    Check if URL is valid and uses http/https scheme.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        parsed = urlparse(url)
        return parsed.scheme in ['http', 'https'] and bool(parsed.netloc)
    except Exception:
        return False


def get_domain(url: str) -> Optional[str]:
    """
    Extract domain from URL.
    
    Args:
        url: URL string
        
    Returns:
        Domain (e.g., 'example.com') or None if invalid
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except Exception:
        return None


def is_same_domain(url1: str, url2: str) -> bool:
    """
    Check if two URLs belong to the same domain.
    
    Args:
        url1: First URL
        url2: Second URL
        
    Returns:
        True if same domain, False otherwise
    """
    return get_domain(url1) == get_domain(url2)


def should_skip_url(url: str) -> bool:
    """
    Check if URL should be skipped based on blacklist patterns.
    
    Filters out:
    - Media files (images, videos, css, js)
    - Login/signup pages
    - External tracking domains
    - Common unwanted paths
    
    Args:
        url: URL to check
        
    Returns:
        True if should skip, False otherwise
    """
    url_lower = url.lower()

    # Skip invalid schemes
    if any(url_lower.startswith(scheme) for scheme in ['mailto:', 'tel:', 'javascript:', 'data:', 'file:']):
        return True
    skip_extensions = [
        '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico',
        '.mp4', '.avi', '.mov', '.wmv', '.flv',
        '.mp3', '.wav', '.ogg',
        '.pdf', '.zip', '.tar', '.gz', '.rar',
        '.css', '.js', '.json', '.xml',
        '.woff', '.woff2', '.ttf', '.eot'
    ]
    
    if any(url_lower.endswith(ext) for ext in skip_extensions):
        return True
    
    # Path patterns to skip
    skip_patterns = [
        '/login', '/signin', '/signup', '/register',
        '/auth/', '/logout',
        '/cart', '/checkout', '/payment',
        '/admin/', '/wp-admin/',
        '/cdn-cgi/', '/ajax/',
        '/_next/', '/static/',
        '/embed/', '/widget/',
        '/share?', '/print',
    ]
    
    if any(pattern in url_lower for pattern in skip_patterns):
        return True
    
    # External tracking/social domains
    skip_domains = [
        'facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com',
        'youtube.com', 'vimeo.com',
        'google-analytics.com', 'doubleclick.net',
        'adservice.', 'ads.',
    ]
    
    domain = get_domain(url)
    if domain and any(skip in domain for skip in skip_domains):
        return True
    
    return False


def detect_website_type(url: str) -> str:
    """
    Detect the type of website from URL.
    
    Types:
    - 'github': GitHub repository
    - 'news': News website
    - 'normal': Regular website
    
    Args:
        url: Website URL
        
    Returns:
        Website type identifier
    """
    domain = get_domain(url)
    
    if not domain:
        return 'normal'
    
    # GitHub repository detection
    if 'github.com' in domain:
        # Check if it's a repository URL (not gist, issues, etc.)
        if re.search(r'github\.com/[^/]+/[^/]+/?$', url) or '/tree/' in url or '/blob/' in url:
            return 'github'
    
    # News website detection (common news domains)
    news_indicators = [
        'news', 'times', 'post', 'herald', 'tribune', 'journal',
        'bbc.co', 'cnn.com', 'reuters.com', 'ap.org',
        'theguardian.com', 'nytimes.com', 'wsj.com',
        'bloomberg.com', 'forbes.com'
    ]
    
    if any(indicator in domain for indicator in news_indicators):
        return 'news'
    
    return 'normal'


def is_github_relevant_path(url: str) -> bool:
    """
    Check if GitHub URL path should be indexed.
    
    Only index: README, /docs, /wiki
    Skip: issues, pulls, commits, stars, etc.
    
    Args:
        url: GitHub URL
        
    Returns:
        True if should be indexed, False otherwise
    """
    if 'github.com' not in url:
        return True  # Not a GitHub URL
    
    skip_paths = [
        '/issues', '/pull', '/commit', '/releases',
        '/stargazers', '/watchers', '/network',
        '/graphs', '/pulse', '/settings',
        '/actions', '/projects', '/security'
    ]
    
    # Skip unwanted GitHub sections
    if any(path in url for path in skip_paths):
        return False
    
    # Allow main repo page, docs, wiki, blob (code view)
    allow_paths = ['README', '/docs', '/wiki', '/blob', '/tree']
    
    # If it's the main repo page (no subpath), allow it
    if re.match(r'https://github\.com/[^/]+/[^/]+/?$', url):
        return True
    
    return any(path in url for path in allow_paths)
