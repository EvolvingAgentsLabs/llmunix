# Vercel Deployment Analysis for LLMos-Lite

**Date**: December 13, 2025
**Status**: Feasibility Analysis
**Verdict**: ✅ **Highly Feasible with Recommended Architecture**

---

## Executive Summary

**YES, llmos-lite can be deployed to Vercel** with some architectural adjustments. The combination of:
- **Vercel's Python runtime** (FastAPI support)
- **WebAssembly support** (Pyodide in browser)
- **OpenRouter API** (flexible LLM provider)
- **User-provided API keys** (no server-side key management)

Makes this a **perfect fit** for a fully serverless, scalable deployment.

---

## Architecture: Vercel-Native LLMos-Lite

### Recommended Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    VERCEL DEPLOYMENT                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Frontend (Edge Network)                               │ │
│  │ - Next.js 14 (Static + SSR)                          │ │
│  │ - React Flow, Monaco, xterm.js                       │ │
│  │ - Pyodide (WebAssembly in browser)                   │ │
│  │ - User's API key (localStorage)                      │ │
│  └───────────────────────────────────────────────────────┘ │
│                          ↓                                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ API Routes (Vercel Functions - Python)               │ │
│  │ /api/chat.py        - OpenRouter proxy              │ │
│  │ /api/skills.py      - Skills CRUD                    │ │
│  │ /api/sessions.py    - Session management             │ │
│  │ /api/evolve.py      - Evolution cron                 │ │
│  │ /api/workflows.py   - Workflow execution prep        │ │
│  └───────────────────────────────────────────────────────┘ │
│                          ↓                                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Storage (Vercel Blob / KV / Postgres)                │ │
│  │ - Vercel Blob: Git volumes (files)                   │ │
│  │ - Vercel KV: Session cache (Redis)                   │ │
│  │ - Vercel Postgres: Traces, patterns (optional)       │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Analysis

### ✅ 1. Python Runtime (FastAPI)

**Vercel Support**: ✅ **Full support** for FastAPI in Beta

**Current llmos-lite API**:
```python
# api/main.py (FastAPI)
from fastapi import FastAPI
app = FastAPI()

@app.post("/chat")
async def chat(request: ChatRequest):
    # Current implementation
    pass
```

**Vercel Adaptation**:
```python
# api/chat.py (Vercel Function)
from fastapi import FastAPI
app = FastAPI()

@app.post("/")
async def chat_handler(request: ChatRequest):
    # Same logic, different entry point
    return await chat(request)
```

**Migration Effort**: **Low** - Minimal changes needed

**Bundle Size**: FastAPI + dependencies = ~50MB (well under 250MB limit)

**Recommendation**: ✅ **Use Vercel's Python runtime for API routes**

---

### ✅ 2. WebAssembly (Pyodide)

**Vercel Support**: ✅ **Full support** in Edge/Node/Bun runtimes

**Current Implementation**:
```typescript
// ui/lib/pyodide-runner.ts
const pyodide = await loadPyodide();
await pyodide.runPythonAsync(`
  def execute(inputs):
    # VQE optimization
    return {"eigenvalue": -1.137}
`);
```

**Vercel Deployment**:
- Pyodide loads **client-side** (no server execution needed!)
- Vercel Edge Network delivers Wasm binaries efficiently
- Works perfectly with current architecture

**Recommendation**: ✅ **Keep current browser-based Pyodide execution**

---

### ✅ 3. OpenRouter Integration

**Why OpenRouter?**
- ✅ Single API for multiple LLM providers (Claude, GPT, Gemini)
- ✅ No vendor lock-in (switch models easily)
- ✅ Free tier options (moonshotai/kimi-k2:free)
- ✅ User-provided keys (no server-side key management)
- ✅ OpenAI-compatible API (easy migration)

**Implementation**:

```typescript
// lib/llm-client.ts
export class LLMClient {
  constructor(private apiKey: string, private model: string) {}

  async chat(messages: Message[]): Promise<string> {
    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'HTTP-Referer': 'https://llmos-lite.vercel.app',
        'X-Title': 'LLMos-Lite',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: this.model, // User-selected: claude-opus-4.5, gpt-5.2-pro, kimi-k2:free
        messages: messages
      })
    });

    const data = await response.json();
    return data.choices[0].message.content;
  }
}
```

**User Flow**:
1. User provides OpenRouter API key (stored in localStorage)
2. User selects model (Claude, GPT, or free tier)
3. Chat messages go through Vercel API route → OpenRouter
4. API key never stored on server

**Recommendation**: ✅ **Use OpenRouter with user-provided keys**

---

### ✅ 4. Git-Backed Volumes

**Challenge**: Vercel functions are **stateless** (no persistent file system)

**Solution**: Use **Vercel Blob Storage**

