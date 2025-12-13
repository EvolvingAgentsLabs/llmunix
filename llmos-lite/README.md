# LLMos-Lite

> A simplified, Git-backed, Skills-driven LLM Operating System

**LLMos-Lite** is a refactored version of the original `llmos` system, designed as a **web-first, collaborative platform** for building self-evolving AI systems.

## Key Concepts

### 1. Skills (Not Tools)
Skills are **Markdown files** containing best practices, patterns, and instructions. They get injected into the LLM's context to guide behavior.

**Example Skill:**
```markdown
---
name: Python Testing
category: coding
description: How to write effective Python tests
keywords: [python, testing, pytest]
---

# Skill: Python Testing

## When to Use
Use when writing tests for Python code.

## Approach
1. Write test functions starting with `test_`
2. Use descriptive names
3. Test one thing per function
4. Use fixtures for setup
...
```

### 2. Git-Backed Volumes
All artifacts (skills, traces, memory) are stored in **Git repositories**, enabling:
- Version control of skills
- Pull requests for skill promotion (User → Team → System)
- Distributed collaboration
- Rollback capabilities

**Volume Hierarchy:**
```
/volumes/
  system/         # Global skills (read-only for users)
  teams/
    {team_id}/    # Shared team skills
  users/
    {user_id}/    # Private user skills
```

### 3. Evolution Engine
The **Evolution Cron** analyzes execution traces, detects patterns, and auto-generates skills.

**Flow:**
1. User executes tasks → Traces saved
2. Evolution Cron runs (nightly or on-demand)
3. Detects repeated patterns (3+ occurrences)
4. Generates draft skills
5. Commits to user's Git volume
6. User reviews → Promotes to team if valuable

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web UI (React)                       │
│   - Chat Interface                                      │
│   - Skills Panel (browse/create)                        │
│   - Evolution View (review auto-generated skills)       │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                 FastAPI Service                         │
│   - /chat (LLM with skills injection)                   │
│   - /skills (CRUD operations)                           │
│   - /evolve (trigger pattern detection)                 │
│   - /volumes (Git history, stats)                       │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  Core Modules                           │
│   - volumes.py (Git-backed storage)                     │
│   - skills.py (Skills loader & context injection)       │
│   - evolution.py (Pattern detection & skill generation) │
└─────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Installation

```bash
cd llmos-lite
pip install -r requirements.txt
```

### 2. Set API Key

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### 3. Run the API

```bash
python api/main.py
```

Server starts at `http://localhost:8000`

### 4. API Docs

Visit `http://localhost:8000/docs` for interactive API documentation.

---

## API Examples

### Chat with Skills

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice",
    "team_id": "engineering",
    "message": "Write a Python function to calculate Fibonacci numbers",
    "include_skills": true,
    "max_skills": 5
  }'
```

**Response:**
```json
{
  "response": "Here's a Fibonacci function...",
  "skills_used": ["Python Coding Best Practices"],
  "trace_id": "trace_20250101_120000"
}
```

### List Skills

```bash
curl "http://localhost:8000/skills?user_id=alice&team_id=engineering"
```

**Response:**
```json
{
  "total": 3,
  "skills": [
    {
      "name": "Python Coding Best Practices",
      "category": "coding",
      "volume": "system",
      "keywords": ["python", "coding"]
    },
    ...
  ]
}
```

### Trigger Evolution

```bash
curl -X POST "http://localhost:8000/evolve" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice",
    "team_id": "engineering",
    "auto_apply": true
  }'
```

**Response:**
```json
{
  "status": "completed",
  "traces_analyzed": 47,
  "patterns_detected": 5,
  "skills_created": 2
}
```

### Create a Skill

```bash
curl -X POST "http://localhost:8000/skills" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice",
    "skill_id": "my-testing-skill",
    "name": "My Testing Workflow",
    "category": "coding",
    "description": "How I write tests",
    "content": "## Approach\n1. Write test\n2. Run test\n...",
    "keywords": ["testing", "pytest"]
  }'
