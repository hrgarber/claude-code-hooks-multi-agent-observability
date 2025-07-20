# Harrison's Plan: Centralized Claude Observability Service

## Vision
Transform the current local observability setup into a centralized, "Docker-style" service that works across all projects without per-project configuration.

## Current Architecture Analysis

### Components That Could Be Centralized

#### 1. **Event Collection & Storage Service** (High Priority)
Currently, the server at `apps/server/` handles:
- **Event ingestion** (POST /events endpoint)
- **SQLite database** with event storage
- **WebSocket broadcasting** for real-time updates
- **Filter options API** for dynamic filtering

This could be centralized as a standalone microservice that multiple projects could send events to, with features like:
- Multi-tenant support (project isolation)
- Scalable event storage (potentially moving from SQLite to PostgreSQL/TimescaleDB)
- Event routing and filtering rules
- Rate limiting and authentication
- Event retention policies

#### 2. **Theme Management Service** (Medium Priority)
The theme system (`/api/themes/*` endpoints) could be extracted as a shared service:
- Theme CRUD operations
- Theme sharing and permissions
- Rating system
- Import/export functionality
- Theme statistics

This would allow themes to be shared across multiple visualization dashboards or projects.

#### 3. **Real-time Communication Layer** (High Priority)
The WebSocket infrastructure could be centralized:
- WebSocket connection management
- Event broadcasting with topic/channel support
- Connection pooling
- Automatic reconnection logic
- Message queuing for offline clients

#### 4. **Hook Script Library** (Medium Priority)
The Python hook scripts in `.claude/hooks/` could be packaged as:
- A pip-installable package
- Standardized event formatting
- Built-in server URL configuration
- Common utilities (summarization, validation)
- Easy integration for new projects

#### 5. **Configuration Management** (Low Priority)
Currently hardcoded values like `http://localhost:4000` could be centralized:
- Environment-based configuration
- Service discovery
- API endpoint registry
- Feature flags

#### 6. **Event Processing Pipeline** (Future Enhancement)
A central service for:
- Event aggregation and analytics
- Real-time alerting
- Event transformation and enrichment
- Integration with external monitoring tools

### Recommended Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Project A     │     │   Project B     │     │   Project C     │
│  (.claude/hooks)│     │  (.claude/hooks)│     │  (.claude/hooks)│
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────────────────┴───────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Central Event Service │
                    │  - Event Ingestion     │
                    │  - Storage (Multi-DB)  │
                    │  - WebSocket Hub       │
                    │  - Theme Management    │
                    │  - API Gateway         │
                    └────────────┬───────────┘
                                 │
                    ┌────────────┴───────────┐
                    ▼                        ▼
           ┌─────────────────┐      ┌─────────────────┐
           │  Dashboard A     │      │  Dashboard B     │
           │  (Vue Client)    │      │  (React Client)  │
           └─────────────────┘      └─────────────────┘
```

### Implementation Priority

1. **Phase 1**: Extract the event collection service with multi-project support
2. **Phase 2**: Create a shared hook script package
3. **Phase 3**: Centralize theme management
4. **Phase 4**: Add authentication and project isolation
5. **Phase 5**: Scale storage and add analytics

This centralization would enable:
- Multiple projects to share the same observability infrastructure
- Centralized monitoring across all Claude Code agents
- Shared themes and configurations
- Better resource utilization
- Easier maintenance and updates

## User Experience Design

### Current User Interaction Model

#### 1. **Dashboard Access**
The current system uses a local setup with:
- **Server**: Runs on `http://localhost:4000` (Bun TypeScript server)
- **Dashboard UI**: Accessible at `http://localhost:5173` (Vue 3 client via Vite)
- **WebSocket**: Real-time updates via `ws://localhost:4000/stream`

Users access the dashboard by:
1. Running `./scripts/start-system.sh` to launch both server and client
2. Opening a browser to `http://localhost:5173`
3. Seeing real-time events stream as Claude Code performs actions

