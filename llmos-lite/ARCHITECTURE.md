# LLMos-Lite Architecture

> From Terminal OS to Browser-Native Computational Workbench

## 🚀 Migration Status

**We are migrating from original llmos to llmos-lite + WebAssembly workflows:**

### What Changed
- **From:** Terminal UI, Python tools, server execution
- **To:** Web UI, executable skills, browser execution (WebAssembly)

### Why
- ⚡ **Zero-latency** - No network round-trips
- 🎨 **Rich previews** - Interactive 3D, plots, circuits
- 🔒 **Sandboxed** - Browser security, no server risk
- 💰 **Cost-free** - User devices, not servers
- 🌍 **P2P scalable** - Unlimited execution capacity

## Philosophy

LLMos-Lite combines **two paradigms**:

1. **Skills as Context** (OpenAI/Anthropic 2025)
   - Markdown files injected into LLM prompts
   - Git-backed version control
   - Simple pattern detection

2. **Skills as Executables** (WebAssembly Era)
   - Runnable nodes in visual workflows
   - Browser-native execution
   - Multi-runtime support (Python, JS, SPICE)

---

## Four-Layer Architecture

```
┌──────────────────────────────────────────────────────────┐
│          PRESENTATION LAYER (Browser)                    │
│  ┌──────────────┐  ┌────────────────┐                   │
│  │ React Flow   │  │ Chat Interface │                   │
│  │ Canvas       │  │ (Skill Context)│                   │
│  └──────┬───────┘  └────────┬───────┘                   │
└─────────┼──────────────────────┼────────────────────────┘
          │                      │
┌─────────▼─────────┐  ┌────────▼────────┐
│ Workflow Executor │  │ Skills Manager  │
│ (TypeScript/Wasm) │  │ (Load/Filter)   │
└─────────┬─────────┘  └────────┬────────┘
          │                     │
┌─────────▼─────────────────────▼─────────┐
│        INTERFACE LAYER (API)            │
│  - FastAPI endpoints                    │
│  - /workflows (executable skills)       │
│  - /chat (LLM + context)                │
│  - /evolve (pattern detection)          │
└─────────┬───────────────────────────────┘
          │
┌─────────▼─────────────────────────────────┐
│         LOGIC LAYER (Core)                │
│  - WorkflowEngine: DAG execution          │
│  - SkillsManager: Load/filter skills      │
│  - EvolutionCron: Detect patterns         │
│  - PatternDetector: Analyze traces        │
└─────────┬─────────────────────────────────┘
          │
┌─────────▼─────────────────────────────────┐
│         STORAGE LAYER (Volumes)           │
│  - GitVolume: Git-backed storage          │
│  - VolumeManager: Multi-tenant access     │
│  - Hierarchy: System → Team → User        │
└───────────────────────────────────────────┘
```

---

## Core Components

### 1. GitVolume (core/volumes.py)

**Purpose:** Git-backed storage for skills and traces.

**Structure:**
```
/volumes/{type}/{id}/
  skills/           # Markdown skill definitions
  traces/           # Execution history
  memory/           # Consolidated memory (future)
  .git/             # Git repository
  metadata.json     # Volume metadata
```

**Key Methods:**
- `write_skill(skill_id, content, commit_message)` - Save skill and commit
- `read_skill(skill_id)` - Read skill content
- `list_skills()` - List all skills
- `commit_changes(message, author)` - Git commit
- `get_git_log(limit)` - Git history

**Access Control:**
| Volume | User Can | Team Cron Can | System Cron Can |
|--------|----------|---------------|-----------------|
| User   | R/W      | R             | R/W             |
| Team   | R        | R/W           | R/W             |
| System | R        | R             | R/W             |

---

### 2. SkillsManager (core/skills.py)

**Purpose:** Load, filter, and inject skills into LLM context.

**Flow:**
```
1. load_skills_for_user(user_id, team_id)
   ↓
2. Load System + Team + User skills
   ↓
3. Parse Markdown with YAML frontmatter
   ↓
4. Return List[Skill]

5. filter_skills_by_query(skills, query)
   ↓
6. Score skills by keyword/name/category match
   ↓
7. Return top N relevant skills

8. build_context_for_query(user_id, team_id, query)
   ↓
9. Load → Filter → Format for LLM
   ↓
10. Return context string (injected into system prompt)
```

**Skill Format:**
```markdown
---
name: Skill Name
category: coding|analysis|writing|data
description: One-line description
keywords: [keyword1, keyword2]
---

# Skill: [Name]

## When to Use
[Description]

## Approach
[Steps]

## Example
[Code/example]
```

---

### 3. EvolutionCron (core/evolution.py)

**Purpose:** Analyze traces, detect patterns, generate skills.

**Components:**

