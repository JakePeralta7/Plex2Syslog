#!/usr/bin/env python3

import json
import logging
import logging.handlers
import os
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuration
SYSLOG_HOST = os.getenv('SYSLOG_HOST', 'localhost')
SYSLOG_PORT = int(os.getenv('SYSLOG_PORT', '514'))
SYSLOG_FACILITY = os.getenv('SYSLOG_FACILITY', 'LOCAL0')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

# Setup application logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Setup syslog
syslog_logger = None
try:
    facility_map = {
        'LOCAL0': logging.handlers.SysLogHandler.LOG_LOCAL0,
        'LOCAL1': logging.handlers.SysLogHandler.LOG_LOCAL1,
        'LOCAL2': logging.handlers.SysLogHandler.LOG_LOCAL2,
        'LOCAL3': logging.handlers.SysLogHandler.LOG_LOCAL3,
        'LOCAL4': logging.handlers.SysLogHandler.LOG_LOCAL4,
        'LOCAL5': logging.handlers.SysLogHandler.LOG_LOCAL5,
        'LOCAL6': logging.handlers.SysLogHandler.LOG_LOCAL6,
        'LOCAL7': logging.handlers.SysLogHandler.LOG_LOCAL7,
        'USER': logging.handlers.SysLogHandler.LOG_USER,
        'MAIL': logging.handlers.SysLogHandler.LOG_MAIL,
        'DAEMON': logging.handlers.SysLogHandler.LOG_DAEMON,
        'AUTH': logging.handlers.SysLogHandler.LOG_AUTH,
        'SYSLOG': logging.handlers.SysLogHandler.LOG_SYSLOG,
        'LPR': logging.handlers.SysLogHandler.LOG_LPR,
        'NEWS': logging.handlers.SysLogHandler.LOG_NEWS,
        'UUCP': logging.handlers.SysLogHandler.LOG_UUCP,
        'CRON': logging.handlers.SysLogHandler.LOG_CRON,
        'AUTHPRIV': logging.handlers.SysLogHandler.LOG_AUTHPRIV,
    }
    
    facility = facility_map.get(SYSLOG_FACILITY, logging.handlers.SysLogHandler.LOG_LOCAL0)
    
    syslog_handler = logging.handlers.SysLogHandler(
        address=(SYSLOG_HOST, SYSLOG_PORT),
        facility=facility
    )
    syslog_handler.setFormatter(logging.Formatter('Plex2Syslog: %(message)s'))
    
    syslog_logger = logging.getLogger('plex_syslog')
    syslog_logger.addHandler(syslog_handler)
    syslog_logger.setLevel(logging.INFO)
    
    logger.info(f"Syslog configured: {SYSLOG_HOST}:{SYSLOG_PORT} (facility: {SYSLOG_FACILITY})")
except Exception as e:
    logger.error(f"Failed to configure syslog: {e}")

def format_plex_event(payload):
    """Format Plex webhook payload into a readable message"""
    try:
        event = payload.get('event', 'unknown')
        
        # Extract account info
        account = payload.get('Account', {}).get('title', 'unknown')
        
        # Extract server info
        server = payload.get('Server', {}).get('title', 'unknown')
        
        # Extract metadata
        metadata = payload.get('Metadata', {})
        title = metadata.get('title', 'unknown')
        media_type = metadata.get('type', 'unknown')
        
        # Extract player info
        player = payload.get('Player', {})
        player_title = player.get('title', 'unknown')
        
        message = (f"Event: {event} | "
                  f"User: {account} | "
                  f"Server: {server} | "
                  f"Media: {title} ({media_type}) | "
                  f"Player: {player_title}")
        
        return message
    except Exception as e:
        logger.error(f"Error formatting Plex event: {e}")
        return f"Plex Event (parsing error): {json.dumps(payload)}"

@app.route('/webhook', methods=['POST'])
def plex_webhook():
    """Handle Plex webhook requests"""
    try:
        # Get the payload
        if request.content_type == 'application/json':
            payload = request.get_json()
        else:
            # Plex sends multipart/form-data
            payload_str = request.form.get('payload', '{}')
            payload = json.loads(payload_str)
        
        logger.info(f"Received Plex webhook: {payload.get('event', 'unknown')}")
        
        # Format and send to syslog
        if syslog_logger:
            formatted_message = format_plex_event(payload)
            syslog_logger.info(formatted_message)
        else:
            logger.warning("Syslog not configured, event not forwarded")
        
        return jsonify({'status': 'success', 'message': 'Webhook processed'}), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'syslog_configured': syslog_logger is not None,
        'syslog_target': f"{SYSLOG_HOST}:{SYSLOG_PORT}"
    }), 200

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with basic info"""
    return jsonify({
        'service': 'Plex2Syslog',
        'version': '1.0.1',
        'webhook_endpoint': '/webhook',
        'health_endpoint': '/health'
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', '8080'))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"Starting Plex2Syslog on {host}:{port}")
    app.run(host=host, port=port, debug=False)
