# Multi-Agent Observability System

Real-time monitoring and visualization for Claude Code agents through comprehensive hook event tracking.

## 🎯 Overview

A Docker-based observability system that captures all Claude Code interactions across multiple projects with zero friction. Once running, it provides a real-time dashboard at `localhost:5173` showing all Claude Code events.

## 🏗️ Architecture

```
Claude Agents → Hook Scripts → HTTP POST → Bun Server → SQLite → WebSocket → Vue Client
```

```
┌─────────────────────────────────────────────┐
│          Docker Container                   │
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Server (Bun)   │  │  Client (Vue)   │ │
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

## 🚀 Quick Start

### 1. Start the Docker Container
```bash
docker-compose up -d --build
```

### 2. Add Hooks to Your Project
Copy the `.claude/hooks/` folder to any project you want to observe.

### 3. View the Dashboard
Open `http://localhost:5173` in your browser.

That's it! Events will automatically flow from all projects to your dashboard.

## 📊 Current Implementation Status

### ✅ All Hooks Now Integrated!
- **pre_tool_use.py** - Captures tool usage before execution
- **user_prompt_submit.py** - Captures user prompts
- **post_tool_use.py** - Tool results logging
- **notification.py** - TTS notifications
- **stop.py** - Session completion
- **subagent_stop.py** - Subagent completion

All hooks now send events to the observability server using the one-line integration method.

## ⚙️ Configuration

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

## 🔌 Hook Integration

### One-Line Integration (New!)
Add observability to any hook with just one line:

```python
from hook_utils import enable_observability; enable_observability(__file__)
```

That's it! The hook will automatically send events to the server.

### Manual Integration
For hooks that need custom logic, add after the JSON write:

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

## 🧪 Testing

### Run All Tests
```bash
# E2E test with Puppeteer
node tests/test-e2e.js

# Test notification hook
python tests/test-notification-hook.py

# Test TTS directly
python tests/test-tts-directly.py
```

## 💡 Key Design Decisions

1. **Single Container** - Both server and client in one container for simplicity
2. **Fail Silently** - Hooks never interrupt Claude Code workflow
3. **Minimal Changes** - Original hook code preserved, only ~10 lines added
4. **Zero Config** - Hardcoded localhost URLs, no configuration needed
5. **Local Only** - No cloud dependencies, all data stays on your machine

## 🔧 Troubleshooting

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

## 🎨 Event Types & Visualization

| Event Type | Emoji | Purpose | Display |
|------------|-------|---------|----------|
| PreToolUse | 🔧 | Before tool execution | Tool name & details |
| PostToolUse | ✅ | After tool completion | Tool name & results |
| Notification | 🔔 | User interactions | Notification message |
| Stop | 🛑 | Response completion | Summary & chat transcript |
| SubagentStop | 👥 | Subagent finished | Subagent details |
| UserPromptSubmit | 💬 | User prompt submission | _"user message"_ (italic) |

## 📋 Project Structure

```
.
├── apps/
│   ├── server/          # Bun TypeScript server
│   └── client/          # Vue 3 dashboard
├── .claude/
│   └── hooks/           # Claude Code hooks
├── tests/               # Test files
├── docker-compose.yml   # Docker configuration
└── README.md           # This file
```

## 🚧 Future Improvements
- Add authentication for multi-user scenarios
- Consider cloud deployment for team sharing
- Add event filtering and search in the dashboard
- Implement event export functionality