#!/usr/bin/env python3
"""Test TTS scripts directly to diagnose audio issues"""

import subprocess
import os
from pathlib import Path

def test_tts_directly():
    """Test each TTS script directly with a simple message"""
    
    tts_dir = Path(__file__).parent.parent / '.claude' / 'hooks' / 'utils' / 'tts'
    test_message = "Testing TTS audio. Can you hear me?"
    
    print(f"Testing TTS scripts in: {tts_dir}")
    print(f"Test message: '{test_message}'")
    print(f"OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
    print(f"ELEVENLABS_API_KEY: {'Set' if os.getenv('ELEVENLABS_API_KEY') else 'Not set'}")
    
    # Test ElevenLabs TTS (now that it's available)
    elevenlabs_script = tts_dir / 'elevenlabs_tts.py'
    if elevenlabs_script.exists() and os.getenv('ELEVENLABS_API_KEY'):
        print("\n=== Testing ElevenLabs TTS directly ===")
        print(f"Script: {elevenlabs_script}")
        
        try:
            # Run without capturing output so we can see any errors
            result = subprocess.run(
                ['uv', 'run', str(elevenlabs_script), test_message],
                text=True
            )
            print(f"Exit code: {result.returncode}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Also test OpenAI TTS if available
    openai_script = tts_dir / 'openai_tts.py'
    if openai_script.exists() and os.getenv('OPENAI_API_KEY'):
        print("\n=== Testing OpenAI TTS directly ===")
        print(f"Script: {openai_script}")
        
        try:
            result = subprocess.run(
                ['uv', 'run', str(openai_script), test_message],
                text=True
            )
            print(f"Exit code: {result.returncode}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Also test pyttsx3 as fallback
    pyttsx3_script = tts_dir / 'pyttsx3_tts.py'
    if pyttsx3_script.exists():
        print("\n=== Testing pyttsx3 TTS directly ===")
        print(f"Script: {pyttsx3_script}")
        
        try:
            result = subprocess.run(
                ['uv', 'run', str(pyttsx3_script), test_message],
                text=True
            )
            print(f"Exit code: {result.returncode}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_tts_directly()