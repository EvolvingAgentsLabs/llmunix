# Wabi POC - Quick Start Guide

## 5-Minute Demo

Get the Wabi POC running in 5 minutes!

### Step 1: Install Dependencies (1 min)

```bash
pip install fastapi uvicorn pydantic pyyaml python-dotenv
```

### Step 2: Verify Setup (30 seconds)

```bash
# Check user profile exists
cat system/user_profiles/user123/memory.md | head -20

# Check agents are discoverable
ls .claude/agents/ | grep -i wabi
```

### Step 3: Run Tests (1 min)

```bash
python3 projects/Project_wabi_poc/test_wabi_poc.py
```

**Expected output:**
```
🎉 ALL TESTS PASSED!
The Wabi POC is working correctly!
```

### Step 4: Start API Server (30 seconds)

```bash
python3 system/api/wabi_app_server.py
```

**Server starts on:** `http://localhost:8000`

### Step 5: Test API (2 min)

**In a new terminal:**

```bash
# Generate morning briefing app
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"goal": "Create a morning briefing app", "user_id": "user123"}' \
  | python3 -m json.tool
```

**See the generated UI-MD:**

```bash
cat projects/Project_wabi_poc/output/create-a-morning-briefing-app-user123.md
```

## What Just Happened?

1. **API received your goal**: "Create a morning briefing app"
2. **UserMemoryAgent loaded preferences**: Location (SF), interests (tech), theme (dark)
3. **UIGeneratorAgent orchestrated**:
   - WeatherAgent fetched SF weather
   - CalendarAgent got today's schedule
   - NewsAgent retrieved tech headlines
4. **UI-MD was generated**: Personalized markdown UI definition
5. **File was saved**: `projects/Project_wabi_poc/output/[app-id].md`

## Explore the UI-MD

Open the generated file:

```bash
cat projects/Project_wabi_poc/output/create-a-morning-briefing-app-user123.md
```

**You'll see:**
- YAML frontmatter with app metadata
- Personalized greeting: "Good Morning, Alex! ☀️"
- Weather card for San Francisco
- Calendar with today's meetings
- Tech news list
- Interactive buttons

**In a real mobile app, this markdown would be rendered as a native UI!**

## Test User Actions

```bash
# Refresh weather data
curl -X POST http://localhost:8000/api/v1/action \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "create-a-morning-briefing-app-user123",
    "user_id": "user123",
    "action_id": "refresh_weather"
  }' | python3 -m json.tool
```

## API Documentation

Visit: `http://localhost:8000/docs`

Interactive API documentation with:
- All endpoints
- Request/response schemas
- "Try it out" functionality

## Project Structure Overview

```
projects/Project_wabi_poc/
├── README.md                    # Full documentation
├── QUICKSTART.md               # This file
├── test_wabi_poc.py            # End-to-end test suite
├── components/
│   └── agents/                 # Data-gathering agents
│       ├── WeatherAgent.md
│       ├── CalendarAgent.md
│       └── NewsAgent.md
└── output/                     # Generated UI-MD files
    └── [app-id].md

system/
├── agents/
│   ├── UserMemoryAgent.md      # Personalization engine
│   └── UIGeneratorAgent.md     # UI orchestrator
├── infrastructure/
│   └── ui_schema.md            # UI-MD format spec
├── user_profiles/
│   └── user123/
│       └── memory.md           # Sample user data
└── api/
    └── wabi_app_server.py      # FastAPI backend
```

## Common Issues

### Port 8000 Already in Use

```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn wabi_app_server:app --port 8080
```

### Missing Dependencies

```bash
# Install all at once
pip install -r requirements.txt
```

### User Profile Not Found

```bash
# Verify file exists
ls system/user_profiles/user123/memory.md

# If missing, check you're in the llmunix root directory
pwd
# Should end in: /llmunix
```

## Next Steps

### 1. Explore User Memory

```bash
# View full user profile
cat system/user_profiles/user123/memory.md
```

**Try modifying:**
- Location: Change to your city
- Interests: Add your favorite topics
- Theme: Switch to "light"

**Then regenerate the app to see personalization in action!**

### 2. Study the UI-MD Schema

```bash
cat system/infrastructure/ui_schema.md
```

**Learn about:**
- Component types (Header, Card, List, Button)
- Action system
- Layout options
- Styling

### 3. Examine Agent Logic

```bash
# UI Generator (main orchestrator)
cat system/agents/UIGeneratorAgent.md

# User Memory (personalization)
cat system/agents/UserMemoryAgent.md

# Weather data gathering
cat projects/Project_wabi_poc/components/agents/WeatherAgent.md
```