#### 2. **Typical User Workflow**

The current workflow follows this pattern:

```
1. User starts observability system (local)
   └─> Server starts on port 4000
   └─> Client starts on port 5173

2. User opens dashboard in browser
   └─> Connects to WebSocket for live updates
   └─> Shows connection status indicator

3. User runs Claude Code commands in their project
   └─> Hooks trigger automatically
   └─> Events POST to http://localhost:4000/events
   └─> Server broadcasts via WebSocket
   └─> Dashboard updates in real-time

4. User monitors and filters events
   └─> Filter by app, session, event type
   └─> View chat transcripts
   └─> See live pulse chart
```

#### 3. **Configuration Requirements**

Users currently configure:
- **Source App Name**: In `.claude/settings.json` for each project
- **Event Types**: Which hooks to enable (PreToolUse, PostToolUse, etc.)
- **Server URL**: Hardcoded to `http://localhost:4000/events` in hook scripts
- **Max Events Display**: Via `VITE_MAX_EVENTS_TO_DISPLAY` env var

### Ideal "It Just Works" Experience for Centralized Service

#### 1. **Zero-Configuration Access**
```
# Ideal user experience:
1. User installs hooks: cp -R .claude /their/project/
2. User opens browser to: https://observability.claude.tools
3. Events automatically appear - no local server needed!
```

#### 2. **Service URLs & Access Points**

For a centralized service, users would interact via:

**Production URLs:**
- Dashboard: `https://observability.claude.tools` or `https://claude-observe.io`
- API Endpoint: `https://api.claude-observe.io/events`
- WebSocket: `wss://api.claude-observe.io/stream`

**User-Friendly Features:**
- Auto-generated project IDs or API keys for isolation
- Shareable dashboard URLs: `https://claude-observe.io/project/abc123`
- Team workspaces: `https://claude-observe.io/team/myteam`

#### 3. **Simplified Configuration**

**Option A: Environment Variable Configuration**
```bash
# In user's project .env
CLAUDE_OBSERVE_API_KEY=proj_abc123xyz
CLAUDE_OBSERVE_PROJECT=my-awesome-app
```

**Option B: Config File**
```json
// .claude/observe.config.json
{
  "endpoint": "https://api.claude-observe.io",
  "projectId": "auto", // or specific ID
  "teamId": "optional-team-id"
}
```

#### 4. **Authentication & Access Control**

**Simple Authentication Flow:**
1. User signs up at `https://claude-observe.io`
2. Gets API key or project token
3. Adds to their `.env` or hook configuration
4. Events automatically route to their dashboard

**Access Patterns:**
- Personal dashboards: Requires login
- Public read-only links: For sharing with team
- API key for sending events: Separate from viewing

#### 5. **Enhanced User Experience**

**Smart Defaults:**
- Auto-detect project name from git repo
- Default to user's namespace if no project specified
- Automatic session grouping by timestamp

**Progressive Enhancement:**
```
Level 1: Basic - Just works with defaults
├─> Copy .claude folder
└─> Events appear at personal dashboard

Level 2: Configured - Custom project settings  
├─> Set project name and tags
├─> Custom filtering and alerts
└─> Team sharing

Level 3: Advanced - Full integration
├─> CI/CD pipeline integration
├─> Slack/Discord notifications
├─> Custom webhooks
└─> Data export APIs
```

#### 6. **Mobile-Friendly Access**

Since the current UI is already responsive, the centralized service would offer:
- Mobile web app at `m.claude-observe.io`
- Push notifications for critical events
- Quick filters for mobile viewing

### Migration Path from Local to Centralized

For users transitioning from local to centralized:

1. **Backwards Compatible Mode**
   - Keep `localhost:4000` as fallback
   - Add `CLAUDE_OBSERVE_MODE=cloud` to switch

2. **Hybrid Operation**
   - Local server forwards to cloud
   - Useful for corporate firewalls

3. **Export/Import**
   - Export local SQLite data
   - Import to cloud service

