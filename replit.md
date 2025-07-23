# Discord Bot with Social Media Scraper + Live Status Dashboard

## Overview

This project is a Python-based Discord bot that automatically monitors social media platforms (LinkedIn, TikTok, Facebook, and X/Twitter) for new posts and provides real-time notifications through Discord and a web dashboard. The system scrapes social media URLs every 5 minutes, detects new content, and sends automated alerts to a specified Discord channel.

## User Preferences

Preferred communication style: Simple, everyday language in Arabic when communicating with Arabic users.

## Recent Status (July 23, 2025)

### Working Components:
- Discord bot successfully connected (media#2523)
- Web dashboard running on port 5000 with real-time monitoring
- Backup scraper system implemented using requests/BeautifulSoup
- Database storing monitoring data successfully
- LinkedIn, TikTok, and X (Twitter) monitoring functional

### Issues Resolved:
- Playwright browser compatibility issues → Implemented SimpleScraper fallback
- Empty database → Populated with monitoring data
- Failed platform checks → Working with backup scraper system

### Remaining Setup:
- Discord Channel ID needs user configuration for notifications
- Facebook access blocked (HTTP 400 error)
- User needs to test with new LinkedIn posts

## System Architecture

The application follows a multi-threaded architecture with the following key components:

### Core Architecture
- **Discord Bot**: Asynchronous Discord client using discord.py for real-time notifications
- **Web Scraper**: Playwright-based scraper for dynamic content extraction from social media platforms
- **Web Dashboard**: Flask-based web interface for monitoring system status
- **Database Layer**: SQLite database for persistent storage of posts and monitoring status
- **Scheduler**: APScheduler for automated periodic scraping (5-minute intervals)

### Threading Model
- Main thread runs the Discord bot with async event loop
- Separate daemon thread runs the Flask web dashboard
- Scheduled tasks execute within the async event loop

## Key Components

### 1. Discord Bot (`bot.py`)
- **Purpose**: Handles Discord integration and automated notifications
- **Key Features**: 
  - Async event handling for Discord events
  - Scheduled monitoring tasks using APScheduler
  - Channel message posting for new post alerts
  - Error handling and status reporting

### 2. Social Media Scraper (`scraper.py`)
- **Purpose**: Extracts content from social media platforms
- **Technology**: Playwright with Chromium browser
- **Features**:
  - Headless browser automation
  - Platform-specific scraping logic
  - Content change detection
  - Error handling and retry mechanisms

### 3. Web Dashboard (`dashboard.py`)
- **Purpose**: Provides real-time monitoring interface
- **Technology**: Flask web framework
- **Features**:
  - RESTful API endpoints for status data
  - Real-time dashboard with auto-refresh
  - Platform monitoring statistics
  - Error reporting and success rates

### 4. Database Layer (`database.py`)
- **Purpose**: Persistent storage for monitoring data
- **Technology**: SQLite with raw SQL queries
- **Schema**:
  - `posts` table: Individual post records
  - `monitoring_status` table: Platform monitoring state

### 5. Configuration Management (`config.py`)
- **Purpose**: Centralized configuration and environment variables
- **Features**:
  - Discord bot credentials
  - Social media URLs to monitor
  - Scraping intervals and timeouts
  - Database and dashboard settings

## Data Flow

1. **Initialization**: Database tables are created, Discord bot connects, web dashboard starts
2. **Scheduled Monitoring**: Every 5 minutes, the scheduler triggers social media checks
3. **Content Extraction**: Playwright scraper visits each platform URL
4. **Change Detection**: New content is compared against stored previous posts
5. **Notification**: Discord messages are sent for detected new posts
6. **Status Update**: Database records are updated with latest monitoring results
7. **Dashboard Display**: Web interface shows real-time status via API endpoints

## External Dependencies

### Core Libraries
- **discord.py**: Discord bot API integration
- **playwright**: Browser automation for dynamic content scraping
- **flask**: Web framework for dashboard
- **apscheduler**: Task scheduling for periodic monitoring
- **sqlite3**: Built-in database (no external dependency)

### Browser Requirements
- Chromium browser (installed via Playwright)
- Headless browser capabilities

### Environment Variables
- `DISCORD_TOKEN`: Bot authentication token
- `DISCORD_CHANNEL_ID`: Target channel for notifications

## Deployment Strategy

### Local Development
- Single Python process running both bot and dashboard
- SQLite database file for local storage
- Environment variables for configuration

### Production Considerations
- The application is designed to run as a single long-running process
- Uses daemon threads to prevent blocking on dashboard startup
- Includes comprehensive logging to files and console
- Error handling prevents individual platform failures from crashing the system

### Scaling Options
- Database can be easily migrated from SQLite to PostgreSQL using Drizzle ORM
- Dashboard can be separated into independent service
- Multiple bot instances can share the same database for high availability

### Monitoring & Logging
- File-based logging (`bot.log`)
- Console output for real-time monitoring
- Web dashboard provides visual status monitoring
- Success rate tracking for reliability metrics