**Current Implementation**:
```python
# core/volumes.py
class GitVolume:
    def __init__(self, base_path: Path):
        self.base_path = base_path  # Local file system
        self._init_git_if_needed()
```

**Vercel Adaptation**:
```python
# core/volumes_vercel.py
from vercel_blob import put, get, list as blob_list
import json

class BlobGitVolume:
    def __init__(self, volume_id: str):
        self.volume_id = volume_id
        self.prefix = f"volumes/{volume_id}/"

    async def write_skill(self, skill_id: str, content: str):
        # Store in Vercel Blob
        blob_path = f"{self.prefix}skills/{skill_id}.md"
        await put(blob_path, content)

        # Store commit metadata
        commit = {
            "timestamp": datetime.now().isoformat(),
            "message": f"Update skill: {skill_id}",
            "files": [blob_path]
        }
        await put(f"{self.prefix}.git/commits/{commit_id}", json.dumps(commit))

    async def read_skill(self, skill_id: str):
        blob_path = f"{self.prefix}skills/{skill_id}.md"
        return await get(blob_path)

    async def list_skills(self):
        blobs = await blob_list(prefix=f"{self.prefix}skills/")
        return [b.pathname.split('/')[-1].replace('.md', '') for b in blobs]

    async def get_git_log(self, limit: int = 10):
        commits = await blob_list(prefix=f"{self.prefix}.git/commits/")
        # Sort by timestamp, return recent
        return sorted(commits, reverse=True)[:limit]
```

**Vercel Blob Pricing**:
- Free: 1 GB storage
- Pro: 100 GB storage ($0.15/GB/month)

**Recommendation**: ✅ **Use Vercel Blob for Git volumes**

**Alternative**: Use **GitHub as backend** (store volumes in GitHub repos, use API)

---

### ✅ 5. Session Management

**Challenge**: Real-time session state across serverless functions

**Solution**: **Vercel KV** (Redis-compatible)

**Implementation**:
```python
# api/sessions.py
from vercel_kv import kv

async def create_session(user_id: str, session_id: str):
    session_key = f"session:{user_id}:{session_id}"
    await kv.hset(session_key, {
        "id": session_id,
        "user_id": user_id,
        "traces": [],
        "started_at": datetime.now().isoformat()
    })
    await kv.expire(session_key, 86400)  # 24h TTL

async def add_trace(user_id: str, session_id: str, trace: dict):
    session_key = f"session:{user_id}:{session_id}"
    traces = await kv.hget(session_key, "traces") or []
    traces.append(trace)
    await kv.hset(session_key, "traces", traces)

async def get_active_sessions(user_id: str):
    pattern = f"session:{user_id}:*"
    keys = await kv.keys(pattern)
    return [await kv.hgetall(k) for k in keys]
```

**Vercel KV Pricing**:
- Free: 256 MB storage, 100K commands/month
- Pro: 1 GB storage, 10M commands/month

**Recommendation**: ✅ **Use Vercel KV for active sessions**

---

### ✅ 6. Evolution Cron

**Challenge**: Scheduled cron jobs in serverless

**Solution**: **Vercel Cron Jobs**

**Configuration**:
```json
// vercel.json
{
  "crons": [
    {
      "path": "/api/cron/evolution_user",
      "schedule": "0 0 * * *"  // Daily at midnight
    },
    {
      "path": "/api/cron/evolution_team",
      "schedule": "0 0 * * 0"  // Weekly on Sunday
    }
  ]
}
```

**Implementation**:
```python
# api/cron/evolution_user.py
from fastapi import FastAPI, Request
app = FastAPI()

@app.get("/")
async def evolution_user_cron(request: Request):
    # Verify cron secret
    if request.headers.get("Authorization") != f"Bearer {os.getenv('CRON_SECRET')}":
        return {"error": "Unauthorized"}

    # Run evolution for all users
    users = await get_all_users()
    for user in users:
        await run_evolution(user.id)

    return {"status": "completed", "users_processed": len(users)}
```

**Vercel Cron Pricing**:
- Hobby: 1 cron job
- Pro: Unlimited cron jobs

**Recommendation**: ✅ **Use Vercel Cron for evolution**

---

## Proposed Architecture

### Directory Structure (Vercel-Optimized)

