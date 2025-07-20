# Complete Encapsulated Plan: Claude Code Observability as a Service

## 🎯 End Goal
Transform your working observability system from a "development project" into an always-on background service that captures all Claude Code interactions across all projects with zero friction.

## 🏗️ Architecture Overview
- **Docker Service**: Runs the observability infrastructure (server + dashboard) as an always-on container
- **Project Hooks**: Each project only needs `.claude/hooks/` folder that sends events to localhost:4000
- **Complete Separation**: Projects don't need Docker or any knowledge of the observability system

## 📋 The Plan

### **Phase 1: Dockerization** (Making it a Service)

**What:** Create a Docker container that runs your existing server + dashboard forever
**Why:** Eliminate manual startup, make it feel like a real service
**How:**

**Pre-requisites:**

1. Create `npm run start:all` script in root package.json:
```json
"scripts": {
  "start:all": "concurrently \"cd apps/server && bun run dev\" \"cd apps/client && npm run dev\""
}
```
Install dependency: `npm install --save-dev concurrently`

2. Ensure health endpoint exists in server:
```javascript
// In apps/server (add if not exists)
app.get('/health', (req, res) => res.sendStatus(200));
```

1. **Dockerfile** (Multi-stage Node.js build)
   ```dockerfile
   FROM node:20-alpine
   WORKDIR /app
   COPY package*.json ./
   COPY apps/server/package*.json ./apps/server/
   COPY apps/client/package*.json ./apps/client/
   RUN npm ci
   COPY . .
   EXPOSE 4000 5173
   CMD ["npm", "run", "start:all"]
   ```

2. **docker-compose.yml** (Service configuration)
   ```yaml
   version: '3.8'
   services:
     claude-observe:
       build: .
       container_name: claude-observe
       ports:
         - "4000:4000"
         - "5173:5173"
       volumes:
         - ./data:/app/data
       restart: unless-stopped
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:4000/health"]
         interval: 30s
   ```

3. **One-time setup**
   ```bash
   docker-compose up -d
   # Never touch it again
   ```

### **Phase 2: Hook Utils** (Future-Proofing)

**What:** Create minimal utility functions for easier hook development
**Why:** Make future hooks 3 lines instead of 30
**How:**

**hook_utils.py** in `.claude/hooks/`:
```python
import os
import requests
from datetime import datetime

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
        pass

def wrap(event_type):
    """Decorator to auto-send events"""
    def decorator(func):
        def wrapper(event):
            func(event)
            send(event_type, event)
        return wrapper
    return decorator
```

### **Phase 3: TDD Validation** (Proving it Works)

**What:** End-to-end test that validates the entire flow
**Why:** Confidence that everything works before considering it "done"
**How:**

**test-e2e.js** using Puppeteer:
```javascript
const puppeteer = require('puppeteer');
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);
const assert = require('assert');

async function test() {
  // 1. Verify services are up
  const health = await fetch('http://localhost:4000/health');
  assert(health.ok, 'Server should be healthy');

  // 2. Open dashboard
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('http://localhost:5173');
  
  // 3. Verify connected
  await page.waitForSelector('text=Connected', { timeout: 5000 });
  
  // 4. Send test event via Claude Code
  const testId = Date.now();
  await execAsync(`claude "test observability ${testId}" --no-stream`);
  
  // 5. Wait for UserPromptSubmit event to appear
  await page.waitForSelector('span:text("💬 UserPromptSubmit")', {
    timeout: 10000
  });
  
  // 6. Click the latest event to expand
  const events = await page.$$('.group.relative.p-4');
  await events[events.length - 1].click();
  
  // 7. Verify our test prompt is in the payload
  await page.waitForSelector(`pre:text("test observability ${testId}")`);
  
  console.log('✅ Observability system validated!');
  await browser.close();
}

test().catch(console.error);
```

## 📁 File Structure

```
claude-code-hooks-multi-agent-observability/
├── Dockerfile                    [NEW]
├── docker-compose.yml           [NEW]
├── .dockerignore               [NEW]
├── test-e2e.js                 [NEW]
├── .claude/
│   └── hooks/
│       ├── hook_utils.py       [NEW]
│       ├── pre_tool_use.py     [NO CHANGE]
│       ├── post_tool_use.py    [NO CHANGE]
│       └── user_prompt_submit.py [NO CHANGE]
└── apps/
    ├── server/                 [NO CHANGE]
    └── demo-cc-tools/          [NO CHANGE]
```

## 🚀 Execution Sequence

1. **Build Container**
   - Write Dockerfile
   - Write docker-compose.yml
   - Run `docker-compose build`

2. **Start Service**
   - Run `docker-compose up -d`
   - Verify health endpoints

3. **Add Utils**
   - Create hook_utils.py
   - Place in .claude/hooks/

4. **Validate**
   - Run test-e2e.js
   - Confirm event flow works

5. **Use Forever**
   - Copy .claude/ to any project
   - Events automatically flow to dashboard
   - View at localhost:5173 anytime

## ✅ Success Criteria

- [ ] Docker container runs on machine startup
- [ ] No manual server starts ever needed
- [ ] Health endpoint responds at localhost:4000/health
- [ ] Test prompt appears in dashboard via automated test
- [ ] New projects work by just copying .claude/ folder
- [ ] Future hooks can use simple `send()` function

## 🎉 Result

Your observability system becomes invisible infrastructure - always there when you need it, never in your way when you don't. From "project you run" to "service that exists."