# Dockerized Claude Code Observability System

## Overview
A Docker-based observability system that captures all Claude Code interactions across multiple projects with zero friction. Once running, it provides a real-time dashboard at `localhost:5173` showing all Claude Code events.

## Architecture
```
┌─────────────────────────────────────────────┐
│          Docker Container                   │
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Server (Bun)   │  │  Client (Vite)  │ │
│  │  Port: 4000     │  │  Port: 5173     │ │
│  │                 │◀─┤  WebSocket      │ │
│  └────────┬────────┘  └─────────────────┘ │
│           │                                 │
│           ▼                                 │
│  ┌─────────────────┐                      │
│  │  SQLite DB      │                      │
│  └─────────────────┘                      │
└─────────────────────────────────────────────┘
           ▲
           │ HTTP POST to :4000/events
┌──────────┴──────────┐
│  Project Hooks      │
│  .claude/hooks/*.py │
└─────────────────────┘
```

## Quick Start

### 1. Start the Docker Container
```bash
docker-compose up -d --build
```

### 2. Add Hooks to Your Project
Copy the `.claude/hooks/` folder to any project you want to observe.

### 3. View the Dashboard
Open `http://localhost:5173` in your browser.

That's it! Events will automatically flow from all projects to your dashboard.

## Current Hook Status

### ✅ Working (Sending Events)
- **pre_tool_use.py** - Captures tool usage before execution
- **user_prompt_submit.py** - Captures user prompts

### 🚧 Local Only (Not Yet Integrated)
- **post_tool_use.py** - Tool results logging
- **notification.py** - TTS notifications
- **stop.py** - Session completion
- **subagent_stop.py** - Subagent completion

## Configuration

### Environment Variables (.env)
```env
# API Keys for TTS/LLM features
ELEVENLABS_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
ENGINEER_NAME=Your_Name

# Observability Settings (optional)
OBSERVABILITY_SERVER_PORT=4000
OBSERVABILITY_CLIENT_PORT=5173
```

### TTS Priority Order
1. ElevenLabs (if API key present)
2. OpenAI (if API key present)
3. pyttsx3 (fallback, no API needed)

## Extending the System

### Adding Events to Existing Hooks
For hooks that only log locally, add this after the JSON write:

```python
# Send to observability server
try:
    requests.post("http://localhost:4000/events", json={
        "source_app": os.path.basename(os.getcwd()),
        "session_id": session_id,
        "hook_event_type": "hook_name_here",
        "payload": input_data
    }, timeout=1)
except:
    pass  # Never interrupt Claude
```

### Using Hook Utils (Future Hooks)
The `hook_utils.py` needs fixes for field names but will eventually enable:
```python
from hook_utils import send_event
send_event(input_data, 'my_event_type')
```

## Testing

### Run All Tests
```bash
# E2E test with Puppeteer
node tests/test-e2e.js

# Test notification hook
python tests/test-notification-hook.py

# Test TTS directly
python tests/test-tts-directly.py
```

## Key Design Decisions

1. **Single Container** - Both server and client in one container for simplicity
2. **Fail Silently** - Hooks never interrupt Claude Code workflow
3. **Minimal Changes** - Original hook code preserved, only ~10 lines added
4. **Zero Config** - Hardcoded localhost URLs, no configuration needed
5. **Local Only** - No cloud dependencies, all data stays on your machine

## Troubleshooting

### Dashboard Not Loading
- Check Docker is running: `docker ps`
- Verify health: `curl http://localhost:4000/health`
- Check logs: `docker-compose logs -f`

### Events Not Appearing
- Ensure hooks have `requests` dependency
- Check session_id extraction in hooks
- Verify correct field names (source_app, hook_event_type, payload)

### TTS Issues
- Check API keys in .env file
- Test TTS directly: `python tests/test-tts-directly.py`
- Notification hook requires `--notify` flag

## Future Improvements
- Fix hook_utils.py field names and session handling
- Integrate remaining hooks (post_tool_use, stop, etc.)
- Add authentication for multi-user scenarios
- Consider cloud deployment for team sharing