```
llmos-lite/
├── api/                        # Vercel Functions (Python)
│   ├── chat.py                 # POST /api/chat
│   ├── skills.py               # GET/POST /api/skills
│   ├── sessions.py             # GET/POST /api/sessions
│   ├── evolve.py               # POST /api/evolve
│   ├── workflows.py            # GET/POST /api/workflows
│   └── cron/
│       ├── evolution_user.py   # Cron: User evolution
│       └── evolution_team.py   # Cron: Team evolution
│
├── ui/                         # Next.js Frontend
│   ├── app/                    # App Router
│   ├── components/             # React components
│   ├── lib/
│   │   ├── llm-client.ts       # OpenRouter client
│   │   ├── api-client.ts       # API wrapper
│   │   ├── pyodide-runner.ts   # Wasm executor
│   │   └── workflow-executor.ts
│   └── styles/
│
├── core/                       # Shared Python logic
│   ├── volumes_vercel.py       # Blob storage adapter
│   ├── skills.py               # Skills manager
│   ├── evolution.py            # Pattern detection
│   └── workflow.py             # Workflow engine
│
├── vercel.json                 # Vercel configuration
├── requirements.txt            # Python dependencies
└── package.json                # Node dependencies
```

### vercel.json Configuration

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install && pip install -r requirements.txt",
  "framework": "nextjs",
  "functions": {
    "api/**/*.py": {
      "runtime": "python3.12",
      "memory": 512,
      "maxDuration": 30,
      "excludeFiles": "{tests/**,__tests__/**,**/*.test.py}"
    }
  },
  "crons": [
    {
      "path": "/api/cron/evolution_user",
      "schedule": "0 0 * * *"
    },
    {
      "path": "/api/cron/evolution_team",
      "schedule": "0 0 * * 0"
    }
  ],
  "env": {
    "VERCEL_BLOB_READ_WRITE_TOKEN": "@blob-token",
    "VERCEL_KV_REST_API_URL": "@kv-url",
    "VERCEL_KV_REST_API_TOKEN": "@kv-token",
    "CRON_SECRET": "@cron-secret"
  }
}
```

---

## User Flow with OpenRouter

### Setup Flow

1. **User visits https://llmos-lite.vercel.app**
2. **First-time setup screen**:
   ```
   ┌─────────────────────────────────────────┐
   │ Welcome to LLMos-Lite                   │
   ├─────────────────────────────────────────┤
   │                                         │
   │ To get started, configure your LLM:     │
   │                                         │
   │ API Provider:                           │
   │ ○ OpenRouter (Recommended)              │
   │ ○ Anthropic (Claude only)               │
   │ ○ OpenAI (GPT only)                     │
   │                                         │
   │ OpenRouter API Key:                     │
   │ [sk-or-v1-...]                          │
   │ Get your free key at openrouter.ai      │
   │                                         │
   │ Model Selection:                        │
   │ ○ Claude Opus 4.5 ($15/M tokens)        │
   │ ○ GPT-5.2 Pro ($20/M tokens)            │
   │ ○ Kimi K2 (FREE)                        │
   │                                         │
   │ [Save Configuration]                    │
   │                                         │
   └─────────────────────────────────────────┘
   ```
3. **API key stored in localStorage** (never sent to server)
4. **Model selection saved to user profile** (Vercel KV)

### Chat Flow

```typescript
// User types message
const message = "Help me optimize VQE circuit";

// Frontend sends to API route (with user's key)
const response = await fetch('/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': localStorage.getItem('openrouter_key'),  // User's key
    'X-Model': localStorage.getItem('selected_model')     // User's model
  },
  body: JSON.stringify({
    user_id: userId,
    team_id: teamId,
    message: message,
    session_id: sessionId
  })
});

// Backend proxies to OpenRouter
// api/chat.py
@app.post("/")
async def chat(request: Request):
    user_key = request.headers.get("X-API-Key")
    model = request.headers.get("X-Model")

    # Call OpenRouter with user's key
    response = await openrouter_client.chat(
        api_key=user_key,
        model=model,
        messages=[{"role": "user", "content": message}]
    )

    # Save trace to Vercel Blob
    await save_trace(user_id, session_id, trace)

    return response
```

**Benefits**:
- ✅ No server-side API key management
- ✅ User controls costs
- ✅ User chooses model (including free tier)
- ✅ Privacy: API key never leaves user's browser

---

## Cost Analysis

### Vercel Pricing (Pro Plan)

| Resource | Free Tier | Pro Plan | Needed? |
|----------|-----------|----------|---------|
| Functions | 100 GB-hrs/mo | 1,000 GB-hrs/mo | ✅ Yes |
| Bandwidth | 100 GB/mo | 1 TB/mo | ✅ Yes |
| Blob Storage | 1 GB | 100 GB | ✅ Yes |
| KV Storage | 256 MB | 1 GB | ✅ Yes (sessions) |
| Cron Jobs | 1 job | Unlimited | ✅ Yes (evolution) |
| **Total Cost** | **$0/mo** | **$20/mo** | **Pro needed** |

### User LLM Costs (OpenRouter)

| Model | Input | Output | Use Case |
|-------|-------|--------|----------|
| **Kimi K2** (free) | $0/M | $0/M | Free tier users |
| **Claude Opus 4.5** | $15/M | $75/M | Power users |
| **GPT-5.2 Pro** | $20/M | $100/M | Alternative |

**User pays their own LLM costs** via OpenRouter!

**Total Cost to Run llmos-lite**: **$20/mo (Vercel Pro)** + **$0 LLM costs** (user-paid)

---

## Migration Plan

### Phase 1: Vercel-Compatible Backend (Week 1)

**Tasks**:
- [ ] Adapt FastAPI routes to Vercel Functions format
- [ ] Implement `BlobGitVolume` (Vercel Blob adapter)
- [ ] Implement session management (Vercel KV)
- [ ] Configure `vercel.json`
- [ ] Test locally with `vercel dev`

**Files to Create**:
```
api/
├── chat.py
├── skills.py
├── sessions.py
├── evolve.py
└── cron/
    ├── evolution_user.py
    └── evolution_team.py

