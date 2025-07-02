#!/usr/bin/env python3

import json
import logging
import logging.handlers
import os
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Configuration
SYSLOG_HOST = os.getenv('SYSLOG_HOST', 'localhost')
SYSLOG_PORT = int(os.getenv('SYSLOG_PORT', '514'))
SYSLOG_FACILITY = getattr(logging.handlers.SysLogHandler, 
                         f"LOG_{os.getenv('SYSLOG_FACILITY', 'LOCAL0')}")
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

# Setup logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

# Setup syslog handler
try:
    syslog_handler = logging.handlers.SysLogHandler(
        address=(SYSLOG_HOST, SYSLOG_PORT),
        facility=SYSLOG_FACILITY
    )
    syslog_formatter = logging.Formatter('Plex2Syslog: %(message)s')
    syslog_handler.setFormatter(syslog_formatter)
    
    syslog_logger = logging.getLogger('plex_syslog')
    syslog_logger.addHandler(syslog_handler)
    syslog_logger.setLevel(logging.INFO)
    
    logger.info(f"Syslog handler configured for {SYSLOG_HOST}:{SYSLOG_PORT}")
except Exception as e:
    logger.error(f"Failed to setup syslog handler: {e}")
    syslog_logger = None

def format_plex_event(payload):
    """Format Plex webhook payload for syslog"""
    try:
        event = payload.get('event', 'unknown')
        account = payload.get('Account', {}).get('title', 'unknown')
        server = payload.get('Server', {}).get('title', 'unknown')
        
        metadata = payload.get('Metadata', {})
        title = metadata.get('title', 'unknown')
        media_type = metadata.get('type', 'unknown')
        
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
