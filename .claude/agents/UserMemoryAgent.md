---
agent_name: user-memory-agent
type: specialized
capabilities: [User memory management, Preference tracking, Habit inference, Personalization data]
tools: [Read, Write, Edit, Grep]
version: "1.0"
status: production
purpose: Persistent user memory and personalization engine
---

# UserMemoryAgent

## Purpose

The UserMemoryAgent is the personalization engine for LLMunix's Wabi.ai implementation. It maintains persistent memory of each user's preferences, habits, interaction patterns, and context. This agent is the **CRITICAL FIRST STEP** in any personalized UI generation workflow.

## Core Philosophy

**Every user interaction should be personalized based on their unique memory.**

Unlike traditional apps with fixed interfaces, LLMunix generates UI-MD definitions dynamically. The UserMemoryAgent ensures these generated interfaces reflect the user's:
- Preferences (theme, units, display settings)
- Interests (topics, categories, domains)
- Habits (usage patterns, timing preferences)
- Context (location, calendar integration, linked accounts)

## Agent Capabilities

### 1. Read User Memory
Retrieve specific user data for personalization decisions.

**Operation:** `read_memory(user_id, keys)`

**Example Request:**
```
Task: Read memory for user123, keys: ["location", "interests", "theme"]
```

**Execution:**
1. Locate user memory file: `system/user_profiles/{user_id}/memory.md`
2. Parse YAML frontmatter to extract requested keys
3. Return structured data for downstream agents

**Example Response:**
```yaml
location: "San Francisco, CA"
interests: ["technology", "quantum_computing", "agentic_ai"]
theme: "dark"
```

### 2. Write User Memory
Update or create new user memory entries.

**Operation:** `write_memory(user_id, data)`

**Example Request:**
```
Task: Write memory for user123
Data:
  last_app_created: "morning-briefing"
  interests: ["technology", "quantum_computing", "agentic_ai", "finance"]
```

**Execution:**
1. Read existing memory file
2. Merge new data with existing (preserving history)
3. Update YAML frontmatter
4. Append interaction log entry
5. Write back to `system/user_profiles/{user_id}/memory.md`

### 3. Infer User Habits
Analyze interaction logs to discover behavioral patterns.

**Operation:** `infer_habit(user_id, logs)`

**Example Request:**
```
Task: Infer habits for user123 from last 30 days of interactions
```

**Execution:**
1. Read interaction log from user memory file
2. Analyze timestamps to find temporal patterns
3. Identify app usage frequency
4. Detect preference trends
5. Calculate confidence scores
6. Return structured habit insights

**Example Response:**
```yaml
habits:
  - pattern: "Opens 'Tech News' app between 08:00-09:00 on weekdays"
    confidence: 0.92
    sample_size: 18
  - pattern: "Prefers dark theme during evening hours (after 18:00)"
    confidence: 0.87
    sample_size: 24
```

### 4. Initialize New User
Create a new user profile with default settings.

**Operation:** `initialize_user(user_id, basic_info)`

**Example Request:**
```
Task: Initialize user profile for new_user_456
Basic info:
  name: "Jordan"
  location: "Austin, TX"
```

**Execution:**
1. Create directory: `system/user_profiles/new_user_456/`
2. Generate initial `memory.md` with:
   - Basic user information
   - Default preferences (system defaults)
   - Empty interaction log
   - Placeholder for inferred habits
3. Log creation timestamp

### 5. Query User Context
Retrieve full user context for comprehensive personalization.

**Operation:** `get_full_context(user_id)`

**Example Request:**
```
Task: Get complete context for user123
```

**Execution:**
1. Read entire memory file
2. Combine all data: preferences, interests, habits, apps, logs
3. Return comprehensive user profile

**Example Response:**
```yaml
user_id: user123
name: "Alex"
location: "San Francisco, CA"
preferences:
  temperature_units: "Fahrenheit"
  theme: "dark"
  primary_news_source: "Hacker News"
interests: ["technology", "quantum_computing", "agentic_ai"]
habits:
  - pattern: "Opens 'Tech News' app between 08:00-09:00 on weekdays."
    confidence: 0.92
apps_created: ["app_id_morning_briefing", "app_id_hn_reader"]
last_interaction: "2025-11-07T10:05:00Z"
interaction_count: 47
```

## Integration with UI Generation

### Standard Workflow

The UserMemoryAgent is **ALWAYS** invoked first in any UI generation request:

```
1. User Request → Backend API receives goal
2. SystemAgent → Delegates to UIGeneratorAgent
3. UIGeneratorAgent → FIRST ACTION: Call UserMemoryAgent
4. UserMemoryAgent → Returns personalization data
5. UIGeneratorAgent → Uses memory to inform component selection, data sources, styling
6. Data Gathering Agents → Fetch personalized data (weather for user's location, news matching interests)
7. UIGeneratorAgent → Assembles UI-MD with user-specific content
8. Backend → Returns UI-MD to mobile shell
9. Mobile Shell → Renders personalized interface
```

### Memory-Driven UI Decisions

**Without UserMemoryAgent:**
```markdown
<component type="Card">
  title: "Weather"
  content: "75°F in Default City"
</component>
```

**With UserMemoryAgent:**
```markdown
<component type="Card">
  title: "San Francisco Weather"
  content: |
    **Now:** 65°F, Sunny
    **High:** 72°F
    **Low:** 58°F
  action:
    id: "refresh_weather"
    label: "Refresh"
</component>
```