core/
└── volumes_vercel.py  # Blob storage adapter
```

### Phase 2: OpenRouter Integration (Week 2)

**Tasks**:
- [ ] Create `LLMClient` with OpenRouter support
- [ ] Build first-time setup screen
- [ ] Implement API key management (localStorage)
- [ ] Model selection UI
- [ ] Chat proxy through `/api/chat`

**Files to Create**:
```
ui/lib/
├── llm-client.ts
└── api-client.ts

ui/components/
└── setup/
    ├── APIKeySetup.tsx
    └── ModelSelector.tsx
```

### Phase 3: Deployment (Week 3)

**Tasks**:
- [ ] Create Vercel project
- [ ] Configure environment variables (Blob, KV tokens)
- [ ] Deploy to Vercel
- [ ] Test all features
- [ ] Set up cron jobs
- [ ] Production testing

---

## Advantages of Vercel Deployment

### ✅ **Scalability**
- Auto-scales to handle any traffic
- Global CDN for fast UI delivery
- Serverless functions scale independently

### ✅ **Cost Efficiency**
- $20/mo for unlimited users (Pro plan)
- Users pay their own LLM costs
- No server maintenance

### ✅ **Developer Experience**
- `vercel dev` for local development
- Git-based deployments
- Preview deployments for PRs
- Easy rollbacks

### ✅ **Performance**
- Edge Network (<50ms latency globally)
- WebAssembly runs in browser (zero server cost)
- KV for fast session access

### ✅ **Flexibility**
- Users choose LLM provider (OpenRouter)
- Users choose model (Claude, GPT, or free)
- Users provide their own keys (privacy + cost control)

---

## Challenges & Solutions

### Challenge 1: Stateless Functions
**Solution**: Use Vercel KV for active sessions, Vercel Blob for persistent storage

### Challenge 2: Git Operations
**Solution**: Simulate Git with Blob metadata (commit history, branches via JSON)

### Challenge 3: Cold Starts
**Solution**: Use Vercel's Edge Functions for critical paths (chat proxy)

### Challenge 4: Bundle Size Limits (250 MB)
**Solution**: Exclude tests and large files via `vercel.json` config

### Challenge 5: Concurrent Cron Jobs
**Solution**: Use Vercel KV locks to prevent overlapping executions

---

## Recommendation

### ✅ **YES, Deploy to Vercel**

**Reasons**:
1. Perfect fit for serverless architecture
2. Python runtime supports FastAPI
3. WebAssembly works great in browser
4. OpenRouter provides flexibility + user-paid LLM costs
5. Vercel Blob/KV solve storage challenges
6. $20/mo for unlimited scale

**Architecture**:
- **Frontend**: Next.js on Vercel Edge
- **Backend**: Python FastAPI (Vercel Functions)
- **Storage**: Vercel Blob (volumes) + KV (sessions)
- **LLM**: OpenRouter (user-provided keys)
- **Execution**: Pyodide (browser WebAssembly)
- **Cron**: Vercel Cron Jobs

**Next Steps**:
1. Create `vercel.json` configuration
2. Adapt FastAPI routes to Vercel format
3. Implement Blob/KV adapters
4. Build OpenRouter integration
5. Deploy and test

**Timeline**: 3 weeks to production-ready Vercel deployment

---

## Appendix: Free Tier Option

For users on **Vercel Hobby (Free) plan**:

**Limitations**:
- 1 cron job only (evolution-user only)
- 100 GB-hrs/month functions
- 1 GB Blob storage
- 256 MB KV storage

**Workaround**:
- Use **GitHub Actions** for cron jobs (free, unlimited)
- Use **GitHub repos** for volumes (free, unlimited)
- Keep UI/API on Vercel Free tier

**Result**: Fully free deployment possible (with GitHub as backend)!

---

**Status**: Ready to implement Vercel deployment
**Recommendation**: Start with Phase 1 (Vercel-compatible backend)
