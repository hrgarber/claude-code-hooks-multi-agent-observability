"""
Minimal utility functions for easier hook development.
Makes future hooks 3 lines instead of 30.
"""
import os
import requests
from datetime import datetime

# Configuration
SERVER = "http://localhost:4000/events"
APP = os.path.basename(os.getcwd())

def send(event_type, data, **kwargs):
    """Send event to observability server"""
    session = datetime.now().isoformat()  # Generate per-call
    try:
        requests.post(SERVER, json={
            "app": APP,
            "session_id": session,
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "metadata": kwargs
        }, timeout=1)
    except:
        pass  # Never interrupt Claude

def wrap(event_type):
    """Decorator to auto-send events"""
    def decorator(func):
        def wrapper(event):
            func(event)
            send(event_type, event)
        return wrapper
    return decorator