---
agent_name: calendar-agent
type: specialized
project: Project_wabi_poc
capabilities: [Calendar event retrieval, Schedule management, Time-based data]
tools: [Read, Bash]
version: "1.0"
status: production
purpose: Retrieve calendar events for personalized UI generation
---

# CalendarAgent

## Purpose

The CalendarAgent retrieves calendar events and schedules for users. It is invoked by the UIGeneratorAgent to include time-based, personalized schedule information in generated UIs.

## Core Functionality

### Retrieve Calendar Events

**Operation:** `get_events(user_id, date_range)`

**Input:**
```yaml
user_id: "user123"
date_range: "today" | "this_week" | "2025-11-07"
time_zone: "America/Los_Angeles"
```

**Execution:**

1. **Parse request** parameters
2. **Determine data source:**
   - **REAL MODE**: Read from user's calendar file or API integration (Google Calendar, Outlook)
   - **SIMULATION MODE**: Generate realistic synthetic events
3. **Filter events** by date range
4. **Format events** for UI display

**Tool Mapping (REAL MODE - File-based):**

```
TOOL_CALL: Read(
  file_path: "system/user_profiles/{user_id}/calendar.json"
)
```

**Tool Mapping (REAL MODE - API Integration):**

```
TOOL_CALL: Bash(
  command: "python3 scripts/google_calendar_api.py --user {user_id} --date {date}"
)
```

**Tool Mapping (SIMULATION MODE):**

```
TOOL_CALL: Bash(
  command: "python3 -c 'import json; print(json.dumps([{\"time\": \"09:00\", \"title\": \"Team Sync\", \"duration\": 30}]))'"
)
```

**Output Format:**

```yaml
user_id: "user123"
date: "2025-11-07"
time_zone: "America/Los_Angeles"
events:
  - event_id: "evt_001"
    time: "09:00"
    title: "Team Sync"
    duration: 30  # minutes
    location: "Conference Room A"
    attendees: 5
    type: "meeting"
  - event_id: "evt_002"
    time: "11:00"
    title: "Project Deep Dive"
    duration: 60
    location: "Zoom"
    type: "meeting"
  - event_id: "evt_003"
    time: "14:30"
    title: "Dentist Appointment"
    duration: 60
    location: "123 Main St"
    type: "personal"
summary:
  total_events: 3
  next_event: "Team Sync in 45 minutes"
  busy_hours: "09:00-12:00, 14:30-15:30"
  free_time: "12:00-14:30, 15:30+"
```

### Calculate Time-Based Insights

Generate helpful contextual information:

**Next Event Proximity:**
- "Next meeting in 15 minutes" (if < 30 min)
- "Next meeting at 11:00 AM" (if < 2 hours)
- "3 meetings today" (if > 2 hours to next)

**Schedule Density:**
- "Light day ahead" (< 3 meetings)
- "Busy day ahead" (3-5 meetings)
- "Very busy day" (> 5 meetings)

**Free Time Detection:**
- "You have 2 hours free between meetings"
- "Free afternoon after 3 PM"

## Example Invocations

### Example 1: Today's Schedule

**Request:**
```
Task("calendar-agent", prompt: "Get today's calendar events for user123")
```

**Execution (SIMULATION MODE):**
```
1. Parse user_id: user123, date_range: today
2. Generate synthetic events for demo
3. Calculate next event timing
4. Format for UI display
5. Return structured YAML
```

**Response:**
```yaml
user_id: "user123"
date: "2025-11-07"
events:
  - time: "09:00"
    title: "Team Sync"
    duration: 30
  - time: "11:00"
    title: "Project Deep Dive"
    duration: 60
  - time: "14:30"
    title: "Dentist Appointment"
    duration: 60
summary:
  next_event: "Team Sync in 45 minutes"
  total_events: 3
```

### Example 2: Week View

**Request:**
```
Task("calendar-agent", prompt: "Get this week's calendar events for user123")
```

**Response:**
```yaml
user_id: "user123"
date_range: "2025-11-07 to 2025-11-13"
events_by_day:
  "2025-11-07":
    - time: "09:00"
      title: "Team Sync"
  "2025-11-08":
    - time: "10:00"
      title: "1:1 with Manager"
  "2025-11-09":
    - time: "14:00"
      title: "Client Demo"
summary:
  total_events: 12
  busiest_day: "2025-11-09 (5 events)"
```