```

### Promote Skill (User → Team)

```bash
curl -X POST "http://localhost:8000/skills/promote" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice",
    "team_id": "engineering",
    "skill_id": "my-testing-skill",
    "reason": "Useful for all team members"
  }'
```

---

## Directory Structure

```
llmos-lite/
├── core/
│   ├── volumes.py          # Git-backed volume system
│   ├── skills.py           # Skills loader & manager
│   └── evolution.py        # Pattern detection & skill generation
├── api/
│   └── main.py             # FastAPI service
├── volumes/                # Git repositories
│   ├── system/
│   │   ├── skills/         # Global skills library
│   │   └── .git/
│   ├── teams/
│   │   └── {team_id}/
│   │       ├── skills/     # Team-specific skills
│   │       ├── traces/     # Team execution history
│   │       └── .git/
│   └── users/
│       └── {user_id}/
│           ├── skills/     # User's draft skills
│           ├── traces/     # User's execution traces
│           └── .git/
├── requirements.txt
└── README.md
```

---

## Key Differences from Original LLMos

| Original `llmos` | `llmos-lite` |
|------------------|--------------|
| 5 execution modes (LEARNER, FOLLOWER, MIXED, CRYSTALLIZED, ORCHESTRATOR) | 1 mode: Load Skills → Execute → Save Trace |
| Sentience Layer (Valence, Emotion, Theory of Mind) | Simple Pattern Detection |
| Python Tools | Markdown Skills (context injection) |
| File-based Volumes | Git-backed Volumes |
| Complex agent_loader | Simple SkillsManager |
| Terminal UI | Web API (FastAPI) + React UI |

---

## Evolution Workflow

```
┌──────────────┐
│ User Works   │
│ (Chat, Code) │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Save Traces  │
│ (Execution   │
│  History)    │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ Evolution Cron   │
│ (Nightly/Manual) │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Detect Patterns  │
│ (3+ occurrences) │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Generate Skills  │
│ (Markdown files) │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Git Commit       │
│ (User volume)    │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ User Reviews     │
│ → Promote to Team│
└──────────────────┘
```

---

## Development Roadmap

### Phase 1: Core System ✓
- [x] Git-backed volumes
- [x] Skills loader
- [x] Evolution engine
- [x] FastAPI service

### Phase 2: LLM Integration (Next)
- [ ] Anthropic Claude integration
- [ ] Skill-aware prompting
- [ ] Streaming responses
- [ ] Token tracking

### Phase 3: Web UI (Next)
- [ ] React chat interface
- [ ] Skills browser/editor
- [ ] Evolution review panel
- [ ] Git history viewer

### Phase 4: Advanced Features
- [ ] Multi-agent orchestration
- [ ] RAG/Vector search for skills
- [ ] Skill templates library
- [ ] Team collaboration features

---

## Configuration

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=your-key-here

# Optional
LLMOS_VOLUMES_PATH=./volumes          # Default: ./volumes
LLMOS_MIN_PATTERN_COUNT=3             # Default: 3
LLMOS_MIN_SUCCESS_RATE=0.7            # Default: 0.7
```

---

## Contributing

This is a **living system** designed to evolve:

1. **Add System Skills**: Create `.md` files in `/volumes/system/skills/`
2. **Improve Evolution**: Enhance pattern detection in `core/evolution.py`
3. **Build Integrations**: Add support for new LLMs, storage backends
4. **Create UI**: Build web interface for skills management

---

## License

Apache 2.0

---

## Credits

Built on insights from the original [llmos](../llmos) architecture, reimagined for the **Skills Era** of AI development (inspired by OpenAI/Anthropic's 2025 direction).

**Core Innovation**: Treating capabilities as **version-controlled Markdown files** rather than Python code, enabling:
- Human-readable, editable skills
- Git-based collaboration
- LLM-native context injection
- Zero-cost execution (no tool calling overhead)
