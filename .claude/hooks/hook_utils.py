"""
Minimal utility functions for easier hook development.
Makes future hooks 3 lines instead of 30.
"""
import os
import sys
import json
import requests
import threading
from io import StringIO
from datetime import datetime

# Configuration
SERVER = "http://localhost:4000/events"
APP = os.path.basename(os.getcwd())

def enable_observability(hook_file):
    """
    Enable observability for a hook with just one line:
    from hook_utils import enable_observability; enable_observability(__file__)
    
    This function:
    1. Captures stdin data
    2. Extracts session_id
    3. Sends event to server in background
    4. Restores stdin for normal hook operation
    """
    hook_name = os.path.basename(hook_file).replace('.py', '')
    
    # Capture stdin
    original_stdin = sys.stdin
    stdin_data = original_stdin.read()
    
    # Parse to get session_id and send to server
    try:
        input_data = json.loads(stdin_data)
        session_id = input_data.get('session_id', 'unknown')
        
        # Send to server in background thread
        def send_event():
            try:
                requests.post(SERVER, json={
                    "source_app": APP,
                    "session_id": session_id,
                    "hook_event_type": hook_name,
                    "payload": input_data
                }, timeout=1)
            except:
                pass  # Never interrupt Claude
        
        # Start background thread
        thread = threading.Thread(target=send_event)
        thread.daemon = True  # Don't wait for thread to finish
        thread.start()
    except:
        pass  # Fail silently
    
    # Restore stdin for the hook to read
    sys.stdin = StringIO(stdin_data)

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