<<<<<<< HEAD
# Discord Bot with Social Media Scraper + Live Status Dashboard

A Python-based Discord bot that automatically monitors social media platforms for new posts and provides real-time status updates through a web dashboard.

## Features

- **Automatic Monitoring**: Scrapes social media platforms every 5 minutes
- **Discord Notifications**: Sends alerts to Discord channel when new posts are detected
- **Live Dashboard**: Real-time web interface showing monitoring status
- **Multi-Platform Support**: LinkedIn, TikTok, Facebook, and X (Twitter)
- **Error Handling**: Comprehensive error tracking and display
- **Persistent Storage**: SQLite database for tracking posts and status

## Requirements

- Python 3.8+
- Discord Bot Token
- Discord Channel ID for notifications
- Required Python packages (automatically installed):
  - discord.py
  - playwright
  - flask
  - apscheduler
  - sqlite3 (built-in)

## Setup Instructions

### 1. Environment Variables

Set the following environment variables or update `config.py`:

```bash
export DISCORD_TOKEN="your_discord_bot_token"
export DISCORD_CHANNEL_ID="your_discord_channel_id"
=======
# scrapping
>>>>>>> ff02691473c063962a8b4716292969d86b63268f
