"""
Database operations for storing social media post data
"""
import sqlite3
import json
import logging
from datetime import datetime
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

def init_database():
    """Initialize the SQLite database with required tables"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Create posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                url TEXT NOT NULL,
                post_id TEXT,
                post_content TEXT,
                post_url TEXT,
                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_new BOOLEAN DEFAULT 0,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create monitoring status table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitoring_status (
                platform TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                last_post_content TEXT,
                last_post_id TEXT,
                last_post_url TEXT,
                last_checked TIMESTAMP,
                has_new_post BOOLEAN DEFAULT 0,
                error_message TEXT,
                check_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def get_last_post(platform):
    """Get the last known post for a platform"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT last_post_id, last_post_content, last_post_url 
            FROM monitoring_status 
            WHERE platform = ?
        ''', (platform,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'post_id': result[0],
                'content': result[1],
                'url': result[2]
            }
        return None
        
    except Exception as e:
        logger.error(f"Failed to get last post for {platform}: {e}")
        return None

def update_post_status(platform, url, post_data=None, error_message=None, is_new=False):
    """Update the monitoring status for a platform"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Insert or update monitoring status
        cursor.execute('''
            INSERT OR REPLACE INTO monitoring_status 
            (platform, url, last_post_content, last_post_id, last_post_url, 
             last_checked, has_new_post, error_message, check_count, success_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 
                    COALESCE((SELECT check_count FROM monitoring_status WHERE platform = ?), 0) + 1,
                    COALESCE((SELECT success_count FROM monitoring_status WHERE platform = ?), 0) + ?)
        ''', (
            platform, url,
            post_data.get('content', '') if post_data else '',
            post_data.get('post_id', '') if post_data else '',
            post_data.get('url', '') if post_data else '',
            datetime.now(),
            is_new,
            error_message,
            platform, platform,
            1 if error_message is None else 0
        ))
        
        # If there's a new post, also log it in the posts table
        if is_new and post_data:
            cursor.execute('''
                INSERT INTO posts (platform, url, post_id, post_content, post_url, is_new)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                platform, url,
                post_data.get('post_id', ''),
                post_data.get('content', ''),
                post_data.get('url', ''),
                True
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"Updated status for {platform}: new_post={is_new}, error={error_message is not None}")
        
    except Exception as e:
        logger.error(f"Failed to update post status for {platform}: {e}")

def get_all_monitoring_status():
    """Get current monitoring status for all platforms"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT platform, url, last_post_content, last_checked, 
                   has_new_post, error_message, check_count, success_count
            FROM monitoring_status
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        status_list = []
        for row in results:
            status_list.append({
                'platform': row[0],
                'url': row[1],
                'last_post': row[2][:100] + '...' if row[2] and len(row[2]) > 100 else row[2] or 'No posts found',
                'last_checked': row[3],
                'has_new_post': bool(row[4]),
                'error_message': row[5],
                'check_count': row[6] or 0,
                'success_count': row[7] or 0
            })
        
        return status_list
        
    except Exception as e:
        logger.error(f"Failed to get monitoring status: {e}")
        return []

def reset_new_post_flags():
    """Reset all new post flags to False"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE monitoring_status SET has_new_post = 0')
        
        conn.commit()
        conn.close()
        logger.info("Reset all new post flags")
        
    except Exception as e:
        logger.error(f"Failed to reset new post flags: {e}")
