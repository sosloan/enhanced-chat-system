"""Utility functions for message handling"""

def validate_message(message):
    """Validate incoming message format"""
    if not isinstance(message, dict):
        return False, {'error': 'Message must be a dictionary'}
    
    if 'type' not in message:
        return False, {'error': 'Message type not specified'}
        
    return True, None