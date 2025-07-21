#!/usr/bin/env python3
"""Test notification hook with TTS functionality"""

import json
import subprocess
import os
import sys
from pathlib import Path

def test_notification_hook():
    """Test the notification hook with and without TTS"""
    
    hook_path = Path(__file__).parent / '.claude' / 'hooks' / 'notification.py'
    
    # Test data that should trigger notification
    test_data = {
        "session_id": "test-session-123",
        "message": "Please provide more details about the implementation",
        "timestamp": "2024-01-20T12:00:00Z"
    }
    
    print("Testing notification hook...")
    print(f"Hook path: {hook_path}")
    print(f"Test data: {json.dumps(test_data, indent=2)}")
    
    # Test 1: Without --notify flag (should NOT trigger TTS)
    print("\n=== Test 1: Without --notify flag (no TTS expected) ===")
    try:
        result = subprocess.run(
            ['uv', 'run', str(hook_path)],
            input=json.dumps(test_data),
            text=True,
            capture_output=True
        )
        print(f"Exit code: {result.returncode}")
        if result.stdout:
            print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: With --notify flag (should trigger TTS)
    print("\n=== Test 2: With --notify flag (TTS expected) ===")
    try:
        result = subprocess.run(
            ['uv', 'run', str(hook_path), '--notify'],
            input=json.dumps(test_data),
            text=True,
            capture_output=True
        )
        print(f"Exit code: {result.returncode}")
        if result.stdout:
            print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Check if TTS scripts exist
    print("\n=== Test 3: Checking TTS scripts ===")
    tts_dir = hook_path.parent / 'utils' / 'tts'
    print(f"TTS directory: {tts_dir}")
    if tts_dir.exists():
        tts_scripts = list(tts_dir.glob('*.py'))
        print(f"Found {len(tts_scripts)} TTS scripts:")
        for script in tts_scripts:
            print(f"  - {script.name}")
    else:
        print("TTS directory does not exist!")
    
    # Test 4: Check environment variables
    print("\n=== Test 4: Checking environment for TTS ===")
    print(f"ELEVENLABS_API_KEY: {'Set' if os.getenv('ELEVENLABS_API_KEY') else 'Not set'}")
    print(f"OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
    print(f"ENGINEER_NAME: {os.getenv('ENGINEER_NAME', 'Not set')}")
    
    # Test 5: Test with Claude's actual "waiting" message (should NOT trigger TTS even with flag)
    print("\n=== Test 5: With Claude's waiting message (no TTS expected) ===")
    waiting_data = {
        "session_id": "test-session-123",
        "message": "Claude is waiting for your input",
        "timestamp": "2024-01-20T12:00:00Z"
    }
    try:
        result = subprocess.run(
            ['uv', 'run', str(hook_path), '--notify'],
            input=json.dumps(waiting_data),
            text=True,
            capture_output=True
        )
        print(f"Exit code: {result.returncode}")
        print("This should NOT trigger TTS (filtered message)")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_notification_hook()