### Key Benefits of Centralization

From the user's perspective:
- **No Setup**: Just browse to URL, no local servers
- **Persistent History**: Events saved across sessions
- **Team Collaboration**: Share dashboards with colleagues  
- **Multi-Project View**: See all projects in one place
- **Access Anywhere**: Monitor from phone, tablet, any device
- **No Maintenance**: No local database or server management

This centralized approach would transform the user experience from "run local servers and monitor locally" to "just open a web page and see everything" - the true "it just works" experience.

## User Connection Comparison

### Current (Local) Setup
```bash
# Run servers locally
./scripts/start-system.sh
# Open browser to http://localhost:5173
```

### Centralized Service Experience

**1. Zero-Config Access**
```bash
# Just open browser to:
https://claude-observe.io

# Your events automatically appear!
```

**2. Simple Hook Configuration**
```python
# .claude/hooks/hook.py
OBSERVE_ENDPOINT = os.getenv('CLAUDE_OBSERVE_URL', 
                            'https://api.claude-observe.io/events')
```

**3. Authentication Options**

**Option A: API Key in Environment**
```bash
# .env file
CLAUDE_OBSERVE_KEY=proj_abc123xyz
```

**Option B: Personal Dashboard**
- Login at `https://claude-observe.io`
- Events auto-route to your workspace
- Share read-only links with team

### User Journey Comparison

#### Local Journey (Current)
1. Clone repo
2. Install dependencies  
3. Start server (port 4000)
4. Start client (port 5173)
5. Configure hooks to point to localhost
6. Open browser, see events

#### Cloud Journey (Proposed)
1. Sign up at claude-observe.io (once)
2. Copy hooks to project
3. Open browser, see events

### Access Patterns

**Personal Dashboard**
```
https://claude-observe.io/dashboard
└── Shows all your projects
└── Real-time WebSocket updates
└── Persistent event history
```

**Project-Specific View**
```
https://claude-observe.io/p/my-project
└── Filtered to one project
└── Shareable with team
└── Custom domain option
```

**Mobile Access**
```
https://m.claude-observe.io
└── Optimized for phones
└── Push notifications
└── Quick filters
```

### Configuration Simplicity

**Minimal Config Required:**
```json
// .claude/settings.json
{
  "app_name": "my-app",
  "observe": {
    "endpoint": "auto"  // Uses cloud by default
  }
}
```

**Advanced Features Available:**
- Custom webhooks
- Slack/Discord alerts
- Data export APIs
- Team workspaces

The key insight: Just like Docker containers expose services on ports that "just work", your centralized service would expose a web dashboard that "just works" - no local setup, no port management, just a URL you can access from anywhere.

## Architecture Visualizations

### Current Architecture vs Centralized Service

#### Current Local Setup
```
┌─────────────────────────────────────────────────────────────┐
│                     USER'S MACHINE                          │
│                                                             │
│  ┌──────────────┐        ┌──────────────────────┐         │
│  │ Project A    │        │  LOCAL SERVERS       │         │
│  │ .claude/     │───────▶│  - Server :4000      │         │
│  │  └─hooks/    │        │  - Dashboard :5173   │         │
│  └──────────────┘        └──────────┬───────────┘         │
│                                      │                      │
│  ┌──────────────┐                   ▼                      │
│  │ Project B    │        ┌──────────────────────┐         │
│  │ .claude/     │───────▶│  Browser Tab        │         │
│  │  └─hooks/    │        │  localhost:5173     │         │
│  └──────────────┘        └──────────────────────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Centralized Cloud Service
```
┌─────────────────────────────────────────────────────────────┐
│                        CLOUD                                │
│  ┌─────────────────────────────────────────────────────┐  │
│  │           claude-observe.io                          │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │  │
│  │  │ Auth Service│  │Event Service│  │  Dashboard │  │  │
│  │  │   (Auth0)   │  │  (API/WS)   │  │   (Web)    │  │  │
│  │  └──────┬──────┘  └──────┬──────┘  └─────┬──────┘  │  │
│  │         │                 │                │         │  │
│  │         └─────────────────┴────────────────┘         │  │
│  │                           │                          │  │
│  │                    ┌──────▼──────┐                   │  │
│  │                    │  Database   │                   │  │
│  │                    │ (Postgres)  │                   │  │
│  │                    └─────────────┘                   │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ HTTPS/WSS
     ┌────────────────────────┴────────────────────────┐
     │                                                  │
