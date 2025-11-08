---
agent_name: weather-agent
type: specialized
project: Project_wabi_poc
capabilities: [Weather data retrieval, Forecast generation, Location-based data]
tools: [WebFetch, Bash]
version: "1.0"
status: production
purpose: Fetch real-time weather data for personalized UI generation
---

# WeatherAgent

## Purpose

The WeatherAgent retrieves current weather conditions and forecasts for specified locations. It is invoked by the UIGeneratorAgent during the data-gathering phase of UI-MD generation.

## Core Functionality

### Retrieve Weather Data

**Operation:** `get_weather(location)`

**Input:**
```yaml
location: "San Francisco, CA"
units: "fahrenheit"  # or "celsius"
```

**Execution:**

1. **Parse location** from request
2. **Determine data source:**
   - **REAL MODE**: Use WebFetch to call weather API (OpenWeatherMap, Weather.gov, etc.)
   - **SIMULATION MODE**: Generate realistic synthetic data
3. **Structure response** in consistent format

**Tool Mapping (REAL MODE):**

```
TOOL_CALL: WebFetch(
  url: "https://api.openweathermap.org/data/2.5/weather?q={location}&appid={API_KEY}&units=imperial",
  prompt: "Extract current temperature, condition, humidity, and today's high/low forecast"
)
```

**Alternative (Weather.gov for US locations):**
```
TOOL_CALL: WebFetch(
  url: "https://api.weather.gov/gridpoints/{office}/{grid_x},{grid_y}/forecast",
  prompt: "Extract current conditions and forecast"
)
```

**Tool Mapping (SIMULATION MODE):**

```
TOOL_CALL: Bash(
  command: "python3 -c 'import random; print(f\"temp: {random.randint(55, 85)}F, condition: {random.choice([\"Sunny\", \"Cloudy\", \"Rainy\"])}\")'"
)
```

**Output Format:**

```yaml
location: "San Francisco, CA"
timestamp: "2025-11-07T10:00:00Z"
current:
  temperature: 65
  temperature_unit: "F"
  condition: "Sunny"
  condition_code: "clear-day"
  humidity: 60
  wind_speed: 10
  wind_direction: "NW"
forecast:
  high: 72
  low: 58
  precipitation_chance: 10
  conditions: "Mostly sunny"
contextual_message: "Perfect day for a walk!"
```

### Generate Contextual Messages

Based on weather conditions, provide user-friendly messages:

**Sunny + High temp (>75°F):** "Perfect day for a walk!"
**Rainy:** "Don't forget your umbrella!"
**Hot (>85°F):** "Stay hydrated today!"
**Cold (<45°F):** "Bundle up, it's chilly!"
**Windy (>20mph):** "Hold onto your hat!"

## Example Invocations

### Example 1: Morning Briefing

**Request:**
```
Task("weather-agent", prompt: "Get current weather and forecast for San Francisco, CA")
```

**Execution (REAL MODE):**
```
1. Parse location: "San Francisco, CA"
2. WebFetch → https://api.openweathermap.org/data/2.5/weather?q=San+Francisco,CA
3. Extract data: temp=65°F, condition=Sunny
4. WebFetch → Forecast API for high/low
5. Generate contextual message based on conditions
6. Return structured YAML
```

**Response:**
```yaml
location: "San Francisco, CA"
current:
  temperature: 65
  condition: "Sunny"
forecast:
  high: 72
  low: 58
contextual_message: "Perfect day for a walk!"
```

### Example 2: Multiple Locations

**Request:**
```
Task("weather-agent", prompt: "Get weather for New York, NY and Austin, TX")
```

**Response:**
```yaml
locations:
  - location: "New York, NY"
    current:
      temperature: 72
      condition: "Partly Cloudy"
    forecast:
      high: 78
      low: 65
  - location: "Austin, TX"
    current:
      temperature: 88
      condition: "Hot and Sunny"
    forecast:
      high: 95
      low: 75
    contextual_message: "Stay hydrated today!"
```

## Error Handling

### Invalid Location
```
ERROR: Location "XYZ123" not recognized
ACTION: Return default message requesting valid location
```

### API Failure
```
ERROR: Weather API timeout or rate limit exceeded
ACTION: Return cached data if available, otherwise return generic "Weather unavailable" message
```

### Missing API Key
```
ERROR: OpenWeatherMap API key not configured
ACTION: Fall back to simulation mode with synthetic data
```

## Integration with UI-MD

The UIGeneratorAgent uses weather data to populate Card components:

```markdown
<component type="Card">
  title: "{location} Weather"
  content: |
    **Now:** {current.temperature}°{current.temperature_unit}, {current.condition}
    **High:** {forecast.high}°{current.temperature_unit}
    **Low:** {forecast.low}°{current.temperature_unit}

    {contextual_message}
  action:
    id: "refresh_weather"
    label: "Refresh"
    style: secondary
</component>
```

## Configuration

### API Setup (for REAL MODE)

**OpenWeatherMap:**
1. Sign up at https://openweathermap.org/api
2. Get free API key
3. Set environment variable: `OPENWEATHER_API_KEY`

**Weather.gov (US only, no key required):**
- Free API, no authentication
- Use for US locations only

### Simulation Mode

For POC testing without API keys:
```bash
export LLMUNIX_MODE=SIMULATION
```

Agent will generate realistic synthetic weather data.

## Future Enhancements

1. **Weather Alerts**: Severe weather warnings
2. **Historical Data**: Compare to averages
3. **Multi-Day Forecast**: 7-day outlook
4. **Weather Maps**: Include visual precipitation/temperature maps
5. **Air Quality**: AQI data integration
6. **Sunrise/Sunset**: Solar timing data

## Related Components

- **UIGeneratorAgent** (`system/agents/UIGeneratorAgent.md`): Primary consumer
- **UserMemoryAgent** (`system/agents/UserMemoryAgent.md`): Provides location preference
- **UI-MD Schema** (`system/infrastructure/ui_schema.md`): Card component definition

## Usage in POC

This agent demonstrates how LLMunix can integrate real-world data sources into dynamically generated UIs, providing users with timely, location-aware information.
