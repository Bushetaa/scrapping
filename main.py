"""
Main entry point for the Discord Bot with Social Media Scraper
Runs both the Discord bot and the web dashboard concurrently
"""
import asyncio
import threading
import logging
from bot import DiscordBot
from dashboard import app as dashboard_app
from database import init_database

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_dashboard():
    """Run the Flask dashboard in a separate thread"""
    try:
        dashboard_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Dashboard failed to start: {e}")

async def main():
    """Main function to run both bot and dashboard"""
    logger.info("Initializing database...")
    init_database()
    
    logger.info("Starting dashboard server...")
    # Start dashboard in a separate thread
    dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
    dashboard_thread.start()
    
    logger.info("Starting Discord bot...")
    # Start the Discord bot
    bot = DiscordBot()
    await bot.start_bot()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application crashed: {e}")
