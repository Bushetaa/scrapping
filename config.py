"""
Configuration settings for the Discord bot and scraper
"""
import os

# Discord configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN', 'YOUR_DISCORD_TOKEN_HERE')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID', '1396655830690173029'))  # User's channel

# Social media URLs to monitor
SOCIAL_MEDIA_URLS = {
    'LinkedIn': 'https://www.linkedin.com/company/solidpointai/',
    'TikTok': 'https://www.tiktok.com/@solidpointai',
    'X': 'https://x.com/SolidPoint11'
}

# Scraping configuration
SCRAPING_INTERVAL = 300  # 5 minutes in seconds
REQUEST_TIMEOUT = 30000  # 30 seconds for Playwright
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Database configuration
DATABASE_PATH = 'social_media_bot.db'

# Dashboard configuration
DASHBOARD_REFRESH_INTERVAL = 10  # seconds
