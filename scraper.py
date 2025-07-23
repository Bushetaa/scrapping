"""
Social media scraper using Playwright for dynamic content
"""
import asyncio
import logging
from datetime import datetime
from playwright.async_api import async_playwright
from config import USER_AGENT, REQUEST_TIMEOUT
import hashlib
import re

logger = logging.getLogger(__name__)

class SocialMediaScraper:
    def __init__(self):
        self.browser = None
        self.context = None

    async def init_browser(self):
        """Initialize Playwright browser"""
        try:
            self.playwright = await async_playwright().start()
            # Try Firefox first as it has better compatibility
            try:
                self.browser = await self.playwright.firefox.launch(
                    headless=True,
                    args=['--no-sandbox']
                )
            except Exception as firefox_error:
                logger.warning(f"Firefox failed, trying Chromium: {firefox_error}")
                # Fallback to Chromium with system detection
                self.browser = await self.playwright.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-blink-features=AutomationControlled', '--disable-dev-shm-usage']
                )
            self.context = await self.browser.new_context(
                user_agent=USER_AGENT,
                viewport={'width': 1920, 'height': 1080}
            )
            logger.info("Browser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise

    async def close_browser(self):
        """Close browser and cleanup"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")

    async def scrape_linkedin(self, url):
        """Scrape LinkedIn company page"""
        page = None
        try:
            if not self.context:
                raise Exception("Browser context not initialized")
                
            page = await self.context.new_page()
            await page.goto(url, timeout=REQUEST_TIMEOUT)
            await page.wait_for_timeout(3000)  # Wait for content to load
            
            # Try to find recent posts
            posts = await page.query_selector_all('.feed-shared-update-v2')
            
            if not posts:
                # Alternative selectors for LinkedIn posts
                posts = await page.query_selector_all('[data-urn*="update"]')
            
            if posts:
                first_post = posts[0]
                
                # Extract post content
                content_elem = await first_post.query_selector('.feed-shared-text')
                content = ''
                if content_elem:
                    content = await content_elem.text_content()
                
                # Create a unique identifier
                content_str = content or ""
                post_id = hashlib.md5((content_str + str(datetime.now().date())).encode()).hexdigest()[:10]
                
                await page.close()
                return {
                    'post_id': post_id,
                    'content': content.strip()[:200] if content else 'LinkedIn post found',
                    'url': url
                }
            
            await page.close()
            return None
            
        except Exception as e:
            logger.error(f"LinkedIn scraping error: {e}")
            if page:
                await page.close()
            raise

    async def scrape_tiktok(self, url):
        """Scrape TikTok profile page"""
        page = None
        try:
            if not self.context:
                raise Exception("Browser context not initialized")
                
            page = await self.context.new_page()
            await page.goto(url, timeout=REQUEST_TIMEOUT)
            await page.wait_for_timeout(5000)  # TikTok needs more time to load
            
            # Look for video elements
            videos = await page.query_selector_all('[data-e2e="user-post-item"]')
            
            if not videos:
                # Alternative selector
                videos = await page.query_selector_all('div[class*="video"]')
            
            if videos:
                first_video = videos[0]
                
                # Try to get video link
                link_elem = await first_video.query_selector('a')
                video_url = url
                if link_elem:
                    href = await link_elem.get_attribute('href')
                    if href:
                        video_url = href if href.startswith('http') else f'https://www.tiktok.com{href}'
                
                # Create unique identifier based on video URL or current date
                post_id = hashlib.md5((video_url + str(datetime.now().date())).encode()).hexdigest()[:10]
                
                await page.close()
                return {
                    'post_id': post_id,
                    'content': 'New TikTok video available',
                    'url': video_url
                }
            
            await page.close()
            return None
            
        except Exception as e:
            logger.error(f"TikTok scraping error: {e}")
            if page:
                await page.close()
            raise

    async def scrape_facebook(self, url):
        """Scrape Facebook profile page"""
        page = None
        try:
            if not self.context:
                raise Exception("Browser context not initialized")
                
            page = await self.context.new_page()
            await page.goto(url, timeout=REQUEST_TIMEOUT)
            await page.wait_for_timeout(4000)
            
            # Look for posts - Facebook structure varies
            posts = await page.query_selector_all('[role="article"]')
            
            if not posts:
                # Alternative selectors
                posts = await page.query_selector_all('div[data-pagelet*="FeedUnit"]')
            
            if posts:
                first_post = posts[0]
                
                # Try to extract post text
                text_elem = await first_post.query_selector('[data-ad-preview="message"]')
                content = ''
                if text_elem:
                    content = await text_elem.text_content()
                
                if not content:
                    # Try alternative text selectors
                    text_elems = await first_post.query_selector_all('div[dir="auto"]')
                    if text_elems:
                        content = await text_elems[0].text_content()
                
                # Create unique identifier
                content_str = content or ""
                post_id = hashlib.md5((content_str + str(datetime.now().date())).encode()).hexdigest()[:10]
                
                await page.close()
                return {
                    'post_id': post_id,
                    'content': content.strip()[:200] if content else 'Facebook post found',
                    'url': url
                }
            
            await page.close()  
            return None
            
        except Exception as e:
            logger.error(f"Facebook scraping error: {e}")
            if page:
                await page.close()
            raise

    async def scrape_twitter(self, url):
        """Scrape X (Twitter) profile page"""
        page = None
        try:
            if not self.context:
                raise Exception("Browser context not initialized")
                
            page = await self.context.new_page()
            await page.goto(url, timeout=REQUEST_TIMEOUT)
            await page.wait_for_timeout(4000)
            
            # Look for tweets
            tweets = await page.query_selector_all('[data-testid="tweet"]')
            
            if tweets:
                first_tweet = tweets[0]
                
                # Extract tweet text
                text_elem = await first_tweet.query_selector('[data-testid="tweetText"]')
                content = ''
                if text_elem:
                    content = await text_elem.text_content()
                
                # Try to get tweet link
                link_elem = await first_tweet.query_selector('a[href*="/status/"]')
                tweet_url = url
                if link_elem:
                    href = await link_elem.get_attribute('href')
                    if href:
                        tweet_url = f'https://x.com{href}' if href.startswith('/') else href
                
                # Extract tweet ID from URL for unique identification
                tweet_match = re.search(r'/status/(\d+)', tweet_url)
                content_str = content or ""
                post_id = tweet_match.group(1) if tweet_match else hashlib.md5((content_str + str(datetime.now().date())).encode()).hexdigest()[:10]
                
                await page.close()
                return {
                    'post_id': post_id,
                    'content': content.strip()[:200] if content else 'Tweet found',
                    'url': tweet_url
                }
            
            await page.close()
            return None
            
        except Exception as e:
            logger.error(f"Twitter scraping error: {e}")
            if page:
                await page.close()
            raise

    async def scrape_platform(self, platform, url):
        """Scrape a specific platform"""
        try:
            if not self.browser:
                await self.init_browser()
            
            if platform.lower() == 'linkedin':
                return await self.scrape_linkedin(url)
            elif platform.lower() == 'tiktok':
                return await self.scrape_tiktok(url)
            elif platform.lower() == 'facebook':
                return await self.scrape_facebook(url)
            elif platform.lower() == 'x':
                return await self.scrape_twitter(url)
            else:
                logger.error(f"Unknown platform: {platform}")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping {platform}: {e}")
            return None