#### PatternDetector
- Analyzes traces
- Groups by goal signature (hash)
- Calculates success rate
- Returns patterns (3+ occurrences)

#### SkillGenerator
- Takes a Pattern
- Generates SkillDraft
- Can use LLM or heuristics
- Formats as Markdown with frontmatter

#### EvolutionCron
- Orchestrates pattern → skill flow
- Configurable thresholds:
  - `min_pattern_count`: Default 3
  - `min_success_rate`: Default 0.7

**Flow:**
```
run_user_evolution(user_id, team_id)
  ↓
1. Load traces from user volume
  ↓
2. PatternDetector.analyze_traces(traces)
  ↓
3. Filter patterns (count >= 3, success >= 0.7)
  ↓
4. For each pattern:
     SkillGenerator.generate_skill_from_pattern(pattern)
  ↓
5. Save skills to user volume
  ↓
6. Git commit: "Evolution: Create skill X from N traces"
  ↓
Return stats (traces_analyzed, skills_created, etc.)
```

---

## API Design

### Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/chat` | POST | Chat with skills injection |
| `/skills` | GET | List skills |
| `/skills/{skill_id}` | GET | Get skill details |
| `/skills` | POST | Create skill |
| `/skills/promote` | POST | Promote skill (user → team) |
| `/evolve` | POST | Trigger evolution |
| `/traces` | GET | List traces |
| `/traces/{trace_id}` | GET | Get trace |
| `/volumes/stats` | GET | Volume statistics |
| `/volumes/history` | GET | Git commit history |
| `/workflows/skills/executable` | GET | List executable skills |
| `/workflows/execute` | POST | Prepare workflow for execution |
| `/workflows/save` | POST | Save workflow to Git |
| `/workflows/categories` | GET | List skill categories |

### Chat Flow

```
POST /chat
  ↓
1. Load skills (SkillsManager.load_skills_for_user)
  ↓
2. Filter skills (SkillsManager.filter_skills_by_query)
  ↓
3. Build context (Skill.to_context_injection)
  ↓
4. Call LLM with context + user message
  ↓
5. Get response
  ↓
6. Save trace to user volume
  ↓
Return {response, skills_used, trace_id}
```

### Workflow Execution Flow

```
POST /workflows/execute
  ↓
1. Load executable skills (WorkflowEngine.load_executable_skills)
  ↓
2. Create workflow DAG from nodes + edges
  ↓
3. Prepare browser payload
  ↓
4. Return {status: "ready", payload: {workflow, skills}}
  ↓
Browser receives payload
  ↓
5. Load Pyodide if needed (first time: ~3s, cached: 0ms)
  ↓
6. Execute workflow via topological sort
   - Level 1 nodes execute in parallel
   - Level 2 nodes wait for dependencies
   - Continue until all nodes complete
  ↓
7. Render previews
   - Python/Qiskit: Text outputs, plots
   - Three.js: WebGL canvas rendering
   - SPICE: Circuit diagrams, voltage plots
  ↓
Return results to UI
```

---

## Data Flow

### User Perspective

```
Day 1-7: Work
  - User chats via API
  - Skills injected into context
  - Traces saved to user volume
  ↓
Night 7: Evolution
  - Cron runs (or manual trigger)
  - Analyzes 7 days of traces
  - Detects: "Create Python scripts" x 5 times
  ↓
Result:
  - Skill created: "python-script-creation.md"
  - Committed to user volume
  ↓
Day 8+: Use Skill
  - User's future Python tasks
  - New skill auto-loaded
  - Better guidance from LLM
  ↓
Day 30: Promote
  - User reviews skill
  - Clicks "Promote to Team"
  - API: POST /skills/promote
  - Skill copied to team volume
  - Team members now have access
```

### Team Perspective

```
Team Cron (weekly):
  - Analyzes team volume traces
  - Detects cross-user patterns
  - Generates team-level skills
  - Higher threshold (5+ occurrences)
  ↓
System Cron (monthly):
  - Reviews highly-used team skills
  - Promotes to system volume
  - Becomes part of global library
```

---

## Git Workflow

### User Skill Creation

```bash
# User creates skill via API
POST /skills
  ↓
GitVolume.write_skill()
  ↓
git add volumes/users/alice/skills/my-skill.md
git commit -m "Create skill: My Skill"
  ↓
Skill now in alice's Git history
```

### Skill Promotion (User → Team)

```bash
# User promotes skill
POST /skills/promote
  ↓
VolumeManager.promote_skill()
  ↓
1. Read from user volume
2. Write to team volume
3. Git commit in team volume:
   "Promote 'my-skill' from user:alice - Reason: Useful for team"
  ↓
Skill now in team's Git history
```

### Future: Pull Requests

```bash
# Instead of direct promotion, create PR
GitVolume.create_branch("pr/alice/my-skill")
GitVolume.push_to_remote()
  ↓
Team reviews PR
  ↓
Merge to team/main
```