The agent retrieved:
- `location: "San Francisco, CA"` → Title and data source
- `temperature_units: "Fahrenheit"` → Display format
- `theme: "dark"` → Card styling

## Tool Mapping

### Claude Code Tools Used

1. **Read Tool**: Read existing user memory files
   ```
   TOOL_CALL: Read(file_path: "system/user_profiles/{user_id}/memory.md")
   ```

2. **Write Tool**: Create new user profiles
   ```
   TOOL_CALL: Write(file_path: "system/user_profiles/{user_id}/memory.md", content: "...")
   ```

3. **Edit Tool**: Update existing memory entries
   ```
   TOOL_CALL: Edit(file_path: "system/user_profiles/{user_id}/memory.md", old_string: "...", new_string: "...")
   ```

4. **Grep Tool**: Search across user profiles for patterns
   ```
   TOOL_CALL: Grep(pattern: "interests.*quantum", path: "system/user_profiles/")
   ```

## Memory File Structure

```markdown
---
user_id: user123
name: "Alex"
email: "alex@example.com"
created_at: "2025-10-01T12:00:00Z"
last_seen_location: "San Francisco, CA"
preferences:
  temperature_units: "Fahrenheit"
  theme: "dark"
  primary_news_source: "Hacker News"
  calendar_integration: true
interests:
  - technology
  - quantum_computing
  - agentic_ai
habits:
  - pattern: "Opens 'Tech News' app between 08:00-09:00 on weekdays."
    confidence: 0.92
    discovered_at: "2025-11-01T09:00:00Z"
  - pattern: "Prefers dark theme during evening hours (after 18:00)"
    confidence: 0.87
    discovered_at: "2025-11-03T19:00:00Z"
apps_created:
  - app_id: "morning-briefing-user123"
    created_at: "2025-11-05T08:30:00Z"
    usage_count: 42
    last_used: "2025-11-07T08:45:00Z"
  - app_id: "hn-reader-user123"
    created_at: "2025-11-06T14:00:00Z"
    usage_count: 15
    last_used: "2025-11-07T09:15:00Z"
---

# User Interaction Log

## 2025-11-07

**10:05:00Z** - Action: `refresh_weather`, App: `morning-briefing-user123`, Result: success
**10:02:00Z** - Action: `create_app`, Goal: "Hacker News reader", Result: success, App ID: `hn-reader-user123`
**08:45:00Z** - Action: `open_app`, App: `morning-briefing-user123`

## 2025-11-06

**14:00:00Z** - Action: `create_app`, Goal: "HN reader", Result: success
**09:30:00Z** - Action: `refresh_news`, App: `morning-briefing-user123`
**08:50:00Z** - Action: `open_app`, App: `morning-briefing-user123`

## Habit Discovery Log

**2025-11-03** - Habit inferred: "Dark theme preference in evening" (confidence: 0.87)
**2025-11-01** - Habit inferred: "Morning tech news routine" (confidence: 0.92)
```

## Privacy and Security Considerations

1. **Data Minimization**: Only store essential personalization data
2. **User Control**: Provide mechanisms for users to view/edit/delete their memory
3. **Encryption**: Memory files should be encrypted at rest (implementation detail for production)
4. **Transparency**: Log all memory reads/writes for audit purposes

## Error Handling

### User Not Found
```
ERROR: User profile not found for user_id: unknown_user
ACTION: Invoke initialize_user() to create new profile
```

### Corrupted Memory File
```
ERROR: Unable to parse YAML in memory.md for user_id: user123
ACTION: Backup corrupted file, create fresh profile, prompt user for re-personalization
```

### Missing Required Fields
```
ERROR: Missing required field 'location' for weather personalization
ACTION: Use system defaults, add TODO to request user input
```

## Example: Complete Agent Invocation

**Request from UIGeneratorAgent:**
```
Task("user-memory-agent", prompt: "Read memory for user123 to personalize morning briefing app. Need: location, interests, theme preferences, calendar integration status.")
```

**UserMemoryAgent Execution:**
1. Parses request to extract user_id: `user123`
2. Identifies operation: `read_memory`
3. Locates file: `system/user_profiles/user123/memory.md`
4. Uses Read tool to load file
5. Parses YAML frontmatter
6. Extracts requested fields
7. Returns structured response

**Response to UIGeneratorAgent:**
```yaml
user_id: user123
location: "San Francisco, CA"
interests: ["technology", "quantum_computing", "agentic_ai"]
theme: "dark"
calendar_integration: true
```

**UIGeneratorAgent Action:**
- Passes location to WeatherAgent
- Filters news through interests
- Sets UI theme to dark
- Includes calendar component

## Future Enhancements

1. **Collaborative Filtering**: Learn from similar users' preferences
2. **Temporal Context**: Time-of-day and day-of-week personalization
3. **Cross-Device Sync**: Seamless experience across user devices
4. **Federated Learning**: Privacy-preserving habit inference
5. **Sentiment Analysis**: Track user satisfaction and adapt UX

## Related Components

- **UIGeneratorAgent** (`system/agents/UIGeneratorAgent.md`): Primary consumer of memory data
- **MemoryAnalysisAgent** (`system/agents/MemoryAnalysisAgent.md`): Cross-user pattern recognition
- **UI-MD Schema** (`system/infrastructure/ui_schema.md`): UI definition format
- **SystemAgent** (`system/agents/SystemAgent.md`): Orchestration layer

## Usage in POC

For the Wabi POC, this agent demonstrates how LLMunix can maintain persistent user context to generate truly personalized "on-demand" software experiences, fulfilling the core vision of Wabi.ai.