### 4. Read Full Documentation

```bash
cat projects/Project_wabi_poc/README.md
```

**Covers:**
- Full architecture explanation
- Integration patterns
- Roadmap to production
- How to extend the POC

### 5. Try Different Goals

Generate different types of apps:

```bash
# News reader
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"goal": "Create a tech news reader", "user_id": "user123"}'

# Workout tracker
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"goal": "Create a workout tracker", "user_id": "user123"}'

# Custom goal
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"goal": "Your custom app idea here", "user_id": "user123"}'
```

## Understanding the Magic

### How Personalization Works

1. **User Memory First**: Every request starts with `UserMemoryAgent`
2. **Context Matters**: Location, interests, habits inform every decision
3. **Data Gathering**: Agents fetch real-time data based on context
4. **UI Assembly**: Components chosen and populated dynamically
5. **Theme Applied**: Dark/light mode from preferences
6. **Learning Loop**: Every interaction updates user memory

### Why This is Revolutionary

**Traditional App Development:**
```
Idea → Design → Code → Build → Submit → Download → Use
(Weeks/months, one-size-fits-all)
```

**Wabi POC Approach:**
```
Need → Generate → Render → Use
(Seconds, uniquely personalized)
```

**Key Differences:**
- No installation required
- Instant generation
- Fully personalized
- Continuously adaptive
- Zero storage overhead

## Extending the POC

### Add a New Agent

1. **Create agent file:**
   ```bash
   touch projects/Project_wabi_poc/components/agents/MyNewAgent.md
   ```

2. **Define capabilities:**
   ```markdown
   ---
   agent_name: my-new-agent
   capabilities: [Data fetching, Processing]
   tools: [WebFetch, Bash]
   ---

   # My New Agent

   ## Purpose
   Fetch and process data for [specific use case]

   ## Instructions
   1. Receive request
   2. Fetch data from source
   3. Process and structure
   4. Return to UIGeneratorAgent
   ```

3. **Copy to discovery directory:**
   ```bash
   cp projects/Project_wabi_poc/components/agents/MyNewAgent.md \
      .claude/agents/Project_wabi_poc_MyNewAgent.md
   ```

4. **Use in UIGeneratorAgent:**
   The agent will automatically be discoverable by Claude Code!

### Add a New Component Type

1. **Edit UI schema:**
   ```bash
   nano system/infrastructure/ui_schema.md
   ```

2. **Define new component:**
   ```markdown
   ### Chart Component

   <component type="Chart">
     data: [...]
     type: bar | line | pie
   </component>
   ```

3. **Update UIGeneratorAgent** to use the new component

### Integrate Real APIs

**Example: OpenWeatherMap**

1. **Get API key:** https://openweathermap.org/api

2. **Set environment variable:**
   ```bash
   export OPENWEATHER_API_KEY="your_key_here"
   ```

3. **Update WeatherAgent** to use WebFetch with real API

4. **Test:**
   ```bash
   python3 projects/Project_wabi_poc/test_wabi_poc.py
   ```

## Performance Optimization

### For Testing
- Use SIMULATION mode (faster, no API calls)
- Cache user memory in memory (avoid file reads)
- Pre-generate common UI patterns

### For Production
- Implement Redis caching
- Use WebSockets for real-time updates
- CDN for static assets
- Horizontal scaling with load balancer

## Troubleshooting

### Tests Fail

```bash
# Check Python version (need 3.8+)
python3 --version

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Verify file permissions
ls -la system/user_profiles/user123/
```

### API Server Won't Start

```bash
# Check if port is in use
lsof -i:8000

# Check for syntax errors
python3 -m py_compile system/api/wabi_app_server.py
```

### UI-MD Not Generated

```bash
# Check output directory exists
ls projects/Project_wabi_poc/output/

# Check logs for errors
# (Server prints detailed logs to console)

# Verify user profile is valid
python3 -c "import yaml; print(yaml.safe_load(open('system/user_profiles/user123/memory.md').read().split('---')[1]))"
```

## Resources

- **Main README**: `projects/Project_wabi_poc/README.md`
- **UI Schema**: `system/infrastructure/ui_schema.md`
- **Test Suite**: `projects/Project_wabi_poc/test_wabi_poc.py`
- **API Docs**: `http://localhost:8000/docs` (when server running)
- **LLMunix Docs**: `doc/` in main repository

## Get Help

1. Check the full README
2. Review agent definitions
3. Run tests with verbose output
4. Examine API server logs
5. Open an issue on GitHub

---

**You're now ready to explore the future of on-demand software!** 🚀

*Built with LLMunix | Powered by Pure Markdown | Inspired by Wabi.ai*
