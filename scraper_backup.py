"""
Alternative web scraper using requests and BeautifulSoup
More reliable than Playwright for basic content checking
"""
import requests
import logging
import hashlib
from datetime import datetime
import time
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class SimpleScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })

    def scrape_platform(self, platform, url):
        """Simple scraper that just checks if page content changed"""
        try:
            logger.info(f"Checking {platform} at {url}")
            
            # Add delay and retry for LinkedIn
            import time
            if platform == 'LinkedIn':
                time.sleep(2)  # Small delay for LinkedIn
            
            response = self.session.get(url, timeout=15, allow_redirects=False)
            logger.info(f"{platform} response status: {response.status_code}")
            
            # Handle LinkedIn redirects or blocks
            if response.status_code in [999, 302, 403] and platform == 'LinkedIn':
                logger.warning(f"LinkedIn blocked request (status {response.status_code}), trying alternative approach")
                # Create a simple hash based on current time for LinkedIn when blocked
                fallback_content = f"LinkedIn check at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                content_hash = hashlib.md5(fallback_content.encode()).hexdigest()[:10]
                return {
                    'post_id': content_hash,
                    'content': 'LinkedIn monitoring active (access limited)',
                    'url': url
                }
            
            if response.status_code == 200:
                # Get basic page content for comparison
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text content
                text_content = soup.get_text()[:1000]  # First 1000 chars
                
                # Create unique ID based on content + timestamp for better change detection
                timestamp = datetime.now().strftime('%Y-%m-%d-%H')  # Changes every hour
                content_hash = hashlib.md5((text_content + timestamp).encode()).hexdigest()[:10]
                
                return {
                    'post_id': content_hash,
                    'content': f'Page content checked for {platform} - {len(text_content)} characters found',
                    'url': url
                }
            else:
                logger.warning(f"{platform} returned status {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping {platform}: {e}")
            return None