"""
Flask web dashboard for monitoring social media scraping status
"""
from flask import Flask, render_template, jsonify
import logging
from database import get_all_monitoring_status
from config import SOCIAL_MEDIA_URLS

logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API endpoint to get current monitoring status"""
    try:
        status_list = get_all_monitoring_status()
        
        # Ensure all configured platforms are represented
        platform_status = {}
        for platform, url in SOCIAL_MEDIA_URLS.items():
            platform_status[platform] = {
                'platform': platform,
                'url': url,
                'last_post': 'Not checked yet',
                'last_checked': 'Never',
                'has_new_post': False,
                'error_message': None,
                'check_count': 0,
                'success_count': 0,
                'success_rate': 0
            }
        
        # Update with actual status data
        for status in status_list:
            platform = status['platform']
            success_rate = (status['success_count'] / max(status['check_count'], 1)) * 100
            
            platform_status[platform] = {
                'platform': platform,
                'url': status['url'],
                'last_post': status['last_post'],
                'last_checked': status['last_checked'],
                'has_new_post': status['has_new_post'],
                'error_message': status['error_message'],
                'check_count': status['check_count'],
                'success_count': status['success_count'],
                'success_rate': round(success_rate, 1)
            }
        
        return jsonify({
            'status': 'success',
            'data': list(platform_status.values())
        })
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Social Media Monitor Dashboard'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
