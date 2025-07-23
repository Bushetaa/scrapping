"""
Discord bot for social media monitoring and notifications
"""
import asyncio
import logging
import discord
from discord.ext import tasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from typing import Optional, Union
from config import DISCORD_TOKEN, DISCORD_CHANNEL_ID, SOCIAL_MEDIA_URLS, SCRAPING_INTERVAL
from scraper import SocialMediaScraper
from scraper_backup import SimpleScraper
from database import get_last_post, update_post_status, reset_new_post_flags

logger = logging.getLogger(__name__)

class DiscordBot:
    def __init__(self):
        # Set up Discord intents (minimal requirements)
        intents = discord.Intents.default()
        intents.message_content = False  # Don't need message content for this bot
        intents.guilds = True  # Need to access guild channels
        
        self.client = discord.Client(intents=intents)
        self.scraper = SocialMediaScraper()
        self.backup_scraper = SimpleScraper()  # Fallback scraper
        self.scheduler = AsyncIOScheduler()
        self.channel: Optional[discord.TextChannel] = None
        
        # Set up event handlers
        self.setup_events()

    def setup_events(self):
        """Set up Discord bot event handlers"""
        
        @self.client.event
        async def on_ready():
            logger.info(f'Bot logged in as {self.client.user}')
            
            # Get the channel to send messages to
            if DISCORD_CHANNEL_ID:
                channel = self.client.get_channel(DISCORD_CHANNEL_ID)
                if isinstance(channel, discord.TextChannel):
                    self.channel = channel
                    logger.info(f'Connected to channel: {channel.name}')
                    await self.channel.send('🤖 Social Media Monitor Bot is now online and monitoring!')
                else:
                    logger.error(f'Could not find text channel with ID: {DISCORD_CHANNEL_ID}')
            else:
                logger.warning('No Discord channel ID configured')
            
            # Start the monitoring scheduler
            self.scheduler.add_job(
                self.check_all_platforms,
                'interval',
                seconds=SCRAPING_INTERVAL,
                id='social_media_check'
            )
            self.scheduler.start()
            logger.info(f'Scheduler started - checking every {SCRAPING_INTERVAL} seconds')
            
            # Do an initial check
            await self.check_all_platforms()

        @self.client.event
        async def on_message(message):
            # Ignore messages from the bot itself
            if message.author == self.client.user:
                return
            
            # Simple commands for monitoring
            if message.content.startswith('!status'):
                await self.send_status_update(message.channel)
            elif message.content.startswith('!check'):
                await message.channel.send('🔄 Running manual check...')
                await self.check_all_platforms()
                await message.channel.send('✅ Manual check completed!')

    async def check_all_platforms(self):
        """Check all social media platforms for new posts"""
        logger.info("Starting platform check cycle...")
        
        try:
            # Try to initialize main browser, but don't fail if it doesn't work
            try:
                if not self.scraper.browser:
                    await self.scraper.init_browser()
            except Exception as browser_error:
                logger.warning(f"Main browser failed to initialize: {browser_error}")
                logger.info("Will use backup scraper for all platforms")
            
            for platform, url in SOCIAL_MEDIA_URLS.items():
                await self.check_platform(platform, url)
                # Small delay between platform checks
                await asyncio.sleep(2)
                
        except Exception as e:
            logger.error(f"Error during platform check cycle: {e}")
        
        logger.info("Platform check cycle completed")

    async def check_platform(self, platform, url):
        """Check a specific platform for new posts"""
        try:
            logger.info(f"Checking {platform}...")
            
            # Get the last known post
            last_post = get_last_post(platform)
            
            # Use backup scraper only (main scraper has browser issues)
            current_post = None
            logger.info(f"Using backup scraper for {platform}")
            try:
                current_post = self.backup_scraper.scrape_platform(platform, url)
                if current_post:
                    logger.info(f"Backup scraper succeeded for {platform}: {current_post['post_id']}")
                else:
                    logger.warning(f"Backup scraper returned None for {platform}")
            except Exception as backup_error:
                logger.error(f"Backup scraper failed for {platform}: {backup_error}")
                current_post = None
            
            if current_post is None:
                # Scraping failed or no posts found
                update_post_status(platform, url, error_message="No posts found or scraping failed")
                logger.warning(f"No posts found for {platform}")
                return
            
            # Check if this is a new post
            is_new = False
            if last_post is None:
                # First time checking this platform
                is_new = True
                logger.info(f"First post detected for {platform}")
            elif last_post['post_id'] != current_post['post_id']:
                # Post ID changed, new post detected
                is_new = True
                logger.info(f"New post detected for {platform}")
            
            # Update database
            update_post_status(platform, url, current_post, is_new=is_new)
            
            # Send Discord notification for new posts
            if is_new and self.channel:
                await self.send_new_post_notification(platform, current_post)
                
        except Exception as e:
            logger.error(f"Error checking {platform}: {e}")
            update_post_status(platform, url, error_message=str(e))

    async def send_new_post_notification(self, platform, post_data):
        """Send a Discord notification for a new post"""
        try:
            if not self.channel:
                logger.warning("No Discord channel configured for notifications")
                return
                
            embed = discord.Embed(
                title=f"🆕 New {platform} Post Detected!",
                color=self.get_platform_color(platform),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="Content Preview",
                value=post_data['content'][:500] + ('...' if len(post_data['content']) > 500 else ''),
                inline=False
            )
            
            embed.add_field(
                name="Link",
                value=post_data['url'],
                inline=False
            )
            
            embed.set_footer(text=f"Social Media Monitor Bot")
            
            await self.channel.send(embed=embed)
            logger.info(f"Sent notification for new {platform} post")
            
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")

    async def send_status_update(self, channel):
        """Send current monitoring status to Discord"""
        try:
            from database import get_all_monitoring_status
            
            status_list = get_all_monitoring_status()
            
            embed = discord.Embed(
                title="📊 Social Media Monitoring Status",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            
            for status in status_list:
                success_rate = f"{(status['success_count'] / max(status['check_count'], 1) * 100):.1f}%"
                
                field_value = f"**Last Check:** {status['last_checked'] or 'Never'}\n"
                field_value += f"**Success Rate:** {success_rate}\n"
                field_value += f"**Status:** {'✅ New Post' if status['has_new_post'] else '⭕ No Changes'}\n"
                
                if status['error_message']:
                    field_value += f"**Error:** {status['error_message'][:100]}\n"
                
                embed.add_field(
                    name=f"{status['platform']}",
                    value=field_value,
                    inline=True
                )
            
            await channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Failed to send status update: {e}")

    def get_platform_color(self, platform):
        """Get Discord embed color for each platform"""
        colors = {
            'LinkedIn': 0x0077B5,
            'TikTok': 0xFF0050,
            'Facebook': 0x1877F2,
            'X': 0x1DA1F2
        }
        return colors.get(platform, 0x7289DA)

    async def start_bot(self):
        """Start the Discord bot"""
        try:
            await self.client.start(DISCORD_TOKEN)
        except Exception as e:
            logger.error(f"Failed to start Discord bot: {e}")
            raise
        finally:
            # Cleanup
            if self.scraper:
                await self.scraper.close_browser()
