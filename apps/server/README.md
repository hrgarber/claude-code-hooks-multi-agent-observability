# Multi-Agent Observability Server

Real-time event processing server for Claude Code hook events using Bun and SQLite.

## Overview

This server receives events from Claude Code hooks, stores them in SQLite, and broadcasts them to connected clients via WebSocket. It's designed to handle multiple concurrent agents with session tracking.

## Architecture

```
Claude Hooks → HTTP POST → Bun Server → SQLite → WebSocket → Vue Client
```

## Features

- **Real-time Processing**: Immediate event broadcasting via WebSocket
- **SQLite Storage**: Persistent storage with WAL mode for concurrent access
- **Auto-migrations**: Database schema updates automatically
- **Event Validation**: Type-safe event processing
- **WebSocket Broadcasting**: All connected clients receive updates instantly

## API Endpoints

### POST /events
Receives events from Claude Code hooks.

**Request Body:**
```json
{
  "source_app": "my-project",
  "session_id": "db8d7f8e-3cdc-490e-b38a-9b77d2891dc0",
  "hook_event_type": "PreToolUse",
  "payload": {
    "tool_name": "Bash",
    "tool_input": { "command": "ls -la" }
  }
}
```

### GET /events/recent
Retrieves recent events with optional filtering.

**Query Parameters:**
- `offset` - Pagination offset (default: 0)
- `limit` - Results per page (default: 100)
- `app` - Filter by source_app
- `session` - Filter by session_id
- `type` - Filter by hook_event_type

### GET /events/filter-options
Returns available filter values for the UI.

**Response:**
```json
{
  "apps": ["project-1", "project-2"],
  "sessions": ["session-id-1", "session-id-2"],
  "types": ["PreToolUse", "PostToolUse", "Notification"]
}
```

### WebSocket /stream
Real-time event streaming endpoint.

**Messages:**
- Broadcasts all new events as they arrive
- Clients automatically receive updates

## Database Schema

```sql
CREATE TABLE events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_app TEXT NOT NULL,
  session_id TEXT NOT NULL,
  hook_event_type TEXT NOT NULL,
  timestamp TEXT NOT NULL,
  payload TEXT NOT NULL
);
```

## Configuration

The server uses environment variables from the root `.env` file:
- `OBSERVABILITY_SERVER_PORT` - Server port (default: 4000)

## Development

```bash
# Install dependencies
bun install

# Run development server with hot reload
bun run dev

# Run production server
bun run start

# Type checking
bun run typecheck
```

## Docker Support

This server runs as part of the Docker container. See the root `docker-compose.yml` for configuration.

## Files

- `src/index.ts` - Main server with HTTP/WebSocket endpoints
- `src/db.ts` - SQLite database management & migrations
- `src/types.ts` - TypeScript interfaces
- `events.db` - SQLite database (created automatically, gitignored)
