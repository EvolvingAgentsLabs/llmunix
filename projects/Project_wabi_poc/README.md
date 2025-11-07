# Wabi POC: On-Demand Mobile App Generation with LLMunix

## Vision: Realizing Wabi.ai's Dream

> "Software that doesn't exist until you need it, tailored precisely to your context, preferences, and current needs."

This POC transforms LLMunix from a backend agent orchestration framework into an **on-demand mobile app generation engine**, bringing to life the vision articulated by [Wabi.ai](https://wabi.ai/) and exemplified by Claude Imagine.

## What is This?

The Wabi POC demonstrates how LLMunix can generate personalized mobile application interfaces **on-demand** without traditional app compilation. Instead of users downloading separate apps from an app store, they:

1. **Express a need** (e.g., "Create a morning briefing app")
2. **Receive a personalized UI** generated instantly based on their memory and preferences
3. **Interact with the UI** which updates dynamically in response to actions
4. **Build a growing library** of personalized "apps" that evolve with them

## Core Architecture

### The "Pure Markdown App Factory"

LLMunix's "Pure Markdown" philosophy extends to UI generation:

```
User Goal (Text)
    ↓
LLMunix Agents (Markdown Definitions)
    ↓
UI-MD (Pure Markdown UI Definition)
    ↓
Mobile Shell (Renders UI in Real-Time)
    ↓
Personalized App Experience
```

### Key Components

1. **Mobile Shell App** (Not included in POC - external React Native/Flutter app)
   - Single app installed on user's device
   - Renders UI-MD definitions dynamically
   - Sends user actions back to backend

2. **Wabi App Server** (`system/api/wabi_app_server.py`)
   - FastAPI backend that receives goals and actions
   - Orchestrates LLMunix agents
   - Returns UI-MD documents

3. **UI-MD Format** (`system/infrastructure/ui_schema.md`)
   - Markdown-based UI definition language
   - Declarative component syntax
   - LLM-friendly and human-readable

4. **UserMemoryAgent** (`system/agents/UserMemoryAgent.md`)
   - Persistent user memory and preferences
   - Habit inference and learning
   - Personalization engine

5. **UIGeneratorAgent** (`system/agents/UIGeneratorAgent.md`)
   - Orchestrates UI-MD generation
   - Coordinates data-gathering agents
   - Composes personalized interfaces

6. **Data-Gathering Agents** (`projects/Project_wabi_poc/components/agents/`)
   - WeatherAgent: Real-time weather data
   - NewsAgent: Personalized news headlines
   - CalendarAgent: Schedule integration

## How It Works: Morning Briefing Example

### User Request
```
Goal: "Create a morning briefing app"
User: user123
```

### System Execution

**Step 1: Personalization**
```
UIGeneratorAgent → UserMemoryAgent
    ↓
Retrieves:
- Location: "San Francisco, CA"
- Interests: ["technology", "quantum_computing", "agentic_ai"]
- Theme: "dark"
- Habit: "Opens tech news between 08:00-09:00"
```

**Step 2: Data Gathering (Parallel)**
```
UIGeneratorAgent delegates to:
- WeatherAgent → Fetches SF weather forecast
- CalendarAgent → Gets today's schedule
- NewsAgent → Retrieves tech headlines
```

**Step 3: UI-MD Composition**
```
UIGeneratorAgent assembles:
- Header: "Good Morning, Alex! ☀️"
- Weather Card (SF, 65°F, Sunny)
- Calendar Card (3 meetings today)
- News List (5 tech headlines)
- Customize Button
```

**Step 4: Return to User**
```
Backend → Mobile Shell
    ↓
Shell renders UI-MD
    ↓
User sees personalized morning briefing!
```

### Generated UI-MD Sample

```markdown
---
app_id: morning-briefing-user123
user_id: user123
layout: vertical_stack
theme: dark
version: "1.0"
---

# Morning Briefing for Alex

<component type="Header">
  text: "Good Morning, Alex! ☀️"
  size: 24
</component>

<component type="Card">
  title: "San Francisco, CA Weather"
  content: |
    **Now:** 65°F, Sunny
    **High:** 72°F
    Perfect day for a walk!
  action:
    id: "refresh_weather"
    label: "Refresh"
</component>

[... more components ...]
```

## Installation & Setup

### Prerequisites

- Python 3.8+
- LLMunix framework installed
- Claude Code (for real agent invocation)

### Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify user profile exists:**
   ```bash
   ls system/user_profiles/user123/memory.md
   ```

3. **Run the test suite:**
   ```bash
   python3 projects/Project_wabi_poc/test_wabi_poc.py
   ```

4. **Start the API server:**
   ```bash
   python3 system/api/wabi_app_server.py
   ```

5. **Access API documentation:**
   ```
   http://localhost:8000/docs
   ```

## Using the API

### Generate a New App

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Create a morning briefing app",
    "user_id": "user123"
  }'