┌────▼─────┐  ┌──────────┐  ┌──────────┐  ┌──────────▼────┐
│Project A │  │Project B │  │Project C │  │   Browser     │
│.claude/  │  │.claude/  │  │.claude/  │  │claude-observe │
│ hooks    │  │ hooks    │  │ hooks    │  │     .io       │
└──────────┘  └──────────┘  └──────────┘  └───────────────┘
```

#### User Connection Flow
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│1. User Runs  │     │2. Hook Sends │     │3. User Opens │
│   Claude     │────▶│   Event to   │────▶│   Browser    │
│   Command    │     │   Cloud API  │     │   Dashboard  │
└──────────────┘     └──────────────┘     └──────────────┘
       │                     │                     │
       ▼                     ▼                     ▼
   ┌────────┐         ┌─────────────┐      ┌────────────┐
   │.claude/│         │POST https://│      │ https://   │
   │ hooks  │         │api.claude-  │      │ claude-    │
   │        │         │observe.io/  │      │ observe.io │
   └────────┘         │events       │      └────────────┘
                      └─────────────┘              │
                             │                     ▼
                             │              ┌────────────┐
                             └─────────────▶│ Real-time  │
                                           │  Updates   │
                                           │   (WSS)    │
                                           └────────────┘
```

#### Configuration Comparison
```
LOCAL SETUP                    CENTRALIZED SERVICE
─────────────────────────────  ─────────────────────────────
                              
1. Clone repo                  1. Sign up once
2. npm install                 2. Get API key  
3. ./start-system.sh          3. Add to .env
4. localhost:5173             4. claude-observe.io
                              
┌─────────────┐               ┌─────────────┐
│   COMPLEX   │               │    SIMPLE   │
│  MULTI-STEP │               │   ONE-TIME  │
└─────────────┘               └─────────────┘
```

## Implementation Todo List

1. **Design centralized event service API with multi-tenant support** (High Priority)
2. **Create standalone event collection service from existing server code** (High Priority)
3. **Package hook scripts as pip-installable library** (Medium Priority)
4. **Add service discovery and configuration management** (Medium Priority)
5. **Create Docker Compose setup for easy deployment** (Low Priority)
6. **Design user authentication and project isolation** (High Priority)
7. **Create cloud-hosted dashboard with custom domains** (Medium Priority)

## Implementation Approach Options

### Option 1: Microservice with Docker Compose (Recommended)
```yaml
# docker-compose.yml
services:
  event-service:
    build: ./event-service
    ports:
      - "4000:4000"
    environment:
      - DATABASE_URL=postgresql://...
      
  dashboard:
    build: ./dashboard
    ports:
      - "8080:8080"
```

### Option 2: SystemD Service (Linux)
Create a system service that runs on boot and all projects connect to it.

### Option 3: Shared Python Package + Central API
```bash
pip install claude-observability-client
```

Projects would just need:
```python
from claude_observability import track_event
track_event("tool_use", {...})
```

## Summary

This plan transforms the current local observability system into a centralized service that provides:
- **No Setup**: Just browse to URL, no local servers
- **Persistent History**: Events saved across sessions
- **Team Collaboration**: Share dashboards with colleagues
- **Multi-Project View**: See all projects in one place
- **Access Anywhere**: Monitor from phone, tablet, any device
- **No Maintenance**: No local database or server management

The key is creating a service that "just works" like opening a web app, while maintaining all the powerful observability features of the current system.