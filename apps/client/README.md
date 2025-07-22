# Multi-Agent Observability Dashboard

Real-time visualization dashboard for Claude Code agent events built with Vue 3.

## Overview

This client provides a live dashboard for monitoring Claude Code agent activities across multiple projects. It connects to the observability server via WebSocket for real-time updates and displays events with rich visualizations.

## Features

### Visual Design
- **Dual-color system**: App colors (left border) + Session colors (second border)
- **Dark/light theme support** with smooth transitions
- **Responsive layout** optimized for monitoring
- **Event type emojis** for quick visual identification

### Core Functionality
- **Real-time Updates**: WebSocket connection for instant event streaming
- **Multi-criteria Filtering**: Filter by app, session, and event type
- **Live Activity Pulse**: Real-time chart showing event frequency
- **Chat Transcript Viewer**: View complete conversation history
- **Auto-scroll**: Automatic scrolling with manual override
- **Event Limiting**: Configurable maximum events display

### Live Pulse Chart
- Canvas-based real-time visualization
- Session-specific colors for each bar
- Event type emojis displayed on bars
- Time range selection (1m, 3m, 5m)
- Smooth animations and glow effects

## Event Types & Display

| Event Type | Emoji | Display Format |
|------------|-------|----------------|
| PreToolUse | 🔧 | Tool name & input details |
| PostToolUse | ✅ | Tool name & execution results |
| Notification | 🔔 | Notification message |
| Stop | 🛑 | Summary & chat transcript link |
| SubagentStop | 👥 | Subagent completion details |
| PreCompact | 📦 | Context compaction info |
| UserPromptSubmit | 💬 | _"user prompt"_ (italicized) |

## Configuration

Create `.env` file in this directory:

```env
# Maximum events to display (older events are removed)
VITE_MAX_EVENTS_TO_DISPLAY=100
```

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── App.vue                    # Main app with theme & WebSocket management
├── components/
│   ├── EventTimeline.vue      # Event list with auto-scroll
│   ├── EventRow.vue           # Individual event display
│   ├── FilterPanel.vue        # Multi-select filters
│   ├── ChatTranscriptModal.vue # Chat history viewer
│   ├── StickScrollButton.vue  # Scroll control
│   └── LivePulseChart.vue     # Real-time activity chart
├── composables/
│   ├── useWebSocket.ts        # WebSocket connection logic
│   ├── useEventColors.ts      # Color assignment system
│   ├── useChartData.ts        # Chart data aggregation
│   └── useEventEmojis.ts      # Event type emoji mapping
├── utils/
│   └── chartRenderer.ts       # Canvas chart rendering
└── types.ts                   # TypeScript interfaces
```

## Docker Support

This client runs as part of the Docker container. The dashboard is available at `http://localhost:5173` when running via Docker.

## Architecture

The client connects to the observability server at `localhost:4000` and:
1. Establishes WebSocket connection for real-time updates
2. Fetches recent events and filter options on load
3. Updates the UI immediately when new events arrive
4. Maintains color consistency across sessions and apps

## Technologies

- **Vue 3** with Composition API
- **TypeScript** for type safety
- **Vite** for fast development
- **Tailwind CSS** for styling
- **Canvas API** for chart rendering