```

**Response:**
```json
{
  "success": true,
  "app_id": "create-a-morning-briefing-app-user123",
  "ui_md": "---\napp_id: ...\n...",
  "metadata": {
    "generated_at": "2025-11-07T10:00:00Z",
    "user_id": "user123",
    "personalization": {
      "location": "San Francisco, CA",
      "theme": "dark",
      "interests": ["technology", "quantum_computing"]
    }
  }
}
```

### Handle User Action

```bash
curl -X POST http://localhost:8000/api/v1/action \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "morning-briefing-user123",
    "user_id": "user123",
    "action_id": "refresh_weather"
  }'
```

### List User's Apps

```bash
curl http://localhost:8000/api/v1/apps/user123
```

### Get User Preferences

```bash
curl http://localhost:8000/api/v1/user/user123/preferences
```

## Project Structure

```
projects/Project_wabi_poc/
├── components/
│   ├── agents/                      # Project-specific agents
│   │   ├── WeatherAgent.md          # Weather data retrieval
│   │   ├── CalendarAgent.md         # Calendar integration
│   │   └── NewsAgent.md             # News aggregation
│   └── tools/                       # Project-specific tools
├── input/                           # Input documents
├── output/                          # Generated UI-MD files
│   └── create-a-morning-briefing-app-user123.md
├── memory/                          # Project memory
│   ├── short_term/                  # Agent interactions
│   └── long_term/                   # Learnings
├── workspace/                       # Execution state
│   └── state/                       # State files
├── test_wabi_poc.py                 # End-to-end test suite
└── README.md                        # This file

system/
├── agents/                          # System-wide agents
│   ├── UserMemoryAgent.md           # User memory & personalization
│   └── UIGeneratorAgent.md          # UI generation orchestrator
├── infrastructure/
│   └── ui_schema.md                 # UI-MD format specification
├── user_profiles/
│   └── user123/
│       └── memory.md                # Sample user memory
└── api/
    └── wabi_app_server.py           # FastAPI backend
