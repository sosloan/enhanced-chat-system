"""Base agent implementation"""
from pykka import ThreadingActor
from .utils.message_handler import validate_message

class BaseAgent(ThreadingActor):
    """Base agent class with common functionality"""
    
    def __init__(self):
        super().__init__()
        self.state = {}
    
    def on_receive(self, message):
        """Handle incoming messages"""
        is_valid, error = validate_message(message)
        if not is_valid:
            return error
            
        handler = getattr(self, f'handle_{message["type"]}', None)
        if handler:
            return handler(message)
        return {'error': f'Unknown message type: {message["type"]}'}