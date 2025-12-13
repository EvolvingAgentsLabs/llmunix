# LLMos-Lite Quick Start Guide

Get up and running with LLMos-Lite in 5 minutes.

---

## Prerequisites

- Python 3.9+
- Git

---

## Installation

### 1. Install Dependencies

```bash
cd llmos-lite
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

*(Optional: LLM integration not yet implemented, but setting this now prepares for Phase 1)*

---

## Running the API

### Start the Server

```bash
python api/main.py
```

You should see:
```
🚀 LLMos-Lite API starting...
📁 Volumes path: ./volumes
✓ System volume initialized: ./volumes/system
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Access API Docs

Open your browser: `http://localhost:8000/docs`

You'll see interactive Swagger documentation.

---

## Testing the API

### In Another Terminal

```bash
python test_api.py
```

This will run through all endpoints and show you the system in action.

---

## Your First Interactions

### 1. List Available Skills

```bash
curl "http://localhost:8000/skills?user_id=alice&team_id=engineering"
```

**Response:**
```json
{
  "total": 2,
  "skills": [
    {
      "name": "Python Coding Best Practices",
      "category": "coding",
      "description": "Best practices for writing clean Python code",
      "volume": "system",
      "keywords": ["python", "coding", "clean code"]
    },
    {
      "name": "Data Analysis Workflow",
      "category": "analysis",
      "description": "Step-by-step approach for analyzing datasets",
      "volume": "system",
      "keywords": ["data", "analysis", "pandas"]
    }
  ]
}
```

### 2. Create Your First Skill

```bash
curl -X POST "http://localhost:8000/skills" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice",
    "skill_id": "my-first-skill",
    "name": "My First Skill",
    "category": "general",
    "description": "Learning how skills work",
    "content": "## Approach\n\n1. Create the skill\n2. Use it in chat\n3. Evolve it over time",
    "keywords": ["learning", "example"]
  }'
```

**Response:**
```json
{
  "status": "created",
  "skill_id": "my-first-skill"
}
```

### 3. Check Git History

```bash
curl "http://localhost:8000/volumes/history?user_id=alice&limit=5"
```

You'll see the Git commit for your skill creation!

### 4. Chat with Skills

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice",
    "team_id": "engineering",
    "message": "Write a Python function to check if a number is prime",
    "include_skills": true,
    "max_skills": 3
  }'
```

**Response:**
```json
{
  "response": "[LLM Response with skills guidance...]",
  "skills_used": ["Python Coding Best Practices"],
  "trace_id": "trace_20250113_143022"
}
```

*(Note: LLM integration is a placeholder for now - Phase 1 will add real Anthropic API calls)*

### 5. Trigger Evolution

After a few chat interactions, trigger evolution to detect patterns:

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
  "traces_analyzed": 3,
  "patterns_detected": 0,
  "skills_created": 0
}
```

*(You need 3+ similar traces for a pattern to be detected)*

---

## Exploring the File System

### Where Are Your Volumes?

```bash
tree volumes/
```

**Output:**
```
volumes/
├── system/
│   ├── skills/
│   │   ├── python-coding.md
│   │   └── data-analysis.md
│   ├── .git/
│   └── metadata.json
└── users/
    └── alice/
        ├── skills/
        │   └── my-first-skill.md
        ├── traces/
        │   └── trace_20250113_143022.md
        ├── .git/
        └── metadata.json
```

### Check Git History

```bash
cd volumes/users/alice
git log --oneline
```

**Output:**
```
a1b2c3d Create skill: My First Skill
e4f5g6h Initial volume
```

### Read a Skill

```bash
cat volumes/users/alice/skills/my-first-skill.md
```

**Output:**
```markdown
---
name: My First Skill
category: general
description: Learning how skills work
keywords: [learning, example]
---

## Approach

1. Create the skill
2. Use it in chat
3. Evolve it over time
```

---

## Common Workflows

### Workflow 1: Daily Work

```
1. User chats via API
   ↓
2. Relevant skills auto-loaded
   ↓
3. LLM uses skills to guide response
   ↓
4. Trace saved automatically
```

### Workflow 2: Evolution (Weekly)

```
1. Trigger evolution (manual or cron)
   ↓
2. System analyzes past week's traces
   ↓
3. Detects patterns (3+ similar tasks)
   ↓
4. Generates draft skills
   ↓
5. User reviews and refines
   ↓
6. Promotes valuable skills to team
```

### Workflow 3: Skill Promotion

```
1. User creates/refines skill
   ↓
2. Uses it successfully multiple times
   ↓
3. Clicks "Promote to Team" (or API call)
   ↓
4. Skill copied to team volume
   ↓
5. Team members now have access
```

---

## Development Tips

### Hot Reload

For development, use `uvicorn` with reload:

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Changes to Python files will auto-reload the server.

### API Logs

Check the terminal running the API for request logs:

```
INFO:     127.0.0.1:54321 - "POST /chat HTTP/1.1" 200 OK
INFO:     127.0.0.1:54322 - "GET /skills?user_id=alice&team_id=engineering HTTP/1.1" 200 OK
```

### Volume Permissions

If you get Git errors, ensure the volumes directory is writable:

```bash
chmod -R u+w volumes/
```

### Reset Volumes

To start fresh:

```bash
rm -rf volumes/
python api/main.py  # Will recreate system volume
```

---

## Troubleshooting

### Error: "Could not initialize Git"

**Solution:** Ensure Git is installed:
```bash
git --version
```

### Error: "Connection refused"

**Solution:** Make sure the API is running:
```bash
python api/main.py
```

### Error: "Module not found"

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Skills Not Loading

**Solution:** Clear the cache by restarting the API.

---

## Next Steps

### Phase 1: Add Real LLM

1. Get Anthropic API key
2. Update `api/main.py` - uncomment Claude integration
3. Test with real conversations

### Phase 2: Build UI

1. Create React app
2. Connect to API
3. Add chat interface
4. Add skills browser

### Phase 3: Team Collaboration

1. Add user authentication
2. Enable team creation
3. Implement PR workflow for skill promotion

---

## API Reference

### Core Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check |
| `/chat` | POST | Chat with skills |
| `/skills` | GET | List skills |
| `/skills` | POST | Create skill |
| `/skills/{skill_id}` | GET | Get skill |
| `/skills/promote` | POST | Promote skill |
| `/evolve` | POST | Trigger evolution |
| `/traces` | GET | List traces |
| `/traces/{trace_id}` | GET | Get trace |
| `/volumes/stats` | GET | Volume stats |
| `/volumes/history` | GET | Git history |

### Full Documentation

Visit `http://localhost:8000/docs` for interactive Swagger docs.

---

## Learning Resources

- **README.md** - Overview and concepts
- **ARCHITECTURE.md** - Technical deep dive
- **REFACTORING_SUMMARY.md** - What changed from llmos
- **System Skills** - `volumes/system/skills/*.md` for examples

---

## Getting Help

### Check the Logs

API logs show detailed request/response information.

### Test Script

Run `python test_api.py` to verify everything works.

### Examples

Look at system skills in `volumes/system/skills/` for formatting examples.

---

## Congratulations!

You now have a working LLMos-Lite instance. Start chatting, creating skills, and watching the system evolve! 🚀

**What's next?**
- Create more skills
- Integrate with real LLM (Phase 1)
- Build a web UI (Phase 2)
- Share skills with your team

Happy evolving! 🌱