---

## Comparison: llmos vs llmos-lite

| Feature | llmos | llmos-lite |
|---------|-------|------------|
| **Storage** | File-based volumes | Git-backed volumes |
| **Capabilities** | Python tools | Markdown skills (2 types) |
| **Execution** | 5 modes (LEARNER, FOLLOWER, etc.) | Chat + Workflows (hybrid) |
| **Execution Location** | Server (Python/Docker) | Browser (WebAssembly) |
| **Latency** | 100-500ms (network) | <50ms (local) |
| **Previews** | Text logs | Interactive (3D, plots, circuits) |
| **Evolution** | SentienceCron (complex) | EvolutionCron (simple) |
| **State** | Valence, emotion, theory of mind | Pattern detection only |
| **Interface** | Terminal UI | Web UI (React Flow + Chat) |
| **Collaboration** | File system | Git (commits, branches, PRs) |
| **Context Injection** | Tool search + examples | Direct markdown injection |
| **LLM Integration** | Claude SDK with agents | Direct API calls |
| **Cost** | Server compute | Free (user devices) |

---

## Scalability

### Storage

- **Git repositories**: Standard Git scalability
- **Sharding**: Teams in separate repos
- **Archiving**: Old traces can be compressed/archived

### Compute

- **Stateless API**: Horizontal scaling
- **Background jobs**: Evolution crons run async
- **Caching**: Skills manager has in-memory cache

### Future Optimizations

- **Vector DB**: For semantic skill search
- **Redis**: For distributed caching
- **Message Queue**: For async evolution jobs

---

## Security

### Current

- Volume-level isolation (user/team/system)
- Git history for audit trail
- Readonly flags for access control

### Future

- **Authentication**: JWT tokens
- **Authorization**: RBAC (roles: user, team_admin, system_admin)
- **API Keys**: For programmatic access
- **Git signing**: GPG signatures for commits

---

## Migration from llmos

### What to Keep

1. **Traces**: Migrate from `/workspace/memories/traces/` to `/volumes/users/{id}/traces/`
2. **Agents**: Convert to skills (agents/*.md → skills/*.md)
3. **Volume metadata**: Convert file-based to Git-based

### What to Discard

1. **Sentience state** (valence.json, etc.)
2. **Python tools** (replace with markdown skills)
3. **Mode strategies** (simplified to single mode)
4. **Complex hooks system** (use middleware instead)

### Migration Script (Conceptual)

```python
# migrate.py
from pathlib import Path
import shutil

def migrate_user(user_id: str):
    old_workspace = Path(f"workspace/users/{user_id}")
    new_volume = Path(f"volumes/users/{user_id}")

    # 1. Migrate traces
    old_traces = old_workspace / "memories/traces"
    new_traces = new_volume / "traces"
    if old_traces.exists():
        shutil.copytree(old_traces, new_traces)

    # 2. Convert agents to skills
    old_agents = old_workspace / "agents"
    new_skills = new_volume / "skills"
    if old_agents.exists():
        for agent_file in old_agents.glob("*.md"):
            # Convert agent frontmatter to skill frontmatter
            content = agent_file.read_text()
            skill_content = convert_agent_to_skill(content)
            (new_skills / agent_file.name).write_text(skill_content)

    # 3. Git init
    subprocess.run(["git", "init"], cwd=new_volume)
    subprocess.run(["git", "add", "."], cwd=new_volume)
    subprocess.run(["git", "commit", "-m", "Migration from llmos"], cwd=new_volume)
```

---

## Future Directions

### 1. Multi-Agent Orchestration

Keep the ORCHESTRATOR concept from llmos:
- Complex tasks → Decompose into subtasks
- Each subtask → Separate agent with relevant skills
- Coordinate results

### 2. RAG for Skills

- Embed skills into vector DB
- Semantic search for relevant skills
- More intelligent context injection

### 3. Skill Templates

- Library of common skill patterns
- One-click skill creation
- Community skill marketplace

### 4. Real-time Collaboration

- WebSocket for live updates
- Shared editing of skills
- Team chat with skills bot

---

## Design Principles

1. **Simplicity over Features**: One clear way to do things
2. **Git as Source of Truth**: Version control everything
3. **Markdown as Interface**: Human-readable, LLM-friendly
4. **Evolution over Configuration**: Learn from usage, don't pre-configure
5. **Collaboration-First**: Built for teams, not just individuals

---

## Contributing

The architecture is designed to be **extensible**:

- **Add Skills**: Drop `.md` files in system volume
- **Enhance Evolution**: Improve pattern detection algorithms
- **New Storage**: Implement VolumeInterface for S3, etc.
- **Better LLM Integration**: Add streaming, function calling
- **Build UI**: React/Next.js interface

See the main README for contribution guidelines.