```

## Key Features Demonstrated

### 1. Personalization Engine

Every UI is tailored to the user:
- **Location-based data** (weather, local news)
- **Interest filtering** (tech topics for tech enthusiasts)
- **Theme preferences** (dark mode for user123)
- **Habit optimization** (news card prioritized at 8 AM)

### 2. Dynamic UI Generation

No static templates:
- UIs assembled from real-time data
- Components chosen based on goal and context
- Layouts adapt to user preferences
- Content refreshes on demand

### 3. Persistent Memory

User context evolves over time:
- Preferences learned from interactions
- Habits inferred from usage patterns
- App history tracks favorites
- Personalization improves continuously

### 4. On-Demand Creation

Instant gratification:
- No app download required
- No compilation or build process
- Generate in seconds
- Iterate and refine instantly

### 5. Pure Markdown Architecture

Everything is markdown:
- Agents defined in `.md` files
- Tools specified in `.md` format
- UI definitions in markdown
- User memory in markdown
- LLM-native throughout

## What This Enables

### For Users

- **Personal Software**: Every app is uniquely yours
- **No Dark Patterns**: No ads, no engagement manipulation
- **Privacy by Design**: Data stays in your profile
- **Iterative Creation**: Refine apps through conversation
- **Zero Storage**: One shell app, infinite possibilities

### For Developers

- **LLM-Native Development**: Write markdown, not code
- **Composable Architecture**: Reusable agents and tools
- **Rapid Prototyping**: Minutes, not weeks
- **Cross-Platform**: One UI-MD, any platform
- **Learning Systems**: Apps get smarter with use

### For the Ecosystem

- **App Store Disruption**: Functionality without distribution
- **Collaborative Creation**: Share and remix UI-MD definitions
- **Federated Learning**: Improve agents across users
- **Open Standards**: UI-MD as a new interface definition language

## Roadmap: From POC to Production

### Phase 1: POC (Current)
- ✅ Core architecture defined
- ✅ Sample agents implemented
- ✅ API server functional
- ✅ End-to-end test passing
- ✅ Documentation complete

### Phase 2: Mobile Shell
- [ ] React Native shell app
- [ ] UI-MD parser and renderer
- [ ] Component library (Header, Card, List, etc.)
- [ ] Action handling and navigation
- [ ] Offline mode support

### Phase 3: Real Data Integration
- [ ] Weather API integration (OpenWeatherMap)
- [ ] News API integration (NewsAPI, Hacker News scraping)
- [ ] Calendar API integration (Google Calendar, Outlook)
- [ ] OAuth authentication flow
- [ ] User signup and profile management

### Phase 4: Advanced Features
- [ ] Voice input for app creation
- [ ] Multi-modal UI components (images, charts)
- [ ] Collaborative app sharing
- [ ] A/B testing and optimization
- [ ] Federated learning across users

### Phase 5: Production Deployment
- [ ] Scalable backend infrastructure
- [ ] CDN for static assets
- [ ] Real-time updates via WebSockets
- [ ] Analytics and monitoring
- [ ] App Store submission (Mobile Shell)

## Inspiration & References

This POC is inspired by:

- **[Wabi.ai](https://wabi.ai/)**: Vision of personalized, on-demand software
- **Claude Imagine**: Dynamic UI generation by LLMs
- **[Pocket Agent](https://pocket-agent.xyz/)**: Mobile-first agent experiences
- **LLMunix Framework**: Pure Markdown agent orchestration

## Technical Deep Dive

### Why UI-MD?

Traditional app development requires:
1. Design mockups
2. Write UI code (Swift, Kotlin, React Native)
3. Compile and build
4. Submit to app store
5. User downloads
6. Updates require re-submission

**With UI-MD:**
1. User expresses need
2. LLM generates UI-MD
3. Shell renders instantly
4. Updates in real-time

### Why Pure Markdown?

- **LLM-Native**: LLMs excel at generating structured markdown
- **Human-Readable**: Developers can read and modify UI-MD
- **Composable**: Components combine naturally
- **Versionable**: Git-friendly, diffable
- **Universal**: Works across platforms and frameworks

### Why UserMemoryAgent First?

Personalization is the foundation:
- Generic UIs are boring
- Memory makes apps feel intelligent
- Habits enable proactive suggestions
- Preferences save time and effort
- Context creates relevance

Every UI generation **must** start with memory consultation.

## Example: Extending the POC

### Create a Workout Tracker App

**User Request:**
```json
{
  "goal": "Create a workout tracker app",
  "user_id": "user123"
}
```

**System Actions:**
1. Query UserMemoryAgent for fitness preferences
2. Create WorkoutAgent (new, dynamic agent)
3. Generate UI-MD with exercise log, progress charts
4. Return personalized workout interface

**Generated Components:**
- Exercise history list
- Progress charts (reps, weight, cardio)
- Quick-add buttons for favorite exercises
- Rest timer
- Achievement badges

All personalized to user's fitness level, goals, and habits.

## Limitations of Current POC

- **Simulated Agent Invocation**: Uses direct function calls instead of Claude Code's Task tool
- **Hardcoded Data**: Weather/news/calendar data is synthetic
- **No Real Mobile Shell**: UI-MD rendering not implemented
- **Single User**: Multi-tenancy not fully implemented
- **No Authentication**: OAuth flow not included
- **Sync API**: WebSockets for real-time updates not implemented

## Contributing

This POC is part of the LLMunix project. To contribute:

1. Extend the UI-MD schema with new components
2. Create additional data-gathering agents
3. Implement real API integrations (weather, news, calendar)
4. Build the mobile shell app (React Native/Flutter)
5. Add more sophisticated personalization logic

## License

See main LLMunix repository for licensing details.

## Contact & Resources

- **LLMunix Repository**: [evolving-agents-labs/llmunix](https://github.com/EvolvingAgentsLabs/llmunix)
- **Documentation**: `doc/` directory in main repo
- **System Components**: `system/` directory
- **Agent Definitions**: `.claude/agents/` directory

---

**Built with LLMunix** | **Powered by Pure Markdown** | **Inspired by Wabi.ai**

🌟 *"Software that knows you, adapts to you, and exists only when you need it."*