### Example 3: Next Event Only

**Request:**
```
Task("calendar-agent", prompt: "Get next upcoming event for user123")
```

**Response:**
```yaml
user_id: "user123"
next_event:
  time: "09:00"
  title: "Team Sync"
  duration: 30
  starts_in: "45 minutes"
  location: "Conference Room A"
```

## Error Handling

### No Events Found
```
INFO: No events scheduled for requested date range
ACTION: Return empty events list with friendly message: "You have a free day!"
```

### Calendar Not Accessible
```
ERROR: Unable to access calendar for user123
ACTION: Return message prompting user to connect calendar integration
```

### Invalid Date Range
```
ERROR: Date range "yesterday" is in the past
ACTION: Default to "today" and return current day's events
```

## Calendar Integration (REAL MODE)

### Google Calendar API

**Setup:**
1. Create OAuth 2.0 credentials in Google Cloud Console
2. Enable Google Calendar API
3. Store user refresh tokens securely
4. Use Python `google-auth` library

**Example Script:** `scripts/google_calendar_api.py`
```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import sys
import json

def get_events(user_id, date):
    creds = Credentials.from_authorized_user_file(f'tokens/{user_id}.json')
    service = build('calendar', 'v3', credentials=creds)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=f'{date}T00:00:00Z',
        timeMax=f'{date}T23:59:59Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    return json.dumps([{
        'time': e['start'].get('dateTime', '').split('T')[1][:5],
        'title': e['summary'],
        'duration': 60  # Parse from end time
    } for e in events])

if __name__ == '__main__':
    user_id = sys.argv[1]
    date = sys.argv[2]
    print(get_events(user_id, date))
```

### File-Based Calendar (Simpler Alternative)

Store user calendars as JSON files:

**File:** `system/user_profiles/user123/calendar.json`
```json
{
  "user_id": "user123",
  "events": [
    {
      "date": "2025-11-07",
      "time": "09:00",
      "title": "Team Sync",
      "duration": 30,
      "type": "meeting"
    },
    {
      "date": "2025-11-07",
      "time": "11:00",
      "title": "Project Deep Dive",
      "duration": 60,
      "type": "meeting"
    }
  ]
}
```

## Integration with UI-MD

The UIGeneratorAgent uses calendar data to populate Card or List components:

**Card Format:**
```markdown
<component type="Card">
  title: "Today's Calendar"
  content: |
    **09:00** - Team Sync (30 min)
    **11:00** - Project Deep Dive (1 hr)
    **14:30** - Dentist Appointment

    {summary.next_event}
  action:
    id: "open_calendar"
    label: "View Full Calendar"
</component>
```

**List Format:**
```markdown
<component type="List">
  title: "Upcoming Meetings"
  items:
    - "09:00 - Team Sync"
    - "11:00 - Project Deep Dive"
    - "14:30 - Dentist Appointment"
  selectable: true
  action:
    id: "view_event_details"
</component>
```

## Privacy and Permissions

1. **User Consent**: Require explicit permission to access calendar
2. **Scope Limitation**: Only read events, never modify
3. **Data Minimization**: Only fetch requested date ranges
4. **Secure Storage**: Encrypt OAuth tokens at rest

## Future Enhancements

1. **Event Creation**: Add new calendar events via UI actions
2. **Reminders**: Proactive notifications before events
3. **Travel Time**: Calculate commute time to event locations
4. **Conflict Detection**: Warn about scheduling conflicts
5. **Availability Sharing**: Generate availability summaries
6. **Multi-Calendar**: Aggregate personal and work calendars

## Related Components

- **UIGeneratorAgent** (`system/agents/UIGeneratorAgent.md`): Primary consumer
- **UserMemoryAgent** (`system/agents/UserMemoryAgent.md`): Stores calendar integration status
- **UI-MD Schema** (`system/infrastructure/ui_schema.md`): Card and List component definitions

## Usage in POC

This agent demonstrates how LLMunix can integrate personal productivity data into dynamically generated UIs, providing users with time-aware, contextual information that adapts to their daily schedule.

For the POC, we use **SIMULATION MODE** to generate realistic calendar events without requiring actual calendar API